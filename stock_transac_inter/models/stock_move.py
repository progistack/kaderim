from odoo import fields, models, api


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        auto_join=True, index=True, required=True,
        check_company=False,
        help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    product_pdv = fields.Float('PDU TTC',
                               related='product_id.list_price',
                               readonly=True)
    prix_total = fields.Float('TOTAL TTC', compute="_compte_total_ttc")
    product_uom_qty = fields.Float(
        'Nombre de Colis', default=0.0, required=True)
    qtc_totale = fields.Float(
        'QTE TOTALE', compute="_compte_total")
    product_uom = fields.Many2one('uom.uom', "Unité de Mesure", related='product_id.uom_po_id', readonly=True)
    quantite_en_stock = fields.Float(string="PCB en stock", compute='_compute_quantite_en_stock', readonly=True)
    incoming_qty = fields.Float('PCB Avenir', index=True, compute='_compute_incoming_qty',
                                readonly=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=True,
        check_company=False,
        help="Location where the system will stock the finished products.")


    @api.depends('product_id', 'product_uom_qty')
    def _compute_incoming_qty(self):
        for move in self:
            move.incoming_qty = move.quantite_en_stock + move.product_uom_qty

    @api.depends('product_id', 'product_uom_qty')
    def _compte_total_ttc(self):
        for move in self:
            move.prix_total = move.qtc_totale * move.product_pdv

    @api.depends('product_id', 'product_uom_qty')
    def _compte_total(self):
        for move in self:
            move.qtc_totale = move.product_uom_qty * move.product_uom.factor_inv

    @api.depends('product_id')
    def _compute_quantite_en_stock(self):
        for move in self:
            product = self.env['product.product'].search([('id', '=', move.product_id.id)])
            move.quantite_en_stock = product.qty_available

    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']
