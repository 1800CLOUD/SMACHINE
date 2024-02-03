# -*- coding: utf-8 -*-

from odoo import models


class ReportStockMove(models.AbstractModel):
    _name = 'report.stock_report.report_stock_move'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Stock move report'

    def generate_xlsx_report(self, workbook, data, objs):

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '$#,##0'})

        worksheet_info = workbook.add_worksheet('Información')
        worksheet_info.write('A1', 'Compañia', bold)
        worksheet_info.write('B1', data.get('company'))
        worksheet_info.write('A2', 'Usuario', bold)
        worksheet_info.write('B2', data.get('user'))
        worksheet_info.write('A3', 'Desde', bold)
        worksheet_info.write('B3', data.get('start'))
        worksheet_info.write('A4', 'Hasta', bold)
        worksheet_info.write('B4', data.get('end'))
        if data.get('owner'):
            worksheet_info.write('A5', 'Propietario', bold)
            worksheet_info.write('B5', data.get('owner'))

        products = data.get('products')
        for product in products:
            worksheet = workbook.add_worksheet(product.get('name'))

            worksheet.write('A1', 'Fecha', bold)
            worksheet.write('B1', 'Referencia', bold)
            worksheet.write('C1', 'Producto', bold)
            worksheet.write('D1', 'Desde', bold)
            worksheet.write('E1', 'A', bold)
            worksheet.write('F1', 'Tipo', bold)
            worksheet.write('G1', 'C. Inicial', bold)
            worksheet.write('H1', 'Cantidad', bold)
            worksheet.write('I1', 'C. Final', bold)
            worksheet.write('J1', 'UdM', bold)
            worksheet.write('K1', 'P. Unitario', bold)
            worksheet.write('L1', 'P. Total', bold)
            worksheet.write('M1', 'Estado', bold)

            row = 2
            for move in product.get('moves'):
                worksheet.write('A%s' % row, move.get('date'))
                worksheet.write('B%s' % row, move.get('reference'))
                worksheet.write('C%s' % row, move.get('product'))
                worksheet.write('D%s' % row, move.get('from'))
                worksheet.write('E%s' % row, move.get('to'))
                worksheet.write('F%s' % row, move.get('type'))
                worksheet.write('G%s' % row, move.get('init'))
                worksheet.write('H%s' % row, move.get('demand'))
                worksheet.write('I%s' % row, move.get('final'))
                worksheet.write('J%s' % row, move.get('uom'))
                worksheet.write('K%s' % row, move.get('unit'), money)
                worksheet.write('L%s' % row, move.get('total'), money)
                worksheet.write('M%s' % row, move.get('status'))
                row += 1
