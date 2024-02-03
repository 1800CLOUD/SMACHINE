# -*- coding: utf-8 -*-
{
    'name': 'Stock Reports',
    'summary': '''
        View and create reports
    ''',
    'description': '''
        - falta descripcion.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Juan Arcos juanparmer@gmail.com'
    ],
    'website': 'https://1-800cloud.com',
    'category': 'Inventory/Inventory',
    'license': 'LGPL-3',
    'version': '15.0.0.0.8',
    'depends': [
        'date_range',
        'report_xlsx',
        'stock_account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_move_template.xml',
        'views/stock_picking_template.xml',
        'views/stock_move_line_views.xml',
        'views/stock_location_date_report_views.xml',
        'views/stock_quant_views.xml',
        'report/stock_move_report.xml',
        'report/stock_valuation_report.xml',
        'report/stock_picking_report.xml',
        'wizard/stock_move_wizard_view.xml',
        'wizard/stock_valuation_wizard_view.xml',
        'wizard/stock_location_date_wizard_view.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'stock_report/static/src/js/inventory_date_list_controller.js',
            'stock_report/static/src/js/inventory_date_list_view.js',
        ],
        'web.assets_qweb': [
            'stock_report/static/src/xml/inventory_date_report.xml',
        ]
    }
}
