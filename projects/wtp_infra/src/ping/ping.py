import json

def lambda_handler(event, context):
  print('Event -')
  # parsed_event = json.loads(event)
  print(json.dumps(event, indent=4, sort_keys=True))

  print('Context -')
  # parsed_context = json.loads(context)
  print(json.dumps({
    'function_name': context.function_name,
    'function_version': context.function_version,
    'invoked_function_arn': context.invoked_function_arn,
    'memory_limit_in_mb': context.memory_limit_in_mb,
    'aws_request_id': context.aws_request_id
  }, indent=4, sort_keys=True))
  
  return 'pong'