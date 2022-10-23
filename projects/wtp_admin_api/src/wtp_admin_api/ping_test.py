from ping import lambda_handler

import functools

def test_answer():
    assert lambda_handler({}, {}) == {"statusCode": 200, "body": "pong"}
