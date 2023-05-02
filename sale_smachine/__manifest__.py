# -*- coding: utf-8 -*-
{
    'name': "Sale Strong Machine",
    'summary': """
        Ventas para Strong Machine.\n
    """,
    'description': """
        - Campo número transacción en pedido de venta.
        - Tipo de cliente en contactos.
        - Descuento comerciar y financiero de tercero en ventas (política).
        - Imagen de producto en formato de cotización de venta.
        - Bloqueo de clientes por cupo compartido grupo comercial.
        - Referencia de producto en tirilla pos.
        - Dirección de entrega, ciudad destino y canal de venta desde pedido de venta a orden de entrega.
    """,
    'author': "1-800CLOUD",
    'contributors': [
        "Bernardo D. Lara Guevara <bernardo.lara@1-800cloud.com>"
    ],
    'website': "https://1-800cloud.com/",
    'license': 'OPL-1',
    'category': 'Inventory/Sale',
    'version': '15.0.0.1.7',
    'depends': [
        'sale_baseline',
        'account_voucher',
        'mrp',
        'point_of_sale',
        'l10n_co_pos',
        'account_baseline',
        'stock_report'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/sale_smachine_groups.xml',
        'views/sale_order_views.xml',
        'views/sm_customer_type_views.xml',
        'views/mrp_bom_view.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_templates.xml',
        'views/stock_picking_views.xml',
        'views/stock_picking_templates.xml',
        'views/account_views.xml',
    ],
    'assets': {
        'web.assets_qweb': [
            'sale_smachine/static/src/xml/**/*',
        ],
        'point_of_sale.assets': [
            'sale_smachine/static/src/css/OrderReceipt.css',
            'sale_smachine/static/src/js/point_of_sale.js',
        ],
    }
}
