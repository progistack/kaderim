# Copyright © 2018 Garazd Creation (<https://garazd.biz>)
# @author: Yurii Razumovskyi (<support@garazd.biz>)
# @author: Iryna Razumovska (<support@garazd.biz>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class PrintProductLabel(models.TransientModel):
    _name = "print.product.label"
    _description = 'Product Labels Wizard'

    @api.model
    def _get_products(self):
        res = []
        if self._context.get('active_model') == 'product.template':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['print.product.label.line'].create({
                    'product_id': product.product_variant_id.id,
                })
                res.append(label.id)
        elif self._context.get('active_model') == 'product.product':
            products = self.env[self._context.get('active_model')].browse(self._context.get('default_product_ids'))
            for product in products:
                label = self.env['print.product.label.line'].create({
                    'product_id': product.id,
                })
                res.append(label.id)
        return res

    name = fields.Char(
        'Nom',
        default="Imprimer les étiquettes d'articles",
    )
    message = fields.Char(
        'Message',
        readonly=True,
    )
    output = fields.Selection(
        selection=[('pdf', 'PDF')],
        string='Imprimer en',
        default='pdf',
    )
    label_ids = fields.One2many(
        comodel_name='print.product.label.line',
        inverse_name='wizard_id',
        string='Etiquettes des articles',
        default=_get_products,
    )
    template = fields.Selection(
        selection=[
            ('garazd_product_label.report_product_label_A4_57x35',
             'Etiquette 57x35mm (A4: 21 pcs on a sheet, 3x7)')],
        string="Modèle d'étiquette",
        default='garazd_product_label.report_product_label_A4_57x35',
    )
    qty_per_product = fields.Integer(
        string="Quantité d'étiquettes par article",
        default=1,
    )
    # Options
    humanreadable = fields.Boolean(
        string="Code-barres lisible par l'homme",
        help='Imprimer le code numérique du code-barres.',
        default=False,
    )
    border_width = fields.Integer(
        string='Bordure',
        help='Largeur de la bordure des étiquettes (en pixels). Définissez "2" pour aucune bordure.'
    )

    def action_print(self):
        """ Print labels """
        self.ensure_one()
        labels = self.label_ids.filtered('selected').mapped('id')
        if not labels:
            raise Warning(_("Rien à imprimer, définissez la quantité d'étiquettes dans le tableau."))
        return self.env.ref(self.template).with_context(discard_logo_check=True).report_action(labels)

    def action_preview(self):
        """ Preview labels """
        self.ensure_one()
        labels = self.label_ids.filtered('selected').mapped('id')
        if not labels:
            raise Warning(_("Rien à prévisualiser, définissez la quantité d'étiquettes dans le tableau."))
        return self.env.ref('%s_preview' % self.template).with_context(discard_logo_check=True).report_action(labels)

    def action_set_qty(self):
        self.ensure_one()
        self.label_ids.write({'qty': self.qty_per_product})

    def action_restore_initial_qty(self):
        self.ensure_one()
        for label in self.label_ids:
            if label.qty_initial:
                label.update({'qty': label.qty_initial})
