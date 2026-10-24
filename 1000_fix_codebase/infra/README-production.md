# 1000fix-erp — Production deployment

Status: deployment **definition** complete and locally validated (2026-10-23).
Nothing here has been run against a real cloud account or a real cluster yet;
see [Validation performed](#validation-performed) for exactly what was
executed and [Known gaps](#known-gaps-do-not-paper-over) for what still
blocks a live cut-over.

## 1. Topology

```
Internet ──HTTPS──► edge (compose: Kong :443 │ k8s: Ingress ─► Kong)
                     │ host-based routing (infra/compose/kong/kong.prod.yml)
   api.<domain>      ├─► Odoo JSON-RPC portal API  (Odoo session / Odoo API key; /api/odoo: JWT)
                     ├─► /svc/ml        ml-gateway          (JWT)
                     ├─► /svc/telemetry telemetry-collector (JWT, /api/* only)
                     ├─► /svc/notifications dispatcher      (JWT, GET only)
   erp.<domain>      ├─► Odoo back office + /websocket (Odoo session auth)
   auth.<domain>     ├─► Keycloak /realms, /resources   (/admin NOT routed)
   <portal>.<domain> └─► 8 Next.js portals (customer, corporate, vendor,
                          partner, seller, brand, analytics, agent-console)
internal only: identity-lifecycle, dispatcher POST /consume/once,
               PostgreSQL, Redis/Valkey, Kafka
```

| Component | Image | Compose service | k8s object |
|---|---|---|---|
| Odoo 19 | `1000fix/odoo` (`infra/docker/odoo/Dockerfile`) | `odoo` | StatefulSet `odoo` (1 replica, RWO filestore) |
| Keycloak 26.3 | `quay.io/keycloak/keycloak@sha256:08a3…` | `keycloak` (`start`, external DB) | Deployment `keycloak` ×2 + PDB |
| Kong 3.9 DB-less | `kong@sha256:9203…` + render step | `kong-config` (one-shot) + `kong` | Deployment `kong` ×2 (initContainer `render-config`) + PDB |
| 8 portals | `1000fix/portal-<name>` (`apps/web/Dockerfile.portal`) | `portal-<name>` | Deployment/Service/PDB `portal-<name>` ×2 |
| notification-dispatcher | `1000fix/notification-dispatcher` | yes | Deployment ×1 (in-process KPI/DLQ state) |
| telemetry-collector | `1000fix/telemetry-collector` | yes | Deployment ×2 + PDB |
| ml-gateway | `1000fix/ml-gateway` | yes | Deployment ×2 + PDB |
| identity-lifecycle | `1000fix/identity-lifecycle` | yes | Deployment |
| PostgreSQL 17 | compose: `postgres:17.4@sha256` (TLS, WAL archive, DR slot) | `postgres` | **external** managed (Terraform) |
| Redis 7.2 / Valkey 8 | compose: `redis:7.2.5@sha256` (password) | `redis` | **external** managed Valkey (Terraform) |
| Kafka | **external** (`KAFKA_BOOTSTRAP_SERVERS`) | — | **external** |

`local-residency-stub` is **not** deployed: it is synthetic by design and its
image refuses any `FIX_ENV` other than `local`. Production needs the real
residency service (see §6).

### Environment name

`FIX_ENV=prod` everywhere (the `infra/environments.yaml` name; the Odoo image
accepts only ladder names and refuses `production`). The service images accept
`prod` and the alias `production`; notification-dispatcher's entrypoint
normalises `prod` → `production`, because `src/channels.py` enables its
production gateway rules (https-only + SSRF guard) only on that literal.

## 2. Files

| Path | Purpose |
|---|---|
| `infra/compose/docker-compose.prod.full.yml` | complete single-host production stack (deploy, pull-only images) |
| `infra/compose/docker-compose.prod.build.yml` | build overlay: `build:` + production build args per portal |
| `infra/compose/docker-compose.prod.yml` | unchanged narrow Odoo+DB overlay of the environment ladder |
| `infra/compose/kong/kong.prod.yml` | Kong declarative **template** (single source for compose and k8s) |
| `infra/compose/kong/render-kong-config.py` | fail-closed `${VAR}` renderer (env or `VAR_FILE`) |
| `infra/compose/kong/kustomization.yaml` | exposes the two files above to Kustomize as ConfigMap `kong-config-template` |
| `infra/compose/postgres/init-prod/20-app-databases.sh` | compose initdb: least-privilege roles + DBs `odoo`/`keycloak`/`telemetry` |
| `infra/k3s/base/` | environment-neutral manifests (Deployments, StatefulSet, Services, Ingress, PDBs, NetworkPolicies, ConfigMap) |
| `infra/k3s/overlays/production/` | namespace `fix-erp-prod` (PSA `restricted`), hosts, image registry |
| `infra/terraform/` | DigitalOcean: VPC, DOKS, managed PostgreSQL + roles/DBs + firewall, Valkey, optional Kafka, Spaces bucket, registry |

Hosting target: **DigitalOcean, region `sgp1` (Singapore)** — the regional
primary of decision D-013 Option B (`docs/decisions/D-013-split-residency.md`;
the legal opinion names Singapore as the example region) on the provider named
in the workspace `AGENTS.md`. The Bangladesh Zone 4 replica is not on
DigitalOcean (§6).

## 3. Build a release

```bash
cd 1000_fix_codebase
# release.env: FIX_IMAGE_REGISTRY, FIX_RELEASE and the public host names
docker compose -p fix-prod \
  -f infra/compose/docker-compose.prod.full.yml \
  -f infra/compose/docker-compose.prod.build.yml \
  --env-file release.env build
docker compose ... push            # operator step; record the digests
```

Portal images are built **per public host set**: `NEXT_PUBLIC_*` values are
inlined into the browser bundle by `next build`. `PORTAL_BUILD_PROFILE=production`
(set by the build overlay) fails the build when `NEXT_PUBLIC_FIX_API_BASE` or
`NEXT_PUBLIC_ODOO_DB` is missing, or any `NEXT_PUBLIC_*` URL is not https or
points at a loopback host. Never pass a secret as a build arg.

For Kubernetes, pin the pushed digests into the overlay:

```bash
cd infra/k3s/overlays/production
kustomize edit set image 1000fix/odoo=registry.digitalocean.com/fix-erp/odoo@sha256:<digest>
# ... one line per image (13 first-party images); RELEASE_TAG left in place fails at pull
```

## 4. Deploy — single host (Docker Compose)

1. Provision the host (Docker Engine 24+, compose v2), DNS A/AAAA records for
   every host in §5 pointing at it, firewall allowing only 443/tcp in.
2. Place secrets outside the repository, readable only by the deploying user
   (e.g. Vault-rendered `/etc/1000fix/prod.env` mode 0600 + PEM files).
3. **Bootstrap Keycloak first** (Kong needs the realm public key):
   ```bash
   C="docker compose -p fix-prod -f infra/compose/docker-compose.prod.full.yml --env-file /etc/1000fix/prod.env"
   $C up -d postgres keycloak
   # via an SSH tunnel to the keycloak container (admin console is not routed):
   #   create realm ${KEYCLOAK_REALM}, the portal clients, the identity-lifecycle
   #   service-account client; replace the bootstrap admin with a real one.
   #   Realm settings > Keys > RS256 > "Public key" -> file at KEYCLOAK_REALM_PUBLIC_KEY_FILE
   ```
4. `$C up -d` — `kong-config` renders the gateway config (exits 1 and Kong does
   not start if any value is missing or unsafe), then everything starts.
5. First Odoo database initialisation (once):
   `$C run --rm odoo -d fix_production -i base --stop-after-init` (arguments
   replace the service command, so `-d` must be repeated), then install the
   module set the same way.
6. Backups/DR: `docker-compose.dr.yml` standby consumes the `postgres_dr_standby`
   slot (`PG_REPLICATION_*`); the WAL archive volume must be shipped off-host.

### Required variables (compose)

`docker compose config` refuses to load the file while any of these is unset.

| Variable | What |
|---|---|
| `FIX_IMAGE_REGISTRY`, `FIX_RELEASE` | registry prefix and immutable release tag of the `1000fix/*` images |
| `PROD_DB_PASSWORD` | PostgreSQL superuser `fix_admin` |
| `PG_REPLICATION_PASSWORD` | replication role for the DR standby |
| `ODOO_DB_PASSWORD` | role `odoo` |
| `ODOO_ADMIN_PASSWORD` | Odoo master password (`admin_passwd`) |
| `KEYCLOAK_DB_PASSWORD` | role `keycloak` |
| `KEYCLOAK_BOOTSTRAP_ADMIN_PASSWORD` | one-time Keycloak bootstrap admin |
| `KEYCLOAK_REALM` | production realm name (issuer `https://${AUTH_HOST}/realms/${KEYCLOAK_REALM}`) |
| `TELEMETRY_DB_PASSWORD` | role `telemetry` (URL-safe characters: it is embedded in a DSN) |
| `REDIS_PASSWORD` | Redis `requirepass` (URL-safe: embedded in `REDIS_URL`) |
| `KAFKA_BOOTSTRAP_SERVERS` | event-bus brokers (external) |
| `API_HOST`, `ERP_HOST`, `AUTH_HOST` | public host names |
| `PORTAL_HOST_{CUSTOMER,CORPORATE,VENDOR,PARTNER,SELLER,BRAND,ANALYTICS,AGENT_CONSOLE}` | portal host names |
| `FIX_TECHNICIAN_API_KEY` | customer portal technician relay credential |
| `IDENTITY_LIFECYCLE_CLIENT_SECRET`, `IDENTITY_LIFECYCLE_TOKEN` | Keycloak service-account secret, ops-endpoint token |
| `PG_TLS_CERT_FILE`, `PG_TLS_KEY_FILE` | PostgreSQL server certificate/key (PEM files) |
| `KONG_TLS_CERT_FILE`, `KONG_TLS_KEY_FILE` | edge certificate chain/key covering every public host |
| `KEYCLOAK_REALM_PUBLIC_KEY_FILE` | realm RS256 public key (PEM or the bare base64 from the Keys tab) |

Optional: `ODOO_DB` (default `fix_production`), `ODOO_WORKERS` (4),
`KONG_HTTPS_BIND`/`KONG_HTTPS_PORT` (0.0.0.0/443), `KONG_TRUSTED_IPS` (set to
the load balancer range if one sits in front), `CORPORATE_OIDC_CLIENT_ID`,
`CORPORATE_OIDC_CLIENT_SECRET` (confidential client only),
`FIX_SMS_GATEWAY_URL/TOKEN`, `FIX_SMS_REDUNDANT_GATEWAY_URL/TOKEN`,
`FIX_WHATSAPP_API_URL/TOKEN`, `FIX_EMAIL_API_URL/TOKEN` (unset channel = dry
run / fail closed), `PG_REPLICATION_ALLOWED_ADDRESS`, `SUPERSET_URL` (build).

Networks: `edge` (Kong's published port — the only one), `backend`
(`internal: true`), `egress` (outbound for Odoo, dispatcher, portals,
identity-lifecycle). All app containers: `no-new-privileges`, `cap_drop: ALL`,
non-root, healthchecks, `restart: unless-stopped`, memory/CPU limits.

## 5. Deploy — Kubernetes on DigitalOcean

```bash
# 1. infrastructure (credentials only from the environment)
export DIGITALOCEAN_TOKEN=... SPACES_ACCESS_KEY_ID=... SPACES_SECRET_ACCESS_KEY=...
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars        # adjust; configure the remote backend in versions.tf
terraform init && terraform plan -out plan && terraform apply plan
doctl kubernetes cluster kubeconfig save "$(terraform output -raw kubernetes_cluster_id)"
doctl kubernetes cluster registry add "$(terraform output -raw kubernetes_cluster_id)"   # image pull secret

# 2. cluster add-ons (not in this tree): ingress-nginx in namespace ingress-nginx,
#    cert-manager (or upload the edge certificate as Secret fix-edge-tls)

# 3. managed-DB ownership (once, as doadmin): DigitalOcean creates the databases
#    owned by doadmin; hand each to its application role
#    ALTER DATABASE fix_production OWNER TO odoo;
#    ALTER DATABASE keycloak OWNER TO keycloak;
#    ALTER DATABASE fix_telemetry OWNER TO telemetry;

# 4. namespace + secrets (values from terraform output / the vault)
kubectl apply -f infra/k3s/overlays/production/namespace.yaml
kubectl -n fix-erp-prod create secret generic fix-db-odoo \
  --from-literal=host="$(terraform output -raw postgres_private_host)" \
  --from-literal=port="$(terraform output -raw postgres_port)" \
  --from-literal=user=odoo --from-literal=password="$(terraform output -raw odoo_db_password)"
# ... the remaining Secrets below

# 5. Keycloak first (Kong needs the realm key), then everything
kubectl apply -k infra/k3s/overlays/production
```

### Secrets referenced by the manifests (no values in the repository)

| Secret (ns `fix-erp-prod`) | Keys | Source |
|---|---|---|
| `fix-db-odoo` | `host`, `port`, `user`, `password` | Terraform outputs |
| `fix-db-keycloak` | `jdbc-url`, `username`, `password` | `keycloak_jdbc_url`, `keycloak`, `keycloak_db_password` |
| `fix-db-telemetry` | `database-url` | `telemetry_database_url` |
| `fix-redis` | `url` | `valkey_private_uri` (rediss://) |
| `fix-kafka` | `bootstrap-servers`, `security-protocol` (SASL_SSL), `sasl-mechanism` (SCRAM-SHA-256/512 or PLAIN), `sasl-username`, `sasl-password` | the Kafka cluster (external) |
| `fix-odoo` | `admin-password` | vault |
| `fix-keycloak-bootstrap` | `username`, `password` (optional; delete after creating a real admin) | vault |
| `fix-kong-realm-key` | `public-key` | Keycloak realm Keys tab |
| `fix-portal-customer` | `technician-api-key` | vault |
| `fix-portal-corporate` | `oidc-client-secret` (optional) | Keycloak client |
| `fix-identity-lifecycle` | `client-id`, `client-secret`, `ops-token` | Keycloak service account / vault |
| `fix-notification-gateways` | `sms-url`, `sms-token`, `sms-redundant-url`, `sms-redundant-token`, `whatsapp-url`, `whatsapp-token`, `email-url`, `email-token` (all optional) | providers |
| `fix-edge-tls` | `tls.crt`, `tls.key` (type kubernetes.io/tls) | cert-manager / CA |

Non-secret settings live in ConfigMap `fix-platform` (overlay: host names
under `1000fix.com` — **confirm against the DNS zone**).

Security posture: namespace PSA `restricted`; every pod non-root, all
capabilities dropped, no privilege escalation, RuntimeDefault seccomp,
read-only root filesystem except Keycloak (rebuilds Quarkus at start) and the
portals (Next runtime cache); `automountServiceAccountToken: false`.
NetworkPolicies: default-deny ingress+egress, DNS to kube-system, ingress
controller → Kong only, Kong → each upstream port, data-service egress to the
VPC CIDR (`10.110.0.0/20` = `var.vpc_ip_range`; ports 25060 pg, 25061 valkey,
25073/9092 kafka), internet egress (443, +587 for Odoo) only for Odoo,
dispatcher and portals. Change the CIDR/ingress-namespace assumptions in the
overlay if they differ.

## 6. What remains external (not provided by this tree)

- **Real residency service / Bangladesh Zone 4** (D-013 Option B): the
  replication + key-management daemon and the `postgres-resident` replica on
  Bangladesh-resident infrastructure (IPSec VPN to the regional primary). The
  `local-residency-stub` must never be used outside `local`.
- **Kafka cluster** for `libs/py/fix_events` (see gap 2).
- **Gateway credentials and contracts**: bKash, Nagad, SSLCOMMERZ, NBR IVAS
  (e-VAT), bank feeds, SMS aggregators (primary + redundant), WhatsApp, email
  provider, CPaaS/telephony — all integrations fail closed without them.
- **TLS certificates** (edge certificate for every public host; PostgreSQL
  server certificate for the compose stack) and **DNS** records.
- Keycloak production realm, clients, roles and admin accounts (the dev realm
  JSON is synthetic and is NOT imported).
- Ingress controller and cert-manager installation; container registry push;
  monitoring/alerting stack in production (the observability profile is local).
- Off-host backups of the compose WAL archive / DigitalOcean PITR policy review.

## 7. Known gaps (do not paper over)

1. ~~identity-lifecycle cannot run in prod~~ **Resolved 2026-10-23:** `check_environment()` accepts `prod`/`production`; the compose profile gate and the k8s 0-replica patch are removed. Its ops endpoints stay closed (503) until `IDENTITY_LIFECYCLE_TOKEN` is set.
2. ~~Event bus client cannot reach a production broker~~ **Resolved 2026-10-23:** `kafka-python-ng==2.2.3` is in `uv.lock`, the Odoo image (`requirements-first-party.txt`) and the identity-lifecycle image; `libs/py/fix_events` reads `KAFKA_SECURITY_PROTOCOL`, `KAFKA_SASL_*` and `KAFKA_SSL_CAFILE` (refuses a half-configured SASL setup). Compose and k8s pass them from `fix-kafka`. `create_managed_kafka` can now be enabled; the cluster itself is still external.
3. **Odoo is single-replica** (sessions + filestore on a RWO volume). Scaling
   out needs shared sessions and object-storage attachments (the Spaces bucket
   exists; no attachment-storage module is configured).
4. **Customer portal `/api/odoo` rewrite** (`apps/web/customer/next.config.ts`)
   targets `http://127.0.0.1:8069`, which does not exist in its container.
   Kong serves `/api/odoo` on the customer host directly (Odoo session auth,
   rate-limited) as a workaround; the rewrite should become configurable.
5. ~~JWT on portal API routes vs. session-cookie portals~~ **Resolved 2026-10-23:** the portal JSON-RPC paths (`/customer`, `/vendor`, `/seller`, `/brand`, `/partner`, `/analytics`, `/contact`, `/corporate`, `/technician`, `/storefront`, `/p03`) and the customer host's `/api/odoo` are authenticated by Odoo (session cookie from the portal sign-in, Odoo API key for `/technician`, P03 staff check); Kong applies CORS, rate limiting and size limits there. Keycloak JWT stays on `/api/odoo` (API host) and `/svc/*`. Rendered config verified with `kong config parse` → parse successful. Moving portals to Keycloak tokens later means re-adding the jwt plugin per route.
6. **Portal source still carries localhost fallbacks** for empty
   `NEXT_PUBLIC_*` values; the production build profile prevents empty values
   but the fallbacks remain in `apps/web/*/lib/*.ts`.
7. **ml-gateway image has no `libs/py/fix_telemetry`** (build context is the
   service dir) — request spans are no-ops there.
8. **TimescaleDB**: compose PostgreSQL is plain `postgres:17.4`; the collector
   runs its plain-table path. DigitalOcean managed PostgreSQL offers the
   `timescaledb` extension (enable it to get the hypertable path).
9. `tooling/scripts/verify-compose-digests.py` will report the parameterised
   first-party refs (`${FIX_IMAGE_REGISTRY}/1000fix/...:${FIX_RELEASE}`) in
   `docker-compose.prod.full.yml` as unpinned: production pins digests through
   the registry/overlay, not in the compose file.
10. Terraform has **not** been run: `terraform` is not installed on the
    authoring workstation, so `terraform fmt -check` / `validate` / `plan` are
    still owed (needs `terraform init`, i.e. provider download).

## Validation performed

Run on the authoring workstation on 2026-10-23 (outputs summarised):

- `docker compose -f infra/compose/docker-compose.prod.full.yml --env-file <throwaway> config -q` → exit 0;
  with the build overlay → exit 0; with `REDIS_PASSWORD` removed → exit 1
  (`required variable REDIS_PASSWORD is missing a value`). Only Kong publishes a port.
- Kong: `kong-config` rendered the template (secret key supplied as bare
  base64 via `_FILE`), `kong config parse` → `parse successful`; Kong started
  read-only and became `healthy`; no token → 401 on `/customer/*` and
  `/svc/ml/*`; a token signed with the test realm key → passed to the upstream
  (503: upstream not running); a token signed with another key → 401; `/admin`
  on the auth host → 404; `POST /svc/notifications/consume/once` → 404. A value
  containing a quote/newline is refused by the renderer (exit 1, nothing written).
- `kubectl kustomize infra/k3s/overlays/production` (kustomize v5.8.1) → 62
  objects; every Deployment/StatefulSet container has requests/limits,
  readiness + liveness probes, non-root, no privilege escalation, all caps
  dropped; 0 Secret objects; the Kong config rendered from the generated
  ConfigMaps parses in Kong. No cluster was available for server-side dry-run.
- `docker build` Odoo image (`1000fix/odoo:audit`) → OK;
  `docker run -e FIX_ENV=prod 1000fix/odoo:audit python -c "import libs.py.fix_events"` → OK
  (`/opt/1000fix/libs/py/fix_events`, `PYTHONPATH=/opt/1000fix`).
- `docker build` customer portal (`1000fix/portal-customer:audit`, production
  build args) → OK; runtime: `/` 200 and its `/_next/static/*.js` 200 (the
  previous image served static assets from the wrong directory → 404).
- Service images built (`:audit`) and run with `FIX_ENV=prod`:
  notification-dispatcher listens on 0.0.0.0:8110 (reachable from another
  container: 200; `FIX_ENV` normalised to `production`; uid 10001);
  ml-gateway 200 read-only; telemetry-collector refuses to start without
  `DATABASE_URL` (exit 42) and answers 503 `/health` without a database;
  rmm-collector honours `FIX_RMM_ODOO_URL`; local-residency-stub refuses `prod` (42).
- Unit tests: `services/rmm-collector/tests`, `services/notification-dispatcher/tests` pass.
