# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

COST_LIST = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume')
]

COST_DICT = {
    'equal': 'product_equal',
    'by_quantity': 'product_qty',
    'by_current_cost_price': 'price_cost',
    'by_weight': 'product_weight',
    'by_volume': 'product_volume'
}


class PurchaseImport(models.Model):
    _name = 'purchase.import'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase import'
    _order = 'id desc'

    def _default_company_id(self):
        return self.env.company

    def _default_currency_id(self):
        return self.env.company.currency_id

    def _default_user_id(self):
        return self.env.user

    # Company
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True,
        copy=False,
        default=_default_company_id
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Company currency'
    )

    country_id = fields.Many2one(
        comodel_name='res.country',
        required=True
    )

    # Cost
    cost_id = fields.Many2one(
        comodel_name='stock.landed.cost',
        string='Landed cost',
        copy=False
    )
    cost_type = fields.Selection(
        selection=COST_LIST,
        string='Cost method',
        required=True,
        default='by_quantity'
    )

    # Currency
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        required=True,
        default=_default_currency_id
    )

    # Date
    date_destination = fields.Date()
    date_import = fields.Date()
    date_load = fields.Date()
    date_origin = fields.Date('Port of origin')
    date_port = fields.Date('Port of destination')

    # Expense
    expense_freight = fields.Monetary(
        compute='_compute_expense'
    )
    expense_insurance = fields.Monetary(
        compute='_compute_expense'
    )

    # Incoterm
    incoterms_id = fields.Many2one(
        comodel_name='account.incoterms',
        string="Incoterm",
        required="True"
    )
    incoterms_freight = fields.Boolean(
        compute='_compute_incoterms'
    )
    incoterms_insurance = fields.Boolean(
        compute='_compute_incoterms'
    )

    invoices_ids = fields.Many2many(
        comodel_name='account.move',
        relation='account_move_purchase_import_rel',
        column1='purchase_import_id',
        column2='account_move_id',
        copy=False
    )

    import_type = fields.Selection(
        selection=[
            ('purchase', 'Purchases'),
            ('picking', 'Pickings'),
        ],
        required=True,
        default='purchase'
    )

    line_ids = fields.One2many(
        comodel_name='purchase.import.line',
        inverse_name='import_id',
        string='Lines'
    )

    # Manual
    manual_freight = fields. Monetary()
    manual_insurance = fields.Monetary()

    moves_ids = fields.Many2many(
        comodel_name='stock.move',
        copy=False
    )

    name = fields.Char(
        required=True,
        copy=False,
        default=_('New')
    )

    notes = fields.Html('Terms and Conditions')

    # Partner
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        required=True,
        tracking=True
    )
    partner_ref = fields.Char('Vendor Reference', copy=False)

    pickings_ids = fields.Many2many('stock.picking')

    # Price
    price_cost = fields.Monetary(
        string='Cost',
        compute='_compute_price_cost'
    )
    price_expense = fields.Monetary('Expense')
    price_expenses = fields.Monetary(
        string='Expenses',
        compute='_compute_price_expenses'
    )
    price_freight = fields.Monetary(
        string='Freight',
        compute='_compute_price_freight'
    )
    price_insurance = fields.Monetary(
        string='Insurance',
        compute='_compute_price_insurance'
    )
    price_tariff = fields.Monetary(
        string='Tariff',
        compute='_compute_price_tariff'
    )
    price_total = fields.Monetary(
        string='Subtotal',
        compute='_compute_price_total'
    )

    purchases_ids = fields.Many2many(
        comodel_name='purchase.order',
        copy=False
    )

    user_id = fields.Many2one(
        comodel_name='res.users',
        required=True,
        copy=False,
        default=_default_user_id
    )

    # Rate
    rate_currency = fields.Float(
        compute='_compute_rate',
        store=True,
        help='Exchange rate.'
    )
    rate_inverse = fields.Float(
        compute='_compute_rate',
        store=True,
        help='Reverse exchange rate.'
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('done', 'Done'),
            ('cancel', 'Cancel')
        ],
        readonly=True,
        copy=False,
        default='draft',
        tracking=True
    )

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.country_id = self.partner_id.country_id

    @api.model
    def create(self, vals):
        Sequence = self.env['ir.sequence']
        code = 'purchase.import'
        if vals.get('name', 'New') == 'New':
            vals['name'] = Sequence.next_by_code(code) or '/'
        return super(PurchaseImport, self).create(vals)

    @api.depends('incoterms_id')
    def _compute_incoterms(self):
        for record in self:
            incoterms_id = record.incoterms_id
            incoterms_type = incoterms_id and incoterms_id.incoterms_type or 'dh'
            incoterms_code = incoterms_id and incoterms_id.code or 'dh'
            freight = incoterms_type in ('gc', 'gd')
            insurance = freight and incoterms_code not in ('CPT', 'CFR')
            vals = {
                'incoterms_freight': freight,
                'incoterms_insurance': insurance
            }
            record.update(vals)

    @api.depends('invoices_ids')
    def _compute_expense(self):
        for record in self:
            invoice_freight = record.invoices_ids.filtered(
                lambda i: i.import_type == 'freight')
            invoice_insurance = record.invoices_ids.filtered(
                lambda i: i.import_type == 'insurance')

            invoice_field = record.company_id.purchase_import_type

            amount_freight = abs(
                sum(invoice_freight.mapped(invoice_field)))
            amount_insurance = abs(
                sum(invoice_insurance.mapped(invoice_field)))

            convert_freight = record.company_currency_id._convert(
                amount_freight,
                record.currency_id,
                record.company_id,
                record.date_import or fields.Date.today()
            )
            convert_insurance = record.company_currency_id._convert(
                amount_insurance,
                record.currency_id,
                record.company_id,
                record.date_import or fields.Date.today()
            )

            vals = {
                'expense_freight': convert_freight,
                'expense_insurance': convert_insurance
            }
            record.update(vals)

    @api.depends('line_ids.price_cost')
    def _compute_price_cost(self):
        for record in self:
            price_cost = sum(record.line_ids.mapped('price_cost'))
            record.update({'price_cost': price_cost})

    @api.depends('date_import')
    def _compute_price_expenses(self):
        for record in self:
            invoices_ids = record.invoices_ids.filtered(
                lambda i: i.import_type == 'expense')

            invoice_field = record.company_id.purchase_import_type

            amount_untaxed = abs(
                sum(invoices_ids.mapped(invoice_field)))
            price_expenses = record.company_currency_id._convert(
                amount_untaxed,
                record.currency_id,
                record.company_id,
                record.date_import or fields.Date.today()
            )
            record.update({'price_expenses': price_expenses})

    @api.depends('incoterms_freight', 'manual_freight', 'expense_freight')
    def _compute_price_freight(self):
        for record in self:
            price_freight = record.incoterms_freight and record.manual_freight or record.expense_freight
            record.update({'price_freight': price_freight})

    @api.depends('incoterms_insurance', 'manual_insurance', 'expense_insurance')
    def _compute_price_insurance(self):
        for record in self:
            price_insurance = record.incoterms_insurance and record.manual_insurance or record.expense_insurance
            record.update({'price_insurance': price_insurance})

    @api.depends('line_ids.price_tariff')
    def _compute_price_tariff(self):
        for record in self:
            price_tariff = sum(record.line_ids.mapped('price_tariff'))
            record.update({'price_tariff': price_tariff})

    @api.depends('line_ids.price_subtotal')
    def _compute_price_total(self):
        for record in self:
            price_subtotal = sum(record.line_ids.mapped('price_subtotal'))
            price_total = record.currency_id._convert(
                price_subtotal,
                record.company_currency_id,
                record.company_id,
                record.date_import or fields.Date.today()
            )
            self.update({'price_total': price_total})

    @api.depends('date_import', 'currency_id')
    def _compute_rate(self):
        for record in self:
            from_currency = record.company_currency_id
            to_currency = record.currency_id
            company = record.company_id
            date = record.date_import or fields.Date.today()

            currencies = from_currency + to_currency
            currency_rates = currencies._get_rates(company, date)
            from_currency_rate = currency_rates.get(from_currency.id)
            to_currency_rate = currency_rates.get(to_currency.id)

            record.rate_currency = to_currency_rate / from_currency_rate
            record.rate_inverse = from_currency_rate / to_currency_rate

    def action_draft(self):
        return self.write({'state': 'draft'})

    def action_confirm(self):
        return self.write({'state': 'confirm'})

    def action_validate(self):
        self.ensure_one()
        self = self.with_context(purchase_import_id=self.id)
        return self.pickings_ids.button_validate()

    def action_done(self):
        self.action_lines()
        for record in self:
            record._action_done()
        return self.write({'state': 'done'})

    def _action_done(self):
        self.ensure_one()
        self.action_cost()
        self.action_invoice()

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_moves(self):
        for record in self:
            if record.import_type == 'purchase':
                picking_ids = record.purchases_ids.picking_ids

            if record.import_type == 'picking':
                picking_ids = record.pickings_ids

            pickings = picking_ids.filtered(
                lambda p: p.state not in ('done', 'cancel'))
            # move_lines = pickings.move_lines
            # moves = move_lines.filtered(lambda m: m.state == 'assigned')
            moves = pickings.move_lines
            record.update({
                'moves_ids': [(6, 0, moves.ids)],
                'pickings_ids': [(6, 0, pickings.ids)]
            })

    def action_lines(self):
        for record in self:
            record.line_ids.unlink()
            line_ids = record.prepare_line_ids()
            record.write({'line_ids': line_ids})
            record.action_line_ids()

    def prepare_line_ids(self):
        self.ensure_one()

        line_ids = []
        move_ids = self.moves_ids.filtered(lambda m: m.quantity_done)

        for move in move_ids:
            line = move.purchase_line_id
            product = move.product_id

            product_qty = move.quantity_done

            if self.import_type == 'purchase':
                price_unit = line.price_unit
            else:
                price_move = move._get_price_unit()
                price_unit = self.company_currency_id._convert(
                    price_move,
                    self.currency_id,
                    self.company_id,
                    self.date_import or fields.Date.today()
                )

            price_cost = price_unit * product_qty

            vals = {
                'move_id': move.id,
                'line_id': line and line.id or False,
                'product_id': product.id,
                'name': line and line.name or move.name,
                'product_qty': product_qty,
                'product_uom': move.product_uom.id,
                'product_weight': product_qty * product.weight,
                'product_volume': product_qty * product.volume,
                'price_unit': price_unit,
                'price_cost': price_cost,
            }
            line_ids.append((0, 0, vals))

        return line_ids

    def action_line_ids(self):
        self.ensure_one()

        lines_sum, line_field = self.prepare_percentage()

        for line in self.line_ids:
            product_tmpl = line.product_id.product_tmpl_id
            percentage = sum(line.mapped(line_field)) / lines_sum

            price_insurance = self.price_insurance * percentage
            price_freight = self.price_freight * percentage
            price_cif = line.price_cost + price_insurance + price_freight

            tariffes_ids = product_tmpl.get_tariff_ids(self.country_id)
            tariffes = tariffes_ids.compute_all(
                price_cif,
                currency=self.currency_id,
                quantity=1.0,
                product=line.product_id,
                partner=self.partner_id
            )

            price_tariff = tariffes['total_included'] - \
                tariffes['total_excluded']

            taxes_ids = product_tmpl.tariffes_ids
            taxes = taxes_ids.compute_all(
                price_cif + price_tariff,
                currency=self.currency_id,
                quantity=1.0,
                product=line.product_id,
                partner=self.partner_id
            )

            price_tax = taxes['total_included'] - taxes['total_excluded']

            price_expense = self.price_expenses * percentage
            price_subtotal = price_insurance + price_freight + price_tariff + price_expense
            price_total = price_cif + price_tariff + price_tax + price_expense

            vals = {
                'price_insurance': price_insurance,
                'price_freight': price_freight,
                'price_cif': price_cif,
                'tariffes_ids': [(6, 0, tariffes_ids.ids)],
                'price_tariff': price_tariff,
                'taxes_ids': [(6, 0, taxes_ids.ids)],
                'price_tax': price_tax,
                'price_expense': price_expense,
                'price_subtotal': price_subtotal,
                'price_total': price_total
            }
            line.write(vals)

    def prepare_percentage(self):
        self.ensure_one()
        line_field = COST_DICT.get(self.cost_type)
        lines_sum = sum(self.line_ids.mapped(line_field))
        if not lines_sum:
            raise ValidationError(_('Please modify cost method'))
        return lines_sum, line_field

    def action_cost(self):
        self.ensure_one()
        cost = self.prepare_cost()
        cost.write({'import_is': True})
        return self.write({'cost_id': cost.id, 'price_expense': self.price_expenses})

    def prepare_cost(self):
        self.ensure_one()
        Cost = self.env['stock.landed.cost']
        vals = {
            'picking_ids': [(6, 0, self.pickings_ids.ids)],
            'cost_lines': self.prepare_cost_lines()
        }
        cost = Cost.create(vals)
        cost.compute_landed_cost()
        cost.button_validate()
        return cost

    def prepare_cost_lines(self):
        self.ensure_one()
        partner = self.partner_id
        lines = []
        # Insurance
        if self.price_insurance:
            product = self.env.ref('purchase_import.product_import_insurance')
            if self.incoterms_insurance:
                price = self.currency_id._convert(
                    self.price_insurance,
                    self.company_currency_id,
                    self.company_id,
                    self.date_import or fields.Date.today()
                )
            else:
                invoices_ids = self.invoices_ids.filtered(
                    lambda i: i.import_type == 'insurance')
                for partner in invoices_ids.partner_id:
                    invoices = invoices_ids.filtered(
                        lambda i: i.partner_id.id == partner.id)
                    invoice_field = self.company_id.purchase_import_type
                    price = abs(sum(invoices.mapped(invoice_field)))
            vals = self.prepare_cost_line(partner, product, price)
            lines.append((0, 0, vals))
        # Freight
        if self.price_freight:
            product = self.env.ref('purchase_import.product_import_freight')
            if self.incoterms_freight:
                price = self.currency_id._convert(
                    self.price_freight,
                    self.company_currency_id,
                    self.company_id,
                    self.date_import or fields.Date.today()
                )
            else:
                invoices_ids = self.invoices_ids.filtered(
                    lambda i: i.import_type == 'freight')
                for partner in invoices_ids.partner_id:
                    invoices = invoices_ids.filtered(
                        lambda i: i.partner_id.id == partner.id)
                    invoice_field = self.company_id.purchase_import_type
                    price = abs(sum(invoices.mapped(invoice_field)))
            vals = self.prepare_cost_line(partner, product, price)
            lines.append((0, 0, vals))
        # Tariff
        if self.price_tariff:
            partner = self.env.ref('purchase_import.partner_import_dian')
            product = self.env.ref('purchase_import.product_import_tariff')
            price = self.currency_id._convert(
                self.price_tariff,
                self.company_currency_id,
                self.company_id,
                self.date_import or fields.Date.today()
            )
            vals = self.prepare_cost_line(partner, product, price)
            lines.append((0, 0, vals))
        # Expense
        if self.price_expenses:
            product = self.env.ref('purchase_import.product_import_expense')
            invoices_ids = self.invoices_ids.filtered(lambda i: i.import_type == 'expense')
            for partner in invoices_ids.partner_id:
                invoices = invoices_ids.filtered(lambda i: i.partner_id.id == partner.id)
                invoice_field = self.company_id.purchase_import_type
                price = abs(sum(invoices.mapped(invoice_field)))
                vals = self.prepare_cost_line(partner, product, price)
                lines.append((0, 0, vals))
        return lines

    def prepare_cost_line(self, partner, product, price):
        self.ensure_one()
        accounts = product.product_tmpl_id.get_product_accounts()
        account_id = accounts.get(
            'expense') and accounts['expense'].id or False
        vals = {
            'partner_id': partner.id,
            'product_id': product.id,
            'name': product.name,
            'account_id': account_id,
            'split_method': self.cost_type,
            'price_unit': price
        }
        return vals

    def action_invoice(self):
        self.ensure_one()
        invoices = []

        invoice_tax = self.prepare_invoice()
        if invoice_tax:
            invoices.append(invoice_tax.id)

        if self.import_type == 'purchase':
            purchase_act = self.purchases_ids.action_create_invoice()
            if purchase_act.get('res_id'):
                invoices.append(purchase_act['res_id'])
            else:
                invoices = purchase_act['domain'][0][2]

        return self.write({'invoices_ids': [(4, invoice, 0) for invoice in invoices]})

    def prepare_invoice(self):
        self.ensure_one()
        Move = self.env['account.move']
        invoice_line_ids = self.prepare_invoice_lines()

        if not invoice_line_ids:
            return False

        vals = {
            'move_type': 'in_invoice',
            'invoice_line_ids': invoice_line_ids
        }
        return Move.create(vals)

    def prepare_invoice_lines(self):
        self.ensure_one()
        lines = []

        product_tariff = self.env.ref('purchase_import.product_import_tariff')
        product_tax = self.env.ref('purchase_import.product_import_tax')

        price_tariff = sum(self.line_ids.mapped('price_tariff'))
        price_tax = sum(self.line_ids.mapped('price_tax'))

        if price_tariff:
            vals = self.prepare_invoice_line(
                product_tariff,
                price_tariff
            )
            lines.append((0, 0, vals))

        if price_tax:
            vals = self.prepare_invoice_line(
                product_tax,
                price_tax
            )
            lines.append((0, 0, vals))

        return lines

    def prepare_invoice_line(self, product, price):
        price_unit = self.currency_id._convert(
            price,
            self.company_currency_id,
            self.company_id,
            self.date_import or fields.Date.today()
        )
        vals = {
            'product_id': product.id,
            'name': product.name,
            'quantity': 1,
            'price_unit': price_unit,
        }
        return vals


class PurchaseImportLine(models.Model):
    _name = 'purchase.import.line'
    _description = 'Purchase import line'

    currency_id = fields.Many2one(related='import_id.currency_id')

    import_id = fields.Many2one(
        comodel_name='purchase.import',
        required=True,
        ondelete='cascade'
    )

    line_id = fields.Many2one('purchase.order.line')

    move_id = fields.Many2one('stock.move')

    name = fields.Char(required=True)

    # Price
    price_cif = fields.Monetary('CIF')
    price_cost = fields.Monetary('Cost')
    price_expense = fields.Monetary('Expense')
    price_freight = fields.Monetary('Freight')
    price_insurance = fields.Monetary('Insurance')
    price_subtotal = fields.Monetary('Subtotal')
    price_tariff = fields.Monetary('Tariff')
    price_tax = fields.Monetary('Tax')
    price_total = fields.Monetary('Total')
    price_unit = fields.Monetary('Price')

    # Product
    product_equal = fields.Float(
        string='Equal',
        default=1,
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        required=True
    )
    product_qty = fields.Float(
        string='Quantity',
        digits='Product Unit of Measure',
        required=True
    )
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string='UoM'
    )
    product_volume = fields.Float(
        string='Volume',
        digits='Volume',
    )
    product_weight = fields.Float(
        string='Weight',
        digits='Stock Weight',
    )

    tariffes_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='line_tarrif_rel',
        column1='line_id',
        column2='tax_id',
        string='Tariffes'
    )

    taxes_ids = fields.Many2many(
        comodel_name='account.tax',
        relation='line_tax_rel',
        column1='line_id',
        column2='tax_id',
        string='Taxes'
    )
