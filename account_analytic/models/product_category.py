
from odoo import fields, models

ACCOUNT_DOMAIN = "['&', '&', '&', ('deprecated', '=', False), ('internal_type','=','other'), ('company_id', '=', current_company_id), ('is_off_balance', '=', False)]"


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_account_cost_sale_categ_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=True,
        string="Cost of Sale Account",
        domain=ACCOUNT_DOMAIN,
        help='It is replaced by the expense account when the analytical account is of the cost of sale type.'
    )
    property_account_cost_operation_categ_id = fields.Many2one(
        comodel_name='account.account',
        company_dependent=True,
        string="Cost of Operation Account",
        domain=ACCOUNT_DOMAIN,
        help='It is replaced by the expense account when the analytical account is of the cost of operation type.'
    )
