# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math
import datetime as dt


class HrPublicHolidays(models.Model):
    _name = 'hr.public.holiday'

    name = fields.Char(string='Description', size=64)
    state = fields.Selection(
        [('draft', 'Brouillon'),
         ('validate', 'Valide')],
        string='Status', readonly=True,
        track_visibility='onchange', copy=False,
        help='The status is set to \'To Submit\', \
                  when a holiday request is created.\
                  \nThe status is \'Approved\', when holiday request\
                  is approved by manager.',
        default='draft')
    date_from = fields.Date(string='Start Date', readonly=True,
                            states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, select=True,
                            copy=False)
    date_to = fields.Date(string='End Date', readonly=True,
                          states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, copy=False)
    company_id = fields.Many2one('res.company', string='Company')
    fiscal_id = fields.Many2one('account.fiscalyear', string='Company')
    nbr = fields.Float(string='Description')

    # @api.model
    # def _employees_for_public_holiday(self, company):
    #     company_id = company and company.id or None
    #     employees = self.env['hr.employee'].search(
    #         ['|',
    #          ('company_id', '=', company_id),
    #          ('company_id', '=', False)])
    #     return employees
    #
    # @api.multi
    # def reinit(self):
    #     ##        try:
    #     ##            res_id = self.env['ir.model.data'].get_object(
    #     ##                'hr_public_holidays', 'hr_public_holiday').id
    #     ##        except ValueError:
    #     ##            raise Warning(
    #     ##                _("Leave Type for Public Holiday not found!"))
    #     for holiday in self:
    #         _logger.debug("hr_public_holiday reinit: %s" % (self.name,))
    #
    #         existing = self.env['hr.holidays'].search(
    #             [('public_holiday_id', '=', holiday.id)])
    #         new = []
    #         company = holiday.company_id
    #         for emp in holiday._employees_for_public_holiday(company):
    #             matches = [h for h in existing
    #                        if h.employee_id.id == emp.id and
    #                        h.public_holiday_id.id == holiday.id]
    #             if matches:
    #                 existing = [h for h in existing if h not in matches]
    #             else:
    #                 _logger.info(
    #                     "hr_public_holiday reinit: "
    #                     "created holiday %s for %s" % (
    #                         self.name, emp.name))
    #                 vals = {
    #                     'name': holiday.name,
    #                     'type': 'remove',
    #                     'holiday_type': 'employee',
    #                     ##?                        'holiday_status_id': res_id,
    #                     'date_from': holiday.date_from,
    #                     'date_to': holiday.date_to,
    #                     'employee_id': emp.id,
    #                     'public_holiday_id': holiday.id
    #                 }
    #                 new.append(self.env['hr.holidays'].create(vals))
    #
    #         for leave in existing:
    #             _logger.info(
    #                 "hr_public_holiday reinit: "
    #                 "removed holiday %s for %s" % (
    #                     self.name, leave.employee_id.name))
    #             for sig in ('refuse', 'reset'):
    #                 leave.signal_workflow(sig)
    #             leave.unlink()
    #
    #         for leave_id in new:
    #             for sig in ('confirm', 'validate', 'second_validate'):
    #                 leave_id.signal_workflow(sig)
    #

    @api.onchange('date_to', 'date_from')
    def onchange_date_from(self):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        date_to = self.date_to
        date_from = self.date_from

        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise UserError(_('Warning!\nThe start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = (date_to-date_from).days

            result['value']['nbr'] = round(math.floor(diff_day)) + 1
        else:

            result['value']['nbr'] = 0

        return result

    def validate(self):
        self.state = 'validate'

    def reset(self):
        self.state = 'draft'


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    public_holiday_id = fields.Many2one(
        'hr.public.holiday', string="Public Holiday")

    @api.model
    def get_employee_calendar(self, employee):
        calendar = None
        if employee.resource_id.calendar_id:
            calendar = employee.resource_id.calendar_id.id
        return calendar
