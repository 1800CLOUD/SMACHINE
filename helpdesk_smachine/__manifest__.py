# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Strong Machine SAS',
    'summary': '''
        Helpdesk module extension for Strong Machine company.    
    ''',
    'description': '''
        - Web form extension with supplemental fields.
        - Guide number servientrega and dates CTB in tickets.
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com',
    'category': 'Services/Helpdesk',
    'license': 'OPL-1',
    'version': '15.0.0.1.1',
    'depends': [
        'helpdesk',
        'resource',
        'helpdesk_stock',
        # 'helpdesk_repair',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/damage_type_sm_views.xml',
        'views/res_partner_views.xml',
        'views/helpdesk_team_views.xml',
        'views/helpdesk_ticket_views.xml',
        # 'views/repair_order_views.xml',
        'views/stock_picking_views.xml',
        # 'reports/repair_order_reports.xml',
        # 'reports/repair_order_templates.xml',
        # 'data/denial_letter_mail_template_data.xml',
    ],
}
