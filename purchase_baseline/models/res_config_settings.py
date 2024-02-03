# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_supplier_invoice_without_stock = fields.Boolean(
        'Create supplier invoice without moving stock',
        related='company_id.create_supplier_invoice_without_stock',
        readonly=False
    )
