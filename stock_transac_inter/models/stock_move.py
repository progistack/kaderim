from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True,
        check_company=False,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")

    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=True,
        check_company=False,
        help="Location where the system will stock the finished products.")