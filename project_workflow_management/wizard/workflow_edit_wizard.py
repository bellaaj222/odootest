from odoo import models, fields, api


class ProjectWorkflowEditWizard(models.TransientModel):
    _name = 'project.workflow.edit.wizard'
    _description = 'Project Workflow Edit Wizard'

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
    )

    type = fields.Selection(
        selection=[('form', 'Form'), ('diagram', 'Diagram')],
        string='Editor Type',
        default='form',
    )

    def open_editor(self):
        self.ensure_one()
        action_name = f'project_workflow_{self.type}_edit_action'
        action = self.env['ir.actions.act_window'].sudo().for_xml_id(
            'project_workflow_management', action_name
        )
        action['res_id'] = self.workflow_id.id
        return action
