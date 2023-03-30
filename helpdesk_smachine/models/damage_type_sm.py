# -*- coding: utf-8 -*-

from odoo import fields, models, _


class BankPaymentLine(models.Model):
    _name = 'bank.payment.line'
    _inherit = 'bank.payment.line'

class DamageTypeSm(models.Model):
    _name = 'damage.type.sm'
    _description = 'Damage type for helpdesk'

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True)
