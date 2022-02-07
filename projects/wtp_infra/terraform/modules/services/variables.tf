variable "wtp_route_53_zone_id" {
  type = string
  description = "Id for the primary wtp Route 53 hosted zone"
}

variable "wtp_cert_arn" {
  type = string
  description = "ARN for the wtp SSL cert"
}