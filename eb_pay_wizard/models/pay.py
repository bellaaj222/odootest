# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EbMergePays(models.Model):
    _name = 'base.pay.merge.automatic.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(EbMergePays, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids')

        if self.env.context.get('active_model') == 'bon.show' and active_ids:
            res['bon_ids'] = active_ids
        return res

    bon_ids = fields.Many2many('bon.show', string='pays')
    state = fields.Selection([('draft', 'Brouillon'), ('close', 'Validé')])

    def action_pay(self):
        bon_show = self.env['bon.show']
        for bon_id in self.bon_ids.ids:
            bon = bon_show.browse(bon_id)
            res = self.env['bon.show'].search([('employee_id', '=', bon.employee_id.id),
                                               ('type', '=', 'Facture'), ('name', '=', bon.name),
                                               ('state', '=', 'paid')])

            if res:
                raise UserError(_('Action Impossible ! La facture Numéro %s a été déja payée') % bon.name)
            self.env.cr.execute('update bon_show set  state=%s where id = %s', ('paid', bon.id,))
        return True

    def action_treat(self):
        bon_show = self.env['bon.show']
        for bon_id in self.bon_ids.ids:
            bon = bon_show.browse(bon_id)
            res = self.env['bon.show'].search([('employee_id', '=', bon.employee_id.id),
                                               ('type', '=', 'Facture'), ('name', '=', bon.name),
                                               ('state', '=', 'treat')])
            if res:
                raise UserError(_('Action Impossible ! La facture Numéro %s a été déja traitée') % bon.name)
            self.env.cr.execute('update bon_show set  state=%s where id = %s', ('treat', bon.id,))
        return True
