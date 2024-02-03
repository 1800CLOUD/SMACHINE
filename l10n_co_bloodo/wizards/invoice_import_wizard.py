# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class IvoiceImportWizard(models.TransientModel):
    _name = 'invoice.import.wizard'
    _description = 'Invoice import wizard'

    move_id = fields.Many2one('account.move', 'Invoice')
    doc_file_id = fields.Binary('Supplier invoice file')
    doc_fname = fields.Char('Name file')
    msg = fields.Text('Message')
    btn_create = fields.Boolean('Btn create')
    partner_data = fields.Text('Dict partner')
