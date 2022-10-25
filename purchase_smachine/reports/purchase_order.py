# -*- coding: utf-8 -*-

from odoo import models


class ReportPurchaseOrder(models.AbstractModel):
    _name = 'report.purchase_smachine.report_purchase_order'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Purchase Order Report'

    def generate_xlsx_report(self, workbook, data, objs):

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '$ #,##0'})
        # num_f = workbook.add_format({'num_format': '#.##0'})

        products = data.get('products')
        wc = data.get('wcount')

        worksheet = workbook.add_worksheet('CUADRO COMPRAS')
        worksheet.write('A1', 'PROVEEDOR', bold)
        worksheet.write('B1', 'MARCA', bold)
        worksheet.write('C1', 'SUBMARCA', bold)
        worksheet.write('D1', 'CATEGORIA', bold)
        worksheet.write('E1', 'SUBCATEGORIA', bold)
        worksheet.write('F1', 'REF', bold)
        worksheet.write('G1', 'NOMBRE PRODUCTO', bold)
        worksheet.write('H1', 'COSTO PROVEEDOR DOLARES', bold)
        worksheet.write('I1', 'COSTO UNITARIO PESOS', bold)
        worksheet.write('J1', 'LISTA DE PRECIOS MAYORISTA', bold)
        worksheet.write('K1', 'LISTA DE PRECIOS MONORISTA', bold)
        worksheet.write('L1', 'FECHA FACTURA ULTIMA IMPORTACION', bold)
        worksheet.write('M1', 'NUMERO FACTURA ULTIMA IMPORTACIÓN', bold)
        worksheet.write('N1', 'STOCK MINIMO DE COMPRA POR PRODUCTO', bold)
        worksheet.write('O1', 'COD BARRAS', bold)
        worksheet.write('P1', 'UNIDAD DE EMPAQUE', bold)
        worksheet.write('Q1', 'ALTO', bold)
        worksheet.write('R1', 'ANCHO', bold)
        worksheet.write('S1', 'PROFUNDO', bold)
        worksheet.write('T1', 'VOLUMEN', bold)
        worksheet.write('U1', 'PESO UNITARIO', bold)
        worksheet.write('V1', 'PROMEDIO', bold)

        col = 21
        for i in range(wc):
            col += 1
            worksheet.write(0, col, 'INV. BODEGA %s' % str(i+1), bold)

        worksheet.write(0, col+1, 'SUMA INV. BODEGAS', bold)
        worksheet.write(0, col+2, 'PARA MESES', bold)
        worksheet.write(0, col+3, 'COMPRAS REALIZADAS SIN DESPACHAR', bold)
        worksheet.write(0, col+4, 'PEDIDOS EN TRANSITO', bold)
        worksheet.write(0, col+5, 'TOTAL SUMA PEDIDOS', bold)

        row = 2
        for product in products:
            worksheet.write('A%s' % row, product.get('partner') or '')
            worksheet.write('B%s' % row, product.get('mark') or '')
            worksheet.write('C%s' % row, product.get('submark') or '')
            worksheet.write('D%s' % row, product.get('categ') or '')
            worksheet.write('E%s' % row, product.get('subcateg') or '')
            worksheet.write('F%s' % row, product.get('code') or '')
            worksheet.write('G%s' % row, product.get('name') or '')
            worksheet.write('H%s' % row, product.get('puusd') or 0, money)
            worksheet.write('I%s' % row, product.get('pucop') or 0, money)
            worksheet.write('J%s' % row, product.get('wholesaler'), money)
            worksheet.write('K%s' % row, product.get('retail'), money)
            worksheet.write('L%s' % row, product.get('idate') or '')
            worksheet.write('M%s' % row, product.get('iname') or '')
            worksheet.write('N%s' % row, product.get('orderpoint') or 0),
            worksheet.write('O%s' % row, product.get('barcaode') or '')
            worksheet.write('P%s' % row, '')
            worksheet.write('Q%s' % row, product.get('height') or 0)
            worksheet.write('R%s' % row, product.get('width') or 0)
            worksheet.write('S%s' % row, product.get('length') or 0)
            worksheet.write('T%s' % row, product.get('volume') or 0)
            worksheet.write('U%s' % row, product.get('weight') or 0)
            worksheet.write('V%s' % row, product.get('average') or 0)

            col = 21
            for warehouse in product.get('warehouse_data'):
                col += 1
                worksheet.write(row-1, col, warehouse.get('quantity') or 0)

            worksheet.write(row-1, col+1, product.get('warehouse_sum') or 0)
            worksheet.write(row-1, col+2, product.get('warehouse_average') or 0)
            worksheet.write(row-1, col+3, product.get('received') or 0)
            worksheet.write(row-1, col+4, '')
            worksheet.write(row-1, col+5, product.get('warehouse_total') or 0)

            row += 1
