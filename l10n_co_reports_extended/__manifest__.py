# -*- coding: utf-8 -*-
{
    'name': 'Colombian - Accounting Reports Extended',
    'summary': '''
        Module Extension: Colombian - Accounting Reports
    ''',
    'description': '''
        - Ica retention report with detail by retention percentage.
    ''',
    'author': '1-800CLOUD',
    'contributors': [
        'Bernardo D. Lara Guevara - bernardo.lara@1-800cloud.com'
    ],
    'website': 'https://www.1-800cloud.com/',
    'category': 'Accounting/Localizations/Reporting',
    'license': 'LGPL-3',
    'version': '15.0.0.0.2',
    'depends': [
        'l10n_co_reports'
    ],
    'data': [ 
        # 'security/ir.model.access.csv',
        'report/certification_report_templates.xml',
    ],
}
