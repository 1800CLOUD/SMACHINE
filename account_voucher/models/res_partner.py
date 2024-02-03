
from datetime import datetime
from email.policy import default
from odoo import _, fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'


    block_expired_invoice = fields.Boolean(
        'Block Expired Invoice',
        default=True)
    block_credit_limit = fields.Boolean(
        'Block Credit Limit',
        default=True)

    quota_limit_initial = fields.Float(
        'Quota Limit Initial')
    

    credit_limit_history_ids = fields.One2many(
        'credit.limit.history',
        'partner_id')
    
    account_advance_id = fields.Many2one(
        'account.account',
        'Account advance')
    
    credit_limit = fields.Float(compute='_compute_credit_limit')

    def _compute_credit_limit(self):
        for partner_id in self:
            partner_credit = partner_id.credit
            quota_limit_initial = partner_id.quota_limit_initial
        
            orders_client = self.env['sale.order'].search(
                [('partner_id', '=', partner_id.id), 
                ('state', 'in', ['sale','done']),
                ('invoice_status','=','to invoice')]
            )
            sum_orders_total = sum([x.amount_total for x in orders_client])
            credit_limit = quota_limit_initial - (
                partner_credit + sum_orders_total
            )
            partner_id.credit_limit = credit_limit

    @api.onchange('quota_limit_initial')
    def create_history_credit_partner(self):
        for record in self:
            vals = {
                'date': datetime.now(),
                'name': '',
                'user_id': self.env.user.id,
                'credit': record.quota_limit_initial,
                'partner_id': record.id.origin
            }

            record.credit_limit_history_ids.create(vals)