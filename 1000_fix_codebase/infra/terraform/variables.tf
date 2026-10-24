variable "name" {
  description = "Name prefix for every resource."
  type        = string
  default     = "fix-erp-prod"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.name))
    error_message = "name must be 3-31 chars of lowercase letters, digits and dashes."
  }
}

variable "region" {
  description = "DigitalOcean region of the regional primary (D-013 Option B: Singapore)."
  type        = string
  default     = "sgp1"
}

variable "vpc_ip_range" {
  description = "Private VPC range. Must match the ipBlock CIDRs in infra/k3s/base/networkpolicies.yaml."
  type        = string
  default     = "10.110.0.0/20"

  validation {
    condition     = can(cidrhost(var.vpc_ip_range, 0))
    error_message = "vpc_ip_range must be a valid CIDR block."
  }
}

variable "kubernetes_version_prefix" {
  description = "DOKS minor version to track, e.g. \"1.33.\" (the latest patch of it is used)."
  type        = string
  default     = "1.33."
}

variable "node_size" {
  description = "Droplet size of the Kubernetes worker pool."
  type        = string
  default     = "s-4vcpu-8gb"
}

variable "node_min" {
  description = "Minimum worker nodes (autoscaling)."
  type        = number
  default     = 3

  validation {
    condition     = var.node_min >= 2
    error_message = "node_min must be at least 2 (PodDisruptionBudgets assume >= 2 nodes)."
  }
}

variable "node_max" {
  description = "Maximum worker nodes (autoscaling)."
  type        = number
  default     = 6
}

variable "postgres_version" {
  description = "Managed PostgreSQL major version (the compose stack runs 17)."
  type        = string
  default     = "17"
}

variable "postgres_size" {
  description = "Managed PostgreSQL node size slug."
  type        = string
  default     = "db-s-4vcpu-8gb"
}

variable "postgres_node_count" {
  description = "Managed PostgreSQL nodes (1 primary + standbys); 2+ gives automatic failover."
  type        = number
  default     = 2
}

variable "odoo_database" {
  description = "Odoo database name (= ODOO_DB / NEXT_PUBLIC_ODOO_DB)."
  type        = string
  default     = "fix_production"
}

variable "valkey_version" {
  description = "Managed Valkey (Redis-protocol, BSD-licensed - see D-031) major version."
  type        = string
  default     = "8"
}

variable "valkey_size" {
  description = "Managed Valkey node size slug."
  type        = string
  default     = "db-s-1vcpu-2gb"
}

variable "create_managed_kafka" {
  # Default false: managed Kafka requires SASL/TLS, which the event-bus client
  # (libs/py/fix_events/kafka_backend.py) does not support yet - see
  # infra/README-production.md "Known gaps".
  description = "Create a DigitalOcean managed Kafka cluster (needs SASL/TLS support in fix_events first)."
  type        = bool
  default     = false
}

variable "kafka_version" {
  description = "Managed Kafka version (only used when create_managed_kafka = true)."
  type        = string
  default     = "3.8"
}

variable "kafka_size" {
  description = "Managed Kafka node size slug (only used when create_managed_kafka = true)."
  type        = string
  default     = "gd-2vcpu-8gb"
}

variable "spaces_region" {
  description = "Spaces (object storage) region for the attachments/backups bucket."
  type        = string
  default     = "sgp1"
}

variable "bucket_name" {
  description = "Globally unique Spaces bucket name for Odoo attachments and backups."
  type        = string
  default     = "fix-erp-prod-objects"
}

variable "registry_name" {
  description = "DigitalOcean Container Registry name (images: registry.digitalocean.com/<name>/...)."
  type        = string
  default     = "fix-erp"
}

variable "create_registry" {
  description = "Create the container registry (one per DigitalOcean account)."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Extra tags applied to every taggable resource."
  type        = list(string)
  default     = []
}
