# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrderReportWizard(models.TransientModel):
    _name = 'purchase.order.report.wizard'
    _description = 'Purchase Order Report Wizard'

    def _default_company_id(self):
        return self.env.company

    def _default_user_id(self):
        return self.env.user

    company_id = fields.Many2many(
        comodel_name='res.company',
        default=_default_company_id,
        required=True,
    )

    # date_start = fields.Date('Start date')
    # date_end = fields.Date('End date')

    # range_id = fields.Many2one('date.range')

    products_ids = fields.Many2many('product.product')

    user_id = fields.Many2one(
        comodel_name='res.users',
        default=_default_user_id,
        required=True,
    )

    # @api.onchange('range_id')
    # def _onchange_range_id(self):
    #     if self.range_id:
    #         self.date_start = self.range_id.date_start
    #         self.date_end = self.range_id.date_end

    def generate_report(self):
        self.ensure_one()
        # data = None
        report_type = self.env.context.get('report_type') or 'xlsx'
        if report_type == 'xlsx':
            data = self.prepare_data()
            report_name = 'purchase_smachine.action_report_report_purchase_smachine_report_purchase_order'
        # if report_type == 'pdf':
        #     report_name = 'stock_report.action_report_stock_move_pdf'
        # if report_type == 'html':
        #     report_name = 'stock_report.action_report_stock_move_html'
        report = self.env.ref(report_name)
        return report.report_action(self, data=data)

    def prepare_data(self):
        self.ensure_one()

        # Currency
        usd = self.env.ref('base.USD')
        cop = self.env.ref('base.COP')

        Line = self.env['purchase.order.line']
        Orderpoint = self.env['stock.warehouse.orderpoint']
        Pimport = self.env['purchase.import']
        Pricelist = self.env['product.pricelist']
        Product = self.env['product.product']
        Mline = self.env['account.move.line']
        Warehouse = self.env['stock.warehouse']

        warehouses = Warehouse.search([])
        products = self.products_ids

        wholesaler = Pricelist.search(
            [('pricelist_type', '=', 'wholesaler')],
            limit=1
        )
        retail = Pricelist.search([('pricelist_type', '=', 'retail')], limit=1)

        if not products:
            domain = [('purchase_ok', '=', True)]
            products = Product.search(domain)

        product_data = []
        for product in products:
            # Purchase
            line_domain = [
                ('product_id', '=', product.id),
                ('state', 'in', ('purchase', 'done')),
            ]
            lines = Line.search(line_domain)
            lines = lines.sorted(lambda l: l.order_id.date_order)
            line = lines and lines[-1] or Line

            purchase = line.order_id
            pcurrency = purchase.currency_id

            # Import
            import_domain = [
                ('state', '=', 'done'),
                ('line_ids.product_id', '=', product.id)
            ]
            pimport = Pimport.search(
                import_domain, order='date_import desc', limit=1
            )

            # Sales
            sale_domain = [
                ('move_id.move_type', '=', 'out_invoice'),
                ('move_id.state', '=', 'posted'),
                ('product_id', '=', product.id),
                ('date', '>=', fields.Date.subtract(fields.Date.today(), months=6))
            ]
            sales = Mline.search(sale_domain)
            average = sum(sales.mapped('quantity'))/6

            # Warehouses
            warehouse_data = []
            for warehouse in warehouses:
                nproduct = product.with_context(warehouse=warehouse.id)
                warehouse_vals = {
                    'name': warehouse.name,
                    'quantity': nproduct.qty_available,
                }
                warehouse_data.append(warehouse_vals)

            # Orderpoint
            orderpoint = Orderpoint.search(
                [('product_id', '=', product.id)], 
                limit=1
            )

            product_vals = {
                # Product
                'mark': product.mark_id.name,
                'submark': product.mark_sub_id.name,
                'categ': product.categ_id.name,
                'subcateg': product.categ_sub_id.name,
                'code': product.default_code,
                'name': product.name,
                'barcaode': product.barcode,
                'height': product.height,
                'width': product.width,
                'length': product.length,
                'volume': product.volume,
                'weight': product.weight,
                # Purchase
                'partner': purchase.partner_id.name,
                'puusd': pcurrency._convert(line.price_unit, usd, self.company_id, purchase.date_order or fields.Date.today()),
                'pucop': pcurrency._convert(line.price_unit, cop, self.company_id, purchase.date_order or fields.Date.today()),
                'received': sum(l.product_qty - l.qty_received for l in lines),
                # Import
                'idate': pimport.date_import,
                'iname': pimport.partner_ref,
                # Sales
                'average': average,
                # Warehouse
                'warehouse_data': warehouse_data,
                'warehouse_sum': sum(w.get('quantity') for w in warehouse_data),
                'warehouse_average': sum(w.get('quantity') for w in warehouse_data) / (average or 1),
                'warehouse_total': sum(w.get('quantity') for w in warehouse_data) + sum(l.product_qty - l.qty_received for l in lines),
                # Pricelist
                'wholesaler': wholesaler.price_get(product.id, 1)[1],
                'retail': retail.price_get(product.id, 1)[1],
                # Orderpoint
                'orderpoint': orderpoint.product_min_qty,
            }
            product_data.append(product_vals)

        return {
            # 'companies': self.companies_ids,
            'user': self.env.user.name,
            # 'start': self.date_start,
            # 'end': self.date_end,
            'wcount': len(warehouses),
            'products': product_data,
        }

    def report_data(self):
        return self.prepare_data()
