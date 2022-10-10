# -*- coding: utf-8 -*-

from lxml import etree

from odoo import models, fields, api, _


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    def write(self, vals):
        if 'use_website_helpdesk_form' in vals and not vals['use_website_helpdesk_form']:
            if self.website_form_view_id:
                self.website_form_view_id.unlink()
                vals['website_form_view_id'] = False
        return super(HelpdeskTeam, self).write(vals)

    def _ensure_submit_form_view(self):
        for team in self:
            if not team.website_form_view_id:
                default_form = etree.fromstring(self.env.ref(
                    'website_helpdesk_form_smachine.ticket_submit_form').arch)
                xmlid = 'website_helpdesk_form_smachine.team_form_' + \
                    str(team.id)
                form_template = self.env['ir.ui.view'].create({
                    'type': 'qweb',
                    'arch': etree.tostring(default_form),
                    'name': xmlid,
                    'key': xmlid
                })
                self.env['ir.model.data'].create({
                    'module': 'website_helpdesk_form_smachine',
                    'name': xmlid.split('.')[1],
                    'model': 'ir.ui.view',
                    'res_id': form_template.id,
                    'noupdate': True
                })

                team.write({'website_form_view_id': form_template.id})

    def _get_data_fields_website_form(self):
        self.ensure_one()
        self = self.sudo()
        out = {}
        # Doc type
        doc_type_obj = self.env['l10n_latam.identification.type']
        country_id = self.company_id.country_id
        domain = []
        if country_id:
            domain = [('country_id', '=', country_id.id)]
        doc_type_ids = doc_type_obj.search(domain)
        out['doc_types'] = [(d.id, d.name) for d in doc_type_ids]
        # Country
        domain = []
        country_ids = self.env['res.country'].search(domain)
        out['countries'] = [(s.id, s.name) for s in country_ids]
        # Department
        # domain = []
        # state_ids = self.env['res.country.state'].search(domain)
        # out['states'] = [(s.id, s.name) for s in state_ids]
        # City
        # domain = []
        # city_ids = self.env['res.city'].search(domain)
        # out['o_cities'] = [(c.id, c.name) for c in city_ids]
        # Damage type
        domain = []
        damage_ids = self.env['damage.type.sm'].search(domain)
        out['damage_type'] = [(c.id, c.name) for c in damage_ids]
        # Products
        domain = [('detailed_type','=','product')]
        product_ids = self.env['product.product'].search(domain)
        out['products'] = [(p.id, p.display_name) for p in product_ids]
        if self.web_technician_req:
            # city
            domain = [('country_id', '=', country_id.id)]
            city_ids = self.env['res.city'].search(domain)
            out['cities'] = [(p.id, p.display_name) for p in city_ids]
            domain = [('is_technician', '=', True)]
            tech_ids = self.env['res.partner'].search(domain)
            out['technicians'] = [(p.id, p.display_name) for p in tech_ids]
        return out
