# -*- coding: utf-8 -*-

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('location_id', 'quantity')
    def _check_negative_inventory(self):
        for record in self:
            location = record.location_id
            quantity = record.quantity
            product = record.product_id
            if location and location.usage == 'internal' and quantity < 0:
                if not self.env.company.negative_inventory:
                    raise ValidationError(
                        _('No negative moves allowed. Location: %s, Product: %s') % (
                            location.complete_name, product.display_name
                        )
                    )
