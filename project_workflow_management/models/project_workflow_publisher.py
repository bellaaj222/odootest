# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models, exceptions, _

from odoo import models, fields, api, _


class PublisherResult(models.AbstractModel):
    """
    This model represents the result of a workflow publishing process.
    """
    _name = 'project.workflow.publisher.result'
    _description = 'Workflow Publisher Result'

    # Define the possible status values
    WORKFLOW_PUBLISHED = 'published'
    WORKFLOW_CONFLICTS = 'conflicts'

    # Status field to store the result status
    status = fields.Selection(
        selection=[(WORKFLOW_PUBLISHED, 'Published'), (WORKFLOW_CONFLICTS, 'Conflicts')],
        string='Status',
        required=True,
        readonly=True,
        default=WORKFLOW_PUBLISHED,
    )

    # Action field to store the related action in case of conflicts
    action_id = fields.Many2one(
        comodel_name='ir.actions.act_window',
        string='Action',
        readonly=True,
    )

    @property
    def is_published(self):
        """
        Check if the result indicates that the workflow is successfully published.
        """
        return self.status == self.WORKFLOW_PUBLISHED

    @property
    def has_conflicts(self):
        """
        Check if the result indicates that there are conflicts in the workflow.
        """
        return self.status == self.WORKFLOW_CONFLICTS

    @staticmethod
    def success():
        """
        Create a successful result instance.
        """
        return {'status': PublisherResult.WORKFLOW_PUBLISHED}

    @staticmethod
    def conflict(action):
        """
        Create a result instance indicating conflicts with a specific action.
        """
        return {'status': PublisherResult.WORKFLOW_CONFLICTS, 'action_id': action.id}


class ProjectWorkflowPublisher(models.AbstractModel):
    _name = 'project.workflow.publisher'
    _description = 'Project Workflow Publisher'

    def publish(self, old, new, mappings=None, project_id=None, switch=False):
        """
        Publish a new workflow for a project, handling conflicts and mapping if necessary.
        """
        if not new:
            raise exceptions.ValidationError(_("You have to provide the new workflow!"))

        if not old and not project_id:
            raise exceptions.ValidationError(_(
                "In case old workflow is not present, "
                "you need to provide a project to which "
                "a new workflow will be applied!"
            ))

        diff = self.diff(old, new, project_id, switch)

        if diff['is_empty']:
            return self._do_publish(old, new, project_id=project_id, switch=switch)

        if self._do_map(diff, mappings, old, new, project_id):
            return self._do_publish(old, new, project_id=project_id, switch=switch)

        return PublisherResult.conflict(
            self._get_wizard_action(
                self._build_mapping_wizard(old, new, diff, project_id=project_id, switch=switch)
            )
        )

    def diff(self, old, new, project_id, switch):
        """
        Compare the difference between old and new workflow or project and workflow.
        """
        result = dict()

        def get_states(obj, is_workflow=True):
            if is_workflow:
                states = set(state.stage_id.id for state in obj.state_ids)
                return states
            else:
                self.env.cr.execute(
                    """
                    SELECT distinct(stage_id)
                    FROM project_task
                    WHERE project_id IN %s
                    """, (tuple([obj.id]),)
                )
                return set([x[0] for x in self.env.cr.fetchall()])

        if old and new:
            removed_stages = get_states(old) - get_states(new)
            project_ids = [project_id.id] if switch else old.project_ids.ids
        else:
            removed_stages = get_states(project_id, False) - get_states(new)
            project_ids = [project_id.id]

        hits = []

        for stage_id in removed_stages:
            task_count = self.env['project.task'].search([
                ('project_id', 'in', project_ids), ('stage_id', '=', stage_id)
            ], count=True)

            if task_count > 0:
                hits.append({'id': stage_id or False, 'count': task_count})

        result['stages'] = hits
        result['is_empty'] = len(hits) == 0
        return result

    def _do_map(self, result, mappings, old, new, project_id=None):
        """
        Apply stage mappings if possible.
        """
        if not self._can_be_mapped(result, mappings):
            return False

        if old and new:
            project_ids = old.project_ids.ids
        else:
            project_ids = [project_id.id]

        if 'stages' in mappings:
            for mapping in mappings['stages']:
                tasks = self.env['project.task'].search([
                    ('project_id', 'in', project_ids),
                    ('stage_id', '=', mapping['from'])])
                tasks._write({'stage_id': mapping['to']})
        return True

    def _can_be_mapped(self, result, mappings):
        """
        Check if stages can be mapped.
        """
        if not mappings:
            return False

        if 'stages' in mappings:
            data = set([m['from'] for m in mappings['stages']])
            for stage in result['stages']:
                if stage['id'] not in data:
                    return False

        return True

    def _do_publish(self, old, new, project_id=None, switch=False):
        """
        Publish the new workflow.
        """
        if switch:
            stage_ids = [(6, 0, [x.stage_id.id for x in new.state_ids])]

            if project_id:
                project_id.write({
                    'workflow_id': new.id,
                    'type_ids': stage_ids
                })
            else:
                old.project_ids.write({
                    'workflow_id': new.id,
                    'type_ids': stage_ids
                })
        else:
            data = {}
            if not new.name.startswith('Draft'):
                data['name'] = new.name

            if new.description != old.description:
                data['description'] = new.description

            data['default_state_id'] = False
            if new.default_state_id:
                data['default_state_id'] = new.default_state_id.id

            if data:
                old.write(data)

            old.transition_ids.unlink()
            old.state_ids.unlink()
            new.transition_ids.write({'workflow_id': old.id})
            new.state_ids.write({'workflow_id': old.id})

            new.unlink()

        return PublisherResult.success()

    def _build_mapping_wizard(self, old, new, result, project_id=None,
                              switch=False):
        """
        Build the mapping wizard to handle conflicts and stage mapping.
        """
        wizard = self.env['project.workflow.stage.mapping.wizard'].create(
            self._prepare_mapping_wizard(
                old, new, project_id=project_id, switch=switch
            )
        )

        wstages = []
        for stage in result['stages']:
            wstage = self.env['project.workflow.stage.mapping.wizard.stage'] \
                .create(self._prepare_deleted_wizard_stage(wizard, stage))

            wstages.append(wstage)

        for state in new.state_ids:
            self.env['project.workflow.stage.mapping.wizard.stage'].create(
                self._prepare_possible_stage(wizard, state)
            )

        for wstage in wstages:
            self.env['project.workflow.stage.mapping.wizard.line'].create(
                self._prepare_wizard_line(wizard, wstage)
            )

        return wizard

    def _prepare_mapping_wizard(self, old, new, project_id, switch):
        """
        Prepare data for creating the mapping wizard.
        """
        return {
            'from_id': old.exists() and old.id or False,
            'to_id': new.id,
            'project_id': project_id and project_id.id or False,
            'switch': switch,
            'from_diagram': self.env.context.get('diagram', False)
        }

    def _prepare_deleted_wizard_stage(self, wizard, stage):
        """
        Prepare data for creating a deleted wizard stage.
        """
        return {
            'wizard_id': wizard.id,
            'type': 'from',
            'task_count': stage['count'],
            'stage_id': stage['id'],
        }

    def _prepare_possible_stage(self, wizard, state):
        """
        Prepare data for creating a possible stage in the mapping wizard.
        """
        return {
            'wizard_id': wizard.id,
            'type': 'to',
            'stage_id': state.stage_id.id,
        }

    def _prepare_wizard_line(self, wizard, from_state):
        """
        Prepare data for creating a wizard line in the mapping wizard.
        """
        return {
            'wizard_id': wizard.id,
            'from_id': from_state.id,
        }

    def _get_wizard_action(self, wizard):
        """
        Get the action to open the mapping wizard.
        """
        action = self.env['ir.actions.act_window'].for_xml_id(
            'project_workflow_management',
            'project_workspace_mapping_wizard_action')
        action['res_id'] = wizard.id
        return action
