
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    taxes_id = fields.Many2many(
        compute='_compute_taxes_id',
        inverse='_inverse_taxes_id',
        store=True
    )
    supplier_taxes_id = fields.Many2many(
        compute='_compute_taxes_id',
        inverse='_inverse_taxes_id',
        store=True
    )

    @api.depends('categ_id.taxes_categ_id', 'categ_id.supplier_taxes_categ_id')
    def _compute_taxes_id(self):
        for template in self:
            template.taxes_id = template.categ_id.taxes_categ_id
            template.supplier_taxes_id = template.categ_id.supplier_taxes_categ_id

    def _inverse_taxes_id(self):
        for template in self:
            template.inverse_taxes_id()

    def inverse_taxes_id(self):
        self.ensure_one()
        # TO DO create a wizard o note
        return True
