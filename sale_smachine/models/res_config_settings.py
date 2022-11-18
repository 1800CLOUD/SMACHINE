
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    duplicate_orders = fields.Boolean(
        related='company_id.duplicate_orders',
        readonly=False
    )

