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
