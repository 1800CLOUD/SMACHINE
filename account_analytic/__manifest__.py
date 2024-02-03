# -*- coding: utf-8 -*-
{
    'name': 'Analytic Accounting',
    'summary': '''
        Module for defining analytic accounting object.
    ''',
    'description': '''
        - Module for defining analytic accounting object.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com/',
    'category': 'Accounting/Accounting',
    'license': 'LGPL-3',
    'version': '15.0.0.0.2',
    'depends': [
        'account',
        'base_data_baseline',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'security/account_analytic_groups.xml',
        'views/account_analytic_view.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
    ],
}
