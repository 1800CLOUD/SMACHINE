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
    is_commercial_group = fields.Boolean(
        'Grupo comercial',
        related='partner_id.is_commercial_group',
        store=True,
        copy=False
    )
    portfolio_approved = fields.Boolean(
        'Aprobado por cartera',
        default=False,
        copy=False
    )
    destination_city_id = fields.Many2one('res.city', 'Ciudad destino')

    def action_confirm(self):
        for record in self:
            record.validation_product_kit()
            if record.is_commercial_group and \
                    not record.portfolio_approved:
                raise UserError(_(
                    'El cliente %s está bloqueado por grupo comercial.\n'
                    'Este pedido debe ser aprobado por '
                    'cartera antes de confirmalo.'
                ))
        res = super(SaleOrder, self).action_confirm()
        return res

    def validation_date_expiration(self, mrp_bom_kits):
        for record in self:
            datetime_now = datetime.now()
            for kit in mrp_bom_kits:
                if kit.date_expiration <= datetime_now:
                    raise UserError(_(
                        'El producto %s ya expiró'
                    ) % kit.product_tmpl_id.name)

    def validation_quantity_mrp_bom(self, mrp_bom_kits):
        for record in self:
            for line in record.order_line:
                for kit in mrp_bom_kits:
                    if line.product_template_id.id == kit.product_tmpl_id.id:
                        if line.product_uom_qty > kit.quantity_available:
                            raise UserError(_(
                                'El producto %s supera la cantidad '
                                'establecidad en el kit'
                            ) % kit.product_tmpl_id.name
                            )
                        kit.quantity_available = \
                            kit.quantity_available - line.product_uom_qty

    def validation_product_kit(self):
        for record in self:
            if record.order_line:
                mrp_bom_ids = []
                for line in record.order_line:
                    for bom_ids in line.product_id.bom_ids:
                        for bom_id in bom_ids:
                            mrp_bom_ids.append(bom_id)

                mrp_bom_kits = list(
                    filter(lambda x: x.type == 'phantom', mrp_bom_ids)
                )
                record.validation_date_expiration(mrp_bom_kits)
                record.validation_quantity_mrp_bom(mrp_bom_kits)

    def _compute_editable_line_discount(self):
        for record in self:
            user_id = self.env.user
            record.is_line_discount_edit = user_id.has_group(
                'sale_smachine.group_edit_line_discount_sale')

    def _calculate_partner_discount(self):
        '''
            Retorna descuento comercial del tercero y descuento financiero
            si el producto no pertenece a un kit, el termino de pago es
            inmediato y tiene 3 o más pedidos confirmados.
        '''
        bom_obj = self.env['mrp.bom']
        for sale in self:
            partner = sale.partner_id
            discount = 0.0
            lines = sale.order_line.filtered(lambda x: not x.display_type)
            if partner.discount_com or partner.discount_fin:
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
                                    lambda s: s.state in ('sale', 'done')
                            )) >= 3:
                                discount += partner.discount_fin or 0.0
        return discount*100

    @api.onchange('partner_id', 'payment_term_id', 'order_line')
    def onchange_discount_partner(self):
        if self.company_id.calculate_partner_discount:
            discount = self._calculate_partner_discount()
            order_line_val = []
            lines = self.order_line.filtered(lambda x: not x.display_type)
            if any([ln.no_calc_discount for ln in lines]):
                order_line_val = [
                    (1, ln.id, {'no_calc_discount': False}) for ln in lines]
            else:
                order_line_val = [
                    (1, ln.id, {'discount': discount}) for ln in lines]
            return {
                'value': {
                    'order_line': order_line_val
                }
            }
        else:
            pass
