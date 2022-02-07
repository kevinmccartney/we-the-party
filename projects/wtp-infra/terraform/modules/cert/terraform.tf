locals {
  wtp_sans = concat([for key, value in var.domain_names : "*.${value}" if key != "infra"], [for key, value in var.domain_names : value if key != "apex"])
}

resource "aws_route53_zone" "domain_routes" {
  name = "wethe.party"
}

resource "aws_acm_certificate" "default" {
  domain_name               = var.domain_names["apex"]
  subject_alternative_names = local.wtp_sans
  validation_method         = "DNS"
  options {
    certificate_transparency_logging_preference = "ENABLED"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_route53_record" "validation" {
  depends_on = [aws_acm_certificate.default]

  for_each = {
    for dvo in aws_acm_certificate.default.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }

  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = aws_route53_zone.domain_routes.zone_id
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "default" {
  count = length(aws_route53_record.validation)

  certificate_arn = aws_acm_certificate.default.arn

  validation_record_fqdns = [for validation in aws_route53_record.validation : validation.fqdn]
}

output "wtp_route_53_zone_id" {
  value       = aws_route53_zone.domain_routes.zone_id
  description = "Id for the primary wtp Route 53 hosted zone"
}

output "cert_arn" {
  value       = aws_acm_certificate.default.arn
  description = "ARN for the wtp SSL cert"
}