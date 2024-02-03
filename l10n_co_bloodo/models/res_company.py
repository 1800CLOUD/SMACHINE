# -*- coding: utf-8 -*-

from requests import post, exceptions
from lxml import etree

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResCompany(models.Model):
    _inherit = 'res.company'

    type_einvoicing = fields.Selection([('no', _("Don't apply")),
                                        ('edi_dir', _('Direct to DIAN')), ],
                                       'e-Invoicing',
                                       default='no')

    fv_sent = fields.Integer('fv sent')
    nc_sent = fields.Integer('nc sent')
    nd_sent = fields.Integer('nd sent')
    zip_sent = fields.Integer('Zips sent')
    ar_sent = fields.Integer('ar sent')
    ad_sent = fields.Integer('ad sent')
    ds_sent = fields.Integer('ds sent')
    nas_sent = fields.Integer('nas sent')
    ars_sent = fields.Integer('ars sent')

    target_environment_id = fields.Selection([('1', 'Production'),
                                             ('2', 'Test')],
                                             'e-Invoice target environment ',
                                             default='2',
                                             required=True)
    test_set_id = fields.Char('Test Set Id')
    software_id = fields.Char('Software Id')
    software_pin = fields.Char('Software PIN')
    certificate_filename = fields.Char('Certificate Name')
    certificate_file = fields.Binary('Certificate')
    certificate_password = fields.Char('Certificate password')
    signature_policy_url = fields.Char(
        'Url signature policy',
        default='https://facturaelectronica.dian.gov.co'
                '/politicadefirma/v2/politicadefirmav2.pdf'
    )
    signature_policy_description = fields.Char(
        'Signature policy description',
        default='Política de firma para facturas '
        'electrónicas de la República de Colombia.')
    signature_policy_filename = fields.Char(
        'Signature policy file name'
    )
    signature_policy_file = fields.Binary('Signature policy file')
    response_get_numbering_range = fields.Text('Response of numbering ranges')
    tributary_information = fields.Text('Tributary information')

    edi_email = fields.Char('e-invoicing mail',
                            help='Mail of origin for e-invoicing')
    edi_email_error = fields.Char('Error notification emails',
                                  help='To add multiple emails, you must '
                                  'separate them with a comma (,).')
    report_template = fields.Many2one('ir.actions.report', 'Report Template')
    # DS
    type_support_doc = fields.Selection([('no', _("Don't apply")),
                                         ('edi_dir', _('Direct to DIAN')), ],
                                        'Support document',
                                        default='no')
    ds_target_environment_id = fields.Selection(
        [('1', 'Production'),
         ('2', 'Test')],
        'Support doc target environment',
        default='2',
        required=True
    )
    ds_test_set_id = fields.Char('SD Test Set Id')
    ds_software_id = fields.Char('SD Software Id')
    ds_software_pin = fields.Char('SD Software PIN')

    ei_fiscal_respo = fields.Char(
        'Responabilidad fiscal',
        help='Texto de responsabilidad fiscal que se presenta en el encabezado del formato de factura electronica'
    )

    def write(self, vals):
        res = super(ResCompany, self).write(vals)
        for record in self:
            if vals.get('edi_email'):
                record.partner_id.write({
                    'edi_email': record.edi_email
                })
            
        return res
