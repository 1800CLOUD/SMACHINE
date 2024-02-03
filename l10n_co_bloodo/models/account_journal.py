# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_einvoicing = fields.Boolean(
        'e-Invoicing',
        help='Enables the option to configure the DIAN'
        ' resolution for electronic invoicing'
    )
    edi_code = fields.Char(
        'Short code',
        size=5,
        help='It is used to create the prefix of the sequences'
    )
    resolution_text = fields.Text(
        'Resolution Information',
        help='Informative text about the resolution of electronic'
        ' invoicing that will appear in the graphic representation.'
    )
    note_ei = fields.Text('Notes in e-invoice',
                          help='The text will show in the format '
                          'electonic invoice')
    debit_note_sequence = fields.Boolean(
        'Dedicated debit note sequence',
        help='Check this box if you do not want to share the same sequence'
        ' for invoices and electronic debit notes made from this journal.',
        default=False
    )
    debit_note_sequence_id = fields.Many2one(
        'ir.sequence',
        'Debit note sequence',
        help='This field contains the information related to the numbering'
        ' of the electronic debit notes of this journal.',
        copy=False
    )
    debit_note_sequence_number_next = fields.Integer(
        'Next number of debit note',
        help='The next sequence number will be used for the next debit note.',
        compute='_compute_debit_seq_number_next',
        inverse='_inverse_debit_seq_number_next'
    )

    remaining_numbers = fields.Integer(
        'Remaining numbers',
        default=False
    )
    remaining_days = fields.Integer(
        'Remaining days',
        default=False
    )
    edi_technical_key = fields.Char(
        'Technical key'
    )

    @api.depends(
        'debit_note_sequence_id.use_date_range',
        'debit_note_sequence_id.number_next_actual'
    )
    def _compute_debit_seq_number_next(self):
        '''
            Compute 'sequence_number_next' according to the
            current sequence in use, an ir.sequence or an
            ir.sequence.date_range.
        '''
        for journal in self:
            if journal.debit_note_sequence_id and journal.debit_note_sequence:
                sequence = \
                    journal.debit_note_sequence_id._get_current_sequence()
                journal.debit_note_sequence_number_next = \
                    sequence.number_next_actual
            else:
                journal.debit_note_sequence_number_next = 1

    def _inverse_debit_seq_number_next(self):
        '''
            Inverse 'debit_note_sequence_number_next'
            to edit the current sequence next number.
        '''
        for journal in self:
            if journal.debit_note_sequence_id and \
                    journal.debit_note_sequence and \
                    journal.debit_note_sequence_number_next:
                sequence = \
                    journal.debit_note_sequence_id._get_current_sequence()
                sequence.sudo().number_next = \
                    journal.debit_note_sequence_number_next

    def write(self, vals):
        for journal in self:
            if ('code' in vals and journal.edi_code != vals['code']):
                if self.env['account.move'].search(
                        [('journal_id', 'in', self.ids)], limit=1):
                    raise UserError(_(
                        'This journal already contains items, '
                        'therefore you cannot modify its short name.'
                    ))
                if journal.debit_note_sequence_id:
                    new_prefix = self._get_sequence_prefix(
                        vals['code'], refund=False, type_note='debit')
                    journal.debit_note_sequence_id.write(
                        {'prefix': new_prefix})
            if vals.get('debit_note_sequence'):
                for journal in self.filtered(
                        lambda j: j.type in (
                            'sale',
                            'purchasex'
                        ) and not j.debit_note_sequence_id):
                    journal_vals = {
                        'name': journal.name,
                        'company_id': journal.company_id.id,
                        'code': journal.code,
                        'debit_note_sequence_number_next': vals.get(
                            'debit_note_sequence_number_next',
                            journal.debit_note_sequence_number_next
                        ),
                    }
                    journal.debit_note_sequence_id = \
                        self.sudo()._create_sequence(
                            journal_vals, type_note='debit').id
        result = super(AccountJournal, self).write(vals)
        return result

    @api.model
    def create(self, vals):
        if vals.get('type') in ('sale', 'purchasex') and \
                vals.get('debit_note_sequence') and \
                not vals.get('debit_note_sequence_id'):
            vals.update({'debit_note_sequence_id': self.sudo(
            )._create_sequence(vals, type_note='debit').id})
        journal = super(AccountJournal, self).create(vals)
        return journal

    @api.model
    def _get_sequence_prefix(self, code, refund=False, type_note=False):
        prefix = code.upper()
        if type_note == 'credit' or refund:
            prefix = 'C' + prefix
        if type_note == 'debit':
            prefix = 'D' + prefix
        return prefix  # + '/%(range_year)s/'

    @api.model
    def _create_sequence(self, vals, refund=False, type_note=False):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_sequence_prefix(vals['code'], refund, type_note)
        seq_name = (refund or type_note == 'credit') and \
            prefix + _(': Credit Note Sequence') or \
            type_note == 'debit' and \
            prefix + _(': Debit Note Sequence') or \
            vals['code']
        seq = {
            'name': '%s' % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = (refund or type_note == 'credit') and \
            vals.get('refund_sequence_number_next', 1) or \
            type_note == 'debit' and \
            vals.get('debit_note_sequence_number_next', 1) or \
            vals.get('sequence_number_next', 1)
        return seq

    def create_journal_sequence(self):
        if not self.sequence_id:
            seq = self.create_sequence(refund=False, type_note='')
            self.sequence_id = seq.id
        if self.refund_sequence and not self.refund_sequence_id:
            seq = self.create_sequence(refund=True, type_note='credit')
            self.refund_sequence_id = seq.id
        if self.debit_note_sequence and not self.debit_note_sequence_id:
            seq = self.create_sequence(refund=False, type_note='debit')
            self.debit_note_sequence_id = seq.id

    def create_sequence(self, refund=False, type_note=''):
        prefix = self._get_sequence_prefix(self.code, refund, type_note)
        seq_name = (refund or type_note == 'credit') and \
            self.code + _(': Secuencia Rectificativa') or \
            type_note == 'debit' and \
            self.code + _(': Secuencia Nota Débito') or \
            self.code
        seq = {
            'name': '%s' % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if self.company_id:
            seq['company_id'] = self.company_id.id
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = (refund or type_note == 'credit') and \
            (self.refund_sequence_number_next or 1) or \
            type_note == 'debit' and \
            (self.debit_note_sequence_number_next or 1) or \
            (self.sequence_number_next or 1)
        return seq
