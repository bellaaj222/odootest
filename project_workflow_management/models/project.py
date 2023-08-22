from odoo import models, fields, api


class Project(models.Model):
    _inherit = 'project.project'

    allow_workflow = fields.Boolean(
        string='Allow Workflow?',
        default=False,
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        ondelete="restrict",
        help="Project Workflow"
    )


class Task(models.Model):
    _inherit = 'project.task'

    allow_workflow = fields.Boolean(
        related="project_id.allow_workflow",
        readonly=True,
    )
    #
    # stage_id = fields.Many2one(group_expand='_read_workflow_stage_ids')


    wkf_stage_id = fields.Many2one(
        comodel_name='project.task.type',
        related='stage_id',
        string='Workflow Stage',
        readonly=True,
        track_visibility='never',
    )

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        related='project_id.workflow_id',
        readonly=True,
    )

    # wkf_state_id = fields.Many2one(
    #     comodel_name='project.workflow.state',
    #     string='Workflow State',
    #     compute="_compute_workflow_state",
    #     compute_sudo=True,
    #     store=True
    # )

    # wkf_state_type = fields.Selection(
    #     related='wkf_state_id.type',
    #     string='Wkf State Type'
    # )
