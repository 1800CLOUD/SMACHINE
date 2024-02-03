# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    purchase_import_type = fields.Selection(
        selection=[
            ('amount_untaxed_signed', 'Amount Untaxed'),
            ('amount_total_signed', 'Amount Total')
        ],
        string='Invoice Value',
        required=True,
        default='amount_untaxed_signed',
        help='The value of invoices in imports.'
    )
