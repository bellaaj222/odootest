from odoo import models, fields, api, _

class YourWizardModel(models.TransientModel):
    _name = 'your.wizard.model'

    work_ids = fields.One2many('project.task.work', 'wizard_id', string="Related Works")

    def default_get(self, fields_list):
        res = super(YourWizardModel, self).default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])

        if self.env.context.get('active_model') == 'project.task.work' and active_ids:
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
                        if not work.is_copy:
                            if not kit_work.is_copy and kit_work.id not in vv:
                                vv.append(kit_work.id)
                        elif work.is_copy:
                            if kit_work.is_copy and kit_work.rank == work.rank and kit_work.id not in vv:
                                vv.append(kit_work.id)

                    res['work_ids'] = [(0, 0, {'work_id': work_id}) for work_id in vv]
                else:
                    res['work_ids'] = [(0, 0, {'work_id': work_id}) for work_id in active_ids]

            r = []
            pref = ''
            test = ''
            list1 = []
            proj = []
            gest_id2 = False
            emp_id2 = False
            for jj in active_ids:
                work = self.env['project.task.work'].browse(jj)
                user = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1).id
                user1 = self.env.uid

                if work.project_id.id not in proj:
                    proj.append(work.project_id.id)

                if work.state == 'pending':
                    raise UserError(_('Action impossible!'), _("Travaux Suspendus!"))
                if work.state == 'draft':
                    raise UserError(_('Action impossible!'), _("Travaux Non Affectés!"))
                if len(proj) > 1:
                    raise UserError(_('Action impossible!'), _("Déclaration se fait uniquement sur un projet!"))

                if work.gest_id.user_id.id == self.env.uid or self.env.uid == 1:
                    done = 1
                else:
                    done = 0

                if work.employee_id.user_id.id == self.env.uid or self.env.uid == 1:
                    done1 = 1
                else:
                    done1 = 0

                if work.affect_cor_list and str(user1) in work.affect_cor_list:
                    type1 = 'correction'
                    emp_id2 = user
                elif work.affect_con_list and str(user1) in work.affect_con_list:
                    type1 = 'controle'
                    gest_id2 = user
                else:
                    type1 = 'bon'

                test = test + pref + str(work.project_id.name) + ' - ' + str(work.task_id.sequence) + ' - ' + str(work.sequence)

                res.update({
                    'states': test,
                    'employee_id': work.employee_id.id,
                    'gest_id': work.gest_id.id,
                    'project_id': work.project_id.id,
                    'zo': work.zo,
                    'sect': work.sect,
                    'categ_id': work.categ_id.id,
                    'coordin_id': work.gest_id3.id,
                    'coordin_id1': work.coordin_id1.id,
                    'coordin_id2': work.coordin_id2.id,
                    'coordin_id3': work.coordin_id3.id,
                    'coordin_id4': work.coordin_id4.id,
                    'coordin_id5': work.coordin_id5.id,
                    'type1': type1,
                    'gest_id2': gest_id2,
                    'emp_id2': emp_id2,
                })

                poteau = 0

                tt = self.env['project.task.work'].search([
                    ('project_id', '=', work.project_id.id),
                    ('categ_id', '=', work.categ_id.id),
                    ('name', 'ilike', 'qualit'),
                    ('etape', '=', work.etape)
                ]).ids

                for ji in tt:
                    work = self.env['project.task.work'].browse(ji)

                    move_line1 = {
                        'product_id': work.product_id.id,
                        'employee_id': work.gest_id.id,
                        'state': 'draft',
                        'work_id': work.id,
                        'task_id': work.task_id.id,
                        'categ_id': work.categ_id.id,
                        'date_start_r': work.date_start_r,
                        'date_end_r': work.date_end_r,
                        'poteau_t': work.poteau_t,
                        'poteau_r': poteau,
                        'project_id': work.task_id.project_id.id,
                        'gest_id': work.gest_id.id,
                        'uom_id': work.uom_id.id,
                        'uom_id_r': work.uom_id_r.id,
                        'zone': work.zone,
                        'secteur': work.secteur,
                    }

                    if tt:
                        list1.append((0, 0, move_line1))

                for task in active_ids:
                    work = self.env['project.task.work'].browse(task)
                    res_user = self.env['res.users'].browse(self.env.uid)
                    categ_ids = self.env['hr.academic'].search([('employee_id', '=', res_user.employee_id.id)])
                    jj = []
                    if categ_ids:
                        for dep in categ_ids:
                            jj.append(dep.categ_id.id)
                    if work.categ_id.id not in jj:
                        raise UserError(_('Action impossible!'), _('Vous n''etes pas autorisé à exécuter cette action sur un département externe'))

            res['work_ids'] = list1
            return res

    @api.model
    def default_get(self, fields):
        res = super(EbMergegroups, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')

        if self.env.context.get('active_model') == 'project.task.work' and active_ids:
            vv = []
            for hh in active_ids:
                work = self.env['project.task.work'].browse(hh)

                dd = []
                if work.kit_id:
                    kit_list = self.env['project.task.work'].search(
                        [('project_id', '=', work.project_id.id), ('zone', '=', work.zone)
                            , ('secteur', '=', work.secteur), ('kit_id', '=', work.kit_id.id),
                         ('product_id.name', 'not ilike', '%correction%'), ('product_id.name', 'not ilike', '%cont%')
                            , ('product_id.name', 'not ilike', '%gestion client%')])
                    for hh in kit_list.ids:

                        work1 = self.env['project.task.work'].browse(hh)
                        if work.is_copy is False:
                            if work1.is_copy is False:
                                if work1.id not in vv:
                                    vv.append(work1.id)
                        else:
                            if work1.is_copy is not False:
                                if work1.rank == work1.rank:
                                    if work1.id not in vv:
                                        vv.append(work1.id)

                    ##raise osv.except_osv(_('Action impossible!'),_("%s")%vv)
                    res['work_ids'] = vv
                else:
                    res['work_ids'] = active_ids
            r = []
            pref = ''
            test = ''
            list = []
            list1 = []
            proj = []
            gest_id2 = False
            emp_id2 = False
            for jj in active_ids:
                work = self.env['project.task.work'].browse(jj)
                user = self.env['hr.employee'].search([('user_id', '=', self._uid)])[0].id
                user1 = self._uid
                if work.project_id.id not in proj:
                    proj.append(work.project_id.id)

                ##                tt=self.env['project.task.work.line'].search([('work_id','=',jj),('state','=','affect')]).ids

                if work.state == 'pending':
                    raise osv.except_osv(_('Action impossible!'), _("Travaux Suspendus!"))
                if work.state == 'draft':
                    raise osv.except_osv(_('Action impossible!'), _("Travaux Non Affectés!"))
                if len(proj) > 1:
                    raise osv.except_osv(_('Action impossible!'), _("Déclaration se fait uniquement sur un projet!"))
                if len(active_ids) > 1:
                    pref = '/'
                # if str(user) not in (work.affect_emp_list or '') :
                # raise osv.except_osv(_('Action impossible!'),_("Vous n'êtes pas affecté pour déclarer un Bon!"))
                done = 0
                if work.gest_id.user_id.id == self._uid or self._uid == 1:
                    done = 1
                else:
                    done = 0
                done1 = 0
                if work.employee_id.user_id.id == self._uid or self._uid == 1:
                    done1 = 1
                else:
                    done1 = 0

                if work.affect_cor_list != False and (str(user1) in work.affect_cor_list):
                    type1 = 'correction'
                    emp_id2 = user

                elif work.affect_con_list != False and (str(user1) in work.affect_con_list):
                    type1 = 'controle'
                    gest_id2 = user
                else:
                    type1 = 'bon'
                    if work.state == 'close':
                        raise osv.except_osv(_('Action impossible!'), _("Travaux Clotués!"))
                    if work.state == 'valid':
                        raise osv.except_osv(_('Action impossible!'), _("Travaux Terminés!"))
                # raise osv.except_osv(_('Action impossible!'),_("%s")%user)
                test = test + pref + str(work.project_id.name) + ' - ' + str(work.task_id.sequence) + ' - ' + str(
                    work.sequence)

                res.update({'states': test, 'employee_id': work.employee_id.id, 'gest_id': work.gest_id.id,
                            'project_id': work.project_id.id
                               , 'zo': work.zo, 'sect': work.sect, 'categ_id': work.categ_id.id,
                            'coordin_id': work.gest_id3.id, 'coordin_id1': work.coordin_id1.id,
                            'coordin_id2': work.coordin_id2.id, 'coordin_id3': work.coordin_id3.id
                               , 'coordin_id4': work.coordin_id4.id, 'coordin_id5': work.coordin_id5.id, 'type1': type1,
                            'gest_id2': gest_id2, 'emp_id2': emp_id2})
                ##for kk in tt:
                ##  pr_lines.append((0,0, {gest_id3
                values = {}

                art = {}

                ##newline= self.env['project.task.work.line'].create(
                ##'aggr_ids': line.id,
                list_intervention = []

                poteau = 0

                tt = self.env['project.task.work'].search(
                    [('project_id', '=', work.project_id.id), ('categ_id', '=', work.categ_id.id),
                     ('name', 'ilike', 'qualit'), ('etape', '=', work.etape)]).ids
                for ji in tt:
                    work = self.env['project.task.work'].browse(ji)

                    move_line1 = {
                        'product_id': work.product_id.id,
                        'employee_id': work.gest_id.id,
                        'state': 'draft',
                        'work_id': work.id,
                        'task_id': work.task_id.id,
                        'categ_id': work.categ_id.id,
                        ##'hours': work.hours,

                        'date_start_r': work.date_start_r,
                        'date_end_r': work.date_end_r,
                        'poteau_t': work.poteau_t,
                        'poteau_r': poteau,
                        ##'poteau_r': work.poteau_r,
                        ## 'hours_r': work.hours_r,
                        ##'color1': work.color1,
                        ## 'total_t':work.color1*7 ,  ##*work.employee_id.contract_id.wage
                        'project_id': work.task_id.project_id.id,

                        ##'amount_line': work.employee_id.contract_id.wage*work.hours_r,
                        ## 'wage': work.employee_id.contract_id.wage,
                        'gest_id': work.gest_id.id,
                        'uom_id': work.uom_id.id,
                        'uom_id_r': work.uom_id_r.id,

                        'zone': work.zone,
                        'secteur': work.secteur,

                    }
                if tt:
                    list1.append([0, 0, move_line1])
                for task in active_ids:
                    work = self.env['project.task.work'].browse(task)
                    context = self._context
                    current_uid = context.get('uid')
                    res_user = self.env['res.users'].browse(current_uid)
                    categ_ids = self.env['hr.academic'].search([('employee_id', '=', res_user.employee_id.id)])
                    jj = []
                    if categ_ids:
                        for ll in categ_ids.ids:
                            dep = self.env['hr.academic'].browse(ll)
                            jj.append(dep.categ_id.id)
                    if work.categ_id.id not in jj:
                        raise osv.except_osv(_('Action impossible!'),
                                             _('Vous n''etes pas autorisé à exécuter cette action sur un département externe'))

            return res