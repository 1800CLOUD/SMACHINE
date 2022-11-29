# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    calculate_partner_discount = fields.Boolean(
        'Partner discount in sales',
        related='company_id.calculate_partner_discount',
        readonly=False
    )
