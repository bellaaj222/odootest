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

    @api.onchange('workflow_id')
    def onchange_workflow_id(self):
        """
        When a workflow gets changed we need to collect workflow stages
        and link them to the project as well.
        """
        if self.workflow_id:
            self.type_ids = self.workflow_id.state_ids.mapped('stage_id')
        else:
            self.type_ids = []

    @api.model
    def create(self, vals):
        if not vals.get('allow_workflow', False):
            vals['workflow_id'] = False
            # vals['type_ids'] = []
        new = super().create(vals)

        if new.allow_workflow and new.workflow_id:
            publisher = self.get_workflow_publisher()
            publisher.publish(
                False, new.workflow_id, project_id=new, switch=True
            )

        return new

    def write(self, vals):
        if 'allow_workflow' in vals and not vals['allow_workflow']:
            vals['workflow_id'] = False
            # vals['type_ids'] = [(5,)]

        return super().write(vals)

    def get_workflow_publisher(self):
        return self.env['project.workflow.publisher']

    def button_run_workflow_wizard(self):
        """
        This method opens ``project_edit_workflow_wizard_action`` wizard.
        :return: Returns ``project_edit_workflow_wizard_action`` action.
        """
        self.ensure_one()
        return self.get_edit_workflow_wizard_action()

    def get_edit_workflow_wizard_action(self):
        """
        Loads and prepares an action which opens a wizard for setting or
        switching a workflow on the current project.
        :return: Returns a prepared action which opens a wizard for setting or
        switching a workflow on the current project.
        """
        self.ensure_one()
        workflow_id = self.workflow_id.id if self.workflow_id else False
        action = self.load_edit_workflow_wizard_action()
        action_context = action.get('context', False)
        action_context = action_context and safe_eval(action_context) or {}
        action_context['default_current_workflow_id'] = workflow_id
        action_context['default_project_id'] = self.id
        action['context'] = action_context
        return action

    @api.model
    def load_edit_workflow_wizard_action(self):
        """
        Loads an action which opens a wizard for setting or switching
        a workflow on a project.
        :return: Returns an action which opens a wizard for setting or
        switching a workflow on a project.
        """
        return self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow_management',
            'project_edit_workflow_wizard_action'
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

    wkf_state_id = fields.Many2one(
        comodel_name='project.workflow.state',
        string='Workflow State',
        compute="_compute_workflow_state",

        compute_sudo=True,
        store=True
    )

    # wkf_state_type = fields.Selection(
    #     related='wkf_state_id.type',
    #     string='Wkf State Type'
    # )
    @api.model
    def _read_workflow_stage_ids(self, stages, domain, order):
        if 'default_project_id' not in self.env.context:
            return self._read_group_stage_ids(stages, domain, order)

        project = self.env['project.project'].browse(
            self.env.context['default_project_id']
        )

        if not project.allow_workflow or \
                not project.workflow_id or not project.workflow_id.state_ids:
            return self._read_group_stage_ids(stages, domain, order)

        sorted_state_ids = project.workflow_id.state_ids.sorted(
            key=lambda s: s.kanban_sequence
        )
        stage_ids = [x.stage_id.id for x in sorted_state_ids]
        return stages.browse(stage_ids)

    @api.depends(
        'stage_id', 'workflow_id', 'project_id.workflow_id',
        'workflow_id.state_ids', 'workflow_id.state_ids.stage_id')
    def _compute_workflow_state(self):
        state = self.env['project.workflow.state']
        with_workflow = self.filtered(lambda r: r.project_id.allow_workflow)

        for task in with_workflow:
            if task.project_id.allow_workflow:
                wkf_state = state.search([
                    ('workflow_id', '=', task.workflow_id.id),
                    ('stage_id', '=', task.stage_id.id)
                ])
                task.wkf_state_id = wkf_state.exists() and \
                                    wkf_state.id or False
            else:
                task.wkf_state_id = False

    # @api.onchange('stage_id', 'workflow_id', 'project_id.workflow_id')
    # def _onchange_workflow_state(self):
    #     state = self.env['project.workflow.state']
    #     if self.project_id.allow_workflow:
    #         wkf_state = state.search([
    #             ('workflow_id', '=', self.workflow_id.id),
    #             ('stage_id', '=', self.stage_id.id)
    #         ])
    #         self.wkf_state_id = wkf_state.exists() and wkf_state.id or False
    #     else:
    #         self.wkf_state_id = False
