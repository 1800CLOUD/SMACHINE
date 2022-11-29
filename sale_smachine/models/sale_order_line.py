# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty', 'price_unit')
    def _onchange_partner_discounts(self):
        self.order_id.onchange_discount_partner()