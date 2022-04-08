# -*- coding: utf-8 -*-
import logging

import pytz
from odoo import models, fields, api
from datetime import timedelta, datetime, date

_logger = logging.getLogger(__name__)


class PosDashboard(models.Model):
    _inherit = 'pos.order'

    date = fields.Date(string="Date", compute='get_order_date', store=True, readonly=True)

    @api.model
    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        print('777777777',dt_utc)
        return dt_utc.date()

    @api.depends('date_order')
    def get_order_date(self):
        for order in self:
            order.date = order.date_order.date()

    @api.model
    def get_department(self, option):
        company_id = self.env.company.id
        if option == 'pos_hourly_sales':

            user_tz = self.env.user.tz if self.env.user.tz else pytz.UTC
            query = '''select  EXTRACT(hour FROM date_order at time zone 'utc' at time zone '{}') 
                       as date_month,sum(amount_total) from pos_order where  
                       EXTRACT(month FROM date_order::date) = EXTRACT(month FROM CURRENT_DATE) 
                       AND pos_order.company_id = ''' + str(
                company_id) + ''' group by date_month '''
            query = query.format(user_tz)
            label = 'HOURS'
        elif option == 'pos_monthly_sales':
            query = '''select  date_order::date as date_month,sum(amount_total) from pos_order where 
             EXTRACT(month FROM date_order::date) = EXTRACT(month FROM CURRENT_DATE) AND pos_order.company_id = ''' + str(
                company_id) + '''  group by date_month '''
            label = 'DAYS'
        else:
            query = '''select TO_CHAR(date_order,'MON')date_month,sum(amount_total) from pos_order where
             EXTRACT(year FROM date_order::date) = EXTRACT(year FROM CURRENT_DATE) AND pos_order.company_id = ''' + str(
                company_id) + ''' group by date_month'''
            label = 'MONTHS'

        self._cr.execute(query)
        docs = self._cr.dictfetchall()
        order = []
        for record in docs:
            order.append(record.get('sum'))
        today = []
        for record in docs:
            today.append(record.get('date_month'))
        final = [order, today, label]
        return final

    @api.model
    def get_details(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        company_id = self.env.company.id
        cr = self._cr
        cr.execute(
            """select pos_payment_method.name,sum(amount) from pos_payment inner join pos_payment_method on 
            pos_payment_method.id=pos_payment.payment_method_id group by pos_payment_method.name ORDER 
            BY sum(amount) DESC; """)
        payment_details = cr.fetchall()
        cr.execute(
            '''select hr_employee.name,sum(pos_order.amount_paid) as total,count(pos_order.amount_paid) as orders 
            from pos_order inner join hr_employee on pos_order.user_id = hr_employee.user_id 
            where pos_order.date = %(default_date)s GROUP BY hr_employee.name order by total DESC;''', {'default_date': default_date})
        salesperson = cr.fetchall()
        total_sales = []
        for rec in salesperson:
            rec = list(rec)
            sym_id = rec[1]
            company = self.env.company
            if company.currency_id.position == 'after':
                rec[1] = "%s %s" % (sym_id, company.currency_id.symbol)
            else:
                rec[1] = "%s %s" % (company.currency_id.symbol, sym_id)
            rec = tuple(rec)
            total_sales.append(rec)
        cr.execute(
            '''select DISTINCT(product_template.name) as product_name,sum(qty) as total_quantity from 
       pos_order_line inner join product_product on product_product.id=pos_order_line.product_id inner join 
       product_template on product_product.product_tmpl_id = product_template.id  where pos_order_line.company_id =''' + str(
                company_id) + ''' group by product_template.id ORDER 
       BY total_quantity DESC Limit 10 ''')
        selling_product = cr.fetchall()
        sessions = self.env['pos.config'].search([])
        sessions_list = []
        dict = {
            'closing_control': 'Closed',
            'opened': 'Opened',
            'new_session': 'New Session',
            'opening_control': "Opening Control"
        }
        for session in sessions:
            sessions_list.append({
                'session': session.name,
                'status': dict.get(session.pos_session_state)
            })
        payments = []
        for rec in payment_details:
            rec = list(rec)
            sym_id = rec[1]
            company = self.env.company
            if company.currency_id.position == 'after':
                rec[1] = "%s %s" % (sym_id, company.currency_id.symbol)
            else:
                rec[1] = "%s %s" % (company.currency_id.symbol, sym_id)
            rec = tuple(rec)
            payments.append(rec)
        return {
            'payment_details': payments,
            'salesperson': total_sales,
            'selling_product': sessions_list,
        }

    @api.model
    def get_refund_details(self):
        company_id = self.env.company.id
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        last_week_date = default_date - timedelta(days=7)
        pos_order = self.env['pos.order'].search([])
        pos = self.env['pos.order']
        pos_order_semaine = pos.search([('date', '>=', last_week_date), ('date', '<=', default_date)])
        pos_order_day = pos_order.filtered(lambda order: order.date == default_date)
        print('request -------', pos_order_day)
        total = 0
        total_day = 0
        today_refund_total = 0
        total_order_count = 0
        total_refund_count = 0
        today_sale = 0
        total_moyen = 0
        total_qty_sell_day = 0
        qty_my_client = 0
        price_my_product = 0
        a = 0
        query = '''select sum(qty) as total_quantity from pos_order_line where pos_order_line.date = %(default_date)s
        ORDER BY total_quantity'''
        cr = self._cr
        cr.execute(query, {'default_date': default_date})
        print('dddddddddddddddd', query)
        data = self._cr.dictfetchall()
        _logger.info('default date -----------------%s', default_date)
        for val in data:
            if val['total_quantity']:
                total_qty_sell_day = val['total_quantity']
        for tot in pos_order_semaine:
            total = total + tot.amount_total
            total_order_count = total_order_count + 1
        for day in pos_order_day:
            total_day = total_day + day.amount_total
        for rec in pos_order:
            if rec.amount_total < 0.0 and rec.date_order.date() == default_date:
                today_refund_total = today_refund_total + 1
            total_sales = rec.amount_total
            if rec.date_order.date() == default_date:
                today_sale = today_sale + 1
            if rec.amount_total < 0.0:
                total_refund_count = total_refund_count + 1
        if total_order_count > 0:
            total_moyen = total / total_order_count
        if total_qty_sell_day > 0:
            qty_my_client = total_qty_sell_day / today_sale
            price_my_product = total_day / total_qty_sell_day
        magnitude = 0
        magnitude1 = 0
        magnitude2 = 0
        magnitude3 = 0
        magnitude4 = 0
        magnitude5 = 0
        while abs(total) >= 1000:
            magnitude += 1
            total /= 1000.0

        while abs(total_day) >= 1000:
            magnitude1 += 1
            total_day /= 1000.0

        while abs(total_moyen) >= 1000:
            magnitude2 += 1
            total_moyen /= 1000.0

        while abs(total_qty_sell_day) >= 1000:
            magnitude3 += 1
            total_qty_sell_day /= 1000.0
        while abs(price_my_product) >= 1000:
            magnitude4 += 1
            price_my_product /= 1000.0
        while abs(qty_my_client) >= 1000:
            magnitude5 += 1
            qty_my_client /= 1000.0

        val1 = '%.2f%s' % (total_day, ['', 'K', 'M', 'G', 'T', 'P'][magnitude1])
        val2 = '%.2f%s' % (total_moyen, ['', 'K', 'M', 'G', 'T', 'P'][magnitude2])
        val3 = '%.2f%s' % (total_qty_sell_day, ['', 'K', 'M', 'G', 'T', 'P'][magnitude3])
        val4 = '%.2f%s' % (price_my_product, ['', 'K', 'M', 'G', 'T', 'P'][magnitude4])
        val5 = '%.2f%s' % (qty_my_client, ['', 'K', 'M', 'G', 'T', 'P'][magnitude5])
        # add more suffixes if you need them
        val = '%.2f%s' % (total, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
        print('val val', val)
        pos_session = self.env['pos.session'].search([('create_date', '>=', default_date)])
        total_session = 0
        for record in pos_session:
            total_session = total_session + 1
        return {
            'total_sale': val,
            'total_order_count': total_order_count,
            'total_refund_count': total_refund_count,
            'total_session': total_session,
            'today_refund_total': today_refund_total,
            'today_sale': today_sale,
            'amount_today': val1,
            'total_moy': val2,
            'total_qty_sell_day': val3,
            'qty_my_client': val5,
            'price_my_product': val4
        }

    @api.model
    def get_the_top_customer(self, ):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        company_id = self.env.company.id
        query = '''select res_partner.name as customer,pos_order.partner_id,sum(pos_order.amount_paid) as amount_total from pos_order 
        inner join res_partner on res_partner.id = pos_order.partner_id where pos_order.date = %(default_date)s GROUP BY pos_order.partner_id,
        res_partner.name  ORDER BY amount_total  DESC LIMIT 10;'''
        self._cr.execute(query, {'default_date': default_date})
        docs = self._cr.dictfetchall()
        print(docs)

        order = []
        for record in docs:
            order.append(record.get('amount_total'))
        day = []
        for record in docs:
            day.append(record.get('customer'))
        final = [order, day]
        self.get_pos_information_day()
        _logger.info('-----------------------------return function **************** -----------------%s', self.get_pos_information_day())
        return final

    @api.model
    def get_the_top_products(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        company_id = self.env.company.id

        query = '''select DISTINCT(product_template.name) as product_name,sum(qty) as total_quantity from 
        pos_order_line inner join product_product on product_product.id=pos_order_line.product_id inner join 
        product_template on product_product.product_tmpl_id = product_template.id where pos_order_line.date = %(default_date)s group by product_template.id ORDER BY total_quantity DESC Limit 10 '''

        self._cr.execute(query, {'default_date': default_date})
        top_product = self._cr.dictfetchall()

        total_quantity = []
        for record in top_product:
            # if record.get('total_quantity') != 0:
            #     print(total_quantity.append(record.get('total_quantity')))
            total_quantity.append(record.get('total_quantity'))
        product_name = []
        for record in top_product:
            product_name.append(record.get('product_name'))
        final = [total_quantity, product_name]
        return final

    @api.model
    def get_the_top_categories(self):
        company_id = self.env.company.id
        query = '''select DISTINCT(product_category.complete_name) as product_category,sum(qty) as total_quantity 
        from pos_order_line inner join product_product on product_product.id=pos_order_line.product_id  inner join 
        product_template on product_product.product_tmpl_id = product_template.id inner join product_category on 
        product_category.id =product_template.categ_id where pos_order_line.company_id = ''' + str(
            company_id) + ''' group by product_category ORDER BY total_quantity DESC '''
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        for record in top_product:
            total_quantity.append(record.get('total_quantity'))
        product_categ = []
        for record in top_product:
            product_categ.append(record.get('product_category'))
        final = [total_quantity, product_categ]

        return final

    def create_liste(self, vals, date):

        pos_order = self.env['pos.order'].search([('date', '=', date)])

        if pos_order:
            pos_order.write(vals)
        else:
            pos_order.create(vals)

    def get_pos_information_day(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        default_date = dt_utc.date()
        company_id = self.env.company.id
        pan_moy = 0
        query = '''select sum(pos_order.amount_paid) as amount_total,count(pos_order.id) as order_number,
        pos_session.config_id from pos_order inner join pos_session on pos_order.session_id = pos_session.id where 
        pos_order.date = %(default_date)s GROUP BY pos_session.config_id ORDER BY amount_total DESC'''

        self._cr.execute(query, {'default_date': default_date})
        data = self._cr.dictfetchall()
        print('------------------***************+++++++++++++++++', data)
        _logger.info('default data**************** -----------------%s', data)
        for val in data:
            if val['order_number'] > 0:
                pan_moy = val['amount_total'] / val['order_number']
            val.update({'cart_moyen': pan_moy})
            line = self.env['history.dashboard'].search([('config_id', '=', val['config_id']),
                                                         ('date', '=', default_date)])
            if line:
                line.sudo().write(val)
            else:
                val.update({'date': default_date})
                self.env['history.dashboard'].sudo().create(val)
