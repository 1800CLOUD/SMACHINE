
from odoo import _, fields, models
from odoo.exceptions import RedirectWarning


class ResCompany(models.Model):
    _inherit = 'res.company'

    duplicate_orders = fields.Boolean(
        'Active Duplicate orders Option',
        help='Active Duplicate orders for '
        'multicompany.'
    )
