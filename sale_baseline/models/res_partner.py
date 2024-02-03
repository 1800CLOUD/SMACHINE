# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_blocked_not_buy = fields.Boolean('Blocked for time without buying',
                                        company_dependent=True,
                                        default=False)
