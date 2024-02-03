
from odoo import models, fields


class ResCity(models.Model):
    _inherit = 'res.city'

    base_value = fields.Float(
        string='Base value',
        digits='Account',
        help='Retention base for ICT.',
    )

    classification_ids = fields.One2many(
        comodel_name='res.city.classification',
        inverse_name='city_id',
        string='Retention rates'
    )


class ResPartnerClassification(models.Model):
    _name = 'res.city.classification'
    _description = 'ISIC Rate'

    _sql_constraints = [
        ('unique_city_classification', 'unique(city_id,classification_id)',
         'The ISIC must be unique per city!')
    ]

    city_id = fields.Many2one(
        comodel_name='res.city',
        required=True,
        ondelete='cascade'
    )

    classification_id = fields.Many2one(
        comodel_name='res.partner.classification',
        string='ISIC',
        required=True,
        ondelete='cascade'
    )

    tax_id = fields.Many2one(
        comodel_name='account.tax',
        required=True,
        ondelete='cascade'
    )
