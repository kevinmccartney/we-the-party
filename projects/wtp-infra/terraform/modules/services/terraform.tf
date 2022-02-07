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

  tags = {
    "project"    = "we-the-party",
    "managed_by" = "terraform"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id = aws_apigatewayv2_api.services.id
  name   = "$default"
  auto_deploy = true
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