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

resource "aws_api_gateway_resource" "resources" {
  rest_api_id = aws_api_gateway_rest_api.services.id
  parent_id   = aws_api_gateway_rest_api.services.root_resource_id
  path_part   = "services"
}