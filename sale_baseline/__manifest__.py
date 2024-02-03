# -*- coding: utf-8 -*-
{
    'name': 'Sale Baseline',
    'summary': '''
        Sale Baseline
    ''',
    'description': '''
        - Restringir la edición del campo de vendedor en ventas y facturas (Política).
        - Permite agregar una etiqueta y bloquear al cliente que no ha comprado en los últimos meses (Política).
        - No permite confirmar el pedido de venta si no hay cantidades disponibles.
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com',
    'license': 'LGPL-3',
    'category': 'Sales',
    'version': '15.0.0.0.6',
    'depends': ['sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/sale_baseline_groups.xml',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
}
