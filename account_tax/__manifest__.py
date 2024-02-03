# -*- coding: utf-8 -*-
{
    'name': 'Account Tax',
    'summary': '''
        Account Tax
    ''',
    'description': '''
        - falta descripcion.
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
        'account',
        'contacts',
        'purchase',
        'sale',
    ],
    'data': [
        'data/res.partner.classification.csv',
        'data/ir_ui_menu_data.xml',
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/account_tax_view.xml',
        'views/product_category_view.xml',
        'views/purchase_order_view.xml',
        'views/res_city_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',
    ],
}
