# 1000fix-erp production platform on DigitalOcean (regional primary, D-013
# Option B). See infra/README-production.md for the full deploy sequence.
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = ">= 2.55.0, < 3.0.0"
    }
  }

  # State holds generated database passwords: keep it in an encrypted, access-
  # controlled remote backend - never in git. Example (DigitalOcean Spaces,
  # S3-compatible; credentials via AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY):
  #
  # backend "s3" {
  #   endpoints                   = { s3 = "https://sgp1.digitaloceanspaces.com" }
  #   bucket                      = "<state-bucket>"
  #   key                         = "fix-erp/production.tfstate"
  #   region                      = "us-east-1"
  #   skip_credentials_validation = true
  #   skip_requesting_account_id  = true
  #   skip_metadata_api_check     = true
  #   skip_region_validation      = true
  #   skip_s3_checksum            = true
  # }
}
