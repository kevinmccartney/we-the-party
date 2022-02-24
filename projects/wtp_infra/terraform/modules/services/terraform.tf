resource "aws_api_gateway_rest_api" "services" {
  name = "wtp-service"
  # disable_execute_api_endpoint = true
}

resource "aws_api_gateway_domain_name" "services" {
  certificate_arn = var.wtp_cert_arn
  domain_name     = "infra.wethe.party"
}

resource "aws_api_gateway_base_path_mapping" "example" {
  api_id      = aws_api_gateway_rest_api.services.id
  stage_name  = aws_api_gateway_stage.v1.stage_name
  domain_name = aws_api_gateway_domain_name.services.domain_name
}

resource "aws_route53_record" "services" {
  name    = aws_api_gateway_domain_name.services.domain_name
  type    = "A"
  zone_id = var.wtp_route_53_zone_id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.services.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.services.cloudfront_zone_id
  }
}

resource "aws_api_gateway_deployment" "services" {
  rest_api_id = aws_api_gateway_rest_api.services.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.services))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_resource" "ping" {
  rest_api_id = aws_api_gateway_rest_api.services.id
  parent_id   = aws_api_gateway_rest_api.services.root_resource_id
  path_part   = "ping"
}

resource "aws_api_gateway_method" "ping_get" {
  rest_api_id   = aws_api_gateway_rest_api.services.id
  resource_id   = aws_api_gateway_resource.ping.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "ping_get" {
  rest_api_id             = aws_api_gateway_rest_api.services.id
  resource_id             = aws_api_gateway_resource.ping.id
  http_method             = aws_api_gateway_method.ping_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = sensitive(aws_lambda_function.ping.invoke_arn)
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.services.id
  rest_api_id   = aws_api_gateway_rest_api.services.id
  stage_name    = "v1"
}

resource "aws_lambda_permission" "apigw_lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ping.function_name
  principal     = "apigateway.amazonaws.com"

  # More: http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-control-access-using-iam-policies-to-invoke-api.html
  source_arn = "arn:aws:execute-api:${var.wtp_aws_region}:${var.wtp_aws_account_id}:${aws_api_gateway_rest_api.services.id}/*/${aws_api_gateway_method.ping_get.http_method}${aws_api_gateway_resource.ping.path}"
}

resource "aws_iam_role" "lambda_execution" {
  name = "iam_for_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

data "aws_iam_policy" "AWSLambdaBasicExecutionRole" {
  name = "AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "aws-lambda-basic-execution-role" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = data.aws_iam_policy.AWSLambdaBasicExecutionRole.arn
}

resource "aws_lambda_function" "ping" {
  s3_bucket     = "wtp-infra-lambdas"
  s3_key        = "ping.zip"
  function_name = "wtp_services_ping"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "ping.lambda_handler"

  runtime = "python3.9"
}

resource "aws_s3_bucket" "infra_lambdas" {
  bucket = "wtp-infra-lambdas"
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}