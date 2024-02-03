# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    negative_inventory = fields.Boolean(
        string='Negative Inventory',
        help='Allow negative inventory.',
        default=False,
    )

    note_sale_to_picking = fields.Boolean(
        string='Sales order note in the delivery order',
        help='Allows you to keep the sales order note to the delivery order note.'
    )

    picking_analytic = fields.Boolean(
        string='Transfer Analytic',
        help='Create analytical lines on the transfer.',
        default=True,
    )
    counting_sheet_without_columns = fields.Boolean(
        string='Remove columns from the tally sheet',
        help='Remove "quantity on hand and available" columns from tally sheet.',
        default=False
    )
