# -*- coding: utf-8 -*-
{
    'name': 'Voucher Account',
    'summary': '''
        Voucher Account
    ''',
    'description': '''
        - falta descripcion.
    ''',
    'author': '1-800CLOUD',
    'contributors': ['Juan Arcos juanparmer@gmail.com'],
    'website': 'https://www.1-800cloud.com/',
    'license': 'LGPL-3',
    'category': 'Accounting/Accounting',
    'version': '15.0.0.2.3',
    'depends': [
        'account_payment',
        'sale',
        'account_baseline',
        'contacts'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        # 'data/res_groups_data.xml',
        'security/res_groups_security.xml',
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
        'views/account_voucher_line_view.xml',
        'views/account_voucher_view.xml',
        'views/account_payment_term_view.xml',
        'views/account_journal_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
        'views/res_config_settings_views.xml',
        'wizard/account_voucher_wizard_view.xml',
        'report/account_voucher_reports.xml',
        'views/account_voucher_customer_template.xml',
        'views/account_voucher_supplier_template.xml',
        'views/generic_accounting_receipt_template.xml',
        'views/voucher_mail_error_views.xml',
        'data/mail_template_voucher_data.xml',
    ],
    'installable': True,
}
