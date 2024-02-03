from email.policy import default
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    charges_from_the_journal = fields.Boolean(
        string="Charge account from the journal",
        default=False
    )

    payments_from_the_journal = fields.Boolean(
        string="Payment accounts from the journal",
        default=False
    )
