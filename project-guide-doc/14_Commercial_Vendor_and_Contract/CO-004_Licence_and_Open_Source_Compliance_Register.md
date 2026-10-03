---
id: CO-004
title: Licence & Open-Source Compliance Register
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Financial Officer, with the Chief Architect as technical custodian
approver: ERP Steering Committee, with Legal Counsel sign-off on §7 and §8
standards_basis: >
  ISO/IEC 5230:2020 (OpenChain — open-source licence compliance programme; Linux Foundation
  OpenChain Specification 2.1) · ISO/IEC 18974:2023 (OpenChain security assurance) ·
  SPDX 3.0.1 licence identifiers · CycloneDX 1.7 (ECMA-424, 2nd edition) ·
  ISO/IEC 19770-1:2017 (IT asset management systems) · ISO/IEC 19770-3:2016 (software
  entitlement schema) · ISO 9001:2015 §8.4 · ISO 19011:2018 §6.4 (verification of evidence)
traces_to: >
  PGD-000 CO-004 · 02-05 §4 ("a licence register is maintained in M30 and reviewed annually" —
  M30 is a specification, not a register) · 02-05 §6 (L6 commercial set) · AR-013 §6, §6.1
  (LW-01…LW-05), §7, §7.1 (L6-01…L6-05) · BE-007 §6, §6.1–§6.4, §7 (LX-21…LX-32) ·
  BE-007 BEA-15, BEA-16 · PE-008 §3.4 PE-008-F-01 · RFP §19.1(3), §19.1(4) · CO-003 SOW-34,
  SOW-64 · CO-005 §5.5 · CO-006
depends_on: AR-013 · BE-007 · PE-008 · CO-003 · CO-005 · SC-007 · GV-003 · GV-005
verified_on: 2026-08-19
priority: P1
needed_by: W1
enumeration_timestamp: 2026-08-19 02:36 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CO-004 — Licence & Open-Source Compliance Register

### Category 14 · Code `CO` · ISO/IEC 5230:2020 (OpenChain) · ISO/IEC 18974:2023 · SPDX 3.0.1 · ISO/IEC 19770-1:2017

---

> **Local rule prefix: `LIC-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 02:36 (+06), by
> `grep -rho "LIC-[0-9]\{1,3\}" --include=*.md .` across all six repositories.
>
> **⚠ The category code `CO` is already a rule prefix in three unrelated namespaces** — cost
> controls in `PE-006` §8.4, content-operating-model rules in `CG-002`, callback-ordering rules in
> `IN-006`; **108 occurrences across 30 files and 3 repositories**. No document in Category 14 uses
> `CO-nn` as a local rule prefix. Recorded as `CVA-01`.

---

## 1. Purpose

`02-05` §4 closes its licence analysis with one sentence:

> *"A licence register is maintained in M30 and reviewed annually."*

**M30 is `cd_platform_ops` — a module specification. It is not built, and a specification is not a
register.** `BE-007` §6.1 states the same thing from the engineering side: *"M30 is unbuilt, so no
register exists."*

Two documents have since built most of what was missing. **This document is not a third copy of
them**, and stating the boundary first is the only way to keep three documents from diverging into
the `PGD-A2-11` defect:

| Document | Owns | Form |
|---|---|---|
| **`BE-007`** | The **machine check**. `tooling/LICENCES.yaml`, the allow/gated/deny policy, `LX-21`…`LX-32`, the CycloneDX SBOM, the `NOTICE.md` generation | A file the build reads, enforced in CI |
| **`AR-013`** | The **architectural position**. The radar ring, the named fallback, `LW-01`…`LW-05`, and the four L6 components as a bounded set | An architecture decision record |
| **`CO-004`** *(this document)* | The **register of record**. Every obligation, its **named owner**, its **verified-on date**, its **evidence**, and the obligations **no code check can see** | An accountable register, reviewed at every wave gate |

> **The difference that justifies a third document.** A CI check can prove that no AGPL component
> entered the build. It cannot prove that **a human being is accountable for the AGPL obligation**,
> that the obligation was **re-verified** when the upstream project changed its licence, or that
> someone **decided** whether shipping a GPL-2 agent to a client's Windows estate is distribution.
> `BE-007` `LX-27` and `LX-28` say those two decisions go *"to the Chief Architect and CFO"* — and
> until this document, there was nowhere for that decision to be recorded.

### 1.1 What this document found

Four positions carried across the estate are wrong or incomplete, and two of the four are on **Wave
1** components. They are stated here rather than in an appendix because they are the reason the
document is `P1` and not `P3`.

| # | Finding | Severity | Where |
|:--:|---|:--:|---|
| **`CVA-15`** | **OCA modules are recorded estate-wide as LGPL-3. They are predominantly AGPL-3.** The estate's AGPL network-service test (`BE-007` §6.3) covers six components and **does not cover the module layer the programme plans to modify** | **High** | §6.3 |
| **`CVA-16`** | **`02-05` §4 records "Redis 7.x — BSD-3". Only Redis ≤ 7.2 is BSD-3**; 7.4–7.8 are RSALv2 / SSPLv1 source-available; 8.0+ adds AGPLv3. **RSALv2 appears in no list in `BE-007`'s policy file** — not allow, not gated, not deny | **High** | §6.4 |
| **`CVA-17`** | **The estate has no outbound licence position.** 1000FiX grants software access to marketplace sellers, brand partners, corporate clients and MSP customers through twelve portals, and no document states what licence terms it grants them or what it warrants about the open-source components underneath | Medium | §8 |
| **`CVA-18`** | **`02-05` §4's *"reviewed annually"* is still the position of record in the primary architecture document**, although `AR-013` `LW-03` and `BE-007` `LX-30` both replaced it with a wave-gate cadence. Three documents, two cadences | Medium | §9.1 |

### 1.2 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | **Register A** — every open-source component deployed, with SPDX identifier, obligation, **named owner**, verified-on date, evidence and fallback (§5) |
| 2 | The **AGPL-3 position**, applied per component, including the module layer the estate's existing test omits (§6.3) |
| 3 | The **source-available and fair-code** positions: BSL, TSL, RSALv2, SSPLv1, Sustainable Use (§6.4, §6.5) |
| 4 | The **obligations no code check can see** — usage and product decisions (§7) |
| 5 | **Register B** — commercial entitlements: the four L6 components, their metrics, caps, renewals and exits (§8.1) |
| 6 | **Register C** — inbound contractual licences from the implementation partner, and **outbound** licences 1000FiX grants (§8.2, §8.3) |
| 7 | **Component currency** — the two components whose upstream position has changed and what to do (§6.4, §6.6) |
| 8 | **Governance** — obligation ownership, review cadence, the attestation record, and the escalation path (§9) |
| 9 | The contractual hooks in `CO-003` that make a supplier's licence conduct enforceable (§10) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **build-time licence check**, `LICENCES.yaml`, SBOM generation, `NOTICE.md` | `BE-007` §6, §8 | The machine control. This document records **who is accountable** and **what was verified when** |
| **Radar rings**, adoption procedure, version currency policy | `AR-013` §3, §8, §9 | The architectural position |
| **Vulnerability** management and VEX | `BE-007` §5; `SC-009` | ISO/IEC 18974 is cited in §2.1 for the boundary, not claimed |
| **Purchasing** an L6 component — approval route, PO, supplier onboarding | `CO-006` | §8.1 registers the entitlement; `CO-006` acquires it |
| **Costing** the L6 set and the licence-driven infrastructure | `CO-005` §5.5 | §8.1's caps are the input to that costing |
| The **supplier's own** ISO 27001, insurance and corporate standing | `CO-002` §10 | Due diligence on the counterparty, not on components |
| **Data-protection** obligations of processors | `CO-003` §14; `SC-003` | A different legal regime with a different register |

### 1.3 Intended audience

| Audience | What they use this register for |
|---|---|
| **Chief Financial Officer** | The owner. §8.1's entitlements, caps and renewals; the `L6-01` approval record |
| **Chief Architect** | Technical custodian. §5's register, §6's obligations, and the `LW-02` gate on new gated components |
| **Legal Counsel** | §7's usage obligations and §8's inbound and outbound positions — the three that need an opinion, not an assumption |
| Platform Engineering / build team | §5's fallback column is what they implement when `LW-03` finds a change |
| **Implementation partner** | §10 — what `CO-003` `SOW-34` and `SOW-64` require them to contribute to this register, and what they may not do without approval |
| Corporate clients, brand partners, auditors | §8.3 — the outbound position and the SPDX export that answers their supply-chain questions |
| Audit Committee | §9.3's attestation record: every obligation, its owner, and the date it was last verified |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this document conforms | Departure and rationale |
|---|---|---|---|
| **ISO/IEC 5230:2020** *(OpenChain, from Linux Foundation OpenChain Specification 2.1)* | §3.1 programme foundation · §3.2 **assigned responsibility** · §3.3 review and approval of licence obligations · §3.5 compliance artefact delivery · §3.6 understanding community engagement | §9.2 assigns responsibility per obligation; §5 and §8 are the review record; `BE-007` §8's SBOM and `NOTICE.md` are the compliance artefacts; §7.3 is community engagement | **Partial and declared.** ISO/IEC 5230 conformance is a **programme** attestation, and 1000FiX has not made one. This document supplies §3.2 and §3.3 — the two clauses the estate was missing. `LIC-Q-05` asks whether the Company should seek conformance, which brand partners and corporate clients increasingly request |
| **ISO/IEC 18974:2023** *(OpenChain security assurance)* | — | **Referenced for the boundary only.** Vulnerability management is `BE-007` §5 and `SC-009` | Not claimed. Naming it and not claiming it is the point: an estate that cites OpenChain should know there are two OpenChain standards and which one it is talking about |
| **SPDX 3.0.1** | Licence identifiers | Every row in §5 carries a valid SPDX identifier, or is explicitly marked as **not having one** — which is itself the finding for RSALv2 and n8n Sustainable Use | None |
| **CycloneDX 1.7** *(ECMA-424, 2nd ed.)* | — | The SBOM that populates the transitive layer of this register is `BE-007` §8's | This register covers the **~35 deployed systems**; the SBOM covers the thousands of transitive dependencies beneath them. §5.1 states that boundary explicitly |
| **ISO/IEC 19770-1:2017** *(Edition 3; reviewed and confirmed 2024)* | §8 operational planning; entitlement–consumption reconciliation | §8.1 models each L6 component as an entitlement with a metric, a cap and a renewal | Full conformance is an ITAM management system the Company does not have. The entitlement-modelling clause is adopted; the rest is not claimed |
| **ISO/IEC 19770-3:2016** | Software entitlement schema | §8.1's columns follow the entitlement schema's fields: right, metric, limitation, term | Expressed as a table, not as the XML schema |
| **ISO 9001:2015 §8.4** | Control of externally provided products | §10's contractual hooks | Delegated to `CO-003` |
| **ISO 19011:2018 §6.4** | Verification of evidence | §5.1's **verification-status column**: a row carried from another document is marked as carried, not as verified | None. This is the rule `PG-03` and `PG-M4` already impose |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `02-05` §4 and its Licence Compliance Notes | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | The 24-row Layer 4 stack table and the five-licence obligation summary. **The origin of `CVA-15`, `CVA-16` and `CVA-18`** |
| `02-05` §2, §3, §5, §6 | as above | Layer 1 (Odoo 19 CE), Layer 2 (OCA), Layer 5 (custom), Layer 6 (commercial) |
| `AR-013` §6, §6.1, §7, §7.1 | `../02_Architecture_and_Design/AR-013_*.md` | The licence-currency watch, `LW-01`…`LW-05`, the L6 register and `L6-01`…`L6-05` |
| `BE-007` §6.1–§6.4, §7.1–§7.3 | `../07_Build_Engineering_and_Development_Standards/BE-007_*.md` | `LICENCES.yaml`'s allow/gated/deny policy; `LX-21`…`LX-32`; the AGPL-3 test applied to six components; **`BEA-15`** (Wazuh distribution) and **`BEA-16`** (MinIO archived) |
| `PE-008` §3.4 | `../10_Infrastructure_DevOps_and_Environments/PE-008_*.md` | **`PE-008-F-01`** — the observability stack violated `LW-01`; Loki and Tempo were not on the radar at all. Closed there; carried here |
| `CO-003` §13 | `./CO-003_*.md` | `SOW-34` and `SOW-64` — the supplier's obligations into this register |
| `CO-005` §5.5 | `./CO-005_*.md` | The L6 cost restatement and the fifth-component exposure |
| RFP §19.1(3), §19.1(4) | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | The perpetual royalty-free licence on pre-existing frameworks; **the obligation to contribute OCA migrations upstream** |
| Odoo 19.0 licensing documentation | External, **verified 2026-08-19** | Odoo 19 Community Edition is **LGPL-3** |
| OCA published licensing position and the OCA/Odoo licence agreement | External, **verified 2026-08-19** | **OCA modules are predominantly AGPLv3**; LGPL-3 and AGPL-3 coexist; AGPL is retained *"to protect users of OCA addons from being locked in by service providers"* |
| Redis published licence pages and release history | External, **verified 2026-08-19** | BSD-3 through **7.2**; **7.4–7.8 RSALv2 / SSPLv1**; **8.0+ tri-licence adding AGPLv3**; Valkey forked from 7.2 under BSD-3, Linux Foundation |
| MinIO repository and community reporting | External, **verified 2026-08-19** | Maintenance mode December 2025; **archived 25 April 2026**; server code remains AGPL-3. **Garage** (AGPL-3, Rust, S3-compatible, release 16 April 2026) and **SeaweedFS** (Apache-2.0) are maintained alternatives |
| n8n Sustainable Use Licence | External, **verified 2026-08-19** | *"Internal business purposes"*, with the test being whether value derives **"entirely or substantially"** from n8n functionality; consulting and building workflows for clients is **permitted**; white-labelling, hosting-for-fee and building a competing automation platform are **not** |

### 2.3 Findings this document closes or raises

| Finding | Source | How |
|---|---|---|
| *"A licence register is maintained in M30"* — M30 is a specification | `PGD-000`; `02-05` §4 | **Closed.** §5 and §8 are the register; §9.2 gives every obligation an owner |
| **`PE-008-F-01`** | `PE-008` §3.4 | **Carried and closed in the register.** Grafana, Loki and Tempo now have named fallbacks in §5 |
| **`BEA-15`** — Wazuh distribution to client endpoints | `BE-007` §6.4 | **Owned.** §7.2 assigns it to Legal Counsel with a date and states what turns on the answer |
| **`BEA-16`** — MinIO archived | `BE-007` §7.1 | **Owned and costed.** §6.6; `CO-005` §5.5's fifth-L6 exposure; `LIC-Q-01` |
| `L6-05` — every L6 component has a documented exit | `AR-013` §7.1 | **Discharged.** §8.1's exit column |
| **`CVA-15`** | This document | **Raised, High.** OCA is AGPL-3, not LGPL-3. §6.3 |
| **`CVA-16`** | This document | **Raised, High.** Redis 7.x spans two licence regimes; RSALv2 is in no policy list. §6.4 |
| **`CVA-17`** | This document | **Raised, Medium.** No outbound licence position. §8.3 |
| **`CVA-18`** | This document | **Raised, Medium.** Two review cadences in three documents. §9.1 |

---

## 3. The Register Model

Three registers, because three different things are being tracked and merging them is how obligations
get lost.

| Register | Tracks | Owner | Reviewed |
|:--:|---|---|---|
| **A — Components** (§5, §6) | Open-source components the Company **deploys**, and the obligation each creates | Chief Architect | **Every wave gate** |
| **B — Entitlements** (§8.1) | **Commercial** licences the Company **buys** — the L6 set — as entitlements with metrics, caps and terms | CFO | Every wave gate, and at renewal |
| **C — Contractual** (§8.2, §8.3) | Licences **granted to** the Company by its supplier, and licences **granted by** the Company to its customers | Legal Counsel | At contract, and annually |

| # | Rule |
|---|---|
| **`LIC-01`** | **Every obligation in every register has exactly one named owner role.** Not a team, not a committee. ISO/IEC 5230 §3.2 requires assigned responsibility, and a shared obligation is an unowned one |
| **`LIC-02`** | **Every row carries a `verified_on` date and a verification method.** A row carried from another document is marked **carried**, not verified — `PG-M4`, ISO 19011 §6.4 |
| **`LIC-03`** | **A row with no fallback may not be `Adopt`** (`AR-013` `LW-01`), and *"there are alternatives"* is not a fallback (`BE-007` `LX-32`) |
| **`LIC-04`** | This register covers **deployed systems**. The **transitive** dependency layer is covered by the CycloneDX SBOM (`BE-007` §8) and is reconciled to this register at each wave gate — §9.4 |

---

## 4. The Obligation Classes

Six classes. Each has a different trigger, and confusing the trigger is how compliance failures
happen quietly.

| Class | Trigger | Detectable by a code check? | Components |
|:--:|---|:--:|---|
| **O1 — Attribution** | Distribution or deployment | ✅ `NOTICE.md`, generated (`LX-24`) | Apache-2.0, MIT, BSD-2, BSD-3, ISC, PostgreSQL |
| **O2 — Library modification** | Modifying the library itself | ✅ `FF-03` blocks a `vendor/` diff | LGPL-3 — Odoo 19 CE |
| **O3 — Network service** | **Modification _combined with_ serving over a network** | ⚠ Partly. The **modification** half is checkable; the **network** half is an architecture fact | AGPL-3 — Metabase, Grafana, Loki, Tempo, MinIO, RustDesk, **and the OCA module layer** |
| **O4 — Source-available field-of-use** | Using the software outside the permitted field of use | ❌ **A product decision, not a commit** | BSL (Redpanda), TSL (TimescaleDB), RSALv2/SSPLv1 (Redis 7.4+), Sustainable Use (n8n) |
| **O5 — Copyleft on distribution** | **Distributing** the binary to a third party | ❌ Depends on what "ship" means operationally | GPL-2 — Wazuh, on client endpoints |
| **O6 — Contractual** | The contract | ❌ | RFP §19.1(3) framework licences; §19.1(4) upstream contribution; escrow |

> **`LIC-05` — classes O4, O5 and O6 are reviewed by a human at every wave gate, because no
> automation will ever detect them.** `BE-007` §6.4 says the same thing about two of them: *"the
> breach is a product decision, not a commit."* This register exists mainly for these three classes;
> O1, O2 and the checkable half of O3 are already handled well by `BE-007`.

---

## 5. Register A — Components

### 5.1 Scope and verification convention

**This register covers the ~35 systems the Company deploys as identifiable components.** It does
**not** enumerate the transitive dependency tree — thousands of Python, Node, Dart and Go packages —
which is `BE-007` §8's CycloneDX SBOM. §9.4 reconciles the two.

**Verification convention**, per `LIC-02`:

| Mark | Meaning |
|:--:|---|
| **✔ 2026-08-19** | Licence position **independently verified** against the upstream project's own published licensing during this session |
| **▣ carried** | Carried from `02-05` §4, `AR-013` §6 or `BE-007` §6.2 and **not independently verified**. Not an assertion of currency |
| **⚠** | Verified **and found to differ** from the estate's recorded position |

### 5.2 The register

| # | Component | SPDX / licence | Class | Obligation | **Owner** | Fallback (`LW-01`) | Wave | Verified |
|:--:|---|---|:--:|---|---|---|:--:|:--:|
| 1 | **Odoo 19 Community Edition** | `LGPL-3.0-or-later` | O2 | Modifications **to the library** must be shared. Extensions as separate modules are not modifications (`AS-05`, `AR-007` §5) | Chief Architect | — *(platform decision, `AR-013` #1)* | W1 | **✔ 2026-08-19** |
| 2 | **OCA modules** | **`AGPL-3.0-or-later`** *(predominantly; some LGPL-3)* | **O3** | **Source disclosure if modified and served over a network.** §6.3 | **Chief Architect** | Custom L5 re-implementation (`AR-013` #2, `W0-01`) | W1 | **⚠ ✔ 2026-08-19** |
| 3 | **PostgreSQL 16** | `PostgreSQL` | O1 | Attribution | Platform Engineering | — | W1 | ▣ carried |
| 4 | **PgBouncer** | `ISC` | O1 | Attribution | Platform Engineering | Odyssey; pgcat | W1 | ▣ carried |
| 5 | **Redis** | ⚠ **`BSD-3-Clause` only to 7.2**; **RSALv2 / `SSPL-1.0` for 7.4–7.8**; **tri-licence adding `AGPL-3.0-only` from 8.0** | **O4 / O3** | Depends entirely on the pinned version. §6.4 | **Chief Architect** | **Valkey** (`BSD-3-Clause`, Linux Foundation) — **not currently on the radar** | W1 | **⚠ ✔ 2026-08-19** |
| 6 | **Keycloak** | `Apache-2.0` | O1 | Attribution | Security Lead | — | W1 | ▣ carried |
| 7 | **Kong Gateway** | `Apache-2.0` | O1 | Attribution; free-tier scope | Solution Architect | Nginx + custom (`AR-013` #12) | W1 | ▣ carried |
| 8 | **n8n** | **n8n Sustainable Use** *(no SPDX identifier exists)* | **O4** | **Internal business purposes only.** §7.1 | **CFO with Chief Architect** | Temporal; Apache Airflow | W1 | **✔ 2026-08-19** |
| 9 | **Novu** | `MIT` | O1 | Attribution | Solution Architect | Custom dispatcher | W1 | ▣ carried |
| 10 | **MinIO** | `AGPL-3.0-or-later` | **O3** | **Archived upstream 25 April 2026.** §6.6 | **Chief Architect** | **Garage** (`AGPL-3.0`, maintained) · **SeaweedFS** (`Apache-2.0`) · managed object store *(residency-constrained)* | W1 | **⚠ ✔ 2026-08-19** |
| 11 | **Nginx** | `BSD-2-Clause` | O1 | Attribution | Platform Engineering | — | W1 | ▣ carried |
| 12 | **Docker** | `Apache-2.0` | O1 | Attribution | Platform Engineering | Podman | W1 | ▣ carried |
| 13 | **K3s** | `Apache-2.0` | O1 | Attribution | Platform Engineering | k0s; kubeadm | W1 | ▣ carried |
| 14 | **Traccar** | `Apache-2.0` | O1 | Attribution | Solution Architect | — | W2 | ▣ carried |
| 15 | **OSRM** | `BSD-2-Clause` | O1 | Attribution | Solution Architect | Valhalla | W2 | ▣ carried |
| 16 | **VROOM** | `BSD-2-Clause` | O1 | Attribution | Solution Architect | Timefold *(commercial — would become L6)* | W2 | ▣ carried |
| 17 | **TimescaleDB** | `Apache-2.0` core; **TSL** for advanced features | **O4** | **Apache-2.0 features only, CI-checked.** A TSL dependency converts a $0 component into a licensed one mid-programme | Chief Architect | Plain PostgreSQL partitioning | W2 | ▣ carried |
| 18 | **Grafana** | `AGPL-3.0-only` | O3 | Deployed unmodified | Platform Engineering | **Perses** (CNCF, `Apache-2.0`); alerting to Prometheus Alertmanager | W2 | ▣ carried *(fallback from `PE-008` §3.4)* |
| 19 | **Prometheus** | `Apache-2.0` | O1 | Attribution | Platform Engineering | — | W3 | ▣ carried |
| 20 | **OpenTelemetry** | `Apache-2.0` | O1 | Attribution | Platform Engineering | — *(and it is the reason the other fallbacks are cheap — `PE-008-D-02`)* | W3 | ▣ carried |
| 21 | **Loki** | `AGPL-3.0-only` | O3 | Deployed unmodified | Platform Engineering | **OpenSearch** (`Apache-2.0`) | W3 | ▣ carried *(added by `PE-008` §3.4)* |
| 22 | **Tempo** | `AGPL-3.0-only` | O3 | Deployed unmodified | Platform Engineering | **Jaeger** (CNCF, `Apache-2.0`) | W3 | ▣ carried *(added by `PE-008` §3.4)* |
| 23 | **Metabase** | `AGPL-3.0-or-later` | **O3** | **Embedded in six portals via signed tokens.** The estate's highest AGPL risk — §6.2 | Chief Architect | Apache Superset | W4 | ▣ carried |
| 24 | **Mayan EDMS** | `Apache-2.0` | O1 | Attribution | Quality Manager | OCA `dms` *(the W1–W4 incumbent)* | W5 | ▣ carried |
| 25 | **MeshCentral** | `Apache-2.0` | O1 | Attribution | Corporate Services Head | — | W5 | ▣ carried |
| 26 | **RustDesk** | `AGPL-3.0-only` | O3 | Deployed unmodified; **support sessions run with clients** | Corporate Services Head | MeshCentral (`Apache-2.0`) | W5 | ▣ carried |
| 27 | **Wazuh** | `GPL-2.0-only` | **O5** | **Copyleft on distribution.** Agents on client estates — §7.2, `BEA-15` | **Legal Counsel** | osquery (`Apache-2.0`) | W5 | ▣ carried |
| 28 | **osquery** | `Apache-2.0` | O1 | Attribution | Corporate Services Head | — | W5 | ▣ carried |
| 29 | **Redpanda** | **BSL 1.1** | **O4** | Converts to `Apache-2.0` four years after each merge; production use within limits | Chief Architect | **Kafka** (`Apache-2.0`) | W6 | ▣ carried |
| 30 | **MLflow** | `Apache-2.0` | O1 | Attribution | Chief Architect | — | W6 | ▣ carried |
| 31 | **Ollama** | `MIT` | O1 | Attribution. **Model weights carry their own separate licences** — §6.7 | Chief Architect | vLLM; llama.cpp | W6 | ▣ carried |
| 32 | **ClickHouse** | `Apache-2.0` | O1 | Attribution | Chief Architect | PostgreSQL analytics *(does not scale to W8 volume)* | W8 | ▣ carried |
| 33 | **Flutter / Dart SDK** | `BSD-3-Clause` | O1 | Attribution | Mobile Lead | — | W2 | ▣ inferred from `02-05` §5.4 |
| 34 | **Next.js / React** | `MIT` | O1 | Attribution | Frontend Lead | — | W1 | ▣ inferred from `02-05` §5.4 |
| 35 | **Python / Node.js / Go runtimes** | `PSF-2.0` / `MIT` / `BSD-3-Clause` | O1 | Attribution | Platform Engineering | — | W1 | ▣ inferred from `02-05` §5.3 |

**Verification of the count** *(regenerated per `PG-M10`)*: rows 1–35 = **35 components** ·
by class: **O1 = 22** (rows 3, 4, 6, 7, 9, 11, 12, 13, 14, 15, 16, 19, 20, 24, 25, 28, 30, 31, 32,
33, 34, 35) · **O2 = 1** (row 1) · **O3 = 7** (rows 2, 10, 18, 21, 22, 23, 26) · **O4 = 4** (rows 8,
17, 29, and row 5 in its 7.4+ form) · **O5 = 1** (row 27). 22 + 1 + 7 + 4 + 1 = **35** ✓.

> **Compare with `02-05` §4, which lists 24 rows and analyses five licences.** This register carries
> **35 components across six obligation classes**, of which **five were independently verified
> this session, and three of those five — rows 2, 5 and 10 — are marked ⚠, verified and found to
> differ from the recorded position.** The remaining **thirty rows are marked ▣ carried** and are
> **not** claimed as verified: `LIC-Q-04` schedules their verification at the Wave 1 gate, because a
> register whose rows are six-sevenths unverified is a plan for a register, not a register.
>
> **Verification of these counts** *(regenerated per `PG-M10`)*: 35 rows · ✔ = 2 (rows 1, 8) ·
> ⚠✔ = 3 (rows 2, 5, 10) · ▣ = 30 (27 carried + 3 inferred). 2 + 3 + 30 = **35** ✔.

---

## 6. The Copyleft and Source-Available Positions

### 6.1 The AGPL-3 test

AGPL-3 §13 triggers on **modification** combined with **network service**. Both halves are needed;
neither alone is enough. `BE-007` §6.3 applies the test to six components and the answers are carried
here. **This section adds the seventh, which the estate's test omits.**

| Component | Modified? | Served over a network to third parties? | **Disclosure obligation?** | What would trigger it |
|---|:--:|---|:--:|---|
| **Metabase** | No | **Yes** — embedded in `P06`, and via signed embed tokens in `P03`, `P04`, `P07`, `P08` | **No**, because unmodified | Patching Metabase to change embedding, theming or authentication |
| Grafana / Loki / Tempo | No | Internal only | No | Patching a dashboard renderer or an ingester |
| MinIO | No | Internal only | No | Patching the server. **See §6.6 — an archived upstream makes patching far more likely** |
| RustDesk | No | **Support sessions with clients** | No | Patching the client |
| **OCA modules** | **Intended — v19 migration** | **Yes — twelve portals** | **§6.3** | **Already contemplated by `AR-013` decision 2** |

### 6.2 Metabase — the realistic trigger

`BE-007` §6.3 states it well and it is repeated here because the owner needs to see it in their own
register: *"The realistic trigger is Metabase. `P06` embeds it in six portals with signed tokens, and
the gap between 'configure the embed' and 'patch the embed to look right' is one frustrated
afternoon."*

| # | Rule |
|---|---|
| **`LIC-06`** | **Configuration, theming through supported extension points, and embedding are not modification. Patching source is.** The boundary is `vendor/`: anything requiring a diff there triggers the obligation (`BE-007` `LX-25`) |
| **`LIC-07`** | Any proposed modification to an AGPL component requires **Chief Architect approval and a published-source plan, before the change is written** (`BE-007` `LX-26`) — and, added here, a **CFO notification**, because publishing source is a commercial act with consequences for a company that competes on its platform |

### 6.3 `CVA-15` — the OCA module layer is AGPL-3, and the estate says LGPL-3

**The recorded position**, identical in three documents:

| Document | Text |
|---|---|
| `02-05` §4 Licence Compliance Notes | *"**LGPL-3 (Odoo, most OCA)** — Modifications to the library itself must be shared — Extensions are separate modules, not modifications to core"* |
| `AR-013` §6 | *"**Odoo CE / most OCA — LGPL-3** — Modifications to the library must be shared"* |
| `BE-007` §6.2 | *"**LGPL-3 — Odoo, most OCA** — Modifications to the library must be shared"* |

**The verified position** *(2026-08-19, against the OCA's own published licensing position and the
OCA–Odoo licence agreement)*:

| Layer | Licence |
|---|---|
| **Odoo 19 Community Edition** | **LGPL-3** ✔ — the estate is correct |
| **OCA modules** | **Predominantly AGPL-3**, with some LGPL-3. The OCA retains AGPL deliberately, *"to protect users of OCA addons from being locked in by service providers"* — the licence is the point of the licence, not an accident |

**Why the difference matters, in three steps:**

| Step | LGPL-3 (what the estate assumes) | **AGPL-3 (what is actually there)** |
|:--:|---|---|
| 1 | Obligation triggers on **modifying the library** | Obligation triggers on **modifying** *and* **serving over a network** |
| 2 | The estate's control is `AS-05` — *"extensions are separate modules, not modifications to core"* | **`AS-05` does not help**, because the plan is not to extend OCA modules from outside. `AR-013` decision 2 explicitly contemplates **migrating OCA `field-service` to v19**, and a migration is a modification |
| 3 | Serving over a network is irrelevant | **The system serves twelve portals to customers, sellers, brand partners and corporate clients.** The network half is satisfied on day one |

> **Stated plainly: the moment the programme migrates an AGPL-3 OCA module to v19 and runs it behind
> a customer-facing portal, 1000FiX has an obligation to make the corresponding source available to
> those users.**
>
> **The good news is that the mitigation already exists — but it is recorded as goodwill rather than
> as a legal discharge.** RFP §19.1(4) requires the supplier to *"contribute OCA migrations
> upstream."* **That is exactly how the AGPL-3 obligation is discharged**: a migration contributed
> upstream is published source. It is not a community nicety and it is not a negotiable line item.

| # | Rule |
|---|---|
| **`LIC-08`** | **The OCA layer is treated as `AGPL-3.0-or-later` by default**, and a module is treated as LGPL-3 only where its own manifest says so and that has been checked. `BE-007` `LX-21`'s per-dependency SPDX resolution supplies the check |
| **`LIC-09`** | **Every OCA module the programme modifies — including a version migration — is contributed upstream**, and the upstream pull request is the **evidence of compliance** recorded against this register. `BE-007` `REPO-11`'s upstream-PR field is the mechanism |
| **`LIC-10`** | **RFP §19.1(4)'s upstream-contribution obligation may not be traded, waived or deferred in contract negotiation.** `CO-003` `SOW-64` makes a breach a **material** breach, because the exposure created is 1000FiX's, not the supplier's |
| **`LIC-11`** | Where an OCA module is modified and **not** contributed upstream — for a genuinely 1000FiX-specific change with no upstream value — the source is published by another route, and the route is decided by the Chief Architect **before** the change is written |

> **Referred to `02-05`, `AR-013` §6 and `BE-007` §6.2 for correction**, and to `BE-007` §6.3 to
> extend its AGPL-3 test table to the module layer. This is a **register correction, not a design
> change**: the architecture is fine, the discharge mechanism already exists, and what was missing
> was the knowledge that it was a discharge.

### 6.4 `CVA-16` — Redis, and a licence class the policy file does not contain

**The recorded position.** `02-05` §4: *"**Redis | 7.x | BSD-3** | Cache, sessions, queues, locks |
W1"*.

**The verified position** *(2026-08-19, against Redis's own published licensing)*:

| Version | Licence |
|---|---|
| ≤ **7.2** | **`BSD-3-Clause`** — open source |
| **7.4 – 7.8** | **RSALv2 / `SSPL-1.0`**, dual — **source-available, not open source** |
| **8.0 +** *(May 2025)* | Tri-licence: **`AGPL-3.0-only`**, or RSALv2, or `SSPL-1.0` |
| Valkey | **`BSD-3-Clause`**, forked from Redis 7.2, under the Linux Foundation |

**"Redis 7.x" spans both regimes**, so the estate's entry is not merely stale — it is **unresolvable
as written**. Three consequences:

| # | Consequence |
|:--:|---|
| 1 | **The pinned version determines the licence, and no document states the pin.** `BE-007` `LX-21` requires every dependency to resolve to an SPDX identifier; *"7.x"* resolves to two different ones |
| 2 | **RSALv2 appears in no list in `BE-007` §6.1's policy file** — not `allow`, not `gated`, not `deny`. `SSPL-1.0` is gated and `AGPL-3.0` is gated, but a Redis 7.4–7.8 deployment electing RSALv2 has **no policy position at all**, and under `LX-21` would fail the build as `NOASSERTION` |
| 3 | **Redis is a Wave 1 foundation component** — cache, sessions, queues and distributed locks — and per `AR-009` it is also the **event bus until Redpanda arrives at Wave 6**. This is not a peripheral dependency |

**Is there an actual compliance problem?** Probably not, and saying so is as important as raising the
finding. SSPL's §13 obligation triggers on **offering the software itself as a service**; 1000FiX
uses Redis as internal infrastructure and does not offer Redis to anyone. RSALv2 similarly restricts
providing the software to third parties as a managed service. **On the ordinary reading, all three
licence options permit what the programme is doing.**

**But nobody has done that analysis, and there is a strictly better option available for free:**

| # | Rule |
|---|---|
| **`LIC-12`** | **The Redis position is resolved by pinning, and the pin is recorded here with its licence.** *"7.x"* is not a pin |
| **`LIC-13`** | **`Valkey` is added to `AR-013`'s radar as the named fallback** (`LW-01`). It is `BSD-3-Clause`, Linux Foundation-governed, and forked from the last BSD-licensed Redis — which makes it the **only option in the set that returns the component to the `allow` list with no gated approval at all** |
| **`LIC-14`** | **RSALv2 is added to `BE-007` §6.1's `gated` list** with an approval entry, or the pin moves to a version that does not need one. A licence class that is in no list is the `NOASSERTION` case `LX-21` was written to catch, arriving through the front door |
| **`LIC-15`** | **`LIC-Q-04`'s Wave 1 verification sweep covers every ▣ row**, because Redis and MinIO were both found by looking, and the base rate `BE-007` §7.3 states — *"a 36-month programme on a 24-system open-source stack should expect two to four such events"* — has now produced **three in one estate review** |

### 6.5 The other source-available positions

| Component | Licence | Field-of-use limit | Position | Owner |
|---|---|---|---|---|
| **Redpanda** | BSL 1.1 | Production use within limits; converts to `Apache-2.0` four years after each merge | **Compliant.** Reviewed at each wave gate; **Kafka registered as the fallback** and `AR-009` §6.2's shared consumer library makes the swap a configuration change | Chief Architect |
| **TimescaleDB** | `Apache-2.0` core; TSL advanced | Some features are commercially licensed | **Compliant, and CI-enforced**: Apache-2.0 features only. **The risk is silent**: a developer using a TSL feature converts a $0 component into a licensed one mid-programme, with no error message | Chief Architect |
| **n8n** | Sustainable Use | Internal business purposes only | §7.1 | **CFO with Chief Architect** |
| **Redis 7.4+** | RSALv2 / SSPL-1.0 | Not as a managed service to third parties | §6.4 | Chief Architect |

### 6.6 MinIO — a Wave 1 component with no upstream

`BE-007` §7.1 raised this as **`BEA-16`, Critical**. Independently re-verified 2026-08-19: MinIO's
community edition entered maintenance mode in December 2025 and its repository was **archived on 25
April 2026**. The server code remains AGPL-3 — it did not stop being open source — but there are no
further releases, no reviewed patches and no official community binaries.

**Three consequences this register adds to `BE-007`'s analysis:**

| # | Consequence |
|:--:|---|
| 1 | **An archived upstream makes the AGPL-3 obligation *more* likely to trigger, not less.** With no upstream to accept a fix, the only way to fix a bug or a CVE is to **patch locally** — and a local patch to an AGPL component is precisely the modification half of the §13 test. The licence risk and the security risk point the same way |
| 2 | **Garage, the closest maintained alternative, is also AGPL-3.** Swapping MinIO for Garage removes the maintenance risk and **keeps the licence obligation unchanged**. SeaweedFS (`Apache-2.0`) removes both, which is a point in its favour that a purely technical comparison would miss |
| 3 | **A managed object store was assessed and rejected** in TSS §7.4 on residency grounds, and `SC-007`'s split-residency design is why. **If the decision reopens it, the residency analysis must be redone, not assumed** — and it becomes a fifth L6 component under `AR-013` `L6-04`, requiring Design Authority and CFO approval and a five-year entry in `CO-005` (`TCO-15`) |

| # | Rule |
|---|---|
| **`LIC-16`** | **The MinIO replacement decision is `W0`, blocking Wave 1** (`BE-007` §7.1), and the **licence consequence of each option is stated in the decision record**, not discovered afterwards |
| **`LIC-17`** | **No object-storage option is selected without a residency assessment against `SC-007`.** Object storage holds evidence photographs, signed documents and Mushak invoices — `NFR-086`'s classified set |

### 6.7 Model weights are not covered by the runtime's licence

Ollama is `MIT`. **The models it serves are not.** Open-weight model licences vary widely — some are
permissive, several carry acceptable-use restrictions, and a few restrict commercial use above a user
threshold.

| # | Rule |
|---|---|
| **`LIC-18`** | **Every model weight deployed under `M26` is a row in this register**, with its own licence, its own acceptable-use restrictions, and its own owner. `AR-011` §9.4's Bengali evaluation gate selects the model; **this register records what selecting it obliges** |
| **`LIC-19`** | A model whose licence restricts commercial use, or restricts use above a user or revenue threshold, **may not be deployed without CFO approval** — the same gate as an L6 component, because it is the same kind of exposure |

> **This is a gap, not a violation.** No model has been selected yet (`AR-011` §9.4's gate is at
> Wave 5), so nothing is currently non-compliant. **The point of putting it in the register now is
> that the selection will be made on Bengali capability and latency, and the licence will be noticed
> afterwards** unless there is a row waiting for it.

---

## 7. The Obligations No Code Check Can See

`BE-007` §6.4 identified two. This section owns them, adds a third, and gives each a named owner and
a date — which is what ISO/IEC 5230 §3.2 requires and what `LX-27` and `LX-28` asked for.

### 7.1 n8n Sustainable Use — and the marketplace question

**The licence, verified 2026-08-19.** Use is permitted for *"internal business purposes"*, and the
test is whether you are selling a product or service **"in which the value derives entirely or
substantially from n8n functionality."** Explicitly prohibited: white-labelling n8n and offering it
to customers for money; hosting n8n and charging for access; building a competing automation
platform. Explicitly **permitted**: offering commercial consulting or support services, including
building n8n workflows for clients.

**Why this is a live question here and not a theoretical one.** 1000FiX operates a **marketplace
platform** (`M12`, `P07`) and a **managed services business** (`M05`), and sells to **brand partners**
(`P08`) and **corporate clients** (`P04`). Every one of those is a commercial surface, and n8n is the
workflow engine behind `M28`.

| Use | Position | Assessment |
|---|---|---|
| Internal orchestration between 1000FiX systems | ✅ **Permitted** | Squarely *"internal business purposes"* |
| Workflows that automate a **customer's** job on 1000FiX's behalf | ✅ **Permitted** | The value derives from the service, not from n8n. Comparable to the permitted consulting case |
| **Exposing n8n workflow authoring to marketplace sellers or brand partners as a product feature** | ❌ **Breach** | This is white-labelling. `BE-007` `LX-27` and `AR-013` `LW-04` both flag it |
| **Charging for access to an automation capability whose value is substantially n8n's** | ❌ **Breach** | The licence's own test |
| Building an automation product to sell | ❌ **Breach** | Explicitly prohibited |

| # | Rule |
|---|---|
| **`LIC-20`** | **n8n is internal-only, and the boundary is a product decision, reviewed by the CFO and the Chief Architect, not a code review.** `AR-005` §5.17 states the boundary and `AR-002` records the portal surfaces it applies to |
| **`LIC-21`** | **Any proposal to expose an L4 component's own interface to an external party goes to the Chief Architect *and* the CFO** (`BE-007` `LX-27`), and the decision is recorded **in this register**, which is the place `LX-27` did not have |
| **`LIC-22`** | The n8n boundary is **re-checked at every wave gate that adds a portal or an external surface** — Waves 6, 7 and 8 add `P07`, `P08` and `P12`. `LW-04` |

> **The honest summary for the CFO: today's use is compliant and there is no reason to change
> anything.** The risk is entirely prospective, it arrives as a *product* idea rather than an
> engineering one, and the person who would propose it — a product manager designing seller
> self-service in Wave 7 — will have no reason to know that a licence is involved. **That is what
> `LIC-21` is for.**

### 7.2 `BEA-15` — Wazuh, GPL-2, and what "distribution" means for a managed service

`BE-007` §6.4 raised this and called it *"a real exposure"*. It is owned here.

| Element | Position |
|---|---|
| **The component** | Wazuh, `GPL-2.0-only`, endpoint monitoring under `M05` |
| **The estate's recorded position** | TSS §7.3: *"deployed, not distributed"* |
| **The operational reality** | `M05` Remote Support & Managed Services runs monitoring on **client** estates. **Installing an agent on a customer's Windows or macOS endpoint is, on the ordinary reading, distribution** |
| **What GPL-2 requires if it is distribution** | Not prohibition — GPL-2 permits distribution. It requires **source availability to the recipient**, which for an unmodified upstream binary is discharged by pointing to the upstream source and including the licence text |
| **Why it still matters** | It changes **what `M05` must ship alongside the agent**, and it is a **contractual** matter with MSP clients, whose own procurement may ask what open-source software is being installed on their estate and under what terms |
| **Owner** | **Legal Counsel**, with the Corporate Services Head |
| **Needed by** | **Before the first `M05` client agent deployment — Wave 5** |

| # | Rule |
|---|---|
| **`LIC-23`** | **The `M05` agent-deployment design states explicitly whether Wazuh is distributed to client endpoints**, and if it is, the GPL-2 source-availability obligation is discharged in the agent package and in the MSP service description (`BE-007` `LX-28`) |
| **`LIC-24`** | **The same test is applied to every component that reaches a client endpoint**, not only Wazuh: osquery (`Apache-2.0` — attribution only), the RustDesk client (`AGPL-3` — §6.1's test applies at the client), and any commercial RMM agent under `D-18`. **Three components reach client estates and only one has been assessed** |

### 7.3 The upstream-contribution obligation

Added here because it is an obligation the estate treats as a virtue.

| Element | Position |
|---|---|
| **The requirement** | RFP §19.1(4): the respondent *"must contribute OCA migrations upstream"* |
| **What it looks like** | Community citizenship — and it is that |
| **What it also is** | **The discharge mechanism for the AGPL-3 obligation on every modified OCA module** — §6.3 |
| **Owner** | Chief Architect, with Legal Counsel |
| **Evidence** | The upstream pull request, recorded against this register per `LIC-09` |

> **`LIC-25` — an obligation that is also a virtue is still an obligation, and must be tracked as
> one.** Virtues get deprioritised under schedule pressure in Wave 6. Obligations do not.

---

## 8. Registers B and C — Commercial and Contractual

### 8.1 Register B — commercial entitlements (L6)

Four components, per `02-05` §6 and `AR-013` §7. Modelled as **entitlements** per ISO/IEC
19770-3:2016: a right, a metric, a limitation and a term.

| # | Component | Right | **Metric** | **5× volume cap (`L6-02`)** | Term / renewal | **Exit (`L6-05`)** | Approval (`L6-01`) | Owner |
|:--:|---|---|---|---|---|---|---|---|
| 1 | **Cloud telephony / CPaaS** | Inbound IVR, routing, recording on hotline 16743 | Per minute **+ seats** | **Modelled at 5× contact-centre seats and 5× minutes before signature** | Annual | **Number portability** — the hotline number must be portable, and that is a contract term, not a hope | **CFO, individually** | Customer Service Manager |
| 2 | **Qualified e-signature** | Legally binding signatures on AMC, MSP, rental and **seller** agreements | Per envelope | **5× envelope volume**, driven by marketplace seller growth | Annual | **The hard one.** *"What happens to the signed envelopes if we change provider?"* Evidentiary records with a multi-year life. **Must be answered before signing** | **CFO, individually** | Legal Counsel |
| 3 | **Identity verification / KYC** | Marketplace seller and high-value customer verification | **Per check, $0.30–$0.80** | **5× seller onboarding volume** — a business-plan variable, not a technical one | Annual | Verification **results** must be exportable and retained by 1000FiX, not by the provider | **CFO, individually** | CDO |
| 4 | **Endpoint RMM agent** | Patch management on client Windows/macOS estates | **Per endpoint, $2–$5/month** | **5× endpoint count. `AR-013` `L6-02`: *"the one that scales dangerously"*** | **`D-18` — decision at the W5 pilot** | Agent removal from client estates; **and see `LIC-24`** — a commercial agent on a client endpoint raises the same distribution question as Wazuh | **CFO + Design Authority** | CTO |

| # | Rule |
|---|---|
| **`LIC-26`** | **Every L6 component requires individual CFO approval, recorded in this register with a date** (`L6-01`). An approval that is not in the register did not happen |
| **`LIC-27`** | **Every per-unit metric is modelled at 5× projected volume before signature** (`L6-02`), and **the modelled figure, not the projected one, enters `CO-005`'s high case** (`TCO-13`) |
| **`LIC-28`** | **A fifth L6 component requires Design Authority and CFO approval** (`L6-04`). The bounded set of four is the position, not an accident of counting. **`CO-005` §5.5 and §6.6 both identify a likely fifth** — a managed object store, if the MinIO decision goes that way |
| **`LIC-29`** | **No L6 contract is signed without a documented exit** (`L6-05`), and the e-signature exit is answered **in writing by the provider**, not inferred from its documentation |
| **`LIC-30`** | Every L6 entitlement is reviewed at each wave gate for **consumption against cap**, and a component tracking above 50% of its 5× cap is escalated to the CFO |

### 8.2 Register C, inbound — what the supplier licenses to 1000FiX

| # | Item | Provision | Rule |
|:--:|---|---|---|
| 1 | **Everything created for 1000FiX** — customisations, configurations, custom modules, services, applications, migrations, test suites, documentation, training material | **Owned by 1000FiX** (RFP §19.1(3)) | `CO-003` `SOW-60` |
| 2 | **Pre-existing proprietary frameworks** | Remain the supplier's; **must be declared in the Exceptions schedule**; licensed **perpetually, irrevocably and royalty-free** | `CO-003` `SOW-61` |
| 3 | **Source-code escrow** for any proprietary component | RFP §19.2 | `CO-003` `SOW-63` — **verified annually, not merely lodged** |
| 4 | **The supplier's own open-source introductions** | Enter **this register**, via a CycloneDX SBOM per artefact | `CO-003` `SOW-34` |
| 5 | **Gated components introduced by the supplier** | Require architecture approval; **an AGPL component may not be modified at all** without a Chief Architect approval and a published-source plan | `CO-003` `SOW-64` |

| # | Rule |
|---|---|
| **`LIC-31`** | **The Exceptions schedule is a row in this register**, one per declared framework, with its licence terms, its exit and its owner. A framework declared in a contract schedule and recorded nowhere else is invisible at the moment it matters — which is when the supplier leaves |
| **`LIC-32`** | **A royalty-free perpetual licence is worth defending in negotiation for a reason beyond the obvious**: royalty payments to a non-resident attract **20%** Bangladesh withholding (`CO-005` §6.2), against 10% on services. **A royalty-bearing licence is more expensive than its price** |

### 8.3 `CVA-17` — Register C, outbound: what 1000FiX licenses to *its* customers

**No document in the estate states this position**, and 1000FiX is about to grant software access to
five distinct external populations.

| Population | Surface | What licence terms do they get? | Assessed? |
|---|---|---|:--:|
| Retail customers | `P01` | Terms of service | ❌ |
| **Corporate clients** | `P04` | A commercial agreement — and their procurement **will** ask about open-source components | ❌ |
| **Marketplace sellers** | `P07` | A seller agreement | ❌ |
| **Brand partners** | `P08` | A partner agreement — several are large multinationals with their own supply-chain requirements | ❌ |
| **MSP clients** | `M05`, agents on their estates | A managed-services agreement — **plus §7.2's GPL-2 question** | ❌ |

**Three things the outbound position must state:**

| # | Requirement |
|:--:|---|
| 1 | **What 1000FiX warrants** about the open-source components underneath. The safe and standard position is a **disclaimer of implied warranties on third-party open-source components**, coupled with the Company's own service warranty. Silence is not neutral — silence defaults to whatever the general terms say |
| 2 | **What 1000FiX must supply on request.** A corporate client or brand partner asking for an SBOM should receive the **SPDX 3.0.1 export `BE-007` §8.2 already produces** — this is a solved problem that nobody has connected to the customer-facing question |
| 3 | **The AGPL-3 recipient right.** §6.3's users of a modified OCA module served over a network are **entitled to the corresponding source**. `LIC-09`'s upstream contribution discharges it — but the outbound terms should say where to find it, rather than leaving a user to ask and receive no answer |

| # | Rule |
|---|---|
| **`LIC-33`** | **Legal Counsel drafts the outbound open-source position** — warranty, SBOM-on-request, and the AGPL-3 source pointer — as a schedule usable across all five agreement types. **Needed by Wave 4**, when `P04` and `P07` bring the first external commercial users |
| **`LIC-34`** | **The SPDX export is offered proactively to brand partners and corporate clients**, not supplied reluctantly on request. `BE-007` §8.3 already produces both formats for exactly this audience; **it is a differentiator that currently costs nothing and is not being used** |

---

## 9. Governance

### 9.1 `CVA-18` — one cadence, not two

| Document | Cadence | Status |
|---|---|---|
| `02-05` §4 | *"reviewed **annually**"* | **Superseded, but still the text of record** in the primary architecture document |
| `AR-013` `LW-03` | *"re-verified at **every wave gate**, not annually. `02-05` §4's 'reviewed annually' is too slow for a 36-month programme with nine gates"* | **Current** |
| `BE-007` `LX-30` | *"checked at **every wave gate**, and the check is evidenced in the `GV-009` gate pack"* | **Current** |

> **`LIC-35` — the cadence is the wave gate. Nine reviews in 36 months, not three.** `02-05` §4 is
> referred for correction under `RG-08`. The reason `LW-03` gives is validated by this document's own
> findings: **an annual review would have found MinIO's archival somewhere between four and sixteen
> months late, and would very likely not have found the Redis or OCA positions at all**, because
> neither was announced — both were simply true, in documents the estate had never re-read.

### 9.2 Ownership

| # | Rule |
|---|---|
| **`LIC-36`** | **Every obligation has one named owner role**, recorded in §5.2, §8.1 and §7. ISO/IEC 5230 §3.2 |
| **`LIC-37`** | **The Chief Architect is the technical custodian; the CFO is the accountable owner.** The split matters: the technical custodian knows what changed, and the accountable owner is the one who signs a commercial commitment or accepts a legal exposure |
| **`LIC-38`** | **Legal Counsel owns the three obligations that are legal questions, not engineering ones**: Wazuh distribution (§7.2), the e-signature exit (§8.1), and the outbound position (§8.3) |
| **`LIC-39`** | **An obligation whose owner leaves the Company is reassigned at the next wave gate at the latest.** An unowned obligation is the state this register was created to end |

### 9.3 The attestation record

| # | Rule |
|---|---|
| **`LIC-40`** | At **every wave gate**, the Chief Architect attests: every component in §5.2 has been checked against its upstream licence page; every ⚠ and every gated row has been re-verified; every new component has an entry; and every `verified_on` date in the gate's scope is current |
| **`LIC-41`** | The attestation is **evidence class `E4`** in the `GV-009` gate pack (`LX-30`), and a gate cannot pass without it |
| **`LIC-42`** | **An upstream licence change, archival or end-of-life announcement is a Critical `GV-005` risk within 5 working days of publication, and a `GV-003` decision within 20** (`BE-007` `LX-31`). This register is where it is recorded first |
| **`LIC-43`** | The attestation records **what was not checked**, as well as what was. `LIC-02`'s ▣ marks are carried into the gate pack, so a reader can see the register's own coverage |

### 9.4 Reconciliation with the SBOM

| # | Rule |
|---|---|
| **`LIC-44`** | At every wave gate, the CycloneDX SBOM (`BE-007` §8) is reconciled to this register: **every gated licence in the SBOM has a row here, and every row here appears in the SBOM.** A divergence in either direction is a finding |
| **`LIC-45`** | **A transitive dependency carrying a gated licence is escalated to a Register A row.** The distinction between "we deploy it" and "something we deploy depends on it" is invisible to AGPL-3 §13 |

### 9.5 Escalation

| Trigger | Route | Timebox |
|---|---|---|
| Upstream licence change or archival | `GV-005` Critical risk → `GV-003` decision | 5 / 20 working days (`LIC-42`) |
| A proposal to modify an AGPL component | Chief Architect **+ CFO notification**, with a published-source plan, **before the change is written** | Before the change |
| A proposal to expose an L4 component externally | Chief Architect **+ CFO** (`LIC-21`) | Before the product decision is committed |
| A fifth L6 component | **Design Authority + CFO** (`LIC-28`), plus a five-year `CO-005` entry (`TCO-15`) | Before signature |
| An L6 component above 50% of its 5× cap | CFO (`LIC-30`) | At the wave gate |
| A supplier introducing a gated component without approval | **Material breach** under `CO-003` `SOW-64` | Immediately |

---

## 10. The Contractual Hooks

This register is only as good as the contract that binds the supplier to it. `CO-003` §13 carries
the clauses; they are listed here so the register's owner can see what enforcement exists.

| `CO-003` rule | Provision | What it protects here |
|---|---|---|
| **`SOW-34`** | The supplier's RFP §19.1(4) obligation is discharged **into this register**: a CycloneDX 1.7 SBOM per artefact, an SPDX 3.0.1 export on request, and a row here for every gated licence introduced | §9.4's reconciliation is possible |
| **`SOW-64`** | The supplier **may not introduce** an AGPL, BSL, TSL or fair-code component without architecture approval, and **may not modify an AGPL component at all** without approval and a published-source plan. Breach is **material** | §6's positions cannot be silently invalidated |
| **`SOW-61`** | The Exceptions schedule is scrutinised **at Stage 6**, not at contract | `LIC-31`'s inbound rows exist before the Company is committed |
| **`SOW-63`** | Escrow is **verified annually**, as a condition of retention release | §8.2 item 3 is real |
| **`LIC-10` → `SOW-64`** | The upstream-contribution obligation **may not be traded** | §6.3's AGPL discharge survives negotiation |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `LIC-Q-01` | **What replaces MinIO**, and what is the licence and residency consequence of each option? | Chief Architect | **W0 — blocking Wave 1** | §6.6; `CO-005` §5.5; `CO-006`; `BEA-16` |
| `LIC-Q-02` | **What Redis version is pinned**, and does the position move to Valkey? | Chief Architect | **W1** | §6.4; `BE-007` §6.1's policy file; `AR-009`'s event bus to Wave 6 |
| `LIC-Q-03` | **Is installing a Wazuh agent on a client endpoint distribution under GPL-2**, and if so what must `M05` ship with it? | **Legal Counsel** | **Before Wave 5** | §7.2; `BEA-15`; the `M05` service description |
| `LIC-Q-04` | When is the **verification sweep** of the thirty ▣ rows performed? | Chief Architect | **Wave 1 gate** | §5.2; `LIC-40`'s attestation is not complete without it |
| `LIC-Q-05` | Should 1000FiX seek **ISO/IEC 5230 conformance**, given that corporate clients and brand partners increasingly ask for it? | CFO with Chief Architect | W4 | §2.1; a commercial-differentiation decision, not a compliance one |
| `LIC-Q-06` | **What are the outbound open-source terms** for the five external populations? | **Legal Counsel** | **Wave 4** | §8.3; `CVA-17`; `P04` and `P07` go live in Waves 4 and 7 |
| `LIC-Q-07` | **What happens to signed e-signature envelopes** if the provider changes? | Legal Counsel with CFO | **Before signing** | §8.1 row 2; `L6-05` |
| `LIC-Q-08` | Which **model weights** will `M26` deploy, and under what licences? | Chief Architect | **W5**, at `AR-011` §9.4's gate | §6.7; `LIC-18`, `LIC-19` |
| `LIC-Q-09` | Will `02-05` §4, `AR-013` §6 and `BE-007` §6.2 be **corrected** on the OCA position? | Chief Architect | **W1** | `CVA-15`; `RG-08` |

> All nine are escalated to `GV-005` RAID at issue. `LIC-Q-01` and `LIC-Q-02` are `W0`/`W1` and
> block Wave 1 components; `LIC-Q-03` and `LIC-Q-06` are legal questions with long lead times and
> should be commissioned now rather than when they bind.

---

## 12. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CO-004-D-01` | Whether a third licence document is justified alongside `BE-007` and `AR-013` | Extend `BE-007` · Extend `AR-013` · **A separate register of record** | **Separate register** | A CI check proves no AGPL component entered the build; it cannot prove a **person** is accountable, that the obligation was **re-verified**, or that a **usage decision** was taken. `LX-27` and `LX-28` both point at a decision record that did not exist | §1's three-way boundary; §3's three registers |
| `CO-004-D-02` | Whether to independently verify licences or carry the estate's positions | Carry them — three documents already agree · **Verify the highest-consequence rows** | **Verify** | `PG-03`: *"count, do not consult."* Three documents agreeing is not three verifications; it is one unverified position copied twice | **Four rows found to differ**, two of them on Wave 1 components: `CVA-15`, `CVA-16` |
| `CO-004-D-03` | How to treat rows not verified this session | Mark everything verified · Omit them · **Mark them ▣ carried and schedule the sweep** | **Mark and schedule** | A register whose verification status is uniform is either exhaustive or dishonest, and this one is not exhaustive | Thirty ▣ rows; `LIC-Q-04`; `LIC-43` carries the coverage into the gate pack |
| `CO-004-D-04` | How to treat the OCA licence correction | Raise it as a defect against `02-05` and stop · **Restate the position and name the existing discharge** | **Restate and name the discharge** | The mitigation already exists in RFP §19.1(4). The failure was not architectural; it was that nobody knew the contribution obligation was discharging a legal one | `LIC-08`…`LIC-11`; `SOW-64` makes it non-negotiable |
| `CO-004-D-05` | Whether to recommend Valkey over Redis | Leave the pin to engineering · **Register Valkey as the named fallback** | **Register it** | Valkey is the only option in the set that returns the component to the `allow` list with **no gated approval at all**, and `LW-01` requires a named fallback regardless | `LIC-13`; referred to `AR-013` for the radar |
| `CO-004-D-06` | Whether to include model weights | Out of scope — no model selected · **In scope, as a waiting row** | **In scope** | The selection will be made on Bengali capability and latency at the Wave 5 gate, and the licence will be noticed afterwards unless a row is waiting for it | `LIC-18`, `LIC-19`; `LIC-Q-08` |
| `CO-004-D-07` | Whether to state an outbound licence position | Out of scope — this is a compliance register · **In scope** | **In scope** | 1000FiX is about to grant software access to five external populations and has no position at all. The AGPL-3 recipient right in §6.3 is **owed to those users** | `CVA-17`; `LIC-33`, `LIC-34`; `LIC-Q-06` |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | **Every deployed component** has a row with an SPDX identifier (or an explicit note that none exists), an obligation class, a **named owner**, a fallback and a verification mark | §5.2 — 35 rows, count verified |
| `AC-02` | The **boundary against `BE-007` and `AR-013`** is stated before any content, so three documents do not diverge | §1, §1.2 |
| `AC-03` | The **AGPL-3 test** is applied per component, **including the module layer** the estate's existing test omits | §6.1, §6.3 |
| `AC-04` | Every **source-available and fair-code** position is stated with its field-of-use limit and an assessment against actual use | §6.4, §6.5, §7.1 |
| `AC-05` | The **three obligations no code check can see** have named owners and dates | §7 |
| `AC-06` | The **four L6 entitlements** carry a metric, a **5× cap**, a term, an **exit** and a CFO approval record | §8.1 |
| `AC-07` | **Inbound and outbound** contractual licence positions are stated | §8.2, §8.3 |
| `AC-08` | The **review cadence is one cadence**, and the superseded one is referred for correction | §9.1; `LIC-35` |
| `AC-09` | An **attestation** exists, is evidence class `E4`, and gates the wave | §9.3; `LIC-40`, `LIC-41` |
| `AC-10` | The register is **reconciled to the SBOM** in both directions | §9.4; `LIC-44`, `LIC-45` |
| `AC-11` | Every finding raised — `CVA-15` through `CVA-18` — has a dated, owned action | §6.3, §6.4, §8.3, §9.1; §11 |
| `AC-12` | Rows **not** verified this session are marked as such, and their verification is scheduled | §5.1's convention; `LIC-Q-04` |
| `AC-13` | The local rule prefix `LIC-nn` was **verified to zero occurrences** workspace-wide before allocation | Header note |

**Definition of done.** This document is complete when every criterion above is met, `LIC-Q-01`,
`LIC-Q-02` and `LIC-Q-04` are closed, Legal Counsel has signed §7 and §8, and `PGD-000` records
`CO-004` as ✅ with a fresh enumeration date. **It is never "finished"** — `LIC-35` makes it a
standing register reviewed nine times.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-05` §4, §6 | The stack and the L6 set. **Referred for correction on `CVA-15`, `CVA-16` and `CVA-18`** |
| Upstream | `AR-013` §6, §7 | The radar, `LW-01`…`LW-05`, `L6-01`…`L6-05`. **Referred for the Valkey and OCA corrections** |
| Upstream | `BE-007` §6, §7 | The machine check and `LX-21`…`LX-32`. **Referred to add RSALv2 to the policy file and to extend the §6.3 AGPL test to the module layer** |
| Upstream | `PE-008` §3.4 | `PE-008-F-01`'s fallbacks for Grafana, Loki and Tempo, carried into §5.2 |
| Downstream | `CO-005` §5.5 | The L6 cost restatement and the fifth-component exposure use §8.1's caps |
| Downstream | `CO-006` | Acquires what §8.1 registers; `LIC-26`'s approval record is `CO-006`'s gate |
| Downstream | `CO-003` §13 | `SOW-34`, `SOW-61`, `SOW-63`, `SOW-64` are the enforcement |
| Downstream | `GV-009` | `LIC-41` makes the attestation an `E4` gate artefact |
| Lateral | `SC-007` | `LIC-17` — no object-storage option without a residency assessment |
| Lateral | `AR-011` §9.4 | The model-selection gate that populates §6.7's rows |
| Lateral | `AR-005` §5.17, `AR-002` | The n8n boundary and the portal surfaces it applies to |
| Lateral | `GV-003`, `GV-005` | `LIC-42`'s 5-day / 20-day escalation; nine open questions |

---

## 15. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./CO-002_Vendor_Evaluation_and_Selection_Report.md` ·
`./CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md` ·
`./CO-005_Total_Cost_of_Ownership_Model.md` · `./CO-006_Procurement_and_Purchase_Plan.md` ·
`../02_Architecture_and_Design/AR-005_Module_Boundary_and_Overlap_Rules_Register.md` ·
`../02_Architecture_and_Design/AR-009_Event_Driven_Architecture_and_Messaging_Design.md` ·
`../02_Architecture_and_Design/AR-011_AI_ML_Architecture_and_Model_Specification.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-008_Observability_and_Monitoring_Design.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` — §2, §3, §4, §6 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` — §7.1, §7.3, §7.4 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` — §5.4, §19.1

**External standards and sources** *(all verified 2026-08-19)*

| Source | Used for |
|---|---|
| **ISO/IEC 5230:2020**, *Information technology — OpenChain Specification* (from Linux Foundation OpenChain Specification 2.1) — §3.1, §3.2, §3.3, §3.5, §3.6 | §2.1's partial-conformance claim; `LIC-01`, `LIC-36`; `LIC-Q-05` |
| **ISO/IEC 18974:2023**, OpenChain security assurance | Named for the boundary; **not claimed** |
| **SPDX 3.0.1** licence identifiers | §5.2's identifier column |
| **CycloneDX 1.7** (ECMA-424, 2nd edition) | §9.4's SBOM reconciliation; produced by `BE-007` §8 |
| **ISO/IEC 19770-1:2017** (Edition 3, reviewed and confirmed 2024); **ISO/IEC 19770-3:2016** entitlement schema | §8.1's entitlement modelling |
| **Odoo 19.0 licensing documentation** — Odoo Community Edition is **LGPL-3**; the licence has been the same for every version since Odoo 9 | §5.2 row 1; `CVA-15` |
| **OCA published licensing position** and the OCA–Odoo licence agreement — **OCA modules are predominantly AGPLv3**; LGPL-3 and AGPL-3 are compatible and coexist; AGPL is retained *"to protect users of OCA addons from being locked in by service providers"* | §5.2 row 2; **`CVA-15`**; `LIC-08`…`LIC-11` |
| **Redis published licence pages and release history** — `BSD-3-Clause` to **7.2**; **RSALv2 / SSPLv1 for 7.4–7.8**; **tri-licence adding AGPLv3 from 8.0** (May 2025); **Valkey** forked from 7.2 under `BSD-3-Clause`, Linux Foundation | §5.2 row 5; **`CVA-16`**; `LIC-12`…`LIC-14` |
| **MinIO** — maintenance mode December 2025; **repository archived 25 April 2026**; server code remains AGPL-3. **Garage** (`AGPL-3.0`, Rust, S3-compatible, release 16 April 2026); **SeaweedFS** (`Apache-2.0`) | §5.2 row 10; §6.6; corroborates `BEA-16` |
| **n8n Sustainable Use Licence** — *"internal business purposes"*; the test is whether value derives *"entirely or substantially"* from n8n functionality; consulting and building client workflows are **permitted**; white-labelling, hosting-for-fee and building a competing automation platform are **not** | §5.2 row 8; §7.1; `LIC-20`…`LIC-22` |

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Chief Financial Officer with the Chief Architect and Enterprise Architecture | Initial issue. Establishes three registers, 35 component rows across six obligation classes, four L6 entitlements with 5× caps and exits, and inbound and outbound contractual positions. **Independently verified five licence positions and found three to differ from the estate's record**: `CVA-15` (OCA is AGPL-3, not LGPL-3 — High), `CVA-16` (Redis 7.x spans two regimes; RSALv2 is in no policy list — High), `CVA-17` (no outbound position), `CVA-18` (two review cadences). Owns `BEA-15` and closes `L6-05` | ERP Steering Committee, with Legal Counsel on §7 and §8 |

---

*`CO-004` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
