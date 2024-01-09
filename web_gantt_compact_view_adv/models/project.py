from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta


class ProjectTask(models.Model):
    _inherit = "project.task"

    planned_date_begin = fields.Datetime(string='Planned start', index=True, tracking=True, copy=False,
                                         task_dependency_tracking=True)
    planned_date_end = fields.Datetime(string='Planned stop', index=True, tracking=True, copy=False,
                                       task_dependency_tracking=True)
    task_type = fields.Selection([
        ('task', 'Task'),
        ('milestone', 'Milestone')
    ], string="Task Type", required=True, default='task')
    color = fields.Integer('Project color', default=4)
    task_link_ids = fields.One2many('project.task.link', 'source_id', string="Task Links")
    task_priority = fields.Selection([
        ('normal', 'Normal'),
        ('low', 'Low'),
        ('high', 'High')
    ], string='Priority', required=True, default='normal')
    progress = fields.Integer(tracking=True)

    @api.onchange('planned_date_end')
    def onchange_gantt_stop_date(self):
        if self.planned_date_begin and self.planned_date_end and self.planned_date_end < self.planned_date_begin:
            self.planned_date_end = self.planned_date_begin

    @api.onchange('task_type', 'planned_date_begin')
    def onchange_task_type(self):
        if self.planned_date_begin and self.task_type == 'milestone':
            self.planned_date_end = self.planned_date_begin + timedelta(hours=1)

    @api.model
    def search_read_links(self, domain=None):
        datas = []
        tasks = self.env['project.task'].search(domain)
        for task in tasks:
            if task.task_link_ids:
                for link in task.task_link_ids:
                    link_vals = {
                        'id': link.id,
                        'source': task.id,
                        'target': link.target_id.id,
                        'type': link.link_type,
                    }
                    datas.append(link_vals)
        return datas


class ProjectTaskLink(models.Model):
    _name = "project.task.link"
    _description = "Project Task Links"

    source_id = fields.Many2one('project.task', string='Task')
    target_id = fields.Many2one('project.task', string='Target Task', required=True)
    link_type = fields.Selection([
        ('0', "Finish to Start"),
        ('1', "Start to Start"),
        ('2', "Finish to Finish"),
        ('3', "Start to Finish")
    ], string="Link Type", required=True, default='1')
