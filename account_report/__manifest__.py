# -*- coding: utf-8 -*-
{
    'name': 'Account Report',
    'summary': '''
        Account Report
    ''',
    'description': '''
        - falta descripcion de los reportes.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com',
        'Fernando Fernandez nffernandezm@gmail.com',
        'Bernardo D. Lara G. bernardo.lara@1-800cloud.com'
    ],
    'website': 'https://1-800cloud.com/',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'version': '15.0.0.4.3',
    'depends': [
        'base',
        'account_ifrs',
        'report_xlsx',
        'account_financial_report',
        'account_reports',
        'base_data_baseline',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups_security.xml',
        'data/ir_actions_server_data.xml',
        'report/account_auxiliary_report.xml',
        'report/account_auxiliary_invoices_report.xml',
        'report/account_balance_report.xml',
        'report/account_journal_report.xml',
        'report/account_balance_major_report.xml',
        'report/account_balance_inventory_report.xml',
        'report/report_account_aged_receivable.xml',
        'report/reports.xml',
        'templates/internal_layout_template.xml',
        'templates/account_auxiliary_template.xml',
        'templates/account_balance_template.xml',
        'templates/account_journal_template.xml',
        'templates/account_balance_major_template.xml',
        'templates/account_balance_inventory_template.xml',
        'views/account_group_view.xml',
        'wizard/account_auxiliary_invoices_wizard.xml',
        'wizard/account_auxiliary_wizard.xml',
        'wizard/account_balance_wizard.xml',
        'wizard/account_balance_major_wizard.xml',
        'wizard/account_journal_wizard.xml',
        'wizard/account_balance_inventory_wizard.xml',
        'report/report_payment_days.xml',
        'views/menuitem_views.xml',
        'views/search_template_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'account_report/static/src/js/account_aged_receivable.js',
            'account_report/static/src/css/report_preview.css',
        ]
    },
    'post_init_hook': 'post_init_hook',
}
