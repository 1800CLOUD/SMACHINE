# -*- coding: utf-8 -*-
{
    'name': "Sale SMachine",

    'summary': "SALE orders, tenders and agreements",

    'description': "sale orders, tenders and agreements",

    'author': "1-800sap",
    'contributors': ["Fernando Fernández nffernandezm@gmail.com"],
    'website': "https://1-800sap.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Sale',
    'version': '15.1',

    # any module necessary for this one to work correctly
    'depends': [
        # 'date_range',
        'sale',
        'account'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position_views.xml',
        'views/account_payment_mode_view.xml',
        'views/mrp_bom_view.xml',
        'views/sale_order_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # license
    'license': 'LGPL-3',
}
