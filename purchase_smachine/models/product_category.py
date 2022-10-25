# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductCategorySub(models.Model):
    _name = 'product.category.sub'
    _description = 'Sub-Category'
    _order = 'sequence'

    active = fields.Boolean(default=True)
    code = fields.Char()
    category_id = fields.Many2one(comodel_name='product.category', ondelete='set null')
    name = fields.Char(required=True)
    sequence = fields.Integer()
