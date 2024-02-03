# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    name = fields.Char('Number',
                       required=True,
                       readonly=False,
                       copy=False,
                       default='/')

    @api.depends('posted_before', 'state', 'journal_id', 'date')
    def _compute_name(self):
        self.filtered(lambda m: not m.name).name = '/'

    def _get_sequence(self):
        '''
            Return the sequence to be used during the post of the current move.
            :return: An ir.sequence record or False.
        '''
        self.ensure_one()

        journal = self.journal_id
        if self.move_type in ('entry', 'out_invoice',
                              'in_invoice', 'out_receipt', 'in_receipt') or \
                not journal.refund_sequence:
            return journal.sequence_id
        if not journal.refund_sequence_id:
            return
        return journal.refund_sequence_id

    def _post(self, soft=True):
        if soft:
            future_moves = self.filtered(
                lambda move: move.date > fields.Date.context_today(self))
            to_post = self - future_moves
        else:
            to_post = self

        for move in to_post:
            if not move.name or move.name == '/':
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_(
                        'Please define a sequence on your journal.'
                    ))

                # Consume a new number.
                # to_post['name']
                move.name = sequence.with_context(
                    ir_sequence_date=move.date).next_by_id()

        return super(AccountMove, self)._post(soft)
