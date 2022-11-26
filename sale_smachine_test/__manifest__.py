# -*- coding: utf-8 -*-
{
    'name': "Sale SMachine",
    'summary': """
    - Sale orders, tenders and agreements.\n
    """,
    'description': """
        - Sale orders, tenders and agreements.
        - campo número transacción en pedido de venta.
    """,
    'author': "1-800CLOUD",
    'contributors': ["Fernando Fernández nffernandezm@gmail.com"],
    'website': "https://1-800cloud.com/",
    'license': 'OPL-1',
    'category': 'Inventory/Sale',
    'version': '15.0.0.0.1',
    'depends': [
        # 'date_range',
        'sale',
        'account',
        'sale_baseline'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_fiscal_position_views.xml',
        'views/account_payment_mode_view.xml',
        'views/mrp_bom_view.xml',
        'views/sale_order_view.xml',
        #'views/res_config_settings_views.xml',
    ],
}
