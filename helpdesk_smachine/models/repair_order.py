# -*- coding: utf-8 -*-

from odoo import fields, models, _


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    invoice_number = fields.Char('Invoice number')
