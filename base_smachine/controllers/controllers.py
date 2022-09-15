# -*- coding: utf-8 -*-
# from odoo import http


# class BaseSmachine(http.Controller):
#     @http.route('/base_smachine/base_smachine', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/base_smachine/base_smachine/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('base_smachine.listing', {
#             'root': '/base_smachine/base_smachine',
#             'objects': http.request.env['base_smachine.base_smachine'].search([]),
#         })

#     @http.route('/base_smachine/base_smachine/objects/<model("base_smachine.base_smachine"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('base_smachine.object', {
#             'object': obj
#         })
