# -*- coding: utf-8 -*-
from odoo import http

# class Proves1(http.Controller):
#     @http.route('/proves1/proves1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/proves1/proves1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('proves1.listing', {
#             'root': '/proves1/proves1',
#             'objects': http.request.env['proves1.proves1'].search([]),
#         })

#     @http.route('/proves1/proves1/objects/<model("proves1.proves1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('proves1.object', {
#             'object': obj
#         })