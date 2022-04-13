# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from datetime import timedelta

class ProgisLot(models.Model):
    _inherit = "stock.production.lot"

    #mail_id = fields.Many2one(comodel_name='mail.mail')


    def send_mail_nofresh(self, name, product, exp_date, email, qty):
        mail_obj = self.env['mail.mail']
        subject = "Alerte date d'expiration"
        body_html = "<p> Le lot <strong>{}</strong> de l'article <strong>{}</strong> expire dans 5 semaines. </p>".format(name, product.name)
        mail = mail_obj.create({
            'subject': subject,
            'exp_date': exp_date,
            'qty_min': qty,
            'product_mail_id': product.id,
            'body_html': body_html,
            'email_to':email,
        })
        return mail.send()


    def email_to(self):

        emails = self.env['ir.cron'].search([])

        for email in emails:
            if email.user_id.id == 2:
                return email.user_id.email


    def send_mail_fresh(self, name, product, exp_date, email, qty):
        mail_obj = self.env['mail.mail']
        subject = "Alerte date d'expiration"
        body_html = "<p> Le lot <strong>{}</strong> de l'article <strong>{}</strong> expire dans 2 semaines. </p>".format(name, product.name)
        mail = mail_obj.create({
            'subject': subject,
            'quantity': qty,
            'exp_date': exp_date,
            'product_mail_id': product.id,
            'body_html': body_html,
            'email_to':email,
        })
        return mail.send()


    def check_expiry_lot(self):
        today = fields.Datetime.now()
        lots = self.env['stock.production.lot'].search([])

        for lot in lots:
            if lot.alert_date == False or lot.expiration_date == False:
                pass
            else:
                convert_exp_date = lot.expiration_date.date()
                deadline = today + timedelta(days=35)
                fresh_deadline = today + timedelta(days=14)
                convert_fresh_deadline = fresh_deadline.date()
                convert_deadline = deadline.date()


                if lot.product_id.categ_id == False:
                    pass
                elif lot.product_id.categ_id.fresh == False and convert_exp_date == convert_deadline:
                    self.send_mail_nofresh(lot.name, lot.product_id, lot.expiration_date, self.email_to(), lot.product_qty)

                elif lot.product_id.categ_id.fresh == True and convert_exp_date == convert_fresh_deadline:
                    self.send_mail_fresh(lot.name, lot.product_id, lot.expiration_date, self.email_to(), lot.product_qty)










