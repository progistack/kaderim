from odoo import api, fields, models, _
from odoo.exceptions import UserError

PROCUREMENT_PRIORITIES = [('0', 'Normal'), ('1', 'Urgent')]


class DemandeType(models.Model):
    _name = "demande.type"
    _description = "Type de Demande"
    _check_company_auto = True

    name = fields.Char("Type d'Opération", required=True, translate=True)
    code = fields.Selection([('reaprovsionnement', 'Réaprovisionnement'), ('Retour', 'Retour')], 'Type of Operation', required=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        check_company=True,
        readonly=True,
        default=lambda s: s.env.company.id, index=True)


class DemandeMoveLine(models.Model):
    _name = "demande.move.line"
    _description = "Demande"
    _rec_name = "product_id"
    _order = "demande_id asc, id"

    demande_id = fields.Many2one(
        'stock.demande', 'Demande', auto_join=True,
        check_company=True,
        index=True,
        ondelete='cascade',
        help='The stock operation where the packing has been made')
    product_id = fields.Many2one('product.product', 'Product', ondelete="cascade")
    product_code = fields.Char(
        related='product_id.code',
        readonly=True)
    quantite = fields.Float(
        'Quantité', default=0.0, required=True, copy=False)
    qty_done = fields.Float('Done', default=0.0, digits='Product Unit of Measure', copy=False)
    product_uom = fields.Many2one('uom.uom', "UoM", required=True, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    reference = fields.Char(related='demande_id.name', store=True, related_sudo=False, readonly=False)
    description_demande = fields.Text(string="Description")
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        related='demande_id.company_id',
        readonly=True,
        default=lambda s: s.env.company.id, index=True)


class Demande(models.Model):
    _name = "stock.demande"

    name = fields.Char(
        'Reference',
        copy=False, index=True, readonly=True)
    origin = fields.Char(
        'Source Document', index=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Numero de référence")
    note = fields.Html('Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Waiting'),
        ('validate', 'Validé'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', copy=False, index=True, store=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    priority = fields.Selection(
        PROCUREMENT_PRIORITIES, string='Priority', default='0',
        help="Products will be reserved first for the transfers with the highest priorities.")
    scheduled_date = fields.Datetime(
        'Scheduled Date', store=True,
        index=True, default=fields.Datetime.now,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.")
    date_deadline = fields.Datetime(
        "Deadline",
        help="Date Promise to the customer on the top level document (SO/PO)")
    date = fields.Datetime(
        'Creation Date',
        default=fields.Datetime.now,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Creation Date, usually the time of the order")
    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=True,
                                help="Date at which the transfer has been processed or cancelled.")
    demande_type_id = fields.Many2one(
        'demande.type', 'Operation Type',
        check_company=True,
        required=True, readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company', related='demande_type_id.company_id',
        store=True,
        default=lambda s: s.env.company.id, index=True,
        readonly=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        check_company=True,
        domain=lambda self: [('groups_id', 'in', self.env.ref('stock.group_stock_user').id)],
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        default=lambda self: self.env.user)
    move_lines = fields.One2many('demande.move.line', 'demande_id', string="Stock Moves")

    def action_confirm(self):
        self.state = 'confirmed'
        return True

    def action_assign(self):
        for rec in self:
            company_id = rec.company_id
            get_picking_type = rec.env['stock.picking.type'].search([('company_id', '=', self.env.user.company_id.id),
                                                                     ('code', '=', 'external'),
                                                                     ('default_location_dest_id.company_id', '=', company_id.id)
                                                                     ])
            transfert_obj = self.env["stock.picking"]
            pick = {
                "picking_type_id": get_picking_type[0].id,
                "location_id": get_picking_type[0].default_location_src_id.id,
                "location_dest_id": get_picking_type[0].default_location_dest_id.id,
                "move_ids_without_package": [
                    {
                        'name': rec.name,
                        "location_id": get_picking_type[0].default_location_src_id.id,
                        "location_dest_id": get_picking_type[0].default_location_dest_id.id,
                        'product_id': prod.product_id,
                        'product_uom_qty': prod.quantite,
                        'product_uom': prod.product_uom,
                    } for prod in rec.move_lines
                ],
                "scheduled_date": rec.scheduled_date,
                "origin": rec.origin,
            }
            transfert_obj.create(pick)
            self.state = 'assigned'
        return True

    def action_cancel(self):
        self.state = 'cancel'
        return True

    def button_validate(self):
        self.state = 'validate'
        return True

    def action_done(self):
        self.state = 'done'
        return True
