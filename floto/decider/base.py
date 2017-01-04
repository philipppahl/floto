import logging
import multiprocessing
import socket

import floto.api

logger = logging.getLogger(__name__)


class Base:
    def __init__(self, swf=None, identity=None):
        """Base class for deciders.
        Parameters
        ----------
        swf: floto.api.Swf
            The SWF client, if swf is None an instance is created
        """
        self.task_token = None
        self.last_response = None
        self.history = None
        self.decisions = []
        self.run_id = None
        self.workflow_id = None
        self.domain = None
        self.identity = identity or socket.getfqdn(socket.gethostname())

        self.swf = swf or floto.api.Swf()
        self.task_list = None

        self.terminate_workflow = False
        self.terminate_decider = False

        self._separate_process = None

    def complete(self):
        logger.debug('Base.complete...')
        decisions = [d.get_decision() for d in self.decisions]
        
        try:
            self.swf.client.respond_decision_task_completed(taskToken=self.task_token,
                                                            decisions=decisions)
        except Exception as e:
            self.terminate_workflow = False
            logger.warning(e)

        self.decisions = []
        if self.terminate_workflow:
            self.tear_down()

    def tear_down(self):
        """Tear down method to be overridden by child class."""
        pass

    def poll_for_decision(self):
        """Polls for decision tasks. If a new decision task has been scheduled, the response, 
        history and task token are stored in the corresponding instance variables."""
        self.last_response = self.swf.poll_for_decision_task_page(domain=self.domain,
                                                                  task_list=self.task_list,
                                                                  identity=self.identity)
        if 'taskToken' in self.last_response:
            self.task_token = self.last_response['taskToken']
            # RF_PP make history a global Singleton?
            self.history = floto.History(domain=self.domain, task_list=self.task_list,
                                         response=self.last_response)
            self.run_id = self.last_response['workflowExecution']['runId']
            self.workflow_id = self.last_response['workflowExecution']['workflowId']
            logger.debug('Found task token')
        else:
            self.history = None
            self.task_token = None

    def get_decisions(self):
        """This method must be implemented by child classes to fill self.decisions"""
        raise NotImplementedError

    def run(self, separate_process=False):
        logger.debug('running decider')
        if separate_process:
            self._separate_process = multiprocessing.Process(target=self._run)
            self._separate_process.start()
        else:
            self._run()

    def _run(self):
        while not self.terminate_decider:
            self.poll_for_decision()
            if self.task_token:
                self.get_decisions()
                self.complete()

    def get_workflow_execution_description(self):
        return self.swf.describe_workflow_execution(self.domain, self.workflow_id, self.run_id)
