# -*- coding: utf-8 -*-
# from odoo import http


# class GestionProjet(http.Controller):
#     @http.route('/gestion_projet/gestion_projet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gestion_projet/gestion_projet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gestion_projet.listing', {
#             'root': '/gestion_projet/gestion_projet',
#             'objects': http.request.env['gestion_projet.gestion_projet'].search([]),
#         })

#     @http.route('/gestion_projet/gestion_projet/objects/<model("gestion_projet.gestion_projet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gestion_projet.object', {
#             'object': obj
#         })
