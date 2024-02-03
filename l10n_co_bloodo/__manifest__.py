# -*- coding: utf-8 -*-
{
    'name': 'Colombian E-Invoicing and Document Support',
    'summary': """
        Electronic invoicing, supporting document and events,
         direct integration with the DIAN.
        """,
    'description': """
        Direct integration with DIAN
        - Direct electronic invoicing.
        - Direct support document.
        - Direct events, Resolution 85.
    """,
    'author': 'Bloodo by Bernardo D. Lara Guevara <bdlgrw@gmail.com, bloodo.dev.solutions@gmail.com>',
    'contributors': ['Bernardo David Lara Guevara <bdlgrw@gmail.com>'],
    'website': 'https://www.linkedin.com/in/bernardo-d-lara-guevara-2267a8142'
    '?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details'
    '%3BusuaZT0LSMGZWpv0e%2B0KLA%3D%3D',
    'license': 'OPL-1',
    'category': 'Accounting/Localizations/EDI',
    'version': '15.0.0.1.5',
    'depends': [
        'account',
        'l10n_co',
        'l10n_latam_base',
        'uom',
        'account_debit_note',
        'account_journal_sequence',
        'l10n_co_data_bloodo',
        'resource'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        # 'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/ir_sequence_views.xml',
        'views/account_journal_views.xml',
        'views/res_company_views.xml',
        'views/dian_email_templates.xml',
        'views/dian_event_email_templates.xml',
        'views/history_dian_event_views.xml',
        'wizards/account_move_reversal_views.xml',
        'wizards/account_debit_note_views.xml',
        'wizards/invoice_import_wizard_views.xml',
        'reports/account_move_reports.xml',
        'reports/account_move_templates.xml',
    ],
    'installable': True,
    # 'post_init_hook': 'post_init_hook',
    # 'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_backend': [
            'l10n_co_bloodo/static/src/css/ei_group.css',
        ],
    },
    'external_dependencies': {
        'python': [
            'unidecode',
            'xmlsig',
            'jinja2',
            'OpenSSL',
            'xades',
            'qrcode',
            'pgxades'
        ],
    }
}
