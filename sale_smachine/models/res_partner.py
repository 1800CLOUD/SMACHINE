# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sm_customer_type_id = fields.Many2one('sm.customer.type', 'Customer type')
    discount_com = fields.Float('Commercial discount',
                                company_dependent=True)
    discount_fin = fields.Float('Financial discount',
                                company_dependent=True)
    amount_min_fin = fields.Float(
        'Minimum amount',
        company_dependent=True,
        help='Minimum amount to apply financial discount.'
    )
    view_partner_discounts = fields.Boolean(
        'Partner discount in sales',
        compute='_compute_view_partner_discounts'
    )

    def _compute_view_partner_discounts(self):
        for record in self:
            company = self.env.company
            if company.calculate_partner_discount:
                record.view_partner_discounts = True
            else:
                record.view_partner_discounts = False
