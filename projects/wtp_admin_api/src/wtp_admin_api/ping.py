import typing

from aws_lambda_powertools.utilities.typing import LambdaContext


def lambda_handler(event: dict, context: LambdaContext):
    print(f"event - {event}")
    print(f"context - {context}")

    return {"statusCode": 200, "body": "pong"}


if __name__ == "__main__":
    lambda_handler({}, typing.cast(LambdaContext, {}))
