# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    categ_sub_id = fields.Many2one(
        comodel_name='product.category.sub',
        string='Sub-Category',
        ondelete='set null'
    )

    mark_id = fields.Many2one(
        comodel_name='product.mark',
        string='Mark',
        ondelete='set null'
    )

    mark_sub_id = fields.Many2one(
        comodel_name='product.mark.sub',
        string='Sub-Mark',
        ondelete='set null'
    )
