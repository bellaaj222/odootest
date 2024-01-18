from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    product_id = fields.Many2one('product.product', string='Product', ondelete='cascade', select="1", readonly=True,
                                 states={'draft': [('readonly', False)]}, )
    partner_id = fields.Many2one('res.partner', string='Customer', )
    recurrence_id = fields.Many2one('project.task.recurrence', copy=False)
    kit_id = fields.Many2one('product.kit', 'Kit ID', ondelete='cascade', select="1", readonly=True,
                             states={'draft': [('readonly', False)]}, )
    uom_id = fields.Many2one('product.uom', string='Unité', readonly=True,
                             states={'draft': [('readonly', False)]}, )
