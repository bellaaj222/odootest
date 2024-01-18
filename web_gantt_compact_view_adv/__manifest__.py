# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "All in One Gantt View | Workorder Gantt View | Production Gantt View | Project Task Gantt View | Sale Order Gantt view | Time Off Gantt view | Advanced",
    "summary": """
        The Planning view gives you a clear overview of what is already planned and 
        what remains to be planned using Start Date and End Date. It has  
        Workorder Gantt View, Production Gantt View, Project Task Gantt View, , Time Off Gantt View and 
        Sale Order Gantt view
    """,
    "version": "15.0.1",
    "description": """
        Project Gantt View
        ==================
        The Planning view gives you a clear overview of what is already planned and 
        what remains to be planned using Start Date and End Date. It has  
        Workorder Gantt View, Production Gantt View, Project Task Gantt View, , Time Off Gantt View and 
        Sale Order Gantt view
        - Gantt View
        - create new Task
        - customize an existing Tasks
        - TreeView for Gantt Items
        - Task Deadline Indicator
        - Task Priority Indicator
        - Task Progress Indicator
        - Multiple Scales
        - Navigate to Todat, Previous and Next Day
        - Grouping Task/Project
        - Filter
        - Progress bar on Task
        - Popup Task Informations
        - Overdue Indicator
        - Milestone Task in Different Shape
        - Predecessor Links
        - Todyas Marker
        - Sorting
        - Gantt View
        - Project Gantt
        - Project Gantt View
        - Gantt view Project
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/web_gantt_compact_view_adv.png"],
    "category": "Project",
    "depends": [
        "base",
        "web",
        "task_work",
        "mrp",
        "sale_management",
        "hr",
        "hr_holidays",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_gantt_views.xml",      
        "views/mrp_production_gantt_views.xml",      
        "views/mrp_workorder_gantt_views.xml",      
        "views/sale_gantt_views.xml",      
        "views/hr_leave_allocation_gantt_view.xml",
        "views/hr_leave_gantt_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/dhtmlxgantt.js",
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/api.js",
            "/web_gantt_compact_view_adv/static/lib/dhtmlxGantt/sources/dhtmlxgantt.css",
            
            "/web_gantt_compact_view_adv/static/src/css/gantt.css",
            "/web_gantt_compact_view_adv/static/src/js/gantt_model.js",
            "/web_gantt_compact_view_adv/static/src/js/gantt_renderer.js",
            "/web_gantt_compact_view_adv/static/src/js/gantt_controller.js",
            "/web_gantt_compact_view_adv/static/src/js/gantt_view.js",

            "/web_gantt_compact_view_adv/static/src/scss/time_off.scss",
        ],
        "web.assets_qweb": [
            "/web_gantt_compact_view_adv/static/src/xml/web_gantt.xml",
        ]
    },
    "installable": True,
    "application": True,
    "price"                :  100,
    "currency"             :  "EUR",
    "uninstall_hook"       :  "uninstall_hook",
}
