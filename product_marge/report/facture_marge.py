# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class MargeReport(models.AbstractModel):
    _name = 'report.product_marge.details_marge_report_template'
    _description = 'Rapport de marge de ventes'

    @api.model
    def _get_report_values(self, docids, data=None):
        PosOrder = self.env['pos.order'].sudo().search([
            ('company_id', '>=', self.env.company.id),
            ('date_order', '>=', data['start_date']),
            ('date_order', '<=', data['end_date']),
        ])
        periode = f"Du {data['start_date']} au {data['end_date']}"
        compagnie = self.env.company.name
        list_commandes = []
        message = ""
        if not PosOrder:
            message = "Désolé vous n'avez pas de données dans cette période !!!"

            return {
                'message': message,
                'compagnie': compagnie,
                'periode': periode
            }

        else:
            for rec in PosOrder:

                for line in rec.lines:
                    listes = self.env['pos.order.line'].sudo().search([('id', '=', line.id)])
                    for liste in listes:
                        marge_global = liste.unit_marge * liste.qty
                        article_info = {
                            'nom': liste.full_product_name,
                            'prix_unitaire': liste.price_unit,
                            'marge_unitaire': liste.unit_marge,
                            'quantite': liste.qty,
                            'marge_global': marge_global
                        }
                        vef = 0
                        if len(list_commandes) > 0:
                            for i in list_commandes:
                                if article_info['nom'] == i['nom'] and article_info['prix_unitaire'] == i['prix_unitaire']:
                                    i['quantite'] += article_info['quantite']
                                    i['marge_global'] += article_info['marge_global']
                                else:
                                    vef += 1
                        if vef == len(list_commandes):
                            list_commandes.append(article_info)
            return {
                'docs': PosOrder,
                'commande': list_commandes,
                'compagnie': compagnie,
                'periode': periode
            }
