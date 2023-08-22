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
    "images": ["static/description/banner.png"],

    # any module necessary for this one to work correctly
    'depends': ['base', 'project', ],
    # 'web_ir_actions_act_multi', 'web_ir_actions_act_view_reload',
    #

    # always loaded

    'data': [
        'security/ir.model.access.csv',
        # 'views/project_workflow_management.xml',
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
    'qweb': [
        "static/src/xml/diagram.xml",
        "static/src/xml/base.xml",
    ],
    'assets': {
        'web.assets_backend': [
            'static/src/js/diagram_controller.js',
            'static/src/js/diagram_model.js',
            'static/src/js/diagram_renderer.js',
            'static/src/js/task_workflow.js',
        ],
    },
    'application': True,
    'sequence': -1000,

}
