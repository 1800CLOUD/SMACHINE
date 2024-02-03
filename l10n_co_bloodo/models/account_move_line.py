# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _get_product_standard_code(self):
        """
            For identifying products, different standards can be used.
            If there is a barcode, we take that one, because normally in the
            GTIN standard it will be the most specific one.'
            Otherwise, we will check the
            :return: (standard, product_code)
        """
        self.ensure_one()
        code = []
        if self.product_id:
            if self.move_id.fe_type == '02':
                if not self.product_id.dian_customs_code:
                    raise UserError(_(
                        'Export invoices require a customs code on'
                        ' all products, complete this information'
                        ' before validating the invoice.'
                    ))
                code = [
                    self.product_id.dian_customs_code,
                    '020',
                    '195',
                    'Partida Arancelarias'
                ]
            if self.product_id.barcode:
                code = [self.product_id.barcode, '010', '9', 'GTIN']
            elif self.product_id.unspsc_code_id:
                code = [self.product_id.unspsc_code_id.code, '001',
                        '10', 'UNSPSC']
            elif self.product_id.default_code:
                code = [self.product_id.default_code, '999',
                        '', 'Estándar de adopción del contribuyente']
        if not code:
            code = ['NA', '999',
                    '', 'Estándar de adopción del contribuyente']
        return {'ID': code[0],
                'schemeID': code[1],
                'schemeAgencyID': code[2],
                'schemeName': code[3]}

