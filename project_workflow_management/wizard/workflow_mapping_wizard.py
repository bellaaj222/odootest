from odoo import models, fields, api


class WorkflowMappingWizard(models.TransientModel):
    _name = 'project.workflow.stage.mapping.wizard'
    _description = 'Workflow Stage Mapping Wizard'

    def _default_from_diagram(self):
        return self.env.context.get('default_from_diagram', False)

    from_id = fields.Many2one(
        comodel_name='project.workflow',
        string='From'
    )

    to_id = fields.Many2one(
        comodel_name='project.workflow',
        string='To',
    )

    line_ids = fields.One2many(
        comodel_name='project.workflow.stage.mapping.wizard.line',
        inverse_name='wizard_id',
        required=True,
    )

    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )

    switch = fields.Boolean(
        string='Just Switch',
        default=False,
    )

    from_diagram = fields.Boolean(
        string='Initiated from diagram?',
        default=lambda s: s._default_from_diagram()
    )

    def button_finish(self):
        self.ensure_one()

        stages = [{'from': x.from_id.stage_id.id, 'to': x.to_id.stage_id.id} for x in self.line_ids]
        mappings = {'stages': stages}

        publisher = self.get_workflow_publisher()
        publisher.publish(self.from_id, self.to_id, mappings, project_id=self.project_id, switch=self.switch)

        multi_action = {
            'type': 'ir.actions.act_multi',
            'actions': [
                {'type': 'ir.actions.act_window_close'},
                {'type': 'ir.actions.act_view_reload'},
            ]
        }

        if self.from_diagram:
            multi_action['actions'].append({'type': 'history_back'})

        return multi_action

    def get_workflow_publisher(self):
        return self.env['project.workflow.publisher']


class WorkflowMappingWizardLine(models.TransientModel):
    _name = 'project.workflow.stage.mapping.wizard.line'
    _description = 'Workflow Mapping Wizard Line'

    wizard_id = fields.Many2one(
        comodel_name='project.workflow.stage.mapping.wizard',
        string='Wizard',
        required=True,
        ondelete="cascade"
    )

    from_id = fields.Many2one(
        comodel_name='project.workflow.stage.mapping.wizard.stage',
        domain="[('wizard_id', '=', wizard_id), ('type', '=', 'from')]",
        string='From Stage',
        readonly=True,
    )

    task_count = fields.Integer(
        string='Task Count',
        related='from_id.task_count',
        readonly=True,
    )

    to_id = fields.Many2one(
        comodel_name='project.workflow.stage.mapping.wizard.stage',
        domain="[('wizard_id', '=', wizard_id), ('type', '=', 'to')]",
        string='To Stage',
    )

    @api.onchange('from_id')
    def _onchange_from_id(self):
        self.to_id = False


class WorkflowMappingWizardStage(models.TransientModel):
    _name = 'project.workflow.stage.mapping.wizard.stage'
    _description = 'Workflow Mapping Wizard Stage'

    wizard_id = fields.Many2one(
        comodel_name='project.workflow.stage.mapping.wizard',
        string='Wizard',
        required=True,
        ondelete="cascade"
    )

    type = fields.Selection(
        selection=[('from', 'From'), ('to', 'To')],
        string='Type',
    )

    task_count = fields.Integer(
        string='Task Count',
        default=0,
        help="Applicable only for stages of type 'from'",
    )

    stage_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Stage',
        required=False,
    )

    name = fields.Char(
        string='Name',
        related='stage_id.name',
        readonly=True,
    )
