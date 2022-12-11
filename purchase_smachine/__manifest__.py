# -*- coding: utf-8 -*-
{
    'name': "Purchase SMachine",

    'summary': "Purchase orders, tenders and agreements",

    'description': "Purchase orders, tenders and agreements",

    'author': "1-800sap",
    'contributors': ["Juan Arcos juanparmer@gmail.com"],
    'website': "https://1-800sap.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': [
        # 'date_range',
        # 'report_xlsx',
        'purchase_import'
    ],

    # always loaded
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
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # license
    'license': 'LGPL-3',
}
