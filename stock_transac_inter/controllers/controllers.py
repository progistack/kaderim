# -*- coding: utf-8 -*-
# from odoo import http


# class StockTransacInter(http.Controller):
#     @http.route('/stock_transac_inter/stock_transac_inter/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_transac_inter/stock_transac_inter/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_transac_inter.listing', {
#             'root': '/stock_transac_inter/stock_transac_inter',
#             'objects': http.request.env['stock_transac_inter.stock_transac_inter'].search([]),
#         })

#     @http.route('/stock_transac_inter/stock_transac_inter/objects/<model("stock_transac_inter.stock_transac_inter"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_transac_inter.object', {
#             'object': obj
#         })
