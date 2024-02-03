# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    create_supplier_invoice_without_stock = fields.Boolean(
        'Create supplier invoice without moving stock',
        help='Allows you to create a supplier invoice without having '
        'to have the amount received. '
        'It is necessary to belong to a specific access group.'
    )
