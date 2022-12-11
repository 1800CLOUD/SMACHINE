
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    date_expiration = fields.Datetime()
    quantity_available = fields.Integer('Quantity Available')
