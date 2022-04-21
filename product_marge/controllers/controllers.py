# -*- coding: utf-8 -*-
# from odoo import http


# class ProductMarge(http.Controller):
#     @http.route('/product_marge/product_marge/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_marge/product_marge/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_marge.listing', {
#             'root': '/product_marge/product_marge',
#             'objects': http.request.env['product_marge.product_marge'].search([]),
#         })

#     @http.route('/product_marge/product_marge/objects/<model("product_marge.product_marge"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_marge.object', {
#             'object': obj
#         })
