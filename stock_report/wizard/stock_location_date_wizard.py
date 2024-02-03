# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class StockLocationDateWizard(models.TransientModel):
    _name = 'stock.location.date.wizard'
    _description = 'Wizard reporte inventario por fecha'

    date = fields.Date('Fecha',
                       default=fields.Date.context_today)
    company_id = fields.Many2one('res.company',
                                 'Compañía',
                                 default=lambda self: self.env.company)

    def generate_report(self):
        self.ensure_one()
        location_obj = self.env['stock.location']
        loc_report_obj = self.env['stock.location.date.report']
        date = self.date
        user_id = self.env.user
        report_data = []
        for loc in location_obj.search([]):
            query = '''
                SELECT 
                    '{date}' as date,
                    product_id,
                    {loc} as location_id,
                    lot_id,
                    owner_id,
                    SUM(CASE WHEN location_id = {loc} THEN qty_done*-1 
                             WHEN location_dest_id = {loc} THEN qty_done 
                             END) as qty,
                    product_uom_id,
                    {com} as company_id,
                    {user} as user_id
                FROM stock_move_line
                WHERE state = 'done'
                AND (location_id = {loc} OR 
                     location_dest_id = {loc})
                AND date <= '{date}'
                GROUP BY product_id, owner_id, lot_id, product_uom_id
                ORDER BY product_id, owner_id, lot_id, product_uom_id
            '''.format(loc=loc.id,
                       date=date.strftime('%Y-%m-%d 23:59:59'),
                       com=self.company_id.id,
                       user=user_id.id)
            self._cr.execute(query)
            report_by_loc = self._cr.dictfetchall()
            if report_by_loc:
                report_data += report_by_loc
            else:
                print(loc.complete_name)
        records_rep = loc_report_obj
        # DELETE
        query_rm = '''
            DELETE FROM stock_location_date_report
            WHERE user_id = {}
        '''.format(user_id.id)
        self._cr.execute(query_rm)
        # CREATE
        if report_data:
            query_cr = '''
                INSERT INTO stock_location_date_report
                (date, product_id, location_id, lot_id, owner_id, qty,
                product_uom_id, company_id, user_id)
                VALUES {}
            '''.format(', '.join(
                    [str(tuple(data.values())).replace('None', 'null') 
                     for data in report_data]))
            self._cr.execute(query_cr)
        # for data in report_data:
        #     record_rep_id = loc_report_obj.create(data)
        #     records_rep |= record_rep_id
        action = self.env.ref('stock_report.stock_location_date_report_action').read()[0]
        del action['display_name']
        action['name'] = _('Inventario del %s', self.date.strftime('%Y/%m/%d'))
        action['target'] = 'main'
        return action