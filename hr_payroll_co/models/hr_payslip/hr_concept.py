# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import ValidationError
from odoo.addons.utilities_collection import orm
from odoo.addons.utilities_collection.time import days360
from dateutil.relativedelta import relativedelta

############################################################################
# ------------------- SOLO SE SOPORTAN ValidationError --------------------#
############################################################################

CONCEPTS = [
    'BASICO', 'SUB_TRANS', 'IBD',  'DED_PENS', 'DED_EPS', 'FOND_SOL',
    'FOND_SUB', 'PRIMA_LIQ', 'CES_LIQ', 'ICES_LIQ',
    'BRTF', 'RTEFTE',
    'PRIMA', 'CES', 'ICES',
    'INDEM', 'RTF_INDEM',
    'PRV_CES', 'PRV_ICES', 'PRV_PRIMA',
    'NETO', 'NETO_CES'
]
TPCT = 'total_previous_categories'
TPCP = 'total_previous_concepts'
NCI = 'non_constitutive_income'

DAYS_YEAR = 360


class HrConceptType(models.Model):
    _name = 'hr.concept'
    _inherit = 'model.basic.payslip.novelty.type'
    _description = 'Concepto de Nómina'
    _order = 'name'

    documentation = fields.Char(string='Información')

    def get_seq_concept_category(self):
        for i, concept in enumerate(CONCEPTS):
            if concept == self.code:
                return i
        return len(CONCEPTS)

    def _compute_ibd(self, data_payslip):
        salary = 0
        for category in ['earnings', 'o_salarial_earnings', 'comp_earnings', 'o_rights']:
            salary += data_payslip.get(TPCT, {}).get(category, 0)
            salary += data_payslip.get(category, 0)
        o_earnings = data_payslip.get(TPCT, {}).get('o_earnings', 0)
        o_earnings += data_payslip.get('o_earnings', 0)
        top40 = (salary + o_earnings) * 0.4
        if o_earnings > top40:
            data_payslip['IBD'] = salary + o_earnings - top40
        else:
            data_payslip['IBD'] = salary
        if data_payslip['contract'].contract_type_id.type_class == 'int':
            data_payslip['IBD'] *= 0.7
        smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
        if data_payslip['IBD'] > 25 * smmlv:
            data_payslip['IBD'] = 25 * smmlv

    def _compute_brtf(self, data_payslip):
        total_income = 0
        for category in ['earnings', 'o_earnings', 'o_salarial_earnings', 'comp_earnings', 'o_rights']:
            total_income += data_payslip.get(TPCT, {}).get(category, 0)
            total_income += data_payslip.get(category, 0)
        total_income -= data_payslip.get('income_EXT', 0)
        if data_payslip['contract'].apply_procedure_2:
            for concept in ['PRIMA', 'PRIMA_LIQ']:
                total_income += data_payslip.get(TPCP, {}).get(concept, 0)
                total_income += data_payslip.get(concept, 0)

        total_nci = data_payslip[NCI]
        for nci in ['DED_PENS', 'DED_EPS', 'FOND_SOL', 'FOND_SUB']:
            total_nci += data_payslip.get(TPCP, {}).get(nci, 0)
        neto_income = total_income - total_nci
        if neto_income == 0:
            data_payslip['BRTF'] = 0
            return

        # Deducciones
        uvt = data_payslip['economic_variables']['UVT'][data_payslip['period'].start.year]
        if data_payslip['contract'].deduction_dependents:
            deduction_base = total_income * 0.1
            deduction_dependents = deduction_base if deduction_base <= 32 * uvt else 32 * uvt
        else:
            deduction_dependents = 0

        if data_payslip['contract'].deduction_by_estate <= 100 * uvt:
            deduction_estate = data_payslip['contract'].deduction_by_estate
        else:
            deduction_estate = 100 * uvt

        if data_payslip['contract'].deduction_by_healthcare <= 16 * uvt:
            deduction_healthcare = data_payslip['contract'].deduction_by_healthcare
        else:
            deduction_healthcare = 16 * uvt

        if data_payslip['contract'].deduction_by_icetex <= 8.333 * uvt:
            deduction_icetex = data_payslip['contract'].deduction_by_icetex
        else:
            deduction_icetex = 8.333 * uvt

        deduction_total = deduction_dependents + deduction_estate + \
            deduction_healthcare + deduction_icetex

        AVP = data_payslip.get('outcome_AVP', 0)
        AFC = data_payslip.get('outcome_AFC', 0)
        voluntary_contributions = AVP + AFC
        if voluntary_contributions > neto_income * 0.3:
            voluntary_contributions = neto_income * 0.3

        top25 = (neto_income - deduction_total -
                 voluntary_contributions) * 0.25
        if top25 > 240 * uvt:
            top25 = 240 * uvt

        top40 = neto_income * 0.4 if neto_income * 0.4 <= 420 * uvt else 420 * uvt
        exempt_rent = deduction_total + voluntary_contributions + top25
        if exempt_rent > top40:
            exempt_rent = top40

        data_payslip['BRTF'] = neto_income - exempt_rent

    def _compute_indem(self, data_payslip):
        settlement_type = data_payslip['contract'].settlement_type
        if not settlement_type:
            raise ValidationError('El contrato no tiene tipo de finalización.')
        elif settlement_type not in ['n_causa', 'unil']:
            return
        term = data_payslip['contract'].term
        settlement_date = data_payslip['contract'].settlement_date
        if not settlement_date:
            raise ValidationError('El contrato no tiene fecha de liquidación.')
        if 'last_year' not in data_payslip:
            self.get_last_year(data_payslip, settlement_date)
        if term in ['fijo', 'obra-labor']:
            date_end = data_payslip['contract'].date_end
            if not date_end:
                raise ValidationError('El contrato no tiene fecha de fin.')
            if settlement_date > date_end:
                raise ValidationError(
                    'La fecha de liquidación debe ser menor o igual a la fecha de fin.')
            days_not_pay = days360(settlement_date, date_end) - 1
            if days_not_pay <= 0:
                return
            value, qty = data_payslip['last_year']['average'], days_not_pay
            if term == 'obra-labor' and qty < 15:
                qty = 15
        else:
            date_start = data_payslip['contract'].date_start
            if not date_start:
                raise ValidationError('El contrato no tiene fecha de inicio.')
            duration = days360(date_start, settlement_date)
            value = data_payslip['last_year']['average']
            smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
            qty, days = [30, 20] if value < 10 * smmlv / 30 else [20, 15]
            qty += (duration - 360)*days/360 if duration > 361 else 0
        data_payslip['INDEM_value'] = value
        data_payslip['INDEM_qty'] = qty

    def _compute_social_benefits(self, data_payslip, date_from, date_to):
        ces = ['CESLY', 'ICESLY', 'CES', 'ICES', 'CES_PART',
               'ICES_PART', 'CES_LIQ', 'ICES_LIQ', 'PRV_CES', 'PRV_ICES']
        is_ces = self.code in ces
        if is_ces:
            date_3_months_before = date_to - relativedelta(months=3)
            if date_from > date_3_months_before:
                date_3_months_before = date_from
            has_change_salary = data_payslip['contract'].has_change_salary(
                date_3_months_before, date_to)
            compute_average = True if has_change_salary else False
        else:
            compute_average = True

        data_base = {}
        days_worked = days360(date_from, date_to)
        data = {
            'contract': data_payslip['contract'].id,
            'start': date_from,
            'end': date_to,
        }

        # Compute Salary
        if compute_average:
            concepts = ('BASICO',)
            data_salary = {}
            self._get_total_concepts(
                data_payslip['cr'], data_salary, data, data['contract'], concepts)
            data_base['salary'] += sum(data_salary.values())
            data_base['salary'] += data_payslip.get('BASICO', 0)
        else:
            full_wage = data_payslip.get(
                'full_wage', data_payslip['contract'].wage)
            data_base['salary'] = full_wage * days_worked / 30

        # Cumpute Variable Salary
        data_variable_salary = {}
        self.get_variable_salary(
            data_payslip['cr'], data_variable_salary, data, data['contract'])

        actual_variable = self._get_actual_variable_salary(data_payslip)
        previous_variable = sum(data_variable_salary.values())
        data_base['variable'] = actual_variable + previous_variable

        # Compute Static Salary
        earnings = data_variable_salary.get('earnings', 0)
        earnings += data_base['salary']

        if days_worked <= 30:
            earnings_month = earnings
        else:
            earnings_month = earnings * 30 / days_worked

        if data_payslip['politics']['hr_payroll_coll_co.average_sub_trans']:
            concepts = ('SUB_TRANS', 'SUB_CONNE')
            data_static_salary = {}
            self._get_total_concepts(
                data_payslip['cr'], data_static_salary, data, data['contract'], concepts)

            data_base['static'] = sum(data_static_salary.values())
            data_base['static'] += data_payslip.get('SUB_TRANS', 0)
        else:
            smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
            if earnings_month < 2 * smmlv:
                subsidy = data_payslip['economic_variables']['SUB_TRANS'][data_payslip['period'].start.year]
                data_base['static'] = subsidy * days_worked / 30

        # Compute Base / Total
        base = sum(data_base.values())
        base *= 1 if days_worked <= 30 else 30 / days_worked
        total = base * days_worked / 360
        return base, days_worked, total

    def _compute_rate_fond_sol(self, smmlv, value):
        return 0.5 if value >= 4 * smmlv else 0

    def _compute_rate_fond_sub(self, smmlv, value):
        if value < 4 * smmlv:
            return 0
        elif 4 * smmlv <= value < 16 * smmlv:
            return 0.5
        elif 16 * smmlv <= value < 17 * smmlv:
            return 0.7
        elif 17 * smmlv <= value < 18 * smmlv:
            return 0.9
        elif 18 * smmlv <= value < 19 * smmlv:
            return 1.1
        elif 19 * smmlv <= value < 20 * smmlv:
            return 1.3
        else:
            return 1.5

    def _get_rate_trtefte(self, data_payslip, value):
        uvt = data_payslip['economic_variables']['UVT'][data_payslip['period'].start.year]
        table = data_payslip['economic_variables']['TRTEFTE'][data_payslip['period'].start.year]
        if uvt == 0:
            raise ValidationError(
                'La UVT definida para el año %s es cero.' % data_payslip['period'].start.year)
        base = value / uvt
        subtract, rate, add, lower_limit, upper_limit = [x for x in range(5)]
        rtefte = 0
        for t in table:
            compute = False
            if t[lower_limit] == None and t[upper_limit] != None and base <= t[upper_limit]:
                compute |= True
            elif None not in t[lower_limit:upper_limit-1] and t[lower_limit] < base <= t[upper_limit]:
                compute |= True
            elif t[lower_limit] != None and t[upper_limit] == None and t[lower_limit] < base:
                compute |= True
            if compute:
                rtefte = (base - t[subtract]) * t[rate] / 100 + t[add]
                rtefte *= uvt * 100 / value
        return rtefte

    def _get_total_concepts(self, cr, total_previous, period, contract, concepts):
        """
        Consulta las lineas de nomina y agrupa por categoria
        @params:
            total_previous: Diccionario donde se guardaran los datos
            period: Objeto tipo hr.period o Dicionario con {inicio,fin}
            contract: ID del contrato
            concepts: Tupla de conceptos a consultar
        @return:
            None
        """
        param = {
            'concepts': concepts,
            'contract': contract,
            'start': period.start if type(period) != dict else period['start'],
            'end': period.end if type(period) != dict else period['end'],
        }
        query = f"""
        SELECT HC.code, sum(HPL.total)
        FROM hr_payslip_line as HPL
        INNER JOIN hr_concept as HC
            ON HC.id = HPL.concept_id
        INNER JOIN hr_payslip as HP
            ON HP.id = HPL.payslip_id
        INNER JOIN hr_period as PP
            ON PP.id = HP.period_id
        WHERE
            HP.state = 'paid' AND
            PP.end >= %(start)s AND
            PP.start <= %(end)s AND
            HP.contract_id = %(contract)s AND
            HC.code in %(concepts)s
        GROUP BY HC.code
        """
        data = orm._fetchall(cr, query, param)
        for d in data:
            if d[0] not in total_previous:
                total_previous[d[0]] = d[1]
            else:
                total_previous[d[0]] += d[1]

    def _get_total_concept_categories(self, cr, total_previous, period, contract, exclude=False, categories=False):
        """
        Consulta las lineas de nomina y agrupa por categoria
        @params:
            total_previous: Diccionario donde se guardaran los datos
            period: Objeto tipo hr.period o Dicionario con {'start','end'}
            contract: ID del contrato
            exclude: Tupla con codigo de conceptos a excluir
            categories: Tupla de categorias a consultar
        @return:
            None
        """
        if not categories:
            categories = ('earnings', 'o_salarial_earnings',
                          'comp_earnings', 'o_rights', 'o_earnings')
        param = {
            'categories': categories,
            'contract': contract,
            'start': period.start if type(period) != dict else period['start'],
            'end': period.end if type(period) != dict else period['end'],
        }
        subquery = ['', '']
        if exclude:
            subquery[0] = "LEFT JOIN hr_concept as HC ON HC.id = HPL.concept_id"
            subquery[1] = "AND (HC.code IS NULL or HC.code not in %(exclude)s)"
            param['exclude'] = exclude
        query = f"""
        SELECT HPL.category, sum(HPL.total)
        FROM hr_payslip_line as HPL
        INNER JOIN hr_payslip as HP
            ON HP.id = HPL.payslip_id
        INNER JOIN hr_period as PP
            ON PP.id = HP.period_id
        {subquery[0]}
        WHERE
            HP.state = 'paid' AND
            HPL.category IN %(categories)s AND
            PP.end >= %(start)s AND
            PP.start <= %(end)s AND
            HP.contract_id = %(contract)s
            {subquery[1]}
        GROUP BY HPL.category
        """
        data = orm._fetchall(cr, query, param)
        for d in data:
            if d[0] not in total_previous:
                total_previous[d[0]] = d[1]
            else:
                total_previous[d[0]] += d[1]

    def get_variable_salary(self, cr, data, period, contract):
        categories = ('earnings', 'comp_earnings', 'o_salarial_earnings')
        self._get_total_concept_categories(cr, data, period, contract,
                                           exclude=('BASICO',), categories=categories)

    def get_last_year(self, data_payslip, date_to):
        date_from = date_to - relativedelta(years=1)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start
        days = days360(date_from, date_to)
        data_payslip['last_year'] = {
            'start': date_from, 'end': date_to, 'days': days}
        wd = days
        data_payslip['last_year']['worked_days'] = wd
        data = {}
        self.get_variable_salary(
            data_payslip['cr'], data, data_payslip['last_year'], data_payslip['contract'].id)
        average = data_payslip['full_wage']
        for category in data:
            average += data[category] * (1 if wd < 30 else 30/wd)
        data_payslip['last_year']['average'] = average / 30

    def need_compute_salary_average(self, contract, date_from, date_to):
        date_3_months_before = date_to - relativedelta(months=3)
        if date_from > date_3_months_before:
            date_3_months_before = date_from
        return contract.has_change_salary(date_3_months_before, date_to)

    def get_sum_salary(self, data_payslip, query_params):
        salary = 0

        # Add amount per worked days
        concepts = ('BASICO',)
        data_salary = {}
        self._get_total_concepts(
            data_payslip['cr'], data_salary, query_params, query_params['contract'], concepts)
        salary += sum(data_salary.values())
        salary += data_payslip.get('BASICO', 0)

        # Ignore duplicated amount per worked days in this period
        data_salary_ignore = {}
        query_params['start'] = data_payslip['period'].start
        query_params['end'] = data_payslip['period'].end
        self._get_total_concepts(
            data_payslip['cr'], data_salary_ignore, query_params, query_params['contract'], concepts)
        salary -= sum(data_salary_ignore.values())

        return salary

    def get_sum_variable_salary(self, data_payslip, query_params):
        data_variable_salary = {}
        self.get_variable_salary(
            data_payslip['cr'], data_variable_salary, query_params, query_params['contract'])

        actual_variable = self._get_actual_variable_salary(data_payslip)
        previous_variable = sum(data_variable_salary.values())
        variable = actual_variable + previous_variable
        return variable, data_variable_salary.get('earnings', 0)

    def _get_actual_variable_salary(self, data_payslip):
        categories = ('earnings', 'comp_earnings', 'o_salarial_earnings')
        sum_categories = sum([data_payslip.get(con, 0) for con in categories])
        return sum_categories - data_payslip.get('wage', 0)

    def _compute_layoff(self, data_payslip, date_from, date_to):
        base_layoff, worked_days, layoff = self._get_social_benefits(
            data_payslip, date_from, date_to, False)
        return base_layoff, worked_days, layoff

    def _compute_prima(self, data_payslip, date_from, date_to):
        base_prima, worked_days, prima = self._get_social_benefits(
            data_payslip, date_from, date_to, True)
        return base_prima, worked_days, prima

    def _get_social_benefits(self, data_payslip, date_from, date_to, compute_with_average):
        worked_days = days360(date_from, date_to)

        query_params = {
            'contract': data_payslip['contract'].id,
            'start': date_from,
            'end': date_to,
        }

        days_rate = 1 if worked_days <= 30 else 30 / worked_days

        compute_average = compute_with_average or self.need_compute_salary_average(
            data_payslip['contract'], date_from, date_to)
        if compute_average:
            data_layoff = {'salary': self.get_sum_salary(
                data_payslip, query_params.copy())}
        else:
            data_layoff = {'salary': data_payslip.get(
                'full_wage', 0) * worked_days / 30}

        data_layoff['variable'], variable_earnings = self.get_sum_variable_salary(
            data_payslip, query_params)

        total_earnings = variable_earnings + data_layoff['salary']
        month_earnings = total_earnings * days_rate

        smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]

        if month_earnings < 2 * smmlv:
            subsidy = data_payslip['economic_variables']['SUB_TRANS'][data_payslip['period'].start.year]
            data_layoff['static'] = subsidy * worked_days / 30

        base_social_benefits = sum(data_layoff.values()) * days_rate
        social_benefits = base_social_benefits * worked_days / DAYS_YEAR
        return base_social_benefits, worked_days, social_benefits

    def _get_total_previous(self, data_payslip, date_from, date_to):
        concept = (self.code,)
        query_params = {
            'contract': data_payslip['contract'].id,
            'start': date_from,
            'end': date_to,
        }
        data_total = {}
        self._get_total_concepts(
            data_payslip['cr'], data_total, query_params, query_params['contract'], concept)
        return sum(data_total.values())

    def no_apply_social_benefits(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        return skip

    def _get_credit_account_concept(self, contract):
        type_class = contract.contract_type_id.type_class
        section = contract.contract_type_id.section
        account_field_name = f'{type_class}_{section}_credit'
        account = getattr(self, account_field_name)
        return account

    ############################################################################
    # ------------------- CALCULO DE CONCEPTOS INDIVIDUALES -------------------#
    ############################################################################

    def _BASICO(self, data_payslip):
        type_class = data_payslip['contract'].contract_type_id.type_class
        if type_class == 'int':
            name, value, rate = 'SUELDO BASICO INTEGRAL', data_payslip['wage'], 1
        elif type_class == 'apr':
            salary_day = data_payslip['wage']
            if data_payslip['contract'].fiscal_type_id.code == '12':
                name, value, rate = 'CUOTA DE SOSTENIMIENTO LECTIVO', salary_day, 0.5
            elif data_payslip['contract'].fiscal_type_id.code == '19':
                year = data_payslip['period'].end.year - 1
                rate = 0.75 if data_payslip['economic_variables']['TSDES'][year] >= 10 else 1
                name, value = 'CUOTA DE SOSTENIMIENTO PRODUCTIVO', salary_day
            else:
                raise ValidationError(
                    'Defina <Tipo de Cotizante> en el contrato y asegurese de que tenga código. Códigos validos 12 y 19')
        elif type_class == 'reg':
            name, value, rate = self.name, data_payslip['wage'], 1
        else:
            raise ValidationError(
                'No ha definido el tipo de contrato (Regular, Aprendiz o Integral).')
        data_payslip['BASICO'] = value
        return {
            'name': name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': (value / data_payslip['worked_days']) if data_payslip['worked_days'] else 0,
            'qty': data_payslip['worked_days'],
            'rate': rate * 100,
            'total': value,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _SUB_TRANS(self, data_payslip):
        sena_lec = data_payslip['contract'].fiscal_type_id.code == '12'
        skip_sub_trans = data_payslip['contract'].skip_commute_allowance
        if sena_lec or skip_sub_trans:
            return
        sub_trans = data_payslip['economic_variables']['SUB_TRANS'][data_payslip['period'].start.year] / 30
        portion = 1 if data_payslip['period'].type_period == 'MONTHLY' else 2
        smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
        value_eval = 2 * smmlv / portion
        wage = data_payslip['full_wage'] / portion
        if wage < value_eval and data_payslip.get('earnings', 0) < value_eval:
            pay = True
            if data_payslip['contract'].fiscal_type_id.code == '19':
                pay &= data_payslip['politics']['hr_payroll_coll_coll_co.pays_sub_trans_train_prod']
            if not pay:
                return
            if data_payslip['contract'].remote_work_allowance:
                sub_conne = self.env.ref('hr_payroll_co.hc_sub_conne')
                name = sub_conne.name
                concept_id = sub_conne.id
            else:
                name = self.name
                concept_id = self.id
            total = sub_trans * data_payslip['worked_days']
            data_payslip[self.code] = total
            data_payslip['SUB_TRANS'] = total
            return {
                'name': name,
                'payslip_id': data_payslip['payslip_id'],
                'category': self.category,
                'value': sub_trans,
                'qty': data_payslip['worked_days'],
                'rate': 100,
                'total': total,
                'origin': 'local',
                'concept_id': concept_id,
                'novelty_id': None,
            }

    def _IBD(self, data_payslip):
        if 'IBD' not in data_payslip:
            self._compute_ibd(data_payslip)
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': data_payslip['IBD'],
            'qty': 1,
            'rate': 100,
            'total': data_payslip['IBD'],
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _DED_PENS(self, data_payslip):
        if data_payslip['contract'].contract_type_id.type_class == 'apr':
            return
        if 'IBD' not in data_payslip:
            self._compute_ibd(data_payslip)
        rate = data_payslip['politics']['hr_payroll_coll_co.pen_rate_employee']
        total = data_payslip['IBD'] * rate / 100
        data_payslip[NCI] += total
        total -= data_payslip.get(TPCP, {}).get('DED_PENS', 0)
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': data_payslip['IBD'],
            'qty': 1,
            'rate': rate,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _DED_EPS(self, data_payslip):
        if data_payslip['contract'].contract_type_id.type_class == 'apr':
            return
        if 'IBD' not in data_payslip:
            self._compute_ibd(data_payslip)
        rate = data_payslip['politics']['hr_payroll_co.eps_rate_employee']
        total = data_payslip['IBD'] * rate / 100
        data_payslip[NCI] += total
        total -= data_payslip.get(TPCP, {}).get('DED_EPS', 0)
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': data_payslip['IBD'],
            'qty': 1,
            'rate': rate,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _FOND_SOL(self, data_payslip):
        if data_payslip['contract'].contract_type_id.type_class == 'apr':
            return
        if 'IBD' not in data_payslip:
            self._compute_ibd(data_payslip)
        smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
        rate = self._compute_rate_fond_sol(smmlv, data_payslip['IBD'])
        if data_payslip['contract'].fiscal_subtype_id.code in ['00', False] and rate:
            previous = data_payslip.get(TPCP, {}).get('FOND_SOL', 0)
            total = data_payslip['IBD'] * rate / 100 - previous
            data_payslip[NCI] += total
            return {
                'name': self.name,
                'payslip_id': data_payslip['payslip_id'],
                'category': self.category,
                'value': data_payslip['IBD'],
                'qty': 1,
                'rate': rate,
                'total': total,
                'origin': 'local',
                'concept_id': self.id,
                'novelty_id': None,
            }

    def _FOND_SUB(self, data_payslip):
        if data_payslip['contract'].contract_type_id.type_class == 'apr':
            return
        if 'IBD' not in data_payslip:
            self._compute_ibd(data_payslip)
        smmlv = data_payslip['economic_variables']['SMMLV'][data_payslip['period'].start.year]
        rate = self._compute_rate_fond_sub(smmlv, data_payslip['IBD'])
        if data_payslip['contract'].fiscal_subtype_id.code in ['00', False] and rate:
            previous = data_payslip.get(TPCP, {}).get('FOND_SUB', 0)
            total = data_payslip['IBD'] * rate / 100 - previous
            data_payslip[NCI] += total
            return {
                'name': self.name,
                'payslip_id': data_payslip['payslip_id'],
                'category': self.category,
                'value': data_payslip['IBD'],
                'qty': 1,
                'rate': rate,
                'total': total,
                'origin': 'local',
                'concept_id': self.id,
                'novelty_id': None,
            }

    def _BRTF(self, data_payslip):
        if 'BRTF' not in data_payslip:
            self._compute_brtf(data_payslip)
        if data_payslip['BRTF'] == 0:
            return
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': data_payslip['BRTF'],
            'qty': 1,
            'rate': 100,
            'total': data_payslip['BRTF'],
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _RTEFTE(self, data_payslip):
        if 'BRTF' not in data_payslip:
            self._compute_brtf(data_payslip)
        if data_payslip['BRTF'] == 0:
            return
        previous = data_payslip.get(TPCP, {}).get('RTEFTE', 0)
        if data_payslip['contract'].apply_procedure_2:
            rate = data_payslip['contract'].withholding_percent
        else:
            rate = self._get_rate_trtefte(data_payslip, data_payslip['BRTF'])
        if rate == 0 and previous == 0:
            return
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': data_payslip['BRTF'],
            'qty': 1,
            'rate': rate,
            'total': data_payslip['BRTF'] * rate / 100 - previous,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _INDEM(self, data_payslip):
        if 'INDEM_value' not in data_payslip or 'INDEM_qty' not in data_payslip:
            self._compute_indem(data_payslip)
        value = data_payslip.get('INDEM_value', 0)
        qty = data_payslip.get('INDEM_qty', 0)
        if value == 0 or qty == 0:
            return
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': value,
            'qty': qty,
            'rate': 100,
            'total': value * qty,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _RTF_INDEM(self, data_payslip):
        if 'INDEM_value' not in data_payslip or 'INDEM_qty' not in data_payslip:
            self._compute_indem(data_payslip)
        value = data_payslip.get('INDEM_value', 0)
        qty = data_payslip.get('INDEM_qty', 0)
        uvt = data_payslip['economic_variables']['UVT'][data_payslip['period'].start.year]
        if value * 30 <= 204 * uvt:
            return
        value *= qty * 0.75
        rate = 20
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': value,
            'qty': 1,
            'rate': rate,
            'total': value * rate / 100,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _PRIMA_LIQ(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        if skip:
            return
        if not data_payslip['contract'].settlement_date:
            raise ValidationError('El contrato no tiene fecha de liquidación.')
        date_to = data_payslip['contract'].settlement_date
        from_month = 1 if data_payslip['period'].start.month <= 6 else 7
        date_from = data_payslip['period'].start.replace(
            month=from_month, day=1)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start
        base, qty, total = self._compute_social_benefits(
            data_payslip, date_from, date_to)
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': base,
            'qty': qty,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _PRIMA(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        if skip:
            return
        from_month = 1 if data_payslip['period'].start.month <= 6 else 7
        to_month = 6 if data_payslip['period'].start.month <= 6 else 12
        to_day = 30 if data_payslip['period'].start.month <= 6 else 31
        date_from = data_payslip['period'].start.replace(
            month=from_month, day=1)
        date_to = data_payslip['period'].start.replace(
            month=to_month, day=to_day)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start
        base, qty, total = self._compute_social_benefits(
            data_payslip, date_from, date_to)
        total_previous = {}
        self._get_total_concepts(
            data_payslip['cr'], total_previous, {'start': data_payslip['period'].start, 'end': data_payslip['period'].end}, data_payslip['contract'].id, ('PRIMA',))
        total -= total_previous.get('PRIMA', 0)
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': base,
            'qty': qty,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _CES_LIQ(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        if skip:
            return
        if not data_payslip['contract'].settlement_date:
            raise ValidationError('El contrato no tiene fecha de liquidación.')
        date_to = data_payslip['contract'].settlement_date
        date_from = data_payslip['period'].start.replace(month=1, day=1)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start
        base, qty, total = self._compute_social_benefits(
            data_payslip, date_from, date_to)
        data_payslip['ICES_LIQ'] = [total, 0.12*qty/360]
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': base,
            'qty': qty,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _CES(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        if skip:
            return
        if data_payslip['period'].end.month not in (1, 2):
            raise ValidationError(
                'Las cesantias solo se pueden calcular en nominas de Enero o Febrero.')

        date_ref = data_payslip['period'].end - relativedelta(years=1)
        date_from = date_ref.replace(month=1, day=1)
        date_to = date_ref.replace(month=12, day=31)

        if date_to < data_payslip['contract'].date_start:
            raise ValidationError(
                'Imposible calcular cesantias del año anterior')

        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start

        base, qty, total = self._compute_social_benefits(
            data_payslip, date_from, date_to)

        data_payslip['CES'] = total

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': base,
            'qty': qty,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _ICES(self, data_payslip):
        skip = data_payslip['contract'].fiscal_type_id.code in ['12', '19']
        skip |= data_payslip['contract'].contract_type_id.type_class == 'int'
        if skip:
            return

        if data_payslip['period'].end.month not in (1, 2):
            raise ValidationError(
                'Los intereses de cesantias solo se pueden calcular en nominas de Enero o Febrero.')

        date_ref = data_payslip['period'].end - relativedelta(years=1)
        date_from = date_ref.replace(month=1, day=1)
        date_to = date_ref.replace(month=12, day=31)

        if date_to < data_payslip['contract'].date_start:
            raise ValidationError(
                'Imposible calcular los intereses de cesantias del año anterior')

        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start

        base, qty, ces = self._compute_social_benefits(
            data_payslip, date_from, date_to)

        rate = 0.12 * qty / 360
        total = ces * rate

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': ces,
            'qty': 1,
            'rate': rate * 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _ICES_LIQ(self, data_payslip):
        if 'ICES_LIQ' not in data_payslip:
            raise ValidationError(
                'No se ha calculado cesantías de liquidación')
        value, rate = data_payslip['ICES_LIQ']
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': value,
            'qty': 1,
            'rate': rate * 100,
            'total': value * rate,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _PRV_CES(self, data_payslip):
        if self.no_apply_social_benefits(data_payslip):
            return

        date_to = data_payslip['period'].end
        if data_payslip['contract'].settlement_date and data_payslip['contract'].settlement_date < date_to:
            date_to = data_payslip['contract'].settlement_date
        date_from = data_payslip['period'].start.replace(month=1, day=1)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start

        _, worked_days_year, layoff = self._compute_layoff(
            data_payslip, date_from, date_to)

        provision_layoff = self._get_total_previous(
            data_payslip, date_from, date_to)
        total = layoff - provision_layoff

        rate_worked_days = worked_days_year / 360
        interest = layoff * 0.12 * rate_worked_days
        data_payslip['PRV_ICES'] = (
            interest, date_from, date_to, rate_worked_days)

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': layoff,
            'qty': worked_days_year,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _PRV_ICES(self, data_payslip):
        if self.no_apply_social_benefits(data_payslip):
            return

        if 'PRV_ICES' not in data_payslip:
            raise ValidationError(
                'No se ha calculado la provisión de cesantías')

        interest, date_from, date_to, rate_worked_days = data_payslip['PRV_ICES']
        provision_interest = self._get_total_previous(
            data_payslip, date_from, date_to)

        total = interest - provision_interest

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': interest,
            'qty': 1,
            'rate': rate_worked_days * 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _PRV_PRIMA(self, data_payslip):
        if self.no_apply_social_benefits(data_payslip):
            return

        date_to = data_payslip['period'].end
        if data_payslip['contract'].settlement_date and data_payslip['contract'].settlement_date < date_to:
            date_to = data_payslip['contract'].settlement_date
        from_month = 1 if data_payslip['period'].start.month <= 6 else 7
        date_from = data_payslip['period'].start.replace(
            month=from_month, day=1)
        if date_from < data_payslip['contract'].date_start:
            date_from = data_payslip['contract'].date_start

        _, worked_days_semester, prima = self._compute_prima(
            data_payslip, date_from, date_to)

        provision_prima = self._get_total_previous(
            data_payslip, date_from, date_to)
        total = prima - provision_prima

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': prima,
            'qty': worked_days_semester,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _NETO_CES(self, data_payslip):
        ces_codes = ['CES']
        total = sum([round(data_payslip.get(code, 0)) for code in ces_codes])

        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': total,
            'qty': 1,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }

    def _NETO(self, data_payslip):
        total_earnings = ['earnings', 'o_salarial_earnings',
                          'comp_earnings', 'o_rights', 'o_earnings', 'non_taxed_earnings']
        total_deductions = ['deductions']
        total = 0
        for te in total_earnings:
            total += round(data_payslip.get(te, 0))
        for td in total_deductions:
            total -= round(data_payslip.get(td, 0))

        ces_codes = ['CES']
        total -= sum([round(data_payslip.get(code, 0)) for code in ces_codes])
        return {
            'name': self.name,
            'payslip_id': data_payslip['payslip_id'],
            'category': self.category,
            'value': total,
            'qty': 1,
            'rate': 100,
            'total': total,
            'origin': 'local',
            'concept_id': self.id,
            'novelty_id': None,
        }
