import logging

from floto.specs.task import Task
import floto.specs.retry_strategy

logger = logging.getLogger(__name__)

class LambdaFunction(Task):
    def __init__(self, *, domain, name, id_=None, requires=None, input=None, retry_strategy=None):
        # TODO docstring
        super().__init__(requires=requires)
        
        if retry_strategy and not isinstance(retry_strategy, floto.specs.retry_strategy.Strategy):
            raise ValueError('Retry strategy must be of type floto.specs.retry_strategy.Strategy')

        self.domain = domain
        self.name = name
        self.input = input
        # TODO fix version
        self.id_ = id_ or self._default_id(domain=domain, name=name, version=None, input=input)
        self.retry_strategy = retry_strategy

    def serializable(self):
        cpy = super().serializable()

        retry_strategy = cpy.get('retry_strategy')
        if retry_strategy:
            cpy['retry_strategy'] = retry_strategy.serializable()

        logger.debug('serialized LambdaFunction: {}'.format(cpy))
        return cpy

    @classmethod
    def deserialized(cls, **kwargs):
        cpy = floto.specs.serializer.copy_dict(kwargs, ['type'])

        if cpy.get('retry_strategy'):
            rs = floto.specs.serializer.get_class(cpy['retry_strategy']['type'])
            cpy['retry_strategy'] = rs.deserialized(**cpy['retry_strategy'])

        logger.debug('Deserialize LambdaFunction with: {}'.format(cpy))
        return cls(**cpy)

