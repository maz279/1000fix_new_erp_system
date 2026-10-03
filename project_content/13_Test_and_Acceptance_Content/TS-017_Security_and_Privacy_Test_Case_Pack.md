---
id: TS-017
title: Security and Privacy Test Case Pack
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Security with QA Lead
author: Security Lead with QA Lead, Chief Data Officer and Solution Architect
reviewers: [CTO, Chief Data Officer, Security Lead, Solution Architect, Legal Counsel, CFO delegate, HR Manager]
approver: CTO with Chief Data Officer
content_class: E
purpose: >
  The verification that access control, data scope, consent, residency and audit logging actually
  hold — role by role, portal by portal, field by field, tier by tier. Unverified row-level security
  is the most damaging silent defect a twelve-portal estate can carry: a seller who can see another
  seller's payout, a branch manager who can read another branch's cash, or a corporate user who can
  reach another company's assets produces no error, no alert and no complaint until an outsider
  notices. Since the Personal Data Protection Act 2026 came into force, that outcome is a notifiable
  breach with a penalty attached, not an embarrassment.
traces_to: [05-04, 05-04 §2, 05-04 §3, 05-04 §4, 05-04 §5, 05-04 §6, 05-04 §8, 05-04 §9, 05-04 §10, 05-05, 05-06 §4, 05-06 §6, 05-06 §6.3, 05-06 §6.4, 05-06 §11, 06-02 §4, M06, M24, M29, M60, M62, M65, LG-012, MD-009, MD-012, NT-007, TS-001, TS-002, TS-005, TS-010, TS-011, TS-013, TS-018]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1 38 roles; §2 portal access matrix (38 × 12); §3 module permission matrices with (o)/(b)/(z)/(a) scopes; §4 data isolation tiers T0–T5 with objects per tier; §5 field-level permissions, 13 field groups; §6 SOD-01…SOD-12; §8 EA-01…EA-12; §9 access lifecycle with the one-hour revocation and 24-hour orphaned-account controls; §10 Role Definition-of-Done criterion 6 — negative tests prove the role cannot see or do what it must not
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §4 Security NFR-011…015 and NFR-061…072; §6.3 Personal Data Protection Act 2026 obligations NFR-090…099 with the National Data Management Authority as regulator and penalty exposure to BDT 50 lakh registered as risk RSK-032; §6.4 split-residency architecture NFR-086, NFR-086a/b/c with the residency-classified field list; §11 Security level — SAST, DAST, dependency scanning on every build, penetration test annually
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §11 BRU-SEC-01…08, BRU-DMS-01…03, BRU-ADM-01…02, BRU-AIM-01…03; §12.5 AUT-058, AUT-060
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 1 G1-06 single sign-on and role framework operating for all delivered roles, G1-07 audit trail complete for all delivered objects, G1-09 zero critical or high security findings; §2.10 KPI-089, KPI-090, KPI-091
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# Security and Privacy Test Case Pack

| Item | Value |
|---|---|
| Test level | **Security** — `05-06` §11 level 9; plus the privacy verification the PDPA 2026 requires |
| Roles executing | Security Lead with QA; **and an account per `Rnn` under test** |
| Modules covered | All, through `M29`; `M06` `M24` `M60` `M62` `M65` carry specific obligations |
| Portals covered | All 12 — the matrix is the subject |
| Environment | `UAT` with production-equivalent role configuration; **never production** |
| Test data set | `TS-002` — synthetic only; reserved statutory identifiers; residency-classified fields present |
| Wave | W2 · **but `G1-06`, `G1-07` and `G1-09` are W1 criteria** — open item `O-01` |

> **Template conformance.** `TPL_Test_Script.md` at pack level. All six sections retained in order;
> §3 is organised by the register it derives from — matrix, tier, field, SoD, external, lifecycle,
> privacy, residency, audit — which is the addition and is justified, because each block's case count
> is a **derived** figure rather than an authored list.

> **Boundary with `TS-011`.** This pack proves the matrix holds **systematically and exhaustively**,
> from the inside. `TS-011` `UA-39` proves **experientially** that a real external user cannot reach
> another party's data by the routes a real user tries. **The counting of denied cells belongs here
> alone** (`CP-01`); `TS-011` §2.1 records the same boundary from the other side.

---

## 1. Traceability

### 1.1 The pack is derived, not authored

Every other pack in Category 13 was written by choosing scenarios. **This one is generated from
`05-04` by set arithmetic**, because the requirement is exhaustive: `05-04` §10 criterion 6 makes
*"negative tests prove the role cannot see or do what it must not"* a condition of releasing a role.
"Prove" over 38 roles and 12 portals is not a judgement call about which combinations matter.

| Register | Derivation | Cases |
|---|---|---:|
| §2 Portal access matrix | 38 roles × 12 portals = 456 cells; **77 granted, 379 denied** | **456** |
| §4 Data isolation tiers | 6 tiers × the objects listed per tier, one positive and one negative per tier per object class | **~72** |
| §5 Field-level permissions | 13 field groups × (entitled role, non-entitled role) | **26** |
| §6 Segregation of duties | 12 rules, each blocked at assignment | **12** |
| §8 External party access | 12 rules × the audiences each applies to | **~34** |
| §9 Access lifecycle | 7 stages, each with a timing assertion | **~14** |
| §6.3 PDPA 2026 | `NFR-090`…`099`, 10 obligations | **~28** |
| §6.4 Residency | `NFR-086`, `086a`/`b`/`c` × 7 classified field types | **~20** |
| `BRU-SEC-*`, `BRU-DMS-*`, `BRU-ADM-*`, `BRU-AIM-*` | 16 rules, each satisfied and breached | **32** |
| Audit trail (`NFR-014`, `G1-07`) | Every delivered object class | **~40** |
| **Total derived** | | **~734** |

**The 77/379 split is counted, not estimated.** `05-04` §2's matrix was enumerated cell by cell: 77
cells carry a granted marker and 379 do not. The 379 are the pack's core, because **a granted cell
fails loudly and a denied cell fails silently.**

### 1.2 Why the privacy half is new

`05-06` §6.3 opens with *"These requirements are new. The previous specification contained none of
them."* The Personal Data Protection Act 2026 (Law 63 of 2026) is in force, the regulator is the
National Data Management Authority, enforcement mechanisms activate around **13 May 2027 — inside
Wave 4**, and the penalty exposure is up to **BDT 25 lakh**, or **BDT 50 lakh** for a significant data
fiduciary, registered as risk `RSK-032`.

**That changes what this pack is for.** Access-control testing has always been about preventing
damage. Privacy testing is about *demonstrable compliance* with a statutory duty on a date inside the
programme — which means the evidence matters as much as the result, and `SC-12` follows.

### 1.3 Traceability obligation per case

| Field | Source |
|---|---|
| Register and rule | `05-04` §n, `05-06` `NFR-nnn`, or `BRU-*` — verbatim |
| Role and scope | `Rnn` and its `(o)`/`(b)`/`(z)`/`(a)` scope |
| Expected outcome | **Granted** or **denied**, stated before execution |
| Enforcement layer | Where the control must hold: model, record rule, field, or gateway |
| Evidence | The audit-log entry, the refusal, or the absent field in the payload |
| Statutory obligation | For privacy cases, the `NFR-090`…`099` obligation and its instrument |

---

## 2. Preconditions

### 2.1 Rules

| # | Rule |
|---|---|
| **SC-01** | **Every denied cell is tested.** All 379, not a sample. A sampled denial is an untested denial, and `05-04` §10 criterion 6 says "prove" |
| **SC-02** | **A refusal is verified at the enforcement layer, not at the interface.** `BR-STD-01` states that a rule bypassed by an API call is not a rule, so every denial is attempted **through the API as well as the UI** |
| **SC-03** | **Field-level restriction means the field is absent from the payload**, not hidden in the view. `PRU-P06-04` states the same rule for datasets: enforced by exclusion, never by hiding |
| **SC-04** | **Scope is tested by identifier, not by navigation.** A branch manager is given another branch's record identifier directly, and must be refused (`NFR-015`) |
| **SC-05** | **Every SoD rule is blocked at assignment time**, not detected in a later report (`NFR-064`, `05-04` §6) |
| **SC-06** | **Time-bounded controls are measured against the clock**: leaver access revoked within **one hour**, zero orphaned accounts beyond **24 hours**, rectification notified within **30 days** (`SL-24`) |
| **SC-07** | **Audit completeness is asserted as who, what, when, before and after** (`NFR-014`) — a log entry lacking the before-value does not satisfy `G1-07` |
| **SC-08** | **Every step-up-authentication trigger is tested by attempting the action without it** (`BRU-SEC-02`, `NFR-065`) |
| **SC-09** | **Residency is verified at write time**, by attempting to write a classified field to a non-resident store and being refused — not by inspecting where data ended up (`NFR-086a`) |
| **SC-10** | **Consent, withdrawal and every data-subject right are tested as behaviour**, end to end, with the resulting state verified in every system that holds the data (`NFR-090`…`093`) |
| **SC-11** | **No production data, ever.** `TS-002` synthetic only; `NFR-071`, `NFR-086c`, `BRU-SEC-08`. A security test that uses real personal data is itself a privacy incident |
| **SC-12** | **Privacy evidence is retained as a compliance record** for a minimum of five years (`NFR-095`), through `M24`, not as a test artefact (`TS-001` §4.6 `EV-04`) |
| **SC-13** | **This pack does not perform penetration testing.** `05-06` §11 places an annual penetration test with an external engagement; SAST, DAST and dependency scanning sit in CI. **This pack tests the business-logic layer of security**, and the boundary is stated so neither side assumes the other covers it |
| **SC-14** | **Every finding is reported by register reference**, so a partial pass is expressible: "379 denied cells, 376 verified, 3 open" (`AX-03` pattern) |

### 2.2 Preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | **An account per `Rnn` — all 38 — with production-equivalent record rules, field restrictions and SoD constraints** | **Does not exist** — `TS-002` `O-04`; **the single hard blocker on this pack** |
| 2 | Two accounts of the same role, belonging to different scopes, for every `SC-04` scope test | As above |
| 3 | Two accounts of different roles for every SoD assignment attempt | `SC-05` |
| 4 | API credentials per role, scoped as production would scope them | `SC-02`; `EA-11` |
| 5 | Audit logging enabled and queryable with before-values | `SC-07`; `NFR-014` |
| 6 | Residency enforcement configured, with a non-resident store available to attempt a write to | `SC-09`; `NFR-086a` — **legal opinion on the split-residency design is a `DEP-31` dependency, `O-04`** |
| 7 | Consent and preference records populated for `TS-002` personas | `SC-10`; `UI-042` |
| 8 | `TS-002` residency-classified synthetic fields loaded: NID, passport, TIN, biometric template, recovered-data index, seller KYC | `05-06` §6.4 |
| 9 | Step-up authentication configured for payouts, payroll finalisation, data-case access and bulk export | `BRU-SEC-02` |
| 10 | MFA enforced for admin, finance, HR and all privileged roles | `NFR-012`, `BRU-SEC-01` |
| 11 | A data-subject-rights request path in the product | `NFR-093`; `M33` |

---

## 3. Scripts

### 3.1 Block A — Portal access matrix · 456 cases

`SEC-001` … `SEC-456`. Derived from `05-04` §2 cell by cell.

| Sub-block | Cases | Expected | Pri |
|---|---:|---|:--:|
| **Granted cells** — the role opens the portal and reaches its own scope | **77** | Granted; access logged | **P0** |
| **Denied cells** — the role attempts the portal by direct URL and by API | **379** | **Refused at the enforcement layer** (`SC-01`, `SC-02`) | **P0** |

| Highest-consequence denials, named | Why |
|---|---|
| `R08` Service Centre Agent → any portal but `P03` | 150–250 accounts; the largest population with the narrowest grant |
| `R16` Rider → anything but `P09` | 50–150 accounts on personal devices |
| `R36` Customer → anything but `P01` | 250,000+ accounts; a leak here is a mass breach |
| `R37` Corporate user → anything but `P04` | 500–2,000 accounts across many companies |
| `R38` External party → `P01`, `P02`, `P03`, `P04`, `P06`, `P10`, `P11` | 1,000–3,000 accounts; `P03` and `P06` exposure would be total |
| `R11` Junior Technician → `P03` | The role boundary `TS-006` `UAT-R10-014` also exercises |
| Any internal role → `P06` where not granted | `P06` aggregates everything; `PRU-P06-03` makes row-level security a hard requirement |

### 3.2 Block B — Data isolation tiers · ~72 cases

Derived from `05-04` §4: six tiers, with the object classes listed per tier.

| Tier | Rule | Positive | Negative | Pri |
|---|---|---|---|:--:|
| `T0` Global | Visible to all authenticated internal users | Catalogue, brand master, checklist templates, knowledge, branch directory readable by every internal role | **Not readable by any external role** | P1 |
| `T1` Entity | `company_id` rule | Own entity's chart of accounts, tax config, payroll structures, entity policies | **Another entity's — refused** (`NFR-059`, `G9-02`) | **P0** |
| `T2` Branch | `operating_unit_id` rule | Own branch's orders, work orders, inventory, cash, HR, queue, documents | **Another branch's, by identifier — refused** (`SC-04`, `NFR-015`) | **P0** |
| `T3` Zone | `zone_id` rule | Own zone's technician schedules, van stock, assignments, route plans | **Another zone's — refused** | **P0** |
| `T4` Own record | `partner_id` / `user_id` rule | Own orders, invoices, jobs, earnings, listings, payouts, POs | **Another party's — refused, by identifier and by API** | **P0** |
| `T5` Restricted | Named allow-list, access logged, **step-up authentication** | Individual payroll, NID records, bank details, data-recovery case content, call recordings, audit logs, biometric templates, seller KYC — reachable by the allow-listed role, **with step-up and a log entry** | **Refused to everyone else; and refused to an allow-listed role without step-up** (`SC-08`) | **P0** |

### 3.3 Block C — Field-level permissions · 26 cases

Derived from `05-04` §5: 13 field groups, each tested with an entitled and a non-entitled role.
`SC-03` applies — **the field must be absent from the payload.**

| Field group | Entitled | Non-entitled test | Pri |
|---|---|---|:--:|
| `unit_cost`, `total_cost`, `margin` | `R01`–`R06`, `R17`, `R21`, `R22`, `R26`, `R27` | `R08` on an estimate; **`R37` anywhere** (`EA-02`) | **P0** |
| `salary`, `allowances`, `deductions` | `R03`, `R26`, `R30`, `R31`, own employee | `R06` on a report's payslip (`BRU-HRM-07`) | **P0** |
| `nid_number` | `R26`, `R27`, `R30`, `R31`, `R33` with justification | `R08`; and `R33` **without** justification | **P0** |
| `bank_account` | `R03`, `R26`, `R27`, `R30` | `R21` | **P0** |
| `recovered_data_index` | `R14` case-assigned only, `R02` with approval | `R14` on an **unassigned** case | **P0** |
| `call_recording_url` | `R35`, `R32`, `R02` | `R34` on a colleague's call | **P0** |
| `commission_rate` | `R03`, `R04`, `R24`, `R26` | `R38` seller (`EA-02`) | **P0** |
| `seller_kyc_document` | `R24`, `R26`, `R32` | `R38` on another seller's | **P0** |
| `technician_incentive_detail` | `R30`, `R31`, own technician, `R06` summary only | `R06` attempting **detail** rather than summary | P1 |
| `customer_credit_limit` | `R03`, `R21`, `R22`, `R26`, `R27` | `R08` | P1 |
| `internal_note` | Internal roles only | **Every external portal** (`EA-02`) | **P0** |
| `vendor_price` | `R17`, `R19`, `R26`, `R27` | `R38` vendor on another vendor's | P1 |
| `model_confidence`, `model_features` | `R02`, `R33`, model owners | Any other role | P2 |

### 3.4 Block D — Segregation of duties · 12 cases

Each blocked **at assignment** (`SC-05`), then exercised as a transaction attempt for confirmation.

| Case | Rule | Enforcement | Pri |
|---|---|---|:--:|
| `SEC-SOD-01` | Create vendor + approve vendor invoice | Hard block | **P0** |
| `SEC-SOD-02` | Raise PO + receive goods + approve invoice | Hard block on all three; **any two permitted** | **P0** |
| `SEC-SOD-03` | Process payroll + approve payroll | Hard block | **P0** |
| `SEC-SOD-04` | Create credit note + approve credit note | Hard block | **P0** |
| `SEC-SOD-05` | Adjust inventory + perform the justifying count | Hard block | **P0** |
| `SEC-SOD-06` | Approve marketplace seller + approve their payout | Hard block | **P0** |
| `SEC-SOD-07` | Repair a device + perform its independent QC | Hard block above the value threshold | **P0** |
| `SEC-SOD-08` | Create customer + approve their credit limit | **Warning + approval**, not a block — verify it warns rather than blocks | P1 |
| `SEC-SOD-09` | Administer users + approve own access request | Hard block | **P0** |
| `SEC-SOD-10` | Value a trade-in + purchase + resell | Hard block | **P0** |
| `SEC-SOD-11` | Raise a warranty claim + approve its write-off | Hard block | **P0** |
| `SEC-SOD-12` | Handle cash + reconcile the cash book | Hard block | **P0** |
| **Exception path** | CFO or CTO approval, **time-boxed**, on the standing exception report | Verify expiry and report appearance | P1 |

### 3.5 Block E — External party access · ~34 cases

`EA-01`…`EA-12` × the audiences each applies to.

| Rule | Test | Pri |
|---|---|:--:|
| `EA-01` | Each of 7 external audiences attempts a record where they are not a named party | **P0** |
| `EA-02` | Each attempts to reach cost, margin, `internal_note`, or another party's data | **P0** |
| `EA-03` | A corporate user attempts another company, then another department within their own | **P0** |
| `EA-04` | A seller attempts customer contact data **before** award and **after** the expiry period | **P0** |
| `EA-05` | A brand attempts claims or service data for another brand | **P0** |
| `EA-06` | A vendor attempts another vendor's PO, receipt or invoice | **P0** |
| `EA-07` | A courier attempts an unassigned consignment, and data beyond the delivery minimum | **P0** |
| `EA-08` | External session idles past 30 minutes | P1 |
| `EA-09` | An external financial action attempted without MFA | **P0** |
| `EA-10` | Every external access to customer personal data appears in a report | **P0** |
| `EA-11` | An API call attempts to widen its credential's scope by parameter | **P0** |
| `EA-12` | An external bulk export attempted: limited, rate-controlled, logged | P1 |

### 3.6 Block F — Access lifecycle · ~14 cases

`05-04` §9, with `SC-06` clock measurement.

| Stage | Test | Target | Pri |
|---|---|---|:--:|
| Provision | `employee.joined` → identity, role from position profile, portal access, training assigned | `AUT-047` | **P0** |
| Modify | Transfer → old revoked and new granted on the effective date, **no accumulation** | — | **P0** |
| Elevate | Approved request → time-boxed, **automatic expiry**, session recorded | `NFR-070` | **P0** |
| Review | Quarterly → unconfirmed access revoked at the deadline | `AUT-052` | P1 |
| Suspend | Leave or investigation → access disabled, records preserved | — | P1 |
| **Deprovision** | `employee.left` → **all access revoked within 1 hour**; devices deregistered; delegated authority reassigned; **active session terminated** | `BRU-SEC-06`; `AUT-048`; `TS-005` `G-01` | **P0** |
| Orphaned accounts | **Zero beyond 24 hours**, measured weekly | `KPI-090` | **P0** |
| External expiry | Agreement or registration expiry → access automatically disabled | `BRU-ECM-08` | P1 |

### 3.7 Block G — Personal Data Protection Act 2026 · ~28 cases

| `NFR` | Obligation | Test | Pri |
|---|---|---|:--:|
| `NFR-090` §6.3 | Processing only on consent or a stated legitimate ground, **recorded per purpose** | Attempt processing with no basis recorded; verify the basis is queryable per purpose | **P0** |
| `NFR-091` | Consent **clear, explicit, specific and freely given**; heightened standard for sensitive data | Verify the capture mechanism and the sensitive-data path (`UI-042`) | **P0** |
| `NFR-092` §6.3 | **Transparency notice** before or during processing, stating categories, purposes, risks, retention, transfers and the withdrawal procedure | Verify the notice appears and its content is complete (`LG-008`) | **P0** |
| `NFR-093` | Data-subject rights: access and portability, **rectification with controller notification within 30 days**, erasure, withdrawal via a simplified procedure | End-to-end for each right, in every system holding the data (`SC-10`); **the 30 days measured** (`SC-06`) | **P0** |
| `NFR-094` | **Notify the National Data Management Authority** of a qualifying breach within the prescribed timeframe | Exercise the assessment and notification path (`AUT-058`); `TS-005` `SIT-I-009` | **P0** |
| `NFR-095` | Processing records retained **minimum five years** | Verify retention configuration and that deletion is blocked inside it (`BRU-DMS-01`) | **P0** |
| `NFR-096` | **Chief Data Officer appointed** if classified a significant data fiduciary, with role, authority and reporting line defined | **Procedural, not testable in the system** — verified as an artefact; `O-05` | P1 |
| `NFR-097` | Technical and organisational measures proportionate to risk | Verified through Blocks A–F collectively | P1 |
| `NFR-098` | Processor obligations flowed by contract to every processor and sub-processor | Artefact verification with `M42`; `TS-005` `SIT-I-008` | P1 |
| `NFR-099` | **Restrict large-scale transfer of Sensitive Personally Identifiable Data**; notify cross-border transfers; disclose safeguards | Attempt a bulk transfer of NID, passport, TIN, biometric, genetic or criminal-record data; verify the block and the notification record | **P0** |

### 3.8 Block H — Residency · ~20 cases

`NFR-086`, `086a`, `086b`, `086c` × the seven classified field types in `05-06` §6.4.

| Test | Expected | Pri |
|---|---|:--:|
| Write a classified field to a non-resident store | **Refused at write time** (`SC-09`, `NFR-086a`) | **P0** |
| Read a record joined by resident key | Joined correctly; **the sensitive field is never duplicated** into the regional store | **P0** |
| Cross-border transfer of a classified field without an Authority notification record and a documented safeguard | **Refused before the transfer executes** (`NFR-086b`) | **P0** |
| A non-production environment containing unmasked classified data, in any region | **Impossible** (`NFR-086c`, `SC-11`) | **P0** |
| Each of the 7 classified field types: NID, passport, TIN, biometric template, recovered-data index, seller KYC document, criminal-record check | All four tests above, per type | **P0** |

### 3.9 Block I — Business rules and audit · ~72 cases

| Group | Cases | Test | Pri |
|---|---:|---|:--:|
| `BRU-SEC-01`…`08` | 16 | Each satisfied and each breached: MFA at every login, step-up on sensitive actions, data-case access limits, purge, bulk-export approval, one-hour revocation, SoD assignment, non-production masking | **P0** |
| `BRU-DMS-01`…`03` | 6 | Retention block, legal hold, signed-document immutability | **P0** |
| `BRU-ADM-01`…`02` | 4 | Master-data significance approval; production configuration traceable to a change record | **P0** |
| `BRU-AIM-01`…`03` | 6 | Human confirmation on material recommendations; guard rails; **recovered `M06` data never used as training data** | **P0** |
| **Audit trail** | ~40 | **Every delivered object class logs who, what, when, before and after** (`SC-07`, `NFR-014`, `G1-07`); privileged sessions recorded (`NFR-070`); **no personal data in logs** (`OPS-04`) | **P0** |

**Pack total: ~734 derived cases · ~600 at `P0`.** The figure is derived from the registers and is
reported with its derivation (`SC-14`, `CP-11`); it is **not** an authored list and it changes when
`05-04` changes.

### 3.10 Negative and edge cases

| # | Condition | Expected behaviour |
|---|---|---|
| N-01 | A denial holds in the UI and not through the API | **Critical** — `BR-STD-01`; the defect class this pack exists to find |
| N-02 | A restricted field is hidden in the view but present in the payload | **Critical** — `SC-03` |
| N-03 | Two role grants individually valid, jointly an SoD breach | Second refused at assignment (`SC-05`, `TS-005` `G-02`) |
| N-04 | Permission changed mid-transaction | New scope from the next action; in-flight action atomic (`TS-005` `G-03`) |
| N-05 | Leaver's active session persists after revocation | **Critical** — session terminated, not merely blocked at next login |
| N-06 | A report or export bypasses row-level security | **Critical** — `PRU-P06-03`; the most common route to a silent leak |
| N-07 | Audit entry lacks a before-value | `G1-07` not satisfied (`SC-07`) |
| N-08 | Personal data found in an application log | Defect against `OPS-04`; and a privacy incident in its own right |
| N-09 | Step-up authentication satisfiable by re-entering the same session token | Defect against `NFR-065` |
| N-10 | Residency-classified field duplicated into the regional store "for performance" | **Critical** — `NFR-086` prohibits duplication explicitly |
| N-11 | Consent withdrawn in one system and still honoured as consent in another | **Critical** — `SC-10` requires the state verified in every system holding the data |
| N-12 | An erasure request executed on a record under legal hold or statutory retention | Refused with the constraint explained (`NFR-088`, `BRU-DMS-02`); **an unexplained refusal is also a defect** (`NFR-093`) |

---

## 4. Exit Criteria

| Criterion | Threshold |
|---|---|
| **Denied portal cells verified** | **379 of 379 — no sampling** (`SC-01`) |
| Granted portal cells verified | 77 of 77 |
| Every denial verified at UI **and** API | 100% (`SC-02`) |
| Isolation-tier cases | 100% of `T1`–`T5`; `T0` ≥ 95% |
| Field-level restrictions verified as **payload absence** | 26 of 26 (`SC-03`) |
| SoD assignment blocks | **12 of 12** |
| External access rules | `EA-01`…`EA-12` across all applicable audiences, 100% |
| Access-lifecycle timing | **1-hour revocation and 24-hour orphan control met, measured** (`SC-06`) |
| PDPA obligations `NFR-090`…`099` | **100% of the `P0` set** |
| Residency write-time refusals | **100% across all 7 classified field types** (`SC-09`) |
| Audit completeness — who, what, when, before, after | **100% of delivered object classes** (`G1-07`) |
| `BRU-SEC-*`, `BRU-DMS-*`, `BRU-ADM-*`, `BRU-AIM-*` | Each satisfied and each breached, 100% |
| **`G1-06`** | Single sign-on and role framework operating for **all** delivered roles |
| **`G1-09`** | **Zero critical or high security findings** |
| `KPI-089` critical vulnerabilities open > 7 days | Zero |
| `KPI-090` orphaned accounts after a leaver | Zero beyond 24 hours |
| Coverage reported by register reference | 100% (`SC-14`) |
| Open Critical or High defects | **Zero — and not deferrable** (§5) |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**This pack does not defer.** `TX-16` permits a High defect to be deferred by a named decision;
**here a High or Critical access, scope, consent or residency defect is not deferrable**, because the
deferral decision would be a decision to operate with a known route to a notifiable breach.

| Trigger | Escalation |
|---|---|
| Any case where a user or party reaches data outside their scope | **Critical** to CTO, Chief Data Officer and Security Lead; **not deferrable**. Under `NFR-094` a qualifying breach carries an Authority notification duty and exposure to `BDT 50 lakh` (`RSK-032`) |
| Any residency-classified field written or transferred outside its permitted store | **Critical** to Chief Data Officer with Legal Counsel; `NFR-086`, `NFR-099` |
| Any audit-trail gap on a delivered object class | **High minimum** to CTO — `G1-07` and `NFR-024` ISO 9001 both depend on it, and a gap cannot be reconstructed retrospectively |
| Any denial that holds in the UI and not through the API | **Critical** to Solution Architect and CTO — it indicates the control is in the wrong layer, so other controls are likely to be too |

---

## 6. Sign-off

| Block | Signatory | Record |
|---|---|---|
| A–F access, scope, SoD, lifecycle | **Security Lead with CTO** | Coverage report by register reference (`SC-14`) |
| G Personal Data Protection Act 2026 | **Chief Data Officer with Legal Counsel** | Compliance record via `M24`, retained ≥ 5 years (`SC-12`) |
| H Residency | **Chief Data Officer with CTO** | Compliance record |
| I Business rules and audit | Security Lead with Quality Manager | Gate evidence pack |
| **Pack acceptance** | **CTO with Chief Data Officer** | Gate evidence pack (`TS-018`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`G1-06`, `G1-07` and `G1-09` are Month 4 criteria in W1, and this pack is registered at W2.** All three name outputs only this pack produces: the role framework operating for all delivered roles, a complete audit trail, and zero critical or high security findings. **The gate that most depends on security verification precedes the security pack** — the ninth and final sequencing instance in Category 13 | Programme Content Lead with QA Lead | **W1 — register correction** |
| **O-02** | **The 38 role accounts do not exist, and this pack is 100% dependent on them.** Not partially: every one of the ~734 cases needs an account holding exactly the permissions its role holds. `TS-002` `O-04`, `TS-003` `O-02`, `TS-004` `O-03`, `TS-006` precondition 7 and `TS-011` precondition 9 all record it; **here it is not a precondition but the entire pack** | `M29` owner with Security Lead | **W1 — absolute blocker** |
| **O-03** | **`05-04` §1.7 collapses six external audiences into `R38`**, so a case keyed to `R38` cannot distinguish a vendor from a seller from a brand from a courier from a referral partner from a recycling partner. `EA-04`, `EA-05`, `EA-06` and `EA-07` are **audience-specific rules on a single role**, which means the permission engine cannot express them as role rules and the ~34 Block E cases have no clean derivation. `TS-011` `O-06` records the same gap | Enterprise Architecture with `M29` owner | **W1 — before Block E is derived** |
| **O-04** | **The split-residency design has no legal opinion, and `05-06` §6.4 makes one a stated dependency** — `DEP-31`, decision `D-13`, *"required before the Wave 1 architecture is fixed"*. Block H tests a design that may change. **Twenty `P0` cases rest on an unratified architecture** | CTO with Legal Counsel | **W1 — `DEP-31` is already overdue against its own condition** |
| **O-05** | **`NFR-096` requires a Chief Data Officer where the company is a significant data fiduciary, and this pack's Block G is signed by that role.** The role appears in `05-06` §6.3, in `AUDIT-010` HC-01 and in `HC-019`'s approver block — **and it is not in `05-04`'s 38 roles and no appointment is recorded.** The signatory of the privacy evidence may not exist | CEO with Legal Counsel | **W1 — and before 13 May 2027 when enforcement activates** |
| **O-06** | **~734 cases have no execution estimate and QA capacity is 1 FTE at W1 and W2** (`06-01` §4; `TS-001` `O-08`). At even three minutes a case for the mechanical denials, Block A alone is over 20 person-days per release, and `SC-01` forbids sampling. **Automation is not optional here, and `06-04` does not exist** | CTO with Security Lead | **W1** |
| **O-07** | **`SC-13`'s boundary needs a counterpart.** This pack covers business-logic security; `05-06` §11 places SAST, DAST and dependency scanning in CI and a penetration test annually. **Nothing states who commissions the penetration test, when in the wave plan it falls, or how its findings reach `G1-09`'s "zero critical or high"** | CTO with Security Lead | **W2** |
| **O-08** | **`LG-012` is named in the register as this file's trace target and Category 10 holds 2 of 24 files.** The data-protection legal content this pack verifies against does not exist, so Block G tests the product against `05-06` §6.3 rather than against the company's own published position | Legal Counsel | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; the by-register organisation justified
- [x] **The pack derived from `05-04` by set arithmetic rather than authored, and the derivation shown**
- [x] **The 77 granted / 379 denied portal-cell split counted cell by cell, not estimated**
- [x] **The boundary with `TS-011` stated: systematic versus experiential, with cell counting owned here alone (`CP-01`)**
- [x] Fourteen rules stated, including UI-and-API denial, payload-absence field checks and write-time residency
- [x] The privacy half's statutory basis and its 13 May 2027 enforcement date stated, with the evidence obligation that follows
- [x] Nine blocks enumerated with derived case counts totalling ~734
- [x] Highest-consequence denials named by population, so the 379 are prioritised rather than uniform
- [x] All 12 `SOD-*`, all 12 `EA-*`, all 7 lifecycle stages, all 10 PDPA obligations and all 7 residency field types covered
- [x] `NFR-096` correctly identified as procedural rather than system-testable
- [x] `SC-13` boundary against penetration testing and CI scanning stated, so neither side assumes the other covers it
- [x] Twelve edge cases stated, including report-bypassed row-level security and cross-system consent divergence
- [x] Non-deferral rule stated with the statutory reason
- [x] Privacy evidence routed as a five-year compliance record rather than a test artefact
- [x] All internal links resolve
- [x] Eight open items recorded, including an unappointed signatory and an overdue architectural dependency
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The ~734 cases instantiated and automated — outstanding**
- [ ] **`O-02` 38 role accounts absent — outstanding; absolute blocker on the whole pack**
- [ ] **`O-04` split-residency legal opinion absent — outstanding; `DEP-31` overdue**
- [ ] **`O-05` Chief Data Officer unappointed — outstanding; the Block G signatory may not exist**
- [ ] Named approvers recorded — **pending CTO and Chief Data Officer**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
