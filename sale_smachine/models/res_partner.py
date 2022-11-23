# -*- coding: utf-8 -*-

from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sm_customer_type_id = fields.Many2one('sm.customer.type', 'Customer type')