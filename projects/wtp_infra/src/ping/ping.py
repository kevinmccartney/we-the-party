import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def response(status=200, headers={"Content-Type": "application/json"}, body=""):
    """
    http://www.awslessons.com/2017/lambda-api-gateway-internal-server-error/
    """
    if not body:
        return {"statusCode": status}

    return {"statusCode": status, "headers": headers, "body": json.dumps(body)}


def log_event(event, context):
    logger.info("Event -")
    logger.info(json.dumps(event, indent=4, sort_keys=True))

    logger.info("Context -")
    logger.info(
        json.dumps(
            {
                "function_name": context.function_name,
                "function_version": context.function_version,
                "invoked_function_arn": context.invoked_function_arn,
                "memory_limit_in_mb": context.memory_limit_in_mb,
                "aws_request_id": context.aws_request_id,
            },
            indent=4,
            sort_keys=True,
        )
    )


def lambda_handler(event, context):
    log_event(event, context)

    return response(status=200, body={"message": "pong"})


if __name__ == "__main__":
    pass
