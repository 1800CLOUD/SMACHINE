# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    edi_email = fields.Char(string='Correo EDI',
                            help='Correo para facturación electrónica.')
