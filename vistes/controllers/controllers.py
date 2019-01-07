# -*- coding: utf-8 -*-
from odoo import http

# class Vistes(http.Controller):
#     @http.route('/vistes/vistes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vistes/vistes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vistes.listing', {
#             'root': '/vistes/vistes',
#             'objects': http.request.env['vistes.vistes'].search([]),
#         })

#     @http.route('/vistes/vistes/objects/<model("vistes.vistes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vistes.object', {
#             'object': obj
#         })