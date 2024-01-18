# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import time


class WlShow(models.TransientModel):
    _name = 'wl.show'

    def _get_user(self):
        res = []
        employee_id = self.env['res.users'].browse(self.env.uid).employee_id
        if employee_id:
            if employee_id.is_super:
                res.append(employee_id.id)
        if len(res) > 0:
            return res[0]
        else:
            return False

    def _get_user1(self):
        res = []
        employee_id = self.env['res.users'].browse(self.env.uid).employee_id
        if employee_id:
            if not employee_id.is_super:
                res.append(employee_id.id)
        if len(res) > 0:
            return res[0]
        else:
            return False

    def _get_depart(self):
        res = []
        employee_id = self.env['res.users'].browse(self.env.uid).employee_id
        if employee_id:
            for aca in employee_id.academic_ids:
                depart_id = self.env['hr.academic'].browse(aca.id)
                res.append(depart_id.categ_id.id)

        else:
            tt = self.env['product.category'].search([]).ids
            for ac in tt:
                res.append(ac)
        if len(res) == 1 and res[0] == 6:
            res = res[0]
        return res

    current_uid = fields.Char('Litigation')
    categ_id = fields.Many2one('product.category', string='Tags', default=_get_depart)
    date_from = fields.Date('date de', select=True, default=time.strftime('%Y-01-01'))
    date_to = fields.Date(u'date a', select=True, default=time.strftime('%Y-12-31'))
    send = fields.Boolean('Litigation', default=True)
    checked = fields.Boolean('Litigation')
    all1 = fields.Boolean('Litigation')
    name = fields.Char('Litigation', default='Mod. Rech.')
    partner_id = fields.Many2one('res.partner', 'Nationality')
    employee_id = fields.Many2one('hr.employee', 'Task', default=_get_user1)
    project_id = fields.Many2one('project.project', 'Nationality')
    project_ids = fields.Many2many('project.project', 'work_show_project_rel', 'project_id', 'work_id',
                                   'Projects', )
    task_id = fields.Many2one('project.task', 'Nationality')
    work_id = fields.Many2one('project.task.work', 'Nationality')
    product_id = fields.Many2one('product.product', 'Nationality')
    user_id = fields.Many2one('hr.employee', 'Nationality', default=_get_user)
    state = fields.Selection([
        ('draft', 'T. Planifiés'),
        ('affect', 'T. Affectés'),
        ('tovalid', 'T.Encours'),
        ('valid', 'T.Terminés'),
        ('cancel', 'T. Annulés'),
        ('pending', 'T. Suspendus'),
    ],
        'Status', copy=False)
    type = fields.Selection([
        ('tableau', 'Tableau'),
        ('kanban', 'Kanban'),
    ],
        'Status', copy=False, default='tableau')
    inv_emp = fields.Selection([
        ('f', 'Travaux Facturés'),
        ('nf', 'Travaux Non Facturés'),
        ('all', 'Tous les Travaux'),
    ],
        'Status', copy=False)
    inv_cust = fields.Selection([
        ('f', 'Travaux Facturés'),
        ('nf', 'Travaux Non Facturés'),
        ('all', 'Tous les Travaux'),

    ],
        'Status', copy=False)

    def _get_all_partners(self):
        return self.env['res.partner'].search([]).ids

    def _get_all_users(self):
        return self.env['hr.employee'].search([]).ids

    def _get_all_employees(self):
        return self.env['hr.employee'].search([]).ids

    def _get_all_projects(self):
        return self.env['project.project'].search([]).ids

    def _get_all_tasks(self):
        return self.env['project.task'].search([]).ids

    def _get_all_categs(self):
        categ = self.env['product.category'].search([]).ids
        categ.append(False)
        return categ

    def _get_all_products(self):
        return self.env['product.product'].search([]).ids

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        str1 = ''
        return {'value': {'current_uid': str1}}

    @api.onchange('categ_id')
    def onchange_place(self):
        res = {}
        emp = self.env['res.users'].browse(self.env.uid)
        if self.categ_id and (emp.employee_id.id != 63) and (
                emp.employee_id.id != 80):  # on old api it will return id, instead of record
            r = []

            dep = self.env['hr.academic'].search([('categ_id', '=', self.categ_id)]).ids

            if dep:
                for nn in dep:
                    em = self.env['hr.academic'].browse(nn).employee_id.id

                    r.append(em)
            res['domain'] = {'employee_id': [('id', 'in', r)]}
        return res

    def delete(self):
        """
        Action that shows the list of (non-draft) account moves from
        the selected journals and periods, so the user can review
        the renumbered account moves.
        """
        wiz_form = self[0]
        if wiz_form.project_ids:
            self.env.cr.execute("delete from work_show_project_rel  where project_id =%s" % (self.ids[0]))
        return True

    @api.onchange('categ_id', 'date_from')
    def onchange_date_from(self):
        res = {}
        if self.date_from:  # on old api it will return id, instead of record
            r = []
            z = []
            k = []
            emp = self.env['res.users'].browse(self.env.uid)
            if emp.employee_id and (emp.employee_id.id != 63) and (emp.employee_id.id != 80):
                dep1 = self.env['hr.academic'].search([('employee_id', '=', emp.employee_id.id)]).ids
                if dep1:
                    for ll in dep1:
                        c = self.env['hr.academic'].browse(ll).categ_id
                        if c and c.id not in k:
                            k.append(c.id)

                    for nn in k:
                        dep = self.env['hr.academic'].search([('categ_id', '=', nn)]).ids
                        if dep:
                            for jj in dep:
                                em = self.env['hr.academic'].browse(jj).employee_id
                                if em.id and em.id not in r:
                                    r.append(em.id)
                                    if em.is_super is True and em.id not in z:
                                        z.append(em.id)

                res['domain'] = {'categ_id': [('id', 'in', k)], 'employee_id': [('id', 'in', r)],
                                 'user_id': [('id', 'in', z)]}

        return res

    def show_results(self):
        # if context is None:
        #     context = {}
        wiz_form = self[0]
        if wiz_form.user_id:
            user_ids = [j.id for j in wiz_form.user_id]
        else:
            user_ids = self._get_all_users()
        if wiz_form.partner_id:
            partner_ids = [j.id for j in wiz_form.partner_id]
        else:
            partner_ids = self._get_all_partners()
        if wiz_form.checked:
            partner_ids.append('')
        if wiz_form.project_id:
            project_ids = [j.id for j in wiz_form.project_id]
        elif wiz_form.project_ids:
            project_ids = wiz_form.project_ids.ids
        else:
            project_ids = self._get_all_projects()
        if wiz_form.checked:
            project_ids.append('')
        if wiz_form.categ_id:
            categ_ids = [j.id for j in wiz_form.categ_id]
        else:
            categ_ids = self._get_all_categs()
        if wiz_form.task_id:
            task_ids = [j.id for j in wiz_form.task_id]
        else:
            task_ids = self._get_all_tasks()
        if wiz_form.product_id:
            product_ids = [j.id for j in wiz_form.product_id]
        else:
            product_ids = self._get_all_products()
        if wiz_form.inv_cust == 'f':
            send = True
        elif wiz_form.inv_cust == 'nf':
            send = False
        else:
            send = True or False
        if wiz_form.inv_emp == 'f':
            send1 = True
        elif wiz_form.inv_cust == 'nf':
            send1 = False
        else:
            send1 = True or False
        states = [
            'close',
            'treat',
            'paid',
        ]
        user = self.env['res.users'].browse(self.env.uid)
        if user.id == 1:
            if wiz_form.inv_emp == 'all':
                if wiz_form.inv_cust == 'all':
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('project_id','in', %s),('product_id','in', %s),('categ_id','in', %s),('done3','=', True)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, project_ids, product_ids, categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
                else:
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('project_id','in', %s),('product_id','in', %s),('facture','=', %s),('categ_id','in', %s),('done3','=', True)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, project_ids, product_ids, send,
                            categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
            else:
                if wiz_form.inv_cust == 'all':
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('project_id','in', %s),('product_id','in', %s),('done3','=', True),('done1','=', %s),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, project_ids, product_ids,
                            send1,
                            categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
                else:
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('project_id','in', %s),('product_id','in', %s),('facture','=', %s),('done3','=', True),('done1','=', %s),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, project_ids, product_ids,
                            send,
                            send1, categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
        else:
            if wiz_form.inv_emp == 'all':
                if wiz_form.inv_cust == 'all':
                    res = {
                        'type': 'ir.actions.act_window',

                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('project_id','in', %s),('product_id','in', %s),('done3','=', True),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, project_ids, product_ids, categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'views': [[self.env.ref('task_work.view_work_line_tree').id, 'tree'],
                                  [self.env.ref('task_work.view_work_line_search').id, 'search']],
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
                else:
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('project_id','in', %s),('product_id','in', %s),('facture','=', %s),('done3','=', True),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, project_ids, product_ids, send,
                            categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'views': [[self.env.ref('task_work.view_work_line_tree').id, 'tree'],
                                  [self.env.ref('task_work.view_work_line_search').id, 'search']],
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
            else:
                if wiz_form.inv_cust == 'all':
                    res = {
                        'type': 'ir.actions.act_window',
                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('project_id','in', %s),('product_id','in', %s),('done3','=', True),('done1','=', %s),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, project_ids, product_ids,
                            send1,
                            categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'views': [[self.env.ref('task_work.view_work_line_tree').id, 'tree'],
                                  [self.env.ref('task_work.view_work_line_search').id, 'search']],
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
                else:
                    res = {
                        'type': 'ir.actions.act_window',

                        'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('project_id','in', %s),('product_id','in', %s),('facture','=', %s),('done3','=', True),('done1','=', %s),('categ_id','in', %s)]" % (
                            wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, project_ids, product_ids,
                            send,
                            send1, categ_ids),
                        'name': _(" "),
                        'view_type': 'form',
                        'view_mode': 'tree,gantt,calendar,graph',
                        'res_model': 'project.task.work.line',
                        'views': [[self.env.ref('task_work.view_work_line_tree').id, 'tree'],
                                  [self.env.ref('task_work.view_work_line_search').id, 'search']],
                        'nodestroy': True,
                        'target': 'current',
                        'limit': 5000, }
                    return res
