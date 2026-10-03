---
id: SC-002
title: Threat Model (STRIDE) and Abuse Case Register
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Information Security Officer (unappointed — SC-001 Q-01)
approver: Design Authority (constituted under GV-002), countersigned by the CTO
standards_basis: >
  STRIDE (Microsoft threat taxonomy) · ISO/IEC 27001:2022 Annex A.8.25 (secure development
  lifecycle) · ISO/IEC 27005:2022 (information security risk) · OWASP Top 10:2025 ·
  OWASP ASVS 5.0.0 · MITRE ATT&CK Enterprise (technique reference) · NIST SP 800-154 (data-centric
  threat modelling, method reference)
traces_to: >
  PGD-000 SC-002 · SC-001 §4.2, §5, §6, §7 · M29 FR-SEC-001…052 · 05-04 §6 SOD, §8 EA ·
  05-06 §4 NFR-011…072 · audit findings C-05, HC-01, OP-01, OP-08, OP-10, A3-20
depends_on: SC-001 (boundaries and elements) · AR-001 (deployment view) · DA-002 (PII flags)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 13:10 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-002 — Threat Model (STRIDE) and Abuse Case Register

### Category 05 · Code `SC` · STRIDE · ISO/IEC 27001:2022 A.8.25 · ISO/IEC 27005:2022

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-002`.
> 2. **`PG-03` Count, do not consult.** Estate figures counted at **2026-08-18 13:10 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1 states conformance and departures — including why DREAD is
>    **not** used.
> 4. **`PG-M4` Verify citations.** Statutory and standards-version claims carry `verified_on`.

---

## 1. Purpose

This document enumerates, systematically and per component, **how this system can be attacked** —
and states, for each threat, whether a control already answers it, whether the control exists, and
what remains as residual risk.

It exists because **the phrase "threat model" occurs zero times in the source estate**. Counted at
13:10 (+06) across `1000fix_ERP_Module/`, `project_content/`, `primary-doc/` and
`old-primary-doc/` — **0 files of 621**. ISO/IEC 27001:2022 Annex A.8.25 requires security to be
integrated into every stage of development. A system with 52 security requirements and no threat
model has controls chosen from a checklist rather than from its own attack surface, and the two
differ precisely where the system is unusual.

**This system is unusual in six ways**, each of which produces threats a generic ERP checklist
does not contain: a public marketplace with 500–2,000 sellers who transact and are paid; remote
desktop sessions into customer IT estates; recovered customer data held in custody; 12
internet-facing surfaces and a public webhook receiver; biometric templates for 500+ employees;
and a Bangladesh-resident data store whose mishandling is a **statutory act rather than an
incident**.

Its consumers are concrete. **`QA-007` security testing derives its cases from here** — testing
against assumptions instead is what `_CATEGORY_OVERVIEW.md` warns about. `SC-009` derives
penetration-test scope from §9. `SC-005` derives its abuse-case unit-test obligation from §8.
`GV-005` receives the residual risks in §11.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Decomposition** of the system into DFD elements — external entities, processes, data stores, data flows — at the granularity `SC-001` §5 establishes |
| 2 | **Trust boundary enumeration** — 9 boundaries, each with what changes when it is crossed |
| 3 | **STRIDE enumeration per element**, applying the element-type rule rather than asking six questions of everything |
| 4 | The **threat register `TH-001`…`TH-097`** with likelihood, impact, rating, mitigating control and residual position |
| 5 | The **abuse case register `AB-01`…`AB-32`** — adversary-perspective narratives for the six unusual surfaces |
| 6 | **Insider-threat and privilege-abuse** analysis, including the SoD fraud paths as security threats rather than finance controls |
| 7 | **Supply-chain threats** — OWASP Top 10:2025 `A03`, 47 egress destinations, OCA/Odoo dependency surface |
| 8 | **Privacy-specific threats** using LINDDUN category names where STRIDE has no equivalent |
| 9 | **Threat-to-control coverage analysis**, including threats with **no** mitigating control |
| 10 | **Attack trees** for the three highest-consequence outcomes |
| 11 | **Residual risk** hand-off to `GV-005` and the re-modelling triggers |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The boundaries themselves | `SC-001` | A threat model attacks a structure; it does not design one |
| Privacy risk **to data subjects** | `SC-003` | Different question, different standard (ISO/IEC 29134:2023), different subject. §10 covers privacy threats **to the system**; harm to individuals is a DPIA |
| Control specification | `SC-004`…`SC-007`, `SC-010` | This document names the mitigating control; the named document specifies it |
| Test scripts | `QA-007` | This document supplies the case; QA writes the script |
| Pen-test scope and cadence | `SC-009` | Derived from §9 |
| Enterprise risk register | `GV-005`, `M60` | §11 hands over; it does not duplicate |
| Physical and social-engineering attack | `LG-021` IS-07, IS-12 | Real, and outside a software threat model's boundary. Named in §11 as accepted-elsewhere |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Security architect** | Validation that `SC-001`'s boundaries hold against enumerated attack |
| **QA / `QA-007`** | §8 and §9 are the security test basis — **including the negative tests** |
| **Developers** | §8 abuse cases: what a hostile user will do with the feature you are building |
| **Penetration tester (`SC-009`)** | §9's uncovered threats and §12's attack trees are where to look first |
| **CISO / Design Authority** | §11 residual risk — what the programme is accepting, stated as a number |
| **Enterprise client security team** | Evidence that the abuse surface was enumerated rather than assumed |

---

## 2. Method

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **STRIDE** | §5 applies the **element-type mapping**: external entity → S, R; process → S, T, R, I, D, E; data store → T, R, I, D; data flow → T, I, D | Asking all six of every element produces noise and hides the real threats. The element-type rule is STRIDE as designed |
| **ISO/IEC 27001:2022 A.8.25** *(verified 2026-08-18)* | Secure development lifecycle requires threat identification during design. This document is that activity for the W1 architecture, with re-modelling triggers in §13 | — |
| **ISO/IEC 27005:2022** | §4 risk scale, §6 likelihood/impact anchors, §11 residual risk treatment and acceptance | 27005 is method-agnostic on identification; STRIDE supplies identification, 27005 supplies evaluation |
| **OWASP Top 10:2025** *(published 6 Nov 2025, finalised Jan 2026; verified 2026-08-18)* | §7 maps the threat register to the 2025 categories, including new `A03` Software Supply Chain Failures and `A10` Mishandling of Exceptional Conditions | The estate contains **no reference to any OWASP Top 10 edition**. Introduced here |
| **OWASP ASVS 5.0.0** | Every threat with a mitigating control names the ASVS chapter that verifies it, so `SC-005` can bind the gate | — |
| **MITRE ATT&CK Enterprise** | Technique references on the 14 threats where an adversary technique is well characterised (`TA0006` credential access, `TA0008` lateral movement, `TA0010` exfiltration) | Full ATT&CK mapping is disproportionate pre-build and would not change a control decision |
| **LINDDUN** | §10 borrows four category names — **linkability, identifiability, non-repudiation (as a privacy harm), detectability** — where STRIDE has no equivalent | Full LINDDUN would duplicate `SC-003`. Four categories are borrowed, not the method |
| **NIST SP 800-154** | Data-centric method reference for §10 and for the `Z4` analysis | Draft status; used as method inspiration, **not cited as an obligation** |

> **DREAD is deliberately not used.** DREAD produces different scores from different analysts for
> the same threat — it was retired by its originator for exactly that reason. §4 uses an explicit
> **Likelihood × Impact** matrix with published anchors, so a reviewer can dispute a *rating*
> without disputing the *method*. This matters here: `LG-021` §4.1.6 already establishes that an
> unevidenced assertion is a deficiency, and an unreproducible risk score is an unevidenced
> assertion.

### 2.2 What was modelled, and what the model is built from

| Input | Supplied |
|---|---|
| `SC-001` §5.1, §5.2 | 7 trust zones and the permitted-flow matrix |
| `SC-001` §6.1 | 5 identity populations |
| `SC-001` §7.1 | 7 enforcement points and their failure modes |
| `SC-001` §8.1 | 9 `S3` fields and their placement |
| `SC-001` §9.2 | 68 controls — the mitigation vocabulary |
| `AR-001` §6.1, §7.1 | Layer stack, 16 domain services, 12 API families |
| `05-03` §2, §4 | 47 external integrations; the domain event catalogue |
| `05-04` §6, §8 | `SOD-01`…`SOD-12`; `EA-01`…`EA-12` |
| `SP-006` §4.2–§4.6 | `SOD-01`…`SOD-60` — the fraud-path source for §8 |
| `M05`, `M06`, `M12` | The three unusual business surfaces |

### 2.3 Enumeration

| # | Figure | **Counted 2026-08-18 13:10 (+06)** | Note |
|---|---|---:|---|
| 1 | Files containing "threat model" in the source estate | **0** | The gap this document closes. Confirmed against 621 source-estate files |
| 2 | DFD elements modelled | **59** | 8 external entities, **22** processes, 13 data stores, 16 flow classes. *(Corrected during the Category 05 audit — the first issue stated 58 and 21; `SCA-12`)* |
| 3 | Trust boundaries | **9** | 7 zone boundaries + `Z7` enclave + the organisational boundary at `M05` |
| 4 | Threats enumerated | **97** | §6 |
| 5 | Threats whose control **exists in specification and is buildable** (●) | **39** | §9.1 |
| 6 | Threats whose control **is specified but does not exist** (◐) | **50** | §9.2 — the population that matters |
| 7 | Threats with **no** control at any altitude (✖) | **8** | §9.3 |
| 7a | *Check* | **39 + 50 + 8 = 97** ✓ | Regenerated by counting the status column of all 97 register rows, per `PG-M10`. *(The first issue stated 74 / 19 / 4, which did not reconcile — `SCA-12`)* |
| 8 | Abuse cases | **32** | §8 |
| 9 | Critical-rated threats | **11** | §6.1 |
| 10 | Threats traceable to an existing audit finding | **17** | §9.4 |

---

## 3. System Decomposition

### 3.1 The data-flow diagram

```
                              ═══ TB-1 ═══ internet / edge
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │EE-1      │  │EE-2      │  │EE-3      │  │EE-4      │  │EE-5      │
  │Customer  │  │Corporate │  │Seller    │  │Vendor /  │  │Staff     │
  │250k/mo   │  │user      │  │500–2000  │  │brand /   │  │800+      │
  │          │  │500–2000  │  │          │  │courier   │  │          │
  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
       └─────────────┴─────────────┴─────────────┴─────────────┘
                              │
              ┌───────────────▼───────────────┐
              │ P-01  Z0 edge — WAF/CDN/bot   │   EE-6 attacker (unauthenticated)
              └───────────────┬───────────────┘   EE-7 3rd-party API (47)
                        ═══ TB-2 ═══              EE-8 model service / AI
              ┌───────────────▼───────────────┐
              │ P-02  Z1 Kong — introspect,   │◄────► P-03 Keycloak (IdP)
              │       quota, correlation-id   │            │
              └───────────────┬───────────────┘        DS-01 identity store
                        ═══ TB-3 ═══ (EP-2 boundary: authenticated, NOT scoped)
   ┌──────────────────────────▼──────────────────────────────────────┐
   │ Z2 APPLICATION                                                  │
   │  P-04 BFF ×6      P-05 Odoo ORM ★EP-3/4/5   P-06 SoD engine EP-6│
   │  P-07 audit writer   P-08 notification   P-09 dispatch scoring  │
   │  P-10 document gen   P-11 pricing   P-12 OCR   P-13 settlement  │
   │  P-14 ML gateway     P-15 STT       P-16 event replay           │
   │  P-17 DSR orchestrator              P-18 outbox publisher       │
   │  P-19 ★ RESIDENCY SERVICE CD-233 (EP-7)                         │
   │  P-20 masking job    P-21 reconciliation                        │
   └───┬───────────────┬──────────────────┬─────────────────┬────────┘
    ═TB-4═          ═TB-5═             ═TB-6═            ═TB-7═
   ┌───▼───────┐  ┌───▼──────────┐  ┌───▼─────────┐  ┌────▼─────────┐
   │ Z3 DATA   │  │ Z4 RESIDENT  │  │ Z6 EGRESS   │  │ Z7 REMOTE    │
   │ DS-02 pg  │  │ DS-08 pg-BD  │  │ → 47 dests  │  │ SUPPORT M05  │
   │ DS-03 ts  │  │ DS-09 keys-BD│  │             │  │ ═══ TB-9 ═══ │
   │ DS-04 ch  │  │              │  │             │  │ → CUSTOMER   │
   │ DS-05 rd  │  │ ★ only path  │  │             │  │   ESTATES    │
   │ DS-06 s3  │  │   is P-19    │  │             │  │              │
   │ DS-07 log │  └──────────────┘  └─────────────┘  └──────────────┘
   └───────────┘
                        ═══ TB-8 ═══
              ┌────────────────────────────────┐
              │ Z5 MANAGEMENT                  │
              │ P-22 CI/CD  DS-10 Vault        │
              │ DS-11 observability            │
              │ DS-12 artefact registry        │
              │ DS-13 backups   ★ TB-8 crossing│
              └────────────────────────────────┘
```

### 3.2 Element register

**External entities (8)** — STRIDE: **S, R**

| ID | Entity | Population | Authenticated | Highest privilege reachable |
|---|---|---:|---|---|
| `EE-1` | Individual customer | 250,000+/mo | Optional MFA | `T4` own records |
| `EE-2` | Corporate portal user | 500–2,000 | MFA for Approver/Finance | Own company, role-scoped |
| `EE-3` | Marketplace seller | 500–2,000 | MFA for financial actions | Own listings, jobs, payouts |
| `EE-4` | Vendor / brand / courier / auditor — **17 sub-identities on one role** | 1,000–3,000 | MFA for financial actions | Own records |
| `EE-5` | Internal staff | 800+ | MFA where role requires | Up to estate-wide (`R02`, `R33`) |
| `EE-6` | **Unauthenticated attacker** | — | none | `Z0` only, by design |
| `EE-7` | Third-party API | **47** | Per-integration credential | Whatever the integration is scoped to |
| `EE-8` | Model / AI inference service | — | Client credential | Whatever is sent to it |

**Processes (22)** — STRIDE: **all six**

Named in §3.1. The five that carry disproportionate risk:

| ID | Process | Why disproportionate |
|---|---|---|
| `P-03` | **Keycloak** | Single point of authentication for **all 12 surfaces, deliberately**. Its compensating control (break-glass) does not exist (`OP-08`) |
| `P-05` | **Odoo ORM** | Holds `EP-3`, `EP-4`, `EP-5` — three of the five authorisation decisions. A defect here is an estate-wide isolation failure |
| `P-19` | **Residency service `CD-233`** | The **only** path to `Z4`. Its compromise is a statutory event, not an incident |
| `P-17` | **DSR orchestrator** | Enumerates every module holding a subject's data. **An abused DSR is a lawful-looking mass data extraction** — see `AB-19` |
| `P-22` | **CI/CD** | Can change every other element. `TB-8` is the boundary with the widest blast radius and the weakest current control (`PGD-A2-15`: nothing under version control) |

**Data stores (13)** — STRIDE: **T, R, I, D**

| ID | Store | Zone | Sensitivity | Note |
|---|---|---|---|---|
| `DS-01` | Keycloak identity store | `Z3` | `S2` | Credential material, MFA secrets |
| `DS-02` | PostgreSQL regional primary + 2 replicas | `Z3` | `S0`–`S2` | Business truth |
| `DS-03` | TimescaleDB | `Z3` | `S1`–`S2` | 800 GPS/min — **staff location history** |
| `DS-04` | ClickHouse (W8) | `Z3` | `S1`–`S2` | Analytical copies — a copy is a threat surface |
| `DS-05` | Redis | `Z3` | `S1`–`S2` | Session and cache — **`SEC-DC-2`: a cache is a copy** |
| `DS-06` | MinIO object storage | `Z3` | `S1`–`S3` | 50 TB; evidence photographs, documents |
| `DS-07` | Audit and access log store | `Z3` | `S3` (`T5`) | **Insert-only, hash-chained** |
| `DS-08` | **PostgreSQL Bangladesh-resident** | **`Z4`** | **`S3`** | NID, passport, TIN, biometric, recovered data, KYC, criminal records |
| `DS-09` | **Key material, Bangladesh** | **`Z4`** | **`S3`** | `LG-012` `RD-R5` |
| `DS-10` | Vault | `Z5` | `S3` | All credentials |
| `DS-11` | Observability — Loki/Tempo/Prometheus | `Z5` | `S1` | **`SEC-DC-4`: a log is a copy** |
| `DS-12` | Artefact / image registry | `Z5` | `S1` | Supply-chain target (`A03`) |
| `DS-13` | Backups and DR replicas | `Z3`/`Z4` | mirrors source | **`OP-02`: no immutable copy outside the provider account** |

**Data flow classes (16)** — STRIDE: **T, I, D**

`DF-01` browser→edge · `DF-02` edge→gateway · `DF-03` gateway→app · `DF-04` app→app (mTLS) ·
`DF-05` app→regional DB · `DF-06` **app→residency service** · `DF-07` **residency service→`Z4`** ·
`DF-08` app→object storage · `DF-09` app→outbox→broker · `DF-10` broker→consumer ·
`DF-11` app→egress proxy · `DF-12` egress→third party · `DF-13` app→log pipeline ·
`DF-14` CI/CD→runtime · `DF-15` DB→backup/DR · `DF-16` **`Z7`→customer estate**

### 3.3 Trust boundaries

| ID | Boundary | What changes when it is crossed | Enforcement | Highest-rated threat |
|---|---|---|---|---|
| `TB-1` | Internet → `Z0` | Traffic becomes shaped and rate-limited | WAF, bot management | `TH-002` |
| `TB-2` | `Z0` → `Z1` | Traffic is attributable to the edge | Mutual auth | `TH-009` |
| `TB-3` | **`Z1` → `Z2`** | Request becomes **authenticated — and not yet scoped** | `EP-2` introspection | **`TH-021`** |
| `TB-4` | `Z2` → `Z3` | Business intent becomes durable state | `EP-3`/`EP-4`/`EP-5` **before** the write | `TH-034` |
| `TB-5` | **`Z2` → `Z4`** | Access becomes a **statutory** event | `EP-7`, `P-19` only | **`TH-047`** |
| `TB-6` | `Z2` → `Z6` | Data leaves the company | Allow-list, credential injection, logging | `TH-058` |
| `TB-7` | `Z2` → `Z7` | A session becomes a third-party network connection | Agreement scope, recording, origin restriction | `TH-066` |
| `TB-8` | `Z5` → `Z2`/`Z3` | Configuration becomes runtime | MFA, elevation, session recording | **`TH-075`** |
| `TB-9` | **`Z7` → customer estate** | The **organisational** boundary — 1000FiX acts inside a third party's network | Consent record, recording, scope | **`TH-069`** |

> **`TB-3` is the most-misunderstood boundary in the system.** Crossing it means *authenticated*.
> It does **not** mean *scoped*. `SC-001` `SEC-EP-1` states the defect class; `TH-021` is the
> threat; `AB-05` is the abuse case; `QA-007` must test it by **removing the BFF filter and
> re-running the request**.

---

## 4. Risk Scale

### 4.1 Likelihood

| Score | Anchor |
|---|---|
| **5 Almost certain** | Occurs without an adversary — a misconfiguration, a default, or an ordinary user error will produce it |
| **4 Likely** | Requires only publicly known technique and an ordinary account; no insider knowledge |
| **3 Possible** | Requires a valid account of a specific type, or chaining two weaknesses |
| **2 Unlikely** | Requires privileged access, physical access, or a targeted, funded effort |
| **1 Rare** | Requires simultaneous compromise of two independently controlled components |

### 4.2 Impact

| Score | Anchor |
|---|---|
| **5 Severe** | Statutory breach with penalty exposure (**BDT 25–50 lakh**); loss of the data-recovery business line; estate-wide data exposure; loss of a brand authorisation |
| **4 Major** | Single-contract loss; cross-branch or cross-tenant exposure; material fraud; a reportable personal-data breach |
| **3 Moderate** | Single-customer data exposure; localised fraud; a control failure requiring disclosure to one client |
| **2 Minor** | Degraded service; recoverable within RTO; no data exposure |
| **1 Negligible** | Nuisance; absorbed by normal operations |

### 4.3 Rating

| L × I | 1 | 2 | 3 | 4 | 5 |
|---|:--:|:--:|:--:|:--:|:--:|
| **5** | M | M | H | **C** | **C** |
| **4** | L | M | H | H | **C** |
| **3** | L | M | M | H | **C** |
| **2** | L | L | M | M | H |
| **1** | L | L | L | M | M |

**C** Critical — treat before the wave that introduces the element · **H** High — treat before
go-live of that surface · **M** Medium — treat or accept with a named owner · **L** Low — accept,
review at wave gate.

---

## 5. STRIDE Application

Applied by element type. **A cell marked — is not "safe"; it is "not applicable to this element
type"**, which is the distinction that makes STRIDE efficient.

| Element type | S | T | R | I | D | E |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| External entity | ● | — | ● | — | — | — |
| Process | ● | ● | ● | ● | ● | ● |
| Data store | — | ● | ●¹ | ● | ● | — |
| Data flow | — | ● | — | ● | ● | — |

¹ Repudiation applies to a data store when it **is** the record of who did what — `DS-07`. A
tamperable audit store does not merely lose data; it destroys the ability to attribute anything
that ever happened.

---

## 6. Threat Register

97 threats. Columns: **L** likelihood, **I** impact, **R** rating, **Control** the `SC-001`
control or the document that owns it, **St** control status — ● exists in specification and is
buildable · ◐ specified, does not exist yet · ✖ **no control**.

### 6.1 Critical threats — the eleven

Extracted first, because a register of 97 buries them.

| ID | Threat | Element | S T R I D E | L | I | R | Control | St |
|---|---|---|---|:--:|:--:|:--:|---|:--:|
| **`TH-021`** | **Scope widened by request parameter or object reference** — an authenticated `EE-1`/`EE-3` requests another party's record id directly and `EP-4` is bypassed because the BFF was treated as the control | `P-04`,`P-05`,`TB-3` | **E**, I | 4 | 5 | **C** | `SEC-C-015`, `SEC-C-018`, `SEC-C-021` | ● |
| **`TH-047`** | **Residency-classified field written to `Z3`** by a module that did not route through `P-19` — a statutory act committed by ordinary code | `P-05`,`DS-02` | **T**, I | 4 | 5 | **C** | `SEC-C-050`, `SEC-C-062`, `EP-7` | ◐ |
| **`TH-048`** | **A cache, replica, search index or log in `Z3` holds a residency-classified value** — a residency breach nobody decided to commit | `DS-04`,`DS-05`,`DS-07`,`DS-11` | **I** | 4 | 5 | **C** | `SEC-DC-2`, `-3`, `-4` | ◐ |
| **`TH-055`** | **Cross-border restore of `Z4` during an outage** — the only available recovery route is a notifiable regulatory act | `DS-13`,`DF-15` | **I** | 4 | 5 | **C** | `SEC-DR-02` | **✖** |
| **`TH-069`** | **Compromised `R13` remote-support identity used to reach every managed client's network** — one credential, many organisations | `P-*` `Z7`,`TB-9` | **S**, **E** | 3 | 5 | **C** | `SEC-C-064`, `SEC-C-036` | ◐ |
| **`TH-075`** | **CI/CD pipeline compromise deploys attacker code to production** — `TB-8` has the widest blast radius and no version control beneath it | `P-22`,`DF-14` | **T**, **E** | 3 | 5 | **C** | `SEC-C-055`, `SEC-C-056` | ◐ |
| **`TH-081`** | **Identity provider outage with no break-glass** — administrative recovery improvised under Sev1, producing unattributable production change | `P-03` | **D**, **R** | 4 | 4 | **C** | `SEC-C-035` (`BG-A1`…`BG-A5`) | **✖** |
| **`TH-084`** | **Recovered customer data (`M06`) accessed outside the assigned case team, or exfiltrated** — content of unknown classification, in custody | `DS-08`,`P-19` | **I**, **E** | 3 | 5 | **C** | `SEC-C-041`, `BRU-SEC-03`, dual control | ◐ |
| **`TH-088`** | **Biometric templates exfiltrated** — irreversible; a fingerprint cannot be rotated | `DS-08` | **I** | 2 | 5 | **H→C** | `SEC-C-047`, irreversible-template storage | ◐ |
| **`TH-091`** | **Transcript corpus mined without a confirmed lawful basis**, then derived into an FAQ bank and a model — remediation is deletion of a derived corpus and may not be complete | `P-14`,`P-15`,`DS-02` | **I** | 5 | 4 | **C** | `SC-003` lawful basis; `PI-03` | **✖** |
| **`TH-094`** | **Supply-chain compromise via an OCA/Odoo/npm dependency or a poisoned image** — OWASP `A03:2025` | `DS-12`,`P-22` | **T**, **E** | 3 | 5 | **C** | `SEC-C-056` SCA | ◐ |

> **Three of the eleven have no control at any altitude** — `TH-055`, `TH-081`, `TH-091`. They are
> not oversights in this document; each corresponds to an open audit finding (`OP-01`, `OP-08`,
> `HC-01`) whose remediation sits outside engineering. They are carried to `GV-005` in §11.

### 6.2 Spoofing (`TH-001`…`TH-014`)

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-001` | Credential stuffing against `P01` customer login using breached password lists | `EE-1`,`P-03` | 5 | 3 | **H** | `SEC-C-003` breach-list, `SEC-C-011` | ● |
| `TH-002` | Automated account enumeration through registration or reset response differences | `P-03` | 4 | 2 | **M** | `SEC-C-011`, ASVS V6 | ● |
| `TH-003` | Session token theft via XSS on a portal | `P-04` | 3 | 4 | **H** | ASVS V5, CSP, `SEC-C-006` | ● |
| `TH-004` | Session fixation or insufficient rotation after privilege change | `P-03` | 3 | 4 | **H** | ASVS V6, `SEC-C-006` | ● |
| `TH-005` | **MFA not enforced on a role that requires it**, because the requirement lives in a table and not in the realm | `P-03` | 4 | 4 | **H** | `SEC-C-004`; `SC-004` §6 | ◐ |
| `TH-006` | SIM-swap or SMS interception defeating SMS-based MFA | `EE-*`,`P-03` | 3 | 4 | **H** | `SC-004` §6 — TOTP preferred over SMS | ◐ |
| `TH-007` | **Corporate SSO federation trusts an assertion from a compromised client IdP** — 1000FiX inherits the client's authentication weakness | `P-03`,`EE-2` | 3 | 4 | **H** | `SEC-C-009`; assertion validation, per-client trust config | ◐ |
| `TH-008` | Service-account credential reuse across environments | `EE-7`,`DS-10` | 3 | 4 | **H** | `SEC-C-012`, `SEC-C-048` | ● |
| `TH-009` | Direct-to-origin request bypassing `Z0`, defeating WAF and bot controls | `TB-2` | 3 | 4 | **H** | `SEC-C-061`, edge mutual auth | ● |
| `TH-010` | **Webhook receiver accepts a forged inbound event** — a public endpoint by design | `P-02`,`EE-7` | 4 | 4 | **H** | `05-03` signature verification; `SEC-C-021` | ● |
| `TH-011` | Technician/rider device cloned or a registered device reused after loss | `EE-5`,`P-04` | 3 | 3 | **M** | `SEC-C-010` deregistration on leaver/loss | ● |
| `TH-012` | **Shared logins persist in practice** at branch counters, defeating attribution entirely | `EE-5` | 4 | 4 | **H** | `SEC-C-001`; `M29` §7.1; **process, not technical** | ◐ |
| `TH-013` | Seller account takeover leading to payout redirection | `EE-3` | 3 | 4 | **H** | `EA-09` MFA on financial actions; step-up on bank-detail change | ● |
| `TH-014` | Impersonation of a data subject in a DSR to obtain another person's file | `EE-1`,`P-17` | 4 | 4 | **H** | `FR-SEC-051` identity verification; `LG-010` | ● |

### 6.3 Tampering (`TH-015`…`TH-020`, `TH-022`…`TH-040`)

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-015` | Mass assignment — a write to a field the role may not edit, through an API that accepts the whole object | `P-05` | 4 | 4 | **H** | `SEC-C-016` field permissions **on write**; ASVS V4 | ● |
| `TH-016` | Price, discount or estimate manipulated client-side and accepted server-side | `P-04`,`P-11` | 4 | 4 | **H** | `PS-11` no business rule client-side; `SEC-C-021` | ● |
| `TH-017` | Business-logic sequence abuse — approve before estimate, receive before order | `P-05` | 3 | 4 | **H** | State models; `SEC-C-020` | ● |
| `TH-018` | Replay of a payment or settlement instruction | `P-13`,`DF-12` | 3 | 4 | **H** | Idempotency-key enforcement (`API`); `SEC-C-021` | ● |
| `TH-019` | Event tampering between outbox and consumer | `DF-09`,`DF-10` | 2 | 4 | **M** | Signed envelope; `SEC-C-063` mTLS | ◐ |
| `TH-020` | Malicious file upload — web shell, macro, polyglot — stored and later served | `P-05`,`DS-06` | 4 | 4 | **H** | `SEC-C-053` malware scan **before storage or serving** | ● |
| `TH-022` | **Mobile application repackaged or tampered** — one of 4 Flutter builds modified and side-loaded to bypass client checks | `EE-5`,`P-04` | 3 | 3 | **M** | `SR-06` no client-side business rule; MASTG checks (`SC-009` `VS-9`) | ◐ |
| `TH-023` | **Offline-sync writes reordered, replayed or forged** by a technician device on reconnection | `P-04`,`DF-03` | 3 | 4 | **H** | `AR-010` sync protocol: server-authoritative ordering, idempotency (`SR-25`), server time (`SC-010` `TM-6`) | ◐ |
| `TH-024` | **Event replay capability abused** to re-apply a past state change — the replay-from-timestamp feature used as an attack primitive | `P-16`,`DF-10` | 2 | 4 | **M** | Replay restricted to `R33` under elevation; idempotent consumers; replay is an `L4` logged act | ◐ |
| `TH-025` | **Price list, rate card or discount floor tampered through a master-data import** rather than through the UI | `P-05`,`M64` | 3 | 4 | **H** | `SOD-14` propose/approve separation; `source=import` attribution (`SC-010` §4.1) | ◐ |
| `TH-026` | **IoT telemetry injection** — falsified sensor data drives a predictive-maintenance action or an SLA credit | `M48`,`DS-03` | 3 | 3 | **M** | Device identity and signed telemetry; anomaly bounds | ◐ |
| `TH-027` | **Document template tampered** so generated invoices, certificates or evidence packs carry altered content | `P-10`,`M24` | 2 | 5 | **H** | Template change control; **`SC-010` `M6-5` certificate anchored into `L1`** | ◐ |
| `TH-028` | **Webhook signing key compromised**, so forged inbound events pass verification — distinct from `TH-010`, which is unsigned forgery | `P-02`,`DS-10` | 2 | 4 | **M** | `SC-006` `K-S` per-purpose keys, rotation; `SEC-C-048` | ◐ |
| `TH-029` | **Offline device clock manipulated** to inject false chronology into the evidential trail | `P-04`,`DS-07` | 3 | 4 | **H** | `SC-010` `TM-1`, `TM-6` — server receipt time authoritative, divergence retained | ◐ |
| `TH-030` | **Malicious import or migration file** exploits parsing to write outside its intended scope | `P-22`,`P-05` | 3 | 4 | **H** | `SR-13` scripts subject to the same checks; `TH-036` schema-layer enforcement (`SC-007` §5.3) | ◐ |
| `TH-031` | **Audit entry modified or deleted by an administrator** | `DS-07` | 3 | 5 | **H** | `SEC-C-039` insert-only at DB privilege level, hash-chained | ● |
| `TH-032` | Audit chain broken silently, so tampering is undetectable after the fact | `DS-07` | 3 | 5 | **H** | `SC-010` chain verification job | ◐ |
| `TH-033` | Backup or DR replica altered, so a restore reintroduces attacker state | `DS-13` | 2 | 5 | **H** | `SEC-DR-04` immutable copy | **✖** |
| `TH-034` | Direct database write bypassing `EP-3`…`EP-5` by a component with a broad DB grant | `DF-05`,`DS-02` | 3 | 5 | **H** | Least-privilege DB roles; Vault short-lease | ◐ |
| `TH-035` | Record rule weakened by a domain expression error, silently widening `T2` to `T0` | `P-05` | 4 | 5 | **C→H** | `QA-007` negative tests per tier; `SC-004` profiles | ◐ |
| `TH-036` | Migration or data-fix script writes across a tenant or residency boundary | `P-22` | 3 | 5 | **H** | `SEC-C-050` write-time check applies to scripts too | ◐ |
| `TH-037` | Masking job fails partially, leaving unmasked rows in `staging` | `P-20` | 3 | 5 | **H** | `SEC-NP-2` masking **inside** the clone job — fails the clone, not the mask | ● |
| `TH-038` | Configuration drift disables a control silently between deploys | `P-22` | 4 | 4 | **H** | `PE-004` policy check; `AR-012` fitness functions | ◐ |
| `TH-039` | Time manipulation on a device to defeat time-boxed elevation or session expiry | `P-03` | 2 | 3 | **M** | Server-side time authority only | ● |
| `TH-040` | Signed document or e-signature evidence re-sealed or its hash chain broken | `P-10` | 2 | 4 | **M** | `LG-019`; `SC-006` algorithm agility | ◐ |

### 6.4 Repudiation (`TH-041`…`TH-046`)

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-041` | Action attributable to a shared login and therefore to nobody | `EE-5` | 4 | 4 | **H** | `SEC-C-001`; see `TH-012` | ◐ |
| `TH-042` | A privileged action taken without a session recording | `Z5` | 3 | 4 | **H** | `SEC-C-036`; recording failure **terminates** the session | ◐ |
| `TH-043` | Read of `S3` data with no access-log entry, because logging is post-hoc | `EP-5`,`EP-7` | 3 | 5 | **H** | `SEC-C-041` — log written **before** the value returns | ◐ |
| `TH-044` | Bulk export performed without approval or record | `P-05` | 3 | 5 | **H** | `SEC-C-042` approval + log + rate limit | ● |
| `TH-045` | Break-glass used silently | `Z5` | 3 | 5 | **H** | `BG-A2` loud by design | **✖** |
| `TH-046` | Destruction or purge certificate issued without verifiable evidence, undermining the `M06` commercial claim | `P-10`,`M06` | 2 | 5 | **H** | `SC-006` crypto-erase evidence; `SC-010` | ◐ |

### 6.5 Information disclosure (`TH-047`…`TH-062`)

`TH-047`, `TH-048` in §6.1.

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-049` | **Cross-branch read** — `NFR-015` isolation defeated by a missing or wrong record rule | `P-05` | 4 | 4 | **H** | `SEC-C-015`; `T2` negative test | ◐ |
| `TH-050` | **Cross-tenant read in the corporate portal** — one client sees another's estate | `P-04`,`P-05` | 3 | 5 | **H** | `EA-03`; `SEC-C-018` | ◐ |
| `TH-051` | **Seller sees another seller's payout, listing or customer** | `EE-3`,`P-05` | 3 | 4 | **H** | `EA-01`, `EA-04`; `SEC-C-018` | ◐ |
| `TH-052` | Cost, margin or internal notes exposed to an external portal | `P-04` | 4 | 4 | **H** | `EA-02`; `SEC-C-016` | ● |
| `TH-053` | Personal data in an error message, stack trace or debug response | `P-*` | 4 | 3 | **H** | ASVS V7; `SEC-DC-4`; OWASP `A10:2025` | ◐ |
| `TH-054` | Personal data in logs or traces reaching `DS-11` | `DF-13` | 4 | 4 | **H** | `SEC-DC-4` redaction **at emission** | ◐ |
| `TH-056` | Analytics or warehouse copy carries `S3` fields into `DS-04` | `DS-04`,`P-21` | 3 | 5 | **H** | `SEC-DC-2`; `DA-00x` classification propagation | ◐ |
| `TH-057` | Object storage misconfigured to public read — 50 TB including evidence photographs | `DS-06` | 3 | 5 | **H** | `SEC-C-061`; `PE-004` policy check | ◐ |
| `TH-058` | **Data exfiltrated to an unlisted destination** from a `Z2` node | `DF-11`,`TB-6` | 3 | 5 | **H** | `SEC-ZR-1` allow-list, network-enforced | ◐ |
| `TH-059` | Third-party tag on a portal (analytics, chat, video) collects personal data | `P-04`,`EE-7` | 4 | 4 | **H** | `LG-011`; `TR-05` **unregistered**; CSP | **✖** |
| `TH-060` | Technician GPS history reconstructs an employee's movements beyond the operational purpose | `DS-03` | 3 | 3 | **M** | `LG-009` retention; `SC-003` proportionality | ◐ |
| `TH-061` | Evidence photographs incidentally capture a customer's home, screen or documents | `DS-06` | 5 | 3 | **H** | `LG-008` `P-01` risk disclosure; `MM-002` redaction standard | ● |
| `TH-062` | Call recordings accessed outside quality purpose | `DS-06` | 3 | 4 | **H** | `SEC-C-016`; `T5`; `SEC-C-041` | ● |

### 6.6 Denial of service (`TH-063`…`TH-074`)

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-063` | Volumetric DDoS against public portals | `TB-1` | 3 | 3 | **M** | `Z0` absorption; `SEC-C-054` | ● |
| `TH-064` | Application-layer DoS through expensive search or report endpoints | `P-04`,`P-05` | 4 | 3 | **H** | Quotas; `SEC-C-059` latency budget | ● |
| `TH-065` | **Introspection endpoint saturated, taking every request path with it** | `P-03` | 3 | 5 | **H** | `SEC-C-060` ≥ 99.99%, short-TTL cache | ◐ |
| `TH-066` | `Z7` session flood degrading remote-support capacity for managed clients | `Z7` | 2 | 3 | **M** | Per-engineer session limits | ◐ |
| `TH-067` | Account-lockout abuse — an attacker locks out staff accounts deliberately | `P-03` | 4 | 3 | **H** | Rate-limit + risk-based rather than hard lockout | ◐ |
| `TH-068` | Storage exhaustion via unbounded upload | `DS-06` | 3 | 3 | **M** | Size limits; quota per party | ● |
| `TH-070` | Event-broker backlog stalling settlement and notification | `DF-09` | 3 | 3 | **M** | DLQ, replay (`AR-009`) | ● |
| `TH-071` | Residency service unavailable, blocking every `S3` read estate-wide | `P-19` | 3 | 4 | **H** | Degraded mode: operate **without** the sensitive fields | ● |
| `TH-072` | Vault unavailable, preventing new leases and new deployments | `DS-10` | 2 | 4 | **M** | Lease TTL sizing; `SC-001` §12 | ● |
| `TH-073` | Audit store write failure blocking transactions (**fail-closed by design**) | `DS-07` | 3 | 3 | **M** | Accepted consequence of `SC-001-D-06`; sized in `PE-006` | ● |
| `TH-074` | Ransomware encrypting `DS-02`/`DS-06` with no immutable backup | `DS-13` | 2 | 5 | **H** | `SEC-DR-04` | **✖** |

### 6.7 Elevation of privilege (`TH-075`…`TH-083`)

`TH-075` in §6.1.

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-076` | Standing administrative rights abused — no elevation required because none was removed | `EE-5` | 3 | 5 | **H** | `SEC-C-034` no standing rights | ◐ |
| `TH-077` | **Self-approval of an access request** | `EE-5`,`P-05` | 3 | 4 | **H** | `SOD-09`, `SEC-C-037` | ● |
| `TH-078` | Privilege accumulation through the **mover** path — old role never revoked | `EE-5` | 4 | 4 | **H** | `SEC-C-028` atomic revoke-and-grant | ● |
| `TH-079` | Delegation used to acquire an incompatible duty combination temporarily | `P-05`,`P-06` | 3 | 4 | **H** | `SEC-C-023` runtime SoD — **the reason runtime evaluation is authoritative** | ● |
| `TH-080` | **`R60`/`R49`/`R32` identifier ambiguity means a rule written against one does not apply to a user granted another** | `P-05` | 3 | 4 | **H** | `SC-004` §4 ruling; `R60` retired | ● |
| `TH-082` | An unregistered role (`R39`–`R50`) granted with no defined permission set, defaulting wide | `P-05` | 4 | 4 | **H** | `SC-004` §4 — 50-role register | ◐ |
| `TH-083` | **`R38` carries 17 external sub-identities under one identifier**, so a rule for couriers applies to auditors | `EE-4`,`P-05` | 4 | 4 | **H** | `SC-004` §4 sub-typing `R38.1`…`R38.17` | ◐ |

### 6.8 Business-surface and privacy threats (`TH-084`…`TH-097`)

`TH-084`, `TH-088`, `TH-091`, `TH-094` in §6.1.

| ID | Threat | Element | L | I | R | Control | St |
|---|---|---|:--:|:--:|:--:|---|:--:|
| `TH-085` | Recovered data used as model training or retrieval data | `P-14` | 3 | 5 | **H** | `BRU-DTS-14` prohibition; `BRU-CAI-12` | ● |
| `TH-086` | Data purged before its agreed date, or retained past it | `P-05` | 3 | 4 | **H** | `SEC-C-050`; `LG-009`; `BRU-SEC-23` legal hold | ◐ |
| `TH-087` | Destruction gate bypassed — a device proceeds to resale without a certificate | `M06`,`M14`,`M18` | 3 | 5 | **H** | `BRU-DTS-09` hard gate, **fails closed** | ● |
| `TH-089` | NID or KYC document harvested by an insider with legitimate but broad access | `DS-08` | 3 | 5 | **H** | `T5` allow-list, step-up, per-read log, `SEC-C-042` | ◐ |
| `TH-090` | **Marketplace collusion — approve a seller and approve their payout** | `EE-5` | 3 | 4 | **H** | `SOD-06`; `SEC-C-022`/`-023` | ● |
| `TH-092` | **Linkability** — an "anonymised" transcript corpus re-identified through order references, device serials or rare fault text | `P-14`,`DS-02` | 4 | 4 | **H** | `SC-003` anonymisation standard | **✖** |
| `TH-093` | **Identifiability** — the resident key becomes a de-facto identifier if it is derived from, or correlatable with, a natural identifier | `P-19` | 3 | 5 | **H** | `AR-001` §8.3: opaque, non-reversible resident key | ● |
| `TH-095` | Sub-processor of a processor receives personal data undisclosed and uncontracted | `EE-7` | 4 | 4 | **H** | `NFR-098`; `LG-012` §4.6 — **register does not exist** | ◐ |
| `TH-096` | **Detectability** — an attacker infers that a specific person is a data-recovery customer from timing, notification or metadata | `P-08`,`M06` | 2 | 4 | **M** | Metadata minimisation; `SC-003` | ◐ |
| `TH-097` | A DSR erasure is executed against records under legal hold, destroying evidence | `P-17` | 3 | 4 | **H** | `BRU-SEC-23` legal hold overrides erasure | ● |

---

## 7. OWASP Top 10:2025 Coverage

The estate contains **no reference to any OWASP Top 10 edition**. Introduced here so `SC-005` and
`QA-007` have a shared vocabulary with the industry.

| 2025 category | Threats in this register | Weakest position |
|---|---|---|
| `A01` Broken Access Control | `TH-021`, `TH-049`–`TH-052`, `TH-077`–`TH-083` | **The estate's dominant risk class.** 13 threats, most rated H or C |
| `A02` Security Misconfiguration | `TH-038`, `TH-057`, `TH-061` | `PE-004` policy check does not exist yet |
| **`A03` Software Supply Chain Failures** *(new in 2025)* | `TH-075`, `TH-094` | **Nothing under version control** (`PGD-A2-15`); no SBOM; no artefact signing |
| `A04` Cryptographic Failures | `TH-088`, `TH-040`, `TH-046` | `SC-006` does not exist yet |
| `A05` Injection | `TH-003`, `TH-015`, `TH-016` | ORM reduces SQL injection materially; XSS on 6 Next.js surfaces is the live risk |
| `A06` Insecure Design | `TH-017`, `TH-090`, `TH-092` | **This document is the remediation** for the absence of design-stage threat analysis |
| `A07` Authentication Failures | `TH-001`–`TH-014` | MFA enforcement lives in a table, not a realm (`TH-005`) |
| `A08` Software and Data Integrity Failures | `TH-031`–`TH-033`, `TH-036` | No immutable backup (`OP-02`) |
| `A09` Logging and Alerting Failures | `TH-041`–`TH-045`, `TH-054` | Log content specified in `SC-010`; **alerting has no SIEM** (`SEC-CON-03`) |
| **`A10` Mishandling of Exceptional Conditions** *(new in 2025)* | `TH-053`, `TH-037`, `TH-071`, `TH-073` | `SC-001` §12 states failure modes — **the estate's strongest position in this table** |

---

## 8. Abuse Case Register

A threat says *what can go wrong*. An abuse case says *what a specific adversary does, in order,
to make it go wrong* — which is what a developer and a tester can act on. 32 cases.

### 8.1 Marketplace and external party (`AB-01`…`AB-08`)

| ID | Adversary | Abuse case | Threats | Test obligation |
|---|---|---|---|---|
| `AB-01` | Fraudulent seller | Registers with borrowed KYC documents, wins jobs, collects customer contact data at scale under `EA-04`, never completes the work | `TH-013`, `TH-051` | KYC verification; `EA-04` **time-bound** contact visibility after completion |
| `AB-02` | Competitor posing as a seller | Enumerates job volumes, pricing and customer density by branch to derive commercial intelligence | `TH-051`, `TH-052` | Rate limit; no aggregate endpoint for a `T4`-scoped identity |
| `AB-03` | Seller | Changes bank details immediately before a payout run | `TH-013` | **Step-up + cooling period + notification to the previous contact point** |
| `AB-04` | Colluding pair — seller and operations officer | Seller onboarded and payouts approved by the same internal actor | `TH-090` | `SOD-06` runtime enforcement; controlled violation attempt per `BRU-GRC-09` |
| `AB-05` | Authenticated customer | Reads another customer's invoice by substituting the id in a direct API call, having observed the portal filter its own list | **`TH-021`** | **Remove the BFF filter and re-run the request.** `EP-4` must return zero rows |
| `AB-06` | Corporate portal user | Widens scope by supplying another company's id in a request parameter | `TH-050` | `EA-11` — scope from credential, never from parameter |
| `AB-07` | External API consumer | Requests a broader OAuth scope than the credential grants, or reuses a token across API families | `TH-021`, `TH-008` | Per-consumer scope; cross-family token rejection |
| `AB-08` | Courier partner | Uses the delivery interface to enumerate customer addresses beyond assigned consignments | `TH-051` | `EA-07` minimum-data; `R38` sub-typing (`TH-083`) |

### 8.2 Insider and privilege (`AB-09`…`AB-16`)

| ID | Adversary | Abuse case | Threats | Test obligation |
|---|---|---|---|---|
| `AB-09` | Branch agent | Looks up a public figure's, a neighbour's or an ex-partner's service history — **the most common real-world privacy breach in a service business** | `TH-049`, `TH-089` | `T2` isolation; access logging; **anomaly detection on lookups without a linked work item** |
| `AB-10` | IT administrator | Grants themselves a role, performs an action, revokes it, and relies on the elevation window closing before review | `TH-076`, `TH-077` | `SOD-09`; elevation recorded independently of the elevated session |
| `AB-11` | Departing employee | Bulk-exports the customer or price list in the notice period | `TH-044`, `TH-058` | `SEC-C-042` approval + rate limit; export anomaly alerting on notice-period identities |
| `AB-12` | Finance officer | Creates a vendor and approves its invoice | `TH-079` | `SOD-01` at assignment **and** transaction |
| `AB-13` | Manager | Confirms all access in a certification cycle without reading it — **rubber-stamping defeats the control while reporting 100% compliance** | `TH-078` | Sampling by internal audit; **flag zero-revocation certifications as an anomaly** |
| `AB-14` | Developer | Uses a production data extract on a laptop to reproduce a defect | `TH-037`, `TH-058` | `SEC-NP-1`; egress control; `LG-020` acceptable use |
| `AB-15` | Data services technician | Browses recovered customer data outside the assigned case | **`TH-084`** | `BRU-SEC-03` case-scoped; dual control; per-access log |
| `AB-16` | HR officer | Reads salary or medical data outside their assigned scope | `TH-089` | Field permissions; `R46` sole access to medical detail |

### 8.3 Remote support and the organisational boundary (`AB-17`…`AB-20`)

| ID | Adversary | Abuse case | Threats | Test obligation |
|---|---|---|---|---|
| `AB-17` | Attacker with an `R13` credential | Opens remote sessions into multiple client estates, pivoting from 1000FiX into third-party networks | **`TH-069`** | MFA **every session**; agreement scope; recording; per-client alerting on unusual session patterns |
| `AB-18` | Remote support engineer | Copies customer data out of a client estate into `Z2` unclassified | `TH-058` | File-transfer control; classification on ingress; `LG-016` consent terms |
| `AB-19` | Requester abusing the DSR channel | Submits DSRs at volume to harvest data, or to map who exists in the system | **`TH-014`** | Identity verification before assembly; rate limit; **a DSR is not a bulk-export bypass** |
| `AB-20` | Overseas vendor engineer | Views a screen containing residency-classified data during a support session — **a transfer, not a viewing** | `TH-047`, `TH-069` | `LG-012` `RD-R9`; `Z7` origin restriction; `TR-07` registration |

### 8.4 Residency and regulatory (`AB-21`…`AB-26`)

| ID | Adversary / actor | Abuse case | Threats | Test obligation |
|---|---|---|---|---|
| `AB-21` | **Ordinary developer, no hostility** | Adds an NID field to a regional model because the ORM allowed it | **`TH-047`** | **Write-time failure**, not a warning. `QA-007` must attempt the write and assert the transaction aborts |
| `AB-22` | Ordinary operator | Adds a `Z3` search index over a `Z4`-backed view for performance | `TH-048` | `SEC-DC-3`; schema review gate in `SC-005` |
| `AB-23` | On-call engineer at 02:00 | Restores `Z4` into the regional environment to meet RTO | **`TH-055`** | `SEC-DR-02`; the resident target must **exist** so the choice never arises |
| `AB-24` | Analytics engineer | Joins a `Z4`-derived key into a regional warehouse, re-creating identifiability | `TH-093`, `TH-056` | Opaque resident key; `DA-00x` propagation rules |
| `AB-25` | Content author (W2) | Mines contact transcripts to build the FAQ bank before the lawful basis is confirmed | **`TH-091`** | `PI-03` — `P-14` is **provisional and not operative**; a build-time gate, not a policy note |
| `AB-26` | Marketing | Uses service-notification contact points for campaign sends | `TH-059` | `P-04` vs `P-05` basis separation; consent register |

### 8.5 Platform, supply chain and availability (`AB-27`…`AB-32`)

| ID | Adversary | Abuse case | Threats | Test obligation |
|---|---|---|---|---|
| `AB-27` | Supply-chain attacker | Publishes a malicious version of a transitively depended-on package pulled during a `Z5` build | **`TH-094`** | SCA in CI; pinned versions; SBOM; **`Z5` egress allow-list covers registries** |
| `AB-28` | Attacker with CI credentials | Modifies a pipeline definition to deploy an unreviewed artefact | **`TH-075`** | Signed artefacts; protected branches; **four-eyes on pipeline change** |
| `AB-29` | Attacker | Triggers the account-lockout policy across branch accounts on a Sunday close | `TH-067` | Risk-based rather than hard lockout |
| `AB-30` | Attacker | Floods the public webhook receiver with forged events to corrupt state or exhaust capacity | `TH-010`, `TH-064` | Signature verification **before** processing; per-source quota |
| `AB-31` | Ransomware operator | Encrypts `DS-02` and `DS-06`, then the backups reachable from the same account | **`TH-074`** | `SEC-DR-04` immutable copy outside the provider account |
| `AB-32` | Attacker with `Z5` foothold | Reads Vault to obtain every downstream credential at once | `TH-008`, `TH-058` | Vault audit; short leases; **`Z5`→`Z4` denial limits the prize** |

---

## 9. Coverage Analysis

### 9.1 Threats whose control exists in specification and is buildable — 39 (●)

**89 of 97 threats — 39 ● plus 50 ◐ — map to a named control** in `SC-001` §9.2 or to a named
requirement in `M29`, `05-04` or `05-06`. **That part is genuinely good news**: the estate's
*requirement* quality is high, and most of what a threat model would normally recommend has already
been specified somewhere.

**39 of those controls are buildable today** — the specification is complete and a developer could
start. The remaining 50 are §9.2's population, and the distinction is the point of the ● / ◐ split:
a reader who sees "89 threats have a control" concludes the system is defended, when for 50 of them
the control is a sentence in a document that has no build behind it.

### 9.2 Threats whose control is specified but does not exist — 50 (◐)

The population that matters, because a specified control reads as a present control in every
downstream document.

| Threat | Control specified | Why it does not exist | Owner | Needed by |
|---|---|---|---|---|
| `TH-005`, `TH-082`, `TH-083` | Role register to `R50`; `R38` sub-typing; MFA in the realm | 50 profiles unauthored (`OP-10`) | `SC-004` | **W1** |
| `TH-035`, `TH-049`, `TH-050`, `TH-051` | Record rules per tier | Profiles and negative tests unauthored | `SC-004`, `QA-007` | **W1** |
| `TH-047`, `TH-048`, `TH-056` | Residency service and classification | `CD-233` not built; classification not in the model | `SC-007`, `DA-002` | **W1** |
| `TH-053`, `TH-054` | Redaction at emission | Logging standard unwritten | `SC-010` | W2 |
| `TH-058`, `TH-057` | Egress allow-list; storage policy | 8 transfers unregistered; no policy check | `SC-007`, `PE-004` | W1 |
| `TH-069`, `TH-042`, `TH-036` | `Z7` controls; session recording | `Z7` newly declared; `M05` at W5 | `SC-001`, `PE-001` | W5 |
| `TH-075`, `TH-094` | SSDLC and SCA gates | No pipeline; **nothing under version control** | `SC-005`, `PE-004` | **W1** |
| `TH-084`, `TH-088`, `TH-089` | Field encryption; `T5` step-up | `SC-006` unwritten | `SC-006` | W2 |
| `TH-095` | Sub-processor register | **Does not exist** (`LG-012` `O-05`) | `SC-008` | W2 |

### 9.3 Threats with no control at any altitude — 8 identifiers, 5 classes (✖)

| Threat | Why nothing covers it | Consequence of leaving it | Escalated to |
|---|---|---|---|
| **`TH-055`** Cross-border restore of `Z4` | **No Bangladesh-resident DR target exists**, and the alternative is a regulatory act (`OP-01`) | An engineer chooses between RTO and statute during an outage | `GV-005` `RSK-SC-01`; `SC-007`; `PE-007` |
| **`TH-081`** / `TH-045` IdP outage with no break-glass; break-glass used silently | **Break-glass is documented and does not exist** (`OP-08`) — so neither the path nor its loudness exists | Improvised privileged access under Sev1 → unattributable production change | `GV-005` `RSK-SC-02`; `SC-011` §10 |
| **`TH-091`** / `TH-092` Transcript mining without a lawful basis; re-identification | **Lawful basis unconfirmed** (`HC-01`); no anonymisation standard | Processing at scale on an unverified footing; remedy is deletion of a derived corpus | `GV-005` `RSK-SC-03`; `SC-003` |
| **`TH-074`** / `TH-033` Ransomware with no immutable backup | **No immutable copy outside the provider account** (`OP-02`) | No assured recovery path for the scenario most likely to occur | `GV-005` `RSK-SC-04`; `PE-007` |
| **`TH-059`** Third-party tags collecting personal data | **`TR-05` unregistered**; no CSP standard published | Undisclosed processing on customer-facing surfaces | `GV-005` `RSK-SC-05`; `SC-003`, `UX-00x` |

> **Counted as 8 threat identifiers grouped into 5 classes**, because a single remediation closes
> each group: `TH-081`/`TH-045` (break-glass), `TH-091`/`TH-092` (lawful basis and anonymisation),
> `TH-074`/`TH-033` (immutable backup). `TH-055` and `TH-059` stand alone. **The five classes are
> the five risks escalated in §11.** *(The first issue stated "4 classes, 6 identifiers" and omitted
> `TH-045` — corrected during the Category 05 audit, `SCA-12`.)*

### 9.4 Threats that confirm an existing audit finding — 17

`TH-035`, `TH-047`, `TH-048`, `TH-055`, `TH-058`, `TH-069`, `TH-074`, `TH-075`, `TH-080`,
`TH-081`, `TH-082`, `TH-083`, `TH-084`, `TH-091`, `TH-094`, `TH-095`, `TH-059` — mapping to
`C-05`, `HC-01`, `OP-01`, `OP-02`, `OP-08`, `OP-10`, `H2-07`, `A3-17`, `A3-20`, `PGD-A2-15`.

> **`SEC-TM-1`.** That 17 of 97 threats independently re-derive an existing open finding is
> **evidence the findings are real**, not evidence of duplication. A threat model that surfaced
> only new items would suggest the audits had missed the structural risks; one that surfaced only
> old items would suggest the model added nothing. Both populations are present.

---

## 10. Privacy Threats

STRIDE is a security taxonomy; four privacy harms have no STRIDE equivalent and would be missed.
Category names borrowed from LINDDUN. **Harm to data subjects is assessed in `SC-003`**; this
section covers the harms that are *properties of the system*.

| Category | Threat | Where it arises | Position |
|---|---|---|---|
| **Linkability** | `TH-092` — an anonymised corpus is re-identifiable through order references, device serials or rare fault text | `P-14`, `DS-02` | **Open.** No anonymisation standard exists. `SC-003` must set one, and it must be tested, not asserted |
| **Identifiability** | `TH-093` — the resident key becomes a de-facto identifier | `P-19` | **Closed by design.** `AR-001` §8.3 requires an opaque key carrying no personal information and not reversible to a natural identifier. **`QA-007` must test the property, not read the sentence** |
| **Non-repudiation as harm** | An immutable audit trail records that a named individual exercised an erasure right — the record of the erasure outlives the erased data | `DS-07`, `P-17` | **Accepted with justification.** `NFR-095` requires 5-year processing records; the audit entry retains the *fact and basis*, never the erased content. Stated in `SC-003` and in `LG-008` |
| **Detectability** | `TH-096` — an observer infers that a person is a data-recovery customer from notification timing or metadata | `P-08`, `M06` | **Partially open.** Metadata minimisation is specified nowhere. `SC-003` to assess; low likelihood, real impact for `M06` customers |

---

## 11. Residual Risk and Hand-Off to `GV-005`

Five risks are handed to the RAID register. They are **programme risks with engineering
consequences**, not engineering risks — none can be closed inside Category 05.

| ID | Risk | Rating | Owner | Treatment | Trigger that makes it an issue |
|---|---|:--:|---|---|---|
| `RSK-SC-01` | No lawful DR path for `Z4` (`TH-055`) | **Critical** | CTO with Legal | Provision a Bangladesh-resident DR target, **or** obtain the Authority position in writing with a pre-documented safeguard | Any `Z4` outage; or W2 gate reached without either |
| `RSK-SC-02` | Break-glass does not exist (`TH-081`) | **Critical** | CTO with Security Lead | Establish vault path, sealed envelope, two signatories, quarterly test | Any IdP incident; W1 go-live |
| `RSK-SC-03` | Transcript mining without confirmed lawful basis (`TH-091`, `TH-092`) | **Critical** | Legal Counsel with CDO | Confirm basis and anonymisation standard **before** W2 collection begins | First `HC-015` extraction |
| `RSK-SC-04` | No immutable backup outside the provider account (`TH-074`) | **High** | CTO | Provision immutable copy; schedule first restore test | Any ransomware indicator |
| `RSK-SC-05` | Third-party tags and sub-processors unregistered (`TH-059`, `TH-095`) | **High** | CDO with Legal | Populate `LG-012` §4.5 and §4.6 registers; publish CSP standard | First external portal go-live |

**Accepted elsewhere, named so they are not assumed covered here:** physical intrusion, social
engineering and phishing, insider recruitment, and coercion. These are `LG-021` `IS-07`/`IS-12`
and HR controls. **`LG-021` §4.12.4 records that the training vehicle (`TR-025`) does not exist**,
so the accepting document currently has no delivery mechanism — recorded as `SC-001` `SEC-E-06`.

---

## 12. Attack Trees

Three outcomes justify a tree, because each has multiple independent paths and the cheapest path
is not the obvious one.

### 12.1 Goal — obtain residency-classified data at scale

```
GOAL: bulk NID / biometric / KYC extraction
├── A. Through the application
│   ├── A1 compromise an R33/R02 identity ......... blocked: MFA + step-up + T5 allow-list
│   ├── A2 exploit a record-rule defect (TH-035) .. ◐ OPEN until profiles + negative tests exist
│   ├── A3 abuse the DSR channel (AB-19) .......... blocked: identity verification + rate limit
│   └── A4 abuse a bulk export (AB-11) ............ blocked: approval + log + rate limit
├── B. Around the application  ★ CHEAPEST PATH
│   ├── B1 read a Z3 cache/index/log copy (TH-048)  ◐ OPEN until SEC-DC-2/-3/-4 are built
│   ├── B2 read a non-prod environment (TH-037) ... blocked: masking inside the clone job
│   └── B3 read a backup or DR replica (TH-033) ... ✖ OPEN — no immutable copy, no Z4 DR target
├── C. Through the platform
│   ├── C1 Z5 shell into Z4 ....................... blocked by design: Z5→Z4 denied (§5.5)
│   ├── C2 CI/CD deploy of exfiltrating code ...... ◐ OPEN (TH-075) — no VCS, no signing
│   └── C3 Vault compromise for Z4 keys ........... partial: keys in BD, separate material
└── D. Through people
    ├── D1 insider with case access (AB-15) ....... partial: dual control + per-access log
    └── D2 coercion / recruitment ................. accepted elsewhere (LG-021 IS-12)
```

> **The cheapest path is `B`, and it does not involve an attacker defeating a single security
> control.** It involves an engineer creating a copy for a good reason. This is why `SEC-DC-2`,
> `-3` and `-4` are architectural rules rather than operational guidance, and why `SC-007` must
> make copy-creation *fail* rather than *warn*.

### 12.2 Goal — commit and conceal financial fraud

```
GOAL: extract funds and survive the close
├── A. Vendor fraud: create vendor + approve invoice ...... SOD-01 hard block
├── B. Purchase fraud: PO + receipt + invoice approval .... SOD-02 hard block (any two)
├── C. Payroll: process + approve .......................... SOD-03 hard block
├── D. Marketplace: approve seller + approve payout ........ SOD-06 hard block
├── E. Cash: handle + reconcile ............................ SOD-12 hard block
├── F. ★ Acquire the combination through DELEGATION ....... TH-079 — runtime SoD is
│                                                             the ONLY control that sees this
├── G. ★ Acquire it through a MOVER transition ............ TH-078 — atomic revoke-and-grant
├── H. ★ Acquire it through an UNREGISTERED role .......... TH-082 — R39–R50 have no
│                                                             permission sets, so no SoD rule
│                                                             evaluates against them
└── I. Conceal by editing the audit trail .................. TH-031 — insert-only + hash chain
```

> **Paths F, G and H are why `SEC-SOD-1` makes runtime evaluation authoritative, and why `TH-082`
> is rated High rather than Medium.** An unregistered role is not merely undocumented — it is
> **invisible to the SoD engine**, because a rule is expressed over permission sets that do not
> exist for it.

### 12.3 Goal — reach a managed-services customer's network

```
GOAL: pivot from 1000FiX into a client estate
├── A. Compromise an R13 identity (15–40 people) .......... MFA + step-up per session
│    └── ★ one credential reaches MANY client organisations — TH-069
├── B. Compromise the M05 remote-support platform itself ... ◐ W5; Z7 controls
├── C. Abuse a legitimate session (AB-18) ................. recording + file-transfer control
├── D. Reach a client with no live agreement .............. agreement-scoped destinations
└── E. Supply-chain: compromise the RMM agent update ...... TH-094 — SCA + pinning
```

> **This tree is the one an enterprise client's security team will ask to see**, because its
> outcome is *their* breach, not 1000FiX's. `SEC-C-064` and `SC-001` `Z7` exist because of it.

---

## 13. Maintenance and Re-Modelling Triggers

A threat model issued once and never revisited is a document, not a control. **ISO 27001 A.8.25
requires security in every development stage**, which means this model is re-run, not archived.

| # | Trigger | Action | Owner |
|---|---|---|---|
| `RM-01` | A **new trust boundary** or zone is introduced | Full re-model of the affected boundary | Security architect |
| `RM-02` | A **new external population** or `R38` sub-type is onboarded | New abuse cases; re-rate `EA-*` threats | Security architect |
| `RM-03` | **Each wave gate** | Re-rate every H and C threat; confirm ◐ controls that became ● | CISO; `GV-009` evidence class |
| `RM-04` | A new integration is added to the `Z6` allow-list | Threat-assess the destination; register the transfer | CDO |
| `RM-05` | A **security incident** occurs | Add the realised threat if absent; re-rate its class | `SC-011` post-incident review |
| `RM-06` | A penetration-test finding has **no corresponding threat** here | Add it; the model was incomplete and the gap is recorded | `SC-009` |
| `RM-07` | OWASP Top 10 or ASVS publishes a new edition | Re-map §7; re-verify `verified_on` | Security architect |
| `RM-08` | The **legal opinion on residency** (`D-13`) is returned | Re-model `TB-5` and the `Z4` threat set | CDO |

---

## 14. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-002-D-01` | Risk scoring method | DREAD · CVSS · L×I with anchors | **L×I with published anchors** | DREAD is not reproducible between analysts; CVSS scores vulnerabilities, not design threats | §4 anchors must be re-used by `SC-009` so ratings are comparable |
| `SC-002-D-02` | Modelling granularity | Per module (67) · per zone (7) · per DFD element (59) | **Per DFD element** | Per-module produces 67 near-identical models; per-zone is too coarse to find `TH-021` | 59 elements is the maintenance unit; `RM-01`…`RM-08` keep it current |
| `SC-002-D-03` | Include privacy threats? | STRIDE only · full LINDDUN · borrow four categories | **Borrow four** | Full LINDDUN duplicates `SC-003`; STRIDE alone misses linkability and detectability entirely | §10 is explicitly partial and defers to `SC-003` |
| `SC-002-D-04` | Rate threats whose control does not exist as if it did? | Yes (design rating) · No (current-state rating) | **Rate current state; mark control status ◐/✖** | A design rating tells a reader the system is safe today when it is not built | 19 ◐ and 4 ✖ are visible rather than averaged away |
| `SC-002-D-05` | Include fraud/SoD paths as security threats? | No — finance controls · Yes | **Yes** | `SOD-01`…`SOD-12` are enforced by the permission engine; a fraud path is a privilege-escalation path | §12.2 exposed paths F, G, H, which the finance framing does not surface |

---

## 15. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Who ratifies threat ratings in the absence of a CISO? | Design Authority | **Now** | §11 acceptance; `GV-005` entries |
| `Q-02` | What anonymisation standard discharges `TH-092`, and how is it tested? | CDO with Legal | **W2** | `RSK-SC-03`; `HC-015` |
| `Q-03` | Is `R13` remote support permitted from outside Bangladesh at all? | CDO with Legal | W5 | `TH-069`; `AB-20`; `Z7` origin restriction |
| `Q-04` | Does the marketplace require seller identity verification beyond KYC documents (liveness, register check)? | CCO with CDO | W2 | `AB-01`; `TH-013` |
| `Q-05` | Which threats does the programme **accept** rather than treat, and who signs? | CTO with CFO | W1 gate | §11; `GV-009` gate evidence |
| `Q-06` | Is a SIEM funded, or does `A09` alerting remain a manual review? | CTO with CFO | W2 | `TH-066`, `TH-054`; `SC-001` `Q-07` |

---

## 16. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every element in §3.2 has STRIDE applied per its type | §5 mapping; §6 register |
| `AC-02` | Every threat has likelihood, impact, rating and control status | §6 — 97 rows, 5 columns |
| `AC-03` | Threats with **no** control are stated, not omitted | §9.3 — 8 identifiers in 5 classes, escalated in §11 |
| `AC-04` | Threats whose control does not yet exist are distinguished from those whose control does | §6 `St` column ● / ◐ / ✖; §9.2 |
| `AC-05` | Every abuse case has a test obligation `QA-007` can act on | §8 — 32 cases, 32 obligations |
| `AC-06` | The six unusual surfaces each have dedicated abuse cases | §8.1 marketplace · §8.3 remote support · `AB-15` recovered data · `AB-30` webhook · `TH-088` biometric · §8.4 residency |
| `AC-07` | Residual risk is handed to `GV-005` with owner and trigger | §11 — 5 risks |
| `AC-08` | Re-modelling triggers are defined | §13 — 8 triggers |
| `AC-09` | Rating method is reproducible by a second analyst | §4 anchors; `SC-002-D-01` |
| `AC-10` | `SC-009` can derive pen-test scope | §9.3, §12 attack trees |

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` | Boundaries, elements, controls |
| Upstream | `AR-001` | Deployment and runtime views |
| Upstream | `DA-002` | PII flags on fields (Category 03, **authored concurrently**) |
| Downstream | `SC-003` | §10 privacy threats; `TH-091`, `TH-092` |
| Downstream | `SC-004` | `TH-080`, `TH-082`, `TH-083` — the role model |
| Downstream | `SC-005` | §8 abuse cases become abuse unit tests; §7 ASVS binding |
| Downstream | `SC-006` | `TH-088`, `TH-046`, `TH-040` |
| Downstream | `SC-007` | `TH-047`, `TH-048`, `TH-055`, `TH-093` |
| Downstream | `SC-009` | §9.3 and §12 set pen-test priority |
| Downstream | `SC-010` | `TH-031`, `TH-032`, `TH-043`, `TH-054` |
| Downstream | `SC-011` | `TH-081`; `RM-05` |
| Downstream | `QA-007` | **The security test basis** — §8 and §9 |
| Downstream | `GV-005` | §11 residual risks |
| Lateral | `../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_*.md`, `M06_*.md` | `Z7` and recovered data |
| Lateral | `../../1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M12_*.md` | Marketplace abuse surface |
| Lateral | `../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_*.md` | Fraud paths for §12.2 |

---

## 18. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./SC-001_Security_Architecture_Document.md` · `./SC-003` … `./SC-011` ·
`../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md`, `05-04_*.md`, `05-06_*.md` ·
`../../project_content/_AUDIT/AUDIT-010_Category_09_HC_Content_Audit.md` (`HC-01`) ·
`../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md` (`OP-01`, `OP-02`, `OP-08`, `OP-10`) ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-012_*.md`, `LG-016_*.md`, `LG-021_*.md`

**External standards and sources** *(all verified 2026-08-18)*

| Source | Version / date | Used for |
|---|---|---|
| STRIDE | Microsoft threat taxonomy; element-type mapping | §5, §6 |
| ISO/IEC 27001 | :2022 + Amd 1:2024, **A.8.25** | The obligation this document discharges |
| ISO/IEC 27005 | :2022 | §4 scale; §11 residual treatment |
| **OWASP Top 10** | **2025 edition, published 6 November 2025**, finalised January 2026; new `A03` Software Supply Chain Failures, `A10` Mishandling of Exceptional Conditions | §7 |
| **OWASP ASVS** | **5.0.0, 30 May 2025** | Verification binding |
| MITRE ATT&CK | Enterprise matrix, current release | Technique reference on 14 threats |
| LINDDUN | Privacy threat taxonomy | §10 category names only |
| NIST SP 800-154 | Data-centric threat modelling (draft) | Method inspiration for §10, **not cited as an obligation** |
| DREAD | — | **Explicitly not used**; rationale in §2.1 |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. First threat model in the programme's history. 59 elements, 9 boundaries, 97 threats, 32 abuse cases, 3 attack trees; 8 threats in 5 classes with no control escalated to `GV-005`. Counts corrected during the Category 05 audit (`SCA-12`) | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-002` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
