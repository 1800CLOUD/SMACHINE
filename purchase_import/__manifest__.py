# -*- coding: utf-8 -*-
{
    'name': 'Purchase Import',
    'summary': '''
        Purchase imports
    ''',
    'description': '''
        - falta descripcion.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com/',
    'category': 'Inventory/Purchase',
    'license': 'LGPL-3',
    'version': '15.0.0.0.1',
    'depends': [
        'purchase_stock',
        'stock_landed_costs'
    ],
    'data': [
        'security/res_groups_security.xml',
        'security/ir_rule_security.xml',
        'security/ir.model.access.csv',
        'data/account_incoterms_data.xml',
        'data/ir_sequence_data.xml',
        'data/ir_ui_menu_data.xml',
        'data/product_product_data.xml',
        'data/res_partner_data.xml',
        'views/account_incoterms_view.xml',
        'views/account_move_view.xml',
        'views/product_template_view.xml',
        'views/purchase_import_view.xml',
        'views/res_config_settings_views.xml',
        'views/stock_landed_view.xml',
    ],
}
