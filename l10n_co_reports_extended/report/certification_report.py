# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CertificationReport(models.AbstractModel):
    _inherit = 'report.l10n_co_reports.report_certification'

    def _get_report_values(self, docids, data=None):
        res = super(CertificationReport, self)._get_report_values(docids, data)
        res['report_env'] = self.env['account.report']
        return res


class ReportCertificationReport(models.AbstractModel):
    _inherit = 'l10n_co_reports.certification_report'

    def _add_to_partner_total(self, totals, new_values):
        for column, value in new_values.items():
            if isinstance(value, str):
                totals[column] = ''
            if isinstance(value, dict):
                totals[column] = {}
            else:
                totals[column] = totals.get(column, 0) + value
    
    def print_pdf(self, options):
        self = self.with_context(is_tax_detail=True)

        return super(ReportCertificationReport, self).print_pdf(options)


class ReportCertificationReportIca(models.AbstractModel):
    _inherit = 'l10n_co_reports.certification_report.ica'

    def _handle_aml(self, aml, lines_per_bimonth):
        bimonth = self._get_bimonth_for_aml(aml)
        if bimonth not in lines_per_bimonth:
            lines_per_bimonth[bimonth] = {
                'name': self._get_bimonth_name(bimonth),
                'tax_base_amount': 0,
                'balance': 0,
                'detail': {}
            }
        tax_id = aml.tax_line_id and \
            str(abs(aml.tax_line_id.id)) or False
        lines_per_bimonth[bimonth]['balance'] += aml.credit - aml.debit
        if aml.credit:
            lines_per_bimonth[bimonth]['tax_base_amount'] += aml.tax_base_amount
            if tax_id:
                tax_per = aml.tax_line_id and \
                    str(abs(aml.tax_line_id.amount)) or False
                if tax_id not in lines_per_bimonth[bimonth]['detail']:
                    lines_per_bimonth[bimonth]['detail'][tax_id] = {
                        'name': aml.name,
                        'percent': tax_per,
                        'balance': aml.credit - aml.debit,
                        'tax_base_amount': aml.tax_base_amount
                    }
                else:
                    lines_per_bimonth[bimonth]['detail'][tax_id]['balance'] += aml.credit - aml.debit
                    lines_per_bimonth[bimonth]['detail'][tax_id]['tax_base_amount'] += aml.tax_base_amount
        else:
            lines_per_bimonth[bimonth]['tax_base_amount'] -= aml.tax_base_amount
            if tax_id:
                tax_per = aml.tax_line_id and \
                    str(abs(aml.tax_line_id.amount)) or False
                if tax_id not in lines_per_bimonth[bimonth]['detail']:
                    lines_per_bimonth[bimonth]['detail'][tax_id] = {
                        'name': aml.name,
                        'percent': tax_per,
                        'balance': aml.credit - aml.debit,
                        'tax_base_amount': aml.tax_base_amount
                    }
                else:
                    lines_per_bimonth[bimonth]['detail'][tax_id]['balance'] += aml.credit - aml.debit
                    lines_per_bimonth[bimonth]['detail'][tax_id]['tax_base_amount'] -= aml.tax_base_amount
    
    def _get_values_for_columns(self, values):
        out = [
            {'name': values['name'], 'field_name': 'name'},
            {'name': self.format_value(values['tax_base_amount']), 'field_name': 'tax_base_amount'},
            {'name': self.format_value(values['balance']), 'field_name': 'balance'},
        ]
        if self._context.get('is_tax_detail', False):
            out.append({'name': values['detail'], 'field_name': 'detail'})
        return out


class ReportCertificationReportFuente(models.AbstractModel):
    _inherit = 'l10n_co_reports.certification_report.fuente'

    def _get_values_for_columns(self, values):
        out = [
            {'name': values['name'], 'field_name': 'name'},
            {'name': self.format_value(values['tax_base_amount']), 'field_name': 'tax_base_amount'},
            {'name': self.format_value(values['balance']), 'field_name': 'balance'}
        ]
        if self._context.get('is_tax_detail', False):
            out.append({'name': values['detail'], 'field_name': 'detail'})
        return out

    def _handle_aml(self, aml, lines_per_account):
        account_code = aml.account_id.code
        if account_code not in lines_per_account:
            lines_per_account[account_code] = {
                'name': aml.account_id.display_name,
                'tax_base_amount': 0,
                'balance': 0,
                'detail': {}
            }
        tax_id = aml.tax_line_id and \
            str(abs(aml.tax_line_id.id)) or False
        lines_per_account[account_code]['balance'] += aml.credit - aml.debit
        if aml.credit:
            lines_per_account[account_code]['tax_base_amount'] += aml.tax_base_amount

            if tax_id:
                tax_per = aml.tax_line_id and \
                    str(abs(aml.tax_line_id.amount)) or False
                if tax_id not in lines_per_account[account_code]['detail']:
                    lines_per_account[account_code]['detail'][tax_id] = {
                        'name': aml.name,
                        'percent': tax_per,
                        'balance': aml.credit - aml.debit,
                        'tax_base_amount': aml.tax_base_amount
                    }
                else:
                    lines_per_account[account_code]['detail'][tax_id]['balance'] += aml.credit - aml.debit
                    lines_per_account[account_code]['detail'][tax_id]['tax_base_amount'] += aml.tax_base_amount
        else:
            lines_per_account[account_code]['tax_base_amount'] -= aml.tax_base_amount
            if tax_id:
                tax_per = aml.tax_line_id and \
                    str(abs(aml.tax_line_id.amount)) or False
                if tax_id not in lines_per_account[account_code]['detail']:
                    lines_per_account[account_code]['detail'][tax_id] = {
                        'name': aml.name,
                        'percent': tax_per,
                        'balance': aml.credit - aml.debit,
                        'tax_base_amount': aml.tax_base_amount
                    }
                else:
                    lines_per_account[account_code]['detail'][tax_id]['balance'] += aml.credit - aml.debit
                    lines_per_account[account_code]['detail'][tax_id]['tax_base_amount'] -= aml.tax_base_amount
