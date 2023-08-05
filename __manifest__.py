# -*- coding: utf-8 -*-
{
    'name': "Inventario Florestal - IPE",

    'summary': """
        Software de inventário florestal""",

    'description': """
       Softeare para inventário Florestal com os dados estatístivos
    """,

    'author': "Jg Soluções Inteligentes",
    'website': "http://www.jgma.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'diversos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','excel_import_export','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
       # 'views/templates.xml',
        'reports/templates.xml',
        'reports/report.xml',
        'reports/report_inventario.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}