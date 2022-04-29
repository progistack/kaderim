from odoo import fields, models, api


class MargeDetailWizard(models.TransientModel):
    _name = "marge.detail.wizard"
    _description = "Marge Detail Wizard"

    start_date = fields.Datetime(string="Date de début", required=True, default=fields.Datetime.now)
    end_date = fields.Datetime(string="Date de fin", required=True, default=fields.Datetime.now)
    pos_config_ids = fields.Many2many('pos.config', 'report_detail_marge',
                                      default=lambda s: s.env['pos.config'].search([]))

    @api.onchange('start_date')
    def _onchange_start_date(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            self.end_date = self.start_date

    @api.onchange('end_date')
    def _onchange_end_date(self):
        if self.end_date and self.end_date < self.start_date:
            self.start_date = self.end_date

    def generate_report(self):
        data = {'start_date': self.start_date, 'end_date': self.end_date, 'config_ids': self.pos_config_ids.ids}
        return self.env.ref('product_marge.detail_marge_report').report_action([], data=data)
