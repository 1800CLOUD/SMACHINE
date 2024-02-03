
from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('analytic_account_id')
    def _onchange_analytic_account_id(self):
        if self.analytic_account_id:
            self.account_id = self._get_computed_account()

    def _get_computed_account(self):
        if self.analytic_account_id and self.analytic_account_id.account_type:
            self = self.with_context(
                analytic_type=self.analytic_account_id.account_type
            )
        return super(AccountMoveLine, self)._get_computed_account()
