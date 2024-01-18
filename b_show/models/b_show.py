# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time


class BShow(models.TransientModel):
    _name = 'b.show'

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

    categ_id = fields.Many2one('product.category', string='Tags', default=_get_depart)
    date_from = fields.Date('date de', select=True, default=time.strftime('%Y-01-01'))
    date_to = fields.Date(u'date a', select=True, default=time.strftime('%Y-12-31'))
    send = fields.Boolean('Litigation')
    product_id = fields.Many2one('product.product', 'Nationality')
    employee_id = fields.Many2one('hr.employee', string='Employee', default=_get_user1)
    gest_id = fields.Many2one('hr.employee', string='Gestionnaire', default=_get_user)
    name = fields.Char('Litigation', default='Mod. Rech.')
    partner_id = fields.Many2one('res.partner', 'Nationality')
    project_id = fields.Many2one('project.project', 'Nationality')
    project_ids = fields.Many2many('project.project', string='Tags')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('tovalid', 'Dde Validation'),
        ('valid', 'Bons Validés')],
        'Status', copy=False),
    inv_emp = fields.Selection([
        ('f', 'Bons Facturés'),
        ('nf', 'Bons Controlés Non Facturés'),
        ('all', 'Tous les Bons'),
    ], 'Status', copy=False)
    critere = fields.Char('critère', default='Gestion')

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
                                 'gest_id': [('id', 'in', z)]}
        return res

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

    def _get_all_partners(self):
        return self.env['res.partner'].search([]).ids

    def _get_all_products(self):
        return self.env['product.product'].search([]).ids

    def _get_all_employees(self):
        return self.env['hr.employee'].search([]).ids

    def _get_all_users(self):
        return self.env['hr.employee'].search([]).ids

    def _get_all_projects(self):
        return self.env['project.project'].search([]).ids

    def _get_all_categs(self):
        return self.env['product.category'].search([]).ids

    def show_results1(self):

        wiz_form = self[0]
        this1 = [False]
        data = self.read([])[0]
        if wiz_form.gest_id:
            user_ids = [j.id for j in wiz_form.gest_id]
        else:
            user_ids = self._get_all_employees()
            for id in user_ids:
                this1.append(id)
                user_ids = this1
        if wiz_form.gest_id:
            user_ids1 = [j.id for j in wiz_form.gest_id]
        else:
            user_ids1 = False
        if wiz_form.partner_id:
            partner_ids = [j.id for j in wiz_form.partner_id]
        else:
            partner_ids = self._get_all_partners()
        if wiz_form.employee_id:
            employee_ids = [j.id for j in wiz_form.employee_id]
        else:
            employee_ids = self._get_all_employees()

        state = data.get('state')
        if not state:
            state_new = [
                'draft',
                'tovalid',
                'valid',
            ]
        else:
            state_new = [state]
        if wiz_form.categ_id:
            categ_ids = [j.id for j in wiz_form.categ_id]
        else:
            categ_ids = self._get_all_categs()
        tt = [False]
        if wiz_form.project_id:
            project_ids = [wiz_form.project_id.id]
        else:
            proj_ids = self.env['project.project'].search([('state', '<>', 'draft')]).ids
            for kk in proj_ids:
                tt.append(kk)
            project_ids = tt
        if wiz_form.product_id:
            product_ids = [j.id for j in wiz_form.product_id]
        else:
            product_ids = self._get_all_products()
            product_ids.append(None)
            product_ids.append(False)
        if wiz_form.critere:
            res = {
                'type': 'ir.actions.act_window',
                'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime("
                          "'%s'))),('categ_id','in', %s),('employee_id','in', %s),('project_id','in', %s),('name',"
                          "'ilike', '%s')]" % (
                              wiz_form.date_from, wiz_form.date_to, categ_ids, employee_ids, project_ids,
                              wiz_form.critere),
                'name': _(" "),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': self.env.ref('bon_show.view_show_line2_tree').id,
                'res_model': 'bon.show.line2',
                'context': {},
                'nodestroy': True,
                'target': 'current',
                'limit': 5000, }
        else:
            res = {
                'type': 'ir.actions.act_window',
                'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime("
                          "'%s'))),('categ_id','in', %s),('employee_id','in', %s),('project_id','in', %s),('product_id','in', %s)]" % (
                              wiz_form.date_from, wiz_form.date_to, categ_ids, employee_ids, project_ids, product_ids),
                'name': _(" "),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': self.env.ref('bon_show.view_show_line2_tree').id,
                'res_model': 'bon.show.line2',
                'context': {},
                'nodestroy': True,
                'target': 'current',
                'limit': 5000, }

        return res

    def show_results1_(self):
        """
        Action that shows the list of (non-draft) account moves from
        the selected journals and periods, so the user can review
        the renumbered account moves.
        """

        # if context is None:
        #     context = {}

        wiz_form = self[0]
        this1 = [False]
        data = self.read([])[0]

        if wiz_form.gest_id:
            user_ids = [j.id for j in wiz_form.gest_id]
        else:
            user_ids = self._get_all_employees()
            for id in user_ids:
                this1.append(id)
                user_ids = this1
        if wiz_form.gest_id:
            user_ids1 = [j.id for j in wiz_form.gest_id]
        else:
            user_ids1 = False
        if wiz_form.partner_id:
            partner_ids = [j.id for j in wiz_form.partner_id]
        else:
            partner_ids = self._get_all_partners()
        if wiz_form.product_id:
            product_ids = [j.id for j in wiz_form.product_id]
        else:
            product_ids = self._get_all_products()
        if wiz_form.employee_id:
            employee_ids = [j.id for j in wiz_form.employee_id]
        else:
            employee_ids = self._get_all_employees()
        if wiz_form.project_ids:
            project_ids = wiz_form.project_ids.ids
        else:
            project_ids = self._get_all_projects()

        state = data.get('state')
        if not state:
            state_new = [
                'draft',
                'tovalid',
                'valid',

            ]

        else:
            state_new = [(state)]
        if wiz_form.categ_id:
            categ_ids = [j.id for j in wiz_form.categ_id]
        else:
            categ_ids = self._get_all_categs()

        if wiz_form.inv_emp == 'all':
            res = {
                'type': 'ir.actions.act_window',
                'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('employee_id','in', %s),('product_id','in', %s),('done3','=', True),('project_id','in', %s)]" % (
                    wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, employee_ids, product_ids,
                    project_ids),
                'name': _(" "),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': self.env.ref('task_work.view_work_line_tree').id,
                'res_model': 'project.task.work.line',
                'context': {},
                'nodestroy': True,
                'target': 'current',
                'flags': {'initial_mode': 'edit'},
                'limit': 5000, }
        elif wiz_form.inv_emp == 'f':
            res = {
                'type': 'ir.actions.act_window',
                'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('employee_id','in', %s),('product_id','in', %s),('done3','=', True),('done1','=', True),('project_id','in', %s)]" % (
                    wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, employee_ids, product_ids,
                    project_ids),
                'name': _(" "),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': self.env.ref('task_work.view_work_line_tree').id,
                'res_model': 'project.task.work.line',
                'context': {},
                'nodestroy': True,
                'target': 'current',
                'flags': {'initial_mode': 'edit'},
                'limit': 5000, }
        elif wiz_form.inv_emp == 'nf':
            res = {
                'type': 'ir.actions.act_window',
                'domain': "[('date_start_r','>=', (time.strftime('%s'))),('date_start_r','<=', (time.strftime('%s'))),('project_id.partner_id','in', %s),('categ_id','in', %s),('employee_id','in', %s),('product_id','in', %s),('done3','=', True),('done1','=', False),('project_id','in', %s)]" % (
                    wiz_form.date_from, wiz_form.date_to, partner_ids, categ_ids, employee_ids, product_ids,
                    project_ids),
                'name': _(" "),
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': self.env.ref('task_work.view_work_line_tree').id,
                'res_model': 'project.task.work.line',
                'context': {},
                'nodestroy': True,
                'target': 'current',
                'flags': {'initial_mode': 'edit'},
                'limit': 5000, }

        return res
