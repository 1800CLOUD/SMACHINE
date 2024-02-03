# -*- coding: utf-8 -*-

from odoo import fields, models, _


class StockLocationDateReport(models.Model):
    _name = 'stock.location.date.report'
    _description = 'Reporte de inventario a la fecha'

    product_id = fields.Many2one('product.product',
                                 'Producto')
    location_id = fields.Many2one('stock.location',
                                  'Ubicación')
    lot_id = fields.Many2one('stock.production.lot',
                             'Lote/N° de Serie')
    owner_id = fields.Many2one('res.partner',
                               'Propietario')
    qty = fields.Float('Cantidad')
    user_id = fields.Many2one('res.users',
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company',
                                 'Compañía')
    date = fields.Date('Fecha')
    product_uom_id = fields.Many2one('uom.uom',
                                     'UdM')