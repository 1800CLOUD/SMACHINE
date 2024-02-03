
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    journal_id = fields.Many2one(
        related='company_id.journal_id',
        readonly=False
    )
    block_expired_invoice = fields.Boolean(
        related='company_id.block_expired_invoice',
        readonly=False
    )
    block_credit_limit = fields.Boolean(
        related='company_id.block_credit_limit',
        readonly=False
    )
    advance_req_in_immediate_pay = fields.Boolean(
        related='company_id.advance_req_in_immediate_pay',
        readonly=False
    )
    active_payment_advance = fields.Boolean(
        related='company_id.active_payment_advance',
        readonly=False
    )

    voucher_account_id = fields.Many2one(
        related='company_id.voucher_account_id',
        readonly=False
    )
