# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    salesperson_not_editable = fields.Boolean(
        'Salesperson field not editable',
        related='company_id.salesperson_not_editable',
        readonly=False
    )
    add_tag_to_non_buyers = fields.Boolean(
        'Add tag to non buyers and block them',
        related='company_id.add_tag_to_non_buyers',
        readonly=False
    )
    months_without_buying = fields.Integer(
        'Months',
        related='company_id.months_without_buying',
        readonly=False
    )
    tags_to_add_ids = fields.Many2one(
        'res.partner.category',
        'Tag',
        related='company_id.tags_to_add_ids',
        readonly=False
    )

    sale_confirm_quantity = fields.Boolean(
        related='company_id.sale_confirm_quantity',
        readonly=False
    )
