# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    salesperson_not_editable = fields.Boolean(
        'Salesperson field not editable',
        help='Allows to restrict the edition of the '
        'salesperson field in sales and invoices.'
    )
    add_tag_to_non_buyers = fields.Boolean(
        'Add tag to non buyers and block them',
        help='Allows you to add a tag and block to the customer who '
        'has not purchased in the last few months.'
    )
    months_without_buying = fields.Integer(
        'Months without buyings',
        help='months required to add tag.'
    )
    tags_to_add_ids = fields.Many2one(
        'res.partner.category',
        'Tag'
    )

    sale_confirm_quantity = fields.Boolean(
        string='Do not confirm without quantity',
        default=False,
        help='It does not allow to confirm the sales order '
        'if there are no quantities available.',
    )
