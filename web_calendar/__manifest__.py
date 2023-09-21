# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Web Calendar',
    'category': 'Hidden',
    'description': """
Odoo Web Calendar view.
==========================

""",
    'author': 'Odoo SA, Valentino Lab (Kalysto)',
    'version': '2.0',
    'depends': ['web'],
    'data': [
        'views/web_calendar_templates.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'auto_install': True,

    'web.assets_backend': [
            '/web_calendar/static/lib/fullcalendar/js/fullcalendar.js',
            '/web_calendar/static/src/js/widgets.js',
            '/web_calendar/static/src/js/web_calendar.js',
            '/web_calendar/static/src/less/web_calendar.less',
            '/web_calendar/static/lib/fullcalendar/css/fullcalendar.css',
            ''
        ],
}
