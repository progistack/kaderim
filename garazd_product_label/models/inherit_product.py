from odoo import fields, api, models


class InheritProduct(models.Model):
    _inherit = 'product.product'

    date = fields.Date(string='Date', compute='get_update_price_date')

    @api.depends('create_date')
    def get_update_price_date(self):
        data = self.env['product.product'].search([])
        for val in data:
            val.date = val.create_date
