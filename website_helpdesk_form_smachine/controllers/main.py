# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers import form


class WebsiteForm(form.WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        name = request.params.get('partner_name', False)
        phone = request.params.get('partner_phone', False)
        doc_type_id = request.params.pop('partner_doc_type_id')
        vat = request.params.pop('partner_vat')
        email = request.params.pop('partner_email')
        if request.params.get('reentry'):
            request.params.pop('reentry')

        if doc_type_id and vat:
            partner = request.env['res.partner'].sudo().search(
                [('vat', '=', vat),
                 ('l10n_latam_identification_type_id', '=', doc_type_id)],
                limit=1
            )
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'email': email,
                    'name': name,
                    'vat': vat,
                    'l10n_latam_identification_type_id': doc_type_id and
                    int(doc_type_id) or
                    False,
                    'phone': phone

                })
            request.params['partner_id'] = partner.id

        res = super(WebsiteForm, self)._handle_website_form(model_name,
                                                            **kwargs)
        request.params['partner_email'] = email
        return res
