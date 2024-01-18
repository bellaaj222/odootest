# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DebugGest(models.Model):
    _name = 'debug.gest'
    _rec_name = 'reclamation_date'

    def _get_user(self):
        return self.env['res.users'].browse(self.env.uid).employee_id.id

    @api.depends_context('uid')
    def _is_dev(self):
        for record in self:
            record.is_dev = self.env.user.has_group('project_custom.group_dev')

    def _is_affect(self):
        for record in self:
            record.is_affect = self.env['res.users'].browse(self.env.uid).employee_id.id in self.dev_ids.ids

    employee_id = fields.Many2one('hr.employee', 'Employée', default=_get_user)
    dev_ids = fields.Many2many('hr.employee', string='Développeur(s)', readonly=True)
    note_employee = fields.Text('Description', required=True, readonly=True, states={'draft': [('readonly', False)]})
    note_supervisor = fields.Text('Note du Responsable', readonly=True)
    reclamation_date = fields.Date('Date de Réclamation', default=fields.date.today(), readonly=True,
                                   states={'draft': [('readonly', False)]})
    reclamation_type = fields.Selection([
        ('suggest', 'Suggestion'),
        ('fix', "Déclaration d'erreur")
    ], string='Type', required=True, readonly=True, states={'draft': [('readonly', False)]})
    priority = fields.Selection([
        ('low', 'Faible'),
        ('normal', 'Normale'),
        ('urgent', 'Urgent'),
        ('very urgent', 'Très urgent')
    ], string='Priorité', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('waiting', 'En attente'),
        ('allocated', 'Affectée'),
        ('in_progress', 'En cours de Traitement'),
        ('treated', 'Traitée'),
    ], string='Statut', default='draft')
    is_dev = fields.Boolean('Est un Dev', compute='_is_dev')
    is_affect = fields.Boolean('Est affecté', compute='_is_affect')
    attach_ids = fields.Many2many('ir.attachment', string='Pièce(s) Jointe(s)', readonly=True,
                                  states={'draft': [('readonly', False)]})

    def button_send(self):
        self.state = 'waiting'

    def button_affect(self):
        return {
            'name': 'Affectation',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'debug.gest.wizard',
            'view_id': self.env.ref('debug_gest.view_debug_gest_wizard_form').id,
            'context': {'debug_gest_id': self.id},
            'domain': []
        }

    def button_start(self):
        self.state = 'in_progress'

    def button_finish(self):
        self.state = 'treated'


class DebugGestWizard(models.TransientModel):
    _name = 'debug.gest.wizard'

    @api.model
    def default_get(self, fields_list):
        res = super(DebugGestWizard, self).default_get(fields_list)
        debug_gest_id = self.env.context.get('debug_gest_id')
        print(debug_gest_id)
        res.update({'debug_gest_id': debug_gest_id})
        return res

    debug_gest_id = fields.Many2one('debug.gest')
    dev_ids = fields.Many2many('hr.employee', string='Développeur(s)')
    note = fields.Text('Note')

    def action_affect(self):
        self.env['debug.gest'].browse(self.debug_gest_id.id).write({
            'note_supervisor': self.note,
            'dev_ids': [(6, 0, self.dev_ids.ids)],
            'state': 'allocated'
        })
