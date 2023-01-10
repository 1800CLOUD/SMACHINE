# -*- coding: utf-8 -*-
{
    'name': 'Extensión de Factura Electrónica Strong Machine',
    'summary': '''
        Extensión de factura electrónica para Strong Machine.
    ''',
    'description': '''
        - Formato factura de Strong Machine.
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com',
    'contributors': ['Bernardo David Lara Guevara <bernardo.lara@1-800cloud.com>'],
    'category': 'Accounting/Localizations/EDI',
    'license': 'OPL-1',
    'version': '15.0.0.0.1',
    'depends': [
        'l10n_co_bloodo'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'reports/account_move_templates.xml',
        # 'views/templates.xml',
    ],
}
