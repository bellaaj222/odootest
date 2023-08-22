from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_project_workflow_action = fields.Boolean(
        string="Workflow Action"
    )

    module_project_workflow_security = fields.Boolean(
        string="Workflow Security"
    )

    module_project_workflow_transition_by_project = fields.Boolean(
        string="Workflow Transitions by Project"
    )

    module_project_workflow_default_state_per_group = fields.Boolean(
        string="Default task states per security group"
    )
