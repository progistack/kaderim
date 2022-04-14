# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProgisLotQty(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    #_inherit = "stock.production.lot"

    stock_id = fields.Many2one(comodel_name="stock.production.lot")



    def send_mail(self, product, qty, exp_date, email):
        mail_obj = self.env['mail.mail']
        subject = 'Alerte quantité minimum'
        body_html = "<p> L'article <strong>{}</strong> a atteint son minimum <strong>{}</strong> </p>".format(product.name, qty)
        mail = mail_obj.create({
            'subject': subject,
            'qty_min': qty,
            'quantity': product.qty_available,
            'exp_date': exp_date,
            'product_mail_id': product.id,
            'body_html': body_html,
            'email_to': email,
        })
        return mail.send()

    def email_to(self):

        groups = self.env['res.groups'].search([])
        email_list = []

        for group in groups:
            for i in group.users:
                if group.category_id.name == "Stock":
                    email_list.append(i.email)
                else:
                    pass

        email_filter = list(set(email_list))

        return email_filter

    def check_lot_qty(self):
        min_prods = self.env['stock.warehouse.orderpoint'].search([])

        for min_prod in  min_prods:
            if min_prod.product_id.qty_available <= min_prod.product_min_qty:
                print(min_prod.product_id.name,min_prod.product_min_qty)
                for email in self.email_to():
                   self.send_mail(min_prod.product_id, min_prod.product_min_qty, self.stock_id.expiration_date, email)


            






