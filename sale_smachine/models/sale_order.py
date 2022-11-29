
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sm_transaction_number = fields.Char('Transaction number')

    def action_confirm(self):
        for record in self:
            record.validation_product_kit()
        res = super(SaleOrder, self).action_confirm()
        return res

    def validation_date_expiration(self, mrp_bom_kits):
        for record in self:
            datetime_now = datetime.now()
            for kit in mrp_bom_kits:
                if kit.date_expiration <= datetime_now:
                    raise UserError(_(
                        'El producto '+ kit.product_tmpl_id.name +' ya expiró'
                    ))
    def validation_quantity_mrp_bom(self, mrp_bom_kits):
        for record in self:
            for line in record.order_line:
                for kit in mrp_bom_kits: 
                    if line.product_template_id.id == kit.product_tmpl_id.id:
                        if line.product_uom_qty > kit.quantity_available:
                            raise UserError(_(
                                'El producto '+ kit.product_tmpl_id.name +' supera la cantidad establecidad en el kit'
                            ))
                        
                        kit.quantity_available = kit.quantity_available - line.product_uom_qty
    
    def validation_product_kit(self):
        for record in self:
            if record.order_line:
                mrp_bom_ids = []
                for line in record.order_line:
                    for bom_ids  in line.product_id.bom_ids:
                        for bom_id in bom_ids:
                            mrp_bom_ids.append(bom_id)
                
                mrp_bom_kits = list(
                    filter(lambda x: x.type == 'phantom', mrp_bom_ids)
                    )
                
                record.validation_date_expiration(mrp_bom_kits)
                record.validation_quantity_mrp_bom(mrp_bom_kits)