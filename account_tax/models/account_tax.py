
from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    base_city = fields.Boolean(
        string='Base by city?',
        default=False
    )
    base_minimum = fields.Boolean(
        string='Minimum base?',
        default=False
    )
    base_type = fields.Boolean(
        string='Group by city?',
        default=False,
        help='The tax is replaced according to the city.'
    )
    base_value = fields.Float(
        string='Base value',
        digits='Account',
    )

    def compute_base_tax(self, city=False):
        self.ensure_one()

        base_value = self.compute_base_value(city=city)
        base_tax = self.compute_base_city(city)

        return base_value, base_tax

    def compute_base_value(self, city=False):
        self.ensure_one()

        if self.base_city and city:
            return city.base_value

        return self.base_value

    def compute_base_city(self, city):
        self.ensure_one()

        Tax = self.env['account.tax']

        if self.amount_type != 'group':
            return self

        if not self.base_type:
            return self

        partner_id = self.env.context.get(
            'partner_id') or self.env.company.partner_id

        classification_id = partner_id.classification_id

        if not classification_id:
            return Tax

        classification_ids = city.classification_ids.filtered(
            lambda c: c.classification_id.id == classification_id.id)

        return classification_ids and classification_ids.tax_id or Tax
