import json
import logging

import boto3
import botocore.exceptions
from botocore.client import Config

import floto.api
import floto.specs

logger = logging.getLogger(__name__)


class Swf(object):
    def __init__(self, region_name=None, profile_name=None):
        self.init_client(region_name, profile_name)
        self.domains = floto.api.Domains(self)
        self.default_maximum_page_size = 400

    def init_client(self, region_name=None, profile_name=None):

        params = {'region_name': None,
                  'profile_name': None}

        if region_name:
            params['region_name'] = region_name

        if profile_name:
            params['profile_name'] = profile_name

        session_parameter = {k: v for k, v in params.items() if v}
        self._client = self.open_session(session_parameter)

    @property
    def client(self):
        return self._client

    def open_session(self, session_parameter):
        config = Config(connect_timeout=50, read_timeout=70)
        session = boto3.session.Session(**session_parameter)
        return session.client('swf', config=config)

    def poll_for_decision_task_page(self, domain=None, task_list=None, page_token=None,
                                    page_size=None, identity=None):

        if (not domain) or (not task_list):
            raise ValueError('poll_for_decision needs domain and task list.')

        args = {'domain': domain,
                'taskList': {'name': task_list},
                'reverseOrder': True
                }
        if page_token:
            args['nextPageToken'] = page_token
        if identity:
            args['identity'] = identity

        args['maximumPageSize'] = page_size if page_size else self.default_maximum_page_size

        return self.client.poll_for_decision_task(**args)

    def poll_for_activity_task(self, domain, task_list, identity='NA'):
        args = {'domain': domain,
                'taskList': {'name': task_list},
                'identity': identity}
        return self.client.poll_for_activity_task(**args)

    def register_activity_type(self, swf_type):
        self.register_type(swf_type)

    def register_workflow_type(self, swf_type):
        self.register_type(swf_type)

    def register_type(self, swf_type):
        p = swf_type.swf_attributes
        try:
            if isinstance(swf_type, floto.api.ActivityType):
                self.client.register_activity_type(**p)
            elif isinstance(swf_type, floto.api.WorkflowType):
                self.client.register_workflow_type(**p)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'TypeAlreadyExistsFault':
                message = 'Failed to register already existing type {0}.'.format(swf_type.name)
                logger.warning(message)
            else:
                logger.error(e)

    # TODO Test lambda role
    def start_workflow_execution(self, *, domain, workflow_type_name, workflow_type_version,
                                 workflow_id=None, task_list=None, input=None,
                                 decision_task_start_to_close_timeout=None, lambda_role=None):
        """Start the workflow execution

        Parameters
        ----------
        domain: str
            The swf domain
        workflow_type_name: str
            Name of the registered workflow type
        workflow_type_version: str
            Version of the registered workflow type
        workflow_id: Optional[str]
            The workflow id. Defaults to: <workflow_type_name>_<workflow_type_version>
        task_list: Optional[str]
            Name of the task list. If not given, the default task list specified in the workflow
            type is used.
        input: Optional[object]
           Optional input, will be converted to json
        decision_task_start_to_close_timeout : Optional[str, int]
            The maximum duration of decision tasks for this workflow execution, in seconds.
            This parameter overrides the defaultTaskStartToCloseTimeout specified when registering
            the workflow type using RegisterWorkflowType .
        lambda_role : Optional[str]
            IAM role which provides access to Lambda from floto. 
        """

        workflow_id = workflow_id or (workflow_type_name + '_' + workflow_type_version)
        args = {'domain': domain,
                'workflowId': workflow_id,
                'workflowType': {'name': workflow_type_name, 'version': workflow_type_version}}
        if task_list:
            args['taskList'] = {'name': task_list}

        if input:
            args['input'] = floto.specs.JSONEncoder.dump_object(input)

        if decision_task_start_to_close_timeout:
            args['taskStartToCloseTimeout'] = str(decision_task_start_to_close_timeout)

        if lambda_role:
            args['lambdaRole'] = lambda_role

        return self.client.start_workflow_execution(**args)

    def signal_workflow_execution(self, domain, workflow_id, signal_name, input=None, run_id=None):
        args = {'domain': domain,
                'workflowId': workflow_id,
                'signalName': signal_name}
        if input:
            if isinstance(input, str):
                args['input'] = input
            else:
                args['input'] = json.dumps(input, cls=floto.specs.JSONEncoder)

        if run_id:
            args['runId'] = run_id

        self.client.signal_workflow_execution(**args)

    def terminate_workflow_execution(self, domain=None, workflow_id=None, run_id=None):
        if not domain or not workflow_id:
            message = 'terminate_workflow_execution(): domain and workflow_id are required'
            raise ValueError(message)
        args = {'domain': domain,
                'workflowId': workflow_id}
        if run_id:
            args['runId'] = run_id
        self.client.terminate_workflow_execution(**args)

    def describe_workflow_execution(self, domain, workflow_id, run_id):
        args = {'domain': domain,
                'execution': {'workflowId': workflow_id,
                              'runId': run_id}}
        return self.client.describe_workflow_execution(**args)

    def get_workflow_execution_history(self, domain, run_id, workflow_id):
        args = {'domain': domain,
                'execution': {'runId': run_id,
                              'workflowId': workflow_id},
                'reverseOrder': True}
        return self.client.get_workflow_execution_history(**args)

    def record_activity_task_heartbeat(self, task_token, details):
        """
        Parameters
        ----------
        task_token: str
        details: str
        """
        args = {'taskToken': task_token}
        if details: args['details'] = details
        self.client.record_activity_task_heartbeat(**args)
