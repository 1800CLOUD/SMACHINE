# -*- coding: utf-8 -*-

from odoo import fields, models, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    percent_budget = fields.Selection(
        [('theoritical', 'Importe Teórico'),
         ('planned', 'Importe Previsto')],
        'Cálculo de cumplimiento'
        default='planned',
        help='Define si el logro en las líneas de presupuesto se debe calcular'
        ' respecto al importe teórico o el importe previsto')