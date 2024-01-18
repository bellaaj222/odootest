# -*- coding: utf-8 -*-

from datetime import datetime, date
from stdnum import py
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _


class MergeFlowsLine(models.Model):
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
        ('validprod', 'Prod. validée'),
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

    @api.model
    def default_get(self, fields):

        res = super(EbMergeflows, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')

        for task in active_ids:
            work = self.env['project.task.work'].browse(task)
            context = self._context
            current_uid = context.get('uid')
            res_user = self.env['res.users'].browse(current_uid)
            categ_ids = self.env['hr.academic'].search([])
            # ('employee_id', '=', res_user.employee_id.id
            jj = []
            # if self.env.context.get('active_model') == 'project.task.work' and active_ids:
            #
            #     if categ_ids:
            #         print("test1")
            #         for ll in categ_ids.ids:
            #             dep = self.env['hr.academic'].browse(ll)
            #             jj.append(dep.categ_id.id)
            #     if work.categ_id.id not in jj:
            #         raise UserError(_('Action impossible1!'))
        if self.env.context.get('active_model') == 'project.task.work' and active_ids:
            state = 'draft'
            l = []
            l1 = []
            l2 = []
            for jj in active_ids:
                work = self.env['project.task.work'].browse(jj)
                if work.project_id.id not in l:
                    l.append(work.project_id.id)
                if len(l) > 1:
                    raise UserError(_('Action impossible!2\nAction possible pour un seul projet  !'))
                if work.zone not in l1:
                    l1.append(work.zone)
                if len(l1) > 1:
                    raise UserError(_('Action impossible!3\nAction possible pour un seul zone  !'))
                if work.secteur not in l2:
                    l2.append(work.secteur)
                if len(l2) > 1:
                    raise UserError(_('Action impossible!3\nAction possible pour un secteur zone  !'))
                r = []
                for task_id in active_ids:
                    work = self.env['project.task.work'].browse(task_id)
                    record_vals = {
                        'work_id': work.id,
                        'date_start_r': work.date_start,
                        'date_end_r': work.date_end,
                        'color1': work.color,
                        # 'uom_id_r': work.uom_id.id,
                        'poteau_t': work.poteau_t,
                        'gest_id': work.gest_id.id,
                        'state': work.state
                    }
                    r.append((0, 0, record_vals))
                categ_src_id = self.env['project.task.work'].browse(active_ids[0]).categ_id.id
                res.update({'line_ids': r, 'project_id': work.project_id.id, 'zo': work.zo, 'sect': work.sect,
                            'categ_src_id': categ_src_id})
            is_super_admin = self.env.context.get('is_super_admin')
            res.update({'line_ids': r, 'project_id': work.project_id.id, 'zo': work.zo, 'sect': work.sect,
                        'is_super_admin': is_super_admin})
        elif (self.env.context.get('active_model') == 'base.group.merge.automatic.wizard'):
            res = super(EbMergeflows, self).default_get(fields)

            tt = self.env['base.group.merge.automatic.wizard'].browse(self.env.context.get('active_ids'))
            ##   res['work_ids'] = tt.work_ids.ids
            active_ids = tt.work_ids.ids
            r = []
            pref = ''
            test = ''
            list = []
            state = 'draft'
            l = []
            l1 = []
            l2 = []
            for jj in active_ids:
                work = self.env['project.task.work'].browse(jj)
                if work.project_id.id not in l:
                    l.append(work.project_id.id)
                if len(l) > 1:
                    raise UserError(_('Action impossible!4\nAction possible pour un seul projet  !'))
                if work.zone not in l1:
                    l1.append(work.zone)
                if len(l1) > 1:
                    raise UserError(_('Action impossible!5\nAction possible pour une seule zone  !'))
                if work.secteur not in l2:
                    l2.append(work.secteur)
                if len(l2) > 1:
                    raise UserError(_('Action impossible!6\nAction possible pour une seule zone  !'))

                r.append((0, 0, {'work_id': work.id, 'date_start_r': work.date_start, 'date_end_r': work.date_end,
                                 'color1': work.color, 'uom_id_r': work.uom_id.id, 'poteau_t': work.poteau_t,
                                 'gest_id': work.gest_id.id, 'state': work.state
                                 }))
            is_super_admin = self.env.context.get('is_super_admin')
            res.update({'line_ids': r, 'project_id': work.project_id.id, 'zo': work.zo, 'sect': work.sect,
                        'is_super_admin': is_super_admin})

        return res

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

    web_diagram_id = fields.Many2one('web.diagram.plus', string='Diagramme Web')
    is_super_admin = fields.Boolean(string='Super Admin')
    link_ids = fields.One2many('link.line', 'flow_id', string="Work done", readonly=True,
                               states={'draft': [('readonly', False)]}, )
    current_user = fields.Many2one('res.users', compute='_get_current_user')
    gest_id = fields.Many2one('hr.employee', string='Wizard')
    work_ids = fields.Many2many('project.task.work', string='flows', readonly=True,
                                states={'draft': [('readonly', False)]}, )
    user_id = fields.Many2one('res.users', string='Assigned')
    dst_work_id = fields.Many2one('project.task.work', string='Destination Task')
    dst_project = fields.Many2one('project.project', string="Project")
    attach_ids = fields.Many2many('ir.attachment', 'ir_attach_rel', 'flow_id', 'attachment_id', string="Attachments",
                                  help="If any")
    line_ids = fields.One2many(
        'base.flow.merge.line', 'wizard_id', string=u"Role lines", copy=True,
        states={'draft': [('readonly', False)]}, )
    time_ch = fields.Selection([
        ('00:00', '00:00'),
        ('00:05', '00:05'),
        ('00:10', '00:10'),
        ('00:15', '00:15'),
        ('00:20', '00:20'),
        ('00:25', '00:25'),
        ('00:30', '00:30'),
        ('00:35', '00:35'),
        ('00:40', '00:40'),
        ('00:45', '00:45'),
        ('00:50', '00:50'),
        ('00:55', '00:55'),
        ('01:00', '01:00'),
        ('01:05', '01:05'),
        ('01:10', '01:10'),
        ('01:15', '01:15'),
        ('01:20', '01:20'),
        ('01:25', '01:25'),
        ('01:30', '01:30'),
        ('01:35', '01:35'),
        ('01:40', '01:40'),
        ('01:45', '01:45'),
        ('01:50', '01:50'),
        ('01:55', '01:55'),
        ('02:00', '02:00'),
        ('02:05', '02:05'),
        ('02:10', '02:10'),
        ('02:15', '02:15'),
        ('02:20', '02:20'),
        ('02:25', '02:25'),
        ('02:30', '02:30'),
        ('02:35', '02:35'),
        ('02:40', '02:40'),
        ('02:45', '02:45'),
        ('02:50', '02:50'),
        ('02:55', '02:55'),
        ('03:00', '03:00'),
        ('03:05', '03:05'),
        ('03:10', '03:10'),
        ('03:15', '03:15'),
        ('03:20', '03:20'),
        ('03:25', '03:25'),
        ('03:30', '03:30'),
        ('03:35', '03:35'),
        ('03:40', '03:40'),
        ('03:45', '03:45'),
        ('03:50', '03:50'),
        ('03:55', '03:55'),
        ('04:00', '04:00'),
        ('04:05', '04:05'),
        ('04:10', '04:10'),
        ('04:15', '04:15'),
        ('04:20', '04:20'),
        ('04:25', '04:25'),
        ('04:30', '04:30'),
        ('04:35', '04:35'),
        ('04:40', '04:40'),
        ('04:45', '04:45'),
        ('04:50', '04:50'),
        ('04:55', '04:55'),
        ('05:00', '05:00'),
        ('05:05', '05:05'),
        ('05:10', '05:10'),
        ('05:15', '05:15'),
        ('05:20', '05:20'),
        ('05:25', '05:25'),
        ('05:30', '05:30'),
        ('05:35', '05:35'),
        ('05:40', '05:40'),
        ('05:45', '05:45'),
        ('05:50', '05:50'),
        ('05:55', '05:55'),
        ('06:00', '06:00'),
        ('06:05', '06:05'),
        ('06:10', '06:10'),
        ('06:15', '06:15'),
        ('06:20', '06:20'),
        ('06:25', '06:25'),
        ('06:30', '06:30'),
        ('06:35', '06:35'),
        ('06:40', '06:40'),
        ('06:45', '06:45'),
        ('06:50', '06:50'),
        ('06:55', '06:55'),
        ('07:00', '07:00'),
        ('07:05', '07:05'),
        ('07:10', '07:10'),
        ('07:15', '07:15'),
        ('07:20', '07:20'),
        ('07:25', '07:25'),
        ('07:30', '07:30'),
        ('07:35', '07:35'),
        ('07:40', '07:40'),
        ('07:45', '07:45'),
        ('07:50', '07:50'),
        ('07:55', '07:55'),
        ('08:00', '08:00'),
        ('08:05', '08:05'),
        ('08:10', '08:10'),
        ('08:15', '08:15'),
        ('08:20', '08:20'),
        ('08:25', '08:25'),
        ('08:30', '08:30'),
        ('08:35', '08:35'),
        ('08:40', '08:40'),
        ('08:45', '08:45'),
        ('08:50', '08:50'),
        ('08:55', '08:55'),
        ('09:00', '09:00'),
        ('09:05', '09:05'),
        ('09:10', '09:10'),
        ('09:15', '09:15'),
        ('09:20', '09:20'),
        ('09:25', '09:25'),
        ('09:30', '09:30'),
        ('09:35', '09:35'),
        ('09:40', '09:40'),
        ('09:45', '09:45'),
        ('09:50', '09:50'),
        ('09:55', '09:55'),
        ('10:00', '10:00')
    ], string="Temps de Gestion", readonly=True, states={'draft': [('readonly', False)]})
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
    actions_super_admin = fields.Selection([('keep', 'Laisser Les Taches Actives (Pas de changement de statut)'),
                                            ('permis',
                                             'Terminer Les Taches(Retire les taches du tableau de bord mais reste affichable après recherche)'),
                                            ('archiv',
                                             'Archiver Les Taches Sélectionnées(Retire les taches du tableau de bord et de la recherche)'),
                                            ('suspend', 'Suspendre Temporairement Les Taches Encours'),
                                            ('treated', 'Cloturer Définitivement Les Taches Encours'),
                                            ], readonly=True, states={'draft': [('readonly', False)]}, )
    actions = fields.Selection([('keep', 'Laisser Les Taches Actives (Pas de changement de statut)'),
                                ('permis',
                                 'Terminer Les Taches(Retire les taches du tableau de bord mais reste affichable après recherche)'),
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
    done = fields.Selection([('production', 'Production'),
                             ('correction', 'Correction'),
                             ], readonly=True,
                            states={'draft': [('readonly', False)]}, )
    color1 = fields.Integer(string='Assigned')

    uom_id_r = fields.Many2one('product.uom', string='uom_id_r')
    uom_id = fields.Many2one('product.uom', string='uom_id')
    amount_untaxed = fields.Float(compute='_amount_all', string='amount_untaxed')
    amount_total = fields.Float(compute='_amount_all', string='amount_total')
    amount_tvq = fields.Float(compute='_amount_all', string='amount_tvq')
    amount_tps = fields.Float(compute='_amount_all', string='amount_tps')
    categ_id = fields.Many2one('product.category', string='Wizard', readonly=True,
                               states={'draft': [('readonly', False)]}, )
    categ_src_id = fields.Many2one('product.category', 'Departement source')
    employee_ids = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel',
                                    'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                    readonly=True, states={'draft': [('readonly', False)]}, )
    employee_ids1 = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel1',
                                     'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                     readonly=True, states={'draft': [('readonly', False)]}, )
    employee_ids2 = fields.Many2many('hr.employee', 'base_flow_merge_automatic_wizard_hr_employee_rel2',
                                     'base_flow_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes',
                                     readonly=True, states={'draft': [('readonly', False)]}, )
    kit_id = fields.Many2one('product.kit', string='Nom Kit', ondelete='cascade', select="1",
                             readonly=True, states={'draft': [('readonly', False)]}, )

    @api.onchange('actions')
    def onchange_actions(self):
        active = self.env.context.get('active_ids', [])
        if self.actions == 'permis' or self.actions == 'archiv' or self.actions == 'treated':
            for line in active:
                work = self.env['project.task.work'].browse(line)
                if work.state == 'affect_con' or work.state == 'affect_corr' or work.state == 'affect':
                    message = {'title': _('Attention'), 'message': _("Attention la tache: %s est en cours") % work.name}
                    return {'warning': message}
        return {}

    @api.onchange('project_id', 'categ_id', 'zone', 'secteur', 'work_ids')
    def onchange_project_id(self):
        ids = []
        ltask2 = []
        tt = self.env['project.task.work'].search([], order='sequence asc')
        task_ = self.env['project.task']
        task_work = self.env['project.task.work']

        if self.project_id.is_kit:
            if self.zone < 99 and self.secteur < 99 and self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT DISTINCT ON (kit_id, zone, secteur) id FROM project_task_work WHERE project_id=%s AND categ_id=%s AND zone=%s AND secteur=%s ORDER BY kit_id, zone, secteur',
                    (self.project_id.id, self.categ_id.id, self.zone, self.secteur))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]
            elif self.zone < 99 and self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT DISTINCT ON (kit_id, zone, secteur) id FROM project_task_work WHERE project_id=%s AND categ_id=%s AND zone=%s ORDER BY kit_id, zone, secteur',
                    (self.project_id.id, self.categ_id.id, self.zone))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]
            elif self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT DISTINCT ON (kit_id, zone, secteur) id FROM project_task_work WHERE project_id=%s AND categ_id=%s ORDER BY kit_id, zone, secteur',
                    (self.project_id.id, self.categ_id.id))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]
        else:
            if self.zone < 99 and self.secteur < 99 and self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT id FROM project_task_work WHERE project_id=%s AND categ_id=%s AND zone=%s AND secteur=%s',
                    (self.project_id.id, self.categ_id.id, self.zone, self.secteur))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]
            elif self.zone < 99 and self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT id FROM project_task_work WHERE project_id=%s AND categ_id=%s AND zone=%s',
                    (self.project_id.id, self.categ_id.id, self.zone))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]
            elif self.categ_id and self.project_id:
                self.env.cr.execute(
                    'SELECT id FROM project_task_work WHERE project_id=%s AND categ_id=%s',
                    (self.project_id.id, self.categ_id.id))
                ltask2 = [result[0] for result in self.env.cr.fetchall()]

        return {'domain': {'work_ids': [('id', 'in', ltask2)]}}

    def button_cancel(self):
        work_obj = self.env['project.task.work']
        line_obj = self.env['base.flow.merge.automatic.wizard']
        line_obj1 = self.env['base.flow.merge.line']
        work_line = self.env['project.task.work']

        for tt in self.work_ids:
            for msg_id in tt.ids:
                wk = work_obj.browse(msg_id)
                wk.write({'state': 'draft'})

        line_obj.write({'state': 'draft'})

        return {
            'name': 'Affectation les Travaux',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'base.flow.merge.automatic.wizard',
            'res_id': self.id,
            'context': {'default_state': 'draft'},
            'domain': []
        }

    def button_approve(self):

        task_line = self.env['base.flow.merge.line']
        wl = self.env['project.task.work.line']
        ##product = self.env['product.product'].browse(product_id)
        ##        raise ValidationError(
        ##                'assignation  '
        ##                '%s :)' % self.id)

        tt = []
        # if self.env.cr.dbname == 'TEST95':
        #     connection = py.connect(host='localhost', user='root', passwd='', db='rukovoditel_en', use_unicode=True,
        #                             charset="utf8")
        #     cursor = connection.cursor()
        # if self.categ_src_id and self.categ_id:
        #     # Récupérez le diagramme associé au workflow
        #     diagramme = self.web_diagram_id
        #
        #     # Créez le nœud source s'il n'existe pas encore
        #     node_source = self.env['web.diagram.plus.node'].search([
        #         ('web_diagram_id', '=', diagramme.id),
        #         ('categ', '=', self.categ_src_id.id)
        #     ], limit=1)
        #     if not node_source:
        #         node_source = self.env['web.diagram.plus.node'].create({
        #             'web_diagram_id': diagramme.id,
        #             'categ': self.categ_src_id.id,
        #             'name': self.categ_src_id.complete_name,
        #             # Ajoutez d'autres champs si nécessaire
        #         })
        #
        #     # Créez le nœud de destination s'il n'existe pas encore
        #     node_destination = self.env['web.diagram.plus.node'].search([
        #         ('web_diagram_id', '=', diagramme.id),
        #         ('categ', '=', self.categ_id.id)
        #     ], limit=1)
        #     if not node_destination:
        #         node_destination = self.env['web.diagram.plus.node'].create({
        #             'web_diagram_id': diagramme.id,
        #             'categ': self.categ_id.id,
        #             'name': self.categ_id.complete_name,
        #             # Ajoutez d'autres champs si nécessaire
        #         })
        #
        #     # Créez la flèche entre le nœud source et le nœud de destination
        #     arrow = self.env['web.diagram.plus.arrow'].create({
        #         'web_diagram_id': diagramme.id,
        #         'from_node_id': node_source.id,
        #         'to_node_id': node_destination.id,
        #         'name': 'Action associée',
        #         # 'actions': self.actions,  # Utilisez la valeur de votre champ actions
        #         # Ajoutez d'autres champs si nécessaire
        #     })
        # Assurez-vous que les départements source et destination sont définis
        if self.categ_src_id and self.categ_id:
            # Récupérez le diagramme associé au workflow
            diagramme = self.web_diagram_id

            # Créez le nœud source s'il n'existe pas encore
            node_source = self.env['web.diagram.plus.node'].search([
                ('web_diagram_id', '=', diagramme.id),
                ('categ', '=', self.categ_src_id.id)
            ], limit=1)
            if not node_source:
                node_source = self.env['web.diagram.plus.node'].create({
                    'web_diagram_id': diagramme.id,
                    'categ': self.categ_src_id.id,
                    'name': self.categ_src_id.complete_name,
                    # Ajoutez d'autres champs si nécessaire
                })

            # Créez le nœud de destination s'il n'existe pas encore
            node_destination = self.env['web.diagram.plus.node'].search([
                ('web_diagram_id', '=', diagramme.id),
                ('categ', '=', self.categ_id.id)
            ], limit=1)
            if not node_destination:
                node_destination = self.env['web.diagram.plus.node'].create({
                    'web_diagram_id': diagramme.id,
                    'categ': self.categ_id.id,
                    'name': self.categ_id.complete_name,
                    # Ajoutez d'autres champs si nécessaire
                })

            # Créez la flèche entre le nœud source et le nœud de destination
            arrow = self.env['web.diagram.plus.arrow'].create({
                'web_diagram_id': diagramme.id,
                'from_node_id': node_source.id,
                'to_node_id': node_destination.id,
                'name': 'Action associée',
                # Ajoutez d'autres champs si nécessaire
            })

        this = self.browse(self.ids)

        action = ''
        if self.is_super_admin:
            action = self.actions_super_admin
        else:
            action = self.actions

        if action == 'keep':
            self.state = 'affect'
            for line in self.line_ids.ids:
                l1 = task_line.browse(line)
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET active=%s WHERE kit_id=%s AND project_id=%s AND zone=%s AND secteur=%s',
                        (True, l1.work_id.kit_id.id, self.project_id.id, l1.work_id.zone, l1.work_id.secteur))

                else:

                    self.env.cr.execute('UPDATE project_task_work SET active=%s WHERE id=%s ',
                                        (True, l1.work_id.id))

                res_user = self.env['res.users'].browse(self.env.uid)
                wk_histo_id = None

                wk_histo = self.env['work.histo'].search([('work_id', '=', l1.work_id.id)])
                if not wk_histo:
                    for item in tt:
                        work_histo = self.env['work.histo'].create({
                            'task_id': item.task_id.id,
                            'categ_id': item.categ_id.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'date': item.date_start,
                            'create_a': datetime.now(),
                            'create_by': res_user.employee_id.name,
                            'zone': item.zone,
                            'secteur': item.secteur,
                            'project_id': item.project_id.id,
                            'partner_id': item.project_id.partner_id.id,
                        })
                        wk_histo_id = work_histo.id
                else:
                    wk_histo_id = wk_histo.id

                self.env['work.histo.line'].create({
                    'actions': 'keep',
                    'type': 'aw',
                    'execute_by': self.employee_id.name or False,
                    'create_by': res_user.employee_id.name,
                    'work_histo_id': wk_histo_id,
                    'date': fields.Datetime.now(),
                    'coment1': self.note or False,
                    'id_object': self.id,
                })
        if action == 'suspend':
            self.state = 'affect'
            for line in this.line_ids.ids:
                l1 = task_line.browse(line)
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET state=%s WHERE task_id=%s AND zone=%s AND secteur=%s AND project_id=%s AND kit_id=%s',
                        ('pending', l1.work_id.task_id.id, l1.work_id.zone, l1.work_id.secteur, this.project_id.id,
                         l1.work_id.kit_id.id)
                    )
                else:
                    self.env.cr.execute('UPDATE project_task_work SET state=%s WHERE task_id=%s',
                                        ('pending', l1.work_id.task_id.id))

                res_user = self.env['res.users'].browse(self.env.uid)
                wk_histo_id = None

                wk_histo = self.env['work.histo'].search([('work_id', '=', l1.work_id.id)])

                if not wk_histo:
                    for item in tt:
                        work_histo = self.env['work.histo'].create({
                            'task_id': item.task_id.id,
                            'categ_id': item.categ_id.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'date': item.date_start,
                            'create_a': datetime.now(),
                            'create_by': res_user.employee_id.name,
                            'zone': item.zone,
                            'secteur': item.secteur,
                            'project_id': item.project_id.id,
                            'partner_id': item.project_id.partner_id.id,
                        })
                        wk_histo_id = work_histo.id
                else:
                    wk_histo_id = wk_histo.id

                self.env['work.histo.line'].create({
                    'actions': 'suspend',
                    'type': 'aw',
                    'execute_by': self.employee_id.name or False,
                    'create_by': res_user.employee_id.name,
                    'work_histo_id': wk_histo_id,
                    'date': fields.Datetime.now(),
                    'coment1': self.note or False,
                    'id_object': self.id,
                })

        if action == 'archiv':
            self.state = 'affect'
            for line in this.line_ids.ids:
                l1 = task_line.browse(line)
                if l1.work_id:  # Vérifier si work_id est non nul
                    if this.project_id.is_kit is True:
                        self.env.cr.execute(
                            'UPDATE project_task_work SET active=%s WHERE kit_id=%s AND project_id=%s AND zone=%s AND secteur=%s',
                            (False, l1.work_id.kit_id.id, this.project_id.id, l1.work_id.zone, l1.work_id.secteur))
                        # removed .id from kit_id
                    else:
                        self.env.cr.execute('UPDATE project_task_work SET active=%s WHERE id=%s',
                                            (False, l1.work_id.id))

                res_user = self.env['res.users'].browse(self.env.uid)
                wk_histo_id = None

                wk_histo = self.env['work.histo'].search([('work_id', '=', l1.work_id.id)])

                if not wk_histo:
                    for item in tt:
                        work_histo = self.env['work.histo'].create({
                            'task_id': item.task_id.id,
                            'categ_id': item.categ_id.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'date': item.date_start,
                            'create_a': datetime.now(),
                            'create_by': res_user.employee_id.name,
                            'zone': item.zone,
                            'secteur': item.secteur,
                            'project_id': item.project_id.id,
                            'partner_id': item.project_id.partner_id.id,
                        })
                        wk_histo_id = work_histo.id
                else:
                    wk_histo_id = wk_histo.id

                self.env['work.histo.line'].create({
                    'actions': 'archiv',
                    'type': 'aw',
                    'execute_by': self.employee_id.name or False,
                    'create_by': res_user.employee_id.name,
                    'work_histo_id': wk_histo_id,
                    'date': fields.Datetime.now(),
                    'coment1': self.note or False,
                    'id_object': self.id,
                })

                for kk in l1.work_id.line_ids.ids:
                    rec_line = self.env['project.task.work.line'].browse(kk)
                    if rec_line.group_id2:
                        if rec_line.group_id2.ids not in tt:
                            tt.append(rec_line.group_id2.ids)

        if action == 'treated':
            self.state = 'affect'
            for line in this.line_ids.ids:
                l1 = task_line.browse(line)
                if this.project_id.is_kit is True:
                    self.env.cr.execute(
                        'update project_task_work set  state=%s where  kit_id=%s and project_id=%s and zone=%s and secteur=%s',
                        (
                            'valid', l1.work_id.kit_id.id, this.project_id.id, l1.work_id.zone,
                            l1.work_id.secteur))

                else:
                    self.env.cr.execute('update project_task_work set  state=%s where  id=%s ',
                                        ('valid', l1.work_id.id))

                res_user = self.env['res.users'].browse(self.env.uid)
                wk_histo_id = None

                wk_histo = self.env['work.histo'].search([('work_id', '=', l1.work_id.id)])

                if not wk_histo:
                    for item in tt:
                        work_histo = self.env['work.histo'].create({
                            'task_id': item.task_id.id,
                            'categ_id': item.categ_id.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'date': item.date_start,
                            'create_a': datetime.now(),
                            'create_by': res_user.employee_id.name,
                            'zone': item.zone,
                            'secteur': item.secteur,
                            'project_id': item.project_id.id,
                            'partner_id': item.project_id.partner_id.id,
                        })
                        wk_histo_id = work_histo.id
                else:
                    wk_histo_id = wk_histo.id

                self.env['work.histo.line'].create({
                    'actions': 'treated',
                    'type': 'aw',
                    'execute_by': self.employee_id.name or False,
                    'create_by': res_user.employee_id.name,
                    'work_histo_id': wk_histo_id,
                    'date': fields.Datetime.now(),
                    'coment1': self.note or False,
                    'id_object': self.id,
                })

                for kk in l1.work_id.line_ids.ids:
                    rec_line = self.env['project.task.work.line'].browse(kk)
                    if rec_line.group_id2:
                        if rec_line.group_id2.ids not in tt:
                            tt.append(rec_line.group_id2.ids)
        if action == 'permis':
            self.state = 'affect'
            for line in this.line_ids.ids:
                l1 = task_line.browse(line)
                if self.project_id.is_kit is True:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET state=%s WHERE kit_id=%s AND project_id=%s AND zone=%s AND secteur=%s',
                        ('valid', l1.work_id.kit_id.id, this.project_id.id, l1.work_id.zone, l1.work_id.secteur)
                    )

                else:
                    self.env.cr.execute('UPDATE project_task_work SET state=%s WHERE id=%s',
                                        ('valid', l1.work_id.id))

                res_user = self.env['res.users'].browse(self.env.uid)
                wk_histo_id = None

                wk_histo = self.env['work.histo'].search([('work_id', '=', l1.work_id.id)])

                if not wk_histo:
                    for item in tt:
                        work_histo = self.env['work.histo'].create({
                            'task_id': item.task_id.id,
                            'categ_id': item.categ_id.id,
                            'product_id': item.product_id.id,
                            'name': item.name,
                            'date': item.date_start,
                            'create_a': datetime.now(),
                            'create_by': res_user.employee_id.name,
                            'zone': item.zone,
                            'secteur': item.secteur,
                            'project_id': item.project_id.id,
                            'partner_id': item.project_id.partner_id.id,
                        })
                        wk_histo_id = work_histo.id
                else:
                    wk_histo_id = wk_histo.id

                self.env['work.histo.line'].create({
                    'actions': 'permis',
                    'type': 'aw',
                    'execute_by': self.employee_id.name or False,
                    'create_by': res_user.employee_id.name,
                    'work_histo_id': wk_histo_id,
                    'date': fields.Datetime.now(),
                    'coment1': self.note or False,
                    'id_object': self.id,
                })

                for kk in l1.work_id.line_ids:
                    rec_line = self.env['project.task.work.line'].browse(kk)
                    if rec_line.group_id2:
                        if rec_line.group_id2.ids not in tt:
                            tt.append(rec_line.group_id2.ids)
        if this.date_start_r:
            for line in this.work_ids:
                l1 = self.env['project.task.work'].browse(line.id)
                l1.write({'date_start': this.date_start_r})

        if this.date_end_r:
            for line in this.work_ids:
                l1 = self.env['project.task.work'].browse(line.id)
                l1.write({'date_end': this.date_end_r})

        if this.poteau_r:
            for line in this.work_ids:
                l1 = self.env['project.task.work'].browse(line.id)
                l1.write({'poteau_t': this.poteau_r})

        vals = this.time_ch.split(':')
        if len(vals) >= 2:
            hours = float(vals[0])
            minutes = float(vals[1])
            t, hours = divmod(hours, 24)
            t, minutes = divmod(minutes, 60)
            minutes = minutes / 60.0
            total = hours + minutes
        else:
            raise UserError(_("Invalid time format: expected hh:mm"))

        res_user = self.env['res.users'].browse(self.env.uid)
        for rec in self.line_ids[0]:
            self.env.cr.execute(
                "INSERT INTO base_group_merge_automatic_wizard (create_date,date_start_r,project_id,zo,sect,gest_id,state,active,name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (fields.Date.today(), fields.Date.today(), rec.work_id.project_id.id, rec.work_id.zone,
                 rec.work_id.secteur,
                 rec.work_id.gest_id.id if rec.work_id.gest_id else None, 'valid', True, 'gestion affectation')
            )
            self.env.cr.execute('SELECT id FROM base_group_merge_automatic_wizard ORDER BY id DESC LIMIT 1')
            base_group_id = self.env.cr.fetchone()
            ##raise UserError(_("Transfert impossible!\nPas de stock suffisant pour l'article %s !") % rec.work_id.categ_id.name)

            if rec.work_id.categ_id.id == 3:
                product = 156
            elif rec.work_id.categ_id.id == 1:
                product = 80
            elif rec.work_id.categ_id.id == 4:
                product = 218
            elif rec.work_id.categ_id.id == 6:
                product = 174
            elif rec.work_id.categ_id.id == 7:
                product = 197
            elif rec.work_id.categ_id.id == 8:
                product = 132
            elif rec.work_id.categ_id.id == 5:
                product = 132
            else:
                product = 80
            self.env.cr.execute(
                "INSERT INTO base_group_merge_line (create_date,date_start_r,date_end_r,product_id,project_id,hours_r,uom_id_r,uom_id,wizard_id,color1,employee_id,categ_id,zone,secteur)  VALUES ('%s','%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                % (fields.Date.today(), fields.Date.today(), fields.Date.today(), product, rec.work_id.project_id.id,
                   total, 5, 5, base_group_id[0], 1, res_user.employee_id.id, rec.work_id.categ_id.id, rec.zone or 0,
                   rec.secteur or 0))
            move_line = {
                'product_id': product,
                'employee_id': res_user.employee_id.id,
                'state': 'valid',
                'work_id': rec.work_id.id,
                'task_id': rec.work_id.task_id.id,
                'group_id2': base_group_id,
                'sequence': rec.work_id.sequence,
                'done3': True,
                'date': fields.Date.today(),
                'uom_id': 5,
                'date_start_r': fields.Date.today(),
                'date_end_r': fields.Date.today(),
                'categ_id': rec.work_id.categ_id.id,
                'hours_r': total,
                'color1': 1,
                'project_id': rec.work_id.project_id.id,
                'partner_id': rec.work_id.project_id.partner_id.id,
                'gest_id': rec.work_id.gest_id.id,
                'zone': rec.work_id.zone,
                'secteur': rec.work_id.secteur,
            }
            one = wl.create(move_line)

        if self.mail_send == 'yes':

            emp_obj = self.env['hr.employee']
            if self.note is False:
                self.write({'note': ' '})

            ##            if not self.employee_ids:
            ##                    raise ValidationError(_('Erreur ! Vous devez s�lectionner un destinataire.'))
            ##            else:
            kk = ''
            for line in self.employee_ids.ids:
                emp = emp_obj.browse(line)
                if emp.work_email:
                    kk = kk + emp.work_email + ','
                ##raise osv.except_osv(_('Error !'), _('No period defined for this date: %s !\nPlease create one.')%kk)
            self.write({'to': kk})
            if self.employee_ids1:

                ll = ''
                for line in self.employee_ids1.ids:
                    emp1 = emp_obj.browse(line)
                    if emp1.work_email:
                        ll = ll + emp1.work_email + ','
                    ##raise osv.except_osv(_('Error !'), _('No period defined for this date: %s !\nPlease create one.')%kk)
                self.write({'cc': ll})
            ##            if self.employee_ids2:
            ##
            ##                mm=''
            ##                for line in  self.employee_ids2.ids:
            ##                    emp2=emp_obj.browse(line)
            ##                    if emp2.work_email:
            ##                        mm=mm+emp2.work_email+','
            ##                    ##raise osv.except_osv(_('Error !'), _('No period defined for this date: %s !\nPlease create one.')%kk)
            ##            self.write({'cci':mm})
            ##
            if self.done == 'production':

                self.env['mail.template'].sudo().browse(46).send_mail(self.id, force_send=True)
            else:
                self.env['mail.template'].sudo().browse(38).send_mail(self.id, force_send=True)

        self.write({'state': 'affect'})

    def button_affect(self):
        j = []
        r = []
        l = []
        pref = ''
        test = ''
        link = []

        self.env.cr.execute(
            'SELECT CAST(SUBSTR(name, 5, 7) AS INTEGER) FROM base_invoices_merge_automatic_wizard WHERE name IS NOT NULL AND categ_id=1 AND EXTRACT(YEAR FROM create_date)=%s ORDER BY CAST(name AS INTEGER) DESC LIMIT 1',
            (str(fields.Date.today().strftime('%Y%m%d'))[:4],))
        q3 = self.env.cr.fetchone()

        if q3:
            res1 = q3[0] + 1
        else:
            res1 = '001'

        aff = self.env['base.invoices.merge.automatic.wizard'].create({'state': 'draft'})

        if self.link_ids:
            for ll in self.link_ids:
                self.env['link.line'].create({'ftp': ll.ftp, 'name': ll.name, 'affect_id': aff.id})
                link.append((0, 0, {'ftp': ll.ftp, 'name': ll.name, 'affect_id': aff.id}))

        for jj in self.work_ids:
            work = self.env['project.task.work'].browse(jj.id)
            self.env.cr.execute(
                'SELECT base_invoices_merge_automatic_wizard_id FROM base_invoices_merge_automatic_wizard_project_task_work_rel WHERE base_invoices_merge_automatic_wizard_id=%s LIMIT 1',
                (aff.id,))
            tt = self.env.cr.fetchone()

            if not tt:
                self.env.cr.execute(
                    "INSERT INTO base_invoices_merge_automatic_wizard_project_task_work_rel VALUES (%s,%s)",
                    (aff.id, work.id))

            if work.state == 'close':
                raise UserError(_('Erreur!\nTravaux clotués!'))

            done = 0
            if work.gest_id.user_id.id == self._uid:
                done = 1
            else:
                done = 0

            if work.state != 'draft':
                state = 'affect'
            r.append(work.categ_id.id)
            j.append(work.id)

            if r:
                for kk in r:
                    dep = self.env['hr.academic'].search([('categ_id', '=', kk)])
                    if dep:
                        for nn in dep:
                            em = self.env['hr.academic'].browse(nn).employee_id.id
                            l.append(em)
            cat = work[0].categ_id.id
            test = test + pref + str(work.project_id.name) + ' - ' + str(work.task_id.sequence) + ' - ' + str(
                work.sequence)

            if cat == 1:
                name = str(str(fields.Date.today().strftime('%Y%m%d'))[:4] + str(str(res1).zfill(3)))
            else:
                name = ''

        return {
            'name': ('Affectation des Ressources'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'base.invoices.merge.automatic.wizard',
            'res_id': aff.id,
            'context': {'default_color1': 1, 'color1': 1},
            'target': 'new',
            'flags': {'initial_mode': 'edit'}
        }

    def button_load_mail(self):
        work_line = self.env['project.task.work']
        emp_obj = self.env['hr.employee']
        this = self

        kk = []
        kk1 = []

        for line in this.work_ids:
            l1 = work_line.browse(line.id)
            if l1.gest_id and l1.gest_id.id not in kk:
                kk.append(l1.gest_id.id)
                self.env.cr.execute(
                    "INSERT INTO base_flow_merge_automatic_wizard_hr_employee_rel (base_flow_merge_automatic_wizard_id, hr_employee_id) VALUES (%s, %s)",
                    (this.id, l1.gest_id.id))

            if l1.gest_id3 and l1.gest_id3.id not in kk1:
                kk1.append(l1.gest_id3.id)
                self.env.cr.execute(
                    "INSERT INTO base_flow_merge_automatic_wizard_hr_employee_rel1 (base_flow_merge_automatic_wizard_id, hr_employee_id) VALUES (%s, %s)",
                    (this.id, l1.gest_id3.id))

        return {
            'name': ('Affectation les Travaux'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'base.flow.merge.automatic.wizard',
            'res_id': this.id,
            'domain': []
        }

    def button_save_(self):
        # Récupérer l'enregistrement actuel
        this = self

        # Obtenir les objets des modèles correspondants
        task_work_obj = self.env['project.task.work']

        # Initialiser les listes pour stocker les données
        ltask2 = []

        # Insérer les enregistrements dans la table de relation
        for jj in ltask2:
            self.env.cr.execute("""
                 INSERT INTO base_flow_merge_automatic_wizard_project_task_work_rel (base_flow_merge_automatic_wizard_id, project_task_work_id)
                 VALUES (%s, %s)
             """, (this.id, jj))

        # Mettre à jour les enregistrements dans la table project_task_work
        for line in this.work_ids.ids:
            tt = task_work_obj.browse(line)
            self.env.cr.execute("""
                 UPDATE project_task_work
                 SET poteau_t = %s, date_start = %s, date_end = %s
                 WHERE id = %s
             """, (tt.poteau_t, tt.date_start, tt.date_end, tt.id))

        # Retourner l'action à exécuter après le bouton Enregistrer
        return {
            'name': 'Affectation les Travaux',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'base.flow.merge.automatic.wizard',
            'res_id': this.id,
            'target': 'new',
            'context': {},
            'domain': [],
        }


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    def _default_flow(self):

        for rec in self:
            self.env.cr.execute('select id from base_flow_merge_line where work_id= %s', (rec.id,))
            work_ids = self.env.cr.fetchone()
            if work_ids:
                rec.done4 = 1
            else:
                rec.done4 = 0

    done4 = fields.Boolean(compute='_default_flow', string='Company Currency', readonly=True,
                           states={'draft': [('readonly', False)]}, )

    def action_open(self):
        is_super_admin = self.env.user.has_group('project_custom.group_super_admin')
        current = self.ids[0]
        l = []
        this = self.browse(current)
        if this.line_ids:
            for tt in this.line_ids.ids:
                l.append(tt)

        return {
            'name': 'Taches Concernées',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'base.flow.merge.automatic.wizard',

            'context': {'active_ids': self.ids,
                        'active_model': self._name,
                        'is_super_admin': is_super_admin},
            'domain': []
        }


class LinkLine(models.Model):
    _inherit = 'link.line'
    flow_id = fields.Many2one('base.flow.merge.automatic.wizard', string='Event')


class Webdiagram(models.Model):
    _inherit = 'web.diagram.plus'
    web_diagram_id = fields.Many2one('web.diagram.plus', string='Diagramme Web')
