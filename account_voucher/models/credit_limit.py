
from odoo import _, fields, models


class CreditLimitHistory(models.Model):
    _name = 'credit.limit.history'
    _description = 'History for credit limit'

    name = fields.Char()
    date = fields.Datetime()
    user_id = fields.Many2one('res.users', 'User who updated')
    credit = fields.Float('Credit')
    partner_id = fields.Many2one('res.partner')
