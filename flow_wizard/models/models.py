from datetime import datetime, date

from stdnum import py

from odoo import models, fields, api
from odoo.exceptions import UserError
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
    kit = fields.Char(string='Kit')
    kit_id = fields.Char(string='Kit_id')

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
        line_obj = self.pool.get('base.flow.merge.automatic.wizard')
        line_obj1 = self.pool.get('base.flow.merge.line')
        work_line = self.pool.get('project.task.work')
        wl = self.pool.get('project.task.work.line')
        task_line = self.pool.get('base.flow.merge.line')
        task_obj = self.pool.get('project.task')
        emp_obj = self.pool.get('hr.employee')
        tt = []
        # if self.env.cr.dbname == 'TEST95':
        #     connection = py.connect(host='localhost', user='root', passwd='', db='rukovoditel_en', use_unicode=True,
        #                             charset="utf8")
        #     cursor = connection.cursor()

        if not self.actions:
            raise UserError(_('Vous devez obligatoirement sélectionner une action!'))

        for line in self.line_ids:
            l1 = line.work_id
            if self.actions == 'keep':
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET active = %s, display = %s WHERE kit_id = %s AND project_id = %s AND zone = %s AND secteur = %s',
                        (True, True, l1.kit_id.id, self.project_id.id, l1.zone, l1.secteur))
                else:
                    self.env.cr.execute('UPDATE project_task_work SET active = %s, display = %s WHERE id = %s',
                                        (True, True, l1.id))

            elif self.actions == 'suspend':
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET state = %s WHERE task_id = %s AND zone = %s AND secteur = %s AND project_id = %s AND kit_id',
                        ('pending', l1.task_id.id, l1.zone, l1.secteur, self.project_id.id, l1.kit_id))
                else:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET state = %s WHERE task_id = %s AND zone = %s AND secteur = %s',
                        ('pending', l1.task_id.id, l1.zone, l1.secteur))

            elif self.actions == 'permis':
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET state = %s WHERE kit_id = %s AND project_id = %s AND zone = %s AND secteur = %s',
                        ('valid', l1.kit_id.id, self.project_id.id, l1.zone, l1.secteur))
                else:
                    print('Executing SQL query: UPDATE project_task_work SET state = %s WHERE id = %s' % (
                        'valid', int(l1.id)))

                    self.env.cr.execute('UPDATE project_task_work SET state = %s WHERE id = %s', ('valid', int(l1.id)))
                if self.env.cr.dbname == 'TEST95':
                    sql1 = ("update app_entity_26 set field_244='75' WHERE id = %s")
                    self.env.cr.execute(sql1, (l1.work_id.id,))
                    # connection.commit()

                for kk in l1.work_id.line_ids:
                    rec_line = self.env['project.task.work.line'].browse(kk)
                    if rec_line.group_id2:
                        if rec_line.group_id2.ids not in tt:
                            tt.append(rec_line.group_id2.ids)

            elif self.actions == 'archiv':
                if self.project_id.is_kit:
                    self.env.cr.execute(
                        'UPDATE project_task_work SET active = %s WHERE kit_id = %s AND project_id = %s AND zone = %s AND secteur = %s',
                        (False, l1.kit_id.id, self.project_id.id, l1.zone, l1.secteur))
                else:
                    self.env.cr.execute('UPDATE project_task_work SET active = %s WHERE id = %s', (False, l1.id))

                if self.env.cr.dbname == 'TEST95':
                    sql1 = ("update app_entity_26 set field_276=False WHERE id = %s")
                    self.env.cr.execute(sql1, (l1.work_id.id,))
                    # connection.commit()

        res_user = self.env['res.users'].browse(self._uid)
        for line in self.line_ids:
            l1 = line.work_id
            wk_histo = self.env['work.histo'].search([('work_id', '=', l1.id)])
            wk_histo_id = self.env['work.histo'].browse(wk_histo).id

            self.env['work.histo.line'].create({
                'actions': self.actions,
                'type': 'aw',
                'execute_by': self.employee_id.name or False,
                'create_by': res_user.employee_id.name,
                'work_histo_id': wk_histo_id,
                'date': fields.Datetime.now(),
                'coment1': self.note or False,
                'id_object': self.id,
            })

    def button_affect(self):
        work_obj = self.env['base.flow.merge.automatic.wizard']

        j = []
        r = []
        l = []
        pref = ''
        test = ''
        list = []
        link = []
        state = 'draft'

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
                raise UserError(_('Erreur!'), _("Travaux clotués!"))

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
        work_obj = self.env['base.flow.merge.automatic.wizard']
        task_work_obj = self.env['project.task.work']
        task_work = self.env['project.task.work']

        # Initialiser les listes pour stocker les données
        ltask1 = []
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

    work_id = fields.Many2one('project.task.work', string='Work')
    active = fields.Boolean(string='Is doctor?')
    line_ids = fields.One2many(
        'base.flow.merge.line', 'wizard_id', string=u"Role lines", copy=True,
        states={'draft': [('readonly', False)]}, )


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


class WorkHisto(models.Model):
    _name = 'work.histo'
    _description = 'Work Histo'

    name = fields.Char(string='Name')
    work_id = fields.Many2one('project.task.work', string='Work')
    histo_line_ids = fields.One2many('work.histo.line', 'work_histo_id', string='Histo Lines')


class WorkHistoLine(models.Model):
    _name = 'work.histo.line'
    _description = 'Work Histo Line'

    actions = fields.Selection([
        ('keep', 'Keep'),
        ('suspend', 'Suspend'),
        ('permis', 'Permis'),
        ('archiv', 'Archiv')
    ], string='Actions')
    type = fields.Selection([
        ('aw', 'AW')
    ], string='Type')
    create_by = fields.Char(string='Created By')
    work_histo_id = fields.Many2one('work.histo', string='Work Histo')
    date = fields.Datetime(string='Date')
    coment1 = fields.Text(string='Comment 1')
    id_object = fields.Integer(string='Object ID')
    execute_by = fields.Boolean(default="False")


class BaseInvoicesMergeAutomaticWizard(models.Model):
    _name = 'base.invoices.merge.automatic.wizard'
    _description = 'Base Invoices Merge Automatic Wizard'

    name = fields.Char(string='Name')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('affect', 'Affect'),
    ], string='State')
    categ_id = fields.Many2one('product.category', string='Wizard', readonly=True,
                               states={'draft': [('readonly', False)]}, )


class ProjectProject(models.Model):
    _inherit = 'project.project'
    is_kit = fields.Boolean(default=True, )


class BaseInvoicesMergeAutomaticWizardProjectTaskWorkRel(models.Model):
    _name = 'base.invoices.merge.automatic.wizard.project.task.work.rel'
    _description = 'Base Invoices Merge Automatic Wizard Project Task Work Relation'

    # base_invoices_merge_automatic_wizard_id = fields.Many2one('base.invoices.merge.automatic.wizard', string='Wizard')
    # project_task_work_id = fields.Many2one('project.task.work', string='Task Work')

    # Add other fields as needed

    name = fields.Char(string='Field Label')

