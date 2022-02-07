resource "aws_route53_record" "services_gateway" {
  name    = aws_apigatewayv2_domain_name.services.domain_name
  zone_id = var.wtp_route_53_zone_id
  type    = "A"

  alias {
    name                   = aws_apigatewayv2_domain_name.services.domain_name_configuration[0].target_domain_name
    zone_id                = aws_apigatewayv2_domain_name.services.domain_name_configuration[0].hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_apigatewayv2_domain_name" "services" {
  domain_name = "infra.wethe.party"

  domain_name_configuration {
    certificate_arn = var.wtp_cert_arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

resource "aws_apigatewayv2_api" "services" {
  name          = "wtp-services"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.services.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.default.arn
    format          = "$context.identity.sourceIp - - [$context.requestTime] \"$context.httpMethod $context.routeKey $context.protocol\" $context.status $context.responseLength $context.requestId $context.integrationErrorMessage"
  }
}

resource "aws_api_gateway_account" "cloudwatch" {
  cloudwatch_role_arn = aws_iam_role.cloudwatch.arn
}

resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "api_gateway_cloudwatch"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "cloudwatch" {
  name = "default"
  role = aws_iam_role.api_gateway_cloudwatch.id

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
EOF
}


resource "aws_cloudwatch_log_group" "default" {
  name = "wtp-services-gateway-access-log"
}

resource "aws_apigatewayv2_route" "ping" {
  api_id    = aws_apigatewayv2_api.services.id
  route_key = "GET /ping"

  target = "integrations/${aws_apigatewayv2_integration.ping.id}"
}

resource "aws_apigatewayv2_integration" "ping" {
  api_id           = aws_apigatewayv2_api.services.id
  integration_type = "AWS_PROXY"

  connection_type    = "INTERNET"
  description        = "Simple ping endpoint, returns pong"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.ping.invoke_arn
}

resource "aws_lambda_function" "ping" {
  function_name = "wtp-services_ping"
  role          = aws_iam_role.ping_lambda_execution.arn
  runtime       = "python3.9"
  filename      = "./assets/ping.zip"
  handler       = "ping.lambda_handler"
}


resource "aws_iam_role" "ping_lambda_execution" {
  name = "wtp-ping-lambda-execution"

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



# resource "aws_apigatewayv2_route" "initialize_feature" {
#   api_id    = aws_apigatewayv2_api.example.id
#   route_key = "POST /services/feature"

#   target = "integrations/${aws_apigatewayv2_integration.example.id}"
# }