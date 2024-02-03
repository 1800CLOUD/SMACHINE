# -*- coding: utf-8 -*-

import logging
from tokenize import group

from odoo import _, fields, models
from odoo.exceptions import ValidationError

REPORT_TYPE = {
    'local': 'Local',
    'ifrs': 'NIIF'
}

_logger = logging.getLogger(__name__)


class AccountBalanceWizard(models.Model):
    _name = 'account.balance.wizard'
    _description = 'Balance Report Wizard'

    accounts_ids = fields.Many2many(comodel_name='account.account',
                                    string='Accounts')
    date_from = fields.Date('From',
                            default=fields.Date.today())
    date_to = fields.Date('To',
                          default=fields.Date.today())
    group_by = fields.Boolean('Levels?',
                              default=False,)
    line_state = fields.Boolean('Posted?',
                                default=True)
    partner_by = fields.Boolean('By partner')
    partners_ids = fields.Many2many(comodel_name='res.partner',
                                    string='Partners')
    report_type = fields.Selection(selection=[('local', 'Local'),
                                              ('ifrs', 'IFRS')],
                                   default='local',
                                   required="True")
    no_zero = fields.Boolean('Skip zero balances',
                             default=True)

    def action_confirm(self):
        report = self.env.ref('account_report.report_account_balance')
        data = self.prepare_data()
        return report.report_action(self, data=data)

    def update_amounts_line(self, sum_line):
        sum_line = {
            'bold': sum_line['bold'],
            'group': sum_line['group'],
            'account_id': sum_line['account_id'],
            'parent_id': '',
            'group_id': '',
            'code': sum_line['code'],
            'name': sum_line['name'],
            'vat': '',
            'partner': '',
            'residual': sum_line['residual'],
            'debit': sum_line['debit'],
            'credit': sum_line['credit'],
            'balance': sum_line['balance'],
        }
        return sum_line

    def prepare_data(self):
        query_data = self.prepare_data_query()
        sum_line = query_data.pop()
        copy_data = list(query_data)

        if self.group_by:
            aids = [rd.get('account_id') for rd in copy_data]
            aids = list(set(aids))
            accounts = self.env['account.account'].browse(aids)
            for account in accounts:
                datas = [
                    rd for rd in copy_data if rd.get(
                        'account_id') == account.id
                ]
                values = {
                    'bold': True,
                    'group': False,
                    'account_id': account.id,
                    'parent_id': False,
                    'group_id': '',
                    'code': account.code,
                    'name': account.name,
                }
                if self.partner_by:
                    values.update({
                        'vat': '',
                        'partner': '',
                    })
                values.update({
                    'residual': sum(d.get('residual') for d in datas),
                    'debit': sum(d.get('debit') for d in datas),
                    'credit': sum(d.get('credit') for d in datas),
                    'balance': sum(d.get('balance') for d in datas),
                })
                query_data.append(values)

        copy_data = list(query_data)
        parents = False
        if self.group_by:
            aids = [cp.get('account_id') for cp in copy_data]
            aids = list(set(aids))
            accounts = self.env['account.account'].browse(aids)
            groups = self.env['account.group'].search([])
            parents = groups
            code_groups = []
            while parents:
                for parent in parents:
                    if parent.id not in code_groups:
                        aids = parent.compute_account_ids.ids
                        datas = [
                            cp for cp in copy_data if cp.get('bold') and
                            cp.get('account_id') in aids
                        ]
                        values = {
                            'bold': True,
                            'group': True,
                            'account_id': False,
                            'parent_id': parent.parent_id and
                            parent.parent_id.id or
                            False,
                            'group_id': parent.id,
                            'code': parent.code,
                            'name': parent.name,
                        }

                        if self.partner_by:
                            values.update({
                                'vat': '',
                                'partner': '',
                            })

                        values.update({
                            'residual': sum(d.get('residual') for d in datas),
                            'debit': sum(d.get('debit') for d in datas),
                            'credit': sum(d.get('credit') for d in datas),
                            'balance': sum(d.get('balance') for d in datas),
                        })
                        if self.no_zero and \
                            (values['residual'] != 0 or
                             values['balance'] != 0):
                            # and values['debit'] - values['credit'] != 0:
                            query_data.append(values)
                        elif not self.no_zero:
                            query_data.append(values)
                    code_groups.append(parent.id)
                parents = parents.parent_id

            if self.group_by and groups:
                query_data = sorted(
                    query_data,
                    key=lambda r: [r.get('code'), not r.get('bold')]
                )

        if self.partner_by or parents:
            sum_line = self.update_amounts_line(sum_line)

        query_data.append(sum_line)
        return {'report_data': query_data and query_data or []}

    def prepare_data_query(self):
        query = self.prepare_query()
        self.env.cr.execute(query)
        data_query = self.env.cr.dictfetchall()
        data_query = self.sum_amounts(data_query)
        return data_query

    def sum_amounts(self, data_query):
        accounts_list = []
        for line in data_query:
            if line['account_id'] not in accounts_list:
                accounts_list.append(line['account_id'])
        residual = sum(i['residual'] for i in data_query)
        debit = sum(i['debit'] for i in data_query)
        credit = sum(i['credit'] for i in data_query)
        balance = sum(i['balance'] for i in data_query)
        sum_line = {
            'bold': True,
            'group': False,
            'account_id': '',
            'parent_id': '',
            'group_id': '',
            'code': '',
            'name': 'Total',
            'residual': residual,
            'debit': debit,
            'credit': credit,
            'balance': balance
        }
        data_query.append(sum_line)
        return data_query

    def prepare_query(self):
        query_account = self.prepare_query_account()
        query_before = self.prepare_query_before()
        query_after = self.prepare_query_after()

        query = """
        select 
            False as bold,
            False as group,
            aml.account_id,
            '' as parent_id,
            '' as group_id,
            aml.code,
            aml.name,
        """

        if self.partner_by:
            query += """
                aml.vat,
                aml.partner,
            """

        query += """
        coalesce(amlb.debit, 0) - coalesce(amlb.credit, 0) as residual,
        coalesce(amla.debit, 0) as debit,
        coalesce(amla.credit, 0) as credit,
        (coalesce(amlb.debit, 0) - coalesce(amlb.credit, 0)) +
         (coalesce(amla.debit, 0) - coalesce(amla.credit, 0)) as balance
        from (%s) aml
        left join (%s) amlb on
        """ % (query_account, query_before)

        if self.partner_by:
            query += """
             (
                (amlb.account_id = aml.account_id AND
                 amlb.partner_id = aml.partner_id)
                OR
                (amlb.account_id = aml.account_id AND
                 amlb.partner_id is null AND aml.partner_id is null)
            )
            """
        else:
            query += """
             amlb.account_id = aml.account_id
            """

        query += """
        left join (%s) amla on
        """ % (query_after)

        if self.partner_by:
            query += """
             (
                (amla.account_id = aml.account_id AND
                 amla.partner_id = aml.partner_id)
                OR
                (amla.account_id = aml.account_id AND
                 amla.partner_id is null AND aml.partner_id is null)
            )
            """
        else:
            query += """
             amla.account_id = aml.account_id
            """
        if self.no_zero:
            query += """
            where coalesce(amlb.debit, 0) - coalesce(amlb.credit, 0) != 0
                or (
                    coalesce(amlb.debit, 0) - coalesce(amlb.credit, 0)
                ) + (
                    coalesce(amla.debit, 0) - coalesce(amla.credit, 0)
                ) != 0
            """

        return query

    def prepare_query_account(self):
        date = self.date_to.strftime('%Y-%m-%d')
        ids_companies = self.env.companies.ids
        ids_companies = str(tuple(ids_companies)).replace(',)', ')')

        query = """
        select aa.id as account_id, aa.code, aa.name
        """

        if self.partner_by:
            query += """
            , aml.partner_id, rp.vat, rp.name as partner
            """

        query += """
        from account_move_line aml
        """

        query += """
            inner join account_account aa on aa.id = aml.account_id
            """

        if self.partner_by:
            query += """
            left join res_partner rp on rp.id = aml.partner_id
            """

        query += """
        where aml.date <= '%s'
        and aml.company_id in %s
        """ % (date, ids_companies)

        if self.line_state:
            query += """
            and aml.parent_state = 'posted'
            """

        if self.accounts_ids:
            accounts_ids = self.accounts_ids.ids
            aids = str(tuple(accounts_ids)).replace(',)', ')')
            query += """
            and aml.account_id in %s
            """ % aids

        if self.partner_by and self.partners_ids:
            partners_ids = self.partners_ids.ids
            pids = str(tuple(partners_ids)).replace(',)', ')')
            query += """
            and aml.partner_id in %s
            """ % pids

        query += """
        group by aa.id, aa.code, aa.name
        """

        if self.partner_by:
            query += """
            , aml.partner_id, rp.vat, rp.name
            """

        query += """
        order by aa.code
        """

        return query

    def prepare_query_before(self):
        date = self.date_from.strftime('%Y-%m-%d')
        ids_companies = self.env.companies.ids
        ids_companies = str(tuple(ids_companies)).replace(',)', ')')

        query = """
        select aa.id as account_id,
        """

        if self.partner_by:
            query += """
            aml.partner_id,
            """

        if self.report_type == 'ifrs':
            query += """
            sum(aml.ifrs_debit) as debit,
            sum(aml.ifrs_credit) as credit
            """
        else:
            query += """
            sum(aml.debit) as debit,
            sum(aml.credit) as credit
            """

        query += """
        from account_move_line aml
        """

        query += """
            inner join account_account aa on aa.id = aml.account_id
            """

        query += """
        where aml.date < '%s'
        """ % date
        query += """
        and aml.company_id in %s
        """ % ids_companies

        if self.line_state:
            query += """
            and aml.parent_state = 'posted'
            """
        if self.report_type == 'ifrs':
            query += "and aml.ifrs_type != 'local'"
        else:
            query += "and aml.ifrs_type != 'ifrs'"

        if self.partner_by and self.partners_ids:
            partners_ids = self.partners_ids.ids
            pids = str(tuple(partners_ids)).replace(',)', ')')
            query += """
            and aml.partner_id in %s
            """ % pids

        query += """
        group by aa.id
        """

        if self.partner_by:
            query += """
            , aml.partner_id
            """

        return query

    def prepare_query_after(self):
        date_from = self.date_from.strftime('%Y-%m-%d')
        date_to = self.date_to.strftime('%Y-%m-%d')
        ids_companies = self.env.companies.ids
        ids_companies = str(tuple(ids_companies)).replace(',)', ')')

        query = """
        select aa.id as account_id,
        """

        if self.partner_by:
            query += """
            aml.partner_id,
            """

        if self.report_type == 'ifrs':
            query += """
            sum(aml.ifrs_debit) as debit,
            sum(aml.ifrs_credit) as credit
            """
        else:
            query += """
            sum(aml.debit) as debit,
            sum(aml.credit) as credit
            """

        query += """
        from account_move_line aml
        """

        query += """
            inner join account_account aa on aa.id = aml.account_id
            """

        query += """
        where aml.date between '%s' and '%s'
        """ % (date_from, date_to)
        query += """
        and aml.company_id in %s
        """ % ids_companies

        if self.line_state:
            query += """
            and aml.parent_state = 'posted'
            """

        if self.report_type == 'ifrs':
            query += "and aml.ifrs_type != 'local'"
        else:
            query += "and aml.ifrs_type != 'ifrs'"

        query += """
        group by aa.id
        """

        if self.partner_by:
            query += """
            , aml.partner_id
            """

        return query

    def prepare_header(self):
        report_header = [
            ('code', _('Code')),
            ('name', _('Name')),
        ]

        if self.partner_by:
            report_header += [
                ('vat', 'NIT'),
                ('partner', _('Partner'))
            ]

        report_header += [
            ('residual', _('Residual amount (balance)')),
            ('debit', _('Debit')),
            ('credit', _('Credit')),
            ('balance', _('Balance amount'))
        ]

        return report_header

    def preview_html(self):
        self.ensure_one()
        action_report = self.env["ir.actions.report"].search(
            [
                ("report_name", "=",
                 'account_report.account_balance_template'),
                ("report_type", "=", 'qweb-html')
            ],
            limit=1,
        )
        if not action_report:
            raise ValidationError(_(
                'Not found report ID: account_report.account_balance_template'
            ))
        data_report = {}
        out = action_report.report_action(self, data=data_report)
        return out

    def data_report_preview(self):
        self.ensure_one()
        header = self.prepare_header()
        data = self.prepare_data()

        report_name = self.report_type == 'local' and \
            _('Balance de Pruebas') or \
            _('Balance de Pruebas NIIF')
        company = self.env.company.name
        vat = self.env.company.vat
        date_from = self.date_from
        date_to = self.date_to

        html_text = '''
            <div class="report_aux">
                table_header
            </div>
            <div class="act_as_table list_table" style="margin-top: 10px;"/>
            <div class="report_aux">
                <div class="act_as_table data_table">
                    <div class="act_as_thead">
                        <div class="act_as_row labels">
                            th_report
                        </div>
                    </div>
                    data_report
                </div>
            </div>
        '''

        # THEAD
        th_text = ''
        for th in header:
            th_text += '<div class="act_as_cell" style="font-size: 13px; font-family: helvetica;">%s</div>' % th[1]

        html_text = html_text.replace('th_report', th_text)

        # TBODY
        tr_text = ''
        c = 1
        for tr_data in data.get('report_data', []):
            tr_text += '<div class="act_as_row lines">'
            bold = False
            for k, v in tr_data.items():
                if k == 'bold':
                    bold = v
                elif k in ('group', 'account_id', 'parent_id', 'group_id'):
                    continue
                else:
                    class_span = ' '.join([
                        bold and
                        'bold-cell-report back-cell' or
                        'normal-cell-report',
                        k in ('initial', 'debit', 'credit', 'final',
                              'balance', 'residual') and 'amount' or 'left'
                    ])
                    tr_text += '<div class="act_as_cell %s" style="font-size: 13px; font-family: helvetica;">%s</div>' % (
                        class_span,
                        type(v) in (type(2), type(2.3)) and \
                        '{:_.2f}'.format(v).replace('.',',').replace('_','.') or \
                        v or ''
                    )
            tr_text += '</div>'
            c += 1

        html_text = html_text.replace('data_report', tr_text)
        now = fields.Datetime.context_timestamp(
            self,
            fields.Datetime.now()
        ).strftime('%d-%m-%Y %H:%M:%S')

        # HEADER
        table_h = '''
           <div class="act_as_table data_table">
                <div class="act_as_row">
                    <div class="act_as_cell labels" style="font-size: 13px;">{inf_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{inf_val}</div>
                    <div class="act_as_cell labels" style="font-size: 13px;">{dat_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{dat_val}</div>
                </div>
                <div class="act_as_row">
                    <div class="act_as_cell labels" style="font-size: 13px;">{com_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{com_val}</div>
                    <div class="act_as_cell labels" style="font-size: 13px;">{ini_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{ini_val}</div>
                </div>
                <div class="act_as_row">
                    <div class="act_as_cell labels" style="font-size: 13px;">{nit_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{nit_val}</div>
                    <div class="act_as_cell labels" style="font-size: 13px;">{end_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{end_val}</div>
                </div>
                <div class="act_as_row">
                    <div class="act_as_cell labels" style="font-size: 13px;">{type_tag}</div>
                    <div class="act_as_cell" style="font-size: 13px;">{type_val}</div>
                    <div class="act_as_cell labels" style="font-size: 13px;"></div>
                    <div class="act_as_cell" style="font-size: 13px;"></div>
                </div>
            </div>
        '''.format(
            inf_tag=_('Report'),
            inf_val=report_name,
            dat_tag=_('Date'),
            dat_val=now,
            com_tag=_('Company'),
            com_val=company,
            ini_tag=_('From'),
            ini_val=date_from,
            nit_tag=_('NIT'),
            nit_val=vat,
            end_tag=_('To'),
            end_val=date_to,
            type_tag=_('Type'),
            type_val=REPORT_TYPE.get(self.report_type)
        )

        html_text = html_text.replace('table_header', table_h)
        return html_text
