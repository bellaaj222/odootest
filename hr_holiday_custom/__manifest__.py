{
    'name': "Holidays Custom",

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
    'depends': ['base', 'project_custom', 'calendar'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/type.xml',
        'views/histo_co_workers.xml',
        'views/super_view.xml',
        'views/employee_view.xml',
        'views/holiday_histo.xml',
        'views/actions_employee.xml',
        'views/histo_super.xml',
        'views/cloture.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True,
    'sequence': -600,
}
