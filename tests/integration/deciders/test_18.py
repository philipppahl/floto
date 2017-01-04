import uuid
from test_helper import get_result

import floto.specs.task
from floto.specs import DeciderSpec

def test_18():
    domain = 'floto_test'
    lambda_function = floto.specs.task.LambdaFunction(domain=domain, name='floto_test_function')
    decider_spec = DeciderSpec(domain=domain,
                               task_list=str(uuid.uuid4()),
                               activity_tasks=[lambda_function],
                               terminate_decider_after_completion=True)

    decider = floto.decider.Decider(decider_spec=decider_spec)

    swf = floto.api.Swf()
    workflow_args = {'domain':'floto_test', 
            'workflow_type_name':'test_workflow',
            'workflow_type_version':'v1',
            'task_list':decider_spec.task_list,
            # 'lambda_role':'arn:aws:iam::aws:policy/service-role/AWSLambdaRole'}
            # 'lambda_role':'arn:aws:iam::130141755138:role/swf-lambda'}
            'lambda_role':'arn:aws:iam::130141755138:role/swf-lambda'}

    response = swf.start_workflow_execution(**workflow_args)

    run_id = response['runId']
    workflow_id = 'test_workflow_v1'

    print(30*'-'+' Running Test 18 '+30*'-')
    decider.run()
    print(30*'-'+' Done Test 18    '+30*'-')
    return get_result('floto_test', run_id, workflow_id)    
    

