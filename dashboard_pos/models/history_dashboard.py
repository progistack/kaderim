from datetime import datetime, timedelta

import pytz

from odoo import api, fields, models


class HistoryDashboard(models.Model):
    _name = 'history.dashboard'
    _order = 'date DESC'

    order_number = fields.Integer(string='Nombre de Panier')
    amount_total = fields.Float(string="Chiffre d'Affaire")
    cart_moyen = fields.Float(string='panier moyen')
    config_id = fields.Many2one('pos.config', string='Nom', check_company=True)
    date = fields.Date(string='Date')
    company_id = fields.Many2one('res.company', string='Société:', required=True, default=lambda self: self.env.company)

    """pos_config_ids = fields.Many2many('pos.config', 'report_sale_detail',
                                      default=lambda s: s.env['pos.config'].search([]))"""


class InheritPosOderLine(models.Model):
    _inherit = 'pos.order.line'

    date = fields.Date(string='Date', compute='get_order_line_date', store=True, readonly=True)

    @api.depends('create_date')
    def get_order_line_date(self):
        for order_line in self:
            order_line.date = order_line.create_date.date()

    @api.model
    def get_refund_details(self):
        company_id = self.env.company.id
        default_date = datetime.today().date()
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
        a = 0
        query = '''select sum(qty) as total_quantity from pos_order_line where pos_order_line.company_id = ''' + str(
            company_id) + ''' and pos_order_line.date = %(default_date)s '''
        cr = self._cr
        cr.execute(query, {'default_date': default_date})
        data = self._cr.dictfetchall()
        print('eeeeeeehhhhhhhhhhhh ..........', data)
        for val in data:
            total_qty_sell_day = val['total_quantity']
        print('tototoototto', total_qty_sell_day)
        for tot in pos_order_semaine:
            total = total + tot.amount_total
            total_order_count = total_order_count + 1
        for day in pos_order_day:
            print('total day ......', total_day)
            total_day = total_day + day.amount_total
        for rec in pos_order:
            if rec.amount_total < 0.0 and rec.date_order.date() == default_date:
                today_refund_total = today_refund_total + 1
            total_sales = rec.amount_total
            if rec.date_order.date() == default_date:
                today_sale = today_sale + 1
            if rec.amount_total < 0.0:
                total_refund_count = total_refund_count + 1
        total_moyen = total / total_order_count
        magnitude = 0
        magnitude1 = 0
        magnitude2 = 0
        while abs(total) >= 1000:
            magnitude += 1
            total /= 1000.0

        while abs(total_day) >= 1000:
            magnitude1 += 1
            total_day /= 1000.0

        while abs(total_moyen) >= 1000:
            magnitude2 += 1
            total_moyen /= 1000.0

        val1 = '%.2f%s' % (total_day, ['', 'K', 'M', 'G', 'T', 'P'][magnitude1])
        val2 = '%.2f%s' % (total_moyen, ['', 'K', 'M', 'G', 'T', 'P'][magnitude2])
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
            'total_moy': val2
        }


class InheritPosSession(models.Model):
    _inherit = 'pos.session'

    date = fields.Date(string='Date', compute='get_session_date', store=True, readonly=True)

    @api.depends('create_date')
    def get_session_date(self):
        for order_line in self:
            order_line.date = order_line.create_date.date()
