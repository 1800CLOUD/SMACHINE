# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    import_is = fields.Boolean(
        string='Is Import?',
        default=False,
        copy=False,
    )


class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    partner_id = fields.Many2one(
        comodel_name='res.partner'
    )


class StockValuationAdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'

    partner_id = fields.Many2one(
        related='cost_line_id.partner_id'
    )

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        lines = super()._create_account_move_line(move, credit_account_id,
                                                  debit_account_id, qty_out, already_out_account_id)
        if self.partner_id:
            for line in lines:
                line[2].update({'partner_id': self.partner_id.id})
        return lines


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
