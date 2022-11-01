# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pays_sub_trans_train_prod = fields.Boolean(
        string="Paga subsidio de transporte a aprendices en etapa productiva",
        config_parameter='hr_payroll_coll_coll_coll_co.pays_sub_trans_train_prod',
        default=False)
    eps_rate_employee = fields.Float(
        string='EPS para empleado',
        config_parameter='hr_payroll_co.eps_rate_employee')
    eps_rate_employer = fields.Float(
        string='EPS para empleador',
        config_parameter='hr_payroll_co.eps_rate_employer')
    pen_rate_employee = fields.Float(
        string='Pensión para empleado',
        config_parameter='hr_payroll_co.pen_rate_employee')
    pen_rate_employer = fields.Float(
        string='Pensión para empleador',
        config_parameter='hr_payroll_co.pen_rate_employer')
    average_sub_trans = fields.Boolean(
        string="Promediar subsidio de transporte en prestaciones sociales",
        config_parameter='hr_payroll_co.average_sub_trans',
        default=False)
