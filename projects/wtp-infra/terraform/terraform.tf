terraform {
  backend "s3" {
    bucket = "wtp-state"
    key    = "infra-terraform.tfstate"
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
    bucket     = "wtp-state"
    lock_table = "wtp-infra-state-locks"
    region     = var.wtp_aws_region
    key        = "infra-terraform.tfstate"
  }
}


provider "aws" {
  region = var.wtp_aws_region
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
