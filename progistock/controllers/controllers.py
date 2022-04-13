# -*- coding: utf-8 -*-
# from odoo import http


# class Progistock(http.Controller):
#     @http.route('/progistock/progistock', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/progistock/progistock/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('progistock.listing', {
#             'root': '/progistock/progistock',
#             'objects': http.request.env['progistock.progistock'].search([]),
#         })

#     @http.route('/progistock/progistock/objects/<model("progistock.progistock"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('progistock.object', {
#             'object': obj
#         })
