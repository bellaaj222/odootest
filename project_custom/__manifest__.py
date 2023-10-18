# -*- coding: utf-8 -*-

{
    'name': "Project Custom",

    'summary': """
        Project Custom""",

    'description': """
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'task_custom', 'employee_custom', 'partner_custom',
                'company_custom', 'country_custom', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/account_tax.xml',
        'views/project.xml',
        'views/planning.xml',
        'views/template.xml',
        'views/template_gest.xml',
        'views/not_kit.xml',
        'views/type.xml',
        'views/dash.xml',
        'views/menu.xml',
        'views/inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_custom/static/src/css/kanban_custom.css',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'application': True,
    'sequence': -1000,
}
