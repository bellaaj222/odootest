# -*- coding: utf-8 -*-
# from odoo import http


# class ProjectWorkflowManagement(http.Controller):
#     @http.route('/project_workflow_management/project_workflow_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/project_workflow_management/project_workflow_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('project_workflow_management.listing', {
#             'root': '/project_workflow_management/project_workflow_management',
#             'objects': http.request.env['project_workflow_management.project_workflow_management'].search([]),
#         })

#     @http.route('/project_workflow_management/project_workflow_management/objects/<model("project_workflow_management.project_workflow_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('project_workflow_management.object', {
#             'object': obj
#         })
