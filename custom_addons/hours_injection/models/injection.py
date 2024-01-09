# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HoursInjection(models.Model):
    _name = 'hours.injection'
    _order = 'date desc'

    @api.model
    def default_get(self, fields_list):

        res = super(HoursInjection, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        ft = self.env['bon.show'].browse(active_id)
        emp = self.env['hr.employee'].browse(ft.employee_id.id)
        total = 0.0
        for b_id in ft.line_ids2.ids:
            x = self.env['bon.show.line2'].browse(b_id).hours_r
            total += x

        empl_ho = self.env['hr.employee.holiday'].search(
            [('employee_id', '=', ft.employee_id.id), ('name', 'ilike', 'ordinaire')])
        if not empl_ho:
            raise UserError(_("Le type 'Congé Ordinaire' n'existe pas"))
        else:
            sol_ord = empl_ho.remaining_leave

        res.update({'bon_id': active_id,
                    'employee_id': ft.employee_id.id,
                    'sum': total,
                    'sol_bank': emp.bank_hours,
                    'sol_cong': sol_ord})

        return res

    def get_bank(self):
        empl = self.env['hr.employee'].browse(self.employee_id.id)
        self.sol_bank = empl.bank_hours
        empl_ho = self.env['hr.employee.holiday'].search([('employee_id', '=', self.employee_id.id), ('name', 'ilike', 'ordinaire')])
        if not empl_ho:
            raise UserError(_("Le type 'Congé Ordinaire' n'existe pas"))
        else:
            self.sol_cong = empl_ho.remaining_leave

    def _get_user(self):

        employee_id = self.env['res.users'].browse(self.env.uid).employee_id
        if employee_id:
            return employee_id.id
        else:
            return False

    date = fields.Date(string='Date', default=fields.Date.today)
    gest_id = fields.Many2one('hr.employee', string="Gestionnaire", default=lambda self: self._get_user())
    employee_id = fields.Many2one('hr.employee', string='Bénéficiaire')
    bon_id = fields.Many2one('bon.show', string='Réf F.T')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('valid', 'Validé'), ],
        string='Status', copy=False, default='draft')
    sum = fields.Float(string='Total Heures')
    hr_total = fields.Float(string='Total Heures à Injecter', readonly=True, states={'draft': [('readonly', False)]})
    hr_bank = fields.Float(string="Vers Banque d'heures", readonly=True, states={'draft': [('readonly', False)]})
    hr_cong = fields.Selection([
        ('3.5', '03:30'),
        ('7', '07:00'),
        ('10.5', '10:30'),
        ('14', '14:00'),
        ('17.5', '17:30'),
        ('21', '21:00'), ],
        string='Vers Solde de Congés', readonly=True, states={'draft': [('readonly', False)]},)
    sol_bank = fields.Float(compute='get_bank', string="Solde Banque d'heures")
    sol_cong = fields.Float(compute='get_bank', string="Solde Congés")
    choice = fields.Selection([
        ('cong', 'Solde de Congés'),
        ('bank', "Banque d'heures"),
        ('both', 'Les deux'), ],
        string="Voie d'injection", required=True, default='cong',
        readonly=True, states={'draft': [('readonly', False)]})

    _sql_constraints = [
        ('total_inject', 'CHECK (hr_total<=sum)', "Nombre d'heures à injecter ne doit pas dépasser le total "
                                                  "d'heures dans la Feuille du temps."),
        ('bank_inject', 'CHECK (hr_bank<=sum)', "Nombre d'heures à injecter ne doit pas dépasser le total "
                                                "d'heures dans la Feuille du temps."),
        ('cong_inject', 'CHECK (hr_cong<=sum)', "Nombre d'heures à injecter ne doit pas dépasser le total "
                                                "d'heures dans la Feuille du temps."),
        ('nb_hr_bank_positive', 'CHECK (hr_bank>=0)', "Nombre d'heures à injecter dans la banque d'heures ne doit pas "
                                                      "être null"),
        ('nb_hr_total_positive', 'CHECK (hr_total>=0)', "Total d'heures à injecter doit être positif"),
    ]

    @api.onchange('hr_cong')
    def _onchange_rest_bank(self):
        if self.choice == 'both':
            self.hr_bank = self.hr_total - float(self.hr_cong)
        if self.choice == 'cong':
            if float(self.hr_cong) > self.sum:
                raise UserError(
                    _("Nombre d'heures à injecter ne doit pas dépasser le total d'heures dans la Feuille du temps."))

    def send(self):

        ord_id = self.env['hr.holidays.type'].search([('name', 'ilike', 'ordinaire')]).id
        employee = self.env['hr.employee'].browse(self.employee_id.id)

        if self.choice == 'bank':
            bank = employee.bank_hours + self.hr_bank
            employee.write({'bank_hours': bank})

        elif self.choice == 'cong':
            self.env['hr.holidays.histo'].create({
                'employee_id': self.employee_id.id,
                'date': self.date,
                'diff': - float(self.hr_cong)/7,
                'year': self.date.year,
                'motif': "Traitement d'heures",
                'type': ord_id,
            })

        else:
            if (float(self.hr_cong) + self.hr_bank) != self.hr_total:
                raise UserError(_('Somme Saisie invalide'))
            else:
                bank = employee.bank_hours + self.hr_bank
                employee.write({'bank_hours': bank})
                self.env['hr.holidays.histo'].create({
                    'employee_id': self.employee_id.id,
                    'date': self.date,
                    'diff': - float(self.hr_cong) / 7,
                    'year': self.date.year,
                    'motif': "Traitement d'heures",
                    'type': ord_id,
                })

        self.write({'state': 'valid'})

        view = self.env['sh.message.wizard']

        view_id = view and view.id or False
        return {
            'name': 'Traitement effectué avec Succès',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }

    def cancel(self):

        ord_id = self.env['hr.holidays.type'].search([('name', 'ilike', 'ordinaire')]).id
        employee = self.env['hr.employee'].browse(self.employee_id.id)
        if self.choice == 'bank':
            if (self.sol_bank - self.hr_bank) < 0:
                raise UserError("Annulation Impossible!\nSolde d'heures sera négatif.")
            else:
                bank = employee.bank_hours - self.hr_bank
                employee.write({'bank_hours': bank})

        elif self.choice == 'cong':
            if (self.sol_cong*7 - float(self.hr_cong)) < 0:
                raise UserError("Annulation Impossible!\nSolde de Congés sera négatif.")
            else:
                self.env['hr.holidays.histo'].create({
                    'employee_id': self.employee_id.id,
                    'date': self.date,
                    'diff': float(self.hr_cong) / 7,
                    'year': self.date.year,
                    'motif': "Annulation Traitement d'heures",
                    'type': ord_id,
                })

        else:
            if (self.sol_bank - self.hr_bank) < 0:
                raise UserError("Annulation Impossible!\nSolde d'heures sera négatif.")
            elif (self.sol_cong*7 - float(self.hr_cong)) < 0:
                raise UserError("Annulation Impossible!\nSolde de Congés sera négatif.")
            else:
                bank = employee.bank_hours - self.hr_bank
                employee.write({'bank_hours': bank})
                self.env['hr.holidays.histo'].create({
                    'employee_id': self.employee_id.id,
                    'date': self.date,
                    'diff': float(self.hr_cong) / 7,
                    'year': self.date.year,
                    'motif': "Annulation Traitement d'heures",
                    'type': ord_id,
                })

        self.write({'state': 'draft'})
        return True

    def name_get(self):
        res = []
        emp = self.env['hr.employee']
        for rec in self:
            name = emp.browse(rec.employee_id.id).name + '/' + str(rec.date)
            res.append((rec.id, name))
        return res
