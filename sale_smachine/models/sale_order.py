
from cgitb import reset
from odoo import _, fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_duplicate = fields.Boolean()
    confirm_order_duplicate = fields.Boolean()

    def confirm_duplicate(self):
        for record in self:
            if record.order_duplicate and record.state == 'draft':
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
                        sale.action_confirm()
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
    def duplicate_sale(self):
        for record in self:
            companies = self.env['res.company'].search([])
            companies_warehouse_names = []
            companies_fiscal_names = []
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
                        #if fiscal_position:
                        #    fiscal_position = fiscal_position.id
                    #else:
                    #    fiscal_position = False

                    record.copy(
                        {
                            'name': record.name,
                            'company_id': company.id,
                            'warehouse_id':warehouse.id,
                            #'fiscal_position_id': False
                        }
                            )
                    record.order_duplicate = True
    """
    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        companies = self.env['res.company'].search([])
        companies_warehouse_names = []
        companies_fiscal_names = []
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
                                'code','=',res.warehouse_id.code
                            )
                        ]
                        )
                if not warehouse:
                    companies_warehouse_names.append(company.name)
                    
                    continue
                
                if res.fiscal_position_id:
                    fiscal_position = self.env['account.fiscal.position']\
                        .sudo().search(
                            [
                                (
                                    'company_id','=',company.id
                                ),
                                (
                                    'code','=',res.fiscal_position_id.code
                                )
                            ]
                            )
                    #if fiscal_position:
                    #    fiscal_position = fiscal_position.id
                #else:
                #    fiscal_position = False

                res.copy(
                    {
                        'name': res.name,
                        'company_id': company.id,
                        'warehouse_id':warehouse.id,
                        #'fiscal_position_id': False
                    }
                        )

        return res
    """