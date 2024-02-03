# -*- coding: utf-8 -*-

from odoo import models


class ReportStockValuation(models.AbstractModel):
    _name = 'report.stock_report.report_stock_valuation'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Stock valuation report'

    def generate_xlsx_report(self, workbook, data, objs):

        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '$#,##0'})

        worksheet_info = workbook.add_worksheet('Información')
        worksheet_info.write('A1', 'Usuario', bold)
        worksheet_info.write('B1', data.get('user'))
        worksheet_info.write('A2', 'Desde', bold)
        worksheet_info.write('B2', data.get('start'))
        worksheet_info.write('A3', 'Hasta', bold)
        worksheet_info.write('B3', data.get('end'))

        companies = data.get('companies')
        for company in companies:
            worksheet = workbook.add_worksheet(company.get('name'))

            worksheet.write('A1', 'Producto', bold)
            worksheet.write('B1', 'C. Inicial', bold)
            worksheet.write('C1', 'V. Inicial', bold)
            worksheet.write('D1', 'Entradas', bold)
            worksheet.write('E1', 'Salidas', bold)
            worksheet.write('F1', 'C. Final', bold)
            worksheet.write('G1', 'UdM', bold)
            worksheet.write('H1', 'V. Final', bold)

            row = 2
            for product in company.get('products'):
                worksheet.write('A%s' % row, product.get('name'))
                worksheet.write('B%s' % row, product.get('init'))
                worksheet.write('C%s' % row, product.get('value'), money)
                worksheet.write('D%s' % row, product.get('in'))
                worksheet.write('E%s' % row, product.get('out'))
                worksheet.write('F%s' % row, product.get('final'))
                worksheet.write('G%s' % row, product.get('uom'))
                worksheet.write('H%s' % row, product.get('total'), money)
                row += 1
