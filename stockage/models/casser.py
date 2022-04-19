from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockCasser(models.Model):
    _name = "stockage.casser"
    _description = "Gestion des articles cassés"

    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.company)
    entrepot_id = fields.Many2one('stock.warehouse', string='Emplacement', domain="[('company_id', '=', company_id)]")
    article_cas = fields.Many2one('product.product', 'Article', check_company=True, domain="[('type', '=', 'product')]")
    quantite_cas = fields.Integer(string='Quantité', default=1)
    cause_cas = fields.Char(string='Motif')
    date_cas = fields.Datetime(string='Date', default=fields.Datetime.now)
    status = fields.Boolean(string="Status", default=False)
    status_bar = fields.Selection([('attente', 'En attente'), ('retire', 'Retiré du stock'), ('annule', 'Annulé')], string='Etat',
                                  default='attente')
    reference = fields.Char(string='Référence', required=True, copy=False, readonly=True, index=True,
                            default=lambda self: _('New'))
    nom_compagnie = fields.Char(string="Compagnie", default=lambda self: self.env.company.name)

    def name_get(self):
        result = []
        for article in self:
            name = f'{article.article_cas.name}'
            result.append((article.id, name))
        return result

    # annulation de l'expiration
    def action_annule(self):
        self.status_bar = 'annule'
        self.status = False

    # mise en attente
    def action_attente(self):
        self.status_bar = 'attente'
        self.status = True

    # decremente l'article et cree une ligne de mouvement de stock
    def action_succes(self):
        recherche_entrepot_id = self.env['stock.warehouse'].search([
            ('id', '=', self.entrepot_id.id),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        recherche_artcle = self.env['stock.quant'].search([
            ('product_id', '=', self.article_cas.id),
            ('company_id', '=', self.company_id.id),
            ('location_id', '=', recherche_entrepot_id.lot_stock_id.id)
        ], limit=1)

        if len(recherche_artcle) != 0:
            for i in recherche_artcle:
                if i.product_id.id == self.article_cas.id:

                    # création de mouvement de stock
                    record = self.env['stock.move'].create({
                        'name': f"Perte N°{self.reference} : {self.cause_cas}",
                        'company_id': self.company_id.id,
                        'product_id': self.article_cas.id,
                        'product_uom_qty': float(self.quantite_cas),
                        'location_id': recherche_entrepot_id.lot_stock_id.id,
                        'location_dest_id': 14,
                        'product_uom': 1,
                        'state': 'done',
                        'reference': f"Perte N°{self.reference} : {self.cause_cas}"
                    })

                    # création de mouvement de produit + decrementation
                    recherche_mouvement_stock = self.env['stock.move'].search([
                        ('product_id', '=', self.article_cas.id),
                        ('company_id', '=', self.company_id.id),
                        ('location_id', '=', recherche_entrepot_id.lot_stock_id.id),
                        ('name', '=', f"Perte N°{self.reference} : {self.cause_cas}"),
                        ('product_uom_qty', '=', float(self.quantite_cas))
                    ], limit=1)

                    records = self.env['stock.move.line'].create({
                        'move_id': recherche_mouvement_stock.id,
                        'company_id': self.company_id.id,
                        'product_id': self.article_cas.id,
                        'product_uom_id': 1,
                        'qty_done': float(self.quantite_cas),
                        'location_id': recherche_entrepot_id.lot_stock_id.id,
                        'location_dest_id': 14,
                        'reference': f"Perte N°{self.reference} : {self.cause_cas}"

                    })
            self.status_bar = 'retire'
            self.status = False

    # Recupère les entrepots rattacher a une compagnie
    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            self.entrepot_id = warehouse
            self.nom_compagnie = self.company_id.name
        else:
            self.entrepot_id = False
            self.nom_compagnie = lambda self: self.env.company.name

    @api.model
    def create(self, vals):
        recherche_entrepot_id = self.env['stock.warehouse'].search([
            ('id', '=', vals['entrepot_id']),
            ('company_id', '=', vals['company_id'])
        ], limit=1)

        recherche_artcle = self.env['stock.quant'].search([
            ('product_id', '=', vals['article_cas']),
            ('company_id', '=', vals['company_id']),
            ('location_id', '=', recherche_entrepot_id.lot_stock_id.id)
        ], limit=1)

        # verification de la disponibilité en entrepot
        if len(recherche_artcle) == 0:
            raise ValidationError("Erreur : l'article selectionné n'est pas disponible en stock !!!")
        elif vals['article_cas'] == False or vals['cause_cas'] == False:
            raise ValidationError("Erreur : Veuillez remplir tous les champs s'il vous plait ...")
        else:
            vals['status'] = True

        # génération de numéro de référence
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('casser.reference') or _('New')
        res = super(StockCasser, self).create(vals)
        return res
