# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseSmachine(http.Controller):
#     @http.route('/purchase_smachine/purchase_smachine', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_smachine/purchase_smachine/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_smachine.listing', {
#             'root': '/purchase_smachine/purchase_smachine',
#             'objects': http.request.env['purchase_smachine.purchase_smachine'].search([]),
#         })

#     @http.route('/purchase_smachine/purchase_smachine/objects/<model("purchase_smachine.purchase_smachine"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_smachine.object', {
#             'object': obj
#         })
