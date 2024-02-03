# coding: utf-8
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression


class DianTaxType(models.Model):
    _name = 'dian.tax.type'
    _description = 'DIAN Tax Type'

    name = fields.Char('Name')
    description = fields.Char('Description')
    dian_code = fields.Char('DIAN code', required=True)
    retention = fields.Boolean('Withholding')

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
        return self._search(
            expression.AND([domain, args]),
            limit=limit,
            access_rights_uid=name_get_uid
        )
