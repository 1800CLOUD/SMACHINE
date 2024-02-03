# -*- coding: utf-8 -*-
{
    'name': 'Voucher Account Report',
    'summary': '''
        Reporte de pagos
    ''',
    'description': '''
        - Reporte de pagos
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com/',
    'license': 'LGPL-3',
    'category': 'Accounting/Accounting',
    'version': '15.0.0.0.3',
    'depends': [
        'account_voucher',
        'account_report',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/account_voucher_report_security.xml',
        'views/account_voucher_report_views.xml',
    ],
}
