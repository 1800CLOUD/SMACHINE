
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class AccountPaymentMode(models.Model):
    _inherit = 'account.payment.mode'

    code = fields.Char('Code')