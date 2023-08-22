# -*- coding: utf-8 -*-
{
    'name': "WorkFlow Diagram",

    'summary': """
        WorkFLow Diagram Conception""",

    'description': """
        Long description of module's purpose
    """,

    'author': "HTA Consulting",
    'website': "http://www.yourcompany.com",

    'installable': True,
    'auto_install': False,
    'category': 'Uncategorized',
    'licence': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/project_workflow_view.xml',
        # 'views/templates.xml',
        "wizard/workflow_edit_wizard.xml",
        "wizard/workflow_export_wizard.xml",
        "wizard/stage_change_confirmation_wizard.xml",
        "wizard/project_apply_workflow_wizard.xml",
        "wizard/workflow_mapping_wizard.xml",

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'sequence': -1000,

}
