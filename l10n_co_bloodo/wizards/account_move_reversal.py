# -*- coding: utf-8 -*-

from odoo import api, models, fields


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    fe_correction_id = fields.Many2one('dian.discrepancy.response',
                                       'Correction concept')
    ds_correction_id = fields.Many2one('dian.discrepancy.response',
                                       'SD Correction concept')
    is_edoc = fields.Boolean('e-Document', default=False)

    def reverse_moves(self):
        action = super(AccountMoveReversal, self).reverse_moves()
        move_type = self.move_type
        for refund in self.new_move_ids:
            refund.fe_correction_id = (move_type == 'out_invoice' and
                                       self.fe_correction_id and
                                       self.fe_correction_id.id) or \
                (move_type == 'in_invoice' and
                 self.ds_correction_id and
                 self.ds_correction_id.id) or \
                False
            refund.type_note = 'credit'
            # refund._onchange_type()
        return action
