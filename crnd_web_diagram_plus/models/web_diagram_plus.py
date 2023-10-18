from odoo import models, fields, api

DEFAULT_BG_COLOR = 'rgba(120,120,120,1)'
DEFAULT_LABEL_COLOR = 'rgba(255,255,255,1)'


class WebDiagramPlus(models.Model):
    _name = 'web.diagram.plus'
    _description = 'Web Diagram Plus'

    name = fields.Char(required=True)
    project_ids = fields.One2many('project.project', 'web_diagram_id', string='project')
    node_ids = fields.One2many(
        'web.diagram.plus.node', 'web_diagram_id', string='Nodes', copy=True)
    arrow_ids = fields.One2many(
        'web.diagram.plus.arrow', 'web_diagram_id', string='Arrows', copy=True, )

    arrow_count = fields.Integer(string='Arrow Count', compute='_compute_arrow_count', store=True)
    index = fields.Integer(string='Index', readonly=True)
    node_count = fields.Integer(
        compute='_compute_node_count',
        store=True,
        string='Node Count'
    )

    @api.depends('node_ids')
    def _compute_node_count(self):
        for diagram in self:
            diagram.node_count = len(diagram.node_ids)

    # @api.depends('arrow_ids')  # Mettez les champs pertinents ici
    # def _compute_arrow_count(self):
    #     for index, row in enumerate(self, start=1):
    #         row.arrow_count = len(row.arrow_ids)  # Utilisez la liste d'arrows pour compter les éléments
    #         row.index = index
    #         print(row.index)

    @api.depends('arrow_ids')
    def _compute_arrow_count(self):
        for row in self:
            sorted_arrows = sorted(row.arrow_ids, key=lambda x: x.id)
            row.arrow_count = len(sorted_arrows)
            for index, arrow in enumerate(sorted_arrows, start=1):
                arrow.index = index

    @api.model
    def get_action_by_xmlid(self, xmlid, context=None, domain=None):
        action = self.env.ref(xmlid)
        assert isinstance(  # nosec
            self.env[action._name], type(self.env['ir.actions.actions']))
        action = action.read()[0]
        if context is not None:
            action['context'] = context
        if domain is not None:
            action['domain'] = domain

        return action

    def action_web_diagram_plus(self):
        self.ensure_one()
        action = self.get_action_by_xmlid(
            'crnd_web_diagram_plus.action_web_diagram_plus_model',
            context={'default_web_diagram_id': self.id},
        )
        action.update({
            'res_model': 'web.diagram.plus',
            'res_id': self.id,
            'views': [(False, 'diagram_plus'), (False, 'form')],
        })
        return action

    @api.model
    def update_arrow_count(self, arrow_ids):
        row_ids = arrow_ids.mapped('web_diagram_id')
        for row in row_ids:
            row._compute_arrow_count()


class WebDiagramPlusNode(models.Model):
    _name = 'web.diagram.plus.node'
    _description = 'Web Diagram Plus Node'

    name = fields.Char(string='Name', related='categ.complete_name', equired=True)
    categ = fields.Many2one('product.category', required=True, string='Département')

    web_diagram_id = fields.Many2one(
        'web.diagram.plus', 'Project Diagram', ondelete='cascade',
        required=True, index=True)

    res_bg_color = fields.Char(
        default=DEFAULT_BG_COLOR, string="Backgroung Color")
    res_label_color = fields.Char(
        default=DEFAULT_LABEL_COLOR)

    arrow_in_ids = fields.One2many(
        'web.diagram.plus.arrow', 'to_node_id', 'Incoming Arrows')
    arrow_out_ids = fields.One2many(
        'web.diagram.plus.arrow', 'from_node_id', 'Outgoing Arrows')

    diagram_position = fields.Text()

    node_count = fields.Integer(
        compute='_compute_node_count',
        store=True,
        string='Node Count'
    )

    @api.depends('web_diagram_id.node_ids')
    def _compute_node_count(self):
        for node in self:
            node.node_count = len(node.web_diagram_id.node_ids)


class WebDiagramPlusArrow(models.Model):
    _name = 'web.diagram.plus.arrow'
    _description = 'Web Diagram Plus Arrow'

    name = fields.Many2one('base.flow.merge.automatic.wizard', required=True, string='Action')
    actions = fields.Selection([('keep', 'Laisser Les Taches Actives (Pas de changement de statut)'),
                                ('permis',
                                 'Terminer Les Taches(Retire les taches du tableau de bord mais reste affichable après recherche)'),
                                ('archiv',
                                 'Archiver Les Taches Sélectionnées(Retire les taches du tableau de bord et de la recherche)'),
                                ('suspend', 'Suspendre Temporairement Les Taches Encours'),
                                ('treated', 'Cloturer Définitivement Les Taches Encours'),

                                ], readonly=True, related="name.actions")

    workflow_action_id = fields.Char(
        string='Workflow Action ID',
        compute='_compute_workflow_action_id',
        store=True,
        readonly=True
    )
    workflow_name_id = fields.Char(
        string='Workflow Action ID',
        compute='_compute_workflow_name_id',
        store=True,
        readonly=True
    )

    date = fields.Date(string='Date')
    arrow_ids = fields.One2many(
        'web.diagram.plus.arrow', 'web_diagram_id', string='Arrows', copy=True)

    created_by = fields.Many2one('res.users', string='Created By', readonly=True, default=lambda self: self.env.user)
    arrow_count = fields.Integer(string='Arrow Count', compute='_compute_arrow_count', store=True)

    web_diagram_id = fields.Many2one(
        'web.diagram.plus', 'Web Diagram', ondelete='cascade',
        required=True, index=True, tracking=True)

    from_node_id = fields.Many2one(
        'web.diagram.plus.node', 'Department source', ondelete='restrict',
        required=True, index=True, tracking=True)
    to_node_id = fields.Many2one(
        'web.diagram.plus.node', 'Department destination', ondelete='restrict',
        required=True, index=True)
    index = fields.Integer(string='Index', readonly=True)

    # def action_open_workflow_action(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Créer une action workflow',
    #         'res_model': 'base.flow.merge.automatic.wizard',  # Remplacez par le nom de votre modèle
    #         'view_mode': 'form',
    #         'view_type': 'form',
    #         'view_id': self.env.ref('crnd_web_diagram_plus.action.workflow.tree').id,
    #         # Remplacez par l'ID de la vue de création d'action workflow
    #         'target': 'new',
    #     }

    @api.depends('arrow_ids')
    def _compute_arrow_count(self):
        for row in self:
            sorted_arrows = sorted(row.arrow_ids, key=lambda x: x.id)
            row.arrow_count = len(sorted_arrows)
            for index, arrow in enumerate(sorted_arrows, start=1):
                arrow.index = index


    @api.model
    def update_arrow_count(self, arrow_ids):
        row_ids = arrow_ids.mapped('web_diagram_id')
        for row in row_ids:
            row._compute_arrow_count()

    @api.model_create_multi
    def create(self, vals_list):
        arrows = super(WebDiagramPlusArrow, self).create(vals_list)
        self.env['web.diagram.plus'].update_arrow_count(arrows)
        return arrows

    def unlink(self):
        row_ids = self.mapped('web_diagram_id')
        super(WebDiagramPlusArrow, self).unlink()
        self.env['web.diagram.plus'].update_arrow_count(row_ids)

    @api.depends('name')
    def _compute_workflow_action_id(self):
        # Mettez ici la logique pour calculer l'ID de l'action du flux de travail
        # en fonction du champ 'name' ou d'autres champs pertinents.
        for arrow in self:
            # Exemple de calcul basique : utiliser le nom comme ID
            arrow.workflow_action_id = arrow.name.name if arrow.name else ''

    @api.depends('created_by')
    def _compute_workflow_name_id(self):
        for arrow in self:
            # Utiliser le nom de l'utilisateur comme ID de l'action du flux de travail
            arrow.workflow_name_id = arrow.created_by.name if arrow.created_by else ''
            print(arrow.workflow_name_id)

# def get_date_action_values(self):
#     # Utilisez la méthode `search` pour récupérer les enregistrements de ce modèle
#     records = self.search([])
#
#     # Récupérez les valeurs de date_action pour chaque enregistrement
#     date_action_values = records.mapped('date_action')
#
#     return date_action_values
