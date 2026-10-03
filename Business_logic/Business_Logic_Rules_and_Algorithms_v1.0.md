# 1000FiX ERP v2.0 — Business Logic, Rules & Algorithms
## Requirements vs. Current Codebase Status — Comprehensive Reference (v1.2)

**Project**: 1000FiX Services Ltd. ERP System v2.0 (Odoo 19 CE + Next.js portals + Flutter apps)
**Document date**: 2026-10-02 · **Codebase state**: end of Phase 4 + document-audit fixes (commit `869b941` + audit)
**Method**: (1) full survey of the requirements corpus — `project-guide-doc/` (RQ-001…RQ-010, DA-*, UX-*, SC-*), the 67-module specification estate in `1000fix_ERP_Module/03_Modules/` (**1,330 enumerated `BRU-*` business rules**), and IR-002 (architecture standards AS-01…AS-15, MIG-01…08, DoD-01…17, FF-01…37); (2) line-by-line inspection of the implemented code in `1000_fix_codebase/`; (3) targeted internet research on best practice for each algorithm domain (sources in §8); (4) **audit pass** — every status claim re-verified, a whole-tree relation-integrity scan added (§9).

**Revision v1.1 (audit)**: the audit found that §2.2's ✅ on SLA *fields* rested on two dangling model references — `fix.sla.policy` and `fix.diagnostic.node` were referenced by the service-order core but defined nowhere, which would crash Odoo's registry load. Both masters now exist (`fix_sla_policy.py`), the class of defect is permanently blocked (relation-integrity scan in the model-registry check), and §2.2/§4 below are corrected accordingly. Full audit record in §9.

**Status markers**: ✅ applied in code · 🟡 partially applied (see notes) · ⬜ required, not yet built

---

## 1. The rule estate and how rules are governed

The governing instrument is **RQ-009 Business Rules Specification** (`project-guide-doc/01_Requirements_Engineering/`). Every business rule in the estate:

- carries a `BRU-<DOMAIN>-nn` identifier owned by exactly one module;
- is classified **H (hard block)**, **C (controlled)** or **A (advisory)**;
- names an owner (Ops Director, CFO, Quality Manager…);
- declares its **enforcement layer**: Odoo constraint (model layer, AS-09 — never in views), API validation, offline-device validation, or manual procedure;
- has a test obligation scaled to classification (H rules require negative tests — DoD-07).

**Known estate defects to respect when implementing** (RQ-009 §6):

| Defect | Impact | Ruling |
|---|---|---|
| `BRU-ECM-01…-10` double-allocated between M12 marketplace and M38 e-commerce rules (RQA-27) | A developer implementing "BRU-ECM-01" may implement the wrong hard block | M38 keeps the prefix; catalogue marketplace rules move to `BRU-MKP-nn` with tombstones |
| `BRU-BIL-*` (7) and `BRU-SCM-*` (5) are orphans under retired codes | Dead rules | Do not implement; disposition at catalogue revision |

**Rule volume by domain (top of 67 domains)**: FIN 26, FXA 26, TRE 26, TAX 26, APE 26, REV 26, ARB 25, FPA 25, AIM 25, BPA 25, SEC 25, TRF 24, INV 24, DAT 24 … full inventory extractable via the pattern `^\| BRU-…-nn \|` over `1000fix_ERP_Module/03_Modules/**/*.md`.

---

## 2. Domain-by-domain business logic

### 2.1 Service order lifecycle (M01 — `BRU-SRM-*`)

**Required rules**

| Rule | Class | Statement |
|---|---|---|
| BRU-SRM-01 | H | No service order without an identified device; unregistered devices registered at intake |
| BRU-SRM-02 / WTY-01 | H | Warranty-type order only if warranty active at request date |
| BRU-SRM-03 | H | AMC-type order only if device on an active contract's covered-asset list |
| BRU-SRM-04 | H | Cannot reach *Ready* without a passed QC checklist |
| BRU-SRM-05 | H | No invoice for an order that is not *Delivered* |
| BRU-SRM-06 | C | Same device + fault within 30 days → auto-flag as rework and link |
| BRU-SRM-07 | H | Estimates **> BDT 5,000** require documented customer approval before work |
| BRU-SRM-08 | H | Estimates **> BDT 25,000** require customer **and branch-manager** approval |
| BRU-SRM-09 | H | Cannot assign a technician lacking current brand certification |
| BRU-SRM-10 | C | Gold/Diamond members get priority-1 SLA automatically |
| BRU-SRM-12 | H | Beyond-economic-repair needs photos + second technician confirmation |
| BRU-SRM-13 | H | Expired estimate re-issued, never extended |
| BRU-SRM-15 | C | SLA clock suspended only by approved hold reason; auto-resume |
| BRU-SRM-16 | C | Uncollected 30 days after *Ready* → abandonment process with statutory notice |
| BRU-SRM-17 | H | Before/after photos mandatory on warranty orders; no close without them |
| BRU-SRM-18 | H | **Independent QC (second person) mandatory above BDT 25,000** |
| BRU-SRM-19 | C | Reopen only within repair-warranty window; linked as rework |
| BRU-SRM-20 | H | Customer data-access notes captured only with explicit consent; **purged at handover** |

**Algorithms required**

1. **Single-source state machine** (AS-06): 14 states — draft → intake → diagnostic → estimate_pending → estimate_sent → awaiting_approval → approved → in_repair → qc_pending → qc_failed → ready → delivered → closed, plus cancelled; transitions declared **once** and validated on every write.
2. **Rework detection**: on create, search same device + fault category with `create_date >= now − 30 days`; link and flag.
3. **Approval matrix routing**: 5k / 25k thresholds → single vs dual approval activities.

**Codebase status**

| Item | Status | Evidence |
|---|---|---|
| 14-state machine, `VALID_TRANSITIONS`, enforced in `write()` + `_validate_transition()` | ✅ | `addons/domain/a_service_delivery/cd_service_order/models/fix_service_order.py:13-45,136-156` |
| Device required (`device_id` required=True) | 🟡 | intake requires device; auto-registration flow at intake not yet wired |
| QC gate before *ready* | ✅ | `action_ready()` refuses without a checklist and with any unpassed one (BRU-SRM-04; 19-test suite `test_business_gates.py`) |
| Invoice gating (not Delivered) | ✅ | `cd_billing_engine.from_closed_service_order()` raises on non-closed orders (BRU-SRM-05) |
| Warranty-active gate | ✅ | `order_category` + `_check_warranty_gate()` on create — warranty orders need device warranty_status `active` (BRU-SRM-02) |
| AMC contract gate | ⬜ | contracts are M36 (Phase 7) |
| Approval thresholds 5k/25k | ✅ | `APPROVAL_THRESHOLD=5000` / `DUAL_APPROVAL_THRESHOLD=25000`; `action_approve()` demands documented customer approval above 5k and + manager above 25k; `action_manager_approve()` is the ordered second key (BRU-SRM-07/08) |
| Rework 30-day flag | ✅ | `_flag_rework()` on create — same device within 30 days (cancelled excluded), linked via `rework_of_id` (BRU-SRM-06) |
| Technician certification gate | ⬜ | M21 certification data + gate not yet built |
| Photo evidence gates | ⬜ | attachments exist via cd_document_core; gates not enforced |
| Data-access notes purge at handover | ⬜ | — |

### 2.2 SLA engine (M01 §SLA, M30 calendars)

**Required rules & algorithms**

- Two clocks per order: **response** (assignment → first action) and **resolution**; targets per SLA policy × service type × priority.
- Clocks run on **business time** from the branch's `fix.working.calendar` (Asia/Dhaka, holidays incl. moon-dependent dates); suspension only by approved hold reason (BRU-SRM-15); auto-resume.
- Escalation ladders on breach/near-breach (NT-020 templates, `sla_breached` event).
- Best practice (research, §8): persist **time-remaining snapshots**, not recomputation from a mutable calendar — a calendar edit must never retroactively change a running SLA; warning + failure thresholds; pause/resume events recorded.

**Codebase status**: 🟡 fields and **policy master** complete and event-ready (`sla_policy_id` → `fix.sla.policy` with response/resolution targets per service type × priority and the escalation template link; `sla_response_deadline`, `sla_resolution_deadline`, `sla_response_at`, `sla_clock_paused`; response timestamped on entering `in_repair`; diagnostic path master `fix.diagnostic.node` with terminal-node fault codes and cycle protection), the **computation engine is not built** — roadmap places it in `services/sla-engine/` (Phase 5 companion), consuming `fix.working.calendar` lines/holidays. *(v1.1: the SLA policy and diagnostic-tree masters were added by the audit — they had been referenced but undefined.)*

### 2.3 Estimates, pricing & VAT (M01 estimates; M11 pricing; M19/M56 tax)

**Required rules**

- Estimate versioning: expired estimates re-issued as a **new version**, never extended (BRU-SRM-13); part-approval of estimate lines; validity window.
- **All prices `fields.Monetary` with explicit currency** (AS-10/FF-22) — never Float.
- Bangladesh VAT: **standard rate 15%**; VAT shown separately; **Mushak 6.3** tax-invoice format with supplier & buyer name/address/**BIN**, description, qty, unit price, discount, VAT (input-tax credit denied without it); VAT invoice mandatory when supply value exceeds **Tk 25,000**; monthly return (Mushak 9.1) by the 15th.
- Pricing engine (M11, Phase 7): list × contract × tier × campaign with effective dating.

**Codebase status**

| Item | Status | Evidence |
|---|---|---|
| Estimate line model, version increment, `action_revise()` copies as new version | ✅ | `fix_estimate.py` (`version`, `action_revise`) |
| Totals compute: parts + labour − discount; `vat_amount = subtotal × vat_rate/100`; grand total | ✅ | `fix_estimate.py:49-58` |
| VAT default 15% | ✅ | `vat_rate` default 15.0 |
| Monetary everywhere (no Float money) | ✅ | FF-22 blocking check green |
| Mushak 6.3 invoice rendering + BIN fields | ⬜ | Phase 6 (statutory reports); job-card report exists, invoice does not |
| Dual-approval thresholds | ⬜ | see §2.1 |

### 2.4 QC & rework (M01 QC; M31 workshop)

**Required rules**: BRU-SRM-04/18 (above); WSR-04 (L2/L3 repairs require independent QC); WSR-07 (burn-in never shortened); WSR-11 (level revision raising cost above approved estimate → re-approval); WSR-10 (internal rework counted separately, never hidden).

**Codebase status**: ✅ `fix.qc.checklist` with `item_ids`, `all_passed` compute, `action_complete()` refusing empty/failed lists, and `@api.constrains` blocking inspector == repairing technician (BRU-SRM-18). 🟡 the "above BDT 25,000" conditionality is a help-text statement, not enforced (constraint fires whenever both set — stricter than the rule, acceptable but should become conditional when estimate totals link in). ⬜ burn-in protocols and level revisions (M31, Phase 5).

### 2.5 Warranty & protection products (M40 `BRU-WTY-*`)

Key rules: claim auto-created within 5 min of warranty delivery (WTY-03); claim must pass brand rule-set before submission (WTY-04); rate-card version pinned to **service date** (WTY-05); submission-window escalation; **claim and write-off approval are segregated** (WTY-07, SoD-11); evidence of parts/labour or claim blocked (WTY-09); protection-product waiting period rejection (WTY-12); excess collected before fulfilment (WTY-13); reserves at issue, released on settlement (WTY-15); repair-warranty returns charged to 1000FiX only (WTY-16).

**Codebase status**: 🟡 `fix.warranty` model (type, start/end, deductible, status) + device warranty-status compute + ownership transfer history. ⬜ claims engine, brand rule-sets, rate cards, protection products — M40 is a later wave.

### 2.6 Device & customer asset registry (M17)

**Required**: serial/IMEI uniqueness (device identified once, forever); ownership transfers as permanent audit records; full device history never deleted; identity format validation (IMEI 15 digits, MAC format).

**Codebase status**: ✅ SQL uniqueness on serial/IMEI, format constraint, computed display name, `_compute_warranty_status()`, `action_transfer_ownership()` writing history + emitting event, `add_history()` API, create/write hooks that stamp history.

### 2.7 Branch & front desk (M04 `BRU-FRD-*`)

**Required rules**

| Rule | Class | Statement |
|---|---|---|
| FRD-01 | H | No new shift while a previous shift is unclosed |
| FRD-02 | H | Shift cannot close without counted cash |
| FRD-03 | H | Variance beyond tolerance → branch-manager approval before close |
| FRD-04 / FIN-02 | H | Cash receipts **> BDT 50,000** require customer NID |
| FRD-05 | H | No handover without collector identity verification |
| FRD-06 | H | A device cannot occupy two storage locations |
| FRD-07 | C | Gold/Diamond members get priority queue placement |
| FRD-08 | C | Token recallable once before no-show |
| G1-02 (gate) | — | Walk-in intake ≤ 3 minutes (timed fields already on the model) |

**Codebase status**: ✅ token queue with branch-daily sequence + state flow (waiting→called→serving→completed/no-show/cancelled) + events; ✅ cash shift with computed `expected_closing = opening + payments − refunds − advances`, counted close, variance, states open→counting→reconciled/discrepancy. 🟡 token sequence uses max-search (`order="token_number desc"`) — safe at branch scale but a race under concurrent intake; move to a sequence/`ir.sequence` or `SELECT … FOR UPDATE` counter. ⬜ FRD-03 manager approval step, FRD-04 NID capture (NID itself routes to Z4 per §2.10), FRD-05 collector verification gate, FRD-06 storage locations.

### 2.8 Party master, dedup & MDM (M33, M64 `BRU-MDM-*`)

**Required rules & algorithms**

- **One party, many roles** — customer/seller/vendor/corporate-contact are roles on one `res.partner`, never duplicate masters (the M33 design rule; enforced in code by constraint).
- Identity documents (NID/passport/TIN) are **residency-classified** — value in Z4, pointer in the regional store.
- **Dedup ladder** (migration ETL-1 + `fix.dedup.rule`): normalized phone (8801XXXXXXXX) exact → block; email exact → block; fuzzy name (edit distance ≤ 2) + same district → **flag for steward review**, never auto-merge below the confidence threshold (BRU-MDM-10).
- **Survivorship for golden records** (M64): governed attributes change only through approved change requests (BRU-MDM-01 — UI, API, imports and scripts all blocked); proposer ≠ approver (MDM-06); impact analysis before approval (MDM-07); bulk changes all-or-nothing (MDM-08); emergency changes auto-revert in 24 h without retrospective approval (MDM-09); merges notify every referencing module (MDM-12); retired reference values resolvable forever (MDM-13); hierarchies acyclic, no orphans (MDM-18).
- Best practice (research §8): deterministic matching on strong identifiers + probabilistic scoring on names/addresses; survivorship rules defined **before** any merge; source-trust hierarchy ("system of record wins") preferred over attribute-level complexity; xref table keeps every source key pinned to the golden ID.

**Codebase status**: ✅ `fix.party.role` (multi-role, duplicate-role SQL constraint), `res.partner` extension (`name_bn`, `preferred_language`, role/consent links), `fix.identity.document` on `residency.mixin`, `fix.dedup.rule` engine-config model, `fix.mdm.change.request` + golden/match rules (cd_mdm_core). ⬜ the matching/survivorship **execution engine** (auto-merge confidence, impact analysis, change-request enforcement on `fix.*` governed models) is Phase 5+ (M64 completion slice).

### 2.9 Consent & notification policy (M33 consent; M27/NT set)

**Required rules** (from NT-001/002/003 — fully transcribed in the dispatcher):

- One event → one delivery decision (CH-01..06); SMS is reach, push is speed, email is record, in-app is reference.
- Consent classes route SMS lanes: **transactional/security = masking sender "1000FiX"**; **marketing = non-masking numeric sender, never masking** (BD-01/02); promotional copy never carries the masking signature (BD-03); BTRC-listed aggregators only (BD-04).
- **DND**: promotional never reaches DND numbers; transactional exempt, 24/7.
- Windows (Asia/Dhaka): security/transactional 24/7 (QH-01); service 08:00–21:00; marketing 10:00–20:00; held-not-dropped (QH-02); stale-held discarded (QH-03).
- Frequency caps rolling 7 days: service 3, marketing 2, **all non-transactional combined 4**.
- Fallback ladder (NT-001 §4): SMS undeliverable → retry once → next channel; push fail → SMS for act-now events; email bounce → flag + SMS; **all channels fail → operational task, never silent drop**; IP-09 P0 fallback register.
- Consent is auditable: grant needs proof; withdrawal keeps the record forever; absence of record ≠ consent.
- KPIs: delivery rate, p50/p95 latency, channel mix, opt-out rate; OTP excluded from KPIs.

**Codebase status**: ✅ **fully implemented** in `services/notification-dispatcher` (router, policy, channels dry-run default + SSRF-guarded + env-only credentials, retry/DLQ/task, IP-09 register, KPIs) with 37 unit tests; machine-readable registry of all 26 NT packs (Bengali + English); runtime config mirrored in `fix.notification.config`; `fix.consent` model with proof constraint and withdrawal API. The remaining gap is runtime wiring (`fix_events.consume` loop) which needs the Odoo runtime.

### 2.10 Data residency & privacy (Z4 / NFR-086a; PDPA)

Rules: classified personal data (NID/passport/TIN/health notes) lives only in the Bangladesh-resident Z4 store; regional DB holds a `residency_ref` pointer, never the value; **bulk loaders must use the same residency path** (MIG-06 — "the compliance breach the architecture exists to prevent, at scale, on day one"); `libs/py/fix_residency` is the only client (FF-09, blocking); write-time ORM enforcement via `residency.mixin`; events never carry classified values; data-access notes purged at handover (BRU-SRM-20).

**Codebase status**: ✅ mixin + client + FF-09 blocking scanner (0 bypasses) + synthetic local stub; migration ETL specs bind MIG-06. ⬜ BRU-SRM-20 purge job.

### 2.11 Inventory (M15 `BRU-INV-*` — Phase 5)

Key rules to build: ownership classes (brand-consignment usable **only** on that brand's warranty jobs, never in valuation; customer-supplied only on that customer's job; refurbished/harvested **never on warranty work**); no negative on-hand; inspection/blocked stock unreservable; goods available only after inspection; **counter ≠ approver on counts (SoD)**; adjustments reason-coded with authority matrix (≤25k Inventory Manager, above CFO; write-off >25k CFO); van stock reconciled per shift with variance blocking next issue; serial capture mandatory on serial-controlled parts; unreceived/already-consumed serials quarantined; landed-cost provisional until M44 publishes; rental pool not consumable; count variance above threshold → recount.

**Algorithms & best practice** (research §8): **ABC (or ABC-XYZ) cycle counting** — A items counted most frequently by value/movement; ≥95% record accuracy target (G2 criterion) sustained by daily counts + root-cause analysis on variances rather than annual wall-to-wall counts; perpetual quant-level reservation.

**Codebase status**: ⬜ module not started (Phase 5 P05-M01). Design hooks exist: catalogue ↔ stock bridge, `stale_discard` config pattern, OU isolation.

### 2.12 Field service dispatch & routing (M02 — Phase 5)

Rules: certification-gated assignment (BRU-SRM-09, WSR-02); SLA-aware priority (Gold/Diamond priority-1); skills × location × availability matching; geofence/zone awareness; **route optimization must reduce measured travel time ≥ 15% vs baseline** (G2-03) — measured, not estimated.

**Algorithms & best practice** (research §8): dispatch is a **continuous scoring/optimization loop**, not one-shot assignment — score candidates on (certification hard-gate) + (SLA risk) + (travel time from OSRM `/table` matrix) + (workload balance); routes solved as **VRPTW via VROOM over OSRM matrices** (vroom-express pattern; Timefold is the alternative worth comparing); treat routing as live re-optimization through the day.

**Codebase status**: ⬜ `services/dispatch-scoring` and `services/route-orchestrator` are scaffolded empty; Traccar/OSRM/VROOM containers pinned in compose (integration profile).

### 2.13 The shared offline engine (ADR-024 — Phase 5, "hardest requirement")

Requirement: **24-hour offline operation with zero data loss** for technician/rider/auditor apps; one Dart engine shared by all three; server-authoritative.

**Best-practice algorithm** (research §8): server remains authoritative (devices repairable by full re-sync); **idempotent operation queue** per device with server-assigned timestamps; **version vectors to detect concurrent writes** (never device-clock LWW — it silently discards concurrent writes); field-level conflict policy: server-wins for governed fields, merge for operational notes, prompt for genuine business conflicts; every offline write replays through the same business rules (rule enforcement on-device for H rules that must block offline, server re-validation on sync). Codebase hooks that already align: `idempotency_key` uniqueness on service orders (DI-04), transactional outbox (AS-08) for replay ordering.

**Codebase status**: ⬜ engine not started; event/outbox/idempotency substrate ready.

### 2.14 Loyalty (M10 `BRU-LOY-*` — Phase 5)

Rules: privilege discounts on **labour only**; auto-apply where eligible; append-only points ledger (compensating corrections); auto-reversal on cancellation/refund/chargeback; **balance never overdrawn under concurrency** (atomic decrement); points never convertible to withdrawable cash; stacked-discount cap; self-referral and circular-household referral blocked; **points liability + breakage computed every period and published to M19; membership-fee revenue recognized over the period**.

**Best practice** (research §8, IFRS 15/ASC 606): points are a separate performance obligation — defer part of the transaction price at sale; `Liability = outstanding points × (1 − breakage rate) × value per point`; re-estimate breakage from redemption history each period.

**Codebase status**: ⬜ not started (Phase 5 P05-M08).

---

## 3. Cross-cutting algorithms (estate-wide)

| Algorithm | Requirement | Status | Evidence |
|---|---|---|---|
| **Relation-target integrity** | AS-14 companion (added by audit) | ✅ | every `Many2one/One2many/Many2many` target must resolve to a defined or core model — enforced in the model-registry fitness check after `fix.sla.policy`/`fix.diagnostic.node` shipped dangling |
| **State validation in one place** | AS-06 | ✅ | `SERVICE_ORDER_STATES` + `VALID_TRANSITIONS` enforced in `write()`; same pattern mandated for every lifecycle model |
| **Transactional outbox** | AS-08 | ✅ | `fix.event.outbox.emit()` same-transaction; `fix_events` sole client (FF-28); replay-from-timestamp |
| **Idempotent create** | DI-04/DI-05 | ✅ | `idempotency_key` SQL-unique on service order + consumer dedup design |
| **Residency write-interception** | NFR-086a | ✅ | `residency.mixin._extract_classified()` on create/write/read |
| **Monetary discipline** | AS-10 | ✅ | FF-22 blocking |
| **Sequence allocation** | branch token numbers | 🟡 | max-search; recommend `ir.sequence` per branch |
| **Computed stored fields** | Odoo practice | ✅ | totals, warranty status, `all_passed` with correct `@api.depends`; store where searched/grouped |
| **Constraint layering** | Odoo practice | ✅ | SQL constraints for invariants (uniqueness), `@api.constrains` for cross-field rules, model methods for actions (AS-09: nothing in views — FF-checked) |
| **OU isolation** | AS-03 | ✅ | `operating_unit_id` + record rules; config/master exemptions documented in the registry check |
| **Design tokens → all runtimes** | DSY-01 | ✅ | generator + CFM-01..05 conformance |

---

## 4. Applied-vs-required summary matrix

| Domain | Rules required | Applied | Partial | Not built |
|---|---|---|---|---|
| Service-order lifecycle | 16 core SRM | state machine, device-required, QC-independence | warranty gate | QC-ready gate, approvals 5k/25k, rework flag, photo gates, certification gate, purge-on-handover |
| SLA | clocks, calendars, escalation | fields + response stamp | — | computation engine, pause/resume enforcement, escalations |
| Estimates/pricing/VAT | versioning, VAT 15, Mushak 6.3 | versioning, totals+VAT compute, monetary | — | dual approvals, Mushak invoice, pricing engine |
| Warranty/protection | 22 WTY | model + status + transfer | claim-side absent | claims engine, rate cards, protection products |
| Device registry | uniqueness, history | all core | — | — |
| Front desk | 9 FRD + 3-min intake | token queue, cash reconciliation math | token race | variance approval, NID>50k, collector ID, storage, recall-once |
| Party/MDM | 22 MDM + dedup | roles, consent, dedup-config, change-request models | matching engine | survivorship/impact/merge execution |
| Notifications | NT-001/002/003 full set | **entire policy engine** | runtime loop needs Odoo | — |
| Residency/privacy | Z4-only, MIG-06 | mixin + client + scanner | — | SRM-20 purge |
| Inventory | 24 INV | — | — | all (Phase 5) |
| Dispatch/routing | certification, SLA-aware, VRP | — | scaffolds + containers | all (Phase 5) |
| Offline engine | 24 h, zero loss | substrate (outbox/idempotency) | — | engine (Phase 5) |
| Loyalty | 14 LOY | — | — | all (Phase 5) |

---

## 5. Codebase status snapshot (as audited)

- **13 Odoo modules**: 4 domain (device registry, service order, front desk, CRM ext) + 9 platform (entity config, rbac, outbox, party, catalogue, mdm, document, employee, design tokens).
- **Six W1 workspaces** role-gated under the portal shell (UX-002 §6.2); FF-27 portal contract live.
- **Services**: notification-dispatcher complete (37 tests); local residency stub; dispatch-scoring/route-orchestrator/pricing-engine/telemetry scaffolds.
- **Quality**: fitness suite **12 PASS / 0 FAIL** (incl. FF-09 residency bypass scan, FF-16 CD membership, FF-23 tests-present, FF-25 bn_BD 100% across all 13 modules, FF-27 portal+view integrity); G1 gate **2 PASS / 10 CONDITION / 0 FAIL** (CONDITION = runtime/human demonstrations); view-field integrity and repo-format audits green; a11y harness (axe-core WCAG 2.2 AA + Bengali expansion) typechecked with pinned toolchain.
- **Open governance items**: 2 Change Board CRs (design-token register row; NFR-080 restatement); 4 Mimosa medium findings on Phase-2 tooling scripts awaiting user review; Bengali counterparts pending for 110 UI-copy keys / 266 content files (programme content backlog).

---

## 6. Prioritized recommendations (by risk × readiness)

1. **Close the BRU-SRM hard-gate set inside the existing models** (small, high-value): QC-passed gate before `ready`; estimate-approval routing at 5k/25k; warranty-active gate on warranty-type creation; QC-independence conditional on >25k. All are constraints/actions in models that already exist.
2. **Build the SLA engine** (`services/sla-engine`) on `fix.working.calendar` with time-remaining snapshots and pause/resume events — required before G1's SLA demonstration and consumed heavily in Phase 5.
3. **Harden the token sequence** (`ir.sequence` per branch) and add FRD-03/04/05 gates (variance approval, NID>50k → residency, collector identity) — all front-desk closures for G1-02's 3-minute demonstration.
4. **Phase 5 build order** (per roadmap and §2.11–2.14): M15 inventory (ownership classes + ABC cycle counting) → geospatial → dispatch scoring + VROOM/OSRM route orchestrator → offline engine started early (longest pole) → technician app → P01 portal → loyalty with IFRS-15 liability math.
5. **MDM execution engine** when M64's completion slice lands: deterministic-first matching ladder, steward queue, survivorship-before-merge discipline.
6. **Mushak 6.3 invoice** in Phase 6 with BIN on both parties and VAT-separate lines; the >Tk 25,000 invoice-mandatory threshold conveniently matches the SRM-08 approval threshold — implement the two gates together.

---

## 7. Engineering best practices the codebase already follows (keep enforcing)

- Business logic in the model layer only (AS-09) — views/controllers carry none (FF-checked).
- SQL constraints for invariants; Python constraints for cross-field; state transitions via validated action methods, never free `state=` writes.
- Stored computed fields only where searched/grouped/sorted, with complete `@api.depends` (Odoo performance practice).
- Event-driven integration with same-transaction outbox; consumers idempotent.
- Config-driven policy (notification windows/caps, dedup rules, feature flags) — data, not code.
- Negative tests for every H rule (DoD-07) and blocking fitness functions at pre-merge.

## 8. External references (research)

- Field-service dispatch: [ServiceNow Scheduling & Dispatch best practices](https://mynow.servicenow.com/now/best-practices/assets/scheduling-dispatch-process-guide) · [NetSuite dispatch tips](https://www.netsuite.com/portal/resource/articles/erp/dispatch-tips.shtml) · [Salesforce dispatch management](https://www.salesforce.com/service/field-service-management/what-is-dispatch-management) · [SaberTask FSM best practices 2026](https://www.sabertask.com/articles/field-service-management-best-practices)
- SLA business-hours: [Dynamics 365 SLA time scenarios](https://learn.microsoft.com/en-us/dynamics365/customer-service/administer/sla-time-scenarios) · [ServiceNow schedule/pause recalcs](https://www.servicenow.com/community/servicenow-ai-platform-blog/schedule-changes-affect-business-pause-duration-calculations/ba-p/2266387) · [business-hours due-date algorithm (SO)](https://stackoverflow.com/questions/27682810/calculating-due-date-using-business-hours-and-holidays)
- MDM/golden record: [Profisee survivorship](https://profisee.com/blog/mdm-survivorship) · [Pipecode golden records for engineers](https://pipecode.ai/blogs/master-data-management-mdm-data-engineers-golden-records-survivorship-rules) · [IBM survivorship docs](https://www.ibm.com/docs/en/product-master/12.0.0?topic=features-data-survivorship-feature)
- Bangladesh VAT/Mushak 6.3: [PwC Bangladesh other taxes](https://taxsummaries.pwc.com/bangladesh/corporate/other-taxes) · [NBR compliance guide](https://nbr.gov.bd/taxtypes/vat-compliance-guides/details/8/eng) · [1stopVAT Bangladesh](https://1stopvat.com/international-vat-guides-bangladesh) · [VATupdate Bangladesh e-invoicing deck](https://www.vatupdate.com/wp-content/uploads/2026/07/Bangladesh_E-Invoicing_Deck.pdf)
- Offline sync/conflict resolution: [Back4App offline-first sync](https://www.back4app.com/glossary/offline-first-data-sync) · [Android offline-first guide](https://developer.android.com/topic/architecture/data-layer/offline-first) · [LWW vs vector clocks vs CRDT](https://naveedkarimi.com/learn/courses/distributed-systems-fundamentals/10-conflict-resolution-last-write-wins-vector-clocks-and-crdts.html) · [vector clocks detect, don't resolve](https://scaledojo.dev/blogs/vector-clocks-and-conflict-resolution-tracking-causality-in-distributed-systems)
- VRP/routing: [VROOM](https://github.com/vroom-project/vroom) · [vroom-project.org](http://vroom-project.org) · [OSRM+VROOM on GCP guide](https://medium.com/@calroughan/a-beginners-guide-to-installing-osrm-and-vroom-on-gcp-28fbcf1f7857) · [HeiGIT VROOM+ORS](https://heigit.org/solve-routing-optimization-with-vroom-openrouteservice-2)
- Cycle counting: [Kardex ABC cycle counting](https://www.kardex.com/en-us/blog/cycle-counting-and-stock-audits) · [CPCON accuracy benchmarks](https://cpcongroup.com/insights/article/how-to-run-warehouse-cycle-counts) · [RF-Smart cycle counting guide](https://www.rfsmart.com/resources/inventory-cycle-counting-guide)
- Loyalty accounting: [IFRS 15/ASC 606 points liability](https://lji.io/guides/points-liability-accounting) · [PwC breakage viewpoint](https://viewpoint.pwc.com/dt/us/en/pwc/accounting_guides/revenue_from_contrac/revenue_from_contrac_US/chapter_7_options_to_US/74unexercised-rights_US.html) · [Phoenix Strategy liability formula](https://phoenixstrategy.group/blog/loyalty-program-accounting-best-practices)
- Odoo practices: [Odoo 19 compute/onchange tutorial](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/08_compute_onchange.html) · [stored computed fields guide](https://www.dasolo.ai/blog/odoo-data-api-5/odoo-stored-computed-field-guide-118) · [store=True tradeoffs](https://www.cybrosys.com/blog/how-stored-vs-non-stored-computed-fields-impact-odoo-performance)

---

## 9. Audit record (v1.1)

**v1.2 (post-Phase-6 sync audit)**: a frontend↔backend synchronisation audit found and fixed four unenforced business gates — BRU-SRM-04 (QC before Ready), BRU-SRM-07/08 (estimate approval thresholds 5k/25k with the ordered second key), BRU-SRM-02 (warranty-active at creation via the new `order_category`), BRU-SRM-06 (30-day rework flag with linkage) — plus the frontend-surface gaps (MDM match/golden rules and party-hierarchy views added). All 19 gate tests green; status matrix above updated to ✅.

The v1.0 document was audited claim-by-claim against the code. Verified correct: the 67-module and 1,330-rule counts (independently recomputed), every quoted `BRU-*` statement (verbatim against the module specs), the 37-test dispatcher count, the 15% VAT default, and the ✅ items spot-checked (state machine, QC-independence constraint). Three findings, all fixed:

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | **Blocker** | §2.2 marked SLA fields ✅ while `sla_policy_id` pointed at **`fix.sla.policy`, which was defined nowhere** — Odoo's registry load would crash on `cd_service_order` | `fix.sla.policy` written (`fix_sla_policy.py`): response/resolution targets per service type × priority, escalation-template link, positive-and-ordered target constraints, chatter + company |
| 2 | **Blocker** | Same class: `fix.work.order.diagnostic_tree_id` pointed at undefined **`fix.diagnostic.node`** | Diagnostic decision-tree model written: parent/child nodes, computed terminal flag, fault codes on terminals only, cycle protection |
| 3 | **Process** | No checker covered relation-target integrity — FF-27 validated action `res_model`s but not field-level relations; and the model-registry checker's *failure* print path crashed on mixed violation shapes (never exercised since Phase 3) | Relation-integrity scan added to `check_model_registry.py` (negative-tested: injected dangling target fails, clean tree passes); failure printer fixed to handle both shapes |

Post-fix state: bn_BD.po re-closed to 100% (57 strings in cd_service_order), fitness **12 PASS / 0 FAIL**, view-integrity (49 models) and repo-format audits green, G1 gate unchanged, whole-tree dangling scan reports **none**.

---

*Maintained alongside the codebase; update the status matrix at each phase gate. Rule counts reproducible by scanning `1000fix_ERP_Module/03_Modules/**/*.md` for `^\| BRU-…` rows.*
