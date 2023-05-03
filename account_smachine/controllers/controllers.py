# -*- coding: utf-8 -*-
# from odoo import http


# class AccountSmachine(http.Controller):
#     @http.route('/account_smachine/account_smachine', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_smachine/account_smachine/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_smachine.listing', {
#             'root': '/account_smachine/account_smachine',
#             'objects': http.request.env['account_smachine.account_smachine'].search([]),
#         })

#     @http.route('/account_smachine/account_smachine/objects/<model("account_smachine.account_smachine"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_smachine.object', {
#             'object': obj
#         })
