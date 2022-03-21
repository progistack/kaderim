from collections import defaultdict
from datetime import timedelta
from itertools import groupby
from odoo.tools import groupby as groupbyelem
from operator import itemgetter

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.tools.misc import clean_context, OrderedSet


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    location_dest_id = fields.Many2one(
    'stock.location', 'Destination Location',
    auto_join=True, index=True, required=True,
    check_company=False,
    help="Location where the system will stock the finished products.")
