# -*- coding: utf-8 -*-

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(StockPicking, self).button_validate()

        if res is True and self.env.context.get('purchase_import_id'):
            Purchase = self.env['purchase.import']
            purchase_import_id = self.env.context.get('purchase_import_id')
            purchase_import = Purchase.browse(purchase_import_id)
            purchase_import.action_done()

        return res
