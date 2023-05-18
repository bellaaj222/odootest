from odoo import api, fields, models


class HospitalAppointement(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hospital Appointment"
    _rec_name = 'patient_id'
    patient_id = fields.Many2one(comodel_name='hospital.patient', string="Patient")
    gender = fields.Selection(related='patient_id.gender')  # readonly=False pour editer

    appointment_time = fields.Datetime(string="Appointment Time", default=fields.Datetime.now)
    booking_date = fields.Date(string="Booking Date", default=fields.Date.context_today)
    ref = fields.Char(string="Reference", help="Reference of the patient")
    prescription = fields.Html(string="Prescription")
    priority = fields.Selection([('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')],
                                string='Priority')  # pour les starts de priotirity
    state = fields.Selection(
        [('draft', 'Draft'), ('in_consultation', 'In_consultation'), ('done', 'Done'), ('cancel', 'Cancel')],
        string='Status', default="draft", required="True")  # pour les starts de priotirity
    doctor_id = fields.Many2one('res.users', string='Doctor', tracking=True)

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        print(self, self.patient_id, self.patient_id.ref)
        self.ref = self.patient_id.ref  # POUR ENTRER LE REF QUI EXISTER DANS PATIENT

    def action_test(self):
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Click Successfully',
                'type': 'rainbow_man',
            }
        }

    def action_in_consultation(self):
        for rec in self:
            rec.state = 'in_consultation'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'
