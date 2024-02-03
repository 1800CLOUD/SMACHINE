
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    base_calculate = fields.Boolean(
        string='Calculate base?',
        default=True,
        help="Automatically calculate base taxes",
    )

    city_id = fields.Many2one('res.city')

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            self.city_id = self.company_id.partner_id.city_id

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self.move_type in ('in_invoice', 'in_refund'):
            self.city_id = self.partner_id.city_id
        return res

    def calculate_base(self):
        if not self.env.context.get('calculate_base', True):
            return False
        invoices = self.filtered(lambda m: m.is_invoice())
        moves = invoices.filtered(lambda m: m.state == 'draft')
        for move in moves:
            move._calculate_base()

    def _calculate_base(self):
        Tax = self.env['account.tax']

        if not self.is_invoice():
            return False
        if self.state != 'draft':
            return False
        if not self.base_calculate:
            return False

        taxes = Tax
        for line in self.invoice_line_ids:
            taxes |= line._get_computed_taxes()

        if not any(t.base_minimum for t in taxes):
            return False

        amount_untaxed = self.with_context(calculate_base=False).amount_untaxed
        taxes_retention = taxes.filtered(lambda t: t.base_minimum)
        taxes_add = Tax
        taxes_rem = Tax

        for tax in taxes_retention:
            if self.move_type in ('in_invoice', 'in_refund'):
                tax = tax.with_context(partner_id=self.partner_id)
            base_amount, base_tax = tax.compute_base_tax(city=self.city_id)

            if amount_untaxed >= base_amount:
                taxes_rem |= tax
                taxes_add |= base_tax
            else:
                taxes_rem |= tax
                taxes_rem |= base_tax

        for tax in taxes_rem:
            for line in self.invoice_line_ids:
                if tax.id in line.tax_ids.ids:
                    new_ids = [id for id in line.tax_ids.ids if id != tax.id]
                    line.tax_ids = Tax.browse(new_ids)
                    # line.recompute_tax_line = True
                    # self._onchange_invoice_line_ids()

        for tax in taxes_add:
            for line in self.invoice_line_ids:
                if not line.tax_ids & tax:
                    line.tax_ids = line.tax_ids | tax
                    # line.recompute_tax_line = True
                    # self._onchange_invoice_line_ids()
        self._onchange_partner_id()
        # self._onchange_date_aux()
        self.line_ids.onchange_multi_price_unit()
        self.line_ids._onchange_account_id()
        self.line_ids._onchange_price_subtotal()

        self._recompute_dynamic_lines(
            recompute_all_taxes=True,
            recompute_tax_base_amount=True,
        )

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        res = super(AccountMove, self)._compute_amount()
        self.calculate_base()
        return res

    def _check_balanced(self):
        if self.env.context.get('solved_balanced'):
            moves = self.filtered(lambda move: move.line_ids)
            if not moves:
                return

            self.env['account.move.line'].flush(
                self.env['account.move.line']._fields
            )
            self.env['account.move'].flush(['journal_id'])
            self._cr.execute('''
                SELECT line.move_id, ROUND(SUM(line.debit - line.credit), currency.decimal_places)
                FROM account_move_line line
                JOIN account_move move ON move.id = line.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN res_company company ON company.id = journal.company_id
                JOIN res_currency currency ON currency.id = company.currency_id
                WHERE line.move_id IN %s
                GROUP BY line.move_id, currency.decimal_places
                HAVING ROUND(SUM(line.debit - line.credit), currency.decimal_places) != 0.0;
            ''', [tuple(self.ids)])

            query_res = self._cr.fetchall()
            if query_res:
                for move in moves:
                    debit = sum(move.line_ids.mapped('debit'))
                    credit = sum(move.line_ids.mapped('credit'))
                    residual = round(debit - credit, move.journal_id.company_id.currency_id.decimal_places)
                    line = move.line_ids[-1]
                    if line.debit:
                        line.debit = line.debit - residual
                    if line.credit:
                        line.credit = line.credit + residual
        return super(AccountMove, self)._check_balanced()
