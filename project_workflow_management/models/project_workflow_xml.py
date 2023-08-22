import os
import logging

from lxml import etree
from lxml.builder import ElementMaker

from odoo import models, tools, exceptions, _

_logger = logging.getLogger(__name__)


class XmlWorkflowReader(models.AbstractModel):
    _name = 'project.workflow.xml.reader'
    _description = 'Xml Workflow Reader'

    _rng_namespace = 'http://relaxng.org/ns/structure/1.0'
    _rng_namespace_map = {'rng': 'http://relaxng.org/ns/structure/1.0'}

    def get_element_maker(self):
        return ElementMaker(
            namespace=self._rng_namespace,
            nsmap=self._rng_namespace_map,
        )

    def validate_schema(self, xml):
        """
        Validate given XML against the RelaxNG validation schema.
        Raise ValidationError if XML is invalid.
        """
        validator = self.create_validator()
        if not validator.validate(xml):
            errors = []
            for error in validator.error_log:
                error = tools.ustr(error)
                _logger.error(error)
                errors.append(error)
            raise exceptions.ValidationError(
                _("Workflow File Validation Error: %s" % ",".join(errors))
            )

    def create_validator(self):
        """
        Instantiate the RelaxNG schema validator.
        """
        rng_file = tools.file_open(self.get_rng_file_path())
        try:
            rng = etree.parse(rng_file)
            rng = self.extend_rng(rng)
            return etree.RelaxNG(rng)
        except Exception:
            raise
        finally:
            rng_file.close()

    def extend_rng(self, rng_etree):
        """
        Hook to modify the RNG schema for extension purposes.
        """
        return rng_etree

    def get_rng_file_path(self):
        """
        Get the path to the RelaxNG schema file.
        """
        return os.path.join('project_workflow_management', 'rng', 'workflow.rng')

    def wkf_read(self, stream):
        """
        Read workflow data from the given XML stream.
        """
        workflow_tree = etree.parse(stream)
        self.validate_schema(workflow_tree)

        workflow_xml = workflow_tree.getroot()

        workflow = self.read_workflow(workflow_xml)
        self.validate_workflow(workflow)

        return workflow

    def read_workflow(self, workflow_xml):
        """
        Parse the workflow XML data and return the workflow information.
        This method should be implemented in the inheriting classes.
        """
        raise NotImplementedError("read_workflow method must be implemented in inheriting classes")

    def validate_workflow(self, workflow):
        """
        Validate the parsed workflow data.
        This method should be implemented in the inheriting classes.
        """
        raise NotImplementedError("validate_workflow method must be implemented in inheriting classes")

    def validate_workflow(self, workflow):
        """
        Validate the logic of the given workflow object.
        Check if all source and destination states referenced
        in the transition element can be found within defined workflow states.
        """
        states = {state['name']: state for state in workflow['states']}

        if len(states) != len(workflow['states']):
            raise exceptions.ValidationError(
                _("You have defined one or more states with the same name!")
            )

        missing_states = {transition[state] for transition in workflow['transitions'] for state in ['src', 'dst'] if
                          transition[state] not in states}

        if missing_states:
            raise exceptions.ValidationError(
                _("Following state(s) are referenced in the transitions but cannot be found: [%s]") % ",".join(
                    missing_states)
            )

        if not workflow.get('default_state', False):
            raise exceptions.ValidationError(_("Workflow default state is missing!"))

    def read_workflow(self, element):
        """
        Read workflow data from the given xml element.
        """
        return {
            'name': self.read_string(element, 'name'),
            'description': self.read_string(element, 'description'),
            'states': [self.read_state(e) for e in element.iterfind('states/state')],
            'transitions': [self.read_transition(e) for e in element.iterfind('transitions/transition')],
            'default_state': self.read_string(element, 'default-state')
        }

    def read_state(self, element):
        """
        Read workflow state data from the given xml element.
        """
        return {
            'name': self.read_string(element, 'name'),
            'type': self.read_string(element, 'type', 'in_progress'),
            'description': self.read_string(element, 'description'),
            'xpos': self.read_integer(element, 'xpos', -1),
            'ypos': self.read_integer(element, 'ypos', -1),
            'sequence': self.read_integer(element, 'sequence', default_value=1),
            'kanban_sequence': self.read_integer(element, 'kanban_sequence', default_value=10)
        }

    def read_transition(self, element):
        """
        Read project.workflow.transition data from the given xml element.
        """
        return {
            'name': self.read_string(element, 'name'),
            'description': self.read_string(element, 'description'),
            'src': self.read_string(element, 'src'),
            'dst': self.read_string(element, 'dst'),
            'confirmation': self.read_string(element, 'confirmation'),
            'kanban_color': self.read_string(element, 'kanban-color', default_value='1')
        }

    def read_string(self, element, attribute_name, default_value=''):
        """
        Read attribute of type string from the given xml element.
        """
        return self.read_attribute(element, attribute_name, default_value)

    def read_integer(self, element, attribute_name, default_value=0):
        """
        Reads an attribute of type ``integer`` from the given XML element.
        :param element: The XML element from which the attribute value is read.
        :param attribute_name: The name of the XML attribute.
        :param default_value: The default value in case
        the attribute is not present within the XML element.
        :return: Returns the attribute value of type ``integer``.
        """
        return int(self.read_attribute(element, attribute_name, default_value))

    def read_boolean(self, element, attribute_name, default_value=False):
        """
        Reads an attribute of type ``boolean`` from the given XML element.
        :param element: The XML element from which the attribute value is read.
        :param attribute_name: The name of the XML attribute.
        :param default_value: The default value in case
        the attribute is not present within the XML element.
        :return: Returns the attribute value of type ``boolean``.
        """
        return bool(self.read_attribute(element, attribute_name, default_value))

    def read_attribute(self, element, name, default_value=None):
        """
        Reads an attribute value of the given ``name`` from the given XML element.
        :param element: The XML element from which the attribute value is read.
        :param name: The name of the attribute.
        :param default_value: The default value in case
        the attribute is not present within the XML element.
        :return: Returns the attribute value or the default value.
        """
        return element.attrib.get(name, default_value)


DEFAULT_ENCODING = 'utf-8'


class XmlWorkflowWriter(models.AbstractModel):
    _name = 'project.workflow.xml.writer'

    def wkf_write(self, workflow, stream, encoding=DEFAULT_ENCODING):
        """
        Converts the given ``workflow`` object to XML and then
        writes it to the given ``stream`` object.
        :param workflow: The ``project.workflow`` browse object
        to be written to the given stream object.
        :param stream: This object represents any data stream object
         but it must have a write method.
        :return: None
        """
        str_data = self.to_string(workflow, encoding)
        if encoding != "unicode":
            str_data = str_data.decode(encoding)
        stream.write(str_data)

    def to_string(self, workflow, encoding=DEFAULT_ENCODING):
        """
        Gets an XML string representation of the given ``workflow`` object.
        :param workflow: The ``project.workflow`` browse object
        to be converted to an XML string.
        :return: Returns the XML string representation
        of the given ``workflow`` object.
        """
        return etree.tostring(
            self._build_xml(workflow, element_tree=True),
            encoding=encoding,
            pretty_print=True
        )

    def _build_xml(self, workflow, element_tree=False):
        """
        Builds xml out of given ``workflow`` object.
        :param workflow: The ``project.workflow`` browse object.
        :param element_tree: Boolean indicating whether to wrap
        root element into ``ElementTree`` or not.
        :return: Returns workflow xml as a root element or as an element tree.
        """
        root = self.create_workflow_element(workflow)

        states = self.create_states_element(root, workflow)
        for state in workflow.state_ids:
            self.create_state_element(states, state)

        transitions = self.create_transitions_element(root, workflow)
        for transition in workflow.transition_ids:
            self.create_transition_element(transitions, transition)

        if element_tree:
            return etree.ElementTree(root)
        else:
            return root

    def create_workflow_element(self, workflow):
        """
        This method creates root workflow xml element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new root workflow xml element.
        """
        attributes = self.prepare_workflow_attributes(workflow)
        return etree.Element('project-workflow', attributes)

    def prepare_workflow_attributes(self, workflow):
        """
        This method prepares attribute values for a workflow element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {
            'name': workflow.name,
            'description': workflow.description or "",
            'default-state': workflow.default_state_id.name
        }

    def create_states_element(self, parent, workflow):
        """
        This method creates state xml element.
        :param parent: The parent element of the new states element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new state xml element.
        """
        attributes = self.prepare_states_attributes(workflow)
        return etree.SubElement(parent, 'states', **attributes)

    def prepare_states_attributes(self, workflow):
        """
        This method prepares attribute values for a ``states`` element.
        At the moment, this method does nothing, but it's added here
        for possible future usage.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {}

    def create_state_element(self, parent, state):
        """
        This method creates state xml element.
        :param parent: The parent element of the new state element.
        :param state: The ``project.workflow.state`` browse object.
        :return: Returns a new state xml element.
        """
        attributes = self.prepare_state_attributes(state)
        return etree.SubElement(parent, 'state', **attributes)

    def prepare_state_attributes(self, state):
        """
        This method prepares attribute values for a state element.
        :param state: The ``project.workflow.state`` browse object.
        :return: Returns dictionary with attribute values.
        """
        values = {
            'name': state.stage_id.name,
            'type': state.type,
            'xpos': str(state.xpos),
            'ypos': str(state.ypos),
            'sequence': str(state.sequence),
            'kanban_sequence': str(state.kanban_sequence),
        }

        if state.stage_id.description:
            values['description'] = state.description

        return values

    def create_transitions_element(self, parent, workflow):
        """
        This method creates transition xml element.
        :param parent: The parent element of the new transition element.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns a new transition xml element.
        """
        attributes = self.prepare_transitions_attributes(workflow)
        return etree.SubElement(parent, 'transitions', **attributes)

    def prepare_transitions_attributes(self, workflow):
        """
        This method prepares attribute values for a ``transitions`` element.
        At the moment, this method does nothing, but it's added here
        for possible future usage.
        :param workflow: The ``project.workflow`` browse object.
        :return: Returns dictionary with attribute values.
        """
        return {}

    def create_transition_element(self, parent, transition):
        """
        This method creates transition xml element.
        :param parent: The parent element of the new transition element.
        :param transition: The ``project.workflow.transition`` browse object.
        :return: Returns a new transition xml element.
        """
        attributes = self.prepare_transition_attributes(transition)
        return etree.SubElement(parent, 'transition', **attributes)

    def prepare_transition_attributes(self, transition):
        """
        This method prepares attribute values for a transition element.
        :param transition: The ``project.workflow.transition`` browse object.
        :return: Returns dictionary with attribute values.
        """
        values = {
            'name': transition.name,
            'src': transition.src_id.stage_id.name,
            'dst': transition.dst_id.stage_id.name,
            'confirmation': str(transition.user_confirmation or False),
        }

        if transition.description:
            values['description'] = transition.description

        return values
