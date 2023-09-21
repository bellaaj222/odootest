# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import datetime, time


class MergeTasksLine(models.Model):
    _name = 'base.task.merge.line'
    _description = 'base_task_merge_line'

    min_id = fields.Integer(string='MinID', order='min_id asc')
    aggr_ids = fields.Char('Ids')
    zone = fields.Char(string="Zone")
    secteur = fields.Char(string="Secteur")
    secteur_to = fields.Char(string="Secteur")
    date_from = fields.Date(string='Wizard')
    date_to = fields.Date(string='Wizard')
    poteau_t = fields.Float('Time Spent')
    is_display = fields.Boolean(string='Ids')
    plans = fields.Char(string='Ids')
    from_int = fields.Integer(string='MinID')
    to_int = fields.Integer(string='MinID')
    employee_id = fields.Many2one('hr.employee', string='Wizard')
    wizard_id = fields.Many2one('base.task.merge.automatic.wizard', string='Wizard')
    plan_id = fields.Many2one('risk.management.response.category', string='Wizard')
    plan_id2 = fields.Many2one('risk.management.response.category', string='Wizard')
    risk_id = fields.Many2one('risk.management.category', string='Wizard')

    def onchange_plan_id_(self, plan_id, plan_id2):
        result = {'value': {}}

        total = 0  #

        if plan_id and plan_id2:
            plan1 = self.env['risk.management.response.category'].browse(
                plan_id)
            plan2 = self.env['risk.management.response.category'].browse(
                plan_id2)

            for x in range(plan_id, plan_id2 + 1):
                plan = self.env['risk.management.response.category'].browse(
                    x)
                if plan:
                    total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit

            result['value']['plans'] = plan1.plan + '-' + plan2.plan

        return result

    def onchange_plans(self, plans):
        result = {'value': {}}
        total = 0
        count = 0

        if plans:
            if plans.count('-') > 1:
                raise ValidationError(_('Erreur !\nFormat Incorrecte!, un seul tiret est autorisé!'))
            elif plans.count('-') == 1 and plans.count(
                    ';') == 0:
                tt = self.env['risk.management.response.category'].search([('plan', '=', plans.split('-')[0])])
                tt1 = self.env['risk.management.response.category'].search([('plan', '=', plans.split('-')[1])])
                if not tt:
                    raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                else:
                    t1 = tt[0]
                if not tt1:
                    raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                else:
                    t2 = tt1[0]
                for x in range(t1, t2):
                    plan = self.env['risk.management.response.category'].browse(x)
                    if plan:
                        total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
            elif plans.count('-') == 1 and plans.count(
                    ';') > 0:
                tt = self.env['risk.management.response.category'].search(
                    [('plan', '=', (plans.split(';')[0]).split('-')[0])])
                tt1 = self.env['risk.management.response.category'].search(
                    [('plan', '=', (plans.split(';')[0]).split('-')[1])])
                if not tt:
                    raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                else:
                    t1 = tt[0]
                if not tt1:
                    raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                else:
                    t2 = tt1[0]
                for x in range(t1, t2):
                    plan = self.env['risk.management.response.category'].browse(x)
                    if plan:
                        total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
                    lst = (plans.split(';')[1]).split(';')
                    for kk in lst:
                        tt2 = self.env['risk.management.response.category'].search([('plan', '=', kk)])
                        if not tt2:
                            raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                        else:
                            plan = self.env['risk.management.response.category'].browse(tt2[0])
                        if plan:
                            total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
            elif plans.count('-') == 0 and plans.count(
                    ';') > 0:
                lst = plans.split(';')
                for kk in lst:
                    for kk in lst:
                        tt2 = self.env['risk.management.response.category'].search([('plan', '=', kk)])
                        if not tt2:
                            raise ValidationError(_('Erreur !\nElement n"est pas dans le tableau de relevé!'))
                        else:
                            plan = self.env['risk.management.response.category'].browse(tt2[0])
                        if plan:
                            total += plan.aerien + plan.ps + plan.souterrain + plan.double_aerien + plan.double_conduit
            else:
                raise ValidationError(
                    _('Erreur !\nFormat Incorrecte!, seuls les tirets "-" ou les points virgules ";" sont autorisés!'))

        result['value'][
            'poteau_t'] = total / 1000
        return result


class EbMergeTasks(models.Model):
    _name = 'base.task.merge.automatic.wizard'
    _description = 'Merge Tasks'
    _rec_name = 'name'

    """
            Action that shows the list of (non-draft) account moves from
            the selected journals and periods, so the user can review
            the renumbered account moves.
            """

    def show_results(self):

        """
        Action that shows the list of (non-draft) account moves from
        the selected journals and periods, so the user can review
        the renumbered account moves.
        """
        current = self.browse(self.ids[0])
        self.env.cr.execute("DELETE FROM base_group_merge_line2 WHERE wiz_id=%s", (current.id,))
        res_cpt = []

        if current.project_id:
            if current.type == '1':
                if not current.task_ids:
                    raise UserError(_('Action impossible!\nVous devez sélectionner les étapes/kits concernées!'))
                if not current.line_ids:
                    raise UserError(_('Action impossible!\nVous devez Mentionner les Zones et Secteurs!'))

                f = []
                v = []

                for tt in current.task_ids.ids:
                    this_p = self.env['project.task'].browse(tt)
                    if this_p.kit_id:
                        v.append(this_p.kit_id.id)
                    else:
                        f.append(this_p.name)

                if len(v) > 0:
                    self.env.cr.execute(
                        'SELECT id FROM project_task_work WHERE project_id= %s AND state IN %s AND kit_id IN %s AND active=TRUE AND is_copy=FALSE',
                        (current.project_id.id, ('draft', 'affect'), tuple(v)))
                    ll = self.env.cr.fetchall()
                else:
                    self.env.cr.execute(
                        'select id from project_task_work where project_id= %s and state in %s and etape in %s',
                        (current.project_id.id, ('draft', 'affect'), tuple(f)))

                    ll = self.env.cr.fetchall()

                if len(f) > 0:
                    self.env.cr.execute(
                        'SELECT project_task_work_id  FROM base_task_merge_automatic_wizard_project_task_work_rel WHERE base_task_merge_automatic_wizard_id = %s ',
                        (current.id,))
                    ll1 = self.env.cr.fetchall()

                    if not ll1:
                        raise UserError(_("Action impossible!\n Merci de sauvegarder le document avant!"))
                    else:

                        for nn in ll1:
                            wrk = self.env['project.task.work'].browse(nn)
                            res_cpt.append(wrk.id)

                    pp = set(ll).intersection(res_cpt)
                else:
                    res_cpt = ll
            elif current.type == '2':
                w = []
                v = []
                for tt in current.task_ids.ids:
                    this_p = self.env['project.task'].browse(tt)
                    if this_p.kit_id:
                        v.append(this_p.kit_id.id)
                    else:
                        w.append(this_p.name)
                if len(v) > 0:
                    self.env.cr.execute(
                        'select id from project_task_work where project_id= %s and   kit_id in %s and active=True and zone=%s and secteur=%s',
                        (current.project_id.id, tuple(v), current.zone, current.secteur))
                    ll = self.env.cr.fetchall()
                else:

                    self.env.cr.execute(
                        'select id from project_task_work where project_id= %s and   active=True and zone=%s and secteur=%s and etape in %s',
                        (current.project_id.id, current.zone, current.secteur, tuple(w)))
                    ll = self.env.cr.fetchall()
                if len(w) > 0:
                    self.env.cr.execute(
                        'select project_task_work_id  from base_task_merge_automatic_wizard_project_task_work_rel where base_task_merge_automatic_wizard_id = %s ',
                        (current.id,))
                    ll1 = self.env.cr.fetchall()
                    if not ll1:
                        raise UserError(_("Action impossible!'\nMerci de sauvegarder le document avant!"))
                    else:

                        for nn in ll1:
                            wrk = self.env['project.task.work'].browse(nn)
                            res_cpt.append(wrk.id)

                    pp = set(ll).intersection(res_cpt)
                else:
                    res_cpt = ll

            for kk in res_cpt:
                if kk:
                    s2 = self.env['project.task.work'].browse(kk)
                    sequence_w = 0
                    if s2.task_id:
                        self.env.cr.execute(
                            'select sequence from project_task_work where task_id=%s and sequence is not Null order by sequence desc limit 1',
                            (s2.task_id.id,))
                        res = self.env.cr.fetchone()

                    # Checks (alphanumeric, single character, secteur_to > secteur, zone unique)
                    zones = []
                    for jj in current.line_ids:
                        if not (jj.zone.isalnum() and jj.secteur.isalnum() and jj.secteur_to.isalnum()):
                            raise UserError(_('Les Zones et Les Secteurs doivent être Alphanumériques'))
                        if len(jj.zone + jj.secteur + jj.secteur_to) != 3:
                            raise UserError(_('Les Zones et Les Secteurs doivent être des Caractères'))
                        if (jj.secteur.isnumeric() and jj.secteur_to.isalpha()) or (
                                jj.secteur.isalpha() and jj.secteur_to.isnumeric()):
                            raise UserError(_("Les Secteurs de la même Zone doivent être soient numériques soit "
                                              "alphabétiques"))
                        if jj.secteur.upper() > jj.secteur_to.upper():
                            raise UserError(_("Le 'Secteur A' doit précéder le 'Secteur De'"))
                        if jj.zone.upper() in zones:
                            raise UserError(_('Les Zones doivent être Distinctes'))
                        zones.append(jj.zone.upper())

                    for jj in current.line_ids:

                        for hh in range(ord(jj.secteur.upper()), ord(jj.secteur_to.upper()) + 1):
                            if jj.employee_id:
                                employee = jj.employee_id.id
                            else:
                                employee = s2.employee_id.id or False
                            if jj.date_from:
                                date_from = jj.date_from
                            else:
                                date_from = s2.date_start
                            if jj.date_to:
                                date_to = jj.date_to
                            else:
                                date_to = s2.date_end
                            if jj.poteau_t:
                                poteau_t = jj.poteau_t
                            else:
                                poteau_t = s2.poteau_t
                            if jj.is_display is True:
                                is_display = True
                            else:
                                is_display = False
                            if jj.zone == '0':
                                task_name = s2.name + ' - Secteur ' + chr(hh).upper()
                            else:
                                task_name = s2.name + ' - Zone ' + jj.zone.upper() + ' Secteur ' + chr(hh).upper()

                            # Construct the INSERT query
                            sql_query = """

                                INSERT INTO base_group_merge_line2 (
                                    step_id,
                                    task_id,
                                    categ_id,
                                    product_id,
                                    name,
                                    date_start,
                                    date_end,
                                    poteau_i,
                                    poteau_t,
                                    color,
                                    total_t,
                                    project_id,
                                    etape,
                                    gest_id,
                                    employee_id,
                                    uom_id,
                                    uom_id_r,
                                    ftp,
                                    state,
                                    work_id,
                                    sequence,
                                    zone,
                                    secteur,
                                    wiz_id,
                                    is_display,
                                    pos
                                )

                                VALUES (
                                    %(step_id)s,                                    
                                    %(task_id)s,
                                    %(categ_id)s,
                                    %(product_id)s,
                                    %(name)s,
                                    %(date_start)s,
                                    %(date_end)s,
                                    %(poteau_i)s,
                                    %(poteau_t)s,
                                    %(color)s,
                                    %(total_t)s,
                                    %(project_id)s,
                                    %(etape)s,
                                    %(gest_id)s,
                                    %(employee_id)s,
                                    %(uom_id)s,
                                    %(uom_id_r)s,
                                    %(ftp)s,
                                    %(state)s,
                                    %(work_id)s,
                                    %(sequence)s,
                                    %(zone)s,
                                    %(secteur)s,
                                    %(wiz_id)s,
                                    %(is_display)s,
                                    %(pos)s
                                )
                            """

                            # Define the parameters for parameter binding
                            params = {
                                'step_id': s2.step_id.id,
                                'task_id': s2.task_id.id,
                                'categ_id': s2.categ_id.id,
                                'product_id': s2.product_id.id,
                                'name': task_name,
                                'date_start': date_from,
                                'date_end': date_to,
                                'poteau_i': s2.poteau_t,
                                'poteau_t': poteau_t,
                                'color': s2.color,
                                'total_t': s2.total_t,
                                'project_id': s2.project_id.id or None,
                                'etape': s2.etape,
                                'gest_id': s2.gest_id.id or None,
                                'employee_id': employee or None,
                                'uom_id': s2.uom_id.id or None,
                                'uom_id_r': s2.uom_id.id or None,
                                'ftp': s2.ftp,
                                'state': s2.state,
                                'work_id': s2.id,
                                'sequence': res[0] + 1,
                                'zone': jj.zone.upper(),
                                'secteur': chr(hh).upper(),
                                'wiz_id': current.id,
                                'is_display': is_display,
                                'pos': s2.pos
                            }
                            self.env.cr.execute(sql_query, params)

    def apply_(self):
        current = self[0]
        cr_ids = []
        if current.project_id:
            if not current.line_ids1:
                raise UserError(_("Action impossible!'\nAucune Ligne à Créer!"))
            for s2 in current.line_ids1:
                if current.exist is True:
                    found = self.env['project.task.work'].search([('project_id', '=', current.project_id.id),
                                                                  ('zone', '=', ord(s2.zone)),
                                                                  ('secteur', '=', ord(s2.secteur))])

               # TODO check functionality

                seq = s2.sequence + 1
                kk = self.env['project.task.work'].search([('project_id', '=', current.project_id.id),
                                                           ('sequence', '=', seq)])
                res_user = self.env['res.users'].browse(self.env.user.id)
                while kk:
                    seq = seq + 1
                    kk = self.env['project.task.work'].search([('project_id', '=', current.project_id.id),
                                                               ('sequence', '=', seq)])
            for jj in current.line_ids:
                for hh in range(ord(jj.secteur.upper()), ord(jj.secteur_to.upper()) + 1):
                    pr = self.env['project.project'].create({
                        'date': fields.date.today(),
                        'resp_id': current.project_id.resp_id.id or False,
                        'fees_id': current.project_id.fees_id.id or False,
                        'bord': current.project_id.bord,
                        'npc': current.project_id.npc + ' - Zone ' + jj.zone.upper() + ' Secteur ' + chr(hh).upper(),
                        'date_start': current.project_id.date_start,
                        'date_end': current.project_id.date_end,
                        'state_id': current.project_id.state_id.id,
                        'city': current.project_id.city,
                        'ftp': current.project_id.ftp,
                        'priority': current.project_id.priority,
                        'ref': current.project_id.ref,
                        'km': current.project_id.km,
                        'partner_id': current.partner_id.id,
                        'country_id': current.project_id.country_id.id,
                        'type3': current.project_id.type3.id,
                        'zone': jj.zone.upper(),
                        'secteur': chr(hh).upper(),
                        'parent_id1': current.project_id.id,
                        'state': 'open'
                    })
                    cr_ids.append(pr.id)
                    for s2 in current.line_ids1:
                        if s2.task_id.kit_id and s2.zone == pr.zone and s2.secteur == pr.secteur:
                            query = """
                                INSERT INTO project_task_work (
                                    step_id, kit_id, task_id, categ_id, product_id, name, uom_id, date_start, date_end,
                                    poteau_i, poteau_t, color, hours, total_t, project_id, gest_id, uom_id_r,
                                    etape, state, zone, secteur, sequence, active, w_id, display, zo, sect,
                                    gest_id3, current_gest, current_sup, partner_id, work_orig, pr_project_id, pos
                                )
                                VALUES (
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                                )
                            """
                            values = (
                                s2.step_id.id, s2.task_id.kit_id.id, s2.task_id.id, s2.categ_id.id, s2.product_id.id,
                                s2.name.replace("'", "''"), s2.uom_id.id, s2.date_start, s2.date_end,
                                s2.poteau_i, s2.poteau_t, int(s2.color), s2.hours, s2.total_t, pr.id,
                                s2.gest_id.id or None, s2.uom_id.id, s2.etape, 'draft',
                                ord(s2.zone), ord(s2.secteur), seq, True, current.id, s2.is_display,
                                'Zone ' + s2.zone, 'Secteur ' + s2.secteur,
                                s2.task_id.coordin_id.id or None, s2.task_id.coordin_id.id or None,
                                s2.gest_id.id or None, s2.project_id.partner_id.id or None, s2.id or None,
                                current.project_id.id, s2.pos
                            )
                            self.env.cr.execute(query, values)

            del_ids = self.env['project.task'].search([('project_id', 'in', cr_ids)]).ids
            for tt in del_ids:
                self.env['project.task'].browse(tt).unlink()

            self.env['project.project'].browse(current.project_id.id).write({'is_parent': True})

            if len(current.work_ids) > 0:
                for s3 in current.work_ids:
                    if current.type == '1':
                        s3.write({'active': False, 'w_id': current.id})
                    else:
                        if current.choix == '2':
                            s3.write({'active': False, 'w_id': current.id})
                        else:
                            s3.write({'w_id': current.id})

            else:
                v = []
                res_cpt = []
                for tt in current.task_ids.ids:
                    this_p = self.env['project.task'].browse(tt)
                    if this_p.kit_id:
                        v.append(this_p.kit_id.id)

                if len(v) > 0:
                    ll1 = self.env['project.task.work'].search([
                        ('project_id', '=', current.project_id.id),
                        ('state', 'in', ('draft', 'affect')),
                        ('kit_id', 'in', v),
                        ('active', '=', True),
                        ('is_copy', '=', False),
                    ])

                    res_cpt = ll1.ids

                    for kk in res_cpt:
                        if current.type == '1':
                            self.env['project.task.work'].browse(kk).write({'active': False, 'w_id': current.id})
                        else:
                            if current.choix == '2':
                                self.env['project.task.work'].browse(kk).write({'active': False, 'w_id': current.id})
                            else:
                                self.env['project.task.work'].browse(kk).write({'w_id': current.id})

            self.write({'state': 'open'})
            return {
                'name': 'Taches générées avec Succès',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sh.message.wizard',
                'target': 'new',
            }

    def cancel_(self):
        current = self
        found = self.env['project.task.work'].search([('w_id', '=', current.id), ('employee_id', '!=', False)])
        if found:
            for work in found:
                raise UserError(
                    _("Attention!\nAn assignment is made with this configuration: Project %s, Zone: %s, Secteur: %s, Intervenant: %s") % (
                        current.project_id.npc, work.zone, work.secteur, work.employee_id.name))
        sub_ids = self.env['project.task.work'].search([('w_id', '=', current.id)]).ids
        for tt in sub_ids:
            self.env['project.task.work'].browse(tt).unlink()
        for tt in current.project_id.child_ids.ids:
            self.env['project.project'].browse(tt).unlink()

        del_ids = self.env['project.task.work'].search([('w_id', '=', current.id), ('active', '=', False)]).ids
        for tt in del_ids:
            self.env['project.task.work'].browse(tt).write({'w_id': False, 'active': True})

        current.state = 'draft'

        self.env['project.project'].browse(current.project_id.id).write({'is_parent': False})

        return {
            'name': _('Annulation faite avec Succès'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'view_id': False,
            'target': 'new',
        }

    name = fields.Char()
    disponible = fields.Boolean(compute='_compute_disponible', string='Disponible')
    date_from = fields.Date(string='Wizard')
    date_to = fields.Date(string='Wizard')
    exist = fields.Boolean(string='Ids', default=True)
    year_no = fields.Char(string='Priority', default=lambda self: str(time.strftime('%Y')))
    is_kit = fields.Boolean(string="Email")
    zone = fields.Integer(string='Zone')
    secteur = fields.Integer(string='Secteur')

    project_id = fields.Many2one('project.project', string='Wizard')
    partner_id = fields.Many2one('res.partner', string='wizard')
    task_id = fields.Many2one('project.task', string='Wizard')
    work_id = fields.Many2one('project.task.work', string='Wizard')
    product_id = fields.Many2one('product.product', string='Wizard')
    task_ids = fields.Many2many('project.task', string='Tasks')
    work_ids = fields.Many2many('project.task.work', string='Tasks')
    user_id = fields.Many2one('res.users', string='Assigned to')
    dst_task_id = fields.Many2one('project.task', string='Destination Task')
    dst_project = fields.Many2one('project.project', string='Project')
    line_ids = fields.One2many('base.task.merge.line', 'wizard_id', string='Role Lines', copy=True)
    line_ids1 = fields.One2many('base.group.merge.line2', 'wiz_id', string='Role Lines', copy=True)
    line_ids2 = fields.One2many('task_line.show.line2', 'wizard_id', string='Role Lines', copy=True)

    choix = fields.Selection([
        ('1', 'Garder Les Taches Sources Actives'),
        ('2', 'Archiver les Taches Sources')

    ],

        string='Priority', select=True)

    type = fields.Selection([
        ('1', 'Nouvelle Subdivision'),
        ('2', 'Modification Subdivision Existante')
    ], string='Type', select=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('open', 'Validé')
    ], string='Priority', default='draft', select=True)

    week_no = fields.Selection([
        ('00', '00'),
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
        ('24', '24'),
        ('25', '25'),
        ('26', '26'),
        ('27', '27'),
        ('28', '28'),
        ('29', '29'),
        ('30', '30'),
        ('31', '31'),
        ('32', '32'),
        ('33', '33'),
        ('34', '34'),
        ('35', '35'),
        ('36', '36'),
        ('37', '37'),
        ('38', '38'),
        ('39', '39'),
        ('40', '40'),
        ('41', '41'),
        ('42', '42'),
        ('43', '43'),
        ('44', '44'),
        ('45', '45'),
        ('46', '46'),
        ('47', '47'),
        ('48', '48'),
        ('49', '49'),
        ('50', '50'),
        ('51', '51'),
        ('52', '52')
    ], string='Priority', select=True, default=lambda self: str(time.strftime('%W')))

    keep = fields.Selection([
        ('active', 'Actives'),
        ('inactive', 'Archivées'),
        ('both', 'Actives et Archivées')
    ], string='Keep', default='active')

    @api.model
    def default_get(self, fields_list):
        res = super(EbMergeTasks, self).default_get(fields_list)
        if 'active_model' in self.env.context:
            all_task_ids = self.env.context.get('task_ids')
            task_divide_ids = []
            for task_id in all_task_ids:
                task = self.env['project.task'].browse(task_id)
                if task.step_id.is_divide:
                    task_divide_ids.append(task_id)
            res.update({'type': '1', 'task_ids': task_divide_ids,
                        'project_id': self.env.context.get('project_id'),
                        'partner_id': self.env.context.get('partner_id')})
        return res

    def button_divide(self):
        self.show_results()
        self.apply_()

    # Cette méthode utilise le décorateur @api.depends pour indiquer que le calcul du champ disponible doit dépendre de la valeur du champ project_id.user_id
        # Lorsque cette méthode est exécutée, elle itère sur chaque enregistrement (book) pour effectuer les opérations suivantes :
        # vérifie si l'ID de l'utilisateur associé au champ 'user_id' de l'enregistrement 'book.project_id' est égal à l'ID de l'utilisateur actuellement connecté (self.env.user.id).
        # Si les deux ID correspondent, cela signifie que l'utilisateur actuel est associé au projet correspondant à 'book.project_id'. Dans ce cas, le champ 'disponible' de 'book' est défini sur 'True'.
        # Si les deux ID ne correspondent pas, cela signifie que l'utilisateur actuel n'est pas associé au projet correspondant à 'book.project_id'. Dans ce cas, le champ 'disponible' de book est défini sur 'False'

    @api.depends('project_id.user_id')
    def _compute_disponible(self):
        for book in self:
            if book.project_id.user_id.id == self.env.user.id:
                book.disponible = True
            else:
                book.disponible = False

    def _compute_default_flow(self):
        result = {}
        for rec in self:
            work_ids = self.env['base.flow.merge.line'].search_count([('work_id', '=', rec.id)])
            if work_ids:
                result[rec.id] = 1
            else:
                result[rec.id] = 0

        return result

    def action_merge(self):
        names = []

        if self.dst_task_id:
            names.append(self.dst_task_id.name)
        else:
            raise UserError(_('You must select a Destination Task'))

        desc = []

        desc.append(self.dst_task_id.description)
        for record in self.task_ids:
            if record.id != self.dst_task_id.id:
                names.append(record.name)
                desc.append(record.description)

        for message in self.task_ids:
            for msg_id in message.message_ids:
                msg_id.res_id = self.dst_task_id.id

        plan_hours = self.dst_task_id.planned_hours
        for hour in self.task_ids:
            for time in hour.timesheet_ids:
                plan_hours += time.planned_hours

        self.dst_task_id.planned_hours = plan_hours

        transformed_names = ', '.join(names)
        self.dst_task_id.name = transformed_names

        transformed_desc = ', '.join(desc)
        self.dst_task_id.description = transformed_desc

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        for task in self.task_ids:
            task.message_post(
                body=f"This task has been merged into: {base_url}/web#id={self.dst_task_id.id}&model=project.task")

        self.task_ids.active = False
        self.dst_task_id.active = True

        if self.user_id:
            self.dst_task_id.user_id = self.user_id
        elif self.dst_task_id.user_id:
            self.dst_task_id.user_id = self.dst_task_id.user_id
        else:
            raise UserError(
                _('There is no user assigned to the merged task, and the destination task does not have an assigned user!'))

        return True

    @api.onchange('year_no', 'week_no')
    def onchange_week_(self):

        # The result variable is no longer used since the method directly assigns values to the fields.
        if self.year_no and self.week_no:  # The method now uses the self parameter to access the field values.
            d = date(self.year_no, 1, 1)
            # The date object is created using date(self.year_no, 1, 1) instead of date(int(year_no), 1, 1).
            if d.weekday() <= 3:
                d = d - timedelta(d.weekday())
                # The timedelta class is imported separately with from datetime import timedelta.
            else:
                d = d + timedelta(7 - d.weekday())
            dlt = timedelta(days=(int(self.week_no) - 1) * 7)

            self.date_from = d + dlt
            self.date_to = d + dlt + timedelta(days=6)

    @api.onchange('project_id')
    def onchange_project_id(self):

        if self.project_id:
            self.task_ids = False
            self.work_ids = False

        return {'value': {}}

    @api.onchange('exist')
    def onchange_exist(self):
        if not self.exist:
            raise UserError(
                _("Attention!\nSi vous décocher cette option, le système ne vérifiera pas l'existence du Project-Zone-Secteur!"))

    @api.onchange('project_id', 'task_ids')
    def onchange_project_id(self):

        ltask1 = []
        ltask2 = []
        zz = []

        if self.project_id:
            tt = self.env['project.task'].search([('project_id', '=', self.project_id.id)], order='sequence asc')

            for task in tt:
                if self.project_id.is_kit and task.kit_id.id not in ltask1:
                    ltask1.append(task.kit_id.id)
                    ltask2.append(task.id)
                elif 'Etape' in task.product_id.name and task.product_id.name not in ltask1:
                    ltask1.append(task.product_id.name)
                    ltask2.append(task.id)

            zz = self.env['project.task'].search([('id', 'in', ltask2)], order='sequence asc').ids

        return {'domain': {'task_ids': [('id', 'in', zz)]}}

    @api.onchange('project_id', 'task_ids', 'zone', 'secteur', 'keep', 'type')
    def onchange_categ_id(self):

        list_ = []
        list1 = []
        list2 = []
        tt = []

        task_work = self.env['project.task.work']

        if self.type == '1':
            is_kit = False

            if self.task_ids:
                for kk in self.task_ids.ids:
                    task = self.env['project.task'].browse(kk)

                    if task.kit_id:
                        is_kit = True
                        for jj in task.work_ids.ids:
                            work = task_work.browse(jj)

                            if work.kit_id.id not in list1:
                                list1.append(work.kit_id.id)
                                list2.append(work.id)
                    else:
                        list_.append(task.product_id.name)

                if is_kit:
                    tt = self.env['project.task.work'].search([('id', 'in', list2)], order='sequence asc').ids
                else:
                    tt = self.env['project.task.work'].search([
                        ('project_id', '=', self.project_id.id),
                        ('etape', 'in', list_),
                        ('is_copy', '=', False),
                        ('zone', '=', 0),
                        ('secteur', '=', 0),
                        '|', ('active', '=', True), ('active', '=', False)
                    ], order='sequence asc').ids
            else:
                if self.project_id:
                    tt = self.env['project.task.work'].search([
                        ('project_id', '=', self.project_id.id),
                        ('is_copy', '=', False),
                        ('kit_id', '=', False),
                        ('zone', '=', 0),
                        ('secteur', '=', 0),
                        '|', ('active', '=', True), ('active', '=', False)
                    ], order='sequence asc').ids

                    if not tt:
                        for task in tt:
                            work = task_work.browse(task.id)

                            if work.kit_id:
                                if work.kit_id.id not in list1:
                                    list1.append(work.id)

                        tt = self.env['project.task.work'].search([('id', 'in', list1)], order='sequence asc').ids

        else:
            if self.keep == 'active':
                if self.task_ids:
                    for kk in self.task_ids.ids:
                        task = self.env['project.task'].browse(kk)
                        list_.append(task.product_id.name)

                    tt = self.env['project.task.work'].search([
                        ('project_id', '=', self.project_id.id),
                        ('etape', 'in', list_),
                        ('is_copy', '=', False),
                        ('active', '=', True),
                        ('secteur', '=', self.secteur)
                    ], order='sequence asc').ids
                else:
                    if self.project_id:
                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('is_copy', '=', False),
                            ('active', '=', True),
                            ('secteur', '=', self.secteur)
                        ], order='sequence asc').ids

            elif self.keep == 'inactive':
                if self.task_ids:
                    for kk in self.task_ids.ids:
                        task = self.env['project.task'].browse(kk)
                        list_.append(task.product_id.name)

                    tt = self.env['project.task.work'].search([
                        ('project_id', '=', self.project_id.id),
                        ('etape', 'in', list_),
                        ('is_copy', '=', False),
                        ('active', '=', False),
                        ('secteur', '=', self.secteur)
                    ], order='sequence asc').ids
                else:
                    if self.project_id:
                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('is_copy', '=', False),
                            ('active', '=', False),
                            ('secteur', '=', self.secteur)
                        ], order='sequence asc').ids

            elif self.keep == 'both':
                if self.task_ids:
                    for kk in self.task_ids.ids:
                        task = self.env['project.task'].browse(kk)
                        list_.append(task.product_id.name)

                    tt = self.env['project.task.work'].search([
                        ('project_id', '=', self.project_id.id),
                        ('etape', 'in', list_),
                        ('is_copy', '=', False),
                        ('secteur', '=', self.secteur),
                        '|', ('active', '=', True), ('active', '=', False)
                    ], order='sequence asc').ids
                else:
                    if self.project_id:
                        tt = self.env['project.task.work'].search([
                            ('project_id', '=', self.project_id.id),
                            ('is_copy', '=', False),
                            ('secteur', '=', self.secteur),
                            '|', ('active', '=', True), ('active', '=', False)
                        ], order='sequence asc').ids

        return {'domain': {'work_ids': [('id', 'in', tt)]}}

    def action_copy1(self):
        return super().copy()

    def action_copy(self, default=None):
        if default is None:
            default = {}

        for current in self:
            for tt in current.task_ids:
                packaging_obj = self.env['project.task']

                if current.zone == 0 and current.secteur == 0:
                    vals = {
                        'task_id': tt.id,
                        'product_id': tt.product_id.id,
                        'name': tt.name,
                        'date_start': tt.date_start,
                        'date_end': tt.date_end,
                        'poteau_t': tt.qte,
                        'color': tt.color,
                        'total_t': tt.color * 7,
                        'project_id': tt.project_id.id,
                        'gest_id': tt.reviewer_id.id or False,
                        'uom_id': tt.uom_id.id,
                        'uom_id_r': tt.uom_id.id,
                        'ftp': tt.ftp,
                        'zone': tt.zone,
                        'secteur': tt.secteur,
                        'state': 'draft',
                        'priority': tt.priority,
                    }
                    cte = packaging_obj.create(vals)

                elif current.zone > 0 and current.secteur == 0:
                    for cc in range(1, current.zone + 1):
                        vals = {
                            'task_id': tt.id,
                            'product_id': tt.product_id.id,
                            'name': tt.name + ' Zone ' + str(cc),
                            'date_start': tt.date_start,
                            'date_end': tt.date_end,
                            'poteau_t': tt.qte,
                            'color': tt.color,
                            'total_t': tt.color * 7,
                            'project_id': tt.project_id.id,
                            'gest_id': tt.reviewer_id.id or False,
                            'uom_id': tt.uom_id.id,
                            'uom_id_r': tt.uom_id.id,
                            'ftp': tt.ftp,
                            'zone': cc,
                            'secteur': 0,
                            'state': 'draft',
                            'priority': tt.priority,
                        }
                        cte = packaging_obj.create(vals)

                elif current.zone > 0 and current.secteur > 0:
                    for cc in range(1, current.zone + 1):
                        for cc1 in range(1, current.secteur + 1):
                            vals = {
                                'task_id': tt.id,
                                'product_id': tt.product_id.id,
                                'name': tt.name + ' Zone ' + str(cc) + ' Secteur ' + str(cc1),
                                'date_start': tt.date_start,
                                'date_end': tt.date_end,
                                'poteau_t': tt.qte,
                                'color': tt.color,
                                'total_t': tt.color * 7,
                                'project_id': tt.project_id.id,
                                'gest_id': tt.reviewer_id.id or False,
                                'uom_id': tt.uom_id.id,
                                'uom_id_r': tt.uom_id.id,
                                'ftp': tt.ftp,
                                'zone': cc,
                                'secteur': cc1,
                                'priority': tt.priority,
                                'state': 'draft',
                            }
                            cte = packaging_obj.create(vals)

                            return cte

    def action_copy3(self):
        packaging_obj = self.env['project.task']
        packaging_copy = packaging_obj.copy(self.dst_task_id.id)
        packaging_copy.write({'name': 'dfsdf'})
        return True


class ProjectTaskWork(models.Model):
    _inherit = 'project.task.work'

    w_id = fields.Many2one('base.task.merge.automatic.wizard', string='Company', readonly=True,
                           states={'draft': [('readonly', False)]}, )
