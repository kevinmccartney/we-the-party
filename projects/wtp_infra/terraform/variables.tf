variable "wtp_aws_region" {
  type        = string
  description = "The AWS region in which our serverless resources reside"
}

variable "wtp_aws_account_id" {
  type        = string
  description = "The AWS account in which our serverless resources reside"
  sensitive = true
}