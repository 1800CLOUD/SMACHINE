# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    analytic_account_id = fields.Many2one(
        related='group_id.analytic_account_id',
        store=True,
        readonly=False,
        # domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    owner_required = fields.Boolean('Requiere propietario',
                                    related='picking_type_id.owner_required')

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.company_id.note_sale_to_picking and res.origin:
            sale_id = self.env['sale.order'].search(
                [('name', '=', res.origin)],
                limit=1
            )
            if sale_id:
                res.note = res.note and '%s\n%s' % (
                    res.note, sale_id.note or '') or \
                    sale_id.note
        return res
