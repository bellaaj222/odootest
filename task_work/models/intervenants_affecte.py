from odoo import models, fields, api
from datetime import datetime as dt
from odoo.exceptions import UserError
from odoo.tools.translate import _
import math


class IntervenantsAffect(models.Model):
    _name = 'intervenants.affect'
    _description = 'intervenants affectés à la production'
    _rec_name = 'id'

    # Chaque classe a une relation many2one avec project_task_work et permet de stocker
    # l'id de l'employé, son nom, le statut (non traité, ou traité), date affectation, et date D.B.

    name = fields.Char('name')
    # employee_id = fields.Integer('Employee')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    state = fields.Selection([
        ('actif', 'Actif'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('cancelled', 'Annulée'),
    ], string='Statut', default='actif')

    date_affectation = fields.Date('Date affectation')
    date_declaration_bon = fields.Date('Date Declaration')
    task_work_id = fields.Many2one('project.task.work', 'Task Work')
    types_affect = fields.Selection([
        ('intervenant', 'Production'),
        ('controle', 'Contrôle'),
        ('correction', 'Correction')
    ], string="Type d'affectation", default='intervenant')
    invoice_id = fields.Integer('Invoices ID')
    _group_by_default = {'types_affect': 'true'}

    def button_cancel(self):
        vv = []
        work = self.env['project.task.work'].browse(self.task_work_id.id)
        if work.kit_id:
            kit_list = self.env['project.task.work'].search([
                ('project_id', '=', work.project_id.id),
                ('zone', '=', work.zone),
                ('secteur', '=', work.secteur),
                ('kit_id', '=', work.kit_id.id),
                ('product_id.name', 'not ilike', '%correction%'),
                ('product_id.name', 'not ilike', '%cont%'),
                ('product_id.name', 'not ilike', '%gestion client%')
            ])
            for kit_list_id in kit_list.ids:
                work1 = self.env['project.task.work'].browse(kit_list_id)
                if not work.is_copy:
                    if not work1.is_copy:
                        vv.append(work1.id)
                else:
                    if work1.is_copy is not False:
                        if work.rank == work1.rank:
                            vv.append(work1.id)
        invoice = self.env['base.invoices.merge.automatic.wizard'].browse(self.invoice_id)
        self.env['base.invoices.merge.automatic.wizard'].button_cancel_tree(vv,invoice,self.employee_id)

        view = self.env['sh.message.wizard']
        view_id = view and view.id or False

        return {
            'name': "Annulataion d'affectation faite avec Succès",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }



