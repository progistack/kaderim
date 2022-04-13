
from  odoo import fields, models

class ProgisCat(models.Model):
    _inherit = 'product.category'

    fresh = fields.Boolean(string="Catégorie d'articles frais")

