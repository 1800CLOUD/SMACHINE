# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    percent_budget = fields.Selection(
        related='company_id.percent_budget',
        readonly=False)
