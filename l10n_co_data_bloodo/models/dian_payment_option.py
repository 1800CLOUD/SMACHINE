# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression


class DianPaymentOptions(models.Model):
    _name = 'dian.payment.option'
    _description = 'Colombian payment options'

    dian_code = fields.Char('DIAN code')
    name = fields.Char('Payment Option')

    def name_get(self):
        res = []
        for record in self:
            name = u'[%s] %s' % (record.dian_code or '', record.name)
            res.append((record.id, name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike',
                     limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', 'ilike', name),
                      ('dian_code', 'ilike', name)]
        return self._search(expression.AND([domain, args]),
                            limit=limit,
                            access_rights_uid=name_get_uid)
