
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    base_calculate = fields.Boolean(
        string='Calculate base?',
        default=True,
        help="Automatically calculate base taxes",
    )

    city_id = fields.Many2one('res.city')

    @api.onchange('company_id')
    def onchange_company_id(self):
        self.city_id = self.company_id.partner_id.city_id

    # @api.onchange('partner_id')
    # def onchange_partner_id(self):
    #     res = super(SaleOrder, self).onchange_partner_id()
    #     self.city_id = self.partner_id.city_id
    #     return res

    def calculate_base(self):
        if not self.env.context.get('calculate_base', True):
            return False
        sales = self.filtered(lambda m: m.state not in ('done', 'cancel'))
        for sale in sales:
            sale._calculate_base()

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
                line.order_partner_id.id)
            ptaxes = line.product_id.taxes_id.filtered(
                lambda t: t.company_id == line.env.company)
            taxes |= fpos.map_tax(ptaxes)

        if not any(t.base_minimum for t in taxes):
            return False

        amount_untaxed = self.with_context(calculate_base=False).amount_untaxed
        taxes_retention = taxes.filtered(lambda t: t.base_minimum)
        taxes_add = Tax
        taxes_rem = Tax

        for tax in taxes_retention:
            # tax = tax.with_context(partner_id=self.partner_id)
            base_amount, base_tax = tax.compute_base_tax(city=self.city_id)

            if amount_untaxed >= base_amount:
                taxes_rem |= tax
                taxes_add |= base_tax
            else:
                taxes_rem |= tax
                taxes_rem |= base_tax

        for tax in taxes_rem:
            for line in self.order_line:
                if tax.id in line.tax_id.ids:
                    new_ids = [id for id in line.tax_id.ids if id != tax.id]
                    line.tax_id = Tax.browse(new_ids)
                    # line.recompute_tax_line = True
                    # self._onchange_invoice_line_ids()

        for tax in taxes_add:
            for line in self.order_line:
                if not line.tax_id & tax:
                    line.tax_id = line.tax_id | tax
                    # line.recompute_tax_line = True
                    # self._onchange_invoice_line_ids()

    @api.depends('order_line.price_total')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        self.calculate_base()
        return res

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'base_calculate': self.base_calculate,
            'city_id': self.city_id and self.city_id.id or False
        })
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        self = self.with_context(solved_balanced=True)
        return super(SaleOrder, self)._create_invoices(grouped=grouped, final=final, date=date)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(
            **optional_values)
        if self.tax_id:
            res.update({'recompute_tax_line': True})
        return res
