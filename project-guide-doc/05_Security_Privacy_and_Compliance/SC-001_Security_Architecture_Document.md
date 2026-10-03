---
id: SC-001
title: Security Architecture Document
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Information Security Officer (unappointed — see §13 Q-01)
approver: Design Authority (constituted under GV-002), countersigned by the CTO
standards_basis: >
  ISO/IEC 27001:2022 + Amd 1:2024 Annex A · ISO/IEC 27002:2022 · ISO/IEC/IEEE 42010:2022 (security
  viewpoint) · NIST SP 800-207 Zero Trust Architecture · OWASP ASVS 5.0.0 · ISO/IEC 27033 (network
  security) · SABSA layered model (structure only)
traces_to: >
  PGD-000 SC-001 · M29 FR-SEC-001…052 · 05-06 §4 NFR-011…015, NFR-061…072 · 05-06 §6.3 NFR-097 ·
  05-04 §2, §4, §5, §8 · AR-001 §8.1, §8.2, §8.3, §9.1 · LG-021 IS-01…IS-13 ·
  audit findings C-05, OP-01, OP-02, OP-08, OP-10, PGD-A3-06
depends_on: AR-001 (trust zones, deployment view) · AR-002 · RQ-006 (NFR set) · GV-002 (approval body)
verified_on: 2026-08-18
priority: P0
needed_by: W1
enumeration_timestamp: 2026-08-18 12:55 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-001 — Security Architecture Document

### Category 05 · Code `SC` · ISO/IEC 27001:2022 Annex A · NIST SP 800-207 · OWASP ASVS 5.0.0

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-001`.
> 2. **`PG-03` Count, do not consult.** Every figure describing the estate was counted from the
>    filesystem at **2026-08-18 12:55 (+06)**. Where a counted figure disagrees with a published
>    one, the counted figure is used and the disagreement is recorded in §2.4.
> 3. **`PG-06` Cite standards.** Conformance and departures are stated in §2.1.
> 4. **`PG-M4` Verify citations.** Every statutory and standards-version claim carries
>    `verified_on: 2026-08-18` and is re-verified in `SC-008`.

---

## 1. Purpose

This document draws the **security structure** of the 1000FiX ERP System: where the trust
boundaries are, what sits inside each one, how a request is authenticated and authorised as it
crosses them, where secrets live, how one branch's data is kept from another's, and which control
answers which ISO 27001 Annex A obligation.

It exists because the programme has **security requirements and no security architecture**. `M29`
specifies 52 functional security requirements. `05-06` §4 specifies 17 security NFRs and §6.3 ten
statutory ones. `LG-021` states 13 security policies. Between a requirement that says *"enforce
branch-level data isolation at the record level"* (`NFR-015`) and a developer writing an
`ir.rule` domain expression, there is a missing artefact: the statement of **which zone the
record lives in, which identity reaches it, through which enforcement point, and what proves it
happened**. That artefact is this one.

It is also the **input to three other documents that cannot start without it**: `SC-002` threat
models against the boundaries drawn here; `PE-001` builds the network from the zone model here;
and `QA-007` derives security tests from the control catalogue in §9.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | The **trust zone model** `Z0`…`Z6` — contents, permitted ingress and egress, and the controls at each boundary |
| 2 | The **enforcement point model** — where an authorisation decision is made, and how many times |
| 3 | **Identity topology at architecture altitude** — the split between Keycloak and the record layer, and why it is a split |
| 4 | **Data isolation architecture** — the `T0`…`T5` tier model realised as record rules, field permissions and the residency service |
| 5 | **Secrets and key-material flow** — from Vault to a running process, and what never holds a secret |
| 6 | **Tenant, entity and branch isolation** for 51+ branches, multiple legal entities and 3 external populations |
| 7 | **Defence in depth** — the layer stack, and the explicit statement of what each layer is *not* trusted to do |
| 8 | The **security control catalogue** `SEC-C-001`…`SEC-C-068`, each mapped to ISO/IEC 27001:2022 Annex A and to the requirement it discharges |
| 9 | **Security architecturally significant requirements** (`SASR`) — the requirements that changed the structure |
| 10 | The **security failure and degradation model** — what the system does when a security component is unavailable |
| 11 | **Zero-trust position** — which NIST SP 800-207 tenets are adopted, which are deferred, and why |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| Per-component threat enumeration and abuse cases | `SC-002` | A threat model needs a boundary model first. This document supplies the boundaries; `SC-002` attacks them |
| DPIA, lawful basis, necessity and proportionality | `SC-003` | Privacy risk is assessed against data subjects, not against the system. Different method, different standard (ISO/IEC 29134:2023) |
| Keycloak realm, client, role and token configuration | `SC-004` | This document says *identity is federated and authorisation is transactional*; `SC-004` says *which realm, which client, which lifetime* |
| Secure coding rules, SAST/DAST/SCA gates | `SC-005` | Build-time controls. This document names the gate as a control; `SC-005` specifies it |
| Algorithms, key lifetimes, rotation schedules | `SC-006` | This document says *where key material flows*; `SC-006` says *what it is and how long it lives* |
| Residency field list, transfer register, Authority notification | `SC-007` | This document places `Z4` in the topology; `SC-007` governs what enters it and what may leave |
| Scan cadence, severity SLA, pen-test scope | `SC-009` | Assurance activity, not structure |
| Log content, immutability mechanism, retention | `SC-010` | This document requires the audit trail as control `SEC-C-041`; `SC-010` specifies it |
| Incident detection, triage and notification | `SC-011` | Response, not architecture |
| Physical and environmental security | `LG-021` IS-07, `M47` | The company's premises are not this system's architecture |
| Network device configuration, firewall rules, IaC | `PE-001`, `PE-004` | This document is the constraint; infrastructure is the realisation |

### 1.2 Intended audience

| Audience | What they use this document for |
|---|---|
| **Security architect / CISO** | The controlling statement of the security structure; the baseline every change is assessed against |
| **Threat modeller (`SC-002`)** | The boundary and element decomposition to enumerate STRIDE against |
| **Platform engineer (`PE-001`, `PE-004`)** | The zone model, the egress rule and the enforcement points to build |
| **Module developer** | §7 — what the platform gives you, and what you are forbidden to re-implement |
| **QA (`QA-007`)** | §9 — the control catalogue is the test basis; a control with no test is an assertion |
| **Auditor, certification body, enterprise client** | §9's Annex A crosswalk, and §11's honest statement of what is not yet evidenced |
| **Regulator (NDMA, NCSA)** | §5 `Z4`, §8 residency enforcement, and the single-enforcement-point argument |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause / section | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 27001:2022 + Amd 1:2024** *(verified 2026-08-18)* | Annex A — 93 controls in 4 themes | §9 maps every architectural control to its Annex A reference; §9.4 states the 21 Annex A controls this architecture **cannot** discharge and names their owner | Amd 1:2024 adds climate-change relevance to clauses 4.1/4.2 and **no new Annex A controls**. It is an ISMS-scope obligation and is discharged by `LG-021`, not here |
| **ISO/IEC 27002:2022** | Control implementation guidance | Used as the implementation reference for each Annex A control named in §9 | — |
| **ISO/IEC/IEEE 42010:2022** | §5 architecture description | This document is the **security viewpoint** of `AR-001`, not a competing architecture. Zones `Z0`…`Z6` and tiers `T0`…`T5` are *inherited*, not re-derived (§2.2) | A standalone SAD would duplicate `AR-001` §8 and the two would drift. `PGD-A3-18` records that drift is this repository's dominant defect class |
| **NIST SP 800-207** | §2 tenets 1–7 | §10 states adoption per tenet with an explicit deferral list | Tenets 5 and 7 (continuous device-posture assessment, full telemetry-driven policy) are **deferred to W6**. The cost is not justified at 800 internal users, and `M29` §4 already records this position |
| **OWASP ASVS 5.0.0** *(released 30 May 2025; verified 2026-08-18)* | 17 chapters, ~350 requirements, 3 levels | §9 adopts **Level 2 as the estate baseline and Level 3 for the four `Z4`-touching and payment paths**. `SC-005` binds ASVS verification to the build gate | **The category overview and the register both cite "OWASP ASVS 4".** ASVS 4.0.3 is superseded. Corrected here; recorded as finding `SCA-03` |
| **ISO/IEC 27033-1/-2** | Network security architecture | §5's zone model, permitted flows and boundary controls follow the 27033 zone/conduit structure | Device-level configuration is `PE-001`'s |
| **SABSA** | Layered contextual→component model | Structure only: §3 (business drivers) → §5 (conceptual zones) → §9 (logical controls) → `PE-001` (physical) | SABSA's full matrix and business attribute profiling are not adopted; the programme has `RQ-006` for quality attributes already |

> **A departure stated plainly.** This document does **not** claim ISO/IEC 27001 certification, and
> no sentence in it may be read as claiming one. `LG-021` §4.1.4 (`CS3`, `O-03`) records that the
> company **does not hold an ISO 27001 certificate**. `NFR-025` requires *alignment*; `NFR-089`
> requires *readiness*. §9's Annex A crosswalk is a design-alignment artefact and is not evidence
> of certification.

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `AR-001` §8.1 | `../02_Architecture_and_Design/AR-001_*.md` | **The six trust zones `Z0`…`Z6`.** Inherited verbatim; this document adds boundary controls, enforcement points and the failure model |
| `AR-001` §8.2, §8.3 | same | The `T0`…`T5` isolation tiers and the split-residency topology, including the `T5`≈`Z4` coincidence |
| `AR-001` §6.1, §9.1 | same | The layer stack, the 16 domain services (`CD-233…248`), and the identity realisation split |
| `M29` §3, §5, §6, §9 | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` | 52 `FR-SEC` requirements, 16 technical functions `T-01`…`T-16`, 25 business rules `BRU-SEC-01`…`-25` |
| `05-04` §2, §4, §5, §6, §8 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_*.md` | Portal access matrix, six isolation tiers, 13 restricted field groups, `SOD-01`…`SOD-12`, `EA-01`…`EA-12` |
| `05-06` §4, §6.3, §6.4 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*.md` | `NFR-011`…`015`, `NFR-061`…`072`, `NFR-090`…`099`, `NFR-086`…`086c` |
| `05-02` §10 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` | Sensitivity classes `S0`…`S3` and the **9-field `S3` inventory** |
| `05-03` §5.1, §5.2 | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-03_*.md` | **12 API families**, `API-01`…`API-10` standards, 47 external integrations |
| `02-05` §9, §10 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | Keycloak 26.x (`TD-07`), Kong 3.x (`TD-08`), Vault-managed secrets, six environments |
| `LG-021` §4.1–§4.14 | `../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md` | The 13-policy ISMS set `IS-01`…`IS-13` and its policy-to-control map — **the human-facing counterpart this document is the engineering counterpart of** |
| `LG-020`, `LG-012` | same directory | Acceptable use; the residency position and its `O-01`…`O-07` open items |
| `SP-006` §4.2–§4.6 | `../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_*.md` | `SOD-01`…`SOD-60`, the collision resolution, and the compensating-control set |
| `OP-009`, `OP-015` | `../../project_content/17_Operations_Support_and_Runbooks/` | Identity runbook and JML content; break-glass design (`OP-08`: does not exist) |

### 2.3 Audit findings this document closes, or contributes to closing

| Finding | Source | How this document responds |
|---|---|---|
| **`C-05` (Critical)** | `00-06` §3 | Contributes. §5 places `Z4` as a first-class zone with a **single reachable path**, making the residency claim architecturally auditable. The statutory analysis is `SC-007`'s |
| **`OP-01` (Critical)** | `AUDIT-017` | Contributes. §12 `SEC-DR-02` fixes as an architectural constraint that `Z4` recovers **only** to a Bangladesh-resident target, so no engineer faces the choice at 02:00. The lawful path is `SC-007`'s to obtain |
| **`OP-02` (High)** | `AUDIT-017` | Contributes. §12 states the `dr` environment's **security** requirements so `PE-002` cannot size it without them |
| **`OP-08` (High)** | `AUDIT-017` | **Closes the architecture half.** §7.6 specifies break-glass as an architectural component with an independent notification path, a sealed credential, and an availability requirement that does not depend on the system it recovers |
| **`OP-10` (High)** | `AUDIT-017` | Contributes. §7.3 fixes the enforcement-point model that access profiles attach to; the 50-role realisation and the profiles are `SC-004`'s |
| **`PGD-A3-06`** | `PGD-AUDIT-003` | **Corrected here.** `AR-001` §9.1 states the target as **46 roles**; the counted position is **50** (`R01`–`R50`), plus `R54`/`R57` undefined and `R60` already retired to `R49`. See §2.4 and `SC-004` §4 |
| **`H2-07`** | `00-07` | Contributes. §2.4 records that `00-07`'s remediation ("eliminate R60 in favour of R32") was **superseded** by the later module-set audit, which created `R49`. Two audits, contradictory remediations; this document rules |
| **`LG-021` `O-09`** | `LG-021` §4.13.6 | Contributes. §9 registers vulnerability discovery as control `SEC-C-057` with a named owner, so `BRU-SEC-21`'s presumed discovery mechanism has an architectural home. The regime is `SC-009`'s |

### 2.4 Enumeration — counted figures, and where they disagree with published ones

Counted at **2026-08-18 12:55 (+06)** across all five repositories.

| # | Figure | **Counted** | Published elsewhere | Disposition |
|---|---|---:|---|---|
| 1 | Files in the workspace | **682** | 610 (`PGD-000` §0.1, 02:06) · 601 (`_CATEGORY_OVERVIEW`) | Counted figure used. The estate moved **610 → 682** in under eleven hours. Fourth recurrence of `AP-17`/`PGD-A1-03`; `RG-08` still unratified |
| 2 | Files in `project-guide-doc/` | **64** | 22 (`FOLDER_STRUCTURE.md` §3) · 58 (`PGD-000`, 03:10) | Counted. **Categories 03 and 04 are being authored concurrently with this one** — `DA-001`…`DA-004` and `IN-001` appeared during authoring |
| 3 | Occurrences of "threat model" **outside** `project-guide-doc/` | **0 files** | "zero occurrences in 601 files" | **Confirmed.** The claim holds for the source estate. Inside `project-guide-doc/` it now appears in 15 files, all of them *forward references to `SC-002`* |
| 4 | Occurrences of "DPIA" outside `project-guide-doc/` | **17 occurrences in 7 files** | "four" (`PGD-000` §5 preamble) | **Published figure is wrong — 4.25× low.** The seven are `RFP`, `AP-012`, `RF-001`, `RF-006`, `RF-010`, `AUDIT-016`, and the content master index. **None is a DPIA**; all are references to one that does not exist. The gap the figure describes is real; the figure is not. Finding `SCA-01` |
| 5 | `FR-SEC` requirements | **52** | 52 (`M29` §1) | ✓ Agrees |
| 6 | Roles in use above `R38` | **`R39`…`R50` = 12** | `R39`–`R46` (`AR-001` §9.1, `00-07` H2-07) · `R39`–`R50` (`_MODULE_SET_AUDIT` A3-17) | **Counted figure used: 50 roles.** `AR-001` §9.1's "46" is superseded. Finding `SCA-02` |
| 7 | Roles used and undefined anywhere | **`R54`, `R57`** (2) | `R54`, `R57`, `R60` (3) | **`R60` no longer appears in any module file** — it survives only in two audit reports. Already retired to `R49`. Two of three closed |
| 8 | `SOD` identifiers used in module files | **`SOD-01`…`SOD-30` = 30** | 12 (`05-04` §6) | `SP-006` registers to `SOD-60`. `05-04` §6 is **18 short** of live usage and 48 short of the register |
| 9 | `S3` restricted fields | **9** (`05-02` §10) | 7 residency-classified (`05-06` §6.4) + 2 proposed (`LG-012` §4.3) | Two different lists, deliberately. §8.4 reconciles them |
| 10 | API families | **12** (`05-03` §5.1) | 12 | ✓ Agrees |
| 11 | External integrations | **47** (`05-03` §2) | 47 | ✓ Agrees. All 47 are `Z6` egress destinations and each needs an allow-list entry (§5.7) |
| 12 | Portals / surfaces | **12** | 12 | ✓ Agrees. **12 of 12 are internet-reachable**; §4.2 counts the external attack surface |

> **`SEC-E-01`. The DPIA count is the finding that matters most in this table.** A published figure
> of "four" invited the reading *some assessment work exists*. Seventeen occurrences across seven
> files, **not one of which is an assessment**, invites the correct reading: the artefact is
> referenced by the RFP, by a disclosure register, by a glossary, by a decision log, by an
> ownership directory and by an audit — six consumers, zero producers. `SC-003` is the producer.

---

## 3. Security Drivers and Context

### 3.1 What this architecture is defending, and against what consequence

Security architecture is only justifiable against a stated consequence. Five are quantified in
the estate, and they set the proportionality that `NFR-097` requires.

| # | Asset | Volume | Consequence of loss | Source |
|---|---|---|---|---|
| **D-1** | **Sensitive personally identifiable data** — NID, passport, TIN, biometric templates, KYC, criminal records | 250,000+ customers/month; 800+ staff; 1,000–3,000 external users | **BDT 25 lakh**, or **BDT 50 lakh** as a significant data fiduciary, plus repeat-violation fines. Enforcement activates **~13 May 2027, inside Wave 4** | `05-06` §6.3; PDPA 2026 |
| **D-2** | **Recovered customer data held in custody** (`M06`) | Content of unknown classification, per case | The data-recovery **business line cannot operate** without provable custody. `BRU-DTS-16`: never replicated to a foreign region | `M06`; `LG-017` |
| **D-3** | **Corporate and brand-partner data** | 500–2,000 corporate users; **17+ brand authorisations** | A single cross-contract exposure ends the contract and the reference. Brand partners audit their authorised service partners | `05-04` §1.7; `M29` §7.2 |
| **D-4** | **Financial integrity** | 51+ branch cash counters; payroll for 800+; marketplace payouts to 500–2,000 sellers | Fraud paths are enumerated: `SOD-01`…`SOD-12` name fictitious vendors, purchase fraud, payroll fraud, revenue leakage, inventory-theft concealment, cash misappropriation | `05-04` §6; `SP-006` |
| **D-5** | **Availability of a system 51+ branches transact on** | ≥ 99.7% 24×7; ≥ 99.9% 09:00–22:00 | `OP-014` exists because *51+ branches cannot stop because a system is down* | `NFR-045`, `NFR-006` |

### 3.2 The abuse surface, counted

This is not a back-office ERP. Counted from the estate at 12:55 (+06):

| # | Surface | Counted | Why it is architecturally significant |
|---|---|---:|---|
| 1 | **Internet-reachable portals and applications** | **12 of 12** | Every surface is an entry point. `P01` alone is sized for 250,000+ customers a month |
| 2 | **API families exposed through the gateway** | **12** | Including a **Partner API on client-credentials** and a public **Webhook receiver** |
| 3 | **External integration destinations** | **47** | Every one is an egress path and a supply-chain dependency |
| 4 | **External seller population** | 500–2,000 | Sellers can **list, bid, transact and be paid**. `SOD-06` exists because approve-seller plus approve-payout is a collusion path |
| 5 | **External party sub-identities on `R38`** | **17** | Vendor, seller, brand partner, courier, recycling partner, external auditor, tax consultant, calibration provider and more — **all currently one role identifier** (`A3-20`) |
| 6 | **Remote-desktop sessions into customer IT estates** | `M05`, MeshCentral/RustDesk | A support tool with reach into third-party networks is a lateral-movement asset for an attacker and a **transfer** for a regulator (`LG-012` `RD-R9`) |
| 7 | **Biometric templates** | 500+ employees | Statutorily sensitive; irreversible if leaked — a password can be changed, a fingerprint cannot |
| 8 | **Recovered customer data in custody** | Per `M06` case | The only asset class in the estate whose *content classification is unknown by design* |
| 9 | **Legal entities / branches / zones needing isolation** | multiple / 51+ / dispatch zones | `NFR-015` isolation is a legal and contractual obligation, not a preference |

> **`SEC-D-01`. The `M05` remote-support surface is the one most often under-weighted.** It is the
> only capability in the estate that gives a 1000FiX identity a live path **into a third party's
> network**. Compromise of a single Remote Support Engineer identity (`R13`, headcount 15–40) is not
> a breach of 1000FiX — it is a breach of every managed-services client simultaneously. §5.6 places
> it in a dedicated egress path with its own controls, and `SC-002` treats it as its own trust
> boundary.

### 3.3 Constraints this architecture is given, not chosen

| # | Constraint | Source | Architectural consequence |
|---|---|---|---|
| `SEC-CON-01` | Identity is **Keycloak 26.x**; gateway is **Kong 3.x** | `02-05` `TD-07`, `TD-08` | The authorisation split in §7 is not a free choice; it follows from having an OIDC provider outside the ORM |
| `SEC-CON-02` | The ERP core is **Odoo 19 CE**, and record rules are the isolation mechanism available | `02-05` `TD-01` | `T0`…`T5` are realised as `ir.rule` domains plus `OCA/operating-unit`; the isolation model must be expressible in that mechanism |
| `SEC-CON-03` | **No commercial security licence is budgeted** | `02-05` §7 | WAF, SIEM, secrets, scanning and PAM must be met from open-source components or from cloud-provider primitives. §9 marks the six controls where this is a material limitation |
| `SEC-CON-04` | **Split residency is mandatory**, and the legal opinion is not yet obtained | `NFR-086`; `DEP-31`/`D-13` | The mechanism is built regardless (`AR-001` §8.3). A change of legal opinion must be a **reclassification, not a redesign** |
| `SEC-CON-05` | **No CISO, DPO or Chief Data Officer is appointed** | `LG-021`; `NFR-096` | Every control in §9 has an owner **role**; §13 `Q-01` records that three of those roles do not exist as people |
| `SEC-CON-06` | The estate is **not under version control** | `PGD-A2-15` | Integrity of the architecture itself is unevidenced. §11 states this rather than assuming it away |

---

## 4. The Security Architecture in One Page

### 4.1 The five structural decisions

Everything else in this document follows from five decisions. They are stated first so a reader
can disagree with the architecture rather than with its details.

| # | Decision | Because | Consequence if reversed |
|---|---|---|---|
| **`SEC-SD-1`** | **Authorisation is transactional, not edge-only.** Record rules and field permissions execute **inside the database transaction**; the gateway check is an optimisation, never the decision | An API-edge check alone is one crafted request away from being wrong. `M29` `T-01` treats an edge-only check as a **defect**, and `API-10`/`M28` `AC-11` tests exactly this | Every one of 67 modules becomes individually responsible for scope enforcement — 67 places to get `NFR-015` wrong |
| **`SEC-SD-2`** | **Identity is federated; authorisation is local.** Keycloak proves *who*; the record layer decides *what*. Keycloak's authorisation services are **deliberately not used** as the permission engine | Business permissions depend on business data — this customer, this branch, this contract. That data is in the ORM, not in the IdP | Permission state duplicates into a second system and the two drift. `M29` §4 rejected this explicitly |
| **`SEC-SD-3`** | **`Z4` is reachable through exactly one component.** The residency service (`CD-233`) is the sole path to Bangladesh-resident data | A rule implemented in one place can be **audited in one place** — which is what a regulator asks for. It also makes `NFR-086a` write-time enforcement mechanically possible | Residency becomes a developer-discipline problem across 67 modules, and `C-05` reopens |
| **`SEC-SD-4`** | **Audit is inherited, never written.** Base-model inheritance and ORM interception; **a module cannot opt out and a developer cannot forget** | Promise 4 of the platform contract. Modules that write their own audit produce inconsistent, incomplete, unqueryable trails | `NFR-014` becomes 67 partial implementations, and `ISO 9001` evidence quality becomes per-module |
| **`SEC-SD-5`** | **No application node reaches the internet except through `Z6`, to an allow-listed destination** | This is what converts `IP-10` (*data leaving the company is minimised and logged*) from an aspiration into a mechanism, and it is the primary exfiltration control | Exfiltration is undetectable, and 47 integration destinations become 47 unmonitored egress paths |

### 4.2 The layered view

```
        ATTACKER                                        REGULATOR / AUDITOR
           │                                                    │
           ▼                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ Z0  PUBLIC EDGE          CDN · WAF (OWASP CRS) · DDoS · bot management       │
│                          Controls: rate limit, bot score, geo rule           │
│                          TRUSTED TO: absorb volume.  NOT TRUSTED TO: decide  │
├──────────────────────────────────────────────────────────────────────────────┤
│ Z1  INGRESS              Kong 3.x · Nginx 1.27                               │
│                          TLS 1.3 termination · OAuth2 introspection ·        │
│                          per-consumer quota · correlation-id injection       │
│                          TRUSTED TO: reject the unauthenticated.             │
│                          NOT TRUSTED TO: establish scope  ◄── SEC-SD-1       │
├──────────────────────────────────────────────────────────────────────────────┤
│ Z2  APPLICATION          Odoo nodes · Next.js nodes · 16 domain services     │
│                          mTLS between services · service identity ·          │
│                          ★ AUTHORISATION DECISION POINT (in-transaction)     │
│                          ★ record rules T0–T5 · field permissions · SoD      │
│                          NO DIRECT INTERNET EGRESS  ◄── SEC-SD-5             │
├───────────────┬──────────────────────────────┬───────────────────────────────┤
│ Z3 DATA       │ Z4 DATA — BANGLADESH         │ Z6 EGRESS                     │
│    REGIONAL   │    RESIDENT                  │    outbound proxy             │
│               │                              │                               │
│ PostgreSQL 16 │ PostgreSQL 16, separate key  │ 47 allow-listed destinations  │
│ +2 replicas   │ material                     │ credential injection ← Vault  │
│ TimescaleDB   │ NID·passport·TIN·biometric·  │ every call logged (IP-10)     │
│ ClickHouse    │ recovered data·KYC·criminal  │                               │
│ Redis·MinIO   │                              │ ★ the ONLY internet path      │
│               │ ★ reachable ONLY via the     │                               │
│ private only  │   residency service CD-233   │                               │
│ no public     │   ◄── SEC-SD-3               │                               │
│ endpoint      │ per-read access logging      │                               │
│               │ step-up auth for human read  │                               │
├───────────────┴──────────────────────────────┴───────────────────────────────┤
│ Z5  MANAGEMENT           CI/CD runners · bastion · Vault · observability      │
│                          restricted source ranges + MFA · session recording  │
│                          NO STANDING ACCESS · break-glass path (§7.6)        │
└──────────────────────────────────────────────────────────────────────────────┘
   CROSS-CUTTING: Keycloak (identity) · Vault (secrets) · OTel→Loki (logs,
                  classified fields redacted AT EMISSION) · residency service
```

### 4.3 How to read the rest of this document

| Section | Answers |
|---|---|
| §5 | Where are the boundaries, and what may cross them |
| §6 | What identity is presented at each boundary |
| §7 | Where is the decision made, and how many times |
| §8 | How is one branch's, one customer's and one seller's data kept apart |
| §9 | Which control answers which obligation, and who owns it |
| §10 | How much zero trust, and which parts are deferred |
| §11 | What is not yet evidenced — stated plainly |
| §12 | What happens when a security component fails |

---

## 5. Trust Zones and Boundary Controls

The six zones are **inherited from `AR-001` §8.1** and are not re-derived. What this section adds
is the **boundary control set**, the **enforcement obligation** at each crossing, and the
**failure behaviour**.

### 5.1 Zone register

| Zone | Contents | Ingress from | Egress to | Data sensitivity present | Owner |
|---|---|---|---|---|---|
| **`Z0`** Public edge | CDN, WAF (OWASP CRS), DDoS, bot management | Internet | `Z1` only | Request metadata only | Platform Engineering |
| **`Z1`** Ingress | Kong 3.x, Nginx 1.27 | `Z0` | `Z2`, `Z3` | `S0`–`S2` in transit | Platform Engineering |
| **`Z2`** Application | Odoo nodes, Next.js nodes, 16 domain services | `Z1` | `Z3`, `Z4`, `Z6` | `S0`–`S3` in memory | Platform Squad |
| **`Z3`** Data — regional | PostgreSQL 16 + 2 replicas, TimescaleDB, ClickHouse, Redis 7, MinIO | `Z2` only | none | `S0`–`S2`; **never residency-classified** | Platform Engineering |
| **`Z4`** Data — Bangladesh resident | Sensitive-data PostgreSQL, separate key material | **`Z2` via `CD-233` only** | none | **`S3` residency-classified** | CDO with Platform Engineering |
| **`Z5`** Management | CI/CD runners, bastion, Vault, observability | Restricted ranges + MFA | `Z2`, `Z3` | Secrets, logs (classified fields redacted) | Platform Engineering |
| **`Z6`** Egress | Outbound proxy to third-party APIs | `Z2` | **Named allow-list only** | `S0`–`S2`; **never `S3`** | Platform Engineering |

### 5.2 The permitted-flow matrix

**Read as: row may initiate a connection to column.** Any cell not marked ● is denied by default
and denied at the network layer, not by application convention.

| From ↓ / To → | `Z0` | `Z1` | `Z2` | `Z3` | `Z4` | `Z5` | `Z6` | Internet |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Internet** | ● | | | | | | | — |
| **`Z0`** | — | ● | | | | | | |
| **`Z1`** | | — | ● | ●¹ | | | | |
| **`Z2`** | | | — | ● | ●² | | ● | **✖** |
| **`Z3`** | | | | — | | | | **✖** |
| **`Z4`** | | | | | — | | | **✖** |
| **`Z5`** | | | ● | ● | ✖³ | — | | ●⁴ |
| **`Z6`** | | | | | | | — | ● |

¹ `Z1`→`Z3` is permitted **only** for gateway session and rate-limit state in Redis. It is not a
data path, and it carries no business object.
² `Z2`→`Z4` is permitted **only** from the residency service `CD-233`. Every other `Z2` workload is
denied at the network layer, so an ordinary Odoo node cannot reach `Z4` even with a valid
credential (`SEC-SD-3`).
³ **`Z5`→`Z4` is denied.** A platform engineer does not get a shell on the resident store. Human
access to `Z4` is through the residency service's audited read path with step-up authentication,
or it does not happen. This is the single most-likely-to-be-argued rule in this document; §5.5
gives the reasoning.
⁴ `Z5`→Internet is permitted for package and image registries **only**, through an allow-list, and
is logged. It is the supply-chain ingress path and is treated as one (`SC-005`).

### 5.3 Boundary controls

| Boundary | Controls at the crossing | Fails how | Requirement |
|---|---|---|---|
| **Internet → `Z0`** | WAF with OWASP Core Rule Set; DDoS absorption; bot management; geo rules; TLS 1.3 | **Fails open to the WAF's own availability** — a WAF outage must not take the estate down. Compensating: `Z1` rate limits are independent | `NFR-068` |
| **`Z0` → `Z1`** | Mutual authentication between edge and ingress; only the edge's egress addresses accepted | Fails closed | `SEC-C-011` |
| **`Z1` → `Z2`** | OAuth 2.0 introspection against Keycloak; per-consumer quota; correlation-id injection; request-size and content-type enforcement; idempotency-key enforcement on writes | **Fails closed** — no valid token, no forward | `API-01`…`API-10`, `NFR-069` |
| **`Z2` → `Z3`** | Private network only; database credentials issued from Vault with short lease; connection from named service identities only; **no public endpoint exists to fail** | Fails closed | `NFR-062` |
| **`Z2` → `Z4`** | **Only `CD-233`.** Per-read access logging; step-up authentication for human-initiated reads; write-time residency classification check; transfer gate on any cross-border move | **Fails closed, and a residency write failure is not retried into `Z3`** | `NFR-086`, `NFR-086a`, `NFR-086b` |
| **`Z2` → `Z6`** | Named allow-list of 47 destinations; credential injection from Vault (the application never holds the credential); full request logging; per-destination rate limit | **Fails closed.** An unlisted destination is refused, and the refusal is a security event | `IP-10`, `SEC-C-045` |
| **`Z5` → `Z2`/`Z3`** | Restricted source ranges; MFA; **no standing access**; time-boxed elevation; privileged session recording | Fails closed | `NFR-070`, `BRU-SEC-19` |
| **`Z6` → Internet** | TLS verification with pinned CA set; response size limits; no redirect following to unlisted hosts | Fails closed | `SEC-C-046` |

### 5.4 The two rules that make the zone model worth its cost

A zone model that is merely a diagram costs operational effort and buys nothing. Two rules convert
it into a mechanism, and both are testable.

> **`SEC-ZR-1` — No application node reaches the internet except through `Z6`, to an allow-listed
> destination.**
> This is the estate's primary **exfiltration** control and its primary **supply-chain egress**
> control. It is what makes `IP-10` real. Test: from a `Z2` node, an outbound connection to any host
> not on the allow-list must fail at the network layer — not be blocked by application code.
> Owner: Platform Engineering. Verified by `QA-007` and by `PE-004` policy check on every deploy.

> **`SEC-ZR-2` — `Z4` is reachable only through the residency service.**
> The residency rule is implemented in exactly one place and can therefore be audited in exactly one
> place. Test: from any `Z2` workload other than `CD-233`, a connection to `Z4` must fail at the
> network layer. Owner: Platform Engineering with the CDO. This is the rule a regulator will ask
> about first, and the only defensible answer is *"one path, and here is its log"*.

### 5.5 Why `Z5` → `Z4` is denied, argued rather than asserted

This rule will be challenged in operations, so the reasoning is recorded rather than left to be
re-litigated at 02:00.

| Argument for allowing it | Response |
|---|---|
| *"Engineers need shell access to diagnose a database problem"* | They need shell access to a **PostgreSQL instance**, which they have. What is denied is unmediated **row access to residency-classified content**. Diagnostics — locks, plans, replication lag, disk — need no plaintext rows |
| *"A backup or restore needs direct access"* | Backup and restore operate on the **encrypted volume and WAL stream**, not on decrypted rows. `SC-006` holds the key material separately, so a restore operator is not automatically a reader |
| *"This will slow down incident response"* | It will. That is the trade. The alternative is that the strongest control in the estate has a standing bypass held by the population with the largest blast radius. `M29` `T-15` requires break-glass to be **loud**, and §7.6 provides the audited path for the genuine case |
| *"No other zone has this restriction"* | No other zone holds data whose mishandling is a **statutory act** rather than an incident. `NFR-086b` makes a cross-border move of this data a notifiable event, not a mistake |

**Escape hatch, specified rather than improvised:** `SEC-C-035` break-glass (§7.6) grants a
time-boxed, recorded, multi-party-notified read path into `Z4`. It exists precisely so that the
denial above never has to be argued during an incident.

### 5.6 The `M05` remote-support enclave — a seventh boundary this architecture adds

`AR-001` §8.1 defines six zones. **This document adds one**, because `M05` does not fit any of
them: it originates connections *outbound into third-party networks* and accepts *inbound* remote
sessions from engineers.

| Attribute | Position |
|---|---|
| **Designation** | **`Z7` Remote-support enclave** — a segment of `Z2` with its own boundary controls |
| **Why separate** | It is the only workload whose egress destination is **a customer's network**, not a listed API. `SEC-ZR-1`'s allow-list model does not express "every managed client's estate" |
| **Ingress** | `Z1` only, `R13` identities only, **MFA mandatory at every session**, step-up before session establishment |
| **Egress** | Customer estates, per an **agreement-scoped** destination record — a client with no live managed-services agreement is not reachable |
| **Controls** | Session recording (`NFR-070`) — **every** session, not only privileged ones; per-session customer consent record (`LG-016`); no file transfer out of the customer estate into `Z2` without classification; independent audit trail |
| **Residency** | **A remote view is a transfer** (`LG-012` `RD-R9`). An engineer outside Bangladesh viewing a screen containing personal data has received it. `Z7` sessions are therefore **origin-restricted** and the restriction is enforced, not advised |
| **Failure** | Fails closed. A recording failure **terminates the session**; an unrecorded privileged remote session into a customer estate is not an acceptable degraded mode |

> **`SEC-ZR-3`.** `Z7` is registered here and raised to `AR-001` for absorption at its next
> revision, so that the zone model has one home. Recorded as finding `SCA-04` — an architecture
> document adding a zone to another architecture document is a drift risk, and it is declared
> rather than absorbed silently.

### 5.7 Egress allow-list — the 47 destinations

`SEC-ZR-1` requires a named allow-list. **Counted: 47 external integrations** across seven
families (`05-03` §2). Each becomes a `Z6` allow-list entry with the attributes below; the
register itself is `IN-002`'s to publish and `SC-008`'s to hold the obligations for.

| Family | Count | Highest-consequence characteristic |
|---|---:|---|
| Payments | 9 | Financial instruction path; **card data never stored** (`BRU-ARB-25`) |
| Communications | 9 | Carries personal data to processors; every one is a `LG-012` §4.5 transfer row (`TR-03`) |
| Location, mapping & logistics | 9 | Carries customer address and rider position |
| Remote support & monitoring | 6 | `Z7`; reach into customer estates |
| Marketplace & trust | 4 | KYC and criminal-record verification — `S3` adjacency |
| Government & compliance | 5 | NBR filings; **statutory, cannot be disabled** |
| AI, data & enterprise | 5 | Model inference — `BRU-DTS-14`: recovered data is never training data |
| **Total** | **47** | |

| # | Allow-list entry attributes |
|---|---|
| 1 | Destination host and port, pinned CA set |
| 2 | Owning module and named business owner |
| 3 | Data categories permitted to traverse — **`S3` never** |
| 4 | The `LG-012` §4.5 transfer register row that authorises it (**currently: 0 of 8 anticipated transfers registered**) |
| 5 | Credential reference in Vault; never a literal |
| 6 | Rate limit and failure mode (`05-03` §7 fallback register) |
| 7 | Review date |

> **`SEC-E-02`.** `LG-012` §4.5 anticipates **eight** transfer classes and registers **zero**. The
> allow-list cannot be populated correctly until they are. This is not an architecture gap — it is
> an architecture that has correctly surfaced a governance gap. Owner: CDO with Legal. Blocks W1
> `Z6` configuration. Raised to `SC-007` and `SC-008`.

---

## 6. Identity at the Boundary

### 6.1 The five identity populations

An architecture that treats "user" as one thing gets external access wrong. Five populations
cross the boundaries, with different lifecycles, different assurance and different blast radius.

| # | Population | Size | Identity source | Authentication | Lifecycle driver | Blast radius |
|---|---|---:|---|---|---|---|
| **`P-INT`** | Internal staff | 800+ | Keycloak, provisioned from `M21` | Password + MFA where the role requires (`R01`–`R05`, `R13`, `R14`, `R19`, `R21`–`R24`, `R26`–`R28`, `R30`–`R33`, `R35`) | `employee.joined` / `.left` | Branch to estate-wide |
| **`P-CUST`** | Individual customers | 250,000+/month | Keycloak, self-registered | Password, MFA **optional** | Self-service | Own records only (`T4`) |
| **`P-CORP`** | Corporate portal users | 500–2,000 | **Federated** from the client's IdP (SAML/OIDC), or local | MFA **mandatory** for Approver and Finance sub-roles | Client administrator + agreement expiry | Own company, role-scoped within it (`EA-03`) |
| **`P-EXT`** | External parties — 17 sub-identities on `R38` | 1,000–3,000 | Keycloak, invited | MFA **mandatory for any action with financial consequence** (`EA-09`) | Agreement/registration expiry (`EA-12`) | Own records only; **never cost, margin or another party's data** (`EA-02`) |
| **`P-SVC`** | Service and machine identities | Per service | Keycloak clients + Vault | mTLS between services; client credentials for external consumers | Owner-accountable, rotated | **Potentially estate-wide — the highest-risk population and the smallest** |

> **`SEC-ID-1`. `P-SVC` is the population that gets least attention and carries most risk.**
> `FR-SEC-012` requires every non-human identity to have *"scoped credentials, rotation and an
> accountable human owner"*. The architecture enforces the third of those structurally: a service
> identity **cannot be created without an owner reference**, and an identity whose owner is
> deprovisioned enters the `BRU-SEC-17` 24-hour orphan path like any other.

### 6.2 What each boundary sees

| Boundary | Credential presented | Verified by | What it establishes | What it does **not** establish |
|---|---|---|---|---|
| Internet → `Z0` | none | — | nothing | — |
| `Z0` → `Z1` | Edge identity | Ingress | Traffic came through the edge | Anything about the user |
| `Z1` → `Z2` | **OAuth 2.0 / OIDC access token** | Kong, by introspection against Keycloak | **Who** the subject is, which client, which scopes, token validity | **Nothing about record scope.** `SEC-SD-1` |
| Inside `Z2` (service→service) | **mTLS service identity** | Peer verification | Which service is calling | Nothing about the end user — the user context travels as a propagated, signed claim |
| `Z2` → `Z3` | Vault-leased DB credential | PostgreSQL | Which service is connecting | Nothing about the user; **row scope is decided above this line, in-transaction** |
| `Z2` → `Z4` | `CD-233` service identity **plus** the end-user context **plus** a purpose | Residency service | Who is reading, why, and which record | — |
| `Z2` → `Z6` | Vault-injected destination credential | Egress proxy | Which integration | The application **never sees** the credential |
| `Z5` → `Z2`/`Z3` | Human identity + MFA + **time-boxed elevation grant** | Bastion, Keycloak | Who, for how long, for what | Standing rights — there are none (`BRU-SEC-19`) |

### 6.3 Token architecture at architecture altitude

Lifetimes, claims and client configuration are `SC-004`'s. Four properties are **architectural**
because reversing them changes the structure:

| # | Property | Statement | Why architectural |
|---|---|---|---|
| `SEC-TK-1` | **Introspection, not blind trust** | `Z1` introspects rather than validating a signature locally | Enables `SEC-TK-3`. The cost is a dependency on Keycloak availability, addressed by `M29` `T-09`: ≥ 99.99%, ≤ 20 ms p95, short-TTL cache |
| `SEC-TK-2` | **Scope is per-consumer, not per-user-request** | External API scope is set by credential and **cannot be widened by request parameter** (`EA-11`) | A parameter-widenable scope is a privilege-escalation primitive. `SC-002` `AB-07` abuses exactly this |
| `SEC-TK-3` | **Revocation propagates in ≤ 60 seconds estate-wide** | A revoked token, suspended identity or leaver event takes effect within 60 s, **not at next expiry** (`BRU-SEC-25`) | Long-lived tokens with no revocation path make the one-hour leaver rule (`BRU-SEC-06`) unachievable regardless of process quality |
| `SEC-TK-4` | **Step-up is a token property, not a UI flow** | Sensitive actions require a token carrying a recent, elevated authentication claim (`NFR-065`) | A UI-only step-up is bypassed by calling the API directly. This is the most common real-world defect of the pattern |

> **`SEC-E-03`. `BRU-SEC-06` says one hour; `KPI-090` measures 24 hours** (`AUDIT-017` `OP-15`).
> The architecture is built to the **one-hour** rule and treats anything beyond it as a control
> failure, because `SEC-TK-3`'s 60-second propagation makes one hour achievable. The KPI is wrong,
> not the rule. Escalated to `SC-008` and `GV-005`.

---

## 7. Enforcement Architecture

### 7.1 The enforcement points

An authorisation decision in this estate is made at **five** places, and each has a different job.
Confusing them is how `NFR-015` gets implemented wrongly.

| # | Point | Location | Decides | Fails how | Realisation |
|---|---|---|---|---|---|
| **`EP-1`** | **Edge filter** | `Z0` WAF | Whether the request is malformed, abusive or from a blocked source | Open (availability) | OWASP CRS |
| **`EP-2`** | **Gateway authentication** | `Z1` Kong | Whether a valid, unrevoked token exists, and whether the consumer is within quota | **Closed** | Kong + Keycloak introspection |
| **`EP-3`** | **Object permission** | `Z2` ORM | Whether this role may create/read/update/delete/approve **this model** | **Closed** | Odoo groups + `CD-130` `cd_rbac_ext` |
| **`EP-4`** | **Record rule** | `Z2` ORM, **in-transaction** | Whether this subject may see **this row** — `T0`…`T5` | **Closed** | `ir.rule` + `OCA/operating-unit` |
| **`EP-5`** | **Field permission** | `Z2` ORM, in-transaction | Whether this subject may see **this field** of a row they may otherwise see | **Closed** | `CD-130` |

Two further gates are not authorisation but are enforced at the same altitude:

| # | Gate | Decides | Realisation |
|---|---|---|---|
| **`EP-6`** | **SoD gate** | Whether this assignment or this transaction creates an incompatible duty combination | `CD-132` `cd_sod` |
| **`EP-7`** | **Residency gate** | Whether this write may land in this store, and whether this transfer may execute | `CD-233` residency service |

> **`SEC-EP-1`. `EP-2` is not `EP-4`, and the architecture must never let it appear to be.**
> `M29` `T-01` states it as a defect class; `M28` `AC-11` tests it. The single most likely
> implementation failure in this estate is a portal BFF that filters a list for display and a
> developer who concludes the filter *is* the control. Every list endpoint must return the same
> rows whether or not the BFF filter runs — **`QA-007` tests this by removing the filter**, not by
> inspecting the code.

### 7.2 Request path with enforcement, end to end

```
 Customer taps "my invoices" on P01
   │
   ├─► Z0  WAF: rate limit, bot score                     EP-1  (open on WAF outage)
   │
   ├─► Z1  Kong: introspect token → subject, client,      EP-2  (CLOSED)
   │        scopes; inject correlation-id; quota
   │
   ├─► Z2  BFF composes the read  ◄── NOT a control, presentation only
   │
   ├─► Z2  ORM: may role R36 read account.move?           EP-3  (CLOSED)
   │
   ├─► Z2  ORM: ir.rule T4 → partner_id = subject         EP-4  (CLOSED, in-transaction)
   │        ★ this is the line that makes EA-01 true
   │
   ├─► Z2  ORM: field permissions strip unit_cost,        EP-5  (CLOSED)
   │        margin, internal_note                          ★ EA-02
   │
   ├─► Z3  PostgreSQL: rows returned                       (no decision here)
   │
   └─► audit: read of S2/S3 fields logged with actor,     SEC-C-041 / SEC-C-043
            purpose, record identity, correlation-id
```

**The same request, if it touches a residency-classified field:**

```
   ├─► Z2  ORM detects a residency-classified field on the model
   │
   ├─► Z2  ★ call to CD-233 residency service — the ONLY path   EP-7
   │        · step-up claim required for human-initiated read (NFR-065)
   │        · per-read access log written BEFORE the value returns
   │
   ├─► Z4  resident store: value read by resident key
   │
   └─► value returned to the transaction, NEVER cached in Z3,
       NEVER written to a Z3 log, NEVER placed in a search index
       (LG-012 §4.4.1–4.4.3: a cache, a log and an index are all copies)
```

### 7.3 The isolation model realised

`T0`…`T5` are inherited from `AR-001` §8.2. What follows is the **realisation contract** — the
part a developer builds against.

| Tier | Domain expression basis | Applies to | Additional control | Test |
|---|---|---|---|---|
| **`T0`** Global | no rule | Catalogue, brand/model master, checklist templates, branch directory | — | A `T0` object must be readable by every authenticated internal identity — including the lowest-privileged (`R11`) |
| **`T1`** Company | `company_id` | Chart of accounts, tax configuration, payroll structures, entity policies | — | Cross-entity read must return zero rows, not an error |
| **`T2`** Branch | `operating_unit_id` | Branch service orders, stock, cash, HR, queue, local documents | — | **The `NFR-015` test.** A Mirpur `R08` must return zero Chittagong rows |
| **`T3`** Zone | `zone_id` / team membership | Technician schedules, van stock, dispatch assignments, route plans | — | — |
| **`T4`** Own record | `partner_id` / `user_id` | Customer's own orders; technician's own jobs; seller's own listings and payouts; vendor's own POs | — | **The `EA-01` test.** Requires an *adversarial* test: authenticate as seller A, request seller B's payout id directly |
| **`T5`** Restricted | named allow-list | Individual payroll, NID, bank details, recovered-data case content, call recordings, audit logs, biometric templates, seller KYC | **Access logged + step-up authentication** (`NFR-065`) | Access without a step-up claim must fail; the access log must exist **before** the value is returned |

> **`SEC-IS-1`. `T5` and `Z4` coincide almost exactly, and the architecture exploits it.** Nearly
> every `T5` class is also residency-classified. Consequence: **a `T5` read is a call to the
> residency service, never a direct database read.** One enforcement point, one audit point, one
> place to get it right. The exceptions — call recordings and audit logs, which are `T5` but held
> regionally — are named explicitly in §8.4 so they are not assumed to be in `Z4`.

**Access profiles.** `OP-10` records that **no standard access profile has been authored for any of
the 38 roles**, so *"every W1 grant is bespoke and justified by precedent"*. Architecturally, a
profile is the **bound triple** `(object permissions `EP-3`, isolation tier `EP-4`, field
restrictions `EP-5`)` attached to a role. This document fixes that as the required shape; the 50
profiles themselves are `SC-004` §5's deliverable and are a **W1 blocker**.

### 7.4 Segregation of duties as an architectural component

| # | Position | Rationale |
|---|---|---|
| `SEC-SOD-1` | **SoD is evaluated twice** — at role assignment (`EP-6` preventive) and inside the transaction (`EP-6` runtime). **The runtime evaluation is authoritative** | `SOD-02` (raise PO + receive goods + approve invoice) is a *runtime* condition. Assignment-time checking alone misses combinations acquired through delegation, temporary elevation or role change across time |
| `SEC-SOD-2` | **`M60` defines and tests; `M29` enforces.** The separation is itself a control | A rule defined and enforced by the same component cannot be independently tested. `BRU-GRC-11` and `M60` `T-12` both state it |
| `SEC-SOD-3` | **An exception is time-boxed, mitigated, approved by CFO or CTO, and appears on a standing quarterly report** | A hard block with no exception path produces shadow workarounds — a person doing the task under someone else's login, which defeats attribution entirely |
| `SEC-SOD-4` | **The rule set the engine is built against is `SP-006`, not `05-04` §6** | Counted: modules use `SOD-01`…`SOD-30`; `05-04` §6 registers 12; `SP-006` registers to `SOD-60` and resolves nine collisions into `SOD-31`…`SOD-39`. **Grant-time enforcement cannot be built against an identifier space where nine numbers mean two things** (`OP-10`b) |

> **`SEC-E-04`.** `AR-001` §9.1 states SoD is *"evaluated at role-assignment time, **not** transaction
> time"*. `M29` `T-07` and `FR-SEC-023` require **both**, with runtime authoritative. **`M29` is the
> module specification and wins on what the system does** (`FOLDER_STRUCTURE.md` §9 cross-repository
> rule). Recorded as finding `SCA-05`; raised to `AR-001` for correction.

### 7.5 Secrets and key-material flow

```
   ┌──────────────────────────────────────────────────────────────┐
   │  Z5  VAULT — the only origin of a credential                 │
   │      · sealed at rest; unseal is a break-glass event         │
   │      · every read audited with requester and purpose         │
   │      · dynamic DB credentials with short lease               │
   └───────┬──────────────────┬───────────────────┬───────────────┘
           │                  │                   │
      short-lease        injected at          key REFERENCE
      DB credential      Z6 egress            only (never material)
           │                  │                   │
           ▼                  ▼                   ▼
      ┌─────────┐      ┌────────────┐      ┌──────────────────┐
      │ Z2 app  │      │ Z6 proxy   │      │ Z2 field-level   │
      │ process │      │ ★ the app  │      │ encryption       │
      │         │      │   NEVER    │      │ ★ Z4 key material│
      │         │      │   sees the │      │   is SEPARATE    │
      │         │      │   creds    │      │   from the DB key│
      └─────────┘      └────────────┘      └──────────────────┘

   NEVER holds a secret: source control · configuration files · container
   images · environment variables in a manifest · logs · tickets · CI job
   output · error messages · a developer's laptop
```

| # | Rule | Requirement |
|---|---|---|
| `SEC-KM-1` | Secrets are held in Vault and **never** in code, configuration files or logs | `NFR-062`, `BRU-RMS-03` |
| `SEC-KM-2` | The application holds a **key reference**, never key material. The vault holds the material | `M29` §10.1 `fix.encryption.key.ref` |
| `SEC-KM-3` | **`S3` fields use key material distinct from the database-level key**, so a database compromise does not yield the sensitive fields | `NFR-061`, `BRU-SEC-15`, `M29` `T-06` |
| `SEC-KM-4` | **Keys for residency-restricted data are held in Bangladesh** | `LG-012` `RD-R5` |
| `SEC-KM-5` | Egress credentials are **injected at the proxy**; the calling application never possesses them | `SEC-ZR-1` |
| `SEC-KM-6` | **Recovered customer data is encrypted with a case-specific key, and purge is by destruction of that key** | `BRU-DTS-05`, `LG-009` `DM-3` |
| `SEC-KM-7` | **Algorithm agility is required** — a cipher or hash chosen today must be replaceable | `LG-021` §4.4.6 |

Algorithms, lifetimes, rotation cadence, HSM position and the crypto-erase standard are `SC-006`'s.

### 7.6 Break-glass — closing the architecture half of `OP-08`

`OP-08` records that break-glass is *documented and does not exist*: **no vault path, no sealed
envelope, no safe procedure, no named holders, no test schedule**. It also records why it matters
more than it looks — *every portal depends on one identity provider, deliberately, and break-glass
is the compensating control for that concentration*.

This document specifies it as an **architectural component** with five properties. The
operational procedure, holders and test schedule are `SC-011` §8 and `PE-008`.

| # | Property | Statement |
|---|---|---|
| `BG-A1` | **Independent of what it recovers** | The break-glass path must not depend on Keycloak, on Kong, or on the network segment being recovered. A break-glass that authenticates through the failed IdP is not a control |
| `BG-A2` | **Loud, not quiet** | Use triggers **immediate multi-party notification** over a path independent of the systems it grants access to (`M29` `T-15`, `BRU-SEC-20`) |
| `BG-A3` | **Time-boxed with automatic expiry** | No manual revocation step. A forgotten revocation is the normal failure mode |
| `BG-A4` | **Recorded end to end** | Session recording is mandatory and its failure **terminates** the session; post-hoc justification is mandatory and its absence is a control failure, not an administrative loose end |
| `BG-A5` | **Rotated after every use** | Credentials rotate on use (`BG-11`), tested quarterly (`BG-10`) |

**Scope:** break-glass covers `Z5`→`Z2`/`Z3` administrative recovery **and** the `Z5`→`Z4`
exception path denied by §5.5. It is **cheap and high-value** — `OP-08` calls it *"days of work,
not months, and the cheapest high-severity item in this report"*. It is a **W1 go-live blocker**.

---

## 8. Data Protection Architecture

### 8.1 Classification drives every downstream control

| Class | Definition | Encryption | Access | Logging | Residency | Retention |
|---|---|---|---|---|---|---|
| **`S0`** Public | No restriction | Transport only | Anonymous | Standard | Any | Standard |
| **`S1`** Internal | Business data, staff-visible | At rest | RBAC (`EP-3`) | Standard | Any | Per `LG-009` |
| **`S2`** Confidential | Restricted business or personal data | At rest | RBAC + field permissions (`EP-5`) | **Access logged** | Any | Per `LG-009` |
| **`S3`** Restricted | Highest sensitivity | **Field-level, separate key material** | Explicit grant + **step-up** (`T5`) | **Full access log, per read** | **Per §8.4** | **Enforced technically** |

**Counted `S3` inventory: 9 fields** (`05-02` §10).

| # | `S3` field | Entity | `Z4` resident? | Additional control |
|---|---|---|:--:|---|
| 1 | National ID number | `fix.identity.document` | **Yes** | Finance and compliance roles only |
| 2 | Bank account details | `fix.party`, `hr.employee` | **Proposed** (`LG-012` `RD1`) | Masked except last four |
| 3 | Individual salary and payslip | `hr.payslip`, `fix.salary.structure` | **Proposed** (`LG-012` `RD1`) | Employee + HR/finance only |
| 4 | Recovered customer data index | `fix.recovered.inventory` | **Yes** | Per-case keys; **dual control**; `BRU-DTS-16` never replicated abroad |
| 5 | Call recordings | `fix.call.record` | **No — regional** | Access logged; retention enforced |
| 6 | Biometric attendance templates | `fix.attendance.record` | **Yes** | Irreversible template; **never exported** |
| 7 | Seller KYC documents | `fix.mp.seller.document` | **Yes** | Onboarding and compliance only |
| 8 | Customer identity documents | `fix.identity.document` | **Yes** | Access logged |
| 9 | API and integration credentials | `fix.integration.credential` | **No — Vault** | **Never displayed after creation** |

### 8.2 The classification-is-data principle

> **`SEC-DC-1`.** Classification and residency are **columns in the data model**, enforced by the
> platform at write time — not documentation, not convention, not a developer's memory
> (`NFR-086a`, `FR-SEC-047`).

This is the single most consequential decision in this document, and its value is
**risk-absorbing**: the split-residency legal opinion (`DEP-31`, `D-13`) is not yet obtained. If
classification is *data*, a change of legal opinion is a **reclassification — a data change** — not
a redesign. `AR-001` §8.3 records this as `TR-02`, and it is why the residency mechanism is built
in Wave 1 **whatever the opinion says**.

### 8.3 Three quiet copies

`LG-012` §4.4 names three ways a residency or classification control is defeated without anyone
deciding to defeat it. Each is an architectural rule here.

| # | Rule | Because |
|---|---|---|
| `SEC-DC-2` | **A cache is a copy.** No `Z3` cache, read replica or materialised view holds a residency-classified field | Redis in `Z3` is the obvious accidental breach path |
| `SEC-DC-3` | **A search index is a copy.** Full-text search over restricted fields, if required at all, runs in Bangladesh | A GIN index on a `Z3` table containing a copied NID is a residency breach nobody committed |
| `SEC-DC-4` | **A log is a copy.** Classified fields are redacted **at emission**, not at ingestion (`BRU-SEC-24`, `M29` `T-13`, `OPS-04`) | Redaction at ingestion means the plaintext existed in `Z2` memory, on the wire and possibly on disk. A regional log aggregator would otherwise become a residency breach |

`SEC-DC-4` has a build consequence: **redaction is a logging-library responsibility**, configured
from the field classification, not a per-call developer decision. `SC-010` specifies it; `SC-005`
gates it.

### 8.4 Reconciling the two lists

Two lists exist and are **deliberately different**. Conflating them is a live error risk.

| List | Purpose | Members | Authority |
|---|---|---:|---|
| **`S3` sensitivity** | Drives encryption, access control, logging, retention | **9** | `05-02` §10 |
| **Residency-classified** | Drives `Z4` placement and the transfer gate | **7** | **`05-06` §6.4 — authoritative** |
| Proposed residency additions | Bank details, individual payroll | 2 | `LG-012` §4.3 `RD1` — **declared, not applied** |

| Relationship | Members |
|---|---|
| Both `S3` **and** residency-classified | NID, customer identity documents, biometric templates, recovered data index, seller KYC |
| Residency-classified, **not** in the 9-field `S3` list | Passport number, TIN, criminal-record checks |
| `S3` but **regional** | Call recordings, API credentials (Vault), and — until `RD1` is answered — bank details and individual payroll |

> **`SEC-E-05`.** `LG-012` §4.3 correctly declines to extend `05-06` §6.4 unilaterally and raises
> `RD1` instead. **Architecturally the question is not neutral:** bank account details and individual
> payroll for Bangladeshi individuals are exactly the categories a regulator would expect in `Z4`,
> and adding them later means migrating live `S3` data across a residency boundary — the one
> migration `NFR-086b` makes a notifiable act. **The architecture therefore builds `Z4` with
> capacity and key separation for all nine `S3` classes**, so that `RD1` becomes a
> reclassification rather than a migration. Owner: CDO with Enterprise Architecture. Raised to
> `SC-007` §6.

### 8.5 Non-production

| # | Rule | Requirement |
|---|---|---|
| `SEC-NP-1` | **No unmasked residency-classified data exists in any non-production environment in any region.** Absolute | `NFR-086c` |
| `SEC-NP-2` | **Masking runs inside the clone job**, so an unmasked clone cannot exist even briefly | `AR-001` §8.3 |
| `SEC-NP-3` | Masking is **deterministic and referentially consistent** — masked data stays testable while being irreversible | `M29` `T-12` |
| `SEC-NP-4` | `local`, `dev`, `staging`, `training` hold residency-classified data **never**; `prod` in `Z4` only; `dr` in a **Bangladesh-resident** standby | `AR-001` §8.5 |

---

## 9. The Security Control Catalogue

### 9.1 How this catalogue is used

Each control has an identifier, an owner **role**, the requirement it discharges, its ISO/IEC
27001:2022 Annex A reference, and its enforcement point or zone. **`QA-007` derives a test from
every row**; a control with no test is an assertion, and `LG-021` §4.1.6 already states that *a
control asserted as operating without evidence is a deficiency, not a pass*.

**Counted: 68 controls across 9 families.**

### 9.2 The catalogue

**Family 1 — Identity and authentication (`SEC-C-001`…`-012`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-001` | Every identity has a type, a status and an accountable owner | CTO | `FR-SEC-001` | A.5.16 | `Z2` |
| `SEC-C-002` | All authentication is against the identity provider; **no module implements its own** | CTO | `FR-SEC-002`, `BRU-SEC-09` | A.5.17 | `Z1` |
| `SEC-C-003` | Password policy: length, complexity, history, **breach-list checking**, bilingual reset | CTO | `FR-SEC-003` | A.5.17 | Keycloak |
| `SEC-C-004` | **MFA at every login** for admin, finance, HR and all privileged roles | CTO | `NFR-012`, `BRU-SEC-01` | A.8.5 | Keycloak |
| `SEC-C-005` | **Step-up authentication** for sensitive actions, carried as a token claim | CTO | `NFR-065`, `SEC-TK-4` | A.8.5 | `EP-2`/`EP-4` |
| `SEC-C-006` | Session policy: 30 min external idle, 60 min internal, 12 h absolute; concurrent-session limits | CTO | `NFR-069`, `EA-08` | A.8.5 | Keycloak |
| `SEC-C-007` | Token issue, introspection, refresh, revocation across 12 API families | CTO | `FR-SEC-007` | A.5.17 | Keycloak |
| `SEC-C-008` | SSO across internal portals from one authentication | CTO | `FR-SEC-008` | A.5.17 | Keycloak |
| `SEC-C-009` | Corporate-client federation over SAML/OIDC (`INT-046`) | CTO | `FR-SEC-009` | A.5.17 | Keycloak |
| `SEC-C-010` | Device registration and deregistration for technician, rider and auditor apps | CTO | `FR-SEC-010` | A.8.1 | `Z2` |
| `SEC-C-011` | Brute-force, credential-stuffing, impossible-travel and anomaly defence | CTO | `FR-SEC-011`, `NFR-068` | A.8.16 | `Z0`/`Z1` |
| `SEC-C-012` | Service accounts: scoped credentials, rotation, **accountable human owner** | CTO | `FR-SEC-012` | A.5.16 | Vault |

**Family 2 — Authorisation and isolation (`SEC-C-013`…`-024`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-013` | Role register maintained to **`R50`**, with headcount, portals, MFA and scope | CTO | `FR-SEC-013` | A.5.15 | `Z2` |
| `SEC-C-014` | Permission sets: CRUDA per module per role | CTO | `FR-SEC-014` | A.5.15 | `EP-3` |
| `SEC-C-015` | **Record rules realise `T0`…`T5`** | CTO | `NFR-015`, `FR-SEC-015` | A.8.3 | `EP-4` |
| `SEC-C-016` | **Field-level permissions** across 13 restricted field groups | CTO | `NFR-011`, `FR-SEC-016` | A.8.3 | `EP-5` |
| `SEC-C-017` | Portal access matrix enforced | CTO | `FR-SEC-017` | A.5.15 | `EP-3` |
| `SEC-C-018` | **External party rules `EA-01`…`EA-12`** | CTO | `FR-SEC-018` | A.5.19 | `EP-4` |
| `SEC-C-019` | Delegation is bounded, scoped, audited and auto-expiring | CTO | `FR-SEC-019` | A.5.15 | `Z2` |
| `SEC-C-020` | Approval-authority matrix evaluated; out-of-band approval rejected | CFO | `FR-SEC-020`, `SP-004` | A.5.15 | `Z2` |
| `SEC-C-021` | **Authorisation evaluated server-side on every request** | CTO | `API-10`, `BRU-SEC-10` | A.8.3 | `EP-3`…`EP-5` |
| `SEC-C-022` | **SoD blocked at assignment** across the `SP-006` rule set | CFO/CTO | `NFR-064`, `BRU-SEC-07` | A.5.3 | `EP-6` |
| `SEC-C-023` | **SoD re-evaluated at transaction — authoritative** | CFO/CTO | `FR-SEC-023` | A.5.3 | `EP-6` |
| `SEC-C-024` | SoD exceptions: time-boxed, mitigated, CFO/CTO-approved, quarterly report | CFO/CTO | `FR-SEC-024` | A.5.3 | `Z2` |

**Family 3 — Access governance (`SEC-C-025`…`-032`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-025` | Access request, justification, approval and provisioning workflow | CTO | `FR-SEC-025` | A.5.18 | `Z2` |
| `SEC-C-026` | **Access certification; unconfirmed access revoked automatically** | CTO | `FR-SEC-026`, `BRU-SEC-16` | A.5.18 | `Z2` |
| `SEC-C-027` | Joiner automation from `employee.joined` | CTO/HR | `FR-SEC-027` | A.6.1 | `Z2` |
| `SEC-C-028` | **Mover: old revoked and new granted in one transaction — never additive** | CTO/HR | `FR-SEC-028` | A.5.18 | `Z2` |
| `SEC-C-029` | **Leaver: all access revoked within one hour** | CTO/HR | `BRU-SEC-06` | A.5.18 | `Z2` |
| `SEC-C-030` | Orphaned-account detection; **zero tolerance beyond 24 h** | CTO | `BRU-SEC-17` | A.5.16 | `Z2` |
| `SEC-C-031` | External access expires automatically at agreement expiry | CTO | `EA-12` | A.5.19 | `Z2` |
| `SEC-C-032` | **Revocation propagates estate-wide in ≤ 60 s** | CTO | `BRU-SEC-25` | A.5.18 | Keycloak/`Z1` |

**Family 4 — Privileged access (`SEC-C-033`…`-037`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-033` | Privileged role and action register with accountable owners | CTO | `FR-SEC-032` | A.8.2 | `Z2` |
| `SEC-C-034` | **Time-boxed elevation; no standing administrative rights** | CTO | `BRU-SEC-19` | A.8.2 | `Z5` |
| `SEC-C-035` | **Break-glass per `BG-A1`…`BG-A5`** | CTO | `BRU-SEC-20`, `OP-08` | A.8.2 | `Z5` |
| `SEC-C-036` | **Privileged session recording**; recording failure terminates the session | CTO | `NFR-070` | A.8.15 | `Z5`/`Z7` |
| `SEC-C-037` | **No self-administration or self-approval of access** | CTO | `SOD-09`, `BRU-SEC-18` | A.5.3 | `EP-6` |

**Family 5 — Audit and accountability (`SEC-C-038`…`-044`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-038` | **Immutable audit trail, inherited — no module-level audit code** | CTO | `NFR-014`, `BRU-SEC-12` | A.8.15 | `Z2` ORM |
| `SEC-C-039` | **Audit insert-only at the database privilege level**; hash-chained per partition | CTO | `BRU-SEC-11`, `M29` `T-03` | A.8.15 | `Z3` |
| `SEC-C-040` | 100% audit coverage of financial transactions, reconcilable to source | CFO | `DI-02` | A.8.15 | `Z2` |
| `SEC-C-041` | **Data access logging** for personal, `S3` and residency-classified reads | CDO | `FR-SEC-040`, `EA-10` | A.8.15 | `EP-5`/`EP-7` |
| `SEC-C-042` | **Bulk export requires approval, is logged and is rate-limited** | CDO | `BRU-SEC-05`, `EA-12` | A.8.12 | `Z2` |
| `SEC-C-043` | Audit searchable by actor, object, field, time, correlation-id; **retained ≥ 5 years** | CTO | `NFR-095` | A.8.15 | `Z3` |
| `SEC-C-044` | Records of processing activity sufficient for `NFR-095` | CDO | `FR-GRC-033` | A.5.34 | `Z2` |

**Family 6 — Data protection and cryptography (`SEC-C-045`…`-052`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-045` | **Egress allow-list of 47 destinations; every outbound call logged** | Platform Eng | `IP-10`, `SEC-ZR-1` | A.8.21 | `Z6` |
| `SEC-C-046` | TLS 1.2+ (1.3 preferred) in transit; AES-256 at rest | CTO | `NFR-013` | A.8.24 | all |
| `SEC-C-047` | **Field-level encryption with key material separate from the DB key** | CTO | `NFR-061`, `BRU-SEC-15` | A.8.24 | `Z2`/`Z4` |
| `SEC-C-048` | **Secrets in Vault; never in code, configuration or logs** | CTO | `NFR-062` | A.8.24 | `Z5` |
| `SEC-C-049` | Key generation, storage, rotation, escrow and access control | CTO | `FR-SEC-046` | A.8.24 | Vault |
| `SEC-C-050` | **Classification and residency carried on every field, enforced at write time** | CDO | `NFR-086a`, `SEC-DC-1` | A.5.12 | `EP-7` |
| `SEC-C-051` | **Cross-border transfer blocked until notification and safeguard exist** | CDO/Legal | `NFR-086b`, `BRU-SEC-14` | A.5.14 | `EP-7` |
| `SEC-C-052` | **Non-production masking, in-job, deterministic** | CTO | `NFR-071`, `NFR-086c` | A.8.33 | pipeline |

**Family 7 — Application and platform security (`SEC-C-053`…`-060`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-053` | **Malware scanning on every upload before storage or serving** | CTO | `NFR-063`, `BRU-SEC-22` | A.8.7 | `Z2` |
| `SEC-C-054` | Rate limiting and bot protection on all public endpoints | Platform Eng | `NFR-068` | A.8.16 | `Z0`/`Z1` |
| `SEC-C-055` | **Security integrated into every development stage** — SSDLC | CTO | ISO 27001 A.8.25 | A.8.25 | `SC-005` |
| `SEC-C-056` | **SAST, DAST, SCA and secret scanning in CI and continuously in production** | CTO | `NFR-066`, `M29` `T-11` | A.8.28 | `SC-005` |
| `SEC-C-057` | **Vulnerability discovery, triage and remediation to SLA**; critical > 7 days escalates to CTO and board | CTO | `BRU-SEC-21`, `LG-021` `O-09` | A.8.8 | `SC-009` |
| `SEC-C-058` | Annual penetration test with findings tracked to closure | CTO | `NFR-067` | A.8.8 | `SC-009` |
| `SEC-C-059` | **Authorisation latency ≤ 15 ms p95** — a slow permission engine gets bypassed | CTO | `M29` `T-08` | A.8.6 | `EP-4` |
| `SEC-C-060` | **Introspection endpoint ≥ 99.99%, ≤ 20 ms p95** | CTO | `M29` `T-09` | A.8.6 | Keycloak |

**Family 8 — Network and zone integrity (`SEC-C-061`…`-065`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-061` | **Zone flow matrix enforced at the network layer**, not by application convention | Platform Eng | `SEC-ZR-1` | A.8.22 | `PE-001` |
| `SEC-C-062` | **`Z4` reachable only via `CD-233`** | Platform Eng/CDO | `SEC-ZR-2` | A.8.22 | `PE-001` |
| `SEC-C-063` | mTLS between services inside `Z2`; service identity verified | Platform Eng | `AR-001` §8.1 | A.8.20 | `Z2` |
| `SEC-C-064` | **`Z7` remote-support enclave**: origin-restricted, agreement-scoped, fully recorded | CTO | `SEC-ZR-3`, `LG-016` | A.8.21 | `Z7` |
| `SEC-C-065` | Branch networks do not reach production data stores directly | Platform Eng | `LG-021` §4.9.5 | A.8.22 | `PE-001` |

**Family 9 — Operations and assurance (`SEC-C-066`…`-068`)**

| ID | Control | Owner | Requirement | Annex A | Point |
|---|---|---|---|---|---|
| `SEC-C-066` | Security event detection, correlation and alerting | CTO | `NFR-072` | A.8.16 | `Z5` |
| `SEC-C-067` | Incident response with severity, containment and **breach-notification assessment** | CTO/CDO | `NFR-094` | A.5.24–A.5.26 | `SC-011` |
| `SEC-C-068` | **Supplier and processor security obligations flowed down by contract** | CTO/Procurement | `NFR-098` | A.5.19–A.5.22 | `SC-008` |

### 9.3 Control coverage by family

Regenerated by counting rows in §9.2, per `PG-M10`.

| Family | Controls | Primary Annex A theme |
|---|---:|---|
| 1 Identity and authentication | 12 | Organizational / Technological |
| 2 Authorisation and isolation | 12 | Technological |
| 3 Access governance | 8 | Organizational / People |
| 4 Privileged access | 5 | Technological |
| 5 Audit and accountability | 7 | Technological |
| 6 Data protection and cryptography | 8 | Technological |
| 7 Application and platform security | 8 | Technological |
| 8 Network and zone integrity | 5 | Technological |
| 9 Operations and assurance | 3 | Organizational |
| **Total** | **68** | |

Check: 12 + 12 + 8 + 5 + 7 + 8 + 8 + 5 + 3 = **68** ✓ against a counted row total of 68.

### 9.4 The Annex A controls this architecture cannot discharge

An architecture that claims full Annex A coverage is claiming something a system cannot deliver.
**22 of the 93 Annex A controls are organisational, physical or people controls with no
architectural realisation.** They are named with their owner so they are not silently assumed.

| Annex A theme | Controls with **no** architectural realisation | Owner |
|---|---|---|
| **Organizational** | A.5.1 policies · A.5.2 roles · A.5.4 management responsibilities · A.5.5 authority contact · A.5.6 special-interest groups · A.5.8 security in project management · A.5.31 legal requirements · A.5.35/36 review and compliance | `LG-021`, `GV-002`, `SC-008` |
| **People** | A.6.1 screening · A.6.2 terms of employment · A.6.3 awareness and training · A.6.4 disciplinary · A.6.5 post-employment · A.6.6 confidentiality · A.6.8 event reporting | HR Director; `TR-021`, `TR-025` |
| **Physical** | A.7.1–A.7.4 perimeter and monitoring · A.7.10 storage media · A.7.12 cabling | Facilities; `M47`, `LG-021` §4.7 |
| **Count** | **22** | 9 Organizational + 7 People + 6 Physical. *(The first issue stated 21; recounted during the Category 05 audit — `SCA-13`)* |

> **`SEC-E-06`.** **Seven of the 22 are People controls, and the ISMS has no delivery vehicle for
> them.** `LG-021` §4.12.4 records that `TR-025` statutory induction *is unregistered*, so §4.12.1's
> annual security-awareness obligation has no mechanism. An estate whose strongest technical
> controls sit on top of an untrained population is not proportionate under `NFR-097`. Owner: CTO
> with L&D. Raised to `SC-008` and to `TC-002`.

---

## 10. Zero-Trust Position

`NFR`s and `M29` §4 assert a *"NIST-aligned zero-trust posture"*. That phrase is unfalsifiable
unless the tenets are taken one at a time. NIST SP 800-207 §2 lists seven.

| # | Tenet | Position | Realisation or reason |
|---|---|---|---|
| 1 | All data sources and computing services are resources | **Adopted** | Zone model treats `Z4`, `Z6` and `Z7` as resources with their own policy, not as network locations |
| 2 | All communication is secured regardless of network location | **Adopted** | TLS everywhere; **mTLS between services inside `Z2`** — the internal network is not trusted |
| 3 | Access granted per-session | **Adopted** | `SEC-TK-3` 60-second revocation; time-boxed elevation; no standing administrative rights |
| 4 | Access determined by dynamic policy including observable state | **Partially adopted** | Policy is role, tier, field, SoD and step-up state. **Device posture and behavioural signals are not yet inputs** |
| 5 | Integrity and security posture of all owned assets monitored | **Deferred to W6** | `Wazuh`/`osquery` arrive at W5 with `M05`. Extending posture assessment to internal endpoints is a W6 scope item, and the cost is not justified at 800 users today |
| 6 | Authentication and authorisation are dynamic and strictly enforced before access | **Adopted — this is `SEC-SD-1`** | Enforced **in-transaction**, on every request, server-side |
| 7 | Collect as much information as possible about assets and network state, and use it to improve posture | **Deferred to W6** | Observability exists (OTel→Prom/Loki/Tempo); **feeding it back into access policy** does not. Requires a SIEM correlation capability `SEC-CON-03` does not fund |

**Score, stated rather than implied: 4 adopted, 1 partial, 2 deferred.**

> **`SEC-ZT-1`.** The two deferrals are recorded as a **known posture gap with a wave**, not as an
> architectural claim. Any document, tender response or client assurance pack asserting
> "zero-trust architecture" without this table is overstating the position. `LG-021` §4.1.4's
> prohibition on implying certification applies here by analogy, and `SC-008` carries it as a
> disclosure obligation.

---

## 11. What Is Not Yet Evidenced

`LG-012` §4.7 sets the precedent: a claim of conformance the company has not demonstrated is a
misstatement, and the honest half of a statement is republished until it is empty. Applied to a
security architecture, this is what an enterprise client's security team, an insurer or a
regulator would ask for, and the answer today.

| What conformance requires | Status at 2026-08-18 12:55 (+06) | Closes with |
|---|---|---|
| A named CISO | **No such role exists.** Every control in §9 has an owner role; three of those roles are unfilled | `GV-002` `CC-01` |
| A named Chief Data Officer | **Not appointed.** `NFR-096` requires it if classified a significant data fiduciary — which at 250,000+ customers/month is near-certain | `SC-003`, `SC-008` |
| A threat model against these boundaries | **Does not exist** — 0 occurrences in the source estate | `SC-002` |
| A DPIA for high-risk processing | **Does not exist** — 17 references, 0 assessments | `SC-003` |
| 50 access profiles bound to roles | **Zero authored** (`OP-10`) | `SC-004` |
| A legal opinion on split residency | **Not obtained** (`DEP-31`, `D-13`) | `SC-007` |
| Break-glass path, envelope, holders, test schedule | **None exists** (`OP-08`) | `SC-011`, `PE-008` |
| A `dr` environment, sized and provisioned | **Named in the architecture, sized nowhere** (`OP-02`) | `PE-002`, `PE-007` |
| A Bangladesh-resident DR target for `Z4` | **Does not exist** (`OP-01`) | `SC-007`, `PE-007` |
| A populated `Z6` egress allow-list | **Not built.** 8 anticipated transfers, 0 registered | `IN-002`, `SC-007` |
| Vulnerability scanning evidence | **None exists** (`LG-021` `O-09`) | `SC-009` |
| Penetration test evidence | **None exists** | `SC-009` |
| A control register with test results | **Does not exist** (`LG-021` `O-04`) | `SC-008`, `M60` |
| Security awareness training delivery | **No vehicle** — `TR-025` unregistered | `TC-002` |
| The estate under version control | **644+ files, zero under version control** (`PGD-A2-15`) | `GV-011`, `PE-004` |
| An approval record for this document | **Cannot exist** until `GV-001` `CC-01` completes (`PGD-A2-25`) | `GV-002` |

> **`SEC-EV-1`.** This section is republished with every version, updated, until it is empty. It is
> not removed for presentation, and this document is **not circulated externally** while a blocking
> row stands.

---

## 12. Security Failure and Degradation Model

An architecture that has not stated what happens when a security component fails will improvise it
during the incident. Six components, six behaviours.

| Component fails | Behaviour | Justification | Compensating control |
|---|---|---|---|
| **WAF / `Z0` edge** | **Fail open** — traffic reaches `Z1` | A WAF outage must not take down 51+ branches. `Z1` still requires a valid token | `Z1` rate limits are independent of `Z0`; `SEC-C-011` anomaly defence continues |
| **Keycloak (identity)** | **Fail closed for new sessions; existing sessions continue to token expiry** | Cannot authenticate what cannot be verified. Killing live sessions turns an IdP blip into an estate outage | **Break-glass `SEC-C-035`** is the recovery path — and is the reason `OP-08` is a W1 blocker. `M29` `T-09` requires ≥ 99.99% |
| **Kong (`Z1` gateway)** | **Fail closed** | There is no bypass path. A gateway bypass is a permanent architectural weakness introduced for a temporary outage | Redundant gateway instances; `PE-001` |
| **Residency service `CD-233`** | **Fail closed.** Residency-classified reads and writes fail; **the rest of the system continues** | `LG-012` `RD-R2`: a write of a restricted field to the regional store **fails — it does not warn, log and proceed** | Degraded mode is explicit: the estate operates **without the sensitive fields** (`OP-012` §4.3 route 1) |
| **Vault** | **Fail closed for new leases; existing leases run to expiry** | Same reasoning as Keycloak. Unsealing is itself a break-glass event | Lease TTLs sized so an outage shorter than the TTL is invisible |
| **Audit subsystem** | ⚠ **Fail closed on write** — a transaction that cannot be audited does not commit | `BRU-SEC-12` and `NFR-014` are absolute; `DI-02` requires 100% financial coverage. An unaudited financial transaction is worse than a refused one | Audit write is in the same transaction (`SEC-SD-4`), so this is a durability property, not a runtime choice |

**Disaster recovery, as security constraints:**

| # | Constraint | Closes |
|---|---|---|
| `SEC-DR-01` | The regional tier fails over to a warm standby meeting RPO ≤ 15 min, RTO ≤ 2 h | `NFR-007` |
| `SEC-DR-02` | **`Z4` fails over only to a Bangladesh-resident standby.** A regional DR target for `Z4` is not an option — `NFR-086b` makes it a notifiable regulatory act, not a recovery step | **`OP-01`** |
| `SEC-DR-03` | The DR drill exercises **both tiers and the residency service**, twice yearly | `NFR-051` |
| `SEC-DR-04` | An **immutable backup copy outside the primary provider account** is required, or the ransomware and account-compromise scenarios have no assured recovery path | `OP-02` |
| `SEC-DR-05` | `dr` is sized from the security requirements above, not from spare capacity; **key material for `Z4` must be recoverable in-country** | `OP-02`, `SC-006` |

> **`SEC-DR-06`. Until `SEC-DR-02` has a target, `NFR-007` does not apply to residency-classified
> data, and the programme must say so** rather than imply otherwise. `AUDIT-017` `OP-01` states this
> and it is repeated here as an architectural position, because the alternative is an engineer
> choosing between a two-hour RTO and a statutory breach at 02:00.

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **Who is the CISO?** 68 controls have owner roles; the CISO, DPO and CDO roles are unfilled | CEO with the Board | **Now** | Approval of this document; `SC-003`; `NFR-096` |
| `Q-02` | Does the split-residency design satisfy the PDPA 2026 obligation? (`DEP-31`, `D-13`) | Legal Counsel | **Before W1 architecture freeze** | `SC-007`; the `Z4` field list |
| `Q-03` | Do bank details and individual payroll become residency-classified? (`LG-012` `RD1`) | CDO with EA | W1 | §8.4; `Z4` sizing; a later change is a **migration**, not a reclassification |
| `Q-04` | Is 1000FiX **critical information infrastructure** under the Cyber Security Ordinance 2025? | Legal Counsel | W2 | A CII designation requires **its own CERT/CIRT and SOC, with quarterly reports to the NCSA** — an obligation no document in the estate has costed. `SC-008`, `SC-011` |
| `Q-05` | Is `Z7` absorbed into `AR-001` §8.1, or does it remain a `SC-001` extension? | Chief Architect | W1 | Zone model single-sourcing; finding `SCA-04` |
| `Q-06` | Which of the 47 egress destinations may receive **any** personal data, and under which transfer row? | CDO with Legal | W1 | `Z6` allow-list configuration; `SEC-E-02` |
| `Q-07` | Is `SEC-CON-03` (no commercial security licence) sustainable for SIEM correlation, or does zero-trust tenet 7 stay deferred permanently? | CTO with CFO | W4 | §10; `SC-009`; `GV-008` |
| `Q-08` | Does `R38` sub-typing (`R38.1`…`R38.17`) happen before W1 external onboarding? | CTO | W1 | `EP-4` external rules; `SC-004` |

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-001-D-01` | Where is authorisation decided? | Edge-only · edge + record layer · record layer only | **In-transaction record layer, authoritative; edge is optimisation** | An edge check is one crafted request away from wrong; business permissions need business data | `EP-2` may never be cited as satisfying `NFR-015` |
| `SC-001-D-02` | Is Keycloak the permission engine? | Yes · No | **No — identity only** | Permission state would duplicate and drift | Keycloak authorisation services are not configured; roles map to Odoo groups |
| `SC-001-D-03` | How many paths into `Z4`? | Per-module · a shared library · one service | **One service (`CD-233`)** | One place to enforce, one place to audit | A network-layer denial for every other `Z2` workload; `CD-233` becomes availability-critical |
| `SC-001-D-04` | Does `Z5` reach `Z4`? | Yes with MFA · Yes with elevation · No | **No** | The largest-blast-radius population must not hold a standing bypass of the strongest control | Diagnostics limited to non-row operations; break-glass is the escape hatch (§5.5) |
| `SC-001-D-05` | Is remote support a zone? | Part of `Z2` · Part of `Z6` · Its own zone | **Its own zone `Z7`** | It is the only workload egressing into third-party networks and the only one where a session **is** a transfer | Adds a zone to `AR-001`'s six; declared as `SCA-04` |
| `SC-001-D-06` | Audit write failure behaviour | Fail open with alert · Queue and retry · Fail closed | **Fail closed** | `DI-02` requires 100% financial audit coverage; an unaudited financial transaction is worse than a refused one | Audit durability becomes an availability dependency; sized in `PE-006` |
| `SC-001-D-07` | ASVS level | L1 · L2 · L3 estate-wide | **L2 baseline, L3 for `Z4`-touching and payment paths** | L3 estate-wide is not proportionate at `SEC-CON-03`; L1 is insufficient for `D-1`…`D-4` | `SC-005` binds the level to the build gate per path |
| `SC-001-D-08` | Build `Z4` for 7 fields or 9? | 7 (`05-06` §6.4) · 9 (all `S3`) | **Provision for 9; classify 7** | A later reclassification of bank details or payroll would otherwise be a **cross-boundary migration** — the one act `NFR-086b` makes notifiable | `Z4` sized above its classified need; `SC-007` §6 |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every zone in §5.1 has stated ingress, egress, sensitivity and owner | §5.1 — 7 zones incl. `Z7`, all four columns populated |
| `AC-02` | Every permitted flow is stated, and every unstated flow is denied by default | §5.2 matrix with four footnoted exceptions |
| `AC-03` | Every enforcement point has a stated failure mode | §7.1 — 7 points, 7 failure modes |
| `AC-04` | Every control carries an owner **role**, a requirement and an Annex A reference | §9.2 — 68 controls, 4 columns each |
| `AC-05` | Annex A controls with **no** architectural realisation are named, not omitted | §9.4 — 22 named with owners |
| `AC-06` | Every figure describing the estate is counted, with disagreements recorded | §2.4 — 12 figures, 4 disagreements recorded as findings |
| `AC-07` | Every statutory or standards-version claim carries `verified_on` | Front matter; §2.1; re-verified in `SC-008` |
| `AC-08` | The zero-trust claim is decomposed per tenet with deferrals named | §10 — 4 adopted, 1 partial, 2 deferred |
| `AC-09` | What is not evidenced is stated plainly and not removed for presentation | §11 — 16 rows |
| `AC-10` | `SC-002` can begin: boundaries, elements, flows and assets are enumerated | §4.2, §5.1, §5.2, §6.1, §7.1, §8.1 |
| `AC-11` | `QA-007` can derive a test from every control | §9.2; `AC-04` |
| `AC-12` | No claim of ISO 27001 certification appears anywhere | §2.1 departure note; §9.4 |

**Definition of done.** Complete when every criterion above is met, its `PGD-000` status is updated
with a fresh enumeration timestamp, and its approver has signed. **The approval record cannot exist
until `GV-001` `CC-01` completes** (`PGD-A2-25`); the ✅ is qualified accordingly.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §8.1–§8.3, §9.1 | Zones, tiers and residency topology inherited |
| Upstream | `RQ-006` | The NFR set this architecture realises |
| Upstream | `GV-002` | Constitutes the body that can approve this |
| Downstream | `SC-002` | Threat models against §5 boundaries and §4.2 elements |
| Downstream | `SC-004` | Realises `EP-3`…`EP-6`; owns the 50-role model and the access profiles |
| Downstream | `SC-005` | Realises `SEC-C-055`, `SEC-C-056`; binds ASVS 5.0 L2/L3 per `SC-001-D-07` |
| Downstream | `SC-006` | Realises §7.5 key flow; algorithms and lifetimes |
| Downstream | `SC-007` | Governs `Z4`, `EP-7` and the `Z6` transfer rows |
| Downstream | `SC-009` | Derives scope from §5 zones and §4.2 surface count |
| Downstream | `SC-010` | Realises `SEC-C-038`…`SEC-C-043` |
| Downstream | `SC-011` | Realises `SEC-C-067`; owns break-glass operation |
| Downstream | `PE-001` | Builds §5.2 as network policy; `SEC-C-061`, `SEC-C-062` |
| Downstream | `QA-007` | Derives a test per control |
| Lateral | `../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` | The module that realises most of §9 |
| Lateral | `../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_*.md`, `M06_*.md` | `Z7` and `D-2` |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-021_*.md` | The human-facing counterpart of this document |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-012_*.md` | The residency position §8 enforces |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./SC-002` … `./SC-011` · `../02_Architecture_and_Design/AR-001_Software_Architecture_Document.md` ·
`../01_Requirements_Engineering/RQ-006_Non_Functional_Requirements_Specification.md` ·
`../00_Programme_Governance_and_Control/GV-002_*.md`, `GV-005_*.md`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_Identity_Access_and_Information_Security.md` ·
`../../1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60_Governance_Risk_and_Compliance.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md`, `05-03_*.md`, `05-04_*.md`, `05-06_*.md` ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md`, `00-07_*.md` ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-012_*.md`, `LG-020_*.md`, `LG-021_*.md` ·
`../../project_content/06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006_*.md` ·
`../../project_content/17_Operations_Support_and_Runbooks/OP-009_*.md`, `OP-015_*.md` ·
`../../project_content/_AUDIT/AUDIT-017_Category_17_OP_Content_Audit.md`

**External standards and sources** *(all verified 2026-08-18)*

| Source | Version / date | Used for |
|---|---|---|
| ISO/IEC 27001 | **:2022 + Amd 1:2024** (Amd published February 2024 — climate action; **no new Annex A controls**) | §9 control crosswalk |
| ISO/IEC 27002 | :2022 — 93 controls, 4 themes | Control implementation reference |
| ISO/IEC 27033-1/-2 | Network security zones and conduits | §5 |
| ISO/IEC/IEEE 42010 | :2022 | Security viewpoint of `AR-001` |
| NIST SP 800-207 | Zero Trust Architecture, August 2020 | §10 tenets |
| **OWASP ASVS** | **5.0.0, released 30 May 2025** — 17 chapters, ~350 requirements, 3 levels. **Supersedes 4.0.3** | `SC-001-D-07`; `SC-005` gate |
| OWASP Core Rule Set | Current CRS release | `Z0` WAF |
| **OWASP Top 10** | **2025 edition, published 6 November 2025**, finalised January 2026 — adds **A03 Software Supply Chain Failures** and **A10 Mishandling of Exceptional Conditions** | `SC-002` threat classes; `SC-005` |
| Personal Data Protection Act 2026 (Law 63 of 2026), Bangladesh | Enacted April 2026; enforcement ~13 May 2027; regulator **National Data Management Authority** | `D-1`, §8, `SC-003`, `SC-007` |
| **Cyber Security Ordinance 2025** (Ordinance No. 25 of 2025), Bangladesh | Gazetted 21 May 2025; **in force**. Establishes the National Cyber Security Agency; a declared **CII must operate its own CERT/CIRT and SOC with quarterly reports to the NCSA** | `Q-04`; `SC-008`; `SC-011` |
| Keycloak | 26.x (`TD-07`) | Identity |
| Kong Gateway | 3.x (`TD-08`) | `Z1` |

> Every path above was resolved at 2026-08-18 12:55 (+06). `PGD-A2-16` records that **14 of 14
> navigation footers in this repository failed to resolve** at the Category 00 audit; this
> document's references were checked individually rather than inherited.

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Establishes the zone, enforcement, isolation and control architecture; adds `Z7`; closes the architecture half of `OP-08`; corrects the role target from 46 to 50 and the ASVS version from 4 to 5.0.0 | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-001` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
