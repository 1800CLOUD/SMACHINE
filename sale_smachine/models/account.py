# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    sale_id = fields.Many2one('sale.order', 'Orden de Venta', related='invoice_line_ids.sale_line_ids.order_id', readonly=True, store=True, copy=False)
    order_purchase_id = fields.Many2one('purchase.order', 'Orden de compra', related='invoice_line_ids.purchase_line_id.order_id', readonly=True, store=True, copy=False)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    order_sale_id = fields.Many2one('sale.order', 'Orden de Venta', related='sale_line_ids.order_id', readonly=True, store=True, copy=False)