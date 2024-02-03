# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Hide Product Price",
    "author": "Softhealer Technologies",
    "website": "http://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Sales",
    "summary": "hide sales price app, Disable sales price,disable cost price, show cost price module,remove cost price, remove sales price, hide cost price, show sales price,Hide Product Price odoo",
    "description": """Useful to hide sales price or cost price in the tree, kanban and form view.""",
    "version": "15.0.3",
    "depends": [
        "product",
    ],
    "application": True,
    "data": [
        "security/hide_price_security.xml",
        "views/hide_price_view.xml",
    ],
    "images": ["static/description/background.jpg", ],
    "live_test_url": "https://youtu.be/k7u4yHtNttE",
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "price": 8,
    "currency": "EUR"
}
