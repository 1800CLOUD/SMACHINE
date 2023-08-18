# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    
    sale_id = fields.Many2one('sale.order', 'Orden de Venta', related='invoice_line_ids.sale_line_ids.order_id', readonly=True, store=True, copy=False)
    order_purchase_id = fields.Many2one('purchase.order', 'Orden de compra', related='invoice_line_ids.purchase_line_id.order_id', readonly=True, store=True, copy=False)
    invoice_user_id = fields.Many2one('res.users', copy=False, tracking=True,
        string='Vendedor', default=lambda self: self._default_invoice_user())
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        if self.partner_id:
            if self.partner_id.user_id:
                self.invoice_user_id = self.partner_id.user_id
            else:
                self.invoice_user_id = self.env.user

        res = super(AccountMove, self)._onchange_partner_id()

        return res
    
    def _default_invoice_user(self):
        if self.partner_id and self.partner_id.user_id:
            return self.partner_id.user_id
    
        return self.env.user


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    order_sale_id = fields.Many2one('sale.order', 'Orden de Venta', related='sale_line_ids.order_id', readonly=True, store=True, copy=False)
    product_brand_id = fields.Many2one(comodel_name="product.brand", related='product_id.product_brand_id', string="Marca", copy=False, readonly=True, store=True)