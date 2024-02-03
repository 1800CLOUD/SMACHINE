# -*- coding: utf-8 -*-
{
    'name': 'Purchase Baseline',
    'summary': '''
        Compras Baseline
    ''',
    'description': '''
        -   Generar factura de proveedor sin recepcionar cantidades (Política).
    ''',
    'author': '1-800CLOUD',
    'website': 'http://www.1-800cloud.com',
    'license': 'LGPL-3',
    'category': 'Inventory/Purchase',
    'version': '15.0.0.0.1',
    'depends': [
        'purchase'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'security/purchase_baseline_groups.xml',
        'views/res_config_settings_views.xml',
        # 'views/templates.xml',
    ],
}
