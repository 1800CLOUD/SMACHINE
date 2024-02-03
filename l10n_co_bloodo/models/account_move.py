# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang, format_date, get_lang

_logger = logging.getLogger(__name__)

TYPE_DOC_NAME = {
    'invoice': _('Invoice'),
    'credit': _('Credit Note'),
    'debit': _('Debit Note')
}

EDI_OPERATION_TYPE = [
    ('10', 'Estandar'),
    ('09', 'AIU'),
    ('11', 'Mandatos'),
    ('20', 'Nota Crédito que referencia una factura electrónica'),
    ('22', 'Nota Crédito sin referencia a facturas'),
    # ('23', 'Nota Crédito para facturación electrónica V1 (Decreto 2242)'),
    ('30', 'Nota Débito que referencia una factura electrónica'),
    ('32', 'Nota Débito sin referencia a facturas'),
    # ('33', 'Nota Débito para facturación electrónica V1 (Decreto 2242)')
]

EVENT_CODES = [
    ('02', '[02] Documento validado por la DIAN'),
    ('04', '[03] Documento rechazado por la DIAN'),
    ('030', '[030] Acuse de recibo'),
    ('031', '[031] Reclamo'),
    ('032', '[032] Recibo del bien'),
    ('033', '[033] Aceptación expresa'),
    ('034', '[034] Aceptación Tácita'),
    ('other', 'Otro')
]


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_einv_warning(self):
        warn_remaining = False
        inactive_resolution = False
        sequence_id = self.journal_id.sequence_id

        if sequence_id.edi_resolution_control:
            remaining_numbers = self.journal_id.remaining_numbers
            remaining_days = self.journal_id.remaining_days
            date_range = self.env['ir.sequence.date_range'].search(
                [('sequence_id', '=', sequence_id.id),
                 ('active_resolution', '=', True)])
            today = datetime.strptime(
                str(fields.Date.today(self)),
                '%Y-%m-%d'
            )
            if date_range:
                date_range.ensure_one()
                date_to = datetime.strptime(
                    str(date_range.date_to),
                    '%Y-%m-%d'
                )
                days = (date_to - today).days
                numbers = date_range.number_to - date_range.number_next_actual
                if numbers < remaining_numbers or days < remaining_days:
                    warn_remaining = True
            else:
                inactive_resolution = True
        self.is_inactive_resolution = inactive_resolution
        self.fe_warning = warn_remaining

    fe_warning = fields.Boolean('Warn by resolution ranges?',
                                compute='_get_einv_warning',
                                store=False)
    is_inactive_resolution = fields.Boolean('Warn Inactive Resolution?',
                                            compute='_get_einv_warning',
                                            store=False)
    fe_invoice_name = fields.Char('Electronic Invoice',
                                  help='Consecutive of the electronic '
                                  'invoice published in the DIAN.',
                                  readonly=True,
                                  copy=False)
    fe_datetime_invoice = fields.Datetime('Validation Date',
                                          help='Technical field used to '
                                          'store the invoice validation time.',
                                          copy=False)
    fe_type = fields.Selection(
        [('01', 'Factura de venta'),
         ('02', 'Factura de exportación'),
         ('03', 'Documento electrónico de transmisión - tipo 03'),
         ('04', 'Factura electrónica de Venta - tipo 04'), ],
        'Electronic Invoice Type',
        required=True,
        default='01',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    fe_operation_type = fields.Selection(EDI_OPERATION_TYPE,
                                         'Operation Type',
                                         default='10',
                                         required=True)
    fe_payment_option_id = fields.Many2one(
        'dian.payment.option',
        'Payment Option',
        default=lambda self: self.env.ref('l10n_co_bloodo.payment_option_1',
                                          raise_if_not_found=False)
    )
    fe_is_direct_payment = fields.Boolean(
        'Direct Payment from Colombia',
        compute='_compute_fe_is_direct_payment'
    )
    fe_mandante_id = fields.Many2one('res.partner',
                                     'Mandante')
    fe_cufe_cude_ref = fields.Char('CUFE/CUDE',
                                   readonly=True,
                                   copy=False)
    fe_url = fields.Char('Url', copy=False)
    fe_cufe_cude_uncoded = fields.Char('CUFE/CUDE uncoded', copy=False)
    fe_ssc_uncoded = fields.Char('SSC uncoded', copy=False)
    fe_ssc = fields.Char('SSC', copy=False)
    fe_qr_image = fields.Binary('QR code', copy=False)
    fe_qr_data = fields.Text('QR code data', copy=False)

    is_external_invoice = fields.Boolean('External invoice?', copy=False)
    name_ei_ref = fields.Char('Ref number', copy=False)
    uuid_ei_ref = fields.Char('Ref Cufe', copy=False)
    issue_date_ei_ref = fields.Date('Ref date', copy=False)
    operation_type_ei_ref = fields.Selection(
        EDI_OPERATION_TYPE[:3],
        'Operation type',
        copy=False
    )
    fe_type_ei_ref = fields.Selection(
        [('01', 'Factura de venta'),
         ('02', 'Factura de exportación'),
         ('03', 'Documento electrónico de transmisión - tipo 03'),
         ('04', 'Factura electrónica de Venta - tipo 04'),
         ('91', 'Nota Crédito'),
         ('92', 'Nota Débito'),
         ('96', 'Eventos (ApplicationResponse)'), ],
        'Ref Type',
        required=True,
        default='01',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    fe_correction_id = fields.Many2one('dian.discrepancy.response',
                                       'Correction concept',
                                       copy=False)
    type_note = fields.Selection([('debit', 'Debit note'),
                                  ('credit', 'Credit note')],
                                 'Note type')
    credit_note_ids = fields.One2many('account.move',
                                      'reversed_entry_id',
                                      'Credit notes',
                                      copy=False)
    credit_note_count = fields.Integer('Number of credit notes',
                                       compute='_compute_credit_count')

    # DIAN DOC
    is_einvoicing_journal = fields.Boolean('Journal with e-doc',
                                           related='journal_id.is_einvoicing')
    fe_pdf_fname = fields.Char('Pdf name', copy=False)
    fe_pdf_file = fields.Binary('Pdf file', copy=False)
    fe_xml_fname = fields.Char('XML name', copy=False)
    fe_xml_file = fields.Binary('XML file', copy=False)
    fe_ad_fname = fields.Char('Attached name', copy=False)
    fe_ad_file = fields.Binary('Attached file', copy=False)
    fe_zip_fname = fields.Char('Zip name', copy=False)
    fe_zip_file = fields.Binary('Zip file', copy=False)
    fe_ar_fname = fields.Char('ApplicationResponse name',
                              copy=False)
    fe_ar_file = fields.Binary('ApplicationResponse file', copy=False)
    fe_zip_key = fields.Char('ZipKey', copy=False)
    # Response
    fe_state = fields.Char('e-Doc. status code',
                           default=False,
                           copy=False)
    fe_state_msg = fields.Char('e-Doc. status Message',
                               default=False,
                               copy=False)
    fe_response = fields.Text('Response', copy=False)
    mail_sent = fields.Boolean('E-mail sent?', copy=False)
    fe_log_ids = fields.One2many('edi.document.log',
                                 'move_id',
                                 'Edi Log',
                                 copy=False)
    # supplier ei
    is_supplier_ei = fields.Boolean('Supplier e-invoice',
                                    default=False,
                                    copy=False)
    way_to_pay = fields.Selection([('credit', 'Credit'),
                                   ('cash', 'Cash')],
                                  'Way to pay',
                                  compute='_compute_way_to_pay',
                                  store=True)
    ie_event_status = fields.Char('Event status code',
                                  copy=False)
    ie_event_history_ids = fields.One2many('history.dian.event',
                                           'move_id',
                                           'History of events',
                                           copy=False,
                                           help='History of events')
    ie_event_active_id = fields.Many2one('history.dian.event',
                                         'Event active',
                                         compute='_compute_event_active_id',
                                         copy=False)
    ie_event_active_date = fields.Datetime('Event registration date',
                                           copy=False)
    ie_claim_id = fields.Many2one('dian.claim.concept',
                                  'Claim concept',
                                  copy=False)
    ie_event_display = fields.Selection(EVENT_CODES,
                                        'Event status',
                                        copy=False,
                                        help='Active event of the electronic '
                                        'invoice, check the status '
                                        'to keep it updated')
    ev_fe_state = fields.Char('Event shipping status',
                              default=False,
                              copy=False,
                              help='Status code of the event delivery '
                              'to the DIAN')
    ev_fe_response = fields.Text(
        'Event shipping response',
        copy=False,
        help='Response message of the event delivery. Here you can see '
        'the validations list to correct if the event has been rejected.')

    def _compute_event_active_id(self):
        for record in self:
            event_id = record.ie_event_history_ids.filtered(
                lambda e: e.ev_active
            )
            record.ie_event_active_id = event_id and \
                event_id[0].id or \
                False

    @api.depends('move_type', 'invoice_date',
                 'invoice_date_due', 'issue_date_ei_ref')
    def _compute_way_to_pay(self):
        for record in self:
            date = record.issue_date_ei_ref or record.invoice_date or False
            date_due = record.invoice_date_due
            pay = 'cash'
            if date and date_due:
                if date < date_due:
                    pay = 'credit'
            record.way_to_pay = pay

    @api.depends('invoice_date_due', 'date')
    def _compute_fe_is_direct_payment(self):
        for rec in self:
            rec.fe_is_direct_payment = (rec.date == rec.invoice_date_due) and \
                rec.company_id.country_id.code == 'CO' and \
                rec.is_einvoicing_journal

    @api.depends('credit_note_ids')
    def _compute_credit_count(self):
        credit_data = self.env['account.move'].read_group(
            [('reversed_entry_id', 'in', self.ids)],
            ['reversed_entry_id'],
            ['reversed_entry_id']
        )
        data_map = {
            datum['reversed_entry_id'][0]:
            datum['reversed_entry_id_count'] for datum in credit_data
        }
        for inv in self:
            inv.credit_note_count = data_map.get(inv.id, 0.0)

    def action_view_credit_notes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Credit Notes'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('reversed_entry_id', '=', self.id)],
        }

    def _get_sequence(self):
        '''
            Return the sequence to be used during
             the post of the current move.
            :return: An ir.sequence record or False.
        '''
        res = super(AccountMove, self)._get_sequence()

        journal = self.journal_id
        if self.move_type == 'out_invoice' and not self.type_note:
            return journal.sequence_id
        elif self.move_type == 'out_refund' and self.type_note == 'credit':
            return journal.refund_sequence_id
        elif self.move_type == 'out_invoice' and self.type_note == 'debit':
            return journal.debit_note_sequence_id
        return res


    def action_invoice_sent(self):
        '''
            Open a window to compose an email, with the edi invoice template
            message loaded by default
        '''
        self.ensure_one()
        if self.is_einvoicing_journal:
            template = self.env.ref(
                'l10n_co_bloodo.dian_email_template',
                raise_if_not_found=False
            )
        else:
            template = self.env.ref(
                'account.email_template_edi_invoice',
                raise_if_not_found=False
            )
        attach_ids = []
        zip_attachment_file = False
        if self.fe_zip_file:
            zip_attachment_file = self.env['ir.attachment'].create({
                'name': self.fe_zip_fname,
                'type': 'binary',
                'datas': self.fe_zip_file,
            })
        if zip_attachment_file:
            attach_ids.append(zip_attachment_file.id)
        if attach_ids:
            template.attachment_ids = [(6, 0, attach_ids)]
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref(
            'account.account_invoice_send_wizard_form',
            raise_if_not_found=False
        )
        ctx = dict(
            default_model='account.move',
            default_res_id=self.id,
            # For the sake of consistency we need a default_res_model if
            # default_res_id is set. Not renaming default_model as it can
            # create many side-effects.
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout='mail.mail_notification_paynow',
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def _get_type_document(self):
        '''
            Return: 'invoice' or 'credit' or 'debit'
        '''
        self.ensure_one()
        if self.move_type == 'out_invoice' and not self.type_note:
            return 'invoice'
        elif self.move_type == 'out_refund' and self.type_note != 'debit':
            return 'credit'
        elif self.move_type == 'out_invoice' and self.type_note == 'debit':
            return 'debit'
        else:
            return False

        # Not used
    def get_name_type_document(self):
        self.ensure_one()
        type_document = self._get_type_document()
        name_doc = ''
        if type_document == 'invoice':
            name_doc = _('Invoice')
        elif type_document == 'credit':
            name_doc = _('Credit Note')
        elif type_document == 'debit':
            name_doc = _('Debit Note')
        return name_doc

    
    

    def _get_payment_mean_edi(self):
        self.ensure_one()
        if self.invoice_date < self.invoice_date_due:
            return '2'  # Credito
        elif self.invoice_date == self.invoice_date_due:
            return '1'  # Contado
        else:
            raise ValidationError(_(
                'An error occurred!!\n '
                'The due date cannot be less than the invoice'
                ' date or it is being calculated incorrectly.'
            ))

    
    
    def action_send_mail(self):
        msg = _('Your invoice has not been posted.')
        template_id = self.env.ref(
            'l10n_co_bloodo.dian_email_template').id
        template = self.env['mail.template'].browse(template_id)

        if not self.name:
            raise UserError(msg)
        zip_attachment = False
        if self.fe_zip_file:
            zip_attachment = self.env['ir.attachment'].create({
                'name': self.fe_zip_fname,
                'type': 'binary',
                'datas': self.fe_zip_file
            })
            if zip_attachment:
                template.attachment_ids = [(6, 0, [zip_attachment.id])]
        template.send_mail(self.id, force_send=True)
        self.write({'mail_sent': True})
        return True

    def lieferant_rechnung_einfuhren(self):
        if self.state != 'draft':
            raise ValidationError(_(
                'This operation is not allowed '
                'if the document is not in draft'
            ))
        return {
            'name': _('Import supplier e-invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'invoice.import.wizard',
            'target': 'new',
            'context': {
                'default_move_id': self.id,
                'default_msg': _(
                    'Please add the file that you want to upload as '
                    'supplier invoice.\n'
                    'This can be the <AttachedDocument> or <Invoice> '
                    'Xml document or the Zip document that contains them.'
                ),
                'default_btn_create': False,
            }
        }

    