# -*- coding: utf-8 -*-
{
    'name': "Merge Invoices to assign",

    'summary': """
        A module to assign employees""",

    'description': """
        Assign Employees
    """,

    'author': "YASMINE",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', 'task_work', 'eb_group_wizard', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views_aff.xml',
        'views/action_aff.xml',
        'views/inherit.xml',

    ],

    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {},
    'sequence': -740,
}
