# -*- coding: utf-8 -*-

from odoo import api, http, fields, models, _

TYPE_DS = {
    'in_invoice': '05',
    'in_refund': '95'
}


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_type_document_ds(self):
        '''
            Return: 'invoice' or 'credit' from the type purchase document
        '''
        self.ensure_one()
        if self.move_type == 'in_invoice':
            return 'invoice'
        elif self.move_type == 'in_refund':
            return 'credit'
        else:
            return False
