
from odoo import fields, models

class ProductLog(models.Model):
    _inherit = 'mail.mail'


    product_mail_id = fields.Many2one(comodel_name='product.product', string='Article')
    exp_date = fields.Date(string="Date d'expiration")
    qty_min = fields.Float(string="Seuil d'alerte")
    quantity = fields.Float(string="Quantité")
    warehouse_id = fields.Many2one(comodel_name='stock.warehouse')

    def action_product_forecast_report(self):
        self.ensure_one()
        action = self.product_mail_id.action_product_forecast_report()
        action['context'] = {
            'active_id': self.product_mail_id.id,
            'active_model': 'product.product',
        }
        warehouse = self.warehouse_id
        if warehouse:
            action['context']['warehouse'] = warehouse.id
        return action







