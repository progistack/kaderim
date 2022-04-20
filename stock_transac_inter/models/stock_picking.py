from odoo.http import request
from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class PickingType(models.Model):
    _inherit = "stock.picking.type"
    _check_company_auto = False

    default_location_src_id = fields.Many2one(
        'stock.location', 'Default Source Location',
        check_company=False,
        help="This is the default source location when you create a picking manually with this operation type. It is possible however to change it or that the routes put another location. If it is empty, it will check for the supplier location on the partner. ")

    default_location_dest_id = fields.Many2one(
        'stock.location', 'Default Destination Location',
        check_company=False,
        help="This is the default destination location when you create a picking manually with this operation type. It is possible however to change it or that the routes put another location. If it is empty, it will check for the customer location on the partner. ")
    entreprise_de_destination_par_defaut = fields.Many2one(
        'res.company', 'Entreprise de Destination')


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
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        check_company=False,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

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

    def action_confirm(self):

        self._check_company()
        print("**************************************")
        self.mapped('package_level_ids').filtered(lambda pl: pl.state == 'draft' and not pl.move_ids)._generate_moves()
        print('+++++++++++++++++++++++++++++++++++++++++++++')
        # call `_action_confirm` on every draft move
        print(self.picking_type_id.code, self.picking_type_id.entreprise_de_destination_par_defaut)
        if self.picking_type_id.code == 'outgoing' and self.picking_type_id.entreprise_de_destination_par_defaut:
            print("##########################################")
            for rec in self:
                print("##########################################")
                company_id = rec.company_id
                print("##########################################")
                get_picking_type = request.env['stock.picking.type'].search(
                    [('company_id', '=', rec.picking_type_id.entreprise_de_destination_par_defaut.id),
                     ('code', '=', 'incoming'),
                     ('name', '=', 'Réceptions'),
                     ])
                print("##########################################")
                print(get_picking_type)
                incomming_obj = self.env["stock.picking"]
                pick = {
                    "picking_type_id": get_picking_type[0].id,
                    "location_dest_id": rec.location_dest_id.id,
                    "location_id": rec.location_id.company_id.partner_id.id,
                    "partner_id": rec.location_id.company_id.partner_id.id,
                    "move_ids_without_package": [
                        {
                            'name': rec.name,
                            "location_id": rec.location_id.id,
                            "company_id": rec.location_id.company_id.id,
                            "location_dest_id": rec.location_dest_id.id,
                            "partner_id": rec.location_id.company_id.partner_id.id,
                            'product_id': prod.product_id,
                            'product_uom_qty': prod.product_uom_qty,
                            'product_uom': prod.product_uom
                        } for prod in rec.move_ids_without_package
                    ],
                    "scheduled_date": rec.scheduled_date,
                    "origin": rec.origin,
                }
                incomming_obj = incomming_obj.create(pick)
                incomming_obj.onchange_partner_id()
                incomming_obj._onchange_picking_type()

        self.mapped('move_lines')\
        .filtered(lambda move: move.state == 'draft')\
        ._action_confirm()

        # run scheduler for moves forecasted to not have enough in stock
        self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))._trigger_scheduler()
        return True

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if self.env.company.entrepot_centrale:
                if pickings_without_lots:
                    message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (
                    ', '.join(pickings_without_lots.mapped('name')),
                    ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        if self.user_has_groups('stock.group_reception_report') \
                and self.user_has_groups('stock.group_auto_reception_report') \
                and self.filtered(lambda p: p.picking_type_id.code != 'outgoing'):
            lines = self.move_lines.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
            if lines:
                # don't show reception report if all already assigned/nothing to assign
                wh_location_ids = self.env['stock.location']._search([('id', 'child_of', self.picking_type_id.warehouse_id.view_location_id.id), ('usage', '!=', 'supplier')])
                if self.env['stock.move'].search([
                        ('state', 'in', ['confirmed', 'partially_available', 'waiting', 'assigned']),
                        ('product_qty', '>', 0),
                        ('location_id', 'in', wh_location_ids),
                        ('move_orig_ids', '=', False),
                        ('picking_id', 'not in', self.ids),
                        ('product_id', 'in', lines.product_id.ids)], limit=1):
                    action = self.action_view_reception_report()
                    action['context'] = {'default_picking_ids': self.ids}
                    return action
        return True
