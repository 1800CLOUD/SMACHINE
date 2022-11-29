# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    calculate_partner_discount = fields.Boolean(
        'Partner discount in sales',
        help='Allows you to calculate the commercial and financial discount '
        'of partner to automatically add it to the sales order lines'
    )
