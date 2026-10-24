# 1000 FiX ERP — Release Checklist

**Generated:** 2026-10-23, deployment-readiness pass.
**Principle:** every ✅ below was measured on this workstation (evidence path
given); every ⬜ is an operator action that will never be faked here
(GV-009: an assertion is not evidence).

---

## 1. Engineering — verified ✅

| # | Item | Measured result | Evidence |
|---|---|---|---|
| 1 | Full test estate | **4,985 passed / 0 failed / 2 explained skips** | pytest exit 0, 2026-10-23 |
| 2 | Fitness suite | **0 failures** (28+ checks, FF-09 residency sole-client included) | `tooling/fitness/evidence/fitness-20261023T085612Z.json` |
| 3 | Lint (whole repo) | ruff `All checks passed!`; `pre-commit run -a` code hooks all green | — |
| 4 | Security — record-rule isolation | **338 ir.rules live** (167 company + 171 OU) in both DBs; live `with_user` proof 6/6 (cross-company/OU read, search, write all raise `AccessError`) | `addons/platform/cd_rbac_ext/tests/test_isolation_rules_runtime.py` |
| 5 | Security — L9 internal pentest | **20/20 measured PASS, 0 Critical/High** | `evidence/r09-m05-l9-pentest-evidence.json` |
| 6 | Digest immutability | **81/81 image refs verified against registries, 0 fail, 0 pending** (incl. local-registry digest round-trip) | `tooling/scripts/verify-compose-digests.py` |
| 7 | Kong gateway | Routes `/storefront` + `/p03` added; CORS, rate-limit 300/min, HSTS/nosniff/DENY/Referrer-Policy on every response — verified over **TLS 8443** (chain `Verify return code: 0`) | `infra/compose/kong/kong.yml`, `infra/compose/kong/certs/` |
| 8 | Odoo production posture | `generate-odoo-conf.py --profile prod`: `list_db=False`, `workers=4`, `proxy_mode=True`, `dbfilter`, env-injected secrets. **Boot smoke verified**: login 200; db-selector 404; `db/list` → AccessDenied; wrong-master-password POST creates nothing | `infra/odoo-conf/prod.conf` |
| 9 | Odoo container image | Built, pushed to local registry, **booted strictly by digest** (health 200 on the compose network; DE-11 env guard enforces FIX_ENV + local-only DB host) | `1000fix/odoo:19.0-dev@sha256:bb924ef…` |
| 10 | Portal container images | All **8 portals** build standalone + boot by digest (HTTP 200) — multi-stage, non-root UID 10001, healthchecked | `1000fix/portal-customer:19.0.0@sha256:282984…` etc. |
| 11 | Kafka event bus (real cluster) | **Broker-kill drill PASS** (1 of 3 stopped; acks=all produce/consume continued on 2 survivors; 60/60 records). **Dual-write parity PASS** (250/250 events real XADD + acks=all produce, 0 mismatches). **Consumer cutover + rollback SLA PASS** (rollback 0.007 s < 5 s). **DLQ+replay PASS** (poison dead-lettered w/ headers, redrive idempotent). **DI-05 dedup barrier PASS** (300 first-pass admitted, 0 re-delivery, 1,564 ops/s over the wire). Topic policy: **130 fix.events.* topics, partitions=3, min-ISR≥2, 0 violations** | `evidence/kafka-cluster-survival-evidence.json`, `dual-write-parity-evidence.json`, `event-bus-cutover-log.json`, `kafka-dlq-replay-evidence.json`, `consumer-idempotency-evidence.json`, `event-schema-registry-audit.json` |
| 12 | Analytics warehouse (real ClickHouse) | Replica restored from primary snapshot (63 MB); **real sync: 123 branches + 200 customers + 500 orders extracted→loaded→reconciled, checksums verified, 0 synthetic rows**; **NFR-039 measured p95 = 0.178 s** (budget 10 s) | `evidence/r09-m01-migration-reconciliation.json`, `r09-m01-nfr039-performance-evidence.json` |
| 13 | Telemetry load (real collector) | **Sustained 50k/min: 16,750 pings accepted, 0 errors; peak 75k/min: 12,500 accepted; POST p95 31 ms** (budget 100 ms) | `evidence/r09-m03-telemetry-load-evidence.json` |
| 14 | Distributed tracing | Correlation-id + traceparent on every response of the instrumented services (verified live on notification-dispatcher + identity-lifecycle: 200 + both headers) | `libs/py/fix_telemetry/http.py` |
| 15 | External integrations | **Fail closed**: payments/e-VAT/payout rail refuse when unconfigured (never canned success, never self-minted NBR tokens); DSR residency over the canonical SSRF-hardened client | service suites green |
| 16 | E2E sweeps | **Visual 36/36 clean; security headers 24/24; API 67/67** (all 8 portals + Odoo + gateway) | `results/visual-drive.json`, `results/api-sweep.json` |
| 17 | Compose hygiene | Integration profile **fully healthy** (novu+mongo, pgbouncer, airflow, keycloak, kong TLS, residency-stub…); **0 host-port collisions across 17 compose files** (78 distinct ports) | — |
| 18 | Runtime deps | Odoo 19 (vendor, FF-03 clean), Kafka transport `kafka-python-ng` pinned in `pyproject.toml` (lazily imported so stdlib-only images still boot) | — |

## 2. Gate verdicts — honest (2026-10-23 re-run)

| Gate | Verdict | What remains |
|---|---|---|
| G1a / G1 | CONDITION | coverage 56% vs 80% target (disclosed); MG-004 sign-off PENDING; walk-in timing INCOMPLETE |
| G0a / G0b / G9 | **RED-OPEN** — genuine human items: B-05b (Steering approves MV-01..05 CR), G2-10/G9-10 (Steering gate sign-offs) | operator/governance |
| G3 / G4 / G5 | CONDITION (0 FAIL) | production volume + human demonstration items |
| G6 / G7 / G8 | CONDITION/FAIL on production items (branch rollout 0/53 live, DR RPO/RTO unmeasured) — all engine-level items now measured PASS | operator |

## 3. Operator-only actions ⬜ (cannot be done from this workstation)

1. **GitHub Actions**: `gh auth login`, push `develop`, trigger `ci.yml` — archive the first real run URL (all current evidence is labelled `runner: local-harness`).
2. **Production registry + CA**: push the built images to your registry (re-pin digests there); replace the development Kong CA with a real CA-issued certificate.
3. **External credentials**: bKash / Nagad / SSLCOMMERZ sandbox→production, NBR IVAS e-filing, bank feed (INT-007), CPaaS/telephony (hotline 16743 capture). Every one of these integrations fails closed today by design.
4. **Independent penetration test** (the internal L9 is green; the gate requires an external one).
5. **Governance**: Steering approval of B-05b CR; G2/G9 Steering sign-offs (recorded in GV-003); training rosters; board minutes.
6. **Branch rollout** (53 registered centres, 0 measured live) and the **DR drill on production infra** (RPO/RTO currently unmeasured).
7. **Production cutover** (R11) — correctly marked NOT EXECUTED; no cutover has occurred.
8. **12-environment ladder on real hosts** — ports no longer collide, but only one host exists here.
9. **BitLocker** (elevated `manage-bde -on C:` on any workstation that will hold production data).

## 4. Deployment quick-start

See `docs/guides/deployment-guide.md` — every command verified on this
workstation. Stack: `docker compose -f infra/compose/docker-compose.yml
--env-file .env --profile core --profile auth --profile integration up -d`;
Odoo via the image or `vendor/odoo/odoo-bin` with the prod profile; portals
via `Dockerfile.portal` (all 8 build standalone); gateway on 8000/8443 (TLS).
