# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    negative_inventory = fields.Boolean(
        related='company_id.negative_inventory',
        readonly=False
    )

    note_sale_to_picking = fields.Boolean(
        related='company_id.note_sale_to_picking',
        readonly=False
    )

    picking_analytic = fields.Boolean(
        related='company_id.picking_analytic',
        readonly=False
    )
    counting_sheet_without_columns = fields.Boolean(
        related='company_id.counting_sheet_without_columns',
        readonly=False
    )
