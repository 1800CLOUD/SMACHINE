from odoo import models

class Users(models.Model):
    _inherit = 'res.users'

    def get_partner_ids(self):
        partner_ids = []
        if self.env.user and self.env.user.partner_id:
            partner_ids.append(self.env.user.partner_id.id)
        bot_user_id = self.env['res.users'].search([('id', '=', 1), ('active', '=', False)], limit=1)
        if bot_user_id and bot_user_id.partner_id:
            partner_ids.append(bot_user_id.partner_id.id)
        return partner_ids