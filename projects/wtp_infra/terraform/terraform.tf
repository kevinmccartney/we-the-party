terraform {
  backend "s3" {
    bucket = "wtp-state"
    key    = "infra.tfstate"
    region = "us-east-1"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

data "terraform_remote_state" "state" {
  backend = "s3"
  config = {
    bucket         = "wtp-state"
    dynamodb_table = "wtp-infra-state-locks"
    region         = var.wtp_aws_region
    key            = "infra.tfstate"
  }
}


provider "aws" {
  region = var.wtp_aws_region

  default_tags {
    tags = {
      "project"     = "we-the-party",
      "managed_by"  = "terraform"
      "environment" = "infra"
    }
  }
}

resource "aws_s3_bucket" "terraform_state" {
  bucket = "wtp-state"
  versioning {
    enabled = true
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

resource "aws_dynamodb_table" "terraform_locks" {
  name         = "wtp-infra-state-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

module "cert" {
  source = "./modules/cert"

  domain_names = tomap({
    "apex"  = "wethe.party",
    "api"   = "api.wethe.party",
    "admin" = "admin.wethe.party",
    "infra" = "infra.wethe.party"
  })
}

module "services" {
  source = "./modules/services"

  wtp_route_53_zone_id = module.cert.wtp_route_53_zone_id
  wtp_cert_arn         = module.cert.cert_arn
  wtp_aws_region       = var.wtp_aws_region
  wtp_aws_account_id   = var.wtp_aws_account_id

  depends_on = [
    module.cert
  ]
}
