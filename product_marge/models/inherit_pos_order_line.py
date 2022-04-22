from odoo import fields, api, models


class InheritPosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    unit_marge = fields.Float(string='Marge unitaire', compute='get_marge_unit')

    @api.depends('qty')
    def get_marge_unit(self):
        for lin in self:
            mu = 0
            if lin.qty != 0:
                mu += lin.margin / lin.qty
                lin.unit_marge = mu


class InheritPosOrder(models.Model):
    _inherit = 'pos.order'

    total_marge = fields.Float(string='Marge globale', digits=0, compute='get_marge_total')
    marge_command = fields.Monetary(string='Marge commande', compute='get_marge_command')

    @api.depends('amount_total')
    def get_marge_total(self):
        marge = 0
        for order in self:
            for line in order.lines:
                marge += line.margin
            order.total_marge = marge

    @api.depends('amount_total')
    def get_marge_command(self):

        for order in self:
            marge = 0
            for line in order.lines:
                marge += line.margin
            order.marge_command = marge