# R02–R11 Zero-Trust Audit & Correction Report

**Report date:** 22 October 2026
**Scope:** All ten phases of `roadmap/Revise_roadmap/` (R02–R11, 242 tasks), plus the runtime/deployment estate, audited on the zero-trust principle (GV-009: an assertion is not evidence) after the R01 correction of 2026-10-21.
**Method:** Three parallel deep-audit agents classified every task REAL / STUB / MISSING / ASSERTION-ONLY with file:line evidence; every finding was re-verified against the codebase; all corrections were executed and re-measured on this workstation (live stack: 13 healthy compose services + host Odoo + 8 built portals).

---

## 0. Verdict

R02–R11 repeated R01's pattern at increasing severity: **the artefacts existed, the measurements did not.** Later phases (R07–R11) went further — hand-authored "signed" gate reports, invented production figures (hypercare request counts, month-1 revenue, an ISO certificate number, a 7-0 board GO vote), and three mutually contradictory DR results were committed as evidence. Simultaneously, genuinely honest measurement tools existed and reported FAIL/INCOMPLETE — and were ignored by the roadmaps.

After this correction: **every gate verifier honours exit codes, every fabricated artefact is quarantined, every locally-achievable stub found by the audit is either fixed or explicitly OPEN**, and the full runtime (Odoo + 8 portals + gateway + services) builds, runs and passes 36/36 visual, 24/24 headers and 67/67 API probes.

---

## 1. What was fixed (found → corrected)

### 1.1 Gate verifiers — all 13 now honest (executed checks, honoured exit codes, `-Json` records)

| Gate | Before | After (measured today) |
|---|---|---|
| G1a | directory-existence PASSes, hardcoded "1094 fields" | **7 PASS / 3 CONDITION** — live psql counts, executed checkers (1659 translated fields parsed from tool output), coverage 56.03% disclosed vs 80% target |
| G1 | MG-004 grep printed "signed off" while the file says PENDING | **6 PASS / 6 CONDITION** — sign-off state parsed; PENDING is CONDITION |
| G2 | source-string blocklist (self-written `source: production` could PASS) | provenance by **generator-script existence**; 0 PASS / 9 CONDITION / 1 OPEN (RED-OPEN, honest) |
| G3 | literal PASS ×5, dead variables, no JSON | **5 PASS / 7 CONDITION / 0 FAIL** — suites executed, Mushak template verified (UTF-8 + `\uXXXX` regex), AUT register parsed (60/60 engines named) |
| G4 | literal PASS ×16 incl. hardcoded "17.0h / 95.56% / 64.0%" | **11 PASS / 7 CONDITION / 0 FAIL** — unit suites executed; simulated "runtime" criteria honestly CONDITION |
| G5 | closure record claimed 10/10 vs measured FAIL | **7 PASS / 3 CONDITION** — journeys/QMS/MSP suites executed; RPO/RTO INCOMPLETE |
| G6 | file-existence + "transacting" prose; hand-written sign-off required | **3 PASS / 6 CONDITION / 1 FAIL** — event registry verified live (215 registered / 175 published); dual-write FAIL is the truth |
| G7 | "payout accuracy 100%" decided by grepping for a string | **3 PASS / 6 CONDITION / 1 FAIL** — 166 marketplace + 65 settlement tests executed; branch rollout FAIL (0/53 live) |
| G8 | existence + grep; read hand-authored promotion record | **2 PASS / 4 CONDITION / 2 FAIL** — L9 pentest read honestly (now 20/20 measured, 0 High); DR FAIL |
| G9 | exit 0 on CONDITION (CI-green ambiguity) | `-Strict` switch; G9-02 now checks the real `cd_multi_entity` module; **0P/9C/1O RED-OPEN** (truth) |
| GP/G0a/G0b | (already corrected 2026-10-21) | re-run green |

The two Python verifiers that ignored exit codes and invented counts (`verify_gate_g3.py`, `verify_gate_g4.py`) are neutralised in place with deprecation stubs that exit 2.

### 1.2 Fabrications quarantined (23 artefacts, with reasons in the two `_quarantine/README.md` files)

- **Evidence JSON (13):** hand-written gate G6/G7/G8 "signed" reports (no generator, role-name or conflicting-name signatories); R10 hand-over/training/GO-decision/readiness-dossier/OpenAPI-PASS; R11 hypercare-day-1 (482,150 requests), month-1 operational proofs (৳42.85M), service-transition handover; content-approval register (CTO named differently in two documents).
- **Markdown narratives (10):** month-1 close "OFFICIALLY SIGNED", SV-004 "DAY-1 OPERATIONAL", capacity-velocity "APPROVED BY STEERING", walk-in timing "PASS" (machine evidence: INCOMPLETE, 0/10), kernel conformance ("Odoo 19 Enterprise" — the vendor tree is Community), online-booking 68.40% (no pilot data), payment "CERTIFICATION" (offline canned successes), Mushak "NBR acceptance" (self-minted token), readiness dossier "ALL GATES RATIFIED", training closure rosters.
- **Left in place, honestly superseded:** governance artefacts (`v1.0-scope-completion-statement`, `GV-003 GO decision`, `SC-003 DPIA`, `docs/decisions/*`) — untouched per the standing governance decision; the honest gate verdicts (G4-08 CONDITION, G9 RED-OPEN) now carry the truthful state on top of them.
- **Corrected, not quarantined:** g3/g5 gate closure records restate the measured verdicts; the GV-005 stub register **REOPENED** `STUB-M10-M11-001` (loyalty: code still returns `stub_active: True`; the prior "closure" even carried a future date); all ten roadmap frontmatters now carry evidence-derived statuses.

### 1.3 Genuine code defects fixed (each with real tests)

| Defect | Fix | Proof |
|---|---|---|
| **Security HIGH — 174 transactional models had no company/OU `ir.rule`** (a column isolates nothing) | Loaded the generated rule set into both databases | **338 rules live** (167 company + 171 OU); L9 pentest re-run: **20/20 measured PASS, 0 Critical/High**; new live `with_user` isolation suite: **6/6** (cross-company read/search/write raises `AccessError`; OU rule enforces; own-company visible) |
| Permission & tenant-isolation "proofs" were tautologies (tests raised `AccessError` themselves) | Real `ir.rule` enforcement now proven at the ORM as a non-superuser (see above); pentest probes documented fail-open → recorded in G7-6 as UNPROVEN until the external pen-test | `addons/platform/cd_rbac_ext/tests/test_isolation_rules_runtime.py` |
| Route "optimisation" was `base_hours × 0.813` (a constant masquerading as an 18.7% gain) | Real optimiser: OSRM table when the field profile is up, haversine otherwise; nearest-neighbour + bounded 2-opt; identical planning constants on both sides; orders without GPS refused | cd_field_service suite **64/64**; tests assert a measured improvement over a crossing layout |
| Consolidation wrote constant 1,000,000/650,000 lines per entity | Aggregates **posted `account.move.line` balances** per entity company, FX at the real rate; refuses to "consolidate" an empty ledger | cd_multi_entity **54/54** (tests now post real journal entries) |
| Payment connectors returned canned sandbox successes; "CERTIFIED" records | **Fail closed**: unconfigured sandbox URL raises; certification requires a live endpoint (in-process HTTP stub in tests) | payment-connectors **75/75** |
| e-VAT minted its own `NBR-IVAS-…-M91-…` acceptance token | Unconfigured → `NOT_SUBMITTED` ("return submission NOT accepted"); submission only over the wire | evat-adapter **26/26** |
| INT-007 payout rail "# Simulate execution" | Unconfigured bank endpoint raises; outcomes only from the rail's response; unresolved recipients → UNKNOWN | payout_rail 63/63 + settlement 43/43 + settlement-ORM 65/65 |
| DSR residency client was `NotImplementedError` (and a duplicate of the canonical client) | `FixResidencyAdapter` over **`libs/py/fix_residency`** (the sole SSRF-hardened Z4 client, FF-09); synthetic values never exported; erase over real HTTP | DSR **29/29** against the live stub; **FF-09: OK** |
| Telemetry collector's TimescaleDB flush was a no-op with `timescaledb_ready: true` hardcoded | Real flush into Postgres with honest `/health` (`storage_mode: plain-postgres-table`, `db_reachable: true`, schema auto-created); added to compose (observability profile) | service **live and healthy** on :8084 |
| Warehouse chain was circular (silent SQLite fallback; synthetic rows reconciled against themselves; catalogue padded to exactly 1,335; dbt freshness simulated) | Fallback loudly labelled; synthetic supplementation removed; real catalogue counts; freshness from the real replica | bi-warehouse + stt **144/144** |
| STT echoed its input (WER from fixture strings) | Unconfigured backend → explicit not-configured; optional real backend seam; "production drift" test renamed to what it is | included in the 144 |
| ml-gateway container printed a line and exited; registry metrics invented | Real stdlib HTTP server (`/health`, `/v1/dispatch`, `/v1/forecast`) with **`model_backend: heuristic-v1`** labels — no invented accuracy, no fake mlflow/s3 ids | ml-gateway + fix_events **173/173** |
| `cd_field_service` security XML used `res.groups.category_id` (removed in Odoo 17+) — module could never install | Field dropped (Odoo-19 pattern) | **71/71 cd_\* modules installed** in `fix_dev` |
| pylint-odoo hook triple-dead (nonexistent tag v8.0.28, no exported hook id, unmatchable path regex) | Local python-env hook, pin 8.0.22, `(^|/)addons/` regex, scoped `.pylintrc-odoo` (sql-injection only) | hook passes estate-wide; `pre-commit run -a` **exit 0** |
| Novu never started (missing Mongo + 3 secrets), PgBouncer healthcheck wrong port, Airflow missing its DB | `novu-mongo` service + env-secret wiring + host port 3040; `LISTEN_PORT`; `postgres/init/10-airflow-db.sql` | integration profile **fully healthy** (13 services) |

### 1.4 Deployment readiness added

- All 8 portals: `output: "standalone"` (8/8 rebuilds succeed) + shared multi-stage non-root healthchecked `apps/web/Dockerfile.portal`.
- Kong now also routes `/storefront` and `/p03` (reloaded, verified through the gateway).
- Odoo production config generator: `generate-odoo-conf.py --profile prod` → `list_db=False`, `workers=4`, `proxy_mode`, `dbfilter`, env-injected secrets (never resolved from the dev `.env`).
- Compose ladder port collisions remapped (migration 5454, HA 5462/5463/8181/8182/8101).
- `docs/guides/deployment-guide.md`: every command verified on this workstation.
- **API sweep** (new `tooling/e2e/api-sweep.py`, SSRF-hardened per the security hook): **67/67 routes** answer through both direct and gateway paths.

### 1.5 Runtime verification (measured today)

- **Visual drive 36/36 clean** (was 23/36 — the four "down" portals are now running production builds).
- **Headers sweep 24/24** (was 11/13).
- **In-app browser inspection** of all 8 portals + the Odoo back-office (logged in; screenshot evidence) + gateway path — customer portal renders fully in Bengali; corporate portal is auth-gated with ৳ formatting; every portal presents its real navigation surface.
- **Fitness 0 failures** (incl. FF-09 now green).
- Full estate suite + pre-commit re-run after every change (final numbers below).

---

## 2. Per-phase honest status

| Phase | Status after correction (evidence) |
|---|---|
| **R02** Kernel & core hardening | EXECUTED — G1a 7P/3C, G1 6P/6C; permission suite tautology superseded by live isolation proof; MG-004 PENDING; walk-in timing INCOMPLETE |
| **R03** Field ops & offline | EXECUTED — G2 RED-OPEN (honest); route optimiser now real; **SQLCipher offline store remains an in-memory fake (OPEN)**; telemetry flush now real |
| **R04** Money & tax depth | EXECUTED — G3 5P/7C on executed checks; payment/e-VAT fail-closed; financial coverage measured (reconciliation.py 92.52%, tax_logic 100%, payroll gaps recorded); 0/60 automation engines deployed (register complete, engines are runtime work); OTel absent (OPEN) |
| **R05** Agreements & PDPA | EXECUTED — G4 11P/7C; all four "runtime" G4 items honestly CONDITION (simulations fixed-by-construction); DSR residency client now real over the canonical lib |
| **R06** People & payroll | EXECUTED — G5 7P/3C (10/10 claim corrected); Odoo payroll coverage 34.7% / payroll-service 0.0% disclosed against the 100% claim |
| **R07** Assets & event bus | EXECUTED — G6 3P/6C/**1F** (dual-write parity 0/1000 is the truth); **real Kafka backend NOT implemented (OPEN — brokers now up, in-memory bus honestly labelled)**; ML registry fabrications removed |
| **R08** Marketplace & settlement | EXECUTED — G7 3P/6C/1F (0/53 branches live); tautological isolation "proofs" superseded; payout rail fail-closed |
| **R09** Intelligence & warehouse | EXECUTED — **L9 pentest 20/20 measured, 0 High after the isolation-rule fix**; warehouse honesty restored; STT/ml-gateway labelled for what they are; hand-written G8 report quarantined (no honest G8 run exists yet) |
| **R10** Multi-entity & pre-production | EXECUTED — machine audits FAIL (honest); consolidation now aggregates real ledger; hand-over/training/GO fabrications quarantined; env-ladder ports decollided but 12 concurrent environments remain single-host only (OPEN) |
| **R11** Cutover & closure | **NOT EXECUTED** — no production cutover occurred; all operational figures were fabrications (quarantined); G9 RED-OPEN |

---

## 3. Remaining OPEN (external or out of this pass — never to be faked)

1. **Real GitHub Actions runs** (gh unauthenticated locally) — everything is labelled `runner: local-harness`.
2. **Kafka real backend + broker-kill/dual-write drills** — brokers are up; the transport code, parity run and drill evidence are unimplemented.
3. **External credentials & certifications** — bKash/Nagad/SSLCOMMERZ, NBR IVAS, bank feeds, CPaaS/telephony, an independent pen-test.
4. **ClickHouse warehouse population + NFR-039** — recorded UNMEASURED (401 without credentials).
5. **Odoo image build + registry push** — digests PENDING-FIRST-BUILD.
6. **k8s/Terraform** (`infra/k3s`, `infra/terraform` empty) and the twelve-environment concurrent ladder.
7. **Flutter apps and the real SQLCipher store; real ML/STT models.** *(OTel instrumentation was OPEN here and is now DONE — see the addendum.)*
8. **All human sign-offs** (Steering gates, countersignatures, training, board minutes) and the production cutover itself.
9. **BitLocker** (operator action), legacy profiling artefacts, physical counts/pilot telemetry.

---

## 4. Concurrency note

A parallel session had modified ~hundreds of files earlier on 2026-10-22 (it had already begun honest-tooling remediation — the isolation-rule generator, the G2/G9 rewrites, the ORM test conftest). Per the operator's decision its edits were treated as the baseline and re-verified; two verification agents were later cut off by a usage limit **after** landing the telemetry/warehouse/STT/ml-gateway work (all suites green) and bringing the Kafka brokers up; their unfinished remainder (the Kafka transport) is OPEN above, and the DSR duplicate client they left was consolidated onto the canonical `fix_residency` client in this pass.

---

## 5. Deployment-Readiness Addendum — 2026-10-23

The operator required "100% deployment-ready". Everything closable from this
workstation was closed in a final pass (full checklist with evidence paths:
`docs/guides/RELEASE-CHECKLIST.md`). Items previously OPEN, now DONE:

- **Kafka real transport (was the largest OPEN item)** — five LIVE drills all
  PASS: broker-kill (acks=all on 2 survivors, 60/60 records), dual-write
  parity (250/250 real Redis XADD + Kafka produce, 0 mismatches), consumer
  cutover with rollback SLA 0.007 s, DLQ+replay (poison dead-lettered with
  headers, redrive idempotent by committed offsets), DI-05 SADD dedup barrier
  (300/300 first pass, 0 re-delivery). Topic policy measured live: 130
  `fix.events.*` topics, partitions=3, min-ISR≥2, 0 violations (one stray
  1-partition drill topic was found by the new measurement and deleted).
- **Container images + real digests** — local registry (127.0.0.1:5500,
  pinned registry:2.8.3); the Odoo image and ALL 8 portal images built,
  pushed, and **booted strictly by digest**; the nine ladder composes'
  PENDING-FIRST-BUILD markers replaced by the pinned digest. The verifier now
  checks local-registry digests too: **81/81 refs, 0 failed, 0 pending**
  (also caught + fixed a corrupted tempo digest and the unpinned `node:22`
  base, now digest-pinned via ARG default resolution).
- **Edge TLS** — dev CA + gateway certificate; Kong serves 8443 with
  `Verify return code: 0` against the committed CA; HSTS/nosniff/DENY verified
  over HTTPS.
- **Warehouse measurements** — the analytics read replica was restored from a
  primary snapshot; the sync now runs for real end-to-end (123 branches + 200
  customers + 500 orders reconciled with checksums, 0 synthetic rows; three
  real bugs found on the way: the extractor queried a nonexistent `res_branch`
  table, the ClickHouse INSERT lacked auth headers and silently fell back to
  SQLite, and the collector's 202-Accepted was counted as failure).
  **NFR-039 measured: p95 = 0.178 s** (budget 10 s).
- **Telemetry load measured for real** — the load tool now POSTs: sustained
  50k/min window 16,750/16,750 accepted, peak 75k/min 12,500/12,500,
  POST p95 ≈ 31 ms (budget 100 ms).
- **OTel/correlation-id propagation** — new `libs/py/fix_telemetry/http.py`
  (FastAPI middleware + stdlib-handler helpers) wired into dispatch-scoring,
  ml-gateway, notification-dispatcher, identity-lifecycle; verified live
  (200 + correlation-id + traceparent on responses). The kafka client import
  became lazy so stdlib-only images still boot.
- **Odoo production-profile boot smoke** — `--profile prod` conf booted:
  login 200, db-selector 404, `db/list` AccessDenied, wrong-master-password
  POST creates nothing; workers=4, proxy_mode, dbfilter.
- **Compose hygiene** — the final host-port collision (mlflow vs OSRM on
  5000) resolved; 17 compose files now expose 78 distinct ports, 0 clashes.
- **Full battery re-run**: estate **4,985 passed / 0 failed**; fitness 0
  failures; whole-repo ruff clean; visual 36/36, headers 24/24, API 67/67.

Gate verdicts remain honest: G0a/G0b/G9 stay RED-OPEN **only** on genuine
human items (B-05b Steering CR approval, G2-10/G9-10 sign-offs) — those are
operator actions, listed in the RELEASE-CHECKLIST, and will not be faked.

---

*Every number in this report comes from a tool run recorded in `docs/traceability/evidence/` or `tooling/gate/evidence/` on 2026-10-22/23, or is explicitly marked OPEN.*
