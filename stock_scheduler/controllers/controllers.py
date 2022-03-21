# -*- coding: utf-8 -*-
# from odoo import http


# class StockScheduler(http.Controller):
#     @http.route('/stock_scheduler/stock_scheduler/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_scheduler/stock_scheduler/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_scheduler.listing', {
#             'root': '/stock_scheduler/stock_scheduler',
#             'objects': http.request.env['stock_scheduler.stock_scheduler'].search([]),
#         })

#     @http.route('/stock_scheduler/stock_scheduler/objects/<model("stock_scheduler.stock_scheduler"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_scheduler.object', {
#             'object': obj
#         })
