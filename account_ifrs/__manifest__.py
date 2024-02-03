# -*- coding: utf-8 -*-
{
    'name': 'IFRS Account',
    'summary': '''
        IFRS Account
    ''',
    'description': '''
        IFRS Account
        - falta descripcion.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'version': '15.0.0.0.1',
    'depends': ['account'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/res_groups_security.xml',
        'views/account_account_view.xml',
        'views/account_move_view.xml',
    ],
}
