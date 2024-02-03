# -*- coding: utf-8 -*-
# from odoo import http


# class StockReport(http.Controller):
#     @http.route('/stock_report/stock_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_report/stock_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_report.listing', {
#             'root': '/stock_report/stock_report',
#             'objects': http.request.env['stock_report.stock_report'].search([]),
#         })

#     @http.route('/stock_report/stock_report/objects/<model("stock_report.stock_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_report.object', {
#             'object': obj
#         })
