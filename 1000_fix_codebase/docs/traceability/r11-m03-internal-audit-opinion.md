# Internal Audit Opinion on Programme Controls & Governance (R11-M03-T05)

**Document ID**: `IAO-2026-R11-01`  
**Standard**: `GV-009` (Programme Assurance & Governance Framework) · `GV-005` (Stub Management)  
**Evaluation Date**: 2026-10-22T14:34:45.571538+00:00  
**Computed Verdict**: **`FAIL`** — QUALIFIED_OPINION_EXCEPTIONS_FOUND  

Every status below was measured by `tooling/scripts/audit_programme_controls.py` in this run (GV-009). A check that could not be observed is UNMEASURED and keeps the verdict from PASS.

---

## 1. Summary of Audit Checks

| Check | Result | Detail |
|---|:---:|---|
| Gate evidence chain G0a→G9 | **FAIL** | 0/12 gates PASS; not passed: G0a, G0b, G1, G1a, G2, G3, G4, G5, G6, G7, G8, G9 |
| GV-005 stub ledger | **FAIL** | 7/8 closed; 1 open; 0 expired |
| Bypass control `ff03_vendor_clean` | **PASS** | check-vendor-clean: OK - vendor/ clean (FF-03) |
| Bypass control `ff09_residency` | **FAIL** | FF-09: FAIL - 7 residency bypass path(s) found: |
| Bypass control `ci_bypass_markers` | **PASS** | 1 files, 0 markers |
| Bypass control `bypass_log_register` | **UNMEASURED** | no AR-012 §10 pipeline bypass log artefact exists in the repository to audit |
| Audit sign-off | **UNMEASURED** | Head of Internal Audit / Audit Committee Chair signatures are a human act; no signed opinion is observable here |

---

## 2. Gate Evidence Chain

| Gate | Name | Script | Evidence | Result | Detail |
|---|---|:---:|---|:---:|---|
| `G0a` | Foundations & Governance | yes | tooling/gate/evidence/gate-g0a-latest.json | **FAIL** | recorded verdict RED-OPEN-BLOCKERS; criteria CONDITION=5, OPEN=1, PASS=12 |
| `G0b` | Sovereignty & Architecture Baseline | yes | tooling/gate/evidence/gate-g0b-latest.json | **FAIL** | recorded verdict RED-OPEN; criteria CONDITION=2, OPEN=1, PASS=8 |
| `G1` | Wave 1 Service Delivery Architecture | yes | tooling/gate/evidence/gate-g1-latest.json | **FAIL** | recorded verdict CONDITION; criteria CONDITION=6, PASS=6 |
| `G1a` | Wave 2 Field Service & Mobile App | yes | tooling/gate/evidence/gate-g1a-latest.json | **FAIL** | recorded verdict CONDITION; criteria CONDITION=3, PASS=7 |
| `G2` | Wave 3 Commercial & Billing Engine | yes | tooling/gate/evidence/gate-g2-latest.json | **FAIL** | recorded verdict RED-OPEN; criteria CONDITION=9, OPEN=1 |
| `G3` | Wave 4 PDPA, Agreements & Contact Centre | yes | tooling/gate/evidence/gate-g3-latest.json | **FAIL** | recorded verdict CONDITION; criteria CONDITION=7, PASS=5 |
| `G4` | Wave 5 People, Payroll & Quality Depth | yes | tooling/gate/evidence/gate-g4-latest.json | **FAIL** | recorded verdict CONDITION; criteria CONDITION=7, PASS=11 |
| `G5` | Wave 6 Asset Management & GRC | yes | tooling/gate/evidence/gate-g5-latest.json | **FAIL** | recorded verdict CONDITION; criteria CONDITION=3, PASS=7 |
| `G6` | Wave 7 Advanced Automation & Integrations | yes | tooling/gate/evidence/gate-g6-latest.json | **FAIL** | recorded verdict RED; criteria CONDITION=6, FAIL=1, PASS=3 |
| `G7` | Wave 8 BI, Warehouse & Analytics | yes | tooling/gate/evidence/gate-g7-latest.json | **FAIL** | recorded verdict RED; criteria CONDITION=6, FAIL=1, PASS=3 |
| `G8` | Wave 9 Multi-Entity & Final Pre-Prod | yes | tooling/gate/evidence/gate-g8-latest.json | **FAIL** | recorded verdict RED; criteria CONDITION=4, FAIL=2, PASS=2 |
| `G9` | Programme Closure & Final Acceptance | yes | tooling/gate/evidence/gate-g9-latest.json | **FAIL** | recorded verdict RED-OPEN; criteria CONDITION=9, OPEN=1 |

## 3. GV-005 Stub Ledger

| Stub | Target Date | Status | Expired |
|---|---|---|:---:|
| `STUB-M15-M19-001` | 2026-10-17 | CLOSED | no |
| `STUB-M31-M22-001` | 2026-10-18 | CLOSED | no |
| `STUB-M31-M23-001` | 2026-10-18 | CLOSED | no |
| `STUB-M02-M22-001` | 2026-10-18 | CLOSED | no |
| `STUB-M34-M23-001` | 2026-10-18 | CLOSED | no |
| `STUB-M42-M23-001` | 2026-10-18 | CLOSED | no |
| `STUB-M02-M55-001` | 2026-10-18 | CLOSED | no |
| `STUB-M10-M11-001` | 2026-11-30 | REOPENED 2026-10-22 — audit: `cd_loyalty/models/fix_loyalty_stub.py` still returns `stub_active: True`; the prior CLOSED was a status write, not an integration, and its closure date (2026-11-30) had not even occurred | no |

## 4. Computed Opinion

- **Opinion**: `QUALIFIED_OPINION_EXCEPTIONS_FOUND` (derived from verdict `FAIL`)
- **Exceptions**: gate_chain, stub_ledger, bypass:ff09_residency
- **Unmeasured**: bypass:bypass_log_register, audit_sign_off
- **Signatories**: none recorded — this tool computes the opinion; signing it is a human act it cannot observe.
