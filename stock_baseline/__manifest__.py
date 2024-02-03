# -*- coding: utf-8 -*-
{
    'name': 'Stock Baseline',
    'summary': '''
        - Llevar notas de los pedidos de venta a las ordenes de entrega (política).\n
    ''',
    'description': '''
        - Llevar notas de los pedidos de venta a las ordenes de entrega (política).
    ''',
    'author': '1-800CLOUD',
    'website': 'http://www.1-800cloud.com',
    'license': 'OPL-1',
    'category': 'Inventory/Inventory',
    'version': '15.0.0.0.8',
    'depends': [
        'sale_stock',
        'stock_account'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/stock_picking_views.xml',
        'views/stock_picking_type_views.xml',
        'views/stock_quant_templates.xml',
        'views/stock_move_line_views.xml',
    ],
}
