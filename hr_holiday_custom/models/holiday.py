# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta
import math


class HrHolidaysStatus(models.Model):
    _name = "hr.holidays.type"
    _description = "Leave Type"
    _rec_name = "name"

    name = fields.Char(string='Type de Congé', size=64, required=True, translate=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    categ_id = fields.Many2one('calendar.event.type', string='Type de Réunion',
                               readonly=True, states={'draft': [('readonly', False)]})
    color_name = fields.Selection([('red', 'Red'),
                                   ('blue', 'Blue'),
                                   ('lightgreen', 'Light Green'),
                                   ('lightblue', 'Light Blue'),
                                   ('lightyellow', 'Light Yellow'),
                                   ('magenta', 'Magenta'),
                                   ('lightcyan', 'Light Cyan'),
                                   ('black', 'Black'),
                                   ('lightpink', 'Light Pink'),
                                   ('brown', 'Brown'),
                                   ('violet', 'Violet'),
                                   ('lightcoral', 'Light Coral'),
                                   ('lightsalmon', 'Light Salmon'),
                                   ('lavender', 'Lavender'),
                                   ('wheat', 'Wheat'),
                                   ('ivory', 'Ivory')], default='red', required=True,
                                  string='Couleur Affichée dans le Rapport',
                                  readonly=True, states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=True)
    max_leave = fields.Integer(string='Nombre de Jours Maximal', required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    employee_ids = fields.Many2many('hr.employee', string='Employés Concernés',
                                    readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [('draft', 'Brouillon'), ('valid', 'Validé')],
        string='Status', readonly=True, copy=False, default='draft')

    _sql_constraints = [
        ('uniq_name', 'unique(name)', 'Le Type de Congé doit être unique !'),
    ]

    def unlink(self):
        for rec in self:
            if rec.state == 'valid':
                raise UserError(
                    _('Action Impossible !\nImpossible de supprimer un type de Congé validé !'))

        return super(HrHolidaysStatus, self).unlink()

    def inject(self):

        if self.employee_ids:
            emp_ids = self.employee_ids.ids
        else:
            emp_ids = self.env['hr.employee'].search([]).ids

        emp_hol = self.env['hr.employee.holiday']
        for tt in emp_ids:
            emp_hol.create({
                'name': self.name,
                'employee_id': tt,
                'max_leave': self.max_leave,
            })

        self.state = 'valid'

        view = self.env['sh.message.wizard']
        view_id = view and view.id or False
        return {
            'name': 'Type ajouté avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    def cancel(self):
        self.state = 'draft'
        if self.employee_ids:
            emp_ids = self.employee_ids.ids
        else:
            emp_ids = self.env['hr.employee'].search([]).ids

        emp_hol = self.env['hr.employee.holiday']
        for tt in emp_ids:
            emp_hol.search([('employee_id', '=', tt), ('name', '=', self.name)]).unlink()
        view = self.env['sh.message.wizard']
        view_id = view and view.id or False
        return {
            'name': 'Type supprimé avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }


class HrHolidays(models.Model):
    _name = 'hr.holidays'
    _description = "Leave"
    _order = 'date desc'

    def name_get(self):
        res = []
        for rec in self:
            name = rec.employee_id.name + ' - ' + str(rec.date_from) + ' - ' + str(rec.holiday_type_id.name)
            res.append((rec.id, name))
        return res

    def _employee_get(self):
        emp_id = self._context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        emp_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]).ids
        if emp_ids:
            return emp_ids[0]
        return False

    name = fields.Char(string='Référence')
    state = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('pending', 'En cours de Traitement'),
            ('accept', 'Accepté'),
            ('refuse', 'Refusé'),
            ('modify', 'Modifié')],
        string='Status', readonly=True, copy=False, default='draft')
    date = fields.Date(string='Date de demande', default=fields.date.today())
    date_from = fields.Date(string='Date de Début', readonly=True, required=True,
                            states={'draft': [('readonly', False)]}, copy=False)
    date_to = fields.Date(string='Date de Fin', readonly=True, required=True,
                          states={'draft': [('readonly', False)]}, copy=False)
    date_from_r = fields.Date(string='Ancienne Date de Début', readonly=True,
                              states={'draft': [('readonly', False)]}, copy=False)
    date_to_r = fields.Date(string='Ancienne Date de Fin', readonly=True,
                            states={'draft': [('readonly', False)]}, copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employé', select=True, invisible=False,
                                  readonly=True, default=lambda self: self._employee_get(), )
    manager_id = fields.Many2one('hr.employee', 'Superviseur', invisible=False, readonly=True,
                                 states={'draft': [('readonly', False)]}, copy=False, required=True,
                                 help='This area is automatically filled by the user who validate the leave')
    notes = fields.Text(string='Reasons', readonly=True,
                        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    notes_r = fields.Text(string='Reasons', readonly=True,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    number_of_days = fields.Float(string='Nombre de Jours', copy=False)
    number_of_days_r = fields.Float(string='Ancien Nombre de Jours')
    meeting_id = fields.Many2one('calendar.event', string='Meeting')
    user_id = fields.Many2one('res.users', string='Utilisateur')
    holiday_line_ids = fields.One2many('hr.holidays.line', 'holiday_id')
    holiday_type_id = fields.Many2one('hr.holidays.type', string='Type de Congé', required=True,
                                      readonly=True, states={'draft': [('readonly', False)]})
    holiday_id = fields.Many2one('hr.holidays', string='Congé', readonly=True,
                                 states={'draft': [('readonly', False)]})
    type = fields.Selection([('take', 'Demande Congé'), ('modify', 'Modification Congé')],
                            string='Type Opération')

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or (holiday_type='category' AND category_id IS NOT NULL))",
         "The employee or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('date_check2', "CHECK ( (type='add') OR (date_from <= date_to))",
         "The start date must be anterior to the end date."),
        ('date_check', "CHECK ( number_of_days >= 0 )", "The number of days must be greater than 0."),
    ]

    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'pending'):
                raise UserError(
                    _('Action Impossible !\nImpossible de Supprimer une Demande Traitée !'))

        return super(HrHolidays, self).unlink()

        # TODO: can be improved using resource calendar method

    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        holiday_proxy = self.env['training.holiday.year']
        if not holiday_proxy.search([('year', '=', date.today().year)]):
            return False
        i = 0
        while date_from < date_to:
            dayoff = self.env['training.holiday.period'].search([('date_start', '<=', date_from),
                                                                 ('date_stop', '>=', date_from)])
            if dayoff:
                i += 1
            date_from = date_from + relativedelta(days=1)
        timedelta = date_to - date_from
        diff_day = timedelta.days
        diff_day -= i
        return i

    @api.onchange('date_to', 'date_from')
    def onchange_date_from(self):

        date_from = self.date_from
        date_to = self.date_to

        if (date_from and date_to) and (date_from > date_to):
            raise UserError(_('Attention!\nLa date de début doit être antérieur à la date de fin.'))

        if date_from and date_to:
            diff = (date_to - date_from).days + 1
            dayoff = self.env['training.holiday.period'].search([('date_start', '>=', date_from),
                                                                 ('date_stop', '<=', date_to)]).ids
            dayoff1 = self.env['training.holiday.period'].search([('date_stop', '=', date_from)]).ids
            dayoff2 = self.env['training.holiday.period'].search([('date_start', '=', date_to)]).ids
            diff -= 2 * len(dayoff) + len(dayoff1) + len(dayoff2)

            hol = self.env['hr.public.holiday'].search([('date_from', '>=', date_from),
                                                        ('date_to', '<=', date_to),
                                                        ('state', '=', 'validate')]).ids
            if hol:
                for tt in hol:
                    diff -= self.env['hr.public.holiday'].browse(tt).nbr
            hol1 = self.env['hr.public.holiday'].search([('date_to', '=', date_from)]).ids
            hol2 = self.env['hr.public.holiday'].search([('date_from', '=', date_to)]).ids
            diff -= len(hol1) + len(hol2)

            self.number_of_days = diff

    @api.onchange('employee_id')
    def onchange_employee(self):
        type_ids = []
        emp_hol_ids = self.env['hr.employee.holiday'].search([('employee_id', '=', self.employee_id.id)]).ids
        hol_line = self.env['hr.holidays.line']
        for tt in emp_hol_ids:
            emp_hol = self.env['hr.employee.holiday'].browse(tt)
            type_ids.append(emp_hol.name)
            hol_line.create({
                'holiday_id': self.id,
                'name': emp_hol.name,
                'max_leave': emp_hol.max_leave,
                'remaining_leave': emp_hol.remaining_leave,
            })
        return {'domain': {'holiday_type_id': [('name', 'in', type_ids)]}}

    @api.onchange('holiday_id')
    def onchange_holiday_id(self):
        hol = self.env['hr.holidays'].browse(self.holiday_id.id)
        self.manager_id = hol.manager_id
        self.holiday_type_id = hol.holiday_type_id
        self.date_from_r = hol.date_from
        self.date_to_r = hol.date_to
        self.number_of_days_r = hol.number_of_days

    def button_send(self):
        name = self.env['hr.holidays.type'].browse(self.holiday_type_id.id).name
        sol_id = self.env['hr.employee.holiday'].search(
            [('name', '=', name), ('employee_id', '=', self.employee_id.id)]).id
        sol = self.env['hr.employee.holiday'].browse(sol_id).remaining_leave
        nb_days = self.number_of_days
        if nb_days > sol:
            raise UserError('Solde Insuffisant')
        else:
            self.write({'state': 'pending'})

    def button_reopen(self):
        self.write({'state': 'draft'})

    def button_accept(self):

        self.env['hr.holidays.histo'].create({
            'holiday_id': self.id,
            'employee_id': self.employee_id.id,
            'date': self.date,
            'diff': self.number_of_days,
            'year': self.date.year,
            'motif': 'Congé attribué',
            'type': self.holiday_type_id.id,
        })

        self.write({'state': 'accept'})

    def button_refuse(self):
        self.write({'state': 'refuse'})

    def button_accept_r(self):
        name = self.env['hr.holidays.type'].browse(self.holiday_type_id.id).name
        sol_id = self.env['hr.employee.holiday'].search(
            [('name', '=', name), ('employee_id', '=', self.employee_id.id)]).id
        sol = self.env['hr.employee.holiday'].browse(sol_id).remaining_leave
        n_sol = sol + self.number_of_days_r
        nb_days = self.number_of_days
        if nb_days > n_sol:
            raise UserError('Solde Insuffisant')
        else:
            self.env['hr.holidays.histo'].create({
                'holiday_id': self.id,
                'employee_id': self.employee_id.id,
                'date': self.date,
                'diff': - self.number_of_days_r,
                'year': self.date.year,
                'motif': 'Congé annulé',
                'type': self.holiday_type_id.id,
            })

            self.env['hr.holidays.histo'].create({
                'holiday_id': self.id,
                'employee_id': self.employee_id.id,
                'date': self.date,
                'diff': self.number_of_days,
                'year': self.date.year,
                'motif': 'Congé attribué',
                'type': self.holiday_type_id.id,
            })

            self.env['hr.holidays'].browse(self.holiday_id.id).write({'state': 'modify'})
            self.write({'state': 'accept'})


class HrHolidayLine(models.Model):
    _name = 'hr.holidays.line'

    holiday_id = fields.Many2one('hr.holidays', string='Congé')
    name = fields.Char(string='Type de Congé', size=64, translate=True)
    max_leave = fields.Integer(string='Nombre de Jours Maximal')
    remaining_leave = fields.Integer(string='Nombre de Jours Restant')


class HrHolidayHisto(models.Model):
    _name = 'hr.holidays.histo'

    holiday_id = fields.Many2one('hr.holidays', string='Référence Congé')
    employee_id = fields.Many2one('hr.employee', string='Employé')
    type = fields.Many2one('hr.holidays.type', string='Type de Congé')
    date = fields.Date(string='Date Opération', default=fields.date.today())
    diff = fields.Float(string='Nombre de Jours')
    year = fields.Integer(string='Année fiscale', default=fields.date.today().year)
    motif = fields.Text(string='Libellé Opération')
    sol = fields.Float(string='Solde Actuel')

    _sql_constraints = [
        ('check_sol', 'check(sol >= diff)',
         'Action Impossible! Le solde doit rester positif .')
    ]

    @api.onchange('employee_id')
    def onchange_holiday_type(self):
        type_names = []
        type_ids = self.env['hr.employee.holiday'].search([('employee_id', '=', self.employee_id.id)]).ids
        for tt in type_ids:
            emp_hol = self.env['hr.employee.holiday'].browse(tt)
            type_names.append(emp_hol.name)
        return {'domain': {'type': [('name', 'in', type_names)]}}

    @api.onchange('employee_id', 'type')
    def onchange_sol(self):
        sol_id = self.env['hr.employee.holiday'].search(
            [('name', '=', self.type.name), ('employee_id', '=', self.employee_id.id)]).id
        self.sol = self.env['hr.employee.holiday'].browse(sol_id).remaining_leave


class HrHolidaysCloture(models.Model):
    _name = 'hr.holidays.cloture'

    type = fields.Selection([('year', 'Année'), ('employee', 'Employé(s)')],
                            string='Type de Clôture', required=True)
    state = fields.Selection([('draft', 'Brouillon'), ('valid', 'Validé')],
                             string='status', default='draft')
    date = fields.Date(string='Date de Clôture', readonly=True, default=fields.date.today())
    year_cl = fields.Integer(string='Année à Clôturer', default=fields.date.today().year)
    employee_ids = fields.Many2many('hr.employee', string='Employé(s)')
    line_ids = fields.One2many('hr.holidays.cloture.line', 'cloture_id')
    cn = fields.Integer(string='compteur')

    _sql_constraints = [
        ('uniq_year', 'unique(year_cl)', 'Année déjà clôturée !'),
    ]

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'year' and self.cn == 0:
            self.cn += 1
            type_ids = self.env['hr.holidays.type'].search([]).ids
            for tt in type_ids:
                hol = self.env['hr.holidays.type'].browse(tt)
                self.env['hr.holidays.cloture.line'].create({
                    'cloture_id': self.id,
                    'name': hol.name,
                    'max_leave': hol.max_leave,
                })

    def button_valid(self):
        if self.type == 'employee' and not self.employee_ids:
            raise UserError(_("Vous n'avez choisi aucun employé"))
        if self.type == 'year':
            for ll in self.line_ids:
                if (ll.avec_sol and ll.sans_sol) or (not ll.avec_sol and not ll.sans_sol):
                    raise UserError(_("Veuillez Choisir entre 'avec' ou 'sans' solde !"))
            for ll in self.line_ids:
                if ll.avec_sol:
                    type_id = self.env['hr.holidays.type'].search([('name', '=', ll.name)]).id
                    hr_ids = self.env['hr.employee.holiday'].search([('name', '=', ll.name)]).ids
                    for x in hr_ids:
                        line = self.env['hr.employee.holiday'].browse(x)
                        self.env['hr.holidays.histo'].create({
                            'employee_id': line.employee_id.id,
                            'date': fields.date.today(),
                            'diff': - line.remaining_leave,
                            'year': self.year_cl + 1,
                            'motif': 'Clôture Avec Solde',
                            'type': type_id,
                        })
            self.state = 'valid'


class HrHolidaysClotureLine(models.Model):
    _name = 'hr.holidays.cloture.line'

    cloture_id = fields.Many2one('hr.holidays.cloture')
    name = fields.Char(string='Type de Congé')
    max_leave = fields.Float(string='Nombre de Jours Maximal')
    avec_sol = fields.Boolean(string='Avec Solde Ouverture')
    sans_sol = fields.Boolean(string='Sans Solde Ouverture')
