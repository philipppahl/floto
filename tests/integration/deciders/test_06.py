import uuid

from test_helper import get_fail_workflow_execution

import floto
import floto.api
import floto.decider
from floto.specs import DeciderSpec
from floto.specs.task import ActivityTask


def test_06():
    domain = 'floto_test'
    rs = floto.specs.retry_strategy.InstantRetry(retries=2)
    activity_task = ActivityTask(domain=domain, name='activity_fails_2', version='v2', 
            retry_strategy=rs)
    decider_spec = DeciderSpec(domain=domain,
                               task_list=str(uuid.uuid4()),
                               activity_tasks=[activity_task],
                               default_activity_task_list='floto_activities',
                               terminate_decider_after_completion=True)

    decider = floto.decider.Decider(decider_spec=decider_spec)

    workflow_args = {'domain': decider_spec.domain,
                     'workflow_type_name': 'my_workflow_type',
                     'workflow_type_version': 'v1',
                     'task_list': decider_spec.task_list,
                     'input': {'foo': 'bar'}}

    response = floto.api.Swf().start_workflow_execution(**workflow_args)

    print(30 * '-' + ' Running Test 06 ' + 30 * '-')
    decider.run()
    print(30 * '-' + ' Done Test 06    ' + 30 * '-')
    return get_fail_workflow_execution(decider.domain, response['runId'], 'my_workflow_type_v1')
