# -*- coding: utf-8 -*-

{
    'name': "Merge Tasks",
    'version': '1.0.',
    'category': 'Project, Tasks',
    'author': "A.A",
    'summary': '  ',
    'description': """    """,
    'depends': ['base', 'project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/work.xml',
    ],
    'demo': [
    ],

    'auto-install': False,
    'installable': True,
    'license': 'LGPL-3',
    'application': True,
}