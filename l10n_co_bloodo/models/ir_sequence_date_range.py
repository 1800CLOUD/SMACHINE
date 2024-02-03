# -*- coding: utf-8 -*-

from odoo import fields, models


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    edi_resolution = fields.Char(string='Resolution')
    number_from = fields.Integer(string='Initial number', default=False)
    number_to = fields.Integer(string='End number', default=False)
    active_resolution = fields.Boolean(string='Active Resolution')
    prefix = fields.Char(string='Prefix')
