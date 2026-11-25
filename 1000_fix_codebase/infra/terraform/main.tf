# Regional primary platform for 1000fix-erp (D-013 Option B):
#   VPC -> DOKS cluster (infra/k3s overlays deploy onto it)
#       -> managed PostgreSQL (odoo / keycloak / telemetry databases + roles)
#       -> managed Valkey (Redis protocol: event-bus dual write, caches)
#       -> optional managed Kafka (off by default - see variables.tf)
#       -> Spaces bucket (attachments / backups), container registry.
# The Bangladesh Zone 4 replica (`postgres-resident`) and the residency
# replication daemon are NOT here: they run on Bangladesh-resident
# infrastructure outside DigitalOcean (README "What remains external").

locals {
  tags = concat(["fix-erp", "env-prod"], var.tags)
}

resource "digitalocean_vpc" "main" {
  name        = "${var.name}-vpc"
  region      = var.region
  ip_range    = var.vpc_ip_range
  description = "1000fix-erp production private network"
}

# ------------------------------------------------------------------ Kubernetes
data "digitalocean_kubernetes_versions" "this" {
  version_prefix = var.kubernetes_version_prefix
}

resource "digitalocean_kubernetes_cluster" "main" {
  name          = "${var.name}-k8s"
  region        = var.region
  version       = data.digitalocean_kubernetes_versions.this.latest_version
  vpc_uuid      = digitalocean_vpc.main.id
  ha            = true
  auto_upgrade  = true
  surge_upgrade = true
  tags          = local.tags

  maintenance_policy {
    day        = "sunday"
    start_time = "20:00"
  }

  node_pool {
    name       = "${var.name}-pool"
    size       = var.node_size
    auto_scale = true
    min_nodes  = var.node_min
    max_nodes  = var.node_max
    tags       = local.tags
  }
}

# ------------------------------------------------------------------ PostgreSQL
resource "digitalocean_database_cluster" "postgres" {
  name                 = "${var.name}-pg"
  engine               = "pg"
  version              = var.postgres_version
  size                 = var.postgres_size
  region               = var.region
  node_count           = var.postgres_node_count
  private_network_uuid = digitalocean_vpc.main.id
  tags                 = local.tags

  maintenance_window {
    day  = "sunday"
    hour = "21:00:00"
  }
}

resource "digitalocean_database_db" "odoo" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = var.odoo_database
}

resource "digitalocean_database_db" "keycloak" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "keycloak"
}

resource "digitalocean_database_db" "telemetry" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "fix_telemetry"
}

# One least-privilege role per application; DigitalOcean generates the
# passwords (exported as sensitive outputs -> Kubernetes Secrets).
resource "digitalocean_database_user" "odoo" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "odoo"
}

resource "digitalocean_database_user" "keycloak" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "keycloak"
}

resource "digitalocean_database_user" "telemetry" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "telemetry"
}

# Only the Kubernetes cluster may connect.
resource "digitalocean_database_firewall" "postgres" {
  cluster_id = digitalocean_database_cluster.postgres.id

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }
}

# ---------------------------------------------------------------------- Valkey
resource "digitalocean_database_cluster" "valkey" {
  name                 = "${var.name}-valkey"
  engine               = "valkey"
  version              = var.valkey_version
  size                 = var.valkey_size
  region               = var.region
  node_count           = 1
  private_network_uuid = digitalocean_vpc.main.id
  tags                 = local.tags
}

resource "digitalocean_database_firewall" "valkey" {
  cluster_id = digitalocean_database_cluster.valkey.id

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }
}

# ----------------------------------------------------------------------- Kafka
resource "digitalocean_database_cluster" "kafka" {
  count = var.create_managed_kafka ? 1 : 0

  name                 = "${var.name}-kafka"
  engine               = "kafka"
  version              = var.kafka_version
  size                 = var.kafka_size
  region               = var.region
  node_count           = 3
  private_network_uuid = digitalocean_vpc.main.id
  tags                 = local.tags
}

resource "digitalocean_database_firewall" "kafka" {
  count = var.create_managed_kafka ? 1 : 0

  cluster_id = digitalocean_database_cluster.kafka[0].id

  rule {
    type  = "k8s"
    value = digitalocean_kubernetes_cluster.main.id
  }
}

# -------------------------------------------------------------- Object storage
resource "digitalocean_spaces_bucket" "objects" {
  name   = var.bucket_name
  region = var.spaces_region
  acl    = "private"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    id      = "expire-noncurrent-versions"
    enabled = true

    noncurrent_version_expiration {
      days = 90
    }
  }
}

# -------------------------------------------------------------------- Registry
resource "digitalocean_container_registry" "main" {
  count = var.create_registry ? 1 : 0

  name                   = var.registry_name
  subscription_tier_slug = "basic"
  region                 = var.region
}
