from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class StockExpirer(models.Model):
    _name = "stockage.expirer"
    _description = "Gestion des articles expirés"

    company_id = fields.Many2one('res.company', 'Compagnie', default=lambda self: self.env.company)
    entrepot_id = fields.Many2one('stock.warehouse', string='Emplacement', domain="[('company_id', '=', company_id)]")
    article_exp = fields.Many2one('product.product', 'Article', check_company=True, domain="[('type', '=', 'product')]")
    quantite_exp = fields.Integer(string='Quantité', default=1)
    cause_exp = fields.Char(string='Motif')
    date_exp = fields.Datetime(string='Date', default=fields.Datetime.now)
    status = fields.Boolean(string="Status", default=False)
    status_bar = fields.Selection([('attente', 'En attente'), ('retire', 'Retiré du stock')], string='Etat',
                                  default='attente')
    reference = fields.Char(string='Référence', required=True, copy=False, readonly=True, index=True,
                            default=lambda self: _('New'))
    nom_compagnie = fields.Char(string="Compagnie", default=lambda self: self.env.company.name)

    def name_get(self):
        result = []
        for article in self:
            name = f'{article.article_exp.name}'
            result.append((article.id, name))
        return result

    # decremente l'article et cree une ligne de mouvement de stock
    def message_succes(self):
        recherche_entrepot_id = self.env['stock.warehouse'].search([
            ('id', '=', self.entrepot_id.id),
            ('company_id', '=', self.company_id.id)
        ], limit=1)

        recherche_artcle = self.env['stock.quant'].search([
            ('product_id', '=', self.article_exp.id),
            ('company_id', '=', self.company_id.id),
            ('location_id', '=', recherche_entrepot_id.lot_stock_id.id)
        ], limit=1)

        if len(recherche_artcle) != 0:
            for i in recherche_artcle:
                if i.product_id.id == self.article_exp.id:

                    # décrémentation de la quantité en stock
                    i.quantity -= self.quantite_exp

                    # création de mouvement de stock
                    record = self.env['stock.move'].create({
                        'name': f"Perte N°{self.reference} : {self.cause_exp}",
                        'company_id': self.company_id.id,
                        'product_id': self.article_exp.id,
                        'product_uom_qty': float(self.quantite_exp),
                        'location_id': recherche_entrepot_id.lot_stock_id.id,
                        'location_dest_id': 14,
                        'product_uom': 1,
                        'state': 'done',
                        'reference': f"Perte N°{self.reference} : {self.cause_exp}"
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
            ('product_id', '=', vals['article_exp']),
            ('company_id', '=', vals['company_id']),
            ('location_id', '=', recherche_entrepot_id.lot_stock_id.id)
        ], limit=1)

        # verification de la disponibilité en entrepot
        if len(recherche_artcle) == 0:
            raise ValidationError("Erreur : l'article selectionné n'est pas disponible en stock !!!")
        elif vals['article_exp'] == False or vals['cause_exp'] == False:
            raise ValidationError("Erreur : Veuillez remplir tous les champs s'il vous plait ...")
        else:
            vals['status'] = True

        # génération de numéro de référence
        if vals.get('reference', _('New')) == _('New'):
            vals['reference'] = self.env['ir.sequence'].next_by_code('expirer.reference') or _('New')
        res = super(StockExpirer, self).create(vals)
        return res
