# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class EbMergeInvoices(models.Model):
    _name = "base.invoices.merge.automatic.wizard"
    _description = "Merge invoicess"

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        print('self.env.context :', self.env.context)

        if active_model != 'project.task.work':
            if active_model == 'base.group.merge.automatic.wizard':
                tt = self.env['base.group.merge.automatic.wizard'].browse(active_ids)
            else:
                tt = self.env['base.flow.merge.automatic.wizard'].browse(active_ids)
            active_ids = tt.work_ids.ids
            selected_work_ids = []
            for active_id in active_ids:
                work = self.env['project.task.work'].browse(active_id)
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
                                selected_work_ids.append(work1.id)
                        else:
                            if work1.is_copy is not False:
                                if work.rank == work1.rank:
                                    selected_work_ids.append(work1.id)
                    res['work_ids'] = selected_work_ids
                else:
                    res['work_ids'] = active_ids
            self.update_result(active_ids, res, tt.work_ids.ids)
        if active_model == 'project.task.work' and active_ids:
            affectation_multiple = self.env['settings.custom'].search([('affectation_multiple', '=', 0)], limit=1)
            tt = self.env['project.task.work'].browse(active_ids)
            if affectation_multiple:
                res = self.get_default_multiple(tt, active_ids, res)
            else:
                for active_id in active_ids:
                    work = self.env['project.task.work'].browse(active_id)
                    res = self.get_default_simple(work, active_ids, res)

            self.update_result(active_ids, res, active_ids)
        print('res: ', res)
        print('self: ', self.work_ids)

        return res

    def update_result(self, active_ids, res, rec_ids):
        department_ids = []
        employee_ids = []
        pref = ''
        test = ''
        state = 'draft'
        self.env.cr.execute(
            'select cast(substr(name, 5, 7) as integer)  from base_invoices_merge_automatic_wizard where name is not Null  and categ_id=1  and EXTRACT(YEAR FROM create_date)=%s   order by cast(name as integer) desc limit 1',
            (str(datetime.today().year),))
        q3 = self.env.cr.fetchone()
        if q3:
            res1 = q3[0] + 1
        else:
            res1 = '001'
        for rec_id in rec_ids:
            work = self.env['project.task.work'].browse(rec_id)
            if work.state == 'close':
                raise UserError(_('Erreur!\nTravaux clotués!'))
            if len(active_ids) > 1:
                pref = '/'
            if work.state != 'draft':
                state = 'affect'
            department_ids.append(work.categ_id.id)
            if department_ids:
                for department_id in department_ids:
                    dep = self.env['hr.academic'].search([('categ_id', '=', department_id)])
                    if dep:
                        for nn in dep.ids:
                            employee_id = self.env['hr.academic'].browse(nn).employee_id.id
                            employee_ids.append(employee_id)
            cat = work.categ_id.id
            test = (test + pref + str(work.project_id.name) + ' - '
                    + str(work.task_id.sequence) + ' - ' + str(
                        work.sequence))
            res.update({'states': test,
                        'employee_id': work.employee_id.id,
                        'gest_id': work.gest_id.id,
                        'categ_id': work.categ_id.id,
                        'project_id': work.project_id.id,
                        'zone': work.zone,
                        'secteur': work.secteur,
                        'state': state,
                        'dep': department_ids})
            if cat == 1:
                res.update({'name': str(str(fields.Date.today().year) + str(res1).zfill(3))})
        return res

    def get_default_multiple(self, tt, active_ids, res):
        for work in tt:
            if (
                    'correction' in work.product_id.name or 'gestion client' in work.product_id.name or u'Contrôle' in work.product_id.name):
                raise UserError(
                    _("Action impossible!\nImpossible d'affecter ce type de tache à partir de ce menu!"))
        vv = []
        for hh in active_ids:
            work = self.env['project.task.work'].browse(hh)
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
                for kit_work in kit_list:

                    if not work.is_copy and not kit_work.is_copy:
                        vv.append(kit_work.id)
                    elif kit_work.is_copy and work.rank == kit_work.rank:
                        vv.append(kit_work.id)

                res['work_ids'] = vv
            else:
                res['work_ids'] = active_ids
        return res

    def get_default_simple(self, work, active_ids, res):
        vv = []
        if 'correction' not in work.product_id.name and u'Contrôle' not in work.product_id.name:
            kit_list = self.env['project.task.work'].search([
                ('project_id', '=', work.project_id.id),
                ('zone', '=', work.zone),
                ('secteur', '=', work.secteur),
                ('kit_id', '=', work.kit_id.id),
                ('work_group_id', '=', work.work_group_id),
                ('product_id.name', 'not ilike', '%correction%'),
                ('product_id.name', 'not ilike', '%cont%'),
                ('product_id.name', 'not ilike', '%gestion client%')
            ])
            for kit_work in kit_list:
                if not work.is_copy and not kit_work.is_copy:
                    vv.append(kit_work.id)
                elif kit_work.is_copy and work.rank == kit_work.rank:
                    vv.append(kit_work.id)
            res['work_ids'] = vv
            return res
        elif u'Contrôle' in work.product_id.name:
            res['types_affect'] = 'controle'

        elif 'correction' in work.product_id.name:
            res['types_affect'] = 'correction'
        if work.kit_id:
            kit_list = self.env['project.task.work'].search([
                ('id', 'in', active_ids),
            ])
            for kit_work in kit_list:
                if not work.is_copy and not kit_work.is_copy:
                    vv.append(kit_work.id)
                elif kit_work.is_copy and work.rank == kit_work.rank:
                    vv.append(kit_work.id)

            res['work_ids'] = vv
            return res

    def _amount_all(self):

        tax_obj = self.env['account.tax']

        tvp_obj = tax_obj.browse(8)
        tps_obj = tax_obj.browse(7)

        for invoice in self:
            invoice.amount_untaxed = sum(line.amount_line for line in invoice.line_ids)
            if invoice.employee_id.job_id.id == 1:
                tvq = 0
                tps = 0
            else:
                tvq = tvp_obj.amount
                tps = tps_obj.amount
            invoice.amount_tps = invoice.amount_untaxed * tps
            invoice.amount_tvq = invoice.amount_untaxed * tvq
            invoice.amount_total = invoice.amount_untaxed + invoice.amount_tps + invoice.amount_tvq

    name = fields.Char(string='name', readonly=True, )
    gest_id = fields.Many2one('hr.employee', string='Wizard', readonly=True, states={'draft': [('readonly', False)]})
    work_ids = fields.Many2many('project.task.work', string='Invoices', readonly=True,
                                states={'draft': [('readonly', False)]})
    user_id = fields.Many2one('res.users', string='Assigned', readonly=True, states={'draft': [('readonly', False)]})
    dst_work_id = fields.Many2one('project.task.work', string='Destination Task')
    dst_project = fields.Many2one('project.project', string="Project")
    group_id = fields.Many2one('base.group.merge.automatic.wizard', string="Project")
    line_ids = fields.One2many(
        'base.invoices.merge.line', 'wizard_id', string="Role lines", copy=True,
        readonly=True, states={'draft': [('readonly', False)]})
    link_ids = fields.One2many('link.line', 'affect_id', string="Work done")
    project_id = fields.Many2one('project.project', string='Wizard', readonly=True,
                                 states={'draft': [('readonly', False)]})
    task_id = fields.Many2one('project.task', string='Wizard', readonly=True, states={'draft': [('readonly', False)]})
    work_id = fields.Many2one('project.task.work', string='Wizard', readonly=True,
                              states={'draft': [('readonly', False)]})
    pay_id = fields.Many2one('hr.payslip', string='Wizard', readonly=True, states={'draft': [('readonly', False)]})
    date_start_r = fields.Date(string='Assigned')
    date_end_r = fields.Date(string='Assigned')
    employee_id = fields.Many2one('hr.employee', string='Assigned',
                                  readonly=True, states={'draft': [('readonly', False)]})
    employee_id2 = fields.Many2one('hr.employee', string='Intervenant')
    hours_r = fields.Float(string='Assigned')
    total_t = fields.Float(string='Assigned')
    total_r = fields.Float(string='Assigned')
    poteau_t = fields.Float(string='Assigned')
    poteau_r = fields.Float(string='Assigned')
    poteau_i = fields.Float(string='Assigned')
    poteau_reste = fields.Float(string='Assigned')
    sequence = fields.Integer(string='Assigned')
    zone = fields.Integer(string='Assigned')
    secteur = fields.Integer(string='Assigned')
    state = fields.Selection([
        ('draft', 'Planif. Trav.'),
        ('affect', 'Travaux Affectés'),
        ('tovalid', 'Validaion Super.'),
        ('valid', 'Factures Br.'),
        ('paid', 'Factures Val.'),
        ('cancel', 'T. Annulés'),
        ('pending', 'T. Suspendus'),
        ('close', 'Traité')], default='draft')
    note = fields.Text(string='Assigned')
    states = fields.Char(string='char', readonly=True, states={'draft': [('readonly', False)]})
    ftp = fields.Char(string='char')
    dep = fields.Char(string='char', readonly=True, states={'draft': [('readonly', False)]})
    done = fields.Boolean(string='Is doctor?', compute='_disponible')
    objet = fields.Char(string='char')
    color1 = fields.Integer(string='Assigned')
    uom_id_r = fields.Many2one('product.uom', string='Assigned')
    uom_id = fields.Many2one('product.uom', string='Assigned')
    amount_untaxed = fields.Float(compute='_amount_all', string='Name', default=0, )
    amount_total = fields.Float(compute='_amount_all', string='Name')
    amount_tvq = fields.Float(compute='_amount_all', string='Name')
    amount_tps = fields.Float(compute='_amount_all', string='Name')
    categ_id = fields.Many2one('product.category', string='Wizard')
    to = fields.Char(string='char')
    cc = fields.Char(string='char')
    cci = fields.Char(string='char')
    mail_send = fields.Selection([('yes', 'Oui'),
                                  ('no', 'Non')],
                                 default='no')
    employee_ids = fields.Many2many('hr.employee', 'base_invoices_merge_automatic_wizard_hr_employee_rel',
                                    'base_invoices_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes')
    employee_ids1 = fields.Many2many('hr.employee', 'base_invoices_merge_automatic_wizard_hr_employee_rel1',
                                     'base_invoices_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes')
    employee_ids2 = fields.Many2many('hr.employee', 'base_invoices_merge_automatic_wizard_hr_employee_rel2',
                                     'base_invoices_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes')
    employee_ids3 = fields.Many2many('hr.employee', 'base_invoices_merge_automatic_wizard_hr_employee_rel3',
                                     'base_invoices_merge_automatic_wizard_id', 'hr_employee_id', string='Legumes')
    types_affect = fields.Selection([
        ('intervenant', 'Production'),
        ('controle', 'Contrôle'),
        ('correction', 'Correction')
    ], string="Type d'affectation", default='intervenant')
    intervenant_id = fields.Many2one('hr.employee', string='Intervenant')
    time = fields.Float(string='Temps de gestion')
    time_ch = fields.Char(string='Temps de gestion')

    # butt_valider = fields.Boolean(string="Default Butt Valider", default =False)

    @api.onchange('employee_id2')
    def onchange_employee_id2(self):
        if self.employee_id2:
            # Mettre à jour le champ employee_ids avec la même valeur que employee_id2
            self.employee_ids = [(6, 0, [self.employee_id2.id])]

    def _compute_done2(self):
        print('_compute_done2')
        for record in self:
            if record.gest_id.user_id.id == self.env.user.id:
                record.done = True
            else:
                record.done = False
                raise UserError(_("Transfert impossible!\nPas de stock suffisant pour l'article %s !") % record.name)

    def _disponible(self):
        print('_disponible')
        print(self.work_ids)

        for book in self:
            if book.gest_id.user_id.id == self.env.user.id:
                print('self.env.user.id:', self.env.user.id)
                book.done = True
            else:
                book.done = False

    @api.model
    def _get_current_user(self):
        print("_get_current_user")
        for record in self:
            record.done = False  # (self.env.user.id == record.gest_id.user_id.id)

    @api.onchange('categ_id', 'project_id', 'zone', 'secteur')
    def onchange_place(self):

        res = {}

        if self.categ_id:
            r = []
            k = []
            dep = self.env['hr.academic'].search([('categ_id', '=', self.categ_id.id)])

            if dep:
                for academic in dep:
                    em = academic.employee_id.id
                    k.append(academic.id)
                    r.append(em)
            res['domain'] = {
                # 'employee_id2': [('id', 'in', r)],
                'work_ids': [
                    ('categ_id', '=', self.categ_id.id),
                    ('project_id', '=', self.project_id.id),
                    ('zone', '=', self.zone),
                    ('secteur', '=', self.secteur)
                ]
            }
        print('res:', res)
        return res

    @api.model
    def action_merge(self):
        names = []

        # Write the name of the destination task because it will be overwritten
        if self.dst_work_id:
            names.append(self.dst_work_id.name)
        else:
            raise UserError(_('You must select a Destination Work'))
        desc = []
        desc.append(self.dst_work_id.description)
        for invoice in self.invoices_ids:
            if invoice.id != self.dst_work_id.id:
                for name in invoice:
                    names.append(name.name)
                    desc.append(name.description)

        # Transfer messages from work_ids to dst_work_id
        for message in self.work_ids:
            for msg_id in message.message_ids:
                msg_id.write({'res_id': self.dst_work_id.id})

        plan_hours = self.dst_work_id.planned_hours

        for hour in self.work_ids:
            for time in hour:
                plan_hours += time.planned_hours

        # Write to dst_work_id full planned hours from all works
        self.dst_work_id.write({'planned_hours': plan_hours})

        # Actual writing to the tasks
        transformed_names = ', '.join(names)
        self.dst_work_id.write({'name': transformed_names})

        transformed_desc = ', '.join(desc)
        self.dst_work_id.write({'description': transformed_desc})

        # Posting a note in the merged and archived tasks
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for work in self.work_ids:
            work.message_post(body="This work has been merged into: %s/#id=%s&amp;view_type=form&amp;model=project.task"
                                   % (base_url, self.dst_work_id.id))

        self.work_ids.write({'active': False})

        # Explicitly write the dst_work_id as active for security reasons
        self.dst_work_id.write({'active': True})

        # Check if user has been assigned and if not raise an error
        if self.user_id:
            # Write the Assigned To user_id
            self.dst_work_id.write({'user_id': self.user_id.id})
        elif self.dst_work_id.user_id:
            self.dst_work_id.write({'user_id': self.dst_work_id.user_id.id})
        else:
            raise Warning(
                "There is no user assigned to the merged work, and the destination work doesn't have an assigned user.")

        return True

    def button_close(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_open(self):
        print("action_open")
        current = self.ids[0]
        work_ids = []
        for tt in self.work_ids.ids:
            work_ids.append(tt)
        butt_valider = False
        return {
            'name': 'Taches Affectées',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            'target': 'current',
            'res_model': 'project.task.work',
            'context': {
                'default_active_ids': work_ids,
                'default_ids': work_ids,
                'default_butt_valider': butt_valider,
            },
            'domain': [('id', 'in', work_ids)],
        }

    def button_cancel(self):
        print("button cancel")
        work_obj = self.env['project.task.work']
        line_obj = self.env['base.invoices.merge.automatic.wizard']
        line_obj1 = self.env['base.invoices.merge.line']
        work_line = self.env['project.task.work']
        emp_obj = self.env['hr.employee']
        this = self

        for tt in this.work_ids:
            for msg_id in tt.ids:
                wk = work_obj.browse(msg_id)
                if this.types_affect == 'intervenant':

                    if this.employee_id2 and str(wk.affect_emp_list).find(
                            str(this.employee_id2.user_id.id)) != -1 and wk.state == 'affect':
                        wk.write({'employee_ids_production': [(3, this.employee_id2.id)]})
                        print('types_affect', this.types_affect)
                        intervenants_affect_records = self.env['intervenants.affect'].search([
                            ('employee_id', '=', self.employee_id2.id),
                            ('task_work_id', '=', wk.id),
                            ('types_affect', '=', this.types_affect)
                        ])
                        intervenants_affect_records.unlink()

                        work_line.write({'state': 'draft'})
                        work_line.write({
                            'job': '',
                            'current_emp': False,
                            'employee_id': False,
                            'state': 'draft',
                        })
                        print('debug', wk.affect_emp_list.replace(str(this.employee_id2.user_id.id) + ',', ''))
                        wk.update({
                            'affect_emp_list': wk.affect_emp_list.replace(str(this.employee_id2.user_id.id) + ',', ''),
                            'affect_e_l': wk.affect_e_l.replace(str(this.employee_id2.user_id.login) + ',', ''),
                            'affect_emp': wk.affect_emp.replace(
                                str(this.employee_id2.name + ',' if this.employee_id2 else ''), ''),

                        })

                    else:
                        raise ValidationError(
                            _("Champs Intervenant vide ou employée n'existe pas dans liste des intervenants"))
                elif this.types_affect == 'controle':
                    if this.employee_id2 and str(wk.affect_con).find(str(this.employee_id2.name)) != -1:
                        print('types_affect', this.types_affect)
                        print('affect_con_list',
                              wk.affect_con_list.replace(str(this.employee_id2.user_id.id) + ',', ''))
                        intervenants_affect_records = self.env['intervenants.affect'].search([
                            ('employee_id', '=', self.employee_id2.id),
                            ('task_work_id', '=', wk.id),
                            ('types_affect', '=', this.types_affect)
                        ])
                        intervenants_affect_records.unlink()
                        wk.update({
                            'employee_ids_controle': [(3, this.employee_id2.id)],
                            'affect_con_list': wk.affect_con_list.replace(str(this.employee_id2.user_id.id) + ',', ''),
                            'affect_con': wk.affect_con.replace(str(this.employee_id2.name) + ',', ''),
                        })
                    else:
                        raise ValidationError(
                            _("Champs Intervenant vide ou employée n'existe pas dans liste des controleurs"))
                elif this.types_affect == 'correction':
                    if this.employee_id2 and str(wk.affect_cor).find(str(this.employee_id2.name)) != -1:
                        intervenants_affect_records = self.env['intervenants.affect'].search([
                            ('employee_id', '=', self.employee_id2.id),
                            ('task_work_id', '=', wk.id),
                            ('types_affect', '=', this.types_affect)
                        ])
                        intervenants_affect_records.unlink()
                        wk.write({
                            'employee_ids_correction': [(3, this.employee_id2.id)],
                            'affect_cor_list': wk.affect_cor_list.replace(str(this.employee_id2.id) + ',', ''),
                            'affect_cor': wk.affect_cor.replace(str(this.employee_id2.name) + ',', ''),
                        })
                    else:
                        raise ValidationError(
                            _("Champs Intervenant vide ou employée n'existe pas dans liste des correcteurs"))

                for rec in self:
                    if self.env.cr.dbname == 'DEMOddddddd':
                        sql = "SELECT field_250 FROM app_entity_26 WHERE id = %s"
                        self.env.cr.execute(sql, (wk.id,))
                        datas = self.env.cr.fetchone()

                        if datas:
                            sql1 = "UPDATE app_entity_26 SET field_269 = %s WHERE id = %s"
                            self.env.cr.execute(sql1, ('', wk.id))

                            sql2 = "UPDATE app_entity_26 SET field_244 = %s WHERE id = %s"
                            self.env.cr.execute(sql2, ('72', wk.id))

                        self.env.cr.commit()

                line_obj1.browse(tt.id).write({'state': 'draft'})

            # line_obj1.write({'state': 'draft'})

        # if this.mail_send == 'yes':
        #     if not this.note:
        #         this.note = ' '
        #     if not this.employee_ids:
        #         raise ValidationError(_('Erreur ! Vous devez sélectionner un destinataire.'))
        #     else:
        #         kk = ''
        #         for line in this.employee_ids.ids:
        #             emp = emp_obj.browse(line)
        #             kk = kk + emp.work_email + ','
        #         this.to = kk
        #         if this.employee_ids1:
        #             ll = ''
        #             for line in this.employee_ids1.ids:
        #                 emp = emp_obj.browse(line)
        #                 ll = ll + emp.work_email + ','
        #             this.cc = ll
        #         if this.employee_ids2:
        #             mm = ''
        #             for line in this.employee_ids2.ids:
        #                 emp = emp_obj.browse(line)
        #                 mm = mm + emp.work_email + ','
        #             this.cci = mm
        #
        # this.state = 'draft'
        # self.env['email.template'].sudo().browse(33).send_mail(this.id, force_send=True)
        #
        line_obj.write({'state': 'draft'})

        view = self.env['sh.message.wizard']
        view_id = view and view.id or False

        return {
            'name': 'Annulataion d"affectation faite avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',

        }

    # def action_calendar(self, cr, uid, ids, context=None):
    #     current = ids[0]
    #     list = []
    #     l = []
    #     this = self.browse(cr, uid, current, context=context)
    #     if this.employee_id2:
    #         cr.execute('select id from project_task_work where employee_id= %s and state=%s',
    #                    (this.employee_id2.id, 'affect',))
    #         work_ids = cr.fetchall()
    #     else:
    #         dep = self.pool.get('hr.academic').search(cr, uid, [('categ_id', '=', this.categ_id.id)])
    #         if dep:
    #             for nn in dep:
    #                 em = self.pool.get('hr.academic').browse(cr, uid, nn).employee_id.id
    #
    #                 l.append(em)
    #         today_date = datetime.today()
    #         from_d = today_date - relativedelta(months=2)
    #         to_d = today_date + relativedelta(months=2)
    #
    #         cr.execute(
    #             'select id from project_task_work where employee_id in %s and state not in %s and employee_id is not null and date_start>=%s and date_start<=%s',
    #             (tuple(l), ('valid', 'cancel', 'pending'), from_d, to_d,))
    #         work_ids = cr.fetchall()
    #     ##     raise osv.except_osv(_('Error !'), _('No period defined for this date: %s !\nPlease create one.')%len(work_ids))
    #     ##            raise osv.except_osv(_('Error !'), _('Vous devez sélectionner un employé pour consulter son calendrier'))
    #
    #     for tt in work_ids:
    #         list.append(tt)
    #
    #     return {
    #         'name': ('Calendrier Ressources'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'timeline',
    #         ##  'target'        :   'popup',
    #         'nodestroy': True,
    #
    #         'target': 'popup',
    #         'res_model': 'project.task.work',
    #         ## 'res_id': ids[0],
    #         'context': {'default_active_ids': list, 'default_ids': list},
    #         'domain': [('id', 'in', list)]
    #     }
    #
    # def action_calendar(self):
    #     current = self.ids[0]
    #     work_ids = []
    #     employee_id2 = self.employee_id2
    #
    #     if employee_id2:
    #         work_ids = self.env['project.task.work'].search(
    #             [('employee_id', '=', employee_id2.id), ('state', '=', 'affect')]).ids
    #     else:
    #         l = []
    #         dep = self.env['hr.academic'].search([('categ_id', '=', self.categ_id.id)])
    #         if dep:
    #             for nn in dep:
    #                 em = nn.employee_id.id
    #                 l.append(em)
    #
    #         today_date = datetime.today()
    #         from_d = today_date - relativedelta(months=2)
    #         to_d = today_date + relativedelta(months=2)
    #
    #         work_ids = self.env['project.task.work'].search([
    #             ('employee_id', 'in', l),
    #             ('state', 'not in', ('valid', 'cancel', 'pending')),
    #             ('employee_id', '!=', False),
    #             ('date_start', '>=', from_d),
    #             ('date_start', '<=', to_d)
    #         ]).ids
    #
    #     list_ids = work_ids
    #
    #     return {
    #         'name': ('Calendrier Ressources'),
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'timeline',
    #         'nodestroy': True,
    #         'target': 'popup',
    #         'res_model': 'project.task.work',
    #         'context': {
    #             'default_active_ids': list_ids,
    #             'default_ids': list_ids
    #         },
    #         'domain': [('id', 'in', list_ids)]
    #     }

    def button_save_(self):
        this = self
        work_obj = self.env['base.invoices.merge.automatic.wizard']
        work_line = self.env['project.task.work']

        for line in this.work_ids:
            line = line

        return {
            'name': ('Affectation les Travaux'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'base.invoices.merge.automatic.wizard',
            'res_id': this.id,
            'context': {},
            'domain': []
        }

    def button_load_mail(self):
        this = self
        work_obj = self.env['base.invoices.merge.automatic.wizard']
        kk = []

        if this.employee_id2 and this.employee_id2.id not in kk:
            kk.append(this.employee_id2.id)

        for jj in kk:
            self.env.cr.execute("INSERT INTO base_invoices_merge_automatic_wizard_hr_employee_rel VALUES (%s,%s)",
                                (this.id, jj))

        return {
            'name': ('Affectation les Travaux'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('eb_invoices_wizard.your_view_id').id,  # Replace with the actual view ID
            'target': 'new',
            'res_model': 'base.invoices.merge.automatic.wizard',
            'res_id': this.id,
            'domain': []
        }

    def message_(self):
        view = self.env.ref('sh_message.sh_message_wizard')  # Replace with the actual view ID

        return {
            'name': 'Affectation faite avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': self.env.context
        }

    def button_approve(self):
        print("button_approve")

        settings_custom = self.env['settings.custom'].search([('affectation_multiple', '=', 0)], limit=1)
        print('settings_custom : ', settings_custom)
        if settings_custom:
            self.affecter_multiple()
        else:
            self.affecter_simple()

        view = self.env['sh.message.wizard']
        view_id = view and view.id or False
        return {
            'name': 'Affectation faite avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': {'default_state': 'affect'},

        }

    def create_histo_affect(self, employee_id, types_affect, date_affectation, wk_id):
        intervenants_affect = self.env['intervenants.affect']
        intervenants_affect.create({
            'name': employee_id.name,
            'employee_id': employee_id.id,
            'types_affect': types_affect,
            'date_affectation': date_affectation,
            'task_work_id': wk_id
        })

    def create_histo_line(self, type_histo, execute_by, create_by, work_histo_id, date_histo, coment1):
        self.env['work.histo.line'].create({
            'type': type_histo,
            'execute_by': execute_by,
            'create_by': create_by,
            'work_histo_id': work_histo_id,
            'date': date_histo,
            'coment1': coment1 or False,
            'id_object': self.ids[0],
        })

    def create_work_histo(self, wk):
        histo = self.env['work.histo'].create({
            'task_id': wk.task_id.id,
            'work_id': wk.id,
            'categ_id': wk.categ_id.id,
            'product_id': wk.product_id.id,
            'name': wk.task_id,
            'date': wk.date_start,
            'create_a': wk.date_start,
            'zone': wk.zo or 0,
            'secteur': wk.sect or 0,
            'project_id': wk.project_id.id,
            'partner_id': wk.project_id.partner_id.id,
        })

        return histo

    def affecter_simple(self):
        print("affecter_simple")

        for line in self.work_ids:
            line = self.env['project.task.work'].browse(line.id)
            if line.state == 'draft':
                self.affecter_multiple()
                break
            else:
                self.duplicate_and_affect_task()
                break
        return

    def get_new_group_work_id(self, project_task_work):
        max_work_group_id = project_task_work.search([], order='work_group_id desc',
                                                     limit=1).work_group_id
        return max_work_group_id + 1

    def get_matching_prod_work_ids(self, ):

        first_work_id = self.work_ids and self.work_ids[0].name or ''
        self.env.cr.execute(
            "SELECT id FROM project_task_work WHERE name = %s AND project_id = %s AND work_group_id = %s AND to_duplicate = %s",
            (first_work_id, self.work_ids.project_id.id, self.work_ids[0].work_group_id, True))
        return [row[0] for row in self.env.cr.fetchall()]

    def duplicate_task(self, project_task_work, work, new_work_group_id, to_duplicate):
        new_work = project_task_work.create({
            'name': work.name,
            'product_id': work.product_id.id,
            'project_id': work.project_id.id,
            'task_id': work.task_id.id,
            'partner_id': work.partner_id.id,
            'kit_id': work.kit_id.id,
            'categ_id': work.categ_id.id,
            'hours': work.hours,
            'date_start': work.date_start,
            'date_end': work.date_end,
            'active': True,
            'sequence': work.sequence,
            'gest_id3': work.gest_id3.id,
            'state': 'draft',
            'work_id': work.id,
            'date_start_r': work.date_start_r,
            'date_end_r': work.date_end_r,
            'poteau_t': work.poteau_t,
            'poteau_r': work.poteau_r,
            'gest_id': work.gest_id.id,
            'uom_id': work.uom_id.id,
            'uom_id_r': work.uom_id_r.id,
            'zone': work.zone,
            'secteur': work.secteur,
            'create_explicitly': True,
            'work_group_id': new_work_group_id,
            'to_duplicate': to_duplicate
        })
        return new_work.id

    def creat_base_group_merge_line(self, product, total, base_group_id, rec):

        res_user = self.env['res.users'].browse(self._uid)
        self.env['base.group.merge.line'].create({
            'create_date': fields.Date.today(),
            'date_start_r': fields.Date.today(),
            'date_end_r': fields.Date.today(),
            'product_id': product,
            'project_id': rec.project_id.id,
            'hours_r': total,
            'uom_id_r': 5,
            'uom_id': 5,
            'wizard_id': base_group_id,
            'color1': 1,
            'employee_id':  res_user.employee_id.id,
            'categ_id': rec.categ_id.id,
            'zone': rec.zone or 0,
            'secteur': rec.secteur or 0
        })

    def create_base_invoices_merge_automatic_wizard(self, rec, total):
        res_user = self.env['res.users'].browse(self._uid)

        move_line = {
            'employee_id': res_user.employee_id.id,
            'state': 'valid',
            'work_id': rec.id,
            'task_id': rec.task_id.id,
            'sequence': rec.sequence,
            'uom_id': 5,
            'date_start_r': fields.Date.today(),
            'date_end_r': fields.Date.today(),
            'categ_id': rec.categ_id.id,
            'hours_r': total,
            'color1': 1,
            'project_id': rec.project_id.id,
            'gest_id': rec.gest_id.id,
            'zone': rec.zone,
            'secteur': rec.secteur,
        }
        self.env['base.invoices.merge.automatic.wizard'].create(move_line)

    def get_product(self, rec):

        product = 80
        if rec.categ_id.id == 3:
            product = 156
        elif rec.categ_id.id == 1:
            product = 80
        elif rec.categ_id.id == 4:
            product = 218
        elif rec.categ_id.id == 6:
            product = 174
        elif rec.categ_id.id == 7:
            product = 197
        elif rec.categ_id.id == 8:
            product = 132
        elif rec.categ_id.id == 5:
            product = 132

        return product

    def create_link_line(self):
        for rec in self.work_ids:
            for line in self.link_ids:
                self.env['link.line'].create({
                    'ftp': line.ftp,
                    'name': line.name,
                    'work_id': rec.id,
                    'affect_id': line.id,
                    'source': 'affectation',
                    'id_record': self.id
                })

    def create_base_group_merge_automatic_wizard(self, rec):
        base_group = self.env['base.group.merge.automatic.wizard'].create({
            'create_date': fields.Date.today(),
            'date_start_r': fields.Date.today(),
            'project_id': rec.project_id.id,
            'zo': rec.zone,
            'sect': rec.secteur,
            'gest_id': rec.gest_id.id,
            'state': 'valid',
            'active': True,
            'name': 'gestion affectation'
        })
        return base_group.id

    def duplicate_and_affect_task(self):
        res_user = self.env['res.users'].browse(self.env.uid)
        link_line = self.env['link.line']
        project_task_work = self.env['project.task.work']
        this = self

        matching_work_ids = []
        new_work_group_id = 0
        to_duplicate = True

        if self.types_affect == 'intervenant':
            new_work_group_id = self.get_new_group_work_id(project_task_work)
            matching_work_ids = self.get_matching_prod_work_ids()

        elif this.types_affect == 'controle' or 'correction':
            first_work_id = self.work_ids.id and self.work_ids[0].id or ''
            self.env.cr.execute("SELECT id FROM project_task_work WHERE id = %s", (first_work_id,))
            matching_work_ids = [row[0] for row in self.env.cr.fetchall()]
            to_duplicate = False
            new_work_group_id = self.work_ids[0].work_group_id
        duplicated_work_ids = []

        for work_id in matching_work_ids:
            work = project_task_work.browse(work_id)
            if work and self.employee_id2:
                # Duplication des taches selectionnés
                new_work_id = self.duplicate_task(project_task_work, work, new_work_group_id, to_duplicate)
                duplicated_work_ids.append(new_work_id)
        prod_work_ids = []
        for new_id in duplicated_work_ids:
            wk = project_task_work.browse(new_id)
            wk_histo = self.env['work.histo'].search([('work_id', '=', new_id)])
            if self.employee_id2 and self.types_affect == 'intervenant' and (
                    'correction' not in wk.product_id.name and 'Contrôle' not in wk.product_id.name):
                prod_work_ids.append(wk.id)
                wk.write({'state': 'affect'})
                self.create_histo_affect(self.employee_id2, self.types_affect,
                                         fields.Date.today(), wk.id)
                wk.write({
                    'employee_ids_production': [(4, self.employee_id2.id)],
                    'current_emp': self.employee_id2.id,
                    'employee_id': self.employee_id2.id,
                    'display': True
                })
                if wk_histo:
                    if len(wk_histo) == 1:
                        wk_histo_id = wk_histo.id
                        self.create_histo_line('affect_inter', self.employee_id2.name,
                                               res_user.employee_id.name,
                                               wk_histo_id, fields.Datetime.now(),
                                               self.note)
                else:
                    histo = self.create_work_histo(wk)

                    self.create_histo_line('affect_inter', self.employee_id2.name,
                                           res_user.employee_id.name,
                                           histo.id, fields.Datetime.now(),
                                           self.note)
            elif this.employee_id2 and this.types_affect == 'controle':
                self.create_histo_affect(this.employee_id2, this.types_affect,
                                         fields.Date.today(), wk.id)
                if wk.state == 'draft':
                    wk.write({'state': 'tovalidcont'})
                wk.write({
                    'employee_ids_controle': [(4, this.employee_id2.id)],
                    'state': 'affect_con',
                })

                if this.group_id:
                    this.group_id.write({'gest_id2': this.employee_id2.id, 'note_con': this.note})
                if wk_histo:
                    if len(wk_histo) == 1:
                        wk_histo_id = wk_histo.id
                        self.create_histo_line('affect_control', this.employee_id2.name, res_user.employee_id.name,
                                               wk_histo_id, fields.Datetime.now(),
                                               this.note)
                else:
                    histo = self.create_work_histo(wk)
                    self.create_histo_line('affect_control', this.employee_id2.name, res_user.employee_id.name,
                                           histo.id, fields.Datetime.now(),
                                           this.note)
            elif self.employee_id2 and self.types_affect == 'correction':
                self.create_histo_affect(this.employee_id2, this.types_affect,
                                         fields.Date.today(), wk.id)
                wk.write({
                    'employee_ids_correction': [(4, this.employee_id2.id)],
                    'state': 'affect_corr',
                })
                if this.group_id:
                    this.group_id.write({'emp_id2': this.employee_id2.id, 'note_corr': this.note})
                if wk_histo:
                    if len(wk_histo) == 1:
                        wk_histo_id = wk_histo.id
                        self.create_histo_line('affect_corr', this.employee_id2.name, res_user.employee_id.name,
                                               wk_histo_id, fields.Datetime.now(),
                                               this.note)
                else:
                    histo = self.create_work_histo(wk)

                    self.create_histo_line('affect_corr', this.employee_id2.name, res_user.employee_id.name,
                                           histo.id, fields.Datetime.now(),
                                           this.note)
            if this.date_start_r:
                wk.write({'date_start': this.date_start_r})
            if this.name:
                wk.write({'job': this.name})
            if this.date_end_r:
                wk.write({'date_end': this.date_end_r})
            if this.poteau_t:
                wk.write({'poteau_t': this.poteau_t})
            if this.ftp:
                link_id = {
                    'name': 'FTP Affectation',
                    'ftp': this.ftp,
                    'work_id': wk.id
                }
                link_line.create(link_id)
            if this.note:
                wk.write({'note': this.note})
            if wk.employee_id:
                self._cr.execute('update project_task_work set current_emp =%s where id=%s ',
                                 (wk.employee_id.id, wk.id))
        self.write({'state': 'affect'})
        vals = self.time_ch.split(':')
        t, hours = divmod(float(vals[0]), 24)
        t, minutes = divmod(float(vals[1]), 60)
        minutes = minutes / 60.0
        total = hours + minutes
        if self.work_ids:
            for rec in self.work_ids:
                base_group_id = self.create_base_group_merge_automatic_wizard(rec)
                product = self.get_product(rec)
                self.creat_base_group_merge_line(product, total, base_group_id, rec)
                self.create_base_invoices_merge_automatic_wizard(rec, total)
            self.create_link_line()

    def affecter_multiple(self):
        link_line = self.env['link.line']
        res_user = self.env['res.users'].browse(self.env.uid)
        project_task_work = self.env['project.task.work']
        this = self

        for work_id in this.work_ids:
            line = project_task_work.browse(work_id.id)
            if this.employee_id2 and this.types_affect == 'intervenant' and line.state == 'draft':
                line.write({'state': 'affect'})
            for line_id in line.ids:
                wk = project_task_work.browse(line_id)
                wk_histo = self.env['work.histo'].search([('work_id', '=', line_id)])

                if this.employee_id2 and this.types_affect == 'intervenant':
                    if wk.state == 'draft':
                        wk.write({'state': 'affect'})
                        self.create_histo_affect(this.employee_id2, this.types_affect,
                                                 fields.Date.today(), wk.id)
                    wk.write({
                        'employee_ids_production': [(4, this.employee_id2.id)],
                        'current_emp': this.employee_id2.id,
                        'employee_id': this.employee_id2.id,
                        'display': True
                    })

                    if wk_histo:
                        if len(wk_histo) == 1:
                            wk_histo_id = wk_histo.id
                            self.create_histo_line('affect_inter', this.employee_id2.name, res_user.employee_id.name,
                                                   wk_histo_id, fields.Datetime.now(),
                                                   this.note)
                    else:
                        histo = self.create_work_histo(wk)

                        self.create_histo_line('affect_inter', this.employee_id2.name, res_user.employee_id.name,
                                               histo.id, fields.Datetime.now(),
                                               this.note)
                elif this.employee_id2 and this.types_affect == 'controle':

                    self.create_histo_affect(this.employee_id2, this.types_affect,
                                             fields.Date.today(), wk.id)
                    if wk.state == 'affect':
                        wk.write({'state': 'tovalidcont'})

                    wk.write({
                        'employee_ids_controle': [(4, this.employee_id2.id)],
                        'state': 'affect_con',
                    })

                    if this.group_id:
                        this.group_id.write({'gest_id2': this.employee_id2.id, 'note_con': this.note})

                    if wk_histo:
                        if len(wk_histo) == 1:
                            wk_histo_id = wk_histo.id
                            self.create_histo_line('affect_control', this.employee_id2.name, res_user.employee_id.name,
                                                   wk_histo_id, fields.Datetime.now(),
                                                   this.note)

                    else:
                        histo = self.create_work_histo(wk)

                        self.create_histo_line('affect_control', this.employee_id2.name, res_user.employee_id.name,
                                               histo.id, fields.Datetime.now(),
                                               this.note)

                elif this.employee_id2 and this.types_affect == 'correction':
                    self.create_histo_affect(this.employee_id2, this.types_affect,
                                             fields.Date.today(), wk.id)
                    wk.write({
                        'employee_ids_correction': [(4, this.employee_id2.id)],
                        'state': 'affect_corr',
                    })
                    if this.group_id:
                        this.group_id.write({'emp_id2': this.employee_id2.id, 'note_corr': this.note})
                    if wk_histo:
                        if len(wk_histo) == 1:
                            wk_histo_id = wk_histo.id
                            self.create_histo_line('affect_corr', this.employee_id2.name, res_user.employee_id.name,
                                                   wk_histo_id, fields.Datetime.now(),
                                                   this.note)
                    else:
                        histo = self.create_work_histo(wk)

                        self.create_histo_line('affect_corr', this.employee_id2.name, res_user.employee_id.name,
                                               histo.id, fields.Datetime.now(),
                                               this.note)
                if this.date_start_r:
                    wk.write({'date_start': this.date_start_r})
                if this.name:
                    wk.write({'job': this.name})
                if this.date_end_r:
                    wk.write({'date_end': this.date_end_r})
                if this.poteau_t:
                    wk.write({'poteau_t': this.poteau_t})
                if this.ftp:
                    link_id = {
                        'name': 'FTP Affectation',
                        'ftp': this.ftp,
                        'work_id': wk.id
                    }
                    link_line.create(link_id)
                if this.note:
                    wk.write({'note': this.note})
                if wk.employee_id:
                    self._cr.execute('update project_task_work set current_emp =%s where id=%s ',
                                     (wk.employee_id.id, wk.id))
            self.write({'state': 'affect'})

            vals = self.time_ch.split(':')
            t, hours = divmod(float(vals[0]), 24)
            t, minutes = divmod(float(vals[1]), 60)
            minutes = minutes / 60.0
            total = hours + minutes

        if self.work_ids:
            for rec in self.work_ids:
                base_group_id = self.create_base_group_merge_automatic_wizard(rec)
                product = self.get_product(rec)
                self.creat_base_group_merge_line(product, total, base_group_id, rec)
                self.create_base_invoices_merge_automatic_wizard(rec, total)
            self.create_link_line()


class ProjectTaskWorkLine(models.Model):
    _inherit = 'project.task.work.line'

    wizard_id = fields.Many2one('base.invoices.merge.automatic.wizard', string='Event')
    group_id2 = fields.Many2one('base.group.merge.automatic.wizard', string='N.U', select="1", readonly=True,
                                states={'draft': [('readonly', False)]})


class LinkLine(models.Model):
    _inherit = 'link.line'

    affect_id = fields.Many2one('base.invoices.merge.automatic.wizard', string='link')
