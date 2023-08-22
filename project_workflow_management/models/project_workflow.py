from odoo import models, fields, api


class Workflow(models.Model):
    _name = 'project.workflow'
    _description = 'Project Workflow'

    name = fields.Char(
        string='Name',
        required=True,
        help="The name of the workflow. It has to be unique!"
    )
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('live', 'Live')],
        string='State',
        default='draft',
        copy=False,
        index=True,
    )
    description = fields.Html(
        string='Description',
        help="Describe this workflow for your colleagues ..."
    )
    default_state_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string="Default state",
        help="Stage from this state will be set by default if not specified "
             "when creating task.",
    )
    transition_ids = fields.One2many(
        comodel_name='project.workflow.transition',
        inverse_name='workflow_id',
        ondelete="cascade",
        string='Transitions',
        copy=True,
        help="The list of all state transitions."
    )
    project_ids = fields.One2many(
        comodel_name='project.project',
        inverse_name='workflow_id',
        string='Projects',
        help="The list of related projects."
    )
    state_ids = fields.One2many(
        comodel_name='project.workflow.state',
        inverse_name='workflow_id',
        string='States',
        copy=True,
        help="The list of all possible states a task can be in."
    )
    stage_ids = fields.Many2many(
        'project.task.type',
        compute="_compute_stage_ids",
        string='All workflow task stages'
    )
    edit_count = fields.Integer(
        string='Edit Count',
        compute="_compute_edit_count",
    )

    edit_ids = fields.One2many(
        'project.workflow',
        'original_id',
        string='Drafts',
    )
    original_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Origin',
        ondelete="cascade",
    )
    original_name = fields.Char(
        string='Original',
        related='original_id.name',
        readonly=True,
    )

    @api.depends('state_ids')
    def _compute_stage_ids(self):
        for record in self:
            record.stage_ids = record.state_ids.mapped('stage_id')

    @api.depends('edit_ids')
    def _compute_edit_count(self):
        for workflow in self:
            workflow.edit_count = len(workflow.edit_ids)

    class WorkflowState(models.Model):
        _name = 'project.workflow.state'
        _description = 'Project Workflow State'
        _order = 'sequence'

        stage_id = fields.Many2one(
            'project.task.type',
            string='Stage',
            required=True,
            ondelete="restrict",
            index=True,
        )

        name = fields.Char(
            string='Name',
            related='stage_id.name',
            required=True,
        )

        description = fields.Text(
            string='Description',
            related='stage_id.description',
            required=True,
        )

        workflow_id = fields.Many2one(
            'project.workflow',
            string='Workflow',
            required=True,
            ondelete="cascade",
        )

        is_default = fields.Boolean(
            string="Is default",
            compute="_compute_is_default",
            inverse="_inverse_is_default",
        )

        is_global = fields.Boolean(
            string='Is global?',
            default=False,
            help="When checked it will allow all transitions from/to this state.",
        )

        out_transitions = fields.One2many(
            'project.workflow.transition',
            'src_id',
            string='Outgoing Transitions'
        )

        in_transitions = fields.One2many(
            'project.workflow.transition',
            'dst_id',
            string='Incoming Transitions'
        )

        type = fields.Selection(
            selection=[
                ('todo', 'ToDo'),
                ('in_progress', 'In Progress'),
                ('done', 'Done'),
            ],
            default='in_progress',
            string='Type',
            required=True,
        )

        xpos = fields.Integer(
            string='X',
            default=50,
            copy=True,
        )

        ypos = fields.Integer(
            string='Y',
            default=50,
            copy=True,
        )

        sequence = fields.Integer(
            string='Sequence',
            default=0,
            help="Value of sequence determines order of transitions. "
                 "When Task is in a workflow state, available transitions are"
                 "shown according to their destinations state sequence.",
        )

        kanban_sequence = fields.Integer(
            string='Kanban Sequence',
            default=0,
            help="Kanban sequence is used for defining order of states"
                 "in kanban view.",
        )

        _sql_constraints = [
            ('unique_state_stage', 'UNIQUE(workflow_id,stage_id)',
             'This state already exists!'
             )
        ]

        def _compute_is_default(self):
            for record in self:
                default_state = record.workflow_id.default_state_id
                record.is_default = default_state.id == record.id

        class WorkflowTransition(models.Model):
            _name = 'project.workflow.transition'
            _description = 'Project Workflow Transition'

            name = fields.Char(
                string='Name',
                required=True,
            )

            description = fields.Html(
                string='Description'
            )

            workflow_id = fields.Many2one(
                'project.workflow',
                string='Workflow',
                required=True,
                ondelete="cascade",
            )

            src_id = fields.Many2one(
                'project.workflow.state',
                string='Source Stage',
                required=True,
                index=True,
                ondelete="cascade",
            )

            dst_id = fields.Many2one(
                'project.workflow.state',
                string='Destination Stage',
                required=True,
                index=True,
                ondelete="cascade",
            )

            user_confirmation = fields.Boolean(
                string='User Confirmation?',
                default=False
            )

            _sql_constraints = [
                ('unique_src_dst', 'unique(workflow_id, src_id, dst_id)',
                 'This transition already exists!')
            ]
