---
id: AR-013
title: Technology Radar & Build-vs-Buy Register
category: 02 — Architecture & Design
code: AR
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Architect
approver: Chief Technology Officer
standards_basis: Technology Radar practice (ThoughtWorks) · ISO/IEC 25010:2023 · ISO/IEC 5230 (OpenChain) for licence governance
traces_to: >
  PGD-000 AR-013 · 02-05 §7 (20 build-vs-buy decisions, frozen 2026-08-12) ·
  Technology Stack Specification §7, §9, §23, §25.2 · AR-004 ADR-027 · risks TR-05…TR-10, TR-15
depends_on: AR-001 · AR-004 · CO-004 (licence register)
verified_on: 2026-08-18
priority: P2
needed_by: W2
enumeration_timestamp: 2026-08-18 02:05 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# AR-013 — Technology Radar & Build-vs-Buy Register

### Category 02 · Code `AR` · Technology Radar practice · ISO/IEC 5230 licence governance

---

## 1. Purpose

`02-05` §7 holds **20 build-versus-buy decisions frozen at 2026-08-12**. Four are explicitly
conditional — the L6 RMM agent is *"deferred to Wave 5"* — and none has a review date, a review
owner, or a trigger that would cause it to be revisited. A frozen register on a **36-month programme
crossing at least one Odoo major version** will be wrong long before the programme ends, and nothing
will notice.

This document converts that register into a **live radar**: every technology assigned a ring, a
review date, a named owner and an **exit criterion** — the condition under which it moves ring.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The four-ring radar model and the ring-assignment rule |
| 2 | The complete technology register — 60+ components across L1–L6, each with ring, owner and review date |
| 3 | **Version currency** — the five findings verified 2026-08-13, restated with 2026-08-18 verification |
| 4 | The build-vs-buy register, restated with revisit triggers |
| 5 | **Licence-currency watch** — AGPL, BSL, TSL, fair-code, and the named fallback for each |
| 6 | The L6 commercial component register, its cost envelope and its approval gate |
| 7 | The adoption procedure — how a new technology enters the estate |
| 8 | The review cadence and what happens when a review is missed |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Why a technology was chosen | `AR-004` ADR library | The radar tracks *state*; the ADR holds *rationale* |
| Component-level licence obligation register | `CO-004` | This document watches for **change**; `CO-004` holds the obligations |
| Infrastructure sizing and cost | `PE-006`, `CO-005` | |
| Procurement process for L6 | `CO-006` | This document sets the gate; `CO-006` executes |
| Vulnerability response | `SC-009` | |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| CTO | §4 version currency and §7 L6 envelope are the two that reach the Board |
| Chief Architect | §8 adoption gate — how the estate acquires a 25th open-source system |
| Solution Architect | §6 licence watch; §5 build-vs-buy triggers |
| CFO | §7 — four L6 components, individually approved, $0–36K over three years |
| Implementation vendor | The stack they must build on and the currency obligations they inherit |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure |
|---|---|---|
| **Technology Radar practice** (ThoughtWorks) | Four rings — Adopt, Trial, Assess, Hold — with movement over time | **Departure:** rings carry a **named owner, a review date and an exit criterion**. A public radar is a point of view; a programme radar must be a control |
| **ISO/IEC 5230 (OpenChain)** | §6 licence-change watch; every fair-code component has a named fallback | Full OpenChain conformance is not sought; `CO-004` holds the obligation register |
| ISO/IEC 25010:2023 | Assessment criteria in §8.2 map to quality characteristics | |

### 2.2 Source material

| Source | Contribution |
|---|---|
| `../../primary-doc/…Technology_Stack_Specification.md` §4–§9 | The complete layer-by-layer stack; TC-xxx component identifiers |
| Ibid. §23 | 18 technology risks, several of which are radar triggers |
| Ibid. **§25.2** | **Five version-currency findings, verified 2026-08-13** — the most valuable single input |
| Ibid. §17.4 | Operational currency standards, including Keycloak's no-LTS position |
| `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` §4, §6, §7 | Licence obligations; the L6 register; 20 build-vs-buy decisions |
| `AR-004` ADR-001, ADR-026, ADR-027, ADR-029 | Rationale for the load-bearing selections |

### 2.3 Audit findings addressed

| Finding | How |
|---|---|
| `PGD-000` `AR-013` — *"`02-05` §7 holds 20 decisions frozen at 2026-08-12; four are conditional with no review mechanism"* | §5 restates all 20 with triggers, owners and review dates |
| **`M-01`** Stale vendor-version citation (Odoo release date) | §4 — every version claim carries a verification date; §9 makes verification a scheduled act |
| `TR-09` Upstream licence change on a fair-code component | §6 — watch list with named fallbacks |
| `TR-15` L6 cost scaling beyond the $36K envelope | §7 — per-unit modelling at 5× before signing |

---

## 3. The Radar Model

### 3.1 Four rings

| Ring | Meaning | Obligation |
|---|---|---|
| **ADOPT** | Default choice. Use without further approval | Kept current per §9; a change of ring requires an ADR |
| **TRIAL** | Approved for use in a **bounded context** with a named owner and a decision date | Must move to Adopt or Hold by its decision date. **It may not stay in Trial** |
| **ASSESS** | Being evaluated. **Not in production** | An assessment with no owner and no date is removed from the radar |
| **HOLD** | Not to be used in new work. Existing use has a **migration plan or an accepted-risk record** | Existing use is reported at every wave gate |

### 3.2 Ring assignment rule

> A technology is **ADOPT** only if all four are true: it is in production somewhere in the estate or
> is the declared W1 choice; it has a named owner; it has a currency policy (§9); **and its licence
> has no unresolved change risk (§6)**.

Anything else is Trial, Assess or Hold. This is what prevents a component drifting into Adopt by
being used rather than by being chosen.

---

## 4. Version Currency

**Five findings were raised in the Technology Stack Specification §25.2, verified 2026-08-13.
Re-verified 2026-08-18.** None invalidates the architecture; all five require a decision, and **three
remain open**.

| # | Component | Specified | Position (**re-verified 2026-08-19**) | Finding | Decision |
|---|---|---|---|---|---|
| **VC-01** | **Odoo** | 19.0 | 19.0 released **18 September 2025**, supported to approximately **September 2028**. **Odoo 20 is released at Odoo Experience, Brussels, 24–26 September 2026** — confirmed 2026-08-19, **five weeks from this issue** | A 36-month programme reaches steady state within about a year of 19.0 leaving support | **`D-025` — OPEN.** ADR-027 proposes one upgrade slot between W5 and W6 |
| **VC-02** | **Next.js** | 15 | **16.3 is current** (released 3 August 2026), with React 19.2. **Next.js 15 is in Maintenance LTS and reaches end of life on 21 October 2026** — confirmed 2026-08-19 | **Six customer-facing applications would be built on a version leaving support during the programme.** `CON-03` constrains the platform, not the version | **`D-026` — OPEN.** Treat 15→16 as a **Wave 1 platform activity**, before six applications exist. Confirm Payload CMS 3 compatibility (`A-05`) |
| **VC-03** | **PostgreSQL** | 16 | 16 supported to **November 2029**; 18 to November 2030 | **Valid and safe.** Margin at steady state is roughly one year | **Retain 16 for W1** — it is Odoo 19's tested pairing. **Review the move at the same gate as the Odoo slot**, so both major upgrades happen once, together |
| **VC-04** | **Keycloak** | 26.x | **No LTS line exists. Only the newest version receives active development and security fixes** | Pinning Keycloak for the life of a wave leaves **authentication on an unpatched release** | **Settled — operational standard, not a version change.** Kept current continuously (§9); HA cluster makes rolling upgrade non-disruptive (`TR-08`) |
| **VC-05** | **Flutter / React Native** | Flutter ×4; P07 mobile unresolved | Flutter current. **React Native's legacy architecture has been removed** (0.83+); New Architecture mandatory | The estate must not acquire a **second mobile framework by default** through P07 | **`D-027` — OPEN.** Confirm Flutter as the single framework; deliver P07's mobile surface as a PWA in W7 |

> **VC-02 is the most time-sensitive, and the date is now known.** The cost of the 15→16 upgrade
> rises with each of the six Next.js applications built on 15. In Wave 1 it is a platform activity;
> after Wave 7 it is a six-application coordinated migration. `D-026` is a Wave 0 decision that
> becomes materially more expensive every wave it is deferred.
>
> **`AR-013-F-01` (HIGH, raised 2026-08-19).** The source specification said 15 was *"leaving the
> supported line during the programme"*. **It leaves it on 21 October 2026 — inside Wave 1
> (months 1–4).** On the `GV-004` §5.2 calendar the programme would be building `P01`, `P03`, `P04`,
> `P06`, `P10` and `P12` on a framework that is out of support before Wave 1 closes.
> **`D-026` is no longer a planning preference; it is a Wave 0 blocker**, and this document
> upgrades it accordingly. `project-guide-doc` still specifies Next.js **15** in twenty places,
> `primary-doc` in fifty-one and `1000fix_ERP_Module` in thirty-eight — none of which can be
> corrected until `D-026` is taken.
>
> **`AR-013-F-02` (MEDIUM, raised 2026-08-19).** `VC-01`'s *"expected September–October 2026"* is
> now a fixed date: **Odoo 20 ships 24–26 September 2026**. `D-025` is a Wave 0 decision with five
> weeks of notice, and `ADR-027` (the upgrade slot) remains **Proposed**.

---

## 5. Build-vs-Buy Register

All 20 decisions from `02-05` §7, restated with the three fields the original lacked: **owner**,
**review date** and **revisit trigger**.

| # | Capability | Decision | Owner | Review | **Revisit if** |
|---|---|---|---|:--:|---|
| 1 | ERP core | **Build on Odoo CE** | CTO | W5 gate | Odoo 20/21 breaks the OCA extension model (`A-08`); CE licensing changes |
| 2 | Field service management | **OCA + custom** | Solution Architect | **W0 — `W0-01`** | OCA `field-service` v19 migration exceeds 20 PW (`A-03`) — reclassifies to L5 |
| 3 | Technician mobile app | **Build (Flutter)** | CTO | W6 | A product emerges meeting 24 h offline + Bengali + deep ERP integration |
| 4 | Dispatch optimisation | **Build on VROOM/OSRM** | Solution Architect | W6 | Routing quality fails the W6 gate (≥ 50% auto-assign, ≥ 88% agreement) |
| 5 | Marketplace platform | **Build** | CCO | W7 | — settlement must live in the ledger; effectively permanent |
| 6 | Managed services PSA | **Build on Odoo + OSS monitoring** | Corporate Services Head | W5 | Commercial PSA licensing becomes favourable below 400 technicians |
| 7 | **RMM agent** | **Conditional buy (L6)** | CTO / CFO | **W5, after pilot** | **`D-18` — OPEN.** Wazuh + osquery cover monitoring; patch orchestration at scale may justify commercial |
| 8 | Contact centre | **Build console, buy telephony** | Customer Service Manager | W4 | Carrier interconnect rules change in Bangladesh |
| 9 | Business intelligence | **Metabase (OSS)** | CTO | W4 | Metabase AGPL-3 terms change (§6) |
| 10 | Data warehouse | **ClickHouse (OSS)** | CTO | W8 | Analytical load outgrows replicas before W8 (`TR-14`) — pull forward |
| 11 | Identity provider | **Keycloak (OSS)** | CTO | **Monthly** (no LTS) | `TR-08` — currency becomes unmanageable |
| 12 | API gateway | **Kong (OSS)** | Solution Architect | W4 | Consumer count or plugin needs exceed the free tier |
| 13 | Document management | **OCA `dms` → Mayan EDMS at W5** | Quality Manager | W4 | Volume or OCR needs arrive before W5 |
| 14 | E-signature | **L6 qualified for contracts; L5 for operational** | Legal / CTO | W3 | An accredited OSS trust service becomes available in Bangladesh |
| 15 | Conversational AI | **Build on self-hosted LLM** | CTO | **W5 — `AR-011` §9.4 gate** | Bengali evaluation fails EV-01/02/03 (`A-04`) → scope narrows to transactional |
| 16 | ML platform | **Build on MLflow (OSS)** | CTO | W6 | — |
| 17 | Payment processing | **Integrate, never build** | CFO | — | Regulated; permanent |
| 18 | Accounting engine | **Odoo `account` + custom BD compliance** | CFO | W3 | NBR mandates full electronic invoice clearance (`A-07`) |
| 19 | Payroll engine | **OCA base + custom BD rules** | HR Director | W5 | — statutory rules change annually; the *pack* changes, not the decision |
| 20 | E-commerce storefront | **Build in Next.js** | CCO | W7 | — must share identity, catalogue, stock and settlement |

### 5.1 The four conditional decisions

`PGD-000` correctly identifies that four decisions are conditional with no review mechanism. All four
now have one:

| # | Decision | Condition | Owner | **Date** |
|---|---|---|---|---|
| 7 | RMM agent — OSS or commercial | Wave 5 pilot outcome | CTO / CFO | **W5** (`D-18`) |
| 2 | OCA `field-service` — extend or reclassify to L5 | v19 migration effort ≤ 20 PW | Implementation Partner | **W0** (`W0-01`, blocking) |
| 15 | Self-hosted LLM scope | Bengali evaluation gate | CTO | **W5** (`AR-011` §9.4) |
| 13 | Mayan EDMS timing | Volume and OCR need | Quality Manager | **W4** |

---

## 6. Licence-Currency Watch

Every fair-code, source-available or copyleft-network component carries a change risk and a **named
fallback**. This is `TR-09`, and it is the risk most likely to arrive without warning.

| Component | Licence | Obligation | **Named fallback** | Watch |
|---|---|---|---|---|
| **Redpanda** | **BSL** — converts to Apache-2.0 four years after each merge | Production use permitted within limits | **Kafka (Apache-2.0)** | Terms reviewed at each wave gate; the consumer library (`AR-009` §6.2) makes the swap a configuration change |
| **TimescaleDB** | Apache-2.0 core; advanced features under **TSL** | Some features require a commercial licence | **Apache-2.0 features only — CI-checked** | A TSL dependency converts a $0 component into a licensed one mid-programme |
| **Metabase** | **AGPL-3** | Source disclosure if modified and served over a network | Superset | Deployed **unmodified**; any modification would be published |
| **Grafana** | **AGPL-3** | As above | — (observability is replaceable but disruptive) | Deployed unmodified |
| **MinIO** | **AGPL-3** | As above | S3-compatible alternative | Deployed unmodified |
| **RustDesk** | **AGPL-3** | As above | MeshCentral (Apache-2.0) | Deployed unmodified |
| **n8n** | **Sustainable Use** | Free for internal business purposes; **not for resale as a competing service** | Temporal / custom orchestration | **Used only for internal orchestration.** A customer-facing automation product would breach it |
| **Odoo CE / most OCA** | **LGPL-3** | Modifications to the library must be shared | — | **Extensions are separate modules, not modifications to core** (AS-05, `AR-007` §5) |
| **Wazuh** | GPL-2 | | osquery (Apache-2.0) | |

### 6.1 Watch rules

| # | Rule |
|---|---|
| **LW-01** | Every AGPL, BSL, TSL or fair-code component has a **named fallback** on the radar. A component with no fallback may not be Adopt |
| **LW-02** | **Automated licence scan on every dependency addition.** AGPL, BSL, TSL and fair-code additions require **architecture approval** |
| **LW-03** | Licence terms are re-verified at **every wave gate**, not annually. `02-05` §4's *"reviewed annually"* is too slow for a 36-month programme with nine gates |
| **LW-04** | The n8n Sustainable Use boundary is stated explicitly in `AR-005` §5.17 and re-checked whenever n8n is used in a customer-facing path |
| **LW-05** | An AGPL component is deployed **unmodified**. A modification is an architecture decision requiring an ADR and a publication commitment |

> **LW-03 changes `02-05`'s position deliberately.** An annual review means a licence change could sit
> undetected for eleven months, across two waves of build. Nine wave gates over 36 months is the right
> cadence, and it costs almost nothing because the scan is automated.

---

## 7. The L6 Commercial Register

Four components. Each requires **CFO approval individually** and an annual review of whether an
open-source alternative has matured.

| Component | Purpose | Module | Cost basis | OSS alternative assessed | Ring |
|---|---|---|---|---|:--:|
| **Cloud telephony / CPaaS** | Inbound IVR, routing, recording on hotline 16743 | M27 | $200–600 / month | Asterisk/FreePBX viable technically, but **carrier interconnect in Bangladesh requires a licensed provider** | ADOPT |
| **Qualified e-signature** | Legally binding signatures on AMC, MSP, rental and seller agreements | M24 | $100–400 / month | OSS signing works technically but **lacks accredited trust-service status for enforceability** | ADOPT |
| **Identity verification / KYC** | Marketplace seller and high-value customer verification | M12 | $0.30–0.80 per check | **Requires an accredited data source**; no OSS equivalent | ADOPT |
| **Endpoint RMM agent** | Patch management at scale on client Windows/macOS estates | M05 | $2–5 per endpoint / month | Wazuh + osquery cover monitoring; patch orchestration at scale may require commercial | **TRIAL — `D-18`, decision W5** |

**Total L6 exposure: $0–36K over three years**, against a programme cost the Technology Stack
Specification restates at approximately $690K–1,150K.

### 7.1 L6 governance

| # | Rule |
|---|---|
| **L6-01** | Every L6 component requires **individual CFO approval** |
| **L6-02** | **Model every per-unit metric at 5× projected volume before signing** (`TR-15`). The RMM agent at $2–5 per endpoint is the one that scales dangerously |
| **L6-03** | Annual review of whether an OSS alternative has matured |
| **L6-04** | A fifth L6 component requires **Design Authority and CFO approval**. The bounded set is the point of the position, not an accident of the current count |
| **L6-05** | Every L6 component has a **documented exit** — what happens to the data and the capability if the contract ends |

> **L6-05 is missing from `02-05` and is added here.** A qualified e-signature provider holds
> evidentiary records for contracts with a multi-year life. *"What happens to the signed envelopes if
> we change provider"* is a question that must have an answer before signing, not after.

---

## 8. The Adoption Procedure

**How the estate acquires a 25th open-source system.** Stated because the estate already has 24, and
the difference between a coherent stack and an accumulation is whether each addition was a decision.

| Step | Action | Gate |
|:--:|---|---|
| 1 | **Apply the L1–L6 selection hierarchy** (`02-01` §5). Can Odoo, OCA, a free third-party module or an existing L4 system do it? | Solution Architect |
| 2 | If a new component is genuinely needed, enter at **ASSESS** with a named owner and a decision date | Chief Architect |
| 3 | Assess against §8.2 criteria | Named owner |
| 4 | If it passes, move to **TRIAL** in a bounded context with a decision date | Chief Architect |
| 5 | Move to **ADOPT** or **HOLD** by the decision date. **It may not remain in Trial** | Design Authority |
| 6 | On Adopt: register in `CO-004` (licence), add to `PE-002` (environments), assign a currency policy (§9), add to the observability stack | Platform |

### 8.2 Assessment criteria

| # | Criterion | Fail condition |
|---|---|---|
| A-01 | **Licence** — permissive, or copyleft with a named fallback | AGPL/BSL/fair-code with no fallback → **fail** (LW-01) |
| A-02 | **Maintenance** — active commits, a release in the last six months, a real community | Single-maintainer or dormant → fail |
| A-03 | **Version currency policy** — does it have an LTS line, or must it be kept current? | No policy at all → fail. *(No LTS is acceptable if the currency obligation is accepted, as for Keycloak)* |
| A-04 | **Operability** — deployable, observable, backup-able, upgradeable by the platform team | No health endpoint, no metrics → fail |
| A-05 | **Data location** — no data leaves Bangladesh or the approved region without a safeguard | Mandatory offshore processing of personal data → **fail** (NFR-099) |
| A-06 | **Skills** — available in Bangladesh, or teachable within a wave | Requires a scarce specialism with no plan → fail |
| A-07 | **Exit** — can it be replaced, and what is the migration path? | No exit path → fail |
| A-08 | **Overlap** — does an Adopt component already do this? | Duplicate capability → fail unless the incumbent is moving to Hold |

> **A-08 is the criterion that keeps the count at 24 rather than 40.** The most common way an estate
> acquires redundant technology is a team adopting a component whose function an existing Adopt
> component already performs adequately.

---

## 9. Currency Policy and Review Cadence

### 9.1 Per-component currency

| Class | Policy |
|---|---|
| **No LTS line** (Keycloak) | **Kept current continuously.** Monthly review; security releases within the standard window. HA cluster permits rolling upgrade |
| **LTS line** (Odoo, PostgreSQL, Next.js) | Pinned to the LTS; major upgrade at a **planned slot** (ADR-027); currency reviewed at every wave gate |
| **Rolling** (most L4 systems) | Pinned exact version; monthly update cycle; security patches out of cycle |
| **Libraries** | **Every dependency pinned to an exact version**; automated vulnerability alerts; monthly update cycle |
| **OCA subtrees** | Pinned commit; controlled cadence; **every update regression-tested in staging** |

### 9.2 Review cadence

| Review | Cadence | Owner | Output |
|---|---|---|---|
| **Version currency** — every component vs upstream release and EOL data | **Every wave gate** | Solution Architect | Updated §4; new findings raised |
| **Licence currency** — every fair-code component | **Every wave gate** (changed from annual — LW-03) | Solution Architect | Updated §6 |
| **Ring review** — Trial components past their decision date | Every wave gate | Chief Architect | Promotion to Adopt, or Hold |
| **L6 review** — has an OSS alternative matured? | Annual + at contract renewal | CTO / CFO | §7 update |
| **Build-vs-buy triggers** — has any §5 revisit condition become true? | Every wave gate | Chief Architect | New ADR where triggered |
| **Security patch level** | Continuous | Platform | `SC-009` |

### 9.3 A missed review

> **A component whose currency review is missed for two consecutive wave gates moves automatically
> to HOLD** until reviewed.

This is deliberately blunt. The failure mode this register exists to prevent is not a bad decision —
it is a good decision quietly becoming stale, which is precisely what audit `M-01` (stale Odoo release
date) and `H-01` (NIST SP 800-88 r1, withdrawn 26 September 2025) both were. **A control that
degrades gracefully when ignored is not a control.**

---

## 10. The Radar

### 10.1 ADOPT

| Component | Layer | Version | Licence | Owner | Next review |
|---|:--:|---|---|---|---|
| Odoo Community Edition | L1 | 19.0 | LGPL-3 | CTO | W5 gate (`D-025`) |
| PostgreSQL | L4 | 16 | PostgreSQL | Solution Architect | W5 gate |
| OCA modules (140+, 18 repos) | L2 | v19 | LGPL/AGPL-3 | Solution Architect | **W0** (`W0-01`) |
| Python | — | 3.12+ | PSF | Solution Architect | W5 gate |
| Keycloak | L4 | 26.x | Apache-2.0 | CTO | **Monthly** |
| Kong Gateway | L4 | 3.x | Apache-2.0 | Solution Architect | W4 |
| Redis | L4 | 7.x | BSD-3 | Platform | W4 |
| n8n | L4 | 1.x | Sustainable Use | Solution Architect | Every gate (LW-04) |
| Novu | L4 | 2.x | MIT | Platform | W4 |
| Nginx · PgBouncer · Docker / K3s | L4 | current | BSD-2 / ISC / Apache-2.0 | Platform | W4 |
| TimescaleDB | L4 | 2.x | Apache-2.0 (+TSL watch) | Platform | Every gate |
| Traccar · OSRM · VROOM | L4 | 6.x / 5.x / 1.14+ | Apache-2.0 / BSD-2 | Solution Architect | W6 |
| Metabase · Grafana | L4 | 0.52+ / 11.x | AGPL-3 | CTO / Platform | Every gate |
| MinIO | L4 | current | AGPL-3 | Platform | Every gate |
| OpenTelemetry · Prometheus · Loki · Tempo | L4 | current | Apache-2.0 | Platform | W4 |
| Vault | L4 | current | — | Head of InfoSec | W4 |
| ClamAV | L4 | current | GPL-2 | Head of InfoSec | W4 |
| Mayan EDMS | L4 | 4.x | Apache-2.0 | Quality Manager | W4 |
| MLflow · Ollama | L4 | 2.x / 0.5+ | Apache-2.0 / MIT | CTO | W5 (`AR-011` §9.4) |
| Wazuh · osquery · MeshCentral | L4 | current | GPL-2 / Apache-2.0 | Corporate Services Head | W5 |
| Flutter / Dart | L5 | current | BSD-3 | CTO | W6 (`D-027`) |
| Next.js / React | L5 | **15 → 16** | MIT | CTO | **W0 (`D-026`)** |
| Payload CMS | L5 | 3 | MIT | Digital team | W0 (`A-05`) |
| L6: telephony · e-signature · KYC | L6 | — | Commercial | CTO / CFO | Annual |

### 10.2 TRIAL

| Component | Purpose | Owner | **Decision date** |
|---|---|---|---|
| **ClickHouse** | Analytical warehouse | CTO | **W8** — pullable forward if analytical load outgrows replicas (`TR-14`) |
| **Redpanda** | Event bus at scale | Solution Architect | **W6** — Kafka is the registered fallback |
| **Endpoint RMM agent (L6)** | Patch orchestration at scale | CTO / CFO | **W5** (`D-18`) |

### 10.3 ASSESS

| Component | Question | Owner | Decision date |
|---|---|---|---|
| **Next.js 16** | Payload CMS 3 compatibility (`A-05`) | CTO | **W0** (`D-026`) |
| **PostgreSQL 17/18** | Move at the same gate as the Odoo upgrade slot? | Solution Architect | W5 |
| Open-weight Bengali LLM candidates | Do they pass `AR-011` §9.4 EV-01…EV-06? | CTO | **W5** |
| PWA vs Flutter for P07 mobile | Avoid a second mobile framework | CTO | **W6** (`D-027`) |

### 10.4 HOLD

| Component | Reason | Existing use |
|---|---|---|
| **Odoo Enterprise** | ADR-001 — licence cost, reduced extensibility | None |
| **Hosted LLM APIs** | **ADR-029 — NFR-099 transfer restriction. Legal, not commercial** | None |
| **Rasa** | OSS in maintenance mode | None |
| **React Native** | ADR-026 — avoid a second mobile framework. Legacy architecture removed at 0.83+ | None; `D-027` must confirm |
| **Google Routes / commercial routing APIs** | ADR-005 — cannot embed skill, certification, van-stock and working-time constraints | None |
| **Marketplace SaaS** | ADR-011 — settlement must live in the ledger | None |
| **Commercial PSA/RMM suite (full)** | ADR-012 — licence scaling at 400 technicians | Agent only, conditionally (§7) |
| **InfluxDB** | ADR-007 — second engine, second skill set | None |
| **OpenSearch/Elasticsearch from W1** | ADR-010 — synchronisation and consistency cost for no measured benefit | None; escalation planned not pre-committed |
| **Digital Security Act 2018 citations** | **Repealed twice** — Cyber Security Act 2023 → Cyber Security Ordinance 2025 | Corrected in `05-06`; **`RR-005` regulatory currency register is the durable control** |
| **NIST SP 800-88 r1** | **Withdrawn 26 September 2025.** M06 destruction certificates are built on it (`H-01`) | **Live exposure** — the certificate's defensibility is the product. `SC-006`'s to close |

> **The last two Hold entries are not technologies; they are citations.** They appear here because the
> failure mode is identical — a correct choice becoming stale with nothing watching — and because
> `RR-005` (Standards & Regulatory Currency Register) is the sibling control to this radar. The two
> documents should be reviewed together at every wave gate.

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| Q-01 | **`D-026` Next.js 15→16 timing.** Cost rises with each of six applications built on 15 | CTO | **W0** | Six portals' foundation |
| Q-02 | **`D-025` Odoo upgrade slot** — ratify ADR-027? | CTO / Steering | **W0** | `GV-004` schedule; VC-01 |
| Q-03 | **`W0-01` OCA v19 gap** — is `field-service` closable within 12–20 PW (`A-03`)? | Implementation Partner | **W0 — blocking** | Wave 2 scope; build-vs-buy #2 |
| Q-04 | **`D-027` P07 mobile framework** | CTO | W6 | ADR-026 |
| Q-05 | **`D-18` RMM agent** | CTO / CFO | W5 | L6 envelope |
| Q-06 | Is the M06 destruction-certificate basis migrated from the withdrawn NIST SP 800-88 r1 to r2 / IEEE 2883 / ISO/IEC 19790? (`H-01`) | Technical Services Head / `SC-006` | **W2** | M06 commercial defensibility |
| Q-07 | Who owns the radar between wave gates? | Chief Architect | W1 | §9.3 automatic-Hold rule |

---

## 12. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| D-A13-01 | Register form | Frozen decision table; **live radar with rings** | **Live radar** | A frozen register on a 36-month programme is wrong before the programme ends | Every component has an owner, a review date and an exit criterion |
| D-A13-02 | Licence review cadence | Annual (`02-05` §4); **every wave gate** | **Every wave gate** | Annual means a change sits undetected across two waves of build. The scan is automated, so cadence is nearly free | LW-03 |
| D-A13-03 | Missed review | Flag; **automatic move to HOLD** | **Automatic HOLD** | `M-01` and `H-01` were both a good decision quietly becoming stale | §9.3 |
| D-A13-04 | Trial ring | May persist; **must decide by its date** | **Must decide** | A permanent Trial is an unowned production dependency | Three Trial components with dates |
| D-A13-05 | Fair-code components | Accept the risk; **named fallback mandatory** | **Named fallback** | Kafka for Redpanda, Apache-only for TimescaleDB, Superset for Metabase | LW-01; a component without one cannot be Adopt |
| D-A13-06 | L6 set | Open; **bounded, individually approved** | **Bounded** | A governed L6 is more honest than forcing an unsuitable OSS substitute or allowing ungoverned SaaS (ADR-020 family) | A fifth component needs Design Authority + CFO |

---

## 13. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | Every technology in the stack has a ring, an owner and a review date | §10 — 60+ components |
| AC-02 | All 20 `02-05` §7 decisions are restated with a revisit trigger | §5 |
| AC-03 | The four conditional decisions have a named decision date | §5.1 |
| AC-04 | Version-currency findings are re-verified with a fresh date | §4 — five findings, verified 2026-08-18 |
| AC-05 | Every fair-code component has a named fallback | §6 — LW-01 |
| AC-06 | The L6 register carries a cost envelope, an approval gate and an exit requirement | §7 — L6-01…L6-05 |
| AC-07 | An adoption procedure exists with fail conditions | §8 — A-01…A-08 |
| AC-08 | A missed review has an automatic consequence | §9.3 |

**Definition of done.** Complete when every criterion is met, `D-025`, `D-026` and `D-027` are decided,
and `PGD-000`'s `AR-013` row is updated with a fresh enumeration timestamp.

---

## 14. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-001` §11.2 | Technology constraints CON-01…CON-07 |
| Upstream | `AR-004` | ADR-001, 006–013, 019, 020, 026–029 — rationale for these selections |
| Downstream | `CO-004` | Licence obligation register |
| Downstream | `CO-005`, `CO-006` | TCO and procurement |
| Downstream | `PE-002`, `PE-006` | Environments and sizing |
| Downstream | `SC-006` | M06 destruction-certificate basis (`H-01`, Q-06) |
| Downstream | `SC-009` | Vulnerability response |
| **Sibling** | **`RR-005`** Standards & Regulatory Currency Register | **The same control for statutes and standards.** Reviewed together at every wave gate |
| Lateral | `../../1000fix_ERP_Module/02_Architecture/02-05` §4, §6, §7 | The frozen register this document makes live |
| Lateral | `../../primary-doc/…Technology_Stack_Specification.md` §4–§9, §23, §25.2 | The technology authority |

---

## 15. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./AR-001` · `./AR-004` · `./AR-011` ·
`../_AUDIT/PGD-AUDIT-003_*.md`

**Workspace**
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §4–§9, §17.4, §18.5, §23, §25.2, §25.4 ·
`../../1000fix_ERP_Module/02_Architecture/02-05` §3, §4, §6, §7

**External sources**

| Source | Verified |
|---|---|
| ThoughtWorks Technology Radar — ring model | 2026-08-18 |
| ISO/IEC 5230 (OpenChain) — open-source licence compliance | 2026-08-18 |
| Odoo 19.0 released 18 September 2025; supported to ~September 2028; Odoo 20 expected Sept–Oct 2026 | 2026-08-18 |
| PostgreSQL 16 supported to November 2029; 18 to November 2030 | 2026-08-18 |
| Keycloak — no LTS line; only the newest release receives security fixes | 2026-08-18 |
| NIST SP 800-88 r1 **withdrawn 26 September 2025**; r2 requires IEEE 2883 and ISO/IEC 19790 key zeroization | 2026-08-18 |
| Cyber Security Ordinance 2025 (Bangladesh) — in force; Digital Security Act 2018 repealed twice | 2026-08-18 |

---

## 16. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Converts `02-05` §7's frozen register into a live four-ring radar with owners, review dates and exit criteria. Re-verifies five version-currency findings. Changes licence review from annual to per-wave-gate. Adds the automatic-HOLD rule for missed reviews | *Pending — CTO* |

---

*`AR-013` · Category 02 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
