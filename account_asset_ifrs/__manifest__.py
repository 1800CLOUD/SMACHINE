# -*- coding: utf-8 -*-
{
    'name': 'IFRS Assets Management',
    'summary': '''
        IFRS Assets Management
    ''',
    'description': '''
        - IFRS Assets Management
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com/',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'version': '15.0.0.0.1',
    'depends': [
        'account_asset',
        'account_ifrs',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset_view.xml',
    ],
}
