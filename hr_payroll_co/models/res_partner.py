# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

EMPLOYEE_EMERGENCY_HELP = "Empleado al que este contacto le sirve para alguna emergencia"


class ResPartner(models.Model):
    _inherit = "res.partner"

    employee = fields.Boolean(
        help="Check this box if this contact is an Employee.", readonly=True)
    employee2emergency_id = fields.Many2one(
        'hr.employee', string="Es contacto de emergencia de", help=EMPLOYEE_EMERGENCY_HELP)
    eps = fields.Boolean(string='Es EPS', default=False,
                         help='Entidad Promotora Salud')
    arl = fields.Boolean(string='Es ARL', default=False,
                         help='Administradora de Riesgos Laborales')
    afp = fields.Boolean(string='Es AFP', default=False,
                         help='Administradora Fondos Pensiones y Cesantías')
    ccf = fields.Boolean(string='Es CCF', default=False,
                         help='Caja Compensación Familiar')
    eps_code = fields.Char(string='Código de EPS')
    arl_code = fields.Char(string='Código de ARL')
    afp_code = fields.Char(string='Código de AFP')
    ccf_code = fields.Char(string='Código de CCF')

    @api.onchange('eps', 'arl', 'afp', 'ccf')
    def _onchange_eps_arl_afp_ccf(self):
        fields_eval = ['eps', 'arl', 'afp', 'ccf']
        for record in self:
            for fe in fields_eval:
                if not getattr(record, fe):
                    setattr(record, fe+'_code', '')
