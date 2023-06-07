# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
import datetime
import xlsxwriter
from io import BytesIO
import io


class ReportInvoice(models.TransientModel):
    _name = "report.pos"
    _description = 'Reporte de productos facturados en POS'


    name = fields.Char('Nombre', default='Informe de Facturados', readonly=True)
    date_from = fields.Date('Desde', required=True, default=(fields.Date.today() - relativedelta(month=1)))
    date_to = fields.Date('Hasta', required=True, default=(fields.Date.today()))
    partner_ids = fields.Many2many('res.partner', string='Clientes') 
    xls_file = fields.Binary(string="XLS file")
    xls_filename = fields.Char()
    


    def compute_report(self):
        def _add_where(table, fld, vl):
            return f" AND {table}.{fld} IN ({','.join(str(x.id) for x in vl)})"
        
        cr = self._cr
        wh = ''
        uid = self.env.user.id
        dt_now = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt_from = str(self.date_from)
        dt_to = str(self.date_to)
        if self.partner_ids:
            wh += _add_where('po', 'partner_id', self.partner_ids)


            
        #add_fields_insert, add_fields_select, add_fields_from = self.extended_compute_fields()
            
        cr.execute(f'DELETE FROM pos_report_line')
            
        qry = f'''
            INSERT INTO pos_report_line (date_order, order_id, session_id, product_id, default_code, categ_id, product_uom_id, 
                quantity, price_subtotal,partner_vat, partner_id, employee_id, create_date, write_date)
                SELECT
            
                    DATE(po.date_order), 
                    pol.order_id,
                    po.session_id,
                    pol.product_id,
                    pt.default_code,
                    pt.categ_id,
                    pt.uom_id,
                    pol.qty,
                    pol.price_subtotal,
                    rp.vat,
                    po.partner_id,
                    po.employee_id,
                    '{dt_now}', 
                    '{dt_now}'

                FROM pos_order_line pol
                    LEFT JOIN pos_order po ON pol.order_id = po.id
                    LEFT JOIN product_product pp ON pol.product_id = pp.id
                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id                        
                    LEFT JOIN res_partner rp ON po.partner_id = rp.id
                                         

                 WHERE
                
                    po.state = 'done' AND
                    DATE(po.date_order) BETWEEN   '{dt_from}' AND '{dt_to}' {wh}
                        
                GROUP BY
                    po.date_order,
                    pol.order_id,
                    po.session_id,
                    pol.product_id,
                    pt.default_code,
                    pt.categ_id,
                    pt.uom_id,
                    pol.qty,
                    pol.price_subtotal,
                    rp.vat,
                    po.partner_id,
                    po.employee_id
        '''
        cr.execute(qry)

    def analysis(self):
        self.compute_report()
        view_id = self.env['ir.ui.view'].search([('name','=','report_invoice.view_pos_report_line_pivot')])
        dt_from = str(self.date_from)
        dt_to = str(self.date_to)
        return {
                'name': 'Análisis de Facturados',
                'view_type': 'form',
                'view_mode': 'pivot',
                'view_id': view_id.id, 
                'res_model': 'pos.report.line',
                'type': 'ir.actions.act_window'
            }
    
    def _compute_excel(self):
        def _add_wh(fld, tbl):
            return " AND {} IN ({})".format(fld, ','.join(str(x.id) for x in tbl))
    
        #APLICAR FILTROS
        wh = '' 
        if self.partner_ids:
            wh = _add_wh('po.partner_id', self.partner_ids)
        cr = self.env.cr
        dt_from = str(self.date_from)
        dt_to = str(self.date_to)
        cr.execute(f'''SELECT
                            DATE(po.date_order), 
                            po.name,
                            ps.name,
                            pt.default_code,
                            pt.name,
                            pc.name,
                            pb.name,
                            uu.name,
                            pol.qty,
                            pol.price_subtotal,
                            rp.vat,
                            rp.name,
                            rp2.name

                        FROM pos_order_line pol
                            LEFT JOIN pos_order po ON pol.order_id = po.id
                            LEFT JOIN pos_session ps ON po.session_id = ps.id 
                            LEFT JOIN product_product pp ON pol.product_id = pp.id
                            LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                            LEFT JOIN product_category pc ON pt.categ_id = pc.id
                            LEFT JOIN uom_uom uu ON pt.uom_id = uu.id                          
                            LEFT JOIN res_partner rp ON po.partner_id = rp.id
                            LEFT JOIN hr_employee he ON po.employee_id = he.id
                            LEFT JOIN res_partner rp2 ON he.partner_id = rp2.id
                            LEFT JOIN product_brand pb ON pt.product_brand_id = pb.id
                             

                        WHERE
    
                            po.state = 'done' AND
                            DATE(po.date_order) BETWEEN   '{dt_from}' AND '{dt_to}' {wh}
                        
                        GROUP BY
                        po.date_order,
                        po.name,
                        pt.default_code,
                        ps.name,
                        pt.name,
                        pc.name,
                        pb.name,
                        uu.name,
                        rp.vat,
                        rp.name,
                        rp2.name,
                        pol.qty,
                        pol.price_subtotal,
                        pol.id
                        
                    
                      ''')
        result = cr.fetchall()
        return result
        
    def get_xlsx_report(self):
        result = self._compute_excel()
        output = io.BytesIO()
        titles = [
                'Fecha', 
                'Orden de venta', 
                'Sesion', 
                'Referencia Interna',
                'Producto',
                'Categoria',
                'Marca',
                'Unidad de medida', 
                'Cantidad', 
                'Valor', 
                'Nit', 
                'Cliente',
                'Cajero'
                ]
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        worksheet = workbook.add_worksheet()

        # Formants
        titles_format = workbook.add_format()
        titles_format.set_align("center")
        titles_format.set_bold()
        worksheet.set_column("A:Q", 22)
        worksheet.set_row(0, 25)
        
        col_num = 0
        for title in titles:
            worksheet.write(0, col_num, title, titles_format)
            col_num += 1
        
        for index, data in enumerate(result):
            row = index + 1
            col_num = 0
            for d in data:
                if isinstance(d, datetime.date):
                    d = d.strftime("%Y-%m-%d")
                worksheet.write(row, col_num, d)
                col_num += 1
        
        workbook.close()
        xlsx_data = output.getvalue()

        self.xls_file = base64.encodebytes(xlsx_data)
        self.xls_filename = "report_invoice_pos.xlsx"


class InvoiceReportLine(models.TransientModel):
    _name = "pos.report.line"
    _description = "Lineas de reporte de Facturados POS"
    

    # ==== Invoice fields ====
    order_id = fields.Many2one('pos.order', string='Orden POS', readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='cliente', readonly=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string='Cajero', readonly=True, copy=False)
    date_order = fields.Date(readonly=True, string="Fecha de orden", copy=False)

    # ==== Invoice line fields ====
    quantity = fields.Float(string='Cantidad Facturada', readonly=True, index=True, copy=False)
    product_id = fields.Many2one('product.product', string='Producto', readonly=True, required=True, copy=False, index=True)
    product_uom_id = fields.Many2one('uom.uom', string='Unidad de Medida', readonly=True)
    categ_id = fields.Many2one('product.category', string='Categoria Producto', readonly=True)
    price_subtotal = fields.Float(string='V. antes Impuesto', readonly=True, required=True, index=True, copy=False )
    partner_vat = fields.Char('NIT', readonly=True, index=True, copy=False)
    default_code = fields.Char('Referencia interna', copy=False, readonly=True, index=True)
    session_id = fields.Many2one('pos.session', string="Sesion", readonly=True, copy=False)
    product_brand_id = fields.Many2one(comodel_name="product.brand", string="Marca", copy=False, readonly=True, index=True)

    

