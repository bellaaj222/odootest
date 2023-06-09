from datetime import datetime, date
from odoo import models, fields, api
from odoo.tools.translate import _


class MergeflowsLine(models.Model):
    _name = 'base.flow.merge.line'
    _order = 'min_id asc'

    wizard_id = fields.Many2one('base.flow.merge.automatic.wizard', string='Wizard')

    min_id = fields.Integer(string='Wizard')
    # aggr_ids = fields.Char('Ids', required=True)
    line_id = fields.Many2one('project.task.work.line', string='Wizard')
    project_id = fields.Many2one('project.project', string='Wizard')
    task_id = fields.Many2one('project.task', string='Wizard')
    work_id = fields.Many2one('project.task.work', string='Wizard')
    date_start_r = fields.Date('Date')
    date_end_r = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', string='Wizard')
    gest_id = fields.Many2one('hr.employee', string='Wizard')
    hours_r = fields.Float('Time Spent')
    total_t = fields.Float('Time Spent')
    total_r = fields.Float('Time Spent')
    poteau_t = fields.Integer('Time Spent')
    poteau_r = fields.Integer('Time Spent')
    wage = fields.Float('Time Spent')
    amount_line = fields.Float('Time Spent')
    poteau_reste = fields.Integer('Time Spent')
    sequence = fields.Integer('Sequence')

    zone = fields.Integer('Color Index')
    secteur = fields.Integer('Color Index')
    state = fields.Selection([
        ('draft', 'T. Planifiés'),
        ('affect', 'T. Affectés'),
        ('tovalid', 'T. Réalisés'),
        ('affect_con', 'T. Affectés controle'),
        ('affect_corr', 'T. Affectés corrction'),

        ('validcont', 'Controle Validée'),
        ('tovalidcorrec', 'Correction Encours'),
        ('tovalidcont', 'Controle Encours'),
        ('validcorrec', 'Correction Validée'),
        ('valid', 'T. Tarminées'),
        ('paid', 'Factures Approuvées'),
        ('cancel', 'T. Annulés'),
        ('pending', 'T. Suspendus'),
        ('close', 'Traité')
    ],
        'Status', copy=False)
    note = fields.Text('Work summary')
    done = fields.Boolean('is done')
    color1 = fields.Integer('Nbdays')

    uom_id_r = fields.Many2one('product.uom', string='Wizard')


class EbMergeflows(models.Model):
    _name = "base.flow.merge.automatic.wizard"
    _description = "Merge flows"
    _rec_name = 'name'

    @api.depends('done')
    def _get_current_user(self):
        for record in self:
            user = self.env.user
            record.current_user = user.id

    @api.model
    def _amount_all(self):
        tax_obj = self.env['account.tax']

        tvp_obj = tax_obj.browse(8)
        tps_obj = tax_obj.browse(7)
        for flow in self:
            flow.amount_untaxed = 0
            flow.amount_tps = 0
            flow.amount_tvq = 0
            flow.amount_total = 0

            if flow.employee_id.job_id.id == 1:
                tvq = 0
                tps = 0
            else:
                tvq = tvp_obj.amount
                tps = tps_obj.amount

            for line in flow.line_ids:
                flow.amount_untaxed += line.amount_line

            flow.amount_tps = flow.amount_untaxed * tps
            flow.amount_tvq = flow.amount_untaxed * tvq
            flow.amount_total = flow.amount_untaxed + flow.amount_tps + flow.amount_tvq

    current_user = fields.Many2one('res.users', compute='_get_current_user')
    gest_id = fields.Many2one('hr.employee', string='Wizard')
    work_ids = fields.Many2many('project.task.work', string='flows', readonly=True,
                                states={'draft': [('readonly', False)]}, )
    user_id = fields.Many2one('res.users', string='Assigned')
    dst_work_id = fields.Many2one('project.task.work', string='Destination Task')
    dst_project = fields.Many2one('project.project', string="Project")
    link_ids = fields.One2many('link.line', 'flow_id', string="Work done", readonly=True,
                               states={'draft': [('readonly', False)]}, )
    attach_ids = fields.Many2many('ir.attachment', 'ir_attach_rel', 'flow_id', 'attachment_id', string="Attachments",
                                  help="If any")
    line_ids = fields.One2many(
        'base.flow.merge.line', 'wizard_id', string=u"Role lines", copy=True,
        states={'draft': [('readonly', False)]}, )
    time_ch = fields.Char(string='Temps de gestion')
    project_id = fields.Many2one('project.project', string='Wizard')
    task_id = fields.Many2one('project.task', string='task_id')
    work_id = fields.Many2one('project.task.work', string='work_id')
    pay_id = fields.Many2one('hr.payslip', string='Wizard')
    date_start_r = fields.Date(string='date_start_r')
    date_end_r = fields.Date(string='date_end_r')
    employee_id = fields.Many2one('hr.employee', string='employee_id')
    employee_id2 = fields.Many2one('hr.employee', string='Assigned')
    hours_r = fields.Float(string='hours_r')
    total_t = fields.Float(string='total_t')
    total_r = fields.Float(string='total_r')
    poteau_t = fields.Float(string='poteau_t')
    poteau_r = fields.Float(string='poteau_r')
    poteau_reste = fields.Float(string='poteau_reste')
    sequence = fields.Integer(string='sequence')
    zone = fields.Integer(string='zone', readonly=True, states={'draft': [('readonly', False)]}, default=99)
    secteur = fields.Integer(string='secteur', readonly=True, states={'draft': [('readonly', False)]}, default=99)
    zo = fields.Char(string='zo', readonly=True, states={'draft': [('readonly', False)]}, )
    sect = fields.Char(string='sect')
    name = fields.Char(string='name', default='Actions Workflow')
    state = fields.Selection([('draft', 'Actions Brouillons'),
                              ('affect', 'Actions Validées'),
                              ('tovalid', 'Validaion Super.'),
                              ('valid', 'Factures Br.'),
                              ('paid', 'Factures Val.'),
                              ('cancel', 'T. Annulés'),
                              ('pending', 'T. Suspendus'),
                              ('close', 'Traité')], default='draft')
    actions = fields.Selection([('keep', 'Laisser Les Taches Actives (Pas de changement de statut)'),
                                ('permis',
                                 'Terminer Les Taches(Retire les taches du tableau de bord mais reste affichable après recherche)'),
                                ('archiv',
                                 'Archiver Les Taches Sélectionnées(Retire les taches du tableau de bord et de la recherche)'),
                                ('suspend', 'Suspendre Temporairement Les Taches Encours'),
                                ('treated', 'Cloturer Définitivement Les Taches Encours'),
                                ('cancel', 'Annuler Les Taches Encours'),

                                ], readonly=True, states={'draft': [('readonly', False)]}, )
    mail_send = fields.Selection([('yes', 'Oui'),
                                  ('no', 'Non'),

                                  ])

    note = fields.Text(string='Assigned', readonly=True, states={'draft': [('readonly', False)]}, )
    states = fields.Char(string='states')
    ftp = fields.Char(string='ftp')
    dep = fields.Char(string='dep')
    to = fields.Char(string='to')
    cc = fields.Char(string='cc')
    cci = fields.Char(string='cci')
    objet = fields.Char(string='char')
    send = fields.Boolean(string='Envoyer Mail?', readonly=True,
                          states={'draft': [('readonly', False)]}, )  ##, default=_disponible
    done = fields.Boolean(string='Is doctor?', readonly=True,
                          states={'draft': [('readonly', False)]}, )  ##, default=_disponible
    ##doctor = fields.Boolean(string='Is doctor?', default=default_done)
    color1 = fields.Integer(string='Assigned')

    uom_id_r = fields.Many2one('product.uom', string='uom_id_r')
    uom_id = fields.Many2one('product.uom', string='uom_id')
    amount_untaxed = fields.Float(compute='_amount_all', string='amount_untaxed')
    amount_total = fields.Float(compute='_amount_all', string='amount_total')
    amount_tvq = fields.Float(compute='_amount_all', string='amount_tvq')
    amount_tps = fields.Float(compute='_amount_all', string='amount_tps')
    categ_id = fields.Many2one('product.category', string='Wizard', readonly=True,
                               states={'draft': [('readonly', False)]}, )
    employee_ids = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel',
                                    'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                    readonly=True, states={'draft': [('readonly', False)]}, )
    employee_ids1 = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel1',
                                     'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                     readonly=True, states={'draft': [('readonly', False)]}, )
    employee_ids2 = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel2',
                                     'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                     readonly=True, states={'draft': [('readonly', False)]}, )

    # @api.onchange('actions')
    # def onchange_actions(self):
    #     active = self.env.context.get('active_ids', [])
    #     if self.actions == 'permis' or self.actions == 'archiv' or self.actions == 'treated':
    #         for line in active:
    #             work = self.env['project.task.work'].browse(line)
    #             if work.state == 'affect_con' or work.state == 'affect_corr' or work.state == 'affect':
    #                 message = {'title': _('Attention'), 'message': _("Attention la tache: %s est en cours") % work.name}
    #                 return {'warning': message}
    #     return {}


class ProjectTaskWork(models.Model):
    _name = 'project.task.work'

    _description = 'Task Work'
    name = fields.Char(string='Name')
    kit = fields.Char(string='Kit')
    project_id = fields.Many2one('project.project', string='Wizard')
    task_id = fields.Many2one('project.task', string='Wizard')
    kit_id = fields.Char(string='Kit')
    date_start = fields.Date('Date')
    date_end = fields.Date('Date')
    uom_id = fields.Char(string='uom')
    poteau_t = fields.Integer('Time Spent')
    gest_id = fields.Many2one('hr.employee', string='Wizard')
    state = fields.Selection([
        ('draft', 'T. Planifiés'),
        ('affect', 'T. Affectés'),
        ('tovalid', 'T. Réalisés'),
        ('affect_con', 'T. Affectés controle'),
        ('affect_corr', 'T. Affectés corrction'),

        ('validcont', 'Controle Validée'),
        ('tovalidcorrec', 'Correction Encours'),
        ('tovalidcont', 'Controle Encours'),
        ('validcorrec', 'Correction Validée'),
        ('valid', 'T. Tarminées'),
        ('paid', 'Factures Approuvées'),
        ('cancel', 'T. Annulés'),
        ('pending', 'T. Suspendus'),
        ('close', 'Traité')
    ],
        'Status', copy=False)


class ProjectTaskWorkLine(models.Model):
    _name = 'project.task.work.line'
    _description = 'Project Task Work Line'
    name = fields.Char(string='Name')


class ProductUom(models.Model):
    _name = 'product.uom'
    name = fields.Char(string='Name')


class LinkLine(models.Model):
    _name = 'link.line'
    flow_id = fields.Integer(string='Flow')
    name = fields.Char(string='Name')

    ftp = fields.Char(string='Name')
