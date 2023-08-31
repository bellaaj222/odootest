from odoo import models, fields, api, exceptions, _
from odoo.tools.safe_eval import safe_eval


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
        help="The list of all possible states a task can be in.",
        editable=True,  # Add this line to make the field editable
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

    type = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done')
    ], string='Type')

    # src_id = fields.Many2one(
    #     'project.workflow.state',
    #     string='Source Stage',
    #     index=True,
    #     ondelete="cascade",
    # )
    dst_id = fields.Many2one(
        'project.workflow.state',
        string='Destination Stage',

    )

    @api.depends('state_ids')
    def _compute_stage_ids(self):
        for record in self:
            record.stage_ids = record.state_ids.mapped('stage_id')

    @api.depends('edit_ids')
    def _compute_edit_count(self):
        for workflow in self:
            workflow.edit_count = len(workflow.edit_ids)

    @api.model
    def copy(self, default=None):
        default = default or {}
        if 'name' not in default:
            default['name'] = "%s (COPY)" % self.name

        new_workflow = super(Workflow, self).copy(default)

        states = dict()
        for state in new_workflow.state_ids:
            states[state.stage_id.id] = state

        def get_new_default_state_id():
            for state in new_workflow.state_ids:
                if state.stage_id.id == self.default_state_id.stage_id.id:
                    return state.id
            return False

        new_default_state_id = get_new_default_state_id()

        for transition in new_workflow.transition_ids:
            src_id = states[transition.src_id.stage_id.id].id
            dst_id = states[transition.dst_id.stage_id.id].id
            transition.write({'src_id': src_id, 'dst_id': dst_id})

        new_workflow.write({'default_state_id': new_default_state_id})

        return new_workflow

    def unlink(self):
        for workflow in self:
            if workflow.project_ids:
                projects = ", ".join([p.name for p in workflow.project_ids])
                raise exceptions.ValidationError(_(
                    "You are not allowed to delete this workflow because it is"
                    " being used by the following projects: %s"
                ) % projects)
        return super(Workflow, self).unlink()

    def is_live(self):
        self.ensure_one()
        return self.state == 'live'

    def is_draft(self):
        self.ensure_one()
        return self.state == 'draft'

    def find_transition(self, task, stage_id):
        def check_transition(t, s):
            return t.workflow_id and t.stage_id.id != s

        if not check_transition(task, stage_id):
            return False

        transitions = self.find_transitions(
            task, task.stage_id.id, group_by='stage_id'
        )

        if stage_id not in transitions:
            raise exceptions.ValidationError(_(
                "Transition to this state is not supported "
                "from the current task state!\n"
                "Please refer to the project workflow '%s' to "
                "see all possible transitions from "
                "the current state or you could view the task in "
                "form view and see possible transitions"
                "from there."
            ) % self.name)

        return transitions[stage_id]

    def trigger(self, task, target_stage_id):
        self.ensure_one()

        transition = self.find_transition(task, target_stage_id)

        if not transition:
            return

        if transition['global']:
            self.env['project.workflow.state'].browse(
                transition['state_id']
            ).apply(task)
        else:
            self.env['project.workflow.transition'].browse(
                transition['transition_id']
            ).apply(task)

    def get_state_transitions(self, workflow_id, stage_id, task_id):
        if not workflow_id or not stage_id:
            return []

        workflow = self.browse(workflow_id)
        task = self.env['project.task'].browse(task_id)

        transitions = workflow.find_transitions(task, stage_id)
        return transitions

    def get_available_transitions(self, task, state):
        return state.out_transitions

    def _populate_state_for_widget(self, transition):
        return {
            'global': False,
            'transition_id': transition.id,
            'name': transition.name,
            'desc': transition.description,
            'confirmation': transition.user_confirmation,
            'id': transition.dst_id.stage_id.id,
            'sequence': transition.dst_id.sequence,
        }

    def export_workflow(self):
        self.ensure_one()
        wizard = self.env['project.workflow.export.wizard'].create(
            {'workflow_id': self.id}
        )
        return wizard.button_export()

    def open_diagram_view(self):
        action = self.env.ref('project_workflow_management.project_workflow_diagram_edit_action')
        ctx = self.env.context.copy()
        ctx['active_id'] = self.id
        ctx['active_ids'] = [self.id]
        action['res_id'] = self.id
        action['context'] = ctx
        return action

    def action_project_workflow_open_diagram(self):
        return {
            'name': 'Edit Diagram',
            'res_model': 'project.workflow',
            'view_mode': 'diagram_plus',
            'view_id': self.env.ref('project_workflow_management.view_project_workflow_diagram').id,
            # Change to your actual view ID
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    def edit_workflow(self):
        print("Debug: Entering edit_workflow method")  # Ajoutez ceci pour indiquer le début de la méthode
        self.ensure_one()

        edit = self
        if self.is_live():
            if len(self.edit_ids) == 0:
                edit = self.copy({
                    'name': _("Draft Version of '%s'") % self.name,
                    'state': 'draft',
                    'default_state_id': self.default_state_id.id,
                    'original_id': self.id
                })
            else:
                edit = self.edit_ids[0]

        action = self.env.ref('project_workflow_management.project_workflow_diagram_edit_action')

        ctx = self.env.context.copy()
        ctx['active_id'] = edit.id
        ctx['active_ids'] = [edit.id]
        action['res_id'] = edit.id

        action['context'] = ctx

        print("Debug: Exiting edit_workflow method with action:",
              action)  # Ajoutez ceci pour indiquer la fin de la méthode
        return action

    # def edit_workflow(self):
    #     print("Debug: Entering edit_workflow method")  # Ajoutez ceci pour indiquer le début de la méthode
    #     self.ensure_one()
    #
    #     edit = self
    #     print("test")
    #     if len(self.edit_ids) == 0:
    #         edit = self.copy({
    #             'name': _("Draft Version of '%s'") % self.name,
    #             'state': 'draft',
    #             'default_state_id': self.default_state_id.id,
    #             'original_id': self.id
    #         })
    #         print("eeeeeeddddddeeeeeeeeeeeeeee", edit)
    #     else:
    #         edit = self.edit_ids[0]
    #         print("eeeeeeeeeeeeeeeeeeeee", edit)
    #
    #     action = self.env.ref('project_workflow_management.project_workflow_diagram_edit_action')
    #
    #     ctx = self.env.context.copy()
    #     ctx['active_id'] = edit.id
    #     ctx['active_ids'] = [edit.id]
    #     action['res_id'] = edit.id
    #
    #     action['context'] = ctx
    #
    #     print("Debug: Exiting edit_workflow method with action:",
    #           action)  # Ajoutez ceci pour indiquer la fin de la méthode
    #     return action

    def publish_workflow(self):
        self.ensure_one()

        if self.is_draft() and self.original_id:
            publisher = self.get_workflow_publisher()
            result = publisher.publish(self.original_id, self)

            if result.has_conflicts:
                from_diagram = self.env.context.get('diagram', False)
                action = result.action
                action_context = safe_eval(action.get('context', '{}'))
                action_context['default_from_diagram'] = from_diagram
                action['context'] = action_context
                return action

        else:
            self.state = 'live'

    def discard_working_copy_from_tree(self):
        self.ensure_one()
        self.with_context(original=True, origin='tree').discard_working_copy()

    def discard_working_copy(self):
        self.ensure_one()

        if self.env.context.get('original', False):
            for edit in self.edit_ids:
                edit.unlink()
            return {'type': 'ir.actions.act_view_reload'}

        self.unlink()

        return {
            'type': 'ir.actions_act_multi',
            'actions': [
                {'type': 'history_back'},
                {'type': 'ir.actions_act_view_reload'},
            ]
        }

    def get_formview_id(self):
        return self.env.ref(
            "project_workflow_management.project_workflow_form").id

    def get_formview_action(self):
        view_id = self.get_formview_id()
        ctx = dict(self._context)
        ctx['edit'] = False
        ctx['create'] = False

        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'current',
            'res_id': self.id,
            'context': ctx,
        }


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

    def _inverse_is_default(self):
        for record in self:
            if record.is_default:
                record.workflow_id.default_state_id = record.id

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        state_ids = self.env.context.get('state_ids', False)
        if state_ids:
            args = args or []
            args.append(('id', 'in', [x[1] for x in state_ids]))

        return super(WorkflowState, self).name_search(
            name, args, operator, limit
        )

    def apply(self, task):
        task.write({'stage_id': self.stage_id.id})


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

    def apply(self, task):
        self.dst_id.apply(task)
