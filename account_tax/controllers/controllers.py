# -*- coding: utf-8 -*-
# from odoo import http


# class AccountTax(http.Controller):
#     @http.route('/account_tax/account_tax', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_tax/account_tax/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_tax.listing', {
#             'root': '/account_tax/account_tax',
#             'objects': http.request.env['account_tax.account_tax'].search([]),
#         })

#     @http.route('/account_tax/account_tax/objects/<model("account_tax.account_tax"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_tax.object', {
#             'object': obj
#         })
