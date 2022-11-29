# -*- coding: utf-8 -*-

from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sm_transaction_number = fields.Char('Transaction number')
    is_line_discount_edit = fields.Boolean(
        'Line discount is editable?',
        compute='_compute_editable_line_discount'
    )

    def _compute_editable_line_discount(self):
        for record in self:
            user_id = self.env.user
            record.is_line_discount_edit = user_id.has_group(
                'sale_smachine.group_edit_line_discount_sale')

    def _calculate_partner_discount(self):
        bom_obj = self.env['mrp.bom']
        for sale in self:
            partner = sale.partner_id
            discount = 0.0
            if partner.discount_com or partner.discount_fin:
                lines = sale.order_line.filtered(lambda x: not x.display_type)
                discount = partner.discount_com or 0.0
                amount_total = sum([
                    ln.price_unit*ln.product_uom_qty*(
                        1+sum([tx.amount/100 for tx in ln.tax_id]))
                    for ln in sale.order_line
                ])
                kits = bom_obj.search([('type', '=', 'panthom')])
                prod_tmpl_ids = kits.product_tmpl_id.ids
                product_ids = [
                    ln.product_id.id for ln in kits.bom_line_ids]
                product_tmpl_ln_ids = [
                    ln.product_id.product_tmpl_id.id for ln in lines]
                product_ln_ids = [ln.product_id.id for ln in lines]
                if sale.payment_term_id and \
                        sale.payment_term_id.immediate_payment:
                    if amount_total >= partner.amount_min_fin:
                        if not any([id in prod_tmpl_ids
                                    for id in product_tmpl_ln_ids]) and \
                                not any([id in product_ids
                                        for id in product_ln_ids]):
                            if len(partner.sale_order_ids.filtered(
                                    lambda s: s.state == 'sale')) >= 1:
                                discount += partner.discount_fin or 0.0
            sale.order_line.write({
                'discount': discount*100
            })

    @api.onchange('partner_id', 'payment_term_id')
    def onchange_discount_partner(self):
        if self.company_id.calculate_partner_discount:
            self._calculate_partner_discount()
        else:
            pass
