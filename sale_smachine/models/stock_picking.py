# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    destination_city_id = fields.Many2one('res.city', 'Ciudad destino', related='sale_id.city_id')
    source_id = fields.Many2one('utm.source', 'Canal de venta')
    guide_number = fields.Char('Guide number')
    team_sale_id = fields.Many2one('crm.team', 'Equipo de Ventas', related='sale_id.team_id', store=True)

    @api.model
    def create(self, vals):
        res = super(StockPicking, self).create(vals)
        if res.origin:
            sale_id = self.env['sale.order'].search(
                [('name', '=', res.origin)],
                limit=1
            )
            if sale_id:
                res.write({
                    'destination_city_id': sale_id.destination_city_id and
                    sale_id.destination_city_id.id,
                    'source_id': sale_id.source_id and sale_id.source_id.id
                })
        return res
