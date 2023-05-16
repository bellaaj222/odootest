from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api


class HospitalPatient(models.Model):
    _name = "hospital.patient"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Patient"

    name = fields.Char(string='Name', tracking=True)
    date_of_birth = fields.Date(string="Date Of Birth")
    ref = fields.Char(string="Reference", tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age', store=True, tracking=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender", tracking=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    appointment_id = fields.Many2one(comodel_name='hospital.appointment', string="Appointments")

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            today = date.today()
            print(today)
            if rec.date_of_birth:
                print(rec, rec.name, rec.date_of_birth, rec.gender)
                rec.age = today.year - rec.date_of_birth.year
            else:
                rec.age = 0
