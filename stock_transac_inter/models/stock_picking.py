from odoo import SUPERUSER_ID, _, api, fields, models


class PickingType(models.Model):
    _inherit = "stock.picking.type"

    code = fields.Selection([('incoming', 'Receipt'), ('outgoing', 'Delivery'), ('internal', 'Internal Transfer'), ('external', 'Transfert Inter-Entreprise')],
                            'Type of Operation', required=True)
    default_location_dest_id = fields.Many2one(
        'stock.location', 'Default Destination Location',
        check_company=False,
        help="This is the default destination location when you create a picking manually with this operation type. It is possible however to change it or that the routes put another location. If it is empty, it will check for the customer location on the partner. ")


class Picking(models.Model):
    _name = "stock.picking"
    _inherit = "stock.picking"

    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(
            self._context.get('default_picking_type_id')).default_location_src_id,
        check_company=False, readonly=True, required=True,
        states={'draft': [('readonly', False)]})

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

        self._check_company()
        print("**************************************")
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        print('+++++++++++++++++++++++++++++++++++++++++++++')
        # call `_action_confirm` on every draft move
        if self.picking_type_id.code == 'external':
            for rec in self:
                company_id = rec.company_id
                get_picking_type = rec.env['stock.picking.type'].search(
                    [('company_id', '=', rec.location_dest_id.company_id.id),
                     ('default_location_dest_id', '=', rec.location_dest_id.id),
                     ('code', '=', 'incoming')
                     ])
                incomming_obj = self.env["stock.picking"]
                print("###################", get_picking_type, rec.location_dest_id.id)
                pick = {
                    "picking_type_id": get_picking_type[0].id,
                    "location_dest_id": rec.location_dest_id.id,
                    "location_id": rec.location_id.company_id.id,
                    "partner_id": rec.location_id.company_id.id,
                    "move_ids_without_package": [
                        {
                            'name': rec.name,
                            "location_id": rec.location_id.company_id.id,
                            "location_dest_id": rec.location_dest_id.id,
                            'product_id': prod.product_id,
                            'product_uom_qty': prod.product_uom_qty,
                            'product_uom': prod.product_uom,
                        } for prod in rec.move_ids_without_package
                    ],
                    "scheduled_date": rec.scheduled_date,
                    "origin": rec.origin,
                }
                incomming_obj.create(pick)
        self.mapped('move_lines')\
        .filtered(lambda move: move.state == 'draft')\
        ._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        return True