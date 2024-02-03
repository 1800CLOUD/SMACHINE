# -*- coding: utf-8 -*-

from odoo import fields, models, _


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    owner_required = fields.Boolean('Requiere propietario',
                                    default=False)