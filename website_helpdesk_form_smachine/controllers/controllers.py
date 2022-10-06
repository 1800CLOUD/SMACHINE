# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class WebsiteHelpdeskFormSmachine(http.Controller):

    @http.route('/helpdesk_form/filter_field/', type='json', auth='public')
    def filter_field(self, **kw):
        data = []
        value = kw.get('value')
        field = kw.get('field')
        model = kw.get('model')
        if value and field and model:
            records = request.env[model].sudo().search_read(
                [(field,'=',int(value))], 
                ['id', 'name']
            )
            data = [[str(l['id']), str(l['name']).upper()] for l in records]
        return data

#     @http.route('/helpdesk_smachine/helpdesk_smachine', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/helpdesk_smachine/helpdesk_smachine/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('helpdesk_smachine.listing', {
#             'root': '/helpdesk_smachine/helpdesk_smachine',
#             'objects': http.request.env['helpdesk_smachine.helpdesk_smachine'].search([]),
#         })

#     @http.route('/helpdesk_smachine/helpdesk_smachine/objects/<model("helpdesk_smachine.helpdesk_smachine"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('helpdesk_smachine.object', {
#             'object': obj
#         })
