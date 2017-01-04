import floto


swf = floto.api.Swf()

domain = 'floto_test'
swf.domains.register_domain('floto_test')

# Workflow types
test_workflow = floto.api.WorkflowType(domain=domain, 
                                       name='test_workflow', 
                                       version='v1', 
                                       default_task_start_to_close_timeout='20')


my_workflow_v1 = floto.api.WorkflowType(domain=domain, 
                                       name='my_workflow_type', 
                                       version='v1', 
                                       default_task_start_to_close_timeout='20')

swf.register_workflow_type(test_workflow)
swf.register_workflow_type(my_workflow_v1)

# Activity types
activity1_v5 = floto.api.ActivityType(name='activity1', version='v5', domain=domain,
                                      default_task_heartbeat_timeout='10')

swf.register_activity_type(activity1_v5)
