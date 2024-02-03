from email.policy import default
from odoo import api, fields, models
from datetime import date, datetime, timedelta


class AccountPaymentOrder(models.Model):
    _inherit = 'account.payment.order'

    current_exchange_rate = fields.Float(
        string='Current exchange rate',
        readonly=False,
    )
    foreign_currency = fields.Boolean(
        string='Active foreign currency',
        compute='compute_active_foreign_currency',
        readonly=True,
        store=True
    )
    total_currency_amount = fields.Monetary(
        compute='_total_currency_amount',
        currency_field='company_currency_id',
        store=True,
        string='Total currency amount'
    )
    total_company_currency_exchange_rate = fields.Monetary(
        compute='_total_company_currency_exchange_rate',
        currency_field='company_currency_id',
        store=True,
        string='Total currency amount (company)'
    )

    @api.depends('payment_line_ids',
                 'payment_line_ids.amount_company_currency',
                 'state')
    def _total_currency_amount(self):
        for rec in self:
            rec.total_currency_amount = sum(
                rec.mapped('payment_line_ids.amount_currency') or [0.0]
            )

    @api.depends('payment_line_ids',
                 'payment_line_ids.amount_company_currency',
                 'state')
    def _total_company_currency_exchange_rate(self):
        for rec in self:
            rec.total_company_currency_exchange_rate = sum(
                rec.mapped('payment_line_ids.amount_currency') or [0.0]
            )*rec.current_exchange_rate

    def default_date_order(self):
        return (datetime.today() - timedelta(hours=5)).date()

    order_date = fields.Date(
        string='Date order',
        default=default_date_order
    )

    def eval_foreing_currency(self):
        currency_id = self.company_id.currency_id
        foreign_currency = False
        for line in self.payment_line_ids:
            if line.currency_id != currency_id:
                foreign_currency = line.currency_id
        return foreign_currency

    @api.depends('payment_line_ids')
    def compute_active_foreign_currency(self):
        foreign_currency = self.eval_foreing_currency()
        self.foreign_currency = True if foreign_currency else False

    @api.onchange('payment_line_ids', 'foreign_currency')
    def _onchange_payment_line_ids(self):
        foreign_currency = self.eval_foreing_currency()
        if foreign_currency and self.order_date:
            amount = self.company_id.currency_id._get_conversion_rate(
                foreign_currency,
                self.company_id.currency_id,
                self.company_id,
                self.order_date
            )
            self.current_exchange_rate = amount
        else:
            self.current_exchange_rate = 1

    @api.depends('move_ids')
    def _compute_move_count(self):
        rg_res = self.env['account.move'].read_group(
            [('payment_order_id', 'in', self.ids)],
            ['payment_order_id'],
            ['payment_order_id'],
        )
        mapped_data = {
            x['payment_order_id'][0]:
            x['payment_order_id_count'] for x in rg_res
        }
        for order in self:
            order.move_count = mapped_data.get(order.id, 0)
        exch_moves = self.returns_number_of_exch_moves()
        order.move_count += exch_moves

    def return_exchange_moves(self):
        exch_moves = []
        for move in self.move_ids:
            for line in move.line_ids:
                if line.matched_credit_ids:
                    for matc_line in line.matched_credit_ids:
                        exch_moves += self.eval_exchange_moves(
                            matc_line, exch_moves)
                if line.matched_debit_ids:
                    for matc_line in line.matched_debit_ids:
                        exch_moves += self.eval_exchange_moves(
                            matc_line, exch_moves)
        exch_moves = self.reconcile_eval_exchange_moves(exch_moves)
        return exch_moves

    def reconcile_eval_exchange_moves(self, exch_moves):
        exch_accounts = self.get_exch_accounts()
        for move in self.move_ids:
            for line in move.line_ids:
                if line.full_reconcile_id:
                    for rline in line.full_reconcile_id.reconciled_line_ids:
                        if rline.move_id not in self.move_ids:
                            for mrline in rline.move_id.line_ids:
                                if mrline.account_id in exch_accounts and \
                                        mrline.move_id.id not in exch_moves:
                                    exch_moves.append(mrline.move_id.id)
        return exch_moves

    def eval_exchange_moves(self, matc_line, exch_moves):
        exch_accounts = self.get_exch_accounts()
        exch_moves = []
        if matc_line.credit_move_id:
            if (matc_line.credit_move_id.move_id not in self.move_ids):
                for line in matc_line.credit_move_id.move_id.line_ids:
                    if line.account_id in exch_accounts and \
                            line.move_id not in exch_moves:
                        exch_moves.append(line.move_id.id)
        if matc_line.debit_move_id:
            if (matc_line.debit_move_id.move_id not in self.move_ids):
                for line in matc_line.debit_move_id.move_id.line_ids:
                    if line.account_id in exch_accounts and \
                            line.move_id not in exch_moves:
                        exch_moves.append(line.move_id.id)
        return exch_moves

    def get_exch_accounts(self):
        return [
            self.journal_id.company_id.expense_currency_exchange_account_id,
            self.journal_id.company_id.income_currency_exchange_account_id
        ]

    def returns_number_of_exch_moves(self):
        return len(self.return_exchange_moves())

    def action_move_journal_line(self):
        self.ensure_one()
        action = self.env.ref(
            'account.action_move_journal_line').sudo().read()[0]
        if self.move_count == 1:
            action.update(
                {
                    'view_mode': 'form,tree,kanban',
                    'views': False,
                    'view_id': False,
                    'res_id': self.move_ids[0].id,
                }
            )
        else:
            action['domain'] = [
                ('id', 'in', self.move_ids.ids + self.return_exchange_moves())
            ]
        ctx = self.env.context.copy()
        ctx.update({'search_default_misc_filter': 0})
        action['context'] = ctx
        return action

    def _prepare_move_line_offsetting_account(
        self, amount_company_currency, amount_payment_currency, bank_lines
    ):
        vals = {}
        payment_method = self.payment_mode_id.payment_method_id
        company_id = self.journal_id.company_id
        account_id = False
        if self.payment_type == 'inbound':
            if company_id.charges_from_the_journal:
                account_id = self.journal_id.default_account_id.id
            else:
                account_id = (
                    self.journal_id.inbound_payment_method_line_ids.filtered(
                        lambda x: x.payment_method_id == payment_method
                    ).payment_account_id.id or
                    company_id.account_journal_payment_debit_account_id.id
                )
        elif self.payment_type == 'outbound':
            if company_id.payments_from_the_journal:
                account_id = self.journal_id.default_account_id.id
            else:
                account_id = (
                    self.journal_id.outbound_payment_method_line_ids.filtered(
                        lambda x: x.payment_method_id == payment_method
                    ).payment_account_id.id or
                    company_id.account_journal_payment_credit_account_id.id
                )

        partner_id = False
        for index, bank_line in enumerate(bank_lines):
            if index == 0:
                partner_id = bank_line.payment_line_ids[0].partner_id.id
            elif bank_line.payment_line_ids[0].partner_id.id != partner_id:
                # we have different partners in the grouped move
                partner_id = False
                break
        vals.update(
            {
                'partner_id': partner_id,
                'account_id': account_id,
                'credit': (
                    self.payment_type == 'outbound' and
                    amount_company_currency or 0.0
                ),
                'debit': (
                    self.payment_type == 'inbound' and
                    amount_company_currency or 0.0
                ),
            }
        )
        if bank_lines[0].currency_id != bank_lines[0].company_currency_id:
            sign = self.payment_type == 'outbound' and -1 or 1
            vals.update(
                {
                    'currency_id': bank_lines[0].currency_id.id,
                    'amount_currency': amount_payment_currency * sign,
                }
            )
        return vals
