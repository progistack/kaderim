from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.http import request

PROCUREMENT_PRIORITIES = [('0', 'Normal'), ('1', 'Urgent')]


class DemandeMoveLine(models.Model):
    _name = "demande.move.line"
    _description = "Demande"
    _rec_name = "product_id"
    _order = "demande_id asc, id"
    _check_company_auto = True

    demande_id = fields.Many2one(
        'stock.demande', 'Demande', auto_join=True,
        check_company=True,
        index=True,
        ondelete='cascade',
        help='The stock operation where the packing has been made')
    product_id = fields.Many2one('product.product',
                                 'Product',
                                 check_company=True,
                                 store=True,
                                 ondelete="cascade",
                                 domain="[('type', '!=', 'service'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    product_code = fields.Char(
        related='product_id.code',
        readonly=True)
    product_pdv = fields.Float('PDU TTC',
        related='product_id.list_price',
        readonly=True)
    prix_total = fields.Float('TOTAL TTC', compute="_compte_total_ttc")
    quantite = fields.Float(
        'Nombre de Colis', default=0.0, required=True, copy=False)
    qtc_totale = fields.Float(
        'QTE TOTALE', compute="_compte_total")
    qty_done = fields.Float('Done', default=0.0, digits='Product Unit of Measure', copy=False)
    product_uom = fields.Many2one('uom.uom', "Unité de Mesure", related='product_id.uom_po_id',  readonly=True)
    quantite_en_stock = fields.Float(string="PCB en stock", compute='_compute_quantite_en_stock', readonly=True)
    incoming_qty = fields.Float('PCB Avenir', index=True, compute='_compute_incoming_qty', readonly=True)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, required=True)
    reference = fields.Char(related='demande_id.name', store=True, related_sudo=False, readonly=False)
    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        related='demande_id.company_id',
        readonly=True,
        store=True,
        default=lambda s: s.env.company.id, index=True)

    @api.depends('product_id', 'quantite')
    def _compute_incoming_qty(self):
        for move in self:
            move.incoming_qty = move.quantite_en_stock + move.quantite

    @api.depends('product_id', 'quantite')
    def _compte_total_ttc(self):
        for move in self:
            move.prix_total = move.qtc_totale * move.product_pdv

    @api.depends('product_id', 'quantite')
    def _compte_total(self):
        for move in self:
            move.qtc_totale = move.quantite * move.product_uom.factor_inv

    @api.depends('product_id')
    def _compute_quantite_en_stock(self):
        for move in self:
            product = self.env['product.product'].search([('id', '=', move.product_id.id)])
            move.quantite_en_stock = product.qty_available

    def _compute_quantities(self):
        res = self._compute_quantities_dict()
        for template in self:
            template.qty_available = res[template.id]['qty_available']


class Demande(models.Model):
    _name = "stock.demande"

    name = fields.Char(
        'Reference',
        default='/',
        readonly=True)
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
    company_id = fields.Many2one(
        'res.company', string='Company',
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
        self.state = 'validate'
        base = "BC/"
        ir_sequence = self.env['ir.sequence']
        for rec in self:
            if rec.company_id.street:
                middle = rec.company_id.street[:3].upper() + "/"
            else:
                middle = "CMX"
            next = str(ir_sequence.next_by_code('demande.name'))
            if len(next) == 3:
                next = '0' + next
            elif len(next) == 2:
                next = '00' + next
            elif len(next) == 1:
                next = '000' + next
            rec.name = base + middle + next
        return True

    def action_assign(self):
        for rec in self:
            company_id = rec.company_id
            get_entrepot_centrale = rec.env['res.company'].search([('entrepot_centrale', '=', True)])
            print("###########################################################")
            print("***********************************************************")
            print(get_entrepot_centrale.name)
            print("###########################################################")
            print("***********************************************************")
            get_picking_type = request.env['stock.picking.type'].search([('company_id', '=', get_entrepot_centrale.id),
                                                                     ('code', '=', 'outgoing'),
                                                                     ('entreprise_de_destination_par_defaut', '=', company_id.id)
                                                                     ])
            print("###########################################################")
            print("***********************************************************")
            print(get_picking_type)
            print("###########################################################")
            print("***********************************************************")
            if not get_picking_type:
                raise UserError(_("Impossible de confirmer la commande. Vous devez cocher l'entreprise de l'entrepôt principal"))
            transfert_obj = self.env["stock.picking"]
            pick = {
                "picking_type_id": get_picking_type[0].id,
                "location_id": get_picking_type[0].default_location_src_id.id,
                "location_dest_id": get_picking_type[0].entreprise_de_destination_par_defaut.partner_id.id,
                "partner_id": get_picking_type[0].entreprise_de_destination_par_defaut.partner_id.id,
                "move_ids_without_package": [
                    {
                        'name': rec.name,
                        "location_id": get_picking_type[0].default_location_src_id.id,
                        "location_dest_id": get_picking_type[0].entreprise_de_destination_par_defaut.partner_id.id,
                        'product_id': prod.product_id,
                        'product_uom_qty': prod.quantite,
                        'product_uom': prod.product_uom,
                    } for prod in rec.move_lines
                ],
                "scheduled_date": rec.scheduled_date,
                "origin": rec.name,
            }
            transfert_obj = transfert_obj.create(pick)
            transfert_obj.onchange_partner_id()
            transfert_obj._onchange_picking_type()
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
