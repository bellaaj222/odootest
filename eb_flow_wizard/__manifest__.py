# -*- coding: utf-8 -*-

{
    'name': 'Test Management test',
    'version': '1.0.0',
    'category': 'test ',
    'author': 'Odoo HTA ',
    'sequence': -100,
    'summary': 'Test managment system',
    'description': """TESt management system""",

    'depends': ['base'],
    'data': ['security/ir.model.access.csv',
             'views/act_flw.xml',
             ],
    'demo': [],
    'auto_install': False,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
