# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    customer_dealer = fields.Char('Customer or Dealer')
    o_country_id = fields.Many2one('res.country', 'Country')
    o_state_id = fields.Many2one('res.country.state', 'Department')
    o_city_id = fields.Many2one('res.city', 'Origin city')
    damage_type_id = fields.Many2one('damage.type.sm', 'Damage type')
    invoice_number = fields.Char('Invoice number')
    technician_id = fields.Many2one('res.partner', 'Technician')
    tech_city_id = fields.Many2one('res.city', 'City')
    retry_ticket_id = fields.Many2one('helpdesk.ticket', 'Re-entry ticket')
    image_sm_ids = fields.One2many('helpdesk.ticket.image.sm',
                                   'ticket_id',
                                   'Images')
    date_start_sm = fields.Datetime('Date init')
    date_due_sm = fields.Date('Date due')
    days_after_init = fields.Integer('Days after init',
                                     compute="_compute_days_after_init")
    days_after_init_str = fields.Char('Alert management days',
                                      compute="_compute_days_after_init")
    guide_number = fields.Char('Guide number')
    url_guide = fields.Char('URL guide', compute='_compute_url_guide')
    date_in_ctb = fields.Date('CTB entry date')
    date_out_ctb = fields.Date('CTB departure date')

    @api.depends('guide_number')
    def _compute_url_guide(self):
        for record in self:
            url = 'https://mobile.servientrega.com/WebSitePortal/RastreoEnvioDetalle.html?Guia=%s'
            if record.guide_number:
                record.url_guide = url % record.guide_number or ''
            else:
                record.url_guide = False

    def _compute_days_after_init(self):
        for record in self:
            if record.date_start_sm:
                date_init = fields.Datetime.from_string(record.date_start_sm)
                date_now = fields.datetime.now()
                date_diff = record.team_id.resource_calendar_id.get_work_duration_data(
                    date_init, date_now)
                days = int(date_diff.get('days'))
            else:
                days = 0
            
            record.days_after_init = days
            record.days_after_init_str = '%s %s' % (
                days,
                days == 1 and _('day') or _('days')
            )
