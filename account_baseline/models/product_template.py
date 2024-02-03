# -*- coding: utf-8 -*-

from odoo import models, fields, api

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    property_account_refund_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=True,
        string='Refund Account',
        domain=ACCOUNT_DOMAIN,
        help='Keep this field empty to use the default value from the product category.'
    )

    height = fields.Float()
    length = fields.Float()
    width = fields.Float()

    @api.onchange('height', 'length', 'width')
    def compute_volume_product(self):
        for record in self:
            record.volume = record.height*record.length*record.width

    def _get_product_accounts(self):
        accounts = super(ProductTemplate, self)._get_product_accounts()
        accounts.update({'refund': self.property_account_refund_id or self.categ_id.property_account_refund_categ_id})
        if self.env.context.get('default_expense'):
            accounts.update(
                {'expense': self.env.context.get('default_expense')}
            )
        return accounts
