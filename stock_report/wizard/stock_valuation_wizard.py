# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockValuationWizard(models.TransientModel):
    _name = 'stock.valuation.wizard'
    _description = 'Stock valuation wizard'

    def _default_companies_ids(self):
        return self.env.companies

    companies_ids = fields.Many2many(
        comodel_name='res.company',
        default=_default_companies_ids
    )

    date_start = fields.Date('Start date')
    date_end = fields.Date('End date')

    products_ids = fields.Many2many('product.product')

    range_id = fields.Many2one('date.range')

    @api.onchange('range_id')
    def _onchange_range_id(self):
        if self.range_id:
            self.date_start = self.range_id.date_start
            self.date_end = self.range_id.date_end

    def generate_report(self):
        self.ensure_one()
        data = self.prepare_data()
        report_type = self.env.context.get('report_type') or 'xlsx'
        if report_type == 'xlsx':
            report_name = 'stock_report.report_stock_valuation_xlsx'
        report = self.env.ref(report_name)
        return report.report_action(self, data=data)

    def prepare_data(self):
        self.ensure_one()

        Product = self.env['product.product']
        Valuation = self.env['stock.valuation.layer']

        company_data = []
        for company in self.companies_ids:
            products = self.products_ids.filtered(
                lambda p: not p.company_id or (
                    p.company_id and p.company_id.id == company.id
                )
            )

            if not products:
                product_domain = [
                    ('type', '=', 'product'),
                    '|',
                    ('company_id', '=', False),
                    ('company_id', '=', company.id),
                ]
                products = Product.search(product_domain)

            product_data = []
            for product in products:
                svl_date = fields.Date.subtract(self.date_start, days=1)
                product_context = product.with_context(to_date=svl_date)
                svl_quantity = product_context.quantity_svl
                svl_value = product_context.value_svl

                valuation_domain = [
                    ('create_date', '>=', fields.Datetime.to_datetime(self.date_start)),
                    ('create_date', '<=', fields.Datetime.to_datetime(self.date_end)),
                    ('product_id', '=', product.id)
                ]
                valuations = Valuation.search(valuation_domain)
                valuations_in = valuations.filtered(
                    lambda v: v.quantity > 0
                )
                valuations_out = valuations.filtered(
                    lambda v: v.quantity < 0
                )

                product_vals = {
                    'id': product.id,
                    'name': product.display_name,
                    'init': svl_quantity,
                    'value': svl_value,
                    'in': sum(valuations_in.mapped('quantity')),
                    'out': sum(valuations_out.mapped('quantity')),
                }

                product_context = product.with_context(to_date=self.date_end)
                svl_quantity = product_context.quantity_svl
                svl_value = product_context.value_svl

                product_vals.update({
                    'final': svl_quantity,
                    'uom': product.uom_id.name,
                    'total': svl_value,
                })
                product_data.append(product_vals)

            company_vals = {
                'id': company.id,
                'name': company.name,
                'products': product_data,
            }
            if not product_data:
                continue
            company_data.append(company_vals)

        return {
            'user': self.env.user.name,
            'start': self.date_start,
            'end': self.date_end,
            'companies': company_data
        }
