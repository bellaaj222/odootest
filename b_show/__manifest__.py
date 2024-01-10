# -*- coding: utf-8 -*-
{
    'name': "Recherche Bons",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project_custom'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/b_show.xml',
        'views/b_gest_show.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'b_show/static/src/css/align_right.css',
        ],
    },
    'application': True,
    'sequence': -520,
}