# -*- coding: utf-8 -*-

from odoo import models, fields

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_refund_categ_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=True,
        string='Refund Account',
        domain=ACCOUNT_DOMAIN,
        help='This account will be used when validating a customer refund.'
    )
