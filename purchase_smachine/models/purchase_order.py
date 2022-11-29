
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_duplicate = fields.Boolean()
    confirm_purchase_duplicate = fields.Boolean()

    def button_confirm(self):
        for record in self:
            record.confirm_purchase_duplicate = True
        res = super(PurchaseOrder, self).button_confirm()
        return res
    
    
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
    
    def confirm_duplicate(self):
        for record in self:
            if record.purchase_duplicate:
                purcharses = self.env['purchase.order']\
                            .sudo().search(
                                [
                                    (
                                        'name','=',record.name
                                    )
                                ]
                                )
                if purcharses:
                    for purcharse in purcharses:
                        if purcharse.state not in ['purchase','cancel']:
                            purcharse.button_confirm()
                            purcharse.confirm_purchase_duplicate = False
                
                record.confirm_purchase_duplicate = False

    def duplicate_purchase(self):
        for record in self:
            companies = self.env['res.company'].search([])
            companies_warehouse_names = []
            fiscal_position = False
            payment_mode_id = False
        for company in companies:
            stock_picking_type_names = []
            if self.env.company.id == company.id:
                    continue
            else:
                picking_type = self.env['stock.picking.type']\
                    .sudo().search(
                        [
                            (
                                'company_id','=',company.id
                            ),
                            (
                                'sequence_code','=',record.picking_type_id.sequence_code
                            )
                        ],
                        limit=1
                        )
                if not picking_type:
                    stock_picking_type_names.append(company.name)
                    continue
            
            record.copy(
                        {
                            'name': record.name,
                            'company_id': company.id,
                            'picking_type_id': picking_type.id
                        }
                            )
        
        record.purchase_duplicate = True