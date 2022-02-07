resource "aws_route53_zone" "domain_routes" {
  name = "wethe.party"
  tags = {
    "project" = "we-the-party",
    "managed_by" = "terraform"
  }
}

resource "aws_acm_certificate" "default" {
  domain_name               = var.domain_names["apex"]
  subject_alternative_names = [for name in var.domain_names : "*.${name}"]
  validation_method         = "DNS"
  options {
    certificate_transparency_logging_preference = "ENABLED"
  }

  lifecycle {
    create_before_destroy = true
  }

  tags                      = {
    "project" = "we-the-party",
    "managed_by" = "terraform"
  }
}

resource "aws_route53_record" "validation" {
  count = length(keys(var.domain_names))
  depends_on = [aws_acm_certificate.default]

  name    = trimprefix(aws_acm_certificate.default.domain_validation_options[count.index + 1].resource_record_name, "*.")
  type    = aws_acm_certificate.default.domain_validation_options[count.index + 1].resource_record_type
  zone_id = aws_route53_zone.domain_routes.zone_id
  records = [aws_acm_certificate.default.domain_validation_options[count.index + 1].resource_record_value]
  ttl     = "60"
  allow_overwrite = true
}

resource "aws_acm_certificate_validation" "default" {
  count = length(aws_route53_record.validation)

  certificate_arn         = aws_acm_certificate.default.arn
  
  validation_record_fqdns = [for validation in aws_route53_record.validation: validation.fqdn]
}