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
    'depends': ['base', 'project', 'web', 'generic_request'],
    'application': True,
    'sequence': -1000,

    # always loaded
    'assets': {
        'web.assets_backend': [
            'custom_addons/project_workflow_management/static/src/js/diagram_controller.js',
            'custom_addons/project_workflow_management/static/src/js/diagram_model.js',
            'custom_addons/project_workflow_management/static/src/js/diagram_renderer.js',
            'custom_addons/project_workflow_management/static/src/js/task_workflow.js',
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/project_workflow_management.xml',
        'views/project_workflow_view.xml',
        'views/res_config_settings_views.xml',
        # 'views/templates.xml',
        "wizard/workflow_edit_wizard.xml",
        "wizard/workflow_export_wizard.xml",
        "wizard/stage_change_confirmation_wizard.xml",
        "wizard/project_apply_workflow_wizard.xml",
        "wizard/workflow_mapping_wizard.xml",

    ],
    'qweb': [
        "project_workflow_management/static/src/xml/diagram.xml",
        "project_workflow_management/static/src/xml/base.xml",
    ],

}
