import logging
logger = logging.getLogger(__name__)

import pytest
import floto.decisions 

class TestScheduleLambdaFunction():
    def test_get_decision(self):
        d = floto.decisions.ScheduleLambdaFunction() 
        assert d

    def test_raises_required_field(self):
        d = floto.decisions.ScheduleLambdaFunction() 
        with pytest.raises(KeyError):
            d.get_decision()

    def test_init_with_parameters(self):
        args = {'id_':'lambda_id',
                'name':'lambda_name',
                'input':{'foo':'bar'},
                'start_to_close_timeout':60}
        d = floto.decisions.ScheduleLambdaFunction(**args).get_decision()
        attributes = d['scheduleLambdaFunctionDecisionAttributes']
        logger.debug(d)
        assert d['decisionType'] == 'ScheduleLambdaFunction'
        assert attributes['id'] == 'lambda_id'
        assert attributes['name'] == 'lambda_name'
        assert attributes['startToCloseTimeout'] == '60'


    


