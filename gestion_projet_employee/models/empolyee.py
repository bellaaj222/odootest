from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProjectEmployee(models.Model):
    _name = 'project.employee'
    _description = 'Project Employee'

    project_id = fields.Many2one('project.project', string='Project')
    weighting = fields.Integer(string='Weighting', digits=(1, 10))
    active = fields.Boolean(string="Active", default=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees')

    @api.constrains('weighting')
    def _check_weighting(self):
        for record in self:
            if record.weighting < 1 or record.weighting > 10:
                raise ValidationError("Weighting must be between 1 and 10.")
