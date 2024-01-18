# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
from dateutil import rrule
from dateutil.relativedelta import relativedelta


class HolidayYear(models.Model):
    _name = 'training.holiday.year'
    _rec_name = 'year'

    year = fields.Char(string='Year', size=64, select=1, required=True, default=lambda *a: datetime.today().year)
    hours = fields.Integer(string='Name', default=7)
    period_ids = fields.One2many('training.holiday.period', 'year_id', string='Holiday Periods')

    _sql_constraints = [
        ('uniq_year', 'unique(year)', 'The year must be unique !'),
    ]


class HolidayPeriodCategory(models.Model):
    _name = 'training.holidays.category'

    name = fields.Char(string='Name', size=128, required=True)


class HolidayPeriod(models.Model):
    _name = 'training.holiday.period'

    year_id = fields.Many2one('training.holiday.year', string='Year', required=True, ondelete='cascade')
    name = fields.Char(string='Name', size=64, required=True)
    date_start = fields.Date(string='Date Start', required=True, default=fields.Date.today)
    date_stop = fields.Date(string='Date Stop', required=True, default=fields.Date.today)
    active = fields.Boolean(string='Active', default=True)
    categ = fields.Many2one('training.holidays.category', string='Category')

    def _check_date_start_stop(self):
        if not self.ids:
            return False
        obj = self[0]
        return obj.date_start <= obj.date_stop

    # def is_in_period(self, cr, date):
    #     if not date:
    #         raise osv.except_osv(_('Error'),
    #                              _('No date specified for \'Is in period\' holiday period check'))
    #     cr.execute("SELECT count(id) "
    #                "FROM training_holiday_period "
    #                "WHERE %s BETWEEN date_start AND date_stop AND active='1'",
    #                (date,))
    #     return cr.fetchone()[0] > 0

    _constraints = [
        (_check_date_start_stop, "Please, check the start date !", ['date_start', 'date_stop']),
    ]


class HolidayYearWizard(models.Model):
    _name = 'training.holiday.year.wizard'

    year = fields.Integer(string='Year', required=True, default=lambda *a: datetime.today().year)

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}

    def action_apply(self):
        if not self.ids:
            return False
        holiday_year_obj = self.env['training.holiday.year']
        holiday_period_obj = self.env['training.holiday.period']
        categ = self.env['training.holidays.category'].search([('name', '=', 'Week-End')]).id
        if not categ:
            cat = self.env['training.holidays.category'].create({'name': 'Week-End'})
            categ = cat.id
        wizard = self[0]
        try:
            year_start = datetime.strptime('%04s-01-01' % (wizard.year,), '%Y-%m-%d')
            year_end = datetime.strptime('%04s-12-31' % (wizard.year,), '%Y-%m-%d')
        except:
            raise UserError(_('Error!\nPlease enter valid year'))

        year_id = holiday_year_obj.create({'year': wizard.year})

        # Generate holiday periods for each week-end of requested year
        # NOTE: we use ISO week number, but if the 1st saturday of the
        #       year is before the 1st thursday we force week-num to 0
        year_rule = rrule.rrule(rrule.DAILY, dtstart=year_start, until=year_end, byweekday=(rrule.SA))
        for saturday in year_rule:
            iso_year, iso_weeknum, iso_weekday = saturday.isocalendar()
            weeknum = iso_year == wizard.year and iso_weeknum or 0
            holiday_period_obj.create({
                'year_id': year_id.id,
                'date_start': saturday.strftime('%Y-%m-%d'),
                'date_stop': (saturday + relativedelta(days=1)).strftime('%Y-%m-%d'),
                'name': _('Week-End %02d') % (weeknum,),
                'categ': categ,
            }),

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'training.holiday.year',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': year_id.id,
        }

    # def action_apply_scheduler(self, cr, uid, context=None):
    #     holiday_year_obj = self.pool.get('training.holiday.year')
    #     holiday_period_obj = self.pool.get('training.holiday.period')
    #     categ = self.pool.get('training.holidays.category').search(cr, uid, [('name', '=', 'Week-End')])
    #     if not categ:
    #         cat = self.pool.get('training.holidays.category').create(cr, uid, {'name': 'Week-End'})
    #         categ = [cat]
    #     date = datetime.now()
    #     year = date.strftime("%Y")
    #     year = int(year)
    #     year += 1
    #     try:
    #         year_start = datetime.strptime('%04s-01-01' % (year,), DT_FORMAT)
    #         year_end = datetime.strptime('%04s-12-31' % (year,), DT_FORMAT)
    #     except:
    #         raise osv.except_osv(_('Error!'),
    #                              _('Please enter valid year'))
    #
    #     year_id = holiday_year_obj.create(cr, uid, {'year': year}, context=context)
    #
    #     # Generate holiday periods for each week-end of requested year
    #     # NOTE: we use ISO week number, but if the 1st saturday of the
    #     #       year is before the 1st thursday we force week-num to 0
    #     year_rule = rrule.rrule(rrule.DAILY, dtstart=year_start, until=year_end, byweekday=(rrule.SA))
    #     for saturday in year_rule:
    #         iso_year, iso_weeknum, iso_weekday = saturday.isocalendar()
    #         weeknum = iso_year == year and iso_weeknum or 0
    #         holiday_period_obj.create(cr, uid, {
    #             'year_id': year_id,
    #             'date_start': saturday.strftime(DT_FORMAT),
    #             'date_stop': (saturday + relativedelta(days=1)).strftime(DT_FORMAT),
    #             'name': _('Week-End %02d') % (weeknum,),
    #             'categ': categ[0],
    #         }, context=context),
    #
    #     return True
