# -*- coding: utf-8 -*-
{
    'name': "Sale Strong Machine",
    'summary': """
        Ventas para Strong Machine.\n
    """,
    'description': """
        - Campo número transacción en pedido de venta.
        - Tipo de cliente en contactos.
    """,
    'author': "1-800CLOUD",
    'contributors': ["Bernardo D. Lara Guevara <bernardo.lara@1-800cloud.com>"],
    'website': "https://1-800cloud.com/",
    'license': 'OPL-1',
    'category': 'Inventory/Sale',
    'version': '15.0.0.0.2',
    'depends': [
        'sale_baseline',
        'mrp'
    ],
    'data': [
        'security/ir.model.access.csv',
        #'views/sale_order_views.xml',
        'views/sm_customer_type_views.xml',
        'views/mrp_bom_view.xml',
        'views/res_partner_views.xml',
    ],
}
