# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import time
from ast import literal_eval
from datetime import date, timedelta
from itertools import groupby
from operator import attrgetter, itemgetter
from collections import defaultdict

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import format_date


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer'), ('external', 'Transfert Inter-Entreprise')], 'Type of Operation', required=True)


class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_dest_id,
        check_company=False, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

    @api.onchange('picking_type_id')
    def _onchange_picking_type_change_destination(self):
        """ Change possible transfert destination when picking type is external transfert"""
        availible_domaines = {}
        if self.picking_type_id.code == 'external':
            availible_domaines = {'domain': {
                                    'location_dest_id': [('company_id', '!=', False), ('company_id', '!=', self.env.company.id), ('usage', '=', "internal")],
                                    'location_id': [('company_id', '!=', False),('usage', 'in', ('internal', 'production', 'supplier'))],
                                }
            }
        return availible_domaines

    def action_confirm(self):
        print("################################################################################################")
        print(self.picking_type_id.code)
        print(self.name)
        print(self.origin)
        print(self.note)
        print(self.move_type)
        print(self.state)
        print(self.priority)
        print(self.scheduled_date)
        print(self.date_deadline)
        print(self.date)
        print(self.location_id)
        print(self.location_dest_id)
        print(self.move_lines)
        print(self.move_ids_without_package)
        print(self.company_id)
        print("################################################################################################")


        self._check_company()
        print("**************************************")
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        print('+++++++++++++++++++++++++++++++++++++++++++++')
        # call `_action_confirm` on every draft move
        if self.picking_type_id.code == 'external':

            print("################################################################################################")
            print("################################################################################################")
            print("################################################################################################")

        self.mapped('move_lines')\
        .filtered(lambda move: move.state == 'draft')\
        ._action_confirm()
        print('----------------------------------------------------')

        # run scheduler for moves forecasted to not have enough in stock
        self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        return True
