# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseImport(http.Controller):
#     @http.route('/purchase_import/purchase_import', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_import/purchase_import/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_import.listing', {
#             'root': '/purchase_import/purchase_import',
#             'objects': http.request.env['purchase_import.purchase_import'].search([]),
#         })

#     @http.route('/purchase_import/purchase_import/objects/<model("purchase_import.purchase_import"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_import.object', {
#             'object': obj
#         })
