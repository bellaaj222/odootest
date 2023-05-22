from odoo import models, fields, api


class GestionEmployee(models.Model):
    _name = "gestion.employe"
    _description = "Gestion Empolyee"

    name = fields.Char(string='Name')
    date_of_birth = fields.Date(string="Date Of Birth")
    ref = fields.Char(string="Reference")
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
