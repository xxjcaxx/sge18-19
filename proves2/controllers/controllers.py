# -*- coding: utf-8 -*-
from odoo import http

# class Proves2(http.Controller):
#     @http.route('/proves2/proves2/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/proves2/proves2/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('proves2.listing', {
#             'root': '/proves2/proves2',
#             'objects': http.request.env['proves2.proves2'].search([]),
#         })

#     @http.route('/proves2/proves2/objects/<model("proves2.proves2"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('proves2.object', {
#             'object': obj
#         })