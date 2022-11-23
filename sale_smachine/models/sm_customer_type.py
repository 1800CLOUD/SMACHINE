# -*- coding: utf-8 -*-

from odoo import fields, models, _

class SmCustomerType(models.Model):
    _name = 'sm.customer.type'
    _description = 'Customer type Strong Machine'

    name = fields.Char('Name')
    code = fields.Char('Code')

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = "[{}] {}".format(record.code, name)
            result.append((record.id, name))
        return result