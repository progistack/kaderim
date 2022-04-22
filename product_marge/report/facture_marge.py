# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class MargeReport(models.AbstractModel):
    _name = 'report.product_marge.details_marge_report_template'
    _description = 'Rapport de marge de ventes'

    @api.model
    def _get_report_values(self, docids, data=None):
        PosOrder = self.env['pos.order']
        print('DATA ===', data)
        print('POST ===', PosOrder)
