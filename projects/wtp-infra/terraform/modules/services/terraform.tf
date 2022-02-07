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

resource "aws_api_gateway_rest_api" "services" {
  name = "wtp-service"
}