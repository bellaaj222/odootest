from odoo import api, fields, models

class View(models.Model):
    _inherit = 'ir.ui.view'
    
    type = fields.Selection(selection_add=[
        ('webganttview', "Gantt View")
        ], ondelete={'webganttview': 'cascade'})