import pytest
import floto.specs.task
import floto.specs.retry_strategy

@pytest.fixture
def function_arguments():
    rs = floto.specs.retry_strategy.InstantRetry(retries=3)
    args = {'domain':'swf_domain',
            'name':'function_name',
            'id_':'function_id',
            'requires':['function2', 'function3'],
            'input':{'foo':'bar'},
            'retry_strategy':rs}
    return args

@pytest.fixture
def function(function_arguments):
    return floto.specs.task.LambdaFunction(**function_arguments)

class TestLambdaFunction:
    def test_init(self):
        lf = floto.specs.task.LambdaFunction(domain='my_domain', name='my_name')
        assert lf.domain == 'my_domain'
        assert lf.name == 'my_name'

    def test_id(self, function):
        assert function.id_ == 'function_id'

    def test_requires(self, function):
        assert function.requires == ['function2', 'function3']

    def test_input(self, function):
        assert function.input == {'foo':'bar'} 

    def test_retry_strategy(self, function):
        assert isinstance(function.retry_strategy, floto.specs.retry_strategy.InstantRetry)
        assert function.retry_strategy.retries == 3

    def test_default_id(self, function_arguments):
        function_arguments.pop('id_')
        f = floto.specs.task.LambdaFunction(**function_arguments)
        assert f.id_ == f._default_id(domain=function_arguments['domain'],
                                      name=function_arguments['name'],
                                      input=function_arguments['input'],
                                      version=None)
        assert f.id_.split(':')[:2] == ['function_name','swf_domain']

    def test_serializable(self, function):
        s = function.serializable()
        assert s['type'] == 'floto.specs.task.LambdaFunction'
        assert isinstance(s['retry_strategy'], dict)

    def test_deserialize(self):
        s = {'domain': 'swf_domain', 
             'type': 'floto.specs.task.LambdaFunction', 
             'name': 'function_name', 
             'id_': 'function_id', 
             'input': {'foo': 'bar'}, 
             'requires': ['function2', 'function3'], 
             'retry_strategy': {'retries': 3, 
                                'type': 'floto.specs.retry_strategy.InstantRetry'}
             }
        f = floto.specs.task.LambdaFunction.deserialized(**s)
        assert f.name == 'function_name'
        assert isinstance(f.retry_strategy, floto.specs.retry_strategy.InstantRetry)
