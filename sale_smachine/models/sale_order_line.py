# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    no_calc_discount = fields.Boolean('No calcular descuento', default=False)

    @api.onchange('discount')
    def _onchange_discount_edit(self):
        if self.discount and not self.no_calc_discount:
            self.no_calc_discount = True
        else:
            pass
    
    @api.onchange('product_id', 'product_uom_qty', 'price_unit')
    def onchange_discount_partner(self):
        if self.company_id.calculate_partner_discount:
            order_line_val = {}
            discount = self.order_id._calculate_partner_discount(self)
            # if self.no_calc_discount:
            #     order_line_val = {'no_calc_discount': False}
            # else:
            order_line_val = {'discount': discount}
            return {
                'value': order_line_val
            }
        else:
            pass
