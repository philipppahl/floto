import logging
from floto.decisions import Decision
import json

logger = logging.getLogger(__name__)

class ScheduleLambdaFunction(Decision):
    def __init__(self, **args):
        """
        Parameters
        id_: str [Required when decision is retrieved]
            id of the lambda function
        name: str [Required when decision is retrieved]
            Name of lambda function
        input: dict
        start_to_close_timeout: str
        """
        super().__init__(required_fields=['decisionType',
                                          'scheduleLambdaFunctionDecisionAttributes.id',
                                          'scheduleLambdaFunctionDecisionAttributes.name'])

        self.id_ = args.get('id_', None)
        self.name = args.get('name', None)
        self.input = args.get('input', None)
        self.start_to_close_timeout = args.get('start_to_close_timeout', None)

    def _get_decision(self):
        d = {'decisionType': 'ScheduleLambdaFunction',
             'scheduleLambdaFunctionDecisionAttributes': self.decision_attributes()
             }
        return d

    def decision_attributes(self):
        logger.debug('ScheduleLambdaFunction.decision_attributes...')
        # if not self.id_ or not self.name:
            # raise ValueError('id_ and name required to schedule lambda function.')

        attributes = {}
        attributes['id'] = self.id_
        attributes['name'] = self.name

        if self.input:
            attributes['input'] = json.dumps(self.input)

        if self.start_to_close_timeout:
            attributes['startToCloseTimeout'] = str(self.start_to_close_timeout) 

        return attributes
