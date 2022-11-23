
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sm_transaction_number = fields.Char('Transaction number')
