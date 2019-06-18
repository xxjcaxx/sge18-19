# -*- coding: utf-8 -*-
from odoo import http

# class Reserves(http.Controller):
#     @http.route('/reserves/reserves/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reserves/reserves/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reserves.listing', {
#             'root': '/reserves/reserves',
#             'objects': http.request.env['reserves.reserves'].search([]),
#         })

#     @http.route('/reserves/reserves/objects/<model("reserves.reserves"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reserves.object', {
#             'object': obj
#         })