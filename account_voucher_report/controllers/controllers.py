# -*- coding: utf-8 -*-
# from odoo import http


# class AccountVoucherReport(http.Controller):
#     @http.route('/account_voucher_report/account_voucher_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_voucher_report/account_voucher_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_voucher_report.listing', {
#             'root': '/account_voucher_report/account_voucher_report',
#             'objects': http.request.env['account_voucher_report.account_voucher_report'].search([]),
#         })

#     @http.route('/account_voucher_report/account_voucher_report/objects/<model("account_voucher_report.account_voucher_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_voucher_report.object', {
#             'object': obj
#         })
