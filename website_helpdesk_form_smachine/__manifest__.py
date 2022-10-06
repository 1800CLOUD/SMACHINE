# -*- coding: utf-8 -*-
{
    'name': 'Online Ticket Submission Strong Machine SAS',
    'summary': '''
        website_helpdesk_form module extension for Strong Machine company.    
    ''',
    'description': '''
        - Web form extension with supplemental fields.
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com',
    'category': 'Services/Helpdesk',
    'license': 'OPL-1',
    'version': '15.0.0.0.1',
    'depends': [
        'helpdesk_smachine',
        'website_helpdesk_form',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/helpdesk_templates.xml',
    ],
    'assets': {
        'web.assets_common': [
            'website_helpdesk_form_smachine/static/src/js/country.js',
        ],
    }
}
