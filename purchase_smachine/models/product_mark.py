# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductMark(models.Model):
    _name = 'product.mark'
    _description = 'Mark'
    _order = 'sequence'

    active = fields.Boolean(default=True)
    code = fields.Char()
    name = fields.Char(required=True)
    sequence = fields.Integer()


class ProductMarkSub(models.Model):
    _name = 'product.mark.sub'
    _description = 'Sub-Mark'
    _order = 'sequence'

    active = fields.Boolean(default=True)
    code = fields.Char()
    mark_id = fields.Many2one(comodel_name='product.mark', ondelete='set null')
    name = fields.Char(required=True)
    sequence = fields.Integer()
