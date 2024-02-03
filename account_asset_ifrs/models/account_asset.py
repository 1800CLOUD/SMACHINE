from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    ifrs_type = fields.Selection(
        selection=[
            ('both', 'Both'),
            ('local', 'Local'),
            ('ifrs', 'IFRS'),
        ],
        string='IFRS Type',
        default='both',
    )
