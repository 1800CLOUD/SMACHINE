# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND

# ---------------------------------------------------------
# Budgets
# ---------------------------------------------------------
class AccountBudgetPost(models.Model):
    _name = "account.budget.post"
    _order = "name"
    _description = "Budgetary Position"

    name = fields.Char('Name', required=True)
    account_ids = fields.Many2many('account.account', 'account_budget_rel', 'budget_id', 'account_id', 'Accounts',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)

    def _check_account_ids(self, vals):
        # Raise an error to prevent the account.budget.post to have not specified account_ids.
        # This check is done on create because require=True doesn't work on Many2many fields.
        if 'account_ids' in vals:
            account_ids = self.new({'account_ids': vals['account_ids']}, origin=self).account_ids
        else:
            account_ids = self.account_ids
        if not account_ids:
            raise ValidationError(_('The budget must have at least one account.'))

    @api.model
    def create(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).create(vals)

    def write(self, vals):
        self._check_account_ids(vals)
        return super(AccountBudgetPost, self).write(vals)


class CrossoveredBudget(models.Model):
    _name = "crossovered.budget.seller"
    _description = "Presupuesto vendedor"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nombre', required=True, states={'done': [('readonly', True)]})
    user_id = fields.Many2one('res.users', 'Responsable', default=lambda self: self.env.user)
    date_from = fields.Date('Desde', states={'done': [('readonly', True)]})
    date_to = fields.Date('Hasta', states={'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('cancel', 'Cancelado'),
        ('confirm', 'Confirmado'),
        ('validate', 'Validado'),
        ('done', 'Hecho')
        ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, tracking=True)
    crossovered_budget_line = fields.One2many('crossovered.budget.lines.sellers', 'crossovered_budget_id', 'Lineas de presupuesto',
        states={'done': [('readonly', True)]}, copy=True)
    company_id = fields.Many2one('res.company', 'Compañia', required=True,
        default=lambda self: self.env.company)

    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    def action_budget_draft(self):
        self.write({'state': 'draft'})

    def action_budget_validate(self):
        self.write({'state': 'validate'})

    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    def action_budget_done(self):
        self.write({'state': 'done'})


class CrossoveredBudgetLines(models.Model):
    _name = "crossovered.budget.lines.sellers"
    _description = "Presupuestos por vendedor"

    name = fields.Char(compute='_compute_line_name')
    crossovered_budget_id = fields.Many2one('crossovered.budget.seller', 'Presupuesto', ondelete='cascade', index=True, required=True)
    date_from = fields.Date('Fecha inicial', required=True)
    date_to = fields.Date('Fecha Limite', required=True)
    paid_date = fields.Date('Fecha de pago')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    planned_amount = fields.Monetary(
        'Importe previsto', required=True,
        help="Cantidad que planeas ganar/gastar. Registra una cantidad positiva si es un ingreso y negativa si es un costo")
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Importe real', help="Cantidad real ganada/gastada")
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount', string='Importe teórico',
        help="Cantidad presunta ganada/gastada a la fecha.")
    percentage = fields.Float(
        compute='_compute_percentage', string='Logro',
        help="Indica si esta por debajo o por encima del presupuesto.")
    company_id = fields.Many2one(related='crossovered_budget_id.company_id', comodel_name='res.company',
        string='Compañia', store=True, readonly=True)
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    crossovered_budget_state = fields.Selection(related='crossovered_budget_id.state', string='Budget State', store=True, readonly=True)
    seller_id = fields.Many2one('res.users', 'Vendedor', required=True)
    brand_id = fields.Many2one('product.brand', 'Marca')

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        # overrides the default read_group in order to compute the computed fields manually for the group

        fields_list = {'practical_amount', 'theoritical_amount', 'percentage'}

        # Not any of the fields_list support aggregate function like :sum
        def truncate_aggr(field):
            field_no_aggr = field.split(':', 1)[0]
            if field_no_aggr in fields_list:
                return field_no_aggr
            return field
        fields = {truncate_aggr(field) for field in fields}

        # Read non fields_list fields
        result = super(CrossoveredBudgetLines, self).read_group(
            domain, list(fields - fields_list), groupby, offset=offset,
            limit=limit, orderby=orderby, lazy=lazy)

        # Populate result with fields_list values
        if fields & fields_list:
            for group_line in result:

                # initialise fields to compute to 0 if they are requested
                if 'practical_amount' in fields:
                    group_line['practical_amount'] = 0
                if 'theoritical_amount' in fields:
                    group_line['theoritical_amount'] = 0
                if 'percentage' in fields:
                    group_line['percentage'] = 0
                    group_line['practical_amount'] = 0
                    group_line['theoritical_amount'] = 0

                domain = group_line.get('__domain') or domain
                all_budget_lines_that_compose_group = self.search(domain)

                for budget_line_of_group in all_budget_lines_that_compose_group:
                    if 'practical_amount' in fields or 'percentage' in fields:
                        group_line['practical_amount'] += budget_line_of_group.practical_amount

                    if 'theoritical_amount' in fields or 'percentage' in fields:
                        group_line['theoritical_amount'] += budget_line_of_group.theoritical_amount

                    if 'percentage' in fields:
                        if group_line['theoritical_amount']:
                            # use a weighted average
                            group_line['percentage'] = float(
                                (group_line['practical_amount'] or 0.0) / group_line['theoritical_amount'])

        return result

    def _is_above_budget(self):
        for line in self:
            if line.theoritical_amount >= 0:
                line.is_above_budget = line.practical_amount > line.theoritical_amount
            else:
                line.is_above_budget = line.practical_amount < line.theoritical_amount

    @api.depends("crossovered_budget_id")
    def _compute_line_name(self):
        #just in case someone opens the budget line in form view
        for record in self:
            computed_name = record.crossovered_budget_id.name
            record.name = computed_name

    def _compute_practical_amount(self):
        for line in self:
            date_to = line.date_to
            date_from = line.date_from
            practical_amount = 0.0

            aml_obj = self.env['account.move.line']

            domain = [
                      ('date', '>=', date_from),
                      ('date', '<=', date_to),
                      ('parent_state', '=', 'posted'),
                      ('move_id.invoice_user_id', '=', line.seller_id.id),  # Filter by seller
                      ('product_id.product_brand_id', '=', line.brand_id.id),  # Filter by brand
                      ]

            where_query = aml_obj._where_calc(domain)
            aml_obj._apply_ir_rules(where_query, 'read')
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            select = """
                        SELECT SUM(price_subtotal * (CASE WHEN (SELECT move_type FROM account_move WHERE account_move.id = account_move_line.move_id) = 'out_invoice' THEN 1 ELSE -1 END))
                        FROM """ + from_clause + """ WHERE """ + where_clause
            self.env.cr.execute(select, where_clause_params)
            practical_amount = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = practical_amount

    @api.depends('date_from', 'date_to')
    def _compute_theoritical_amount(self):
        # beware: 'today' variable is mocked in the python tests and thus, its implementation matter
        today = fields.Date.today()
        for line in self:
            if line.paid_date:
                if today <= line.paid_date:
                    theo_amt = 0.00
                else:
                    theo_amt = line.planned_amount
            else:
                if not line.date_from or not line.date_to:
                    line.theoritical_amount = 0
                    continue
                # One day is added since we need to include the start and end date in the computation.
                # For example, between April 1st and April 30th, the timedelta must be 30 days.
                line_timedelta = line.date_to - line.date_from + timedelta(days=1)
                elapsed_timedelta = today - line.date_from + timedelta(days=1)

                if elapsed_timedelta.days < 0:
                    # If the budget line has not started yet, theoretical amount should be zero
                    theo_amt = 0.00
                elif line_timedelta.days > 0 and today < line.date_to:
                    # If today is between the budget line date_from and date_to
                    theo_amt = (elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                else:
                    theo_amt = line.planned_amount
            line.theoritical_amount = theo_amt

    def _compute_percentage(self):
        for line in self:
            if line.company_id.percent_budget == 'theoritical':
                line.percentage = float((line.practical_amount or 0.0) / line.theoritical_amount)
            elif line.company_id.percent_budget == 'planned':
                line.percentage = float((line.practical_amount or 0.0) / line.planned_amount)
            else:
                line.percentage = 0.00

    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        # suggesting a budget based on given dates
        domain_list = []
        if self.date_from:
            domain_list.append(['|', ('date_from', '<=', self.date_from), ('date_from', '=', False)])
        if self.date_to:
            domain_list.append(['|', ('date_to', '>=', self.date_to), ('date_to', '=', False)])
        # don't suggest if a budget is already set and verifies condition on its dates
        if domain_list and not self.crossovered_budget_id.filtered_domain(AND(domain_list)):
            self.crossovered_budget_id = self.env['crossovered.budget.seller'].search(AND(domain_list), limit=1)

    @api.onchange('crossovered_budget_id')
    def _onchange_crossovered_budget_id(self):
        if self.crossovered_budget_id:
            self.date_from = self.date_from or self.crossovered_budget_id.date_from
            self.date_to = self.date_to or self.crossovered_budget_id.date_to

    #@api.constrains('general_budget_id', 'analytic_account_id')
    #def _must_have_analytical_or_budgetary_or_both(self):
    #    for record in self:
    #        if not record.analytic_account_id and not record.general_budget_id:
    #            raise ValidationError(
    #                _("You have to enter at least a budgetary position or analytic account on a budget line."))

    def action_open_budget_entries(self):
        #if self.analytic_account_id:
        #    # if there is an analytic account, then the analytic items are loaded
        #    action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
        #    action['domain'] = [('account_id', '=', self.analytic_account_id.id),
        #                        ('date', '>=', self.date_from),
        #                        ('date', '<=', self.date_to)
        #                        ]
        #    if self.general_budget_id:
        #        action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]

        # otherwise the journal entries booked on the accounts of the budgetary postition are opened
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
        action['domain'] = [('move_id.invoice_user_id', '=',
                             self.seller_id.id),
                            ('date', '>=', self.date_from),
                            ('date', '<=', self.date_to)
                            ]
        if self.brand_id:
            action['domain'] += [('product_id.product_brand_id', '=', self.brand_id.id)]
        return action

    @api.constrains('date_from', 'date_to')
    def _line_dates_between_budget_dates(self):
        for line in self:
            budget_date_from = line.crossovered_budget_id.date_from
            budget_date_to = line.crossovered_budget_id.date_to
            if line.date_from:
                date_from = line.date_from
                if (budget_date_from and date_from < budget_date_from) or (budget_date_to and date_from > budget_date_to):
                    raise ValidationError(_('"Start Date" of the budget line should be included in the Period of the budget'))
            if line.date_to:
                date_to = line.date_to
                if (budget_date_from and date_to < budget_date_from) or (budget_date_to and date_to > budget_date_to):
                    raise ValidationError(_('"End Date" of the budget line should be included in the Period of the budget'))
