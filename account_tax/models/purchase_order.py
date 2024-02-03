
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    base_calculate = fields.Boolean(
        string='Calculate base?',
        default=True,
        help="Automatically calculate base taxes",
    )

    city_id = fields.Many2one('res.city')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(PurchaseOrder, self).onchange_partner_id()
        self.city_id = self.partner_id.city_id
        return res

    def calculate_base(self):
        if not self.env.context.get('calculate_base', True):
            return False
        purchases = self.filtered(lambda m: m.state not in ('done', 'cancel'))
        for purchase in purchases:
            purchase._calculate_base()

    def _calculate_base(self):
        Tax = self.env['account.tax']

        if self.state in ('done', 'cancel'):
            return False
        if not self.base_calculate:
            return False

        taxes = Tax
        for line in self.order_line:
            line = line.with_company(line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(
                line.order_id.partner_id.id)
            # filter taxes by company
            ptaxes = line.product_id.supplier_taxes_id.filtered(
                lambda r: r.company_id == line.env.company)
            taxes |= fpos.map_tax(ptaxes)

        if not any(t.base_minimum for t in taxes):
            return False

        amount_untaxed = self.with_context(calculate_base=False).amount_untaxed
        taxes_retention = taxes.filtered(lambda t: t.base_minimum)
        taxes_add = Tax
        taxes_rem = Tax

        for tax in taxes_retention:
            tax = tax.with_context(partner_id=self.partner_id)
            base_amount, base_tax = tax.compute_base_tax(city=self.city_id)

            if amount_untaxed >= -base_amount:
                taxes_rem |= tax
                taxes_add |= base_tax
            else:
                taxes_rem |= tax
                taxes_rem |= base_tax

        for tax in taxes_rem:
            for line in self.order_line:
                if tax.id in line.taxes_id.ids:
                    new_ids = [id for id in line.taxes_id.ids if id != tax.id]
                    line.taxes_id = Tax.browse(new_ids)
                    # line.recompute_tax_line = True
                    # self._onchange_order_line()

        for tax in taxes_add:
            for line in self.order_line:
                if not line.taxes_id & tax:
                    line.taxes_id = line.taxes_id | tax
                    # line.recompute_tax_line = True
                    # self._onchange_order_line()

    @api.depends('order_line.price_total')
    def _amount_all(self):
        res = super(PurchaseOrder, self)._amount_all()
        self.calculate_base()
        return res

    def _prepare_invoice(self):
        invoice_vals = super(PurchaseOrder, self)._prepare_invoice()
        invoice_vals.update({
            'base_calculate': self.base_calculate,
            'city_id': self.city_id and self.city_id.id or False
        })
        return invoice_vals

    def action_create_invoice(self):
        self = self.with_context(solved_balanced=True)
        return super(PurchaseOrder, self).action_create_invoice()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine,
                    self)._prepare_account_move_line(move=move)
        if self.taxes_id:
            res.update({'recompute_tax_line': True})
        return res
