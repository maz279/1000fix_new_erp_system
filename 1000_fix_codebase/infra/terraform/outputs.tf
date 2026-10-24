# Connection details for creating the Kubernetes Secrets listed in
# infra/README-production.md. Sensitive outputs print only with
# `terraform output -raw <name>`; never paste them into the repository.

output "vpc_id" {
  description = "Private VPC id."
  value       = digitalocean_vpc.main.id
}

output "vpc_ip_range" {
  description = "VPC CIDR (must equal the NetworkPolicy ipBlock CIDRs)."
  value       = digitalocean_vpc.main.ip_range
}

output "kubernetes_cluster_id" {
  description = "DOKS cluster id (doctl kubernetes cluster kubeconfig save <id>)."
  value       = digitalocean_kubernetes_cluster.main.id
}

output "kubernetes_endpoint" {
  description = "Kubernetes API endpoint."
  value       = digitalocean_kubernetes_cluster.main.endpoint
}

output "kubeconfig" {
  description = "Raw kubeconfig of the cluster (short-lived token)."
  value       = digitalocean_kubernetes_cluster.main.kube_config[0].raw_config
  sensitive   = true
}

output "postgres_private_host" {
  description = "Managed PostgreSQL private host (VPC)."
  value       = digitalocean_database_cluster.postgres.private_host
}

output "postgres_port" {
  description = "Managed PostgreSQL port (TLS required)."
  value       = digitalocean_database_cluster.postgres.port
}

output "odoo_database" {
  description = "Odoo database name."
  value       = digitalocean_database_db.odoo.name
}

output "odoo_db_password" {
  description = "Password of the `odoo` role -> Secret fix-db-odoo/password."
  value       = digitalocean_database_user.odoo.password
  sensitive   = true
}

output "keycloak_db_password" {
  description = "Password of the `keycloak` role -> Secret fix-db-keycloak/password."
  value       = digitalocean_database_user.keycloak.password
  sensitive   = true
}

output "keycloak_jdbc_url" {
  description = "JDBC URL for Keycloak -> Secret fix-db-keycloak/jdbc-url."
  value       = "jdbc:postgresql://${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.keycloak.name}?sslmode=require"
}

output "telemetry_database_url" {
  description = "DSN for telemetry-collector -> Secret fix-db-telemetry/database-url."
  value       = "postgres://${digitalocean_database_user.telemetry.name}:${urlencode(digitalocean_database_user.telemetry.password)}@${digitalocean_database_cluster.postgres.private_host}:${digitalocean_database_cluster.postgres.port}/${digitalocean_database_db.telemetry.name}?sslmode=require"
  sensitive   = true
}

output "valkey_private_uri" {
  description = "Valkey private URI (rediss://, TLS) -> Secret fix-redis/url."
  value       = digitalocean_database_cluster.valkey.private_uri
  sensitive   = true
}

output "kafka_private_host" {
  description = "Managed Kafka private host (null unless create_managed_kafka)."
  value       = try(digitalocean_database_cluster.kafka[0].private_host, null)
}

output "bucket_name" {
  description = "Spaces bucket for attachments / backups."
  value       = digitalocean_spaces_bucket.objects.name
}

output "bucket_endpoint" {
  description = "Spaces bucket endpoint."
  value       = digitalocean_spaces_bucket.objects.bucket_domain_name
}

output "registry_endpoint" {
  description = "Container registry endpoint (null when create_registry = false)."
  value       = try(digitalocean_container_registry.main[0].endpoint, null)
}
