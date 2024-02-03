# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseBaseline(http.Controller):
#     @http.route('/purchase_baseline/purchase_baseline', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_baseline/purchase_baseline/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_baseline.listing', {
#             'root': '/purchase_baseline/purchase_baseline',
#             'objects': http.request.env['purchase_baseline.purchase_baseline'].search([]),
#         })

#     @http.route('/purchase_baseline/purchase_baseline/objects/<model("purchase_baseline.purchase_baseline"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_baseline.object', {
#             'object': obj
#         })
