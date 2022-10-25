# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    pricelist_type = fields.Selection(
        selection=[
            ('other', 'Other'),
            ('wholesaler', 'Wholesaler'),
            ('retail', 'Retail'),
        ],
        string='Type',
        default='other'
    )
