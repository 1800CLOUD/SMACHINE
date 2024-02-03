from odoo import api, fields, models


class AccountAsset(models.Model):
    _inherit = 'account.move'

    @api.model
    def _prepare_move_for_asset_depreciation(self, vals):
        move_vals = super(
            AccountAsset, self)._prepare_move_for_asset_depreciation(vals)
        move_vals.update(ifrs_type=vals['asset_id'].ifrs_type)
        return move_vals
