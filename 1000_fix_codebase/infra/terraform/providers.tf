# No credential in code. The provider reads:
#   DIGITALOCEAN_TOKEN                               - API token
#   SPACES_ACCESS_KEY_ID / SPACES_SECRET_ACCESS_KEY  - Spaces (object storage) keys
# from the environment of the operator / CI runner.
provider "digitalocean" {}
