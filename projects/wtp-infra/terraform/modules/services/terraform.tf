resource "aws_api_gateway_rest_api" "services" {
  name = "wtp-service"
  # disable_execute_api_endpoint = true
}

resource "aws_api_gateway_domain_name" "services" {
  certificate_arn = var.wtp_cert_arn
  domain_name     = "infra.wethe.party"
  security_policy = "TLS_1_2"
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

resource "aws_api_gateway_method_response" "ping_200" {
  # depends_on  = ["aws_api_gateway_method.api-method", "aws_api_gateway_integration.api-method-integration"]
  rest_api_id = aws_api_gateway_rest_api.services.id
  resource_id = aws_api_gateway_resource.ping.id
  http_method = "GET"
  status_code = "200"

  response_models = {
    "application/json" = "Empty"
  }

  # response_parameters = {
  #   "method.response.header.Access-Control-Allow-Headers" = true
  #   "method.response.header.Access-Control-Allow-Methods" = true
  #   "method.response.header.Access-Control-Allow-Origin"  = true
  # }
}

resource "aws_api_gateway_integration" "ping_get" {
  rest_api_id = aws_api_gateway_rest_api.services.id
  resource_id = aws_api_gateway_resource.ping.id
  http_method = aws_api_gateway_method.ping_get.http_method
  type        = "MOCK"

  # request_parameters = {
  #   "integration.request.header.X-Authorization" = "'static'"
  # }

  # Transforms the incoming XML request to JSON
  request_templates = {
    # "application/json" = "{\"statusCode\": 200, \"body\": \"pong\"}"
    "application/json" = <<TEMPLATE
{
  "statusCode": 200
}
TEMPLATE
  }
}

resource "aws_api_gateway_integration_response" "ping_200" {
  # depends_on  = ["aws_api_gateway_method_response.ok", "aws_api_gateway_method.api-method", "aws_api_gateway_integration.api-method-integration"]
  rest_api_id = aws_api_gateway_rest_api.services.id
  resource_id = aws_api_gateway_resource.ping.id
  http_method = "GET"
  status_code = "200"

  response_templates = {
    "application/json" = ""
  }

  # response_parameters = {
  #   "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  #   "method.response.header.Access-Control-Allow-Methods" = "'GET'"
  #   "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  # }
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.services.id
  rest_api_id   = aws_api_gateway_rest_api.services.id
  stage_name    = "v1"
}