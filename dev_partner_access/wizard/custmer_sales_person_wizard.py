# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Devintelle Solutions (<http://devintellecs.com/>).
#
##############################################################################

from odoo import api, fields, models, _

class customer_sale_person(models.TransientModel):
    _name = "customer.sale.person"
    _description = 'customer sale person'
    
    user_ids = fields.Many2many('res.users',string="Sales Person" , required=True)

    def update_sales_Person(self):
        active_id = self._context.get('active_ids')
        if active_id:
            for partner in self.env['res.partner'].browse(active_id):
                partner.users_ids = [(6, 0, self.user_ids.ids)]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
