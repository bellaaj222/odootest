from odoo import models, fields, _
from odoo.exceptions import UserError
from odoo.tools import safe_eval
from datetime import datetime
from pytz import timezone, utc
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from jinja2 import Template    # Ajout d'importations et d'un nouvel import from jinja2 import Template.


class SuperCalendarConfigurator(models.Model):
    _name = 'super.calendar.configurator'

    name = fields.Char(string='Name', required=True)
    line_ids = fields.One2many('super.calendar.configurator.line', 'configurator_id', string='Lines')

    def _clear_super_calendar_records(self):
        """
        Remove old super_calendar records
        """
        super_calendar_pool = self.env['super.calendar']
        super_calendar_list = super_calendar_pool.search([])
        super_calendar_list.unlink()

    def generate_calendar_records(self):
        """
        At every CRON execution, every 'super calendar' data is deleted and
        regenerated again.
        """

        # Remove old records
        self._clear_super_calendar_records()

        # Rebuild all calendar records
        configurator_list = self.search([])
        for configurator in configurator_list:
            for line in configurator.line_ids:
                configurator._generate_record_from_line(line)
        # self.env['log'].info('Calendar generated')
        return True

    def _generate_record_from_line(self, line):
        """
        Create super_calendar records from super_calendar_configurator_line
        objects.
        """
        super_calendar_pool = self.env['super.calendar']
        values = self._get_record_values_from_line(line)
        for record, super_calendar_values in values.items():
            super_calendar_pool.create(super_calendar_values)

    def _get_record_values_from_line(self, line):
        """
        Generate values to create super.calendar records from
        super.calendar.configurator.line.
        """
        values = {}
        current_pool = self.env[line.name.model]
        domain = line.domain and safe_eval(line.domain) or []
        current_record_list = current_pool.search(domain)
        for cur_rec in current_record_list:
            f_user = line.user_field_id.name
            f_descr = line.description_field_id.name
            f_date_start = line.date_start_field_id.name
            f_date_stop = line.date_stop_field_id.name
            f_duration = line.duration_field_id.name

            # Check if f_user refers to a res.users
            if f_user and cur_rec[f_user] and cur_rec[f_user]._name != 'res.users':
                raise UserError(_("The 'User' field of record %s (%s) does not refer to res.users") % (
                    cur_rec[f_descr], line.name.model))

            if (cur_rec[f_descr] or line.description_code) and cur_rec[f_date_start]:
                duration = False

                if line.date_start_field_id.ttype == 'date':
                    date_format = DEFAULT_SERVER_DATE_FORMAT
                else:
                    date_format = DEFAULT_SERVER_DATETIME_FORMAT
                date_start = datetime.strptime(str(cur_rec[f_date_start]), date_format)
                # Utilisation de "DEFAULT_SERVER_DATETIME_FORMAT" et "DEFAULT_SERVER_DATE_FORMAT"
                # pour les formats de date et d'heure par défaut
                if not line.duration_field_id and line.date_stop_field_id and cur_rec[f_date_start] and cur_rec[
                    f_date_stop]:
                    if line.date_stop_field_id.ttype == 'date':
                        date_format = DEFAULT_SERVER_DATE_FORMAT
                    else:
                        date_format = DEFAULT_SERVER_DATETIME_FORMAT
                    date_stop = datetime.strptime(str(cur_rec[f_date_stop]), date_format)
                    date_diff = (date_stop - date_start)
                    duration = date_diff.total_seconds() / 3600
                elif line.duration_field_id:
                    duration = cur_rec[f_duration]

                if line.description_type != 'code':
                    name = cur_rec[f_descr]
                else:
                    parse_dict = {'o': cur_rec}
                    mytemplate = Template(line.description_code)
                    name = mytemplate.render(**parse_dict)

                if line.date_start_field_id.ttype == 'date':
                    tz = timezone(self._context.get('tz') or self.env.user.tz or 'UTC')
                    local_date_start = tz.localize(date_start)
                    utc_date_start = local_date_start.astimezone(utc)
                    date_start = utc_date_start
                date_start = datetime.strftime(date_start, DEFAULT_SERVER_DATETIME_FORMAT)

                if isinstance(cur_rec['id'], str):
                    rec_id = cur_rec['id'].split('-')[0]
                else:
                    rec_id = cur_rec['id']

                super_calendar_values = {
                    'name': name,
                    'date_start': date_start,
                    'duration': duration,
                    'user_id': f_user and cur_rec[f_user].id or False,
                    'configurator_id': self.id,
                    'res_id': f'{line.name.model},{rec_id}',
                    'model_id': line.name.id,
                }
                values[cur_rec] = super_calendar_values
        return values
