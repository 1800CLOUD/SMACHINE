# -*- coding: utf-8 -*-
{
    'name': "Sale Strong Machine",
    'summary': """
        Ventas para Strong Machine.\n
    """,
    'description': """
        - Campo número transacción en pedido de venta.
        - Tipo de cliente en contactos.
        - Descuento comerciar y financiero del tercero en ventas (política).
        - Imagen de producto en formato de cotización de venta.
        - Bloqueo de clientes por cupo compartido grupo comercial.
    """,
    'author': "1-800CLOUD",
    'contributors': [
        "Bernardo D. Lara Guevara <bernardo.lara@1-800cloud.com>"
    ],
    'website': "https://1-800cloud.com/",
    'license': 'OPL-1',
    'category': 'Inventory/Sale',
    'version': '15.0.0.0.6',
    'depends': [
        'sale_baseline',
        'account_voucher',
        'mrp'
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
    ],
}
