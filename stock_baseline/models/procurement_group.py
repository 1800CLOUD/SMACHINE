# -*- coding: utf-8 -*-

from odoo import models, fields


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        help='The analytic account related to a sales order.'
    )
