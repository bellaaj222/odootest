# -*- coding: utf-8 -*-

{
    'name': 'Hospital Management',
    'version': '1.0.0',
    'category': 'Hospital',
    'author': 'Odoo HTA',
    'sequence': -100,
    'summary': 'Hospital managment system',
    'description': """Hospital management system""",

    'depends': ['mail', 'product'],
    'data': ['security/ir.model.access.csv',
             'wizard/cancel_appointment_view.xml',
             'views/menu.xml',
             'views/patient_view.xml',
             'views/female_patient_view.xml',
             'views/appointment_view.xml',
             'views/patient_tag_view.xml'
             ],
    'demo': [],
    'auto_install': False,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
