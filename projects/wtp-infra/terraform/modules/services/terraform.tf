resource "aws_api_gateway_rest_api" "services" {
  name = "wtp-service"
}

resource "aws_api_gateway_domain_name" "services" {
  certificate_arn = var.wtp_cert_arn
  domain_name     = "infra.wethe.party"
  security_policy = "TLS_1_2"
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

resource "aws_api_gateway_deployment" "example" {
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
  rest_api_id          = aws_api_gateway_rest_api.services.id
  resource_id          = aws_api_gateway_resource.ping.id
  http_method          = aws_api_gateway_method.ping_get.http_method
  type                 = "MOCK"

  request_parameters = {
    "integration.request.header.X-Authorization" = "'static'"
  }

  # Transforms the incoming XML request to JSON
  request_templates = {
    "application/json" = "pong"
  }
}

resource "aws_api_gateway_method_response" "response_200" {
  rest_api_id = aws_api_gateway_rest_api.services.id
  resource_id = aws_api_gateway_resource.ping.id
  http_method = aws_api_gateway_method.ping_get.http_method
  status_code = "200"
}

# resource "aws_api_gateway_resource" "resources" {
#   rest_api_id = aws_api_gateway_rest_api.services.id
#   parent_id   = aws_api_gateway_rest_api.services.root_resource_id
#   path_part   = "services"
# }

# resource "aws_api_gateway_resource" "resources" {
#   rest_api_id = aws_api_gateway_rest_api.services.id
#   parent_id   = aws_api_gateway_resource.resources.id
#   path_part   = "features"
# }