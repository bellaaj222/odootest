from odoo import models, fields, api


class SettingsCustom(models.Model):
    _name = 'settings.custom'
    _description = ''
    _rec_name = "name"

    name = fields.Char(string="Settings custom", required=True, translate=True, default='Settings custom')

    affectation_multiple = fields.Selection([
        ('0', 'Affectation Multiple'),
        ('1', 'Affectation Simple'),
    ], string="Type d'affectation", default='0')
    _sql_constraints = [
        ('unique_settings_custom', 'UNIQUE(name)', 'Only one record allowed in Settings Custom table!')
    ]

    @api.model
    def default_get(self, fields_list):
        defaults = super(SettingsCustom, self).default_get(fields_list)
        existing_record = self.search([], limit=1)
        if existing_record:
            defaults['affectation_multiple'] = existing_record.affectation_multiple
        return defaults
    @api.model
    def create(self, vals):
        existing_record = self.search([], limit=1)
        if existing_record:
            existing_record.write(vals)
            return existing_record
        else:
            return super(SettingsCustom, self).create(vals)

