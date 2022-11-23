# -*- coding: utf-8 -*-
{
    'name': "Sale Strong Machine",
    'summary': """
    - Vantas para Strong Machine.\n
    """,
    'description': """
        - Campo número transacción en pedido de venta.
    """,
    'author': "1-800CLOUD,\nBernardo D. Lara Guevara",
    'contributors': ["Bernardo D. Lara Guevara <bernardo.lara@1-800cloud.com>"],
    'website': "https://1-800cloud.com/",
    'license': 'OPL-1',
    'category': 'Inventory/Sale',
    'version': '15.0.0.0.1',
    'depends': [
        'sale_baseline'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
    ],
}
