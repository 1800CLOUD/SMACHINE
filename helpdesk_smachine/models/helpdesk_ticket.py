# -*- coding: utf-8 -*-

from odoo import fields, models, _

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    partner_doc_type_id = fields.Many2one('l10n_latam.document.type',
        'Document type')
    partner_vat = fields.Char('Identification number')
    customer_dealer = fields.Char('Customer or Dealer')
    country_id = fields.Many2one('res.country', 'Country')
    state_id = fields.Many2one('res.country.state', 'Department')
    origin_city_id = fields.Many2one('res.city', 'Origin city')
    damage_type_id = fields.Many2one('damage.type.sm', 'Damage type')
    invoice_number = fields.Char('Invoice number')
    technician_id = fields.Many2one('res.partner', 'Technician')
    tech_city_id = fields.Many2one('res.city', 'City')
