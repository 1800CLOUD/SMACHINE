# -*- coding: utf-8 -*-
from cgitb import reset

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    account_advance_id = fields.Many2one(
        'account.voucher',
        string="Cuenta anticipo"
        )
    check_immediate_payment = fields.Boolean() 
    account_voucher_ids = fields.Many2many(
        comodel_name='account.voucher',
        string='Account Voucher Advance'
    )
    active_payment_advance = fields.Boolean(
        'Enable payment with advances'
        )
    advance_payment_manually = fields.Boolean(
        'Autorizar sin anticipos',
        help='Autorizar si el pedido está bloqueado por no tener anticipos.',
        ) 
    unlock_for_credit_limit = fields.Boolean(
        'Autorizar con LdC',
        help='Autorizar si el cliente esta bloqueado por límite de crédito.',
        default=False
    )
    unlock_for_overdue_invoices = fields.Boolean(
        'Autorizar con Fac. Ven.',
        help='Autorizar si el cliente esta bloqueado por facturas vencidas.',
        default=False
    )

    @api.onchange('account_voucher_ids')
    def check_account_voucher_ids(self):
        for record in self:
            if record.account_voucher_ids:
                ids_voucher = record.account_voucher_ids.ids
                sales = self.env['sale.order'].search([])
                ids_advances = [x.id for x in sales.account_voucher_ids]
                for id_voucher in ids_voucher:
                    for id_advance in ids_advances:
                        if id_advance == id_voucher:
                            raise ValidationError(
                                _('This Advance is already related in another order'))

    @api.onchange('advance_payment_manually')
    def clean_account_voucher_ids(self):
        for record in self:
            if record.advance_payment_manually:
                record.account_voucher_ids = False
    
    @api.onchange('payment_term_id')
    def compute_immediate_payment(self):
        for record in self:
            if record.payment_term_id.immediate_payment is True:
                record.check_immediate_payment = True
            else:
                record.check_immediate_payment = False
                record.account_voucher_ids = False

    @api.model
    def create(self, values): 
        values['account_voucher_ids'] = False 
        values['advance_payment_manually'] = False 
        res = super(SaleOrder, self).create(values)
        return res

    def action_confirm(self):
        for record in self:
            now = datetime.now() - timedelta(hours=5)
            now = now.date()
            if record.partner_id.block_expired_invoice and \
                    record.company_id.block_expired_invoice and \
                        not record.unlock_for_overdue_invoices:
                invoices = self.env['account.move'].search(
                    [('partner_id', '=', record.partner_id.id),
                     ('invoice_date_due', '<=', now),
                     ('state', '=', 'posted'),
                     ('payment_state', '!=', 'paid'),
                     ('move_type', '=', 'out_invoice')]
                )
                if len(invoices) >= 1:
                    raise ValidationError(
                        _('El cliente tiene las siguientes facturas vencidas: \n' \
                          '%s',
                          '\n'.join(['* %s (%s)' % (x.name, x.invoice_date_due) for x in invoices])))
                
            if record.company_id.block_credit_limit or \
                record.company_id.active_payment_advance:
                partner_id = record.partner_id
                partner_credit = partner_id.credit
                quota_limit_initial = record.partner_id.quota_limit_initial
            
                orders_client = self.env['sale.order'].search(
                    [('partner_id', '=', record.partner_id.id), 
                    ('state', 'in', ['sale','done']),
                    ('invoice_status','=','to invoice')]
                )
                sum_orders_total = sum([x.amount_total for x in orders_client])
                credit_limit = quota_limit_initial - (
                    partner_credit + sum_orders_total
                )
                # record.partner_id.credit_limit = credit_limit

                if record.partner_id.block_credit_limit and \
                        record.company_id.block_credit_limit and \
                            record.payment_term_id.immediate_payment == False and \
                                not record.unlock_for_credit_limit:
                    if credit_limit < record.amount_total:
                        raise ValidationError(
                            _('El cliente excede la cuota límite. \n\n' \
                              'Límite de crédito: %(lc)s\n' \
                              'Valor orden: %(vt)s',
                              lc='${:,.2f}'.format(credit_limit).replace(',','@').replace('.',',').replace('@','.'), 
                              vt='${:,.2f}'.format(record.amount_total).replace(',','@').replace('.',',').replace('@','.')))

                if record.company_id.active_payment_advance:
                    if not record.advance_payment_manually:
                        if record.payment_term_id.immediate_payment:
                            if not record.account_voucher_ids:
                                raise ValidationError(
                                    _('Una cuenta anticipo mínimo debe estar relacionada con el pedido.'))
                            else:
                                accounts_noval = []
                                accounts_name = ''
                                for account in record.account_voucher_ids:
                                    if account.state != 'posted':
                                        accounts_name += account.name+' \n'
                                        accounts_noval.append(account)
                                
                                if accounts_noval:
                                    raise ValidationError(
                                        _('Las cuentas: \n %s \n no están publicadas.',
                                          accounts_name))
                                
                                sum_account_advance = sum([x.amount for x in record.account_voucher_ids])
                                if record.amount_total > sum_account_advance:
                                    raise ValidationError(
                                        _('Los anticipos acumulados no superan el total del pedido.'))
    
        res = super(SaleOrder, self).action_confirm()
        return res
