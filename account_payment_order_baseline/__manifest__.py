# -*- coding: utf-8 -*-
{
    'name': 'Account Payment Order Baseline',
    'summary': '''
        Ordenes de pago Baseline.
    ''',
    'description': '''
        - Tasa de cambio modificable en ordenes de pago.
        - Quitar validación de tamaño del numero de cuenta bancaria (bic).
        - Cuenta de cobro desde el diario.
        - Cuenta de pago desde el diario.
    ''',
    'author': '1-800CLOUD',
    'website': 'https://www.1-800cloud.com',
    'license': 'LGPL-3',
    'category': 'Banking addons',
    'version': '15.0.0.0.2',
    'depends': [
        'account_payment_order',
        'account_baseline'
    ],
    'data': [
        'security/account_payment_order_baseline_groups.xml',
        'views/account_payment_order_views.xml',
        'views/res_company_views.xml',
    ],
}
