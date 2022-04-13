# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProgisLotQty(models.Model):
    _inherit = "stock.production.lot"


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

        emails = self.env['ir.cron'].search([])

        for email in emails:
            if email.user_id.id == 2:
                return email.user_id.email

    def check_lot_qty(self):
        min_prods = self.env['stock.warehouse.orderpoint'].search([])
        products = self.env['stock.production.lot'].search([])


        for product in products:
            for min_prod in  min_prods:
                if product.product_id.qty_available <= min_prod.product_min_qty:
                    self.send_mail(product.product_id, min_prod.product_min_qty, product.expiration_date, self.email_to())


            






