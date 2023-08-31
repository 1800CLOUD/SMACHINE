# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget Sale for seller',
    'category': 'Accounting/Accounting',
    'description': """
Presupuesto de ventas por vendedor y marca
--------------------------------------------------------------
""",
    'license': 'LGPL-3',
    'version': '15.0.0.0.4',
    'depends': ['account', 'sale', 'base_setup',],
    'data': [
        'security/ir.model.access.csv',
        'security/account_budget_security.xml',
        'views/account_budget_views.xml',
        
    ],
    
}
