# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    "name": "Salesperson Own Customer & Sale Orders",
    "category": 'Sales',
    "version": '1.0',
    "sequence":1,
    "summary": """
             odoo Apps will help to Salesperson can see own Customer & create their Sale Orders. own customer, customer contact only, user own customer, salesperson customer, salesperson own sale order, own customer sale order, customer order, own partner
        """,
    "description": """

      Odoo Apps will help to Salesperson can see own Customer & create thair Sale Orders.
        
        user can see own customer, sales person can see own customer, own customer only , use own sale order only, sales person own sale order only , own sale order, 
Salesperson Own Customer & Sale Orders
Odoo salesperson own customer and sale orders
Salesperson own customer
Odoo salesperson own customer
Salesperson sale orders
Odoo salesperson sale orders
Salesperson can see Own Customer
Salesperson can see Own Customer into sale order 
Odoo Salesperson can see Own Customer into sale order 
Odoo salesperson can see own customer
Partner access
Odoo partner access
Manage salesperson’s own customer 
Odoo manage salesperson’s own customer
Salesperson can access own customer in quotation/sale order
Odoo Salesperson can access own customer in quotation/sale order
Sales Team Members Access to Sales Order of Team
Sales Order of Team Members
Salesperson Own Customers
Odoo Salesperson Own Customers
Salesperson can access only specific customers visible in Quotation or Sales Order
Odoo Salesperson can access only specific customers visible in Quotation or Sales Order
Salesperson Own Customers and Sale Orders / Invoice
Odoo Salesperson Own Customers and Sale Orders / Invoice
SalesPerson can view only customers
Odoo SalesPerson can view only customers
SalesPerson on Quote/Sales order can view his own customers
Odoo SalesPerson on Quote/Sales order can view his own customers only
Allow your Salesperson can see Own Customer
Odoo Allow your Salesperson can see Own Customer
Allow your Salesperson can see Own Customer into sale order
Odoo Allow your Salesperson can see Own Customer into sale order
Allow your Salesperson can see Own Customer into Invoices
Odoo Allow your Salesperson can see Own Customer into Invoices
Sales Person can add many sales person for single customer
Odoo Sales Person can add many sales person for single customer    

    
    """,
    'author': 'DevIntelle Consulting Service Pvt.Ltd', 
    'website': 'http://www.devintellecs.com',
    'images': ['images/main_screenshot.jpg'],
    "depends": ['sale'],
    "data": [
        'security/group.xml',
	'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'wizard/custmer_sales_person_wizard_view.xml',
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    'uninstall_hook': 'uninstall_hook',
    'price':12.0,
    'currency':'EUR', 
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
