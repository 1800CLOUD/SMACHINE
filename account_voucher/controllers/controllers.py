# -*- coding: utf-8 -*-
# from odoo import http


# class AccountVoucher(http.Controller):
#     @http.route('/account_voucher/account_voucher', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_voucher/account_voucher/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_voucher.listing', {
#             'root': '/account_voucher/account_voucher',
#             'objects': http.request.env['account_voucher.account_voucher'].search([]),
#         })

#     @http.route('/account_voucher/account_voucher/objects/<model("account_voucher.account_voucher"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_voucher.object', {
#             'object': obj
#         })
