# -*- coding: utf-8 -*-

{
    'name': 'Gestion de Projet Employee',
    'version': '1.0.0',
    'category': 'Projet',
    'author': 'Odoo HTA',
    'sequence': -100,
    'summary': 'Hta Gestion de Projet',
    'description': """Hta Gestion de Projet""",

    'depends': ['project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/act_flw.xml',

    ],
    'auto_install': False,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
