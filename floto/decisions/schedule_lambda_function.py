# TODO implement and test
class ScheduleLambdaFunction(Decision):
    def __init__(self):
        # TODO correct
        super().__init(required_fields=['decisionType',
                         'scheduleActivityTaskDecisionAttributes.id',
                         'scheduleActivityTaskDecisionAttributes.name'])

