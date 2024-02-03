# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ReportAccountAgedReceivable(models.Model):
    _inherit = 'account.aged.receivable'

    filter_sales = True

    def _get_options(self, previous_options=None):
        options = super(ReportAccountAgedReceivable, self)._get_options(previous_options=previous_options)
        user_id = self.env.user
        if user_id.has_group('sales_team.group_sale_salesman_all_leads'):
            options['sales'] = True
        else:
            options['sales'] = False
            options['vendor_ids'] = [user_id.id]
        return options

    def get_report_informations(self, options):
        '''
        return a dictionary of informations that will be needed by the js widget, manager_id, footnotes, html of report and searchview, ...
        '''
        options = self._get_options(options)
        self = self.with_context(self._set_context(options)) # For multicompany, when allowed companies are changed by options (such as aggregare_tax_unit)

        searchview_dict = {'options': options, 'context': self.env.context}
        # Check if report needs analytic
        if options.get('analytic_accounts') is not None:
            options['selected_analytic_account_names'] = [self.env['account.analytic.account'].browse(int(account)).name for account in options['analytic_accounts']]
        if options.get('analytic_tags') is not None:
            options['selected_analytic_tag_names'] = [self.env['account.analytic.tag'].browse(int(tag)).name for tag in options['analytic_tags']]
        if options.get('partner'):
            options['selected_partner_ids'] = [self.env['res.partner'].browse(int(partner)).name for partner in options['partner_ids']]
            options['selected_partner_categories'] = [self.env['res.partner.category'].browse(int(category)).name for category in (options.get('partner_categories') or [])]
        if options.get('sales'):
            options['selected_vendor_ids'] = [self.env['res.users'].browse(int(vendor)).name for vendor in (options.get('vendor_ids') or [])]
            options['selected_sale_team_ids'] = [self.env['crm.team'].browse(int(sale_team)).name for sale_team in (options.get('sale_team_ids') or [])]

        # Check whether there are unposted entries for the selected period or not (if the report allows it)
        if options.get('date') and options.get('all_entries') is not None:
            date_to = options['date'].get('date_to') or options['date'].get('date') or fields.Date.today()
            period_domain = [('state', '=', 'draft'), ('date', '<=', date_to)]
            options['unposted_in_period'] = bool(self.env['account.move'].search_count(period_domain))

        report_manager = self._get_report_manager(options)
        info = {'options': options,
                'context': self.env.context,
                'report_manager_id': report_manager.id,
                'footnotes': [{'id': f.id, 'line': f.line, 'text': f.text} for f in report_manager.footnotes_ids],
                'buttons': self._get_reports_buttons_in_sequence(options),
                'main_html': self.get_html(options),
                'searchview_html': self.env['ir.ui.view']._render_template(self._get_templates().get('search_template', 'account_report.search_template'), values=searchview_dict),
                }
        return info

    @api.model
    def _get_options_sales_domain(self, options):
        domain = []
        if options.get('vendor_ids'):
            vendor_ids = [int(vendor) for vendor in options['vendor_ids']]
            domain.append(('move_id.invoice_user_id', 'in', vendor_ids))
        if options.get('sale_team_ids'):
            sale_team_ids = [int(sale_team) for sale_team in options['sale_team_ids']]
            domain.append(('move_id.team_id', 'in', sale_team_ids))
        return domain
    
    @api.model
    def _get_options_domain(self, options):
        domain = super(ReportAccountAgedReceivable, self)._get_options_domain(options)
        
        domain += self._get_options_sales_domain(options)
        return domain

    @api.model
    def _get_templates(self):
        # OVERRIDE
        templates = super(ReportAccountAgedReceivable, self)._get_templates()
        templates['search_template'] = 'account_report.search_template_inh'
        return templates
    
    def _init_filter_partner(self, options, previous_options=None):
        if not self.filter_partner:
            return

        options['partner'] = True
        options['partner_ids'] = previous_options and previous_options.get('partner_ids') or []
        options['partner_categories'] = previous_options and previous_options.get('partner_categories') or []

        selected_partner_ids = [int(partner) for partner in options['partner_ids']]
        selected_partners = selected_partner_ids and self.env['res.partner'].browse(selected_partner_ids) or self.env['res.partner']
        options['selected_partner_ids'] = selected_partners.mapped('name')

        selected_partner_category_ids = [int(category) for category in options['partner_categories']]
        selected_partner_categories = selected_partner_category_ids and self.env['res.partner.category'].browse(selected_partner_category_ids) or self.env['res.partner.category']
        options['selected_partner_categories'] = selected_partner_categories.mapped('name')

    def _init_filter_sales(self, options, previous_options=None):

        if not self.filter_sales:
            return
        options['sales'] = True
        options['vendor_ids'] = previous_options and previous_options.get('vendor_ids') or []
        options['sale_team_ids'] = previous_options and previous_options.get('sale_team_ids') or []

        selected_vendor_ids = [int(vendor) for vendor in options['vendor_ids']]
        selected_vendor_ids = selected_vendor_ids and self.env['res.users'].browse(selected_vendor_ids) or self.env['res.users']
        options['selected_vendor_ids'] = selected_vendor_ids.mapped('name')

        selected_sale_team_ids = [int(sale_team) for sale_team in options['sale_team_ids']]
        selected_sale_team_ids = selected_sale_team_ids and self.env['crm.team'].browse(selected_sale_team_ids) or self.env['res.users']
        options['selected_sale_team_ids'] = selected_sale_team_ids.mapped('name')
