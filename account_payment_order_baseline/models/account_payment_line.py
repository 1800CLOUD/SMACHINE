# © 2015-2016 Akretion - Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPaymentLine(models.Model):
    _inherit = "account.payment.line"

    exchange_rate = fields.Float(
        compute='compute_exchage_rate',
        string="Exchange rate",
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic account",
        related="move_line_id.analytic_account_id",
        store=True,
        readonly=True
    )
    diff_exchange_rate = fields.Float(
        compute='compute_diff_exchange_rate',
        string="Diff exchange rate",
    )

    def compute_diff_exchange_rate(self):
        for record in self:
            record.diff_exchange_rate = \
                record.order_id.current_exchange_rate * \
                record.amount_currency - \
                record.exchange_rate*record.amount_currency

    def compute_exchage_rate(self):
        for record in self:
            if record.move_line_id:
                for line in record.move_line_id:
                    if line.move_id:
                        record.exchange_rate = \
                            line.move_id.current_exchange_rate
            else:
                record.exchange_rate = 0
