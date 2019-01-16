# -*- coding: utf-8 -*-
from odoo import http

# class Wizards(http.Controller):
#     @http.route('/wizards/wizards/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/wizards/wizards/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('wizards.listing', {
#             'root': '/wizards/wizards',
#             'objects': http.request.env['wizards.wizards'].search([]),
#         })

#     @http.route('/wizards/wizards/objects/<model("wizards.wizards"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('wizards.object', {
#             'object': obj
#         })