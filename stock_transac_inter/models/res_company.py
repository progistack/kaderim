import logging
from odoo import api, fields, models, tools, _, Command

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = "res.company"

    entrepot_centrale = fields.Boolean(default=False, string="Est l'entrepôt centrale")