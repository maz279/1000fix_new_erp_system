# Production Security Closure Report (R11-M03-T01)

**Document ID**: `SR-2026-10-R11-M03`  
**Governing Standards**: `SC-009` (Vulnerability & Pen-Test Management) · `DoD-15` (Zero High/Critical Findings)  
**Evaluation Date**: 2026-10-22T14:34:37.912213+00:00  
**Computed Verdict**: **`FAIL`** — 1 Critical, 1 High, 1 Medium findings; 5 vectors UNMEASURED  

Every status below was measured by `tooling/scripts/run_r11_m03_security_review.py` in this run against `http://127.0.0.1:8069` and the repository (GV-009). UNMEASURED items need production access or a human act and keep the verdict from PASS.

## 1. Summary

| Assessment Stream | Result | Detail |
|---|:---:|---|
| Penetration test delta | **FAIL** | 16 PASS / 3 FAIL / 5 UNMEASURED of 24 vectors |
| Secrets: `ep06_prod_enforcement` | **PASS** | prod-mode get_secret() refused the plaintext fallback: EP-06 VIOLATION: Secret 'unmapped/r11-security-review-probe:api_key' must be injected from Vault in production! |
| Secrets: `production_secret_rotation` | **UNMEASURED** | no production Vault/OpenBao is reachable from this workstation; no rotation was performed or observed and no key fingerprints are available |
| Key custody handover | **UNMEASURED** | dual-control HSM / key-shard / certificate custody handover is a human act; no signed custody register is observable here |
| Wazuh / osquery SIEM | **UNMEASURED** | Wazuh manager not reachable on 127.0.0.1:1514/1515 (compose profile msp not running); agents, heartbeats and alert dispatch unobservable |

## 2. Penetration Test Delta Vectors

| Code | Vector | Severity if failed | Result | Details |
|---|---|:---:|:---:|---|
| `A01-01` | Unauthenticated Portal Session Rejection | HIGH | **PASS** | 3/3 protected routes rejected an unauthenticated request |
| `A01-02` | Cross-Tenant IDOR Defense | HIGH | **PASS** | pytest test_tenant_isolation_negative.py: 5 passed, 0 failed, 0 errors, 0 skipped (exit 0) (unit-level isolation tests; no live two-tenant probe) |
| `A01-03` | Broken Object Level Auth (BOLA) Defense | HIGH | **UNMEASURED** | needs two authenticated portal identities to swap object ids; none available to this run |
| `A01-04` | Multi-Company & OU Isolation (AS-03 / FF-21) | HIGH | **PASS** | FF-20/21/22 check_model_registry.py exit 0: model-registry: OK - 174 models checked, all carry AS-02/AS-03 conformant fields; all relation targets resolve |
| `A02-01` | Zero Plaintext Secrets in Source Tree | CRITICAL | **PASS** | 0 secret pattern hit(s) in 4713 source/config files |
| `A02-02` | PDPA Sovereign Residency Enforcement (FF-09) | HIGH | **FAIL** | check_ff09_residency.py exit 1: FF-09: FAIL - 7 residency bypass path(s) found: |
| `A02-03` | TLS 1.3 / mTLS In-Transit Encryption | HIGH | **UNMEASURED** | 0 TLS-version directives in infra/ specs; production edge/mesh TLS termination is not reachable from this workstation |
| `A03-01` | SQL Injection Parameter Sanitization | CRITICAL | **FAIL** | 2 unreviewed execute() calls built by string formatting (of 27 execute calls; 5 more carry a reviewed noqa: S608 justification) in 455 non-test Python files: services/bi-warehouse/src/dbt_runner.py:272; services/bi-warehouse/src/warehouse_sync.py:351 |
| `A03-02` | Arbitrary Command Execution (shell=True / os.system) | CRITICAL | **PASS** | 0 shell=True / os.system / os.popen calls in 455 non-test Python files |
| `A03-03` | Dynamic Code Evaluation (eval/exec) | HIGH | **PASS** | 0 bare eval()/exec() calls in 455 non-test Python files |
| `A04-01` | Seller KYC Verification Gate (M12) | HIGH | **PASS** | pytest test_seller_api.py::TestKycGate: 1 passed, 0 failed, 0 errors, 0 skipped (exit 0) |
| `A04-02` | Commercial Monetary Tampering Defense | HIGH | **PASS** | pytest test_seller_api.py::TestActionDelegation::test_price_validation_server_side: 1 passed, 0 failed, 0 errors, 0 skipped (exit 0) |
| `A04-03` | Dispute SLA 48h Lockout & Escalation | MEDIUM | **PASS** | pytest test_dispute_sla.py: 4 passed, 0 failed, 0 errors, 0 skipped (exit 0) |
| `A05-01` | Stack Trace Masking on Error Responses | MEDIUM | **PASS** | 0 of 4 unauthenticated error/redirect responses carry a Python traceback |
| `A05-02` | ClickHouse Analytical Read-Only Boundary (FF-28) | HIGH | **PASS** | check-lb06-analytics-readonly.py exit 0: [PASS] FF-28: LB-06 Downstream Read-Only Invariant satisfied. |
| `A05-03` | Production Port Surface Hardening | HIGH | **PASS** | 0 DB/cache/analytics ports published beyond loopback across 77 port mappings in 17 compose specs |
| `A06-01` | Zero Unauthorized Forks (AS-05 / FF-03) | MEDIUM | **PASS** | FORKS.yaml entries: 0; check-vendor-clean exit 0: check-vendor-clean: OK - vendor/ clean (FF-03) |
| `A06-02` | Supply-Chain Dependency Vulnerability Scan | HIGH | **UNMEASURED** | sbom.cdx.json components: 176; the CVE lookup needs the OSV/NVD feeds (network) - no offline vulnerability database |
| `A07-01` | Anti-CSRF Route Policy (no csrf=False opt-outs) | MEDIUM | **PASS** | 0 csrf=False route opt-outs across 30 controller files |
| `A07-02` | Session Rotation Upon Privilege Elevation | MEDIUM | **UNMEASURED** | needs an authenticated login against Odoo and the Next.js portals to observe session-id rotation; no test identity is available to this run |
| `A08-01` | Insecure Deserialization (pickle) Defense | HIGH | **PASS** | 0 pickle/dill deserialisation calls in 455 non-test Python files |
| `A08-02` | Container Image Digest Pinning | MEDIUM | **FAIL** | 59/68 compose images @sha256-pinned, 9 carry the PENDING-FIRST-BUILD marker (digest-pinning policy); 10/13 Dockerfile FROM lines pinned; unpinned: apps/web/Dockerfile.portal:13 node:${NODE_VERSION}; apps/web/Dockerfile.portal:22 node:${NODE_VERSION}; apps/web/Dockerfile.portal:32 node:${NODE_VERSION} |
| `A09-01` | Transactional Audit Logging (FF-20) | MEDIUM | **PASS** | FF-20/21/22 check_model_registry.py exit 0: model-registry: OK - 174 models checked, all carry AS-02/AS-03 conformant fields; all relation targets resolve |
| `A09-02` | Privileged Admin Action Audit Trail | MEDIUM | **UNMEASURED** | needs a live privileged action and inspection of the resulting audit records |

## 3. Sign-off

No sign-off is recorded by this tool. The computed verdict is `FAIL`; the closure condition (all vectors measured clean, rotation and custody evidenced) is not met.
