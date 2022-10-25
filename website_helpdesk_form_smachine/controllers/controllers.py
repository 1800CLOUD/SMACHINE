# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class WebsiteHelpdeskFormSmachine(http.Controller):

    @http.route('/helpdesk_form/filter_field/', type='json', auth='public')
    def filter_field(self, **kw):
        data = []
        records = False
        domain = kw.get('domain')
        value = kw.get('value')
        field = kw.get('field')
        model = kw.get('model')
        if domain and model:
            domain = eval(domain)
            records = request.env[model].sudo().search_read(
                domain,
                ['id', 'name']
            )
        elif value and field and model:
            records = request.env[model].sudo().search_read(
                [(field, '=', int(value))],
                ['id', 'name']
            )
        if records:
            data = [[str(l['id']), str(l['name']).upper()] for l in records]
        return data

    @http.route('/helpdesk_form/partner_tickets/', type='json', auth='public')
    def partner_tickets(self, **kw):
        data = []
        tickets = False
        vat = kw.get('vat')
        doc_type = kw.get('doc_type')
        if vat and doc_type:
            records = request.env['res.partner'].sudo().search_read(
                [('vat', '=', int(vat)),
                 ('l10n_latam_identification_type_id', '=', int(doc_type))],
                ['id', 'name'],
                limit=1
            )
            if records:
                tickets = request.env['helpdesk.ticket'].sudo().search_read(
                    [('partner_id', '=', records[0].get('id'))],
                    ['id', 'name']
                )
        if tickets:
            data = [
                [
                    str(l['id']),
                    '(#%s) %s' % (str(l['id']), str(l['name']))
                ] for l in tickets
            ]
        return data
