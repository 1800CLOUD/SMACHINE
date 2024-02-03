# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo.tools.float_utils import float_round, float_is_zero
from odoo import api, fields, models

move_types = {
    '1': 'Entrada',
    '-1': 'Salida',
    '0': 'Interna',
}


class StockMoveWizard(models.TransientModel):
    _name = 'stock.move.wizard'
    _description = 'Stock move wizard'

    def _default_company_id(self):
        return self.env.company

    def _default_user_id(self):
        return self.env.user

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=_default_company_id,
        required=True,
    )

    date_start = fields.Date('Start date')
    date_end = fields.Date('End date')
    products_ids = fields.Many2many('product.product')
    range_id = fields.Many2one('date.range')
    user_id = fields.Many2one(comodel_name='res.users',
                              default=_default_user_id,
                              required=True,
                              )
    owner_id = fields.Many2one('res.partner',
                               'Propietario')

    @api.onchange('range_id')
    def _onchange_range_id(self):
        if self.range_id:
            self.date_start = self.range_id.date_start
            self.date_end = self.range_id.date_end

    def generate_report(self):
        self.ensure_one()
        data = None
        report_type = self.env.context.get('report_type') or 'xlsx'
        if report_type == 'xlsx':
            data = self.prepare_data()
            report_name = 'stock_report.report_stock_move_xlsx'
        if report_type == 'pdf':
            report_name = 'stock_report.action_report_stock_move_pdf'
        if report_type == 'html':
            report_name = 'stock_report.action_report_stock_move_html'
        report = self.env.ref(report_name)
        if self.owner_id:
            report.sudo().name = f'Informe XLSX movimiento de inventario - {self.owner_id.name}'
        else:
            report.sudo().name = 'Informe XLSX movimiento de inventario'
        return report.report_action(self, data=data)

    def prepare_data(self):
        self.ensure_one()

        Product = self.env['product.product']
        Move = self.env['stock.move']

        products = self.products_ids
        if not products:
            domain = [
                ('type', '=', 'product'),
                '|',
                ('company_id', '=', self.company_id.id),
                ('company_id', '=', False)
            ]
            products = Product.search(domain)

        product_data = []
        for product in products:
            move_data = []
            move_domain = [
                ('date', '>=', fields.Datetime.to_datetime(self.date_start)),
                ('date', '<=', fields.Datetime.to_datetime(
                    str(self.date_end) + ' 23:59:59')),
                ('product_id', '=', product.id),
                ('state', '=', 'done'),
                ('company_id', '=', self.company_id.id)
            ]
            moves = Move.search(move_domain, order='date')
            if self.owner_id:
                moves = moves.filtered(
                    lambda m: any([ln.owner_id.id == self.owner_id.id 
                                for ln in m.move_line_ids]))
            
            svl_date = fields.Date.subtract(self.date_start, minutes=1)
            initial_qty = self._get_initial_quantity(to_date=svl_date, 
                                                     product=product)
            for move in moves:
                move_vals = self._get_move_vals(move, product, initial_qty)
                move_data.append(move_vals)
                initial_qty += move_vals.get('qty', 0)

            product_vals = {
                'id': product.id,
                'name': product.display_name,
                'moves': move_data,
            }
            if not move_data:
                continue
            product_data.append(product_vals)

        return {
            'company': self.company_id.name,
            'user': self.env.user.name,
            'start': self.date_start,
            'end': self.date_end,
            'owner': self.owner_id and self.owner_id.name or False,
            'products': product_data
        }

    def report_data(self):
        return self.prepare_data()
    
    def _get_in_price_unit(self, move=False):
        self.ensure_one()
        if not move.origin_returned_move_id and \
            move.purchase_line_id and \
                move.product_id.id == move.purchase_line_id.product_id.id:
            price_unit_prec = self.env['decimal.precision'].precision_get(
                'Product Price')
            line = move.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                qty = line.product_qty or 1
                price_unit = line.taxes_id.with_context(
                    round=False).compute_all(
                        price_unit, 
                        currency=line.order_id.currency_id, 
                        quantity=qty)['total_void']
                price_unit = float_round(price_unit / qty, 
                                         precision_digits=price_unit_prec)
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / \
                    line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                invoice = move.account_move_ids.filtered(
                    lambda x: x.state == 'posted')
                if invoice:
                    price_unit = order.company_id.currency_id.round(
                        price_unit*(invoice[0].current_exchange_rate or 1))
                else:
                    price_unit = move._get_price_unit()
        else:
            price_unit = move._get_price_unit()
        return price_unit
    
    def _is_out(self, move):
        res = self.env['stock.move.line']
        for move_line in move.move_line_ids:
            if move_line.location_id._should_be_valued() \
                and not move_line.location_dest_id._should_be_valued():
                res |= move_line
        return res
    
    def _is_in(self, move):
        res = self.env['stock.move.line']
        for move_line in move.move_line_ids:
            if not move_line.location_id._should_be_valued() \
                and move_line.location_dest_id._should_be_valued():
                res |= move_line
        return res

    def _get_initial_quantity(self, to_date=False, product=False):
        self.ensure_one()
        if self.owner_id:
            sml_obj = self.env['stock.move.line']
            domain = [('product_id', '=', product.id),
                      ('company_id', '=', self.company_id.id),
                      ('owner_id', '=', self.owner_id.id)]
            if to_date:
                to_date = fields.Datetime.to_datetime(to_date)
                domain.append(('create_date', '<=', to_date))
            sml_ids = sml_obj.search(domain)
            qty = [x.qty_done * (self._is_in(x.move_id) and 1 \
                                 or self._is_out(x.move_id) and -1 \
                                    or 0) for x in sml_ids]
            return sum(qty)
        else:
            return product.with_context(to_date=to_date).quantity_svl
    
    def _get_move_vals(self, move, product, initial_qty):
        self.ensure_one()
        price_unit = 0
        price_svl = 0
        price = 0
        qty = 0
        svl_qty = 0
        svl_value = 0
        svl_price = 0
        # Type
        if not self.owner_id:
            if move._is_in():
                move_type = 1
            elif move._is_out():
                move_type = -1
            else:
                move_type = 0
        else:
            if self._is_in(move):
                move_type = 1
            elif self._is_out(move):
                move_type = -1
            else:
                move_type = 0
        
        # Date
        date = move.account_move_ids \
            and move.account_move_ids.mapped('date')[0] \
                or False
        # SVL
        svl_ids = move.stock_valuation_layer_ids.filtered(
            lambda x: x.unit_cost != 0)
        # Qty
        qty = move.product_uom_qty * move_type
        # SVL
        svl_qty = product.with_context(to_date=move.date).quantity_svl or 1
        svl_value = product.with_context(to_date=move.date).value_svl
        svl_price = svl_value/svl_qty
        # Price
        if svl_ids:
            price_svl = sum(svl_ids.mapped('unit_cost'))/len(svl_ids)
        if move_type == 1:
            price = self._get_in_price_unit(move)
        else:
            price = move._get_price_unit()
        price_unit = price_svl or svl_price or price
        price_total = price_unit * qty

        move_vals = {
            'id': move.id,
            'date': date or move.date.date(),
            'reference': move.reference,
            'product': move.product_id.display_name,
            'from': move.location_id.complete_name,
            'to': move.location_dest_id.complete_name,
            'type': move_types.get(str(move_type)),
            'init': initial_qty,
            'demand': move.product_uom_qty,
            'final': initial_qty + qty,
            'uom': move.product_uom.name,
            'unit': price_unit,
            'total': price_total,
            'company': move.company_id.name,
            'status': move.state,
            'qty': qty
        }
        return move_vals