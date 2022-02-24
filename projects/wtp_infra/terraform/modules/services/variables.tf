variable "wtp_route_53_zone_id" {
  type        = string
  description = "Id for the primary wtp Route 53 hosted zone"
}

variable "wtp_cert_arn" {
  type        = string
  description = "ARN for the wtp SSL cert"
}

variable "wtp_aws_region" {
  type        = string
  description = "AWS region for the API gateway"
}

variable "wtp_aws_account_id" {
  type        = string
  description = "The AWS account in which our serverless resources reside"
  sensitive   = true
}