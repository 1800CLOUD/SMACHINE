# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # OVERRIDE
        # Recompute 'partner_shipping_id' based on 'partner_id'.
        partner_shipping_id = self.partner_shipping_id and self.partner_shipping_id.id

        res = super(AccountMove, self)._onchange_partner_id()

        self.partner_shipping_id = partner_shipping_id

        return res
