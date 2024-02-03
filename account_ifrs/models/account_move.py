
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ifrs_type = fields.Selection(
        selection=[
            ('both', 'Both'),
            ('local', 'Local'),
            ('ifrs', 'IFRS'),
        ],
        string='IFRS Type',
        default='both',
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [
        (
            'check_ifrs_credit_debit',
            'CHECK(ifrs_credit + ifrs_debit >= 0 AND ifrs_credit * ifrs_debit = 0)',
            'Wrong IFRS credit or IFRS debit value in accounting entry !'
        ),
    ]

    ifrs_type = fields.Selection(
        related='move_id.ifrs_type',
        store=True
    )
    ifrs_debit = fields.Monetary(
        string='IFRS Debit',
        currency_field='company_currency_id',
        compute='_compute_ifrs',
        inverse='_inverse_ifrs',
        store=True
    )
    ifrs_credit = fields.Monetary(
        string='IFRS Credit',
        currency_field='company_currency_id',
        compute='_compute_ifrs',
        inverse='_inverse_ifrs',
        store=True
    )
    ifrs_balance = fields.Monetary(
        string='IFRS Balance',
        currency_field='company_currency_id',
        compute='_compute_ifrs_balance',
        store=True,
    )

    @api.depends('ifrs_type', 'debit', 'credit')
    def _compute_ifrs(self):
        for line in self:
            vals = {}
            if line.ifrs_type == 'both':
                vals.update(ifrs_debit=line.debit, ifrs_credit=line.credit)
            if line.ifrs_type == 'local':
                vals.update(ifrs_debit=0.0, ifrs_credit=0.0)
            if line.ifrs_type == 'ifrs':
                line = line.with_context(check_move_validity=False)
                vals.update(ifrs_debit=line.debit, ifrs_credit=line.credit)
                vals.update(debit=0.0, credit=0.0)
            line.update(vals)

    def _inverse_ifrs(self):
        for line in self:
            vals = {}
            if line.ifrs_type == 'ifrs':
                vals.update(debit=0.0, credit=0.0)
            line.update(vals)

    @api.depends('ifrs_debit', 'ifrs_credit')
    def _compute_ifrs_balance(self):
        for line in self:
            ifrs_balance = line.ifrs_debit - line.ifrs_credit
            line.update({'ifrs_balance': ifrs_balance})
