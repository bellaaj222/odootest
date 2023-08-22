import logging
import base64
import io
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class WorkflowExportWizard(models.TransientModel):
    _name = 'project.workflow.export.wizard'
    _description = 'Workflow Export Wizard'

    workflow_id = fields.Many2one(
        comodel_name='project.workflow',
        string='Workflow',
        domain=[('state', '=', 'live')]
    )

    data = fields.Binary(
        string='File',
        readonly=True,
    )

    file_name = fields.Char(
        string='File Name',
        readonly=True,
    )

    state = fields.Selection([
        ('start', 'Start'),
        ('end', 'End'),
    ], default='start')

    def button_export(self):
        self.ensure_one()

        exporter = self.get_workflow_exporter()

        stream = io.StringIO()
        exporter.wkf_write(self.workflow_id, stream, "utf-8")
        xml_string = stream.getvalue()
        stream.close()

        file_name = f"{self.workflow_id.name}.xml"

        self.write({
            'data': base64.b64encode(xml_string.encode("utf-8")),
            'file_name': file_name,
            'state': 'end'
        })

        action = self.env['ir.actions.act_window'].sudo().for_xml_id(
            'project_workflow_management',
            'project_workflow_export_wizard_action'
        )
        action['res_id'] = self.id
        return action

    def get_workflow_exporter(self):
        return self.env['project.workflow.xml.writer']
