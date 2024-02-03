# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    imports_ids = fields.Many2many(
        comodel_name='purchase.import',
        relation='account_move_purchase_import_rel',
        column1='account_move_id',
        column2='purchase_import_id',
        copy=False,
    )
    import_id = fields.Many2one(
        comodel_name='purchase.import',
        compute='_compute_import_id',
        inverse='_inverse_import_id'
    )
    import_type = fields.Selection(
        selection=[
            ('insurance', 'Insurance'),
            ('freight', 'Freight'),
            ('expense', 'Expense'),
        ],
        copy=False,
    )

    @api.depends('imports_ids')
    def _compute_import_id(self):
        for move in self:
            move.import_id = move.imports_ids and move.imports_ids[0] or False

    def _inverse_import_id(self):
        for move in self:
            if not move.import_id:
                continue
            move.imports_ids = move.import_id
