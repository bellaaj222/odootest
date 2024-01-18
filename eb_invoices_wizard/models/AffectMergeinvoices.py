# -*- coding: utf-8 -*-
from odoo import models, fields


class AffectMergeInvoices(models.Model):
    _name = 'base.invoices.affect.merge'
    _description = 'Affect Merge Invoices'

    # Vos autres champs existants

    employee_ids = fields.Many2many('hr.employee', string='Employés affectés')
