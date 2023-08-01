# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from odoo.exceptions import AccessError

class User(models.Model):
    _inherit = 'res.users'


    def action_create_employee(self):
        self.ensure_one()
        partner_id= self.partner_id.id if self.partner_id else False
        self.env['hr.employee'].create(dict(
            name=self.name,
            partner_id=partner_id,
            company_id=self.env.company.id,
            **self.env['hr.employee']._sync_user(self)
        ))