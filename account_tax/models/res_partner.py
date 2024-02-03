
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    classification_id = fields.Many2one(
        comodel_name='res.partner.classification',
        string='ISIC Main'
    )

    classifications_ids = fields.Many2many(
        comodel_name='res.partner.classification',
        string='ISIC Minor'
    )


class ResPartnerClassification(models.Model):
    _name = 'res.partner.classification'
    _description = 'ISIC'
    _order = 'code'
    _rec_name = 'code'

    _sql_constraints = [
        ('unique_code', 'unique(company_id, code)',
         'The code must be unique per company!')
    ]

    def _default_company_id(self):
        return self.env.company

    classification_ids = fields.One2many(
        comodel_name='res.city.classification',
        inverse_name='classification_id',
        string='Retention rates'
    )

    code = fields.Char(
        string='Code',
        required=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=_default_company_id,
    )

    name = fields.Char(
        string='Name',
        required=True
    )
