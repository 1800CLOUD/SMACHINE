# -*- coding: utf-8 -*-
{
    'name': 'Purchase SMachine',
    'summary': '''
        Purchase orders, tenders and agreements
    ''',
    'description': '''
        - ..
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com/',
    'category': 'Inventory/Purchase',
    'license': 'LGPL-3',
<<<<<<< HEAD
    'version': '15.0.0.0.2',
=======
    'version': '15.0.0.0.1',
>>>>>>> f4d5727eb78354b89e4d262e0b0a93a7ae60dbf3
    'depends': [
        # 'date_range',
        # 'report_xlsx',
        'purchase_import'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_groups_data.xml',
        'reports/purchase_order_reports.xml',
        'views/product_category_views.xml',
        'views/product_mark_views.xml',
        'views/product_pricelist_views.xml',
        'views/product_template_views.xml',
        'views/purchase_order_views.xml',
        'views/templates.xml',
        'wizards/purchase_order_wizards.xml',
    ],
}
