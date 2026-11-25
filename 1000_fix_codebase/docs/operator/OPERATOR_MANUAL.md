# 1000FiX Integrated Smart ERP Platform — Master Operator Manual
## Operational Procedures, Environment Ladder Management & Site Reliability Engineering (SRE) Handbook
### Conformance: ITIL 4 Operations · ISO 9001:2015 · DoD-11 · TSS §21.3 · PE-001/002

---

## 1. Executive Overview & Estate Baseline

This manual serves as the primary operational authority for System Operators, Site Reliability Engineers (SREs), Database Administrators, and Support Leads managing the **1000FiX Integrated Smart ERP Platform v2.0**.

### Estate Scope & Sizing
- **Total Modules**: 67 Estate Modules (63 Dedicated Addons + 4 Change Requests M25/M26/M32/M42).
- **Installed Addons**: 71 Addons across Layers L1 to L4.
- **Portals**: 8 Specialized Next.js Portals (Customer P01, Field Technician P02, Corporate B2B P05, Brand Partner P06, Marketplace Seller P07, Franchise P08, Agent Console P09, Analytics/BI P10).
- **Environment Ladder**: 12 Segregated Environments (`local`, `ci`, `dev`, `sit`, `uat`, `perf`, `staging`, `training`, `sandbox`, `migration-staging`, `prod`, `dr`).
- **Data Residency**: Strictly divided into General Processing (`RGN-P`) and Sovereign Bangladesh Resident Store (`Z4`).

---

## 2. Standard Operating Procedures (SOPs)

### SOP-01: Environment Ladder Management
| Environment | Purpose | Startup Command | Port Block | Data Rule |
|---|---|---|---|---|
| `dev` | Shared Integration | `docker compose -f infra/compose/docker-compose.dev.yml --profile dev up -d` | 5435 / 6381 / 8071 | Synthetic + Anonymised Sample |
| `sit` | System Integration | `docker compose -f infra/compose/docker-compose.sit.yml --profile sit up -d` | 5436 / 6382 / 8072 | Full TS-002 Set (Moving) |
| `uat` | Business Acceptance | `docker compose -f infra/compose/docker-compose.uat.yml --profile uat up -d` | 5437 / 6383 / 8073 | Full TS-002 Set (Frozen) |
| `perf` | 1.5x Peak Load Test | `docker compose -f infra/compose/docker-compose.perf.yml --profile perf up -d` | 5438 / 6384 / 8074 | Production-shaped Volumes |
| `staging` | Pre-Release Rehearsal | `docker compose -f infra/compose/docker-compose.staging.yml --profile staging up -d` | 5439 / 6385 / 8075 | Production Clone (Masked) |
| `training` | Staff Certification | `docker compose -f infra/compose/docker-compose.training.yml --profile training up -d` | 5440 / 6386 / 8076 | Curated Scenario (Resettable) |
| `sandbox` | Partner APIs | `docker compose -f infra/compose/docker-compose.sandbox.yml --profile sandbox up -d` | 5441 / 6387 / 8077 | Synthetic Externally Reachable |
| `migration` | Cutover Rehearsal | `docker compose -f infra/compose/docker-compose.migration-staging.yml --profile migration-staging up -d` | 5434 / 8069 | Production-volume Clone |
| `prod` | Live Production | `docker compose -f infra/compose/docker-compose.prod.yml --profile prod up -d` | 5442 / 6388 / 8078 | Live Sovereign (Z4 Only) |
| `dr` | Warm Standby | `docker compose -f infra/compose/docker-compose.dr.yml --profile dr up -d` | 5443 / 6389 / 8079 | Streaming Replica (RPO ≤ 15m) |

---

### SOP-02: Production Clone with In-Stream Masking (NFR-086c)
> [!CAUTION]
> Unmasked production clones must NEVER touch disk or intermediate storage in non-production. Always pipe data through the in-stream masking filter.

```bash
# Execute in-stream masked clone from Production to Staging
pg_dump -h 127.0.0.1 -p 5442 -U fix_admin -d fix_production \
  | python tooling/dr/clone_with_masking.py \
  | psql -h 127.0.0.1 -p 5439 -U fix -d fix_staging_masked
```

---

### SOP-03: Disaster Recovery Failover & Cutover (RB-52)
1. **Declare Outage**: Confirm primary unreachable (`pg_isready -h 127.0.0.1 -p 5442` fails).
2. **Fence Primary**: Stop primary container (`docker compose -f infra/compose/docker-compose.prod.yml stop postgres-prod`).
3. **Promote Standby**:
   ```bash
   psql -h 127.0.0.1 -p 5443 -U fix_admin -d fix_production -c "SELECT pg_promote();"
   ```
4. **Shift Ingress Routing**: Update Kong upstream to target DR Odoo (port 8079).
5. **Verify Writes**: Run `py -3.12 tooling/dr/run_r10_m04_dr_rehearsal.py` to confirm write integrity.

---

### SOP-04: High Availability (HA) Pair Management
The four total-outage components (PostgreSQL primary, Keycloak 26, Kong, Nginx) run as clustered pairs per TSS §21.3:
- **Health Verification**:
  ```bash
  py -3.12 tooling/dr/run_ha_kill_node_drills.py
  ```
- **PostgreSQL**: Patroni managed primary-standby pair.
- **Keycloak 26**: Clustered 2-node instances with Infinispan distributed session caching.
- **Kong Gateway**: Clustered multi-node ingress with shared declarative routes.
- **Nginx**: Dual-node edge ingress with keepalived VRRP.

---

### SOP-05: Vault Secret Management & Zero-Leakage Policy (EP-06)
- **Zero Plaintext Secrets**: Hardcoded passwords, API keys, or private tokens in source code, commit history, or logs are strictly prohibited.
- **Runtime Secret Injection**:
  ```python
  from tooling.scripts.vault_secret_manager import VaultSecretManager
  db_password = VaultSecretManager.get_secret("database/credentials/production", "password")
  ```
- **Secret Audit**:
  ```bash
  py -3.12 tooling/scripts/check-secrets.py
  ```

---

### SOP-06: 3-Release Expand/Migrate/Contract Protocol (D-042)
All database schema alterations must follow the 3-release zero-downtime lifecycle:
1. **Release N (Expand)**: Add new columns/tables as nullable or with defaults. Code writes to both old and new columns, reads from old.
2. **Release N+1 (Migrate)**: Backfill data from old to new. Switch application reads to new columns.
3. **Release N+2 (Contract)**: Drop old unused columns/tables after confirming zero legacy queries.

---

## 3. Incident Escalation & On-Call Matrix
| Severity | Impact | Response SLA | Escalation Target |
|---|---|---|---|
| **Sev 1** | Catastrophic Outage (Portal Down / Primary DB Down) | ≤ 15 minutes | Incident Commander + CTO + Lead SRE |
| **Sev 2** | Degraded Performance / Single HA Node Loss | ≤ 30 minutes | Secondary SRE + Module Owner |
| **Sev 3** | Non-Critical Bug / Minor Portal Anomaly | ≤ 4 hours | Support Engineer + Development Lead |
| **Sev 4** | Feature Request / Cosmetic Flaw | Next Sprint | Product Manager |
