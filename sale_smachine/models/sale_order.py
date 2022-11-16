
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_duplicate = fields.Boolean()
    confirm_order_duplicate = fields.Boolean()

    def action_confirm(self):
        for record in self:
            record.validation_product_kit()
            record.confirm_order_duplicate = True
        res = super(SaleOrder, self).action_confirm()
        return res
    
    def confirm_duplicate(self):
        for record in self:
            if record.order_duplicate:
                sales = self.env['sale.order']\
                            .sudo().search(
                                [
                                    (
                                        'name','=',record.name
                                    )
                                ]
                                )
                if sales:
                    for sale in sales:
                        if sale.state not in ['done','cancel']:
                            sale.action_confirm()
                            sale.confirm_order_duplicate = False
                
                record.confirm_order_duplicate = False

                """
                companies = self.env['res.company'].search([])
                for company in companies:
                    if self.env.company.id == company.id:
                        continue
                    else:
                        sales = self.env['sale.order']\
                            .sudo().search(
                                [
                                    (
                                        'name','=',record.name,
                                        'company_id','=',company.id,
                                    )
                                ]
                                )
                        if sales:
                            for sale in sales:
                                sale.action_confirm()
                        else:
                            continue
                """
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
    
    def duplicate_sale(self):
        for record in self:
            companies = self.env['res.company'].search([])
            companies_warehouse_names = []
            fiscal_position = False
            payment_mode_id = False
            for company in companies:
                if self.env.company.id == company.id:
                    continue
                else:
                    warehouse = self.env['stock.warehouse']\
                        .sudo().search(
                            [
                                (
                                    'company_id','=',company.id
                                ),
                                (
                                    'code','=',record.warehouse_id.code
                                )
                            ]
                            )
                    if not warehouse:
                        companies_warehouse_names.append(company.name)
                        
                        continue
                    
                    if record.fiscal_position_id:
                        fiscal_position = self.env['account.fiscal.position']\
                            .sudo().search(
                                [
                                    (
                                        'company_id','=',company.id
                                    ),
                                    (
                                        'code','=',record.fiscal_position_id.code
                                    )
                                ]
                                )
                        if fiscal_position:
                            fiscal_position = fiscal_position.id

                    if record.payment_mode_id:
                        payment_mode_id = self.env['account.payment.mode']\
                            .sudo().search(
                                [
                                    (
                                        'company_id','=',company.id
                                    ),
                                    (
                                        'code','=',record.payment_mode_id.code
                                    )
                                ]
                                )
                        if payment_mode_id:
                            payment_mode_id = payment_mode_id.id

                    record.copy(
                        {
                            'name': record.name,
                            'company_id': company.id,
                            'warehouse_id':warehouse.id,
                            'fiscal_position_id': fiscal_position,
                            'payment_mode_id': payment_mode_id
                        }
                            )
                    record.order_duplicate = True