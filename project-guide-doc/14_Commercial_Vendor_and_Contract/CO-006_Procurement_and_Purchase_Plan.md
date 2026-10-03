---
id: CO-006
title: Procurement & Purchase Plan
category: 14 — Commercial, Vendor & Contract
code: CO
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-19
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Head of Procurement
approver: Chief Financial Officer, with ERP Steering Committee endorsement
standards_basis: >
  ISO 21502:2020 §7.14 (procurement) · ISO 37500:2014 §6 (supplier selection and agreement) ·
  ISO 9001:2015 §8.4 (control of externally provided processes, products and services) ·
  ISO 20400:2017 (sustainable procurement) · ISO/IEC 19770-1:2017 (IT asset management) ·
  ISO 55000:2024 (asset management principles, for the device estate) ·
  ISO 31000:2018 (supply risk) · CIPS procurement practice ·
  Bangladesh VAT & SD Act 2012 and Income Tax Act 2023 (withholding on purchases)
traces_to: >
  PGD-000 CO-006 · 02-05 §6 ("each requires CFO approval and an annual review") ·
  AR-013 §7.1 L6-01…L6-05 · CO-004 §8.1 (the entitlement register this plan acquires against) ·
  CO-005 §5.2, §5.3, §5.5 (the cost lines this plan commits) · CH-002 §7.1, §9.1
  (learner devices and the training environment, both assigned here) · PE-001 §3.3, §3.5
  SEL-01…SEL-05 · PE-006 §8.2 · RSK-008 · BEA-16
depends_on: CO-004 · CO-005 · CO-003 · AR-013 · PE-001 · PE-002 · PE-006 · CH-002 · SC-006 · SC-007 · GV-008
verified_on: 2026-08-19
priority: P2
needed_by: W1
enumeration_timestamp: 2026-08-19 02:36 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# CO-006 — Procurement & Purchase Plan

### Category 14 · Code `CO` · ISO 21502:2020 §7.14 · ISO 9001:2015 §8.4 · ISO 20400:2017 · ISO/IEC 19770-1:2017

---

> **Local rule prefix: `PPP-nn`.** Verified to return **zero** occurrences workspace-wide before
> allocation, at 2026-08-19 02:36 (+06), by
> `grep -rho "PPP-[0-9]\{1,3\}" --include=*.md .` across all six repositories.
>
> **⚠ The category code `CO` is already a rule prefix in three unrelated namespaces** — cost
> controls in `PE-006` §8.4, content-operating-model rules in `CG-002`, callback-ordering rules in
> `IN-006`; **108 occurrences across 30 files and 3 repositories**. No document in Category 14 uses
> `CO-nn` as a local rule prefix. Recorded as `CVA-01`.

---

## 1. Purpose

`02-05` §6 states a control: *"Each [L6 component] requires **CFO approval** and an annual review of
whether an open-source alternative has matured."* `AR-013` `L6-01`…`L6-05` elaborate it into five
rules. `CO-004` §8.1 turns it into an entitlement register with metrics, caps and exits.

**None of that is a procurement instrument.** There is no purchase route, no approval threshold, no
lead-time plan, no supplier-onboarding step and no receipt-and-acceptance test. `PGD-000` puts it in
one line: *"No procurement instrument implements that."*

This plan is that instrument, and it covers considerably more than the four L6 components — because
**four other categories of purchase are named across the estate with no owner at all**:

| # | What | Where it is named | Owner before this plan |
|:--:|---|---|---|
| 1 | **The device estate** — `P02` devices for **215–430 technicians**, plus 12 learner devices per regional hub, plus rider and field-auditor devices | `CH-002` §7.1, §9.1; `RSK-008`'s mitigation includes *"Company-provided devices"* | **`CH-002` §7.1 marks it "`CO-006` ⬜"** — assigned to a document that did not exist |
| 2 | **The `BD-R` facility** — Tier III+ colocation, in-country key custody, cross-border private link | `PE-001` §3.3, §3.4, `SEL-01`…`SEL-05`; `SC-007-D-01` makes it **Wave 1** | Nobody. `PE-001` gives selection considerations and no buyer |
| 3 | **Professional services** — the `DEP-31` residency legal opinion, the `DEP-29` marketplace tax opinion, independent assurance under `GV-010`, penetration testing under `SC-009` | `GV-008` §6.3 names them as calls on the **$60K risk budget** | The risk budget has a holder; **the purchases have no route** |
| 4 | **Training facilities and the training environment** — one classroom per regional hub | `CH-002` §9.1, marked *"⬜ Unconfirmed"* | Operations, unconfirmed |

> **The most consequential sentence in this document.** `RSK-008` — technician rejection of the
> mobile application — is rated **High likelihood / Critical consequence**, and one of its named
> mitigations is *"Company-provided devices."* **215–430 devices, at a lead time nobody has
> established, for a Wave 2 application.** `CH-002` assigned the procurement to this document and
> this document did not exist. §6 gives it a route, a lead time and a date, and §6.4 shows that the
> date is **already tight**.

### 1.1 Scope

**In scope:**

| # | Covered |
|:--:|---|
| 1 | The **seven procurement categories** and the route for each (§3) |
| 2 | The **approval matrix** — who may commit what, and at what value (§4) |
| 3 | **L6 commercial components** — the route that implements `L6-01`…`L6-05` and `CO-004` §8.1 (§5) |
| 4 | The **device estate** — quantities, lead times, the total-cost-of-ownership view, and the sustainability position (§6) |
| 5 | **Infrastructure** — regional cloud, the `BD-R` facility, key custody, the private link (§7) |
| 6 | **Professional services** — the four purchases the risk budget funds (§8) |
| 7 | **Sustainable procurement** under ISO 20400, and the consistency problem a circular-economy business has when it buys hardware (§9) |
| 8 | **Supplier onboarding, purchase orders, receipt and acceptance** (§10) |
| 9 | **Lead times against the wave plan** — the schedule risk that procurement, not development, creates (§11) |
| 10 | **Tax treatment of purchases** — VAT and withholding on goods and services (§12) |

**Explicitly out of scope:**

| Topic | Owned by | Why the boundary sits here |
|---|---|---|
| The **implementation contract** and its supplier | `CO-002`, `CO-003` | A different instrument, a different value, a different governance route. This plan covers everything **except** the implementation partner |
| **What each purchase costs** in the five-year model | `CO-005` §5 | This plan commits; `CO-005` models |
| The **entitlement register** — metrics, caps, exits, obligations | `CO-004` §8.1 | This plan acquires against that register. `PPP-08` is the interface |
| **Which** technology is selected | `AR-013` §5, §8 | Build-vs-buy and radar decisions precede procurement. This plan does not choose; it buys what was chosen |
| **Infrastructure sizing** | `PE-001`, `PE-006` | §7 procures the shapes they specify |
| **Recruitment** of Company staff | HR; `GV-007` §8.3 | People are not procured, and treating them as a procurement category is how hiring lead times get missed |
| **Content and translation** supply | `CG-002`; `GV-001` §6.3 workstream 5 | A chartered Company workstream with its own operating model |

### 1.2 Intended audience

| Audience | What they use this plan for |
|---|---|
| **Head of Procurement** | The owner. §3's routes, §10's process, §11's lead times |
| **Chief Financial Officer** | The approver. §4's matrix and §5's `L6-01` route are where the CFO's `02-05` §6 obligation is actually discharged |
| **Chief Technology Officer / Chief Architect** | §5 and §7 — the technical specification behind each purchase, and the `L6-04` gate on a fifth component |
| **HR Director / Training Lead** | §6's device plan and §9's facility plan are `CH-002`'s unfunded lines, given a route |
| **Operations** | §6.4's device rollout runs through 51+ branches and the regional hubs |
| **Legal Counsel** | §8's professional-services purchases, and §12's tax treatment |
| **Sustainability / ESG owner** | §9 — and the reason a company selling e-waste services must have a device-procurement position |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Clause | How this plan conforms | Departure and rationale |
|---|---|---|---|
| **ISO 21502:2020** | §7.14 procurement | §3's routes, §4's authority, §10's administration | None |
| **ISO 37500:2014** | §6 supplier selection and agreement | §10's onboarding; §5's L6 route | ISO 37500 is written for outsourcing relationships. **Departure:** most purchases here are goods or commodity services, so §6's full selection rigour is applied only above the §4 thresholds |
| **ISO 9001:2015** | **§8.4** — control of externally provided processes, products and services | §4's evaluation criteria, §10.4's receipt and acceptance, §10.5's supplier performance | **Obligatory**, as for `CO-003`: RFP §19.3 requires 1000FiX to maintain ISO 9001 throughout, and §8.4 covers *every* external provider, not only the implementation partner |
| **ISO 20400:2017** | §4 (understanding the fundamentals), §5 (integrating sustainability into policy), §7 (the procurement process) | §9 | **Guidance, not certifiable.** ISO 20400 is a guidance standard with no conformity assessment, and this plan says so rather than implying a certification |
| **ISO/IEC 19770-1:2017** | §8 operational planning | §5's acquisition against `CO-004` §8.1's entitlements | The entitlement clause only; a full ITAM management system is not claimed |
| **ISO 55000:2024** | Asset management principles | §6.5's whole-life view of the device estate — acquisition, deployment, refresh and disposal as one decision | Principles only. The Company has no asset-management system, and §6.5 is a plan for one category of asset, not a management system |
| **ISO 31000:2018** | §6.4 risk evaluation | §11's lead-time risk; §7.3's single-source analysis | None |
| **CIPS** procurement practice | — | §4's segregation of duties; §10.2's three-quote rule | Adopted as practice |
| **VAT & SD Act 2012**; **Income Tax Act 2023** | — | §12 | **Not a tax opinion**; `PPP-Q-06` requires one for the import cases |

### 2.2 Source material relied on

| Source | Location | What it establishes |
|---|---|---|
| `02-05` §6 | `../../1000fix_ERP_Module/02_Architecture/02-05_*.md` | The four L6 components; **CFO approval per component**; the annual open-source review |
| `AR-013` §7, §7.1 | `../02_Architecture_and_Design/AR-013_*.md` | `L6-01`…`L6-05`; the bounded set of four; **`L6-02`'s 5× volume rule**; `D-18`'s open RMM decision |
| `CO-004` §8.1, §9.5 | `./CO-004_*.md` | The entitlement register with metrics, caps, exits and approval records; the escalation route for a fifth component |
| `CO-005` §5.2, §5.3, §5.5, §7 | `./CO-005_*.md` | The cost lines this plan commits: regional infrastructure, `BD-R`, L6, and the fifth-component exposure |
| `CO-003` §7, §9, §11 | `./CO-003_*.md` | The acceptance and remedy patterns §10.4 mirrors at a smaller scale |
| `CH-002` §7.1, §9.1 | `../13_Training_Change_and_Adoption/CH-002_*.md` | **Learner devices — 12 per regional hub, plus `P02` devices for 215–430 technicians — explicitly assigned to `CO-006`.** One classroom per regional hub, *"⬜ Unconfirmed"*. The training environment must be *"available and stable 6 weeks before the first W1 cohort"* |
| `PE-001` §3.3, §3.4, §3.5, §8.2 | `../10_Infrastructure_DevOps_and_Environments/PE-001_*.md` | `BD-R`'s five cost components and **`SEL-01`…`SEL-05`, the five selection considerations** |
| `PE-006` §8.2, §8.4 | `../10_Infrastructure_DevOps_and_Environments/PE-006_*.md` | The three excluded infrastructure lines; cost controls `CO-01`…`CO-06` *(note: `PE-006`'s own rule prefix — see `CVA-01`)* |
| `PE-002` §5.8, §8.2, §9.3 | `../10_Infrastructure_DevOps_and_Environments/PE-002_*.md` | The `training` environment; the provisioning sequence; ephemerality |
| `SC-006` `ES-3` | `../05_Security_Privacy_and_Compliance/SC-006_*.md` | In-country key custody — the HSM or managed-KMS purchase |
| `SC-007` `SC-007-D-01` | `../05_Security_Privacy_and_Compliance/SC-007_*.md` | *"The mechanism is built in Wave 1 … W1 cost incurred before the answer"* — why `BD-R` procurement is W1, not W2 |
| `GV-008` §6.2, §6.3 | `../00_Programme_Governance_and_Control/GV-008_*.md` | The **$60K risk budget** and its five named calls; the $82K management reserve |
| `GV-007` §8.3 | `../00_Programme_Governance_and_Control/GV-007_*.md` | **10–16 week hiring lead times** — the comparator §11 uses for procurement lead times |
| `BE-007` §7.1 | `../07_Build_Engineering_and_Development_Standards/BE-007_*.md` | `BEA-16` — MinIO archived; the `W0` replacement decision that may create a fifth L6 component |
| RFP §16.3 `OPT-12`, §20.6 | `../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` | Additional `BD-R` capacity as a priced option; the Critical risks including `RSK-008` |

### 2.3 Findings this plan raises

| Finding | Severity | Statement |
|---|:--:|---|
| **`CVA-19`** | **High** | **The device estate is unowned, unsized in cost and unscheduled, and it is a named mitigation for a Critical risk.** `CH-002` §7.1 assigned it to `CO-006`; `CO-005` §7 does not carry a device line; no document states a lead time. §6 |
| **`CVA-20`** | Medium | **The number of regional training hubs is not stated anywhere**, and it is the multiplier for classroom devices, facilities and the whole training-delivery logistics plan. `CH-002` §4.6 aggregates 51+ branches into hubs without saying how many. §6.2 |
| **`CVA-21`** | Medium | **`02-05` §6's *"annual review"* of L6 open-source alternatives conflicts with the wave-gate cadence** `AR-013` `LW-03`, `BE-007` `LX-30` and `CO-004` `LIC-35` all adopt. The same defect as `CVA-18`, in the commercial half of the same section. §5.4 |
| **`CVA-22`** | Medium | **A company whose Category D business is e-waste, refurbishment and ESG reporting (`M18`, `cd_esg_report`) has no sustainable-procurement position for its own hardware purchases.** §9 |

---

## 3. The Seven Procurement Categories

| # | Category | Examples | Route | Owner | Approval |
|:--:|---|---|---|---|---|
| **1** | **L6 commercial software** | Telephony/CPaaS, qualified e-signature, KYC, RMM agent | §5 — the `L6` route | CTO proposes; Procurement runs | **CFO individually** (`L6-01`); **+ Design Authority** for a fifth (`L6-04`) |
| **2** | **Cloud and hosting** | Regional compute, storage, network, object storage, CDN/WAF | §7.1 — framework agreement, consumption-based | Platform Engineering | CFO above the §4 threshold; consumption within an approved envelope thereafter |
| **3** | **Colocation and facilities** | The `BD-R` Tier III+ site; cross-border private link | §7.2 — a **selection exercise**, not a purchase order | CTO with Chief Architect | **CFO + Steering Committee** — it is a multi-year commitment with an exit cost |
| **4** | **Security hardware and key custody** | HSM or managed KMS for in-country `K-4` custody | §7.3 | CISO with Chief Architect | CFO |
| **5** | **Devices and endpoint hardware** | `P02` technician handsets; classroom devices; rider (`P09`) and field-auditor (`P11`) devices | §6 | IT with Operations | CFO above threshold; **`RSK-008` makes this a Steering Committee visibility item regardless** |
| **6** | **Professional services** | Legal opinions, independent assurance, penetration testing, tax advice | §8 | The commissioning role | CFO; **funded from the `GV-008` §6.3 risk budget where named** |
| **7** | **Tooling and subscriptions** | Developer tooling, CI minutes, monitoring SaaS, design tools | §10.3 — a light route | The requesting lead | Delegated authority under §4 |

| # | Rule |
|---|---|
| **`PPP-01`** | **Every purchase falls into exactly one category, and the category determines the route.** A purchase that does not fit is escalated to the CFO rather than routed by analogy |
| **`PPP-02`** | **Category 1 purchases are never routed as Category 7**, however small the monthly figure looks. An L6 component is defined by what it is — a commercial dependency in the runtime — not by its price. `AR-013` `L6-04`'s bounded set is defeated the moment a $200/month tool enters through the tooling route |

---

## 4. Authority

### 4.1 The approval matrix

| Value (USD, whole-of-term commitment) | Approver | Additional requirement |
|---|---|---|
| < $2,000 | Requesting lead, within an approved budget line | Recorded in the purchase log |
| $2,000 – $10,000 | Department head | One written quotation |
| $10,000 – $50,000 | **CFO** | **Three quotations**, or a documented single-source justification (§10.2) |
| > $50,000 | **CFO + Steering Committee** | Three quotations; a business case referencing `CO-005`; an exit analysis |
| **Any L6 component, at any value** | **CFO individually** (`L6-01`) | §5's full route, regardless of value |
| **A fifth L6 component** | **Design Authority + CFO** (`L6-04`) | Plus a five-year `CO-005` entry (`TCO-15`) |
| **Any multi-year facility commitment** | **CFO + Steering Committee** | Plus `SEL-01`…`SEL-05` (§7.2) and an exit plan (`SEL-05`) |

| # | Rule |
|---|---|
| **`PPP-03`** | **Authority is assessed on the whole-of-term commitment, not the first invoice.** A $500/month subscription on a three-year term is an **$18,000** commitment and needs CFO approval. `GV-008` `CB-09` already says this for the budget: *"commitment, not just spend, is tracked. A signed contract is committed money whether invoiced or not"* |
| **`PPP-04`** | **Segregation of duties: the person who specifies may not be the person who approves, and neither may be the person who receipts.** CIPS practice, and the same principle as `GV-011` `CM-16` and `CO-002` `VES-04` |
| **`PPP-05`** | **No purchase is committed against an unapproved budget line.** `GV-008` §5.3's funding gates apply: a Tranche 2 purchase may not be committed before the Wave 4 gate releases T2 |
| **`PPP-06`** | **Every purchase order references the `CO-005` line it consumes.** A purchase that maps to no line in the cost model is either out of scope or a gap in the model, and both need finding before the money leaves |

### 4.2 Emergency purchases

| # | Rule |
|---|---|
| **`PPP-07`** | An **emergency purchase** — one required to restore or protect production service — may be committed by the CTO up to **$10,000** without prior approval, and is reported to the CFO **within 2 working days** with the justification. Above that, the CFO is reached, however inconvenient the hour |

---

## 5. L6 Commercial Components — The Route `02-05` §6 Requires

### 5.1 The route

This is the instrument `02-05` §6 called for and did not provide. Seven steps.

| Step | Action | Owner | Evidence |
|:--:|---|---|---|
| **1** | **Open-source alternative assessed** and the assessment recorded — not asserted | Chief Architect | The assessment, in `AR-013` §7's table |
| **2** | **Radar ring assigned** — `Adopt`, `Trial`, `Assess` or `Hold` (`AR-013` §3.2) | Chief Architect | `AR-013` §10 |
| **3** | **The metric identified and modelled at 5× projected volume** (`L6-02`) | CTO with CFO | **`PPP-08`** |
| **4** | **The exit documented** — what happens to the data and the capability if the contract ends (`L6-05`) | Legal Counsel | `CO-004` §8.1's exit column |
| **5** | **CFO approves individually** (`L6-01`), with the date recorded | **CFO** | `CO-004` §8.1's approval column |
| **6** | Contract negotiated: term, cap, exit, data ownership, DPA where personal data is processed | Procurement with Legal | The contract |
| **7** | **Entitlement registered** in `CO-004` §8.1 before the first invoice | Procurement | `CO-004` `LIC-26` |

| # | Rule |
|---|---|
| **`PPP-08`** | **No per-unit L6 contract is signed without the metric having been modelled at 5× projected volume, and the modelled figure entering `CO-005`'s high case.** `AR-013` `L6-02` states the reason: *"the RMM agent at $2–$5 per endpoint is the one that scales dangerously."* This rule converts that observation into a signature precondition |
| **`PPP-09`** | **Every per-unit L6 contract carries a contractual volume cap or a re-pricing trigger.** A metric with no cap transfers business-growth risk to the cost line, which is the opposite of what growth should do |
| **`PPP-10`** | **An L6 contract term may not exceed the review cadence.** A three-year term on a component reviewed at every wave gate makes the review decorative. **Annual terms with renewal options**, unless a longer term buys a material discount **and** an exit right |
| **`PPP-11`** | **No L6 component enters production before its entitlement row exists in `CO-004` §8.1.** The register is not a record of what was bought; it is a precondition to buying |

### 5.2 The four components and their procurement status

| # | Component | Radar ring | Decision status | Procurement action | Timing |
|:--:|---|:--:|---|---|---|
| 1 | **Cloud telephony / CPaaS** | ADOPT | Decided | Select provider; **number portability for hotline 16743 is a contract term, not a hope** | **W4** — `P10` contact-centre console |
| 2 | **Qualified e-signature** | ADOPT | Decided | Select an **accredited trust-service provider**; `L6-05` exit answered **in writing by the provider** before signature | **W3** — `AR-013` review point |
| 3 | **Identity verification / KYC** | ADOPT | Decided | Select provider; **5× seller-onboarding volume modelled**; verification **results** exportable and retained by 1000FiX | **W7** — marketplace `M12`, `P07` |
| 4 | **Endpoint RMM agent** | **TRIAL** | **`D-18` OPEN** | **Do not procure.** Run the Wave 5 pilot; `L6-02` at 5× endpoints before any commitment | **W5 decision** |

### 5.3 The fifth component that is probably coming

`CO-004` §6.6 and `CO-005` §5.5 both identify the same exposure: **MinIO's community edition was
archived on 25 April 2026**, the replacement decision is `W0` and blocking Wave 1, and one of the
three options is a managed object store.

| # | Rule |
|---|---|
| **`PPP-12`** | **If the MinIO replacement is a commercial or managed service, it is a fifth L6 component** and takes the `L6-04` route: **Design Authority + CFO**, plus a five-year `CO-005` entry (`TCO-15`), plus a **residency assessment against `SC-007`** (`CO-004` `LIC-17`) before any commitment |
| **`PPP-13`** | **The bounded set of four is defended, not merely counted.** `AR-013` `L6-04` makes a fifth component a Design Authority matter *"because the bounded set is the point of the position, not an accident of the current count"*. A fifth arriving by default — because an upstream project archived and nobody wanted to pick a fork — is exactly the case the rule was written for |

### 5.4 `CVA-21` — the review cadence, again

| Document | L6 open-source review cadence |
|---|---|
| `02-05` §6 | *"an **annual** review of whether an open-source alternative has matured"* |
| `AR-013` `L6-03` | *"**Annual** review of whether an OSS alternative has matured"* |
| `AR-013` `LW-03` | Licence terms re-verified at **every wave gate** — *"`02-05` §4's 'reviewed annually' is too slow"* |
| `BE-007` `LX-30`; `CO-004` `LIC-35` | **Every wave gate** |

**The estate has settled on wave-gate cadence for the *licence* review and left the *commercial*
review at annual.** That is arguably defensible — a commercial alternative maturing is slower news
than a licence changing — but it is not stated as a deliberate distinction anywhere, and the two
reviews look at the same four components.

| # | Rule |
|---|---|
| **`PPP-14`** | **The L6 commercial review runs at the same wave gate as the licence review**, and produces one finding per component: *has an open-source alternative matured, and has the licence position changed?* One review, one owner, one gate artefact. Referred to `02-05` §6 and `AR-013` `L6-03` for alignment |

---

## 6. The Device Estate — `CVA-19`

### 6.1 What is required

Assembled from `CH-002` §7.1, `RSK-008`'s mitigation set and the four Flutter applications in
`02-05` §5.4. **No single document has ever listed these together, which is why the total has never
been visible.**

| # | Population | Device | Quantity | Driver | Wave |
|:--:|---|---|---:|---|:--:|
| 1 | **Technicians** — `P02` | Rugged or mid-range Android, offline-capable, Bengali-first | **215 – 430** | `CH-002` §7.1; `RSK-008` mitigation *"Company-provided devices"* | **W2** |
| 2 | **Classroom learners** | Shared Android tablets or handsets, 12 per regional hub | **12 × hubs** — **`CVA-20`: the hub count is not stated anywhere** | `CH-002` §7.1, §4.6 | **W1** |
| 3 | **Riders / logistics** — `P09` | Android, offline-capable | **Not stated in any document** | `02-05` §5.4; `P09` | W3 |
| 4 | **Field auditors** — `P11` | Android tablet, camera, offline | **Not stated in any document** | `02-05` §5.4; `P11` | W5 |
| 5 | Branch counter hardware | Existing estate assumed; **not assessed** | Unknown | `M04`, `P03` | W1 |

> **Two of the five populations have no quantity anywhere in the estate**, and a third depends on a
> hub count nobody has stated. **This is not a costing gap; it is a scoping gap.** `CO-005` §7.5
> lists what is outside its model and this belongs on that list — referred back as an addition.

### 6.2 `CVA-20` — the hub count

`CH-002` §4.6 aggregates **51+ branches** into regional hubs — *"one per site; regional aggregation
avoids 51 separate deliveries"* — and §9.1 requires *"one room, 12 seats, projector, 12 devices"*
per hub, marked **"⬜ Unconfirmed"**.

**The hub count is the multiplier for three separate plans**: classroom devices (§6.1 row 2),
training facilities (§9.2), and `CH-002`'s whole delivery logistics. At a plausible range of **6 to
12 hubs** the classroom device requirement is **72 to 144 devices** — a 2× spread on a line nobody
has sized.

| # | Rule |
|---|---|
| **`PPP-15`** | **The regional hub count is fixed by Operations before the Wave 1 training schedule is published**, and is recorded in `CH-002` §9 and here. `PPP-Q-01` |

### 6.3 Total cost of ownership of a device, not its price

ISO 55000 principles: a device is an asset with a life cycle, not a line on an invoice.

| Element | Note |
|---|---|
| **Unit price** | The visible part, and the smallest |
| **Mobile device management** | Enrolment, policy, remote wipe. **A `P02` device holds customer data offline for 24 hours** (`NFR-037`), which makes MDM a security control, not a convenience — `SC-004`, `SC-010` |
| **Connectivity** | Data plans for 215–430 field devices, 36 months |
| **Breakage and replacement** | Field devices in a repair-services business. A replacement pool is not optional |
| **Refresh** | A 36-month programme on a 24–36 month device life means **at least one refresh cycle inside the analysis period** |
| **Disposal** | §9 — and 1000FiX is in the e-waste business |
| **Insurance / loss** | Field devices are lost and stolen |

| # | Rule |
|---|---|
| **`PPP-16`** | **A device purchase is approved on its five-year total cost, not its unit price**, and the total is entered as a line in `CO-005`. **`CO-005` §7 currently carries no device line at all**, and §7.5's exclusion list must be extended until it does |
| **`PPP-17`** | **Every device is enrolled in MDM before it leaves the depot.** A `P02` device holding 24 hours of offline customer data without remote wipe is a `SC-003` DPIA finding waiting to be written |

### 6.4 The lead time, and why it is already tight

| Milestone | Date |
|---|---|
| Today | **19 August 2026** |
| Contract signature (RFP §18.1 target) | 16 April 2027 |
| Programme kickoff | 3 May 2027 |
| **Wave 1 gate** | ~September 2027 |
| **Wave 2 — `P02` technician application go-live** | ~Month 8, ≈ January 2028 |
| **First W1 training cohort** — classroom devices needed | **6 weeks before**, per `CH-002` §9.2 |

**Working backwards for the classroom devices**, which are needed **first**:

| Step | Duration |
|---|---:|
| Specify, quote (three, per §4.1), evaluate, approve | 4 – 6 weeks |
| Order to delivery — imported hardware into Bangladesh, including customs clearance | **8 – 16 weeks** |
| MDM enrolment, imaging, Bengali locale configuration, distribution to hubs | 3 – 4 weeks |
| **Total** | **15 – 26 weeks** |

> **Fifteen to twenty-six weeks is three to six months, and the comparator is `GV-007` §8.3's 10–16
> week hiring lead time — which the programme already treats as a critical-path risk.** The devices
> are needed at roughly Month −1.5 relative to kickoff for the first cohort. **The procurement must
> therefore start before the implementation contract is signed**, which means it must be funded from
> Tranche 0 rather than from the implementation contract.
>
> **`PPP-18` — the classroom device procurement is a Tranche 0 activity and starts on charter
> approval, not on contract signature.** Waiting for the implementation partner to be appointed puts
> the first training cohort at risk for no benefit, because the devices are not the partner's to
> supply.

### 6.5 Sourcing options

| Option | Assessment |
|---|---|
| **Buy outright** | Simplest; capital; **the Company owns the disposal obligation**, which §9 argues is an advantage here rather than a cost |
| **Lease / device-as-a-service** | Smooths cash flow and bundles refresh and replacement. **But it puts a third party in the disposal chain**, which conflicts with §9's argument |
| **Bring-your-own-device** | **Rejected.** `RSK-008`'s mitigation is explicitly *"Company-provided devices"*, `NFR-076` sets measured performance on low-end Android, and BYOD makes both untestable. `CH-002` and `QA-*` would be verifying against an unknown device population |
| **Refurbished, through the Company's own `M14` trade-in and refurbishment business** | **Assess seriously.** §9 |

---

## 7. Infrastructure

### 7.1 Cloud and hosting

| # | Rule |
|---|---|
| **`PPP-19`** | Cloud is procured under a **framework agreement with consumption-based drawdown**, not per-resource purchase orders. `PE-003`'s IaC creates and destroys environments continuously (`PE-002` `LC-03`), and a purchase-order-per-resource model would make ephemerality administratively impossible — destroying the $60K–$110K saving `CO-005` §5.2 attributes to it |
| **`PPP-20`** | The framework carries **`PE-006` §8.4's cost controls as contractual reporting**: cost-centre tagging, bounded autoscaling, and **monthly variance > 15% against the wave budget alerting** |
| **`PPP-21`** | **Egress and data-transfer pricing is negotiated explicitly**, not accepted from a rate card. `PE-006` §5.4 makes the `dr` line *"storage- and egress-dominated"*, and egress is where consumption pricing is least predictable and least visible |
| **`PPP-22`** | **Exit terms are negotiated at entry**: data egress cost and duration on termination. `PE-001` `SEL-05` applies to cloud as much as to colocation |

### 7.2 The `BD-R` facility — a selection exercise, not a purchase

`PE-001` §3.5 supplies five selection considerations. They are converted here into a procurement
process, because `SC-007-D-01` makes this a **Wave 1** commitment.

| # | Consideration (`PE-001` §3.5) | How it is assessed |
|:--:|---|---|
| `SEL-01` | **Facility tier and certification** — Tier III minimum, Tier IV preferred; Uptime Institute certification of **operational sustainability**, not merely of design | Certificate verified against the issuing body's register, per `CO-002` §10.3's discipline |
| `SEL-02` | **Carrier neutrality** — a single-carrier facility makes the private link a single point of failure | Carrier list obtained and verified independently of the facility's own claim |
| `SEL-03` | **Right of audit** — for 1000FiX and, under `PE-001` §12, for a counterparty's regulator | A contract term, tested against the provider's standard terms |
| `SEL-04` | **State ownership cuts both ways** — sovereignty alignment versus placing residency-classified data inside government-operated infrastructure. `PE-001` records this as *"a matter for Legal Counsel and the DPO"* | **Legal Counsel and DPO opinion, before shortlisting** — not after |
| `SEL-05` | **Exit** — what it takes to leave, and how long the data takes to move, **before it is entered** | A written exit plan from the provider, as a condition of shortlisting |

| # | Rule |
|---|---|
| **`PPP-23`** | **`BD-R` selection is a two-envelope exercise**: technical and commercial assessed separately, technical first, mirroring `CO-002`'s discipline at a smaller scale. It is a multi-year commitment holding the Company's statutorily-classified data |
| **`PPP-24`** | **No `BD-R` shortlist without the `SEL-04` legal opinion.** Discovering after selection that the DPO objects to a state-operated facility is a re-run of the whole exercise, on the Wave 1 critical path |
| **`PPP-25`** | **The `DEP-31` residency legal opinion is commissioned before, not after, `BD-R` selection.** `SC-007` `Q-01` asks *"does the split-residency design satisfy the PDPA 2026 obligation?"* and the answer sets the field set, which sets `Z4`'s sizing, which sets what is being bought |

### 7.3 Key custody — the disproportionate line

`PE-001` §3.4 and `CO-005` §5.3 both identify **in-country key custody** as the component whose cost
is out of proportion to its size: **$6K–$24K a year**, against $3K–$6K for the compute it protects.

| Option | Assessment |
|---|---|
| **Dedicated HSM in the colocation facility** | Strongest custody story; highest cost; an operational burden the Company has never carried |
| **In-country managed KMS** | Lower cost and lower burden — **if** an in-country provider offers one that satisfies `SC-006` `ES-3` |
| Cloud KMS outside Bangladesh | **Fails the residency requirement.** `SC-006` `ES-3` requires the key material in country |

| # | Rule |
|---|---|
| **`PPP-26`** | **Key custody is procured against `SC-006` `ES-3`'s requirement, not against a price.** It is a **single-source-risk** purchase (ISO 31000 §6.4): if one in-country provider satisfies the requirement, the Company has no negotiating position and should know that before it needs the service. `PPP-Q-04` |

---

## 8. Professional Services

`GV-008` §6.3 creates a **$60K risk budget** held by the Steering Committee, with five named calls.
Four are procurements and have had no route until now.

| # | Purchase | Funded from | Owner | Needed by | Why it cannot wait |
|:--:|---|---|---|---|---|
| 1 | **`DEP-31` — PDPA 2026 residency legal opinion** | Risk budget | Legal Counsel | **Before the W1 architecture freeze** | `SC-007` `Q-01`; sets `Z4`'s field set; `PPP-25` makes it a `BD-R` precondition |
| 2 | **`DEP-29` — marketplace tax and legal opinion** | Risk budget | Legal Counsel with CFO | **Before W7** | Principal versus agent VAT treatment; RFP `OPT-10` prices the alternative. It determines how `M12` settlement is **built**, not only how it is taxed |
| 3 | **Independent assurance** under `GV-010` | Risk budget + `CO-005` §6.3's PMO line | Programme Director | **From the Wave 1 gate** | `GV-009` §6.4 requires the Audit Committee chair to sign from Gate 4 *"that independent assurance was obtained"* |
| 4 | **Penetration testing** under `SC-009` | Risk budget | CISO | **Per wave, from W1** | `DoD-15` requires zero open high or critical findings; `SG-1` is P0 at every gate |
| 5 | **Bangladesh tax opinion** on the contract structure — **added here** | Risk budget | CFO | **Before contract signature** | `CO-005` `TCO-Q-02` and `TCO-Q-03`; `CO-003` §10's VAT and withholding clauses depend on it |

| # | Rule |
|---|---|
| **`PPP-27`** | **A professional-services purchase names the question it must answer and the decision it unblocks**, before it is commissioned. An opinion procured without a stated question produces a survey of the law and no answer |
| **`PPP-28`** | **Independent assurance and penetration testing are procured from parties independent of the implementation partner.** `GV-009` §5.2 and `GV-010` §3.2 both identify the independence problem; buying assurance from the party being assured resolves it in the wrong direction |
| **`PPP-29`** | **The `$60K` risk budget is committed, not merely allocated.** `GV-005` `Q-02` and `GV-008` §6.3 record that **0 of 12 Critical risks have a treatment in progress** *"because there was no money to start one with."* There is now. `GV-008` `CB-03` escalates monthly until each has one |

---

## 9. Sustainable Procurement — `CVA-22`

### 9.1 The consistency problem, stated plainly

1000FiX's Category D business is **e-waste, refurbishment, trade-in and resale** — `M14` (trade-in,
refurbishment, grading, resale), `M18` (e-waste, recycling, **ESG reporting**), and `cd_esg_report`
is a specified deliverable. The Company sells circular-economy services and reports on ESG.

**It has no position on how it buys its own hardware.**

> This is not a compliance failure — ISO 20400 is guidance and there is no certification to fail.
> **It is a credibility exposure**, and the audience that will notice is the one that matters most:
> the **brand partners** and **corporate clients** in `P04` and `P08` whose own procurement
> questionnaires increasingly ask exactly this. `CO-004` §8.3 makes the same argument about the
> open-source supply chain and reaches the same conclusion — the Company is about to be asked
> questions it has not prepared for.

### 9.2 The position

| # | Rule |
|---|---|
| **`PPP-30`** | **Device procurement assesses refurbished supply first**, including from the Company's **own `M14` trade-in and refurbishment operation**, and records why it was not used where it was not |
| **`PPP-31`** | **Every device purchased carries a disposal route through `M18` at end of life**, recorded at purchase, not decided at disposal. The Company operates the disposal capability; using someone else's would be difficult to explain |
| **`PPP-32`** | **Device suppliers are asked about take-back, repairability and material declarations**, and the answers are recorded. Asking costs nothing and changes what suppliers offer over a 36-month programme |
| **`PPP-33`** | **The device estate's carbon and material position is reportable through `cd_esg_report`** — the Company's own module — so that its internal estate appears in the same report as its customers'. This is the cheapest possible demonstration that the ESG reporting is real |

> **`PPP-34` — this section is deliberately modest.** Four rules, all of which cost approximately
> nothing and one of which may save money. A sustainable-procurement programme proportionate to a
> 500-person company is a position and a question set, not a management system, and claiming
> otherwise would be the kind of unearned conformance `PG-06` exists to prevent.

---

## 10. Process

### 10.1 Supplier onboarding

| # | Step | Applies |
|:--:|---|---|
| 1 | Legal entity, registration and **VAT registration (BIN)** verified — the last determines §12's treatment | All |
| 2 | Bank details verified **through an independent channel**, not from the invoice | All |
| 3 | Conflict-of-interest declaration | > $10,000 |
| 4 | Insurance verified where the supplier's failure could cause loss | > $10,000; all facility and professional services |
| 5 | **ISO 27001 or equivalent** where the supplier processes personal data or holds Company data | All Category 1, 2, 3, 4 |
| 6 | **Data Processing Agreement** where personal data is processed | Per `SC-003`; `CO-003` §14's pattern |
| 7 | Sub-processor list, where relevant, checked against `SC-007`'s residency design | Category 1, 2, 3 |

### 10.2 Quotation and single-source

| # | Rule |
|---|---|
| **`PPP-35`** | **Three quotations above $10,000**, or a **written single-source justification** approved by the CFO |
| **`PPP-36`** | Valid single-source grounds are: **only one provider satisfies a stated technical or regulatory requirement** (§7.3's key custody may be one); continuity with an existing platform where switching cost exceeds the benefit; or a genuine emergency under `PPP-07`. **"We have always used them" is not a ground** |
| **`PPP-37`** | **A single-source purchase records the negotiating position the Company does not have**, and what would restore it. This is what turns a single-source note into a useful risk record |

### 10.3 The light route

For Category 7 tooling and subscriptions under $2,000 whole-of-term: requesting lead approves within
an approved budget line, records it in the purchase log, and **confirms it is not a Category 1
purchase in disguise** (`PPP-02`).

### 10.4 Receipt and acceptance

| # | Rule |
|---|---|
| **`PPP-38`** | **Goods are receipted by someone other than the person who ordered them** (`PPP-04`) |
| **`PPP-39`** | **Services are accepted against the stated deliverable**, using the `CO-003` §6.3 pattern at a smaller scale: a submission without evidence does not start the clock |
| **`PPP-40`** | **A professional-services deliverable is accepted only when it answers the `PPP-27` question.** An opinion that surveys the law without answering the question is not accepted, and saying so at acceptance is far cheaper than discovering it at the architecture freeze |
| **`PPP-41`** | **Devices are accepted after MDM enrolment and configuration** (`PPP-17`), not on delivery to the depot |

### 10.5 Supplier performance

| # | Rule |
|---|---|
| **`PPP-42`** | Category 1, 2, 3 and 4 suppliers are **reviewed at every wave gate**, jointly with `CO-004` `LIC-30`'s entitlement consumption review. One review, one meeting, two registers updated |
| **`PPP-43`** | A supplier failure that causes a **`CO-003` §8.2 relief event** is recorded against the supplier, not only against the programme. Otherwise the same supplier is re-selected for the next wave |

---

## 11. Lead Times Against the Wave Plan

**Procurement lead time, not development capacity, is the binding constraint on at least three Wave 1
items.** `GV-007` §8.3 already treats a 10–16 week hiring lead time as a critical-path risk; three
procurement lead times are comparable or longer.

| Item | Lead time | Needed by | **Must start** | Funded from |
|---|---:|---|---|---|
| **Classroom devices** | **15 – 26 weeks** (§6.4) | 6 weeks before the first W1 cohort | **Tranche 0** — on charter approval | T0 |
| **`BD-R` facility selection and provisioning** | **16 – 30 weeks** — legal opinion, two-envelope selection, contract, build, connectivity | **W1** (`SC-007-D-01`) | **Tranche 0** | T0 |
| **In-country key custody** | 8 – 16 weeks; longer if a physical HSM is imported | W1–W2 (`SC-006` `ES-3`, `SC-007` `Q-04`) | Tranche 0 / early T1 | T0 |
| **`DEP-31` residency legal opinion** | 4 – 8 weeks | **Before the W1 architecture freeze** | **Now** | Risk budget |
| **`P02` technician devices** | 15 – 26 weeks | W2 go-live | Early T1 | T1 |
| **Cloud framework agreement** | 4 – 8 weeks | Before `PE-002` §8.2's provisioning sequence starts | Tranche 0 | T0 |
| **Qualified e-signature** | 6 – 12 weeks — accreditation checks and the `L6-05` exit answer | W3 | T1 | T1 |
| **Telephony / CPaaS** | 8 – 16 weeks — carrier interconnect and number portability | W4 | T1 | T1 |

| # | Rule |
|---|---|
| **`PPP-44`** | **Four procurements are Tranche 0 activities and start on charter approval, not on implementation-contract signature.** They are: classroom devices, `BD-R` selection, key custody and the cloud framework. **None of them is the implementation partner's to supply**, so waiting for the partner delays them for no benefit |
| **`PPP-45`** | **Every procurement lead time is a line in `GV-004`'s master schedule**, with the same status as a development dependency. A 26-week lead time that appears in no schedule is discovered at the moment it binds |
| **`PPP-46`** | **A procurement whose lead time exceeds its remaining float is escalated to the Steering Committee immediately**, not at the next gate |

---

## 12. Tax Treatment of Purchases

`CO-005` §6.1 and §6.2 establish the position for the implementation contract. It applies here too,
with two additions specific to goods.

| Purchase type | VAT | Withholding | Note |
|---|---|---|---|
| **Goods imported** — devices, HSM | **Import VAT and duty at clearance** | — | **Customs clearance is inside §6.4's 8–16 week window** and is the most variable part of it |
| Goods bought locally from a VAT-registered supplier | 15%, **Mushak 6.3** required for input rebate | Per the applicable VDS rate | `PPP-47` |
| **Services from a resident supplier** | 15% with Mushak 6.3 | Generally **5%** | |
| **Services from a non-resident supplier** — cloud, SaaS, an offshore legal opinion | **15% on imported services**, withheld by the bank at payment, accounted for on **Mushak 9.1** | **10%** for entities (20% for individuals) on technical and professional services | **This is the case that catches people**: a cloud subscription paid by card is an imported service, and the obligation applies whether or not anyone processes it as one |

| # | Rule |
|---|---|
| **`PPP-47`** | **No payment is released without a valid Mushak 6.3 from a resident supplier.** Input rebate is unavailable without it, and the amount becomes a real cost (`CO-005` §6.1) |
| **`PPP-48`** | **Non-resident software and cloud subscriptions are routed through Procurement, not paid on a corporate card.** A card payment bypasses the withholding and imported-services VAT mechanism entirely, creating an unrecorded liability — and it is how Category 7 tooling most often becomes a compliance problem |
| **`PPP-49`** | **Every purchase order states the tax treatment assumed**, so that a wrong assumption is visible at commitment rather than at the annual return |

---

## 13. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `PPP-Q-01` | **How many regional training hubs are there?** | Operations with Training Lead | **Before the W1 training schedule** | `CVA-20`; §6.1 row 2; §9.2; `CH-002` §9 |
| `PPP-Q-02` | **How many rider (`P09`) and field-auditor (`P11`) devices?** | Operations | W2 | §6.1 rows 3, 4 — quantities that exist in no document |
| `PPP-Q-03` | **Buy, lease, or refurbish** the device estate? | CFO with Operations | **Before the T0 device order** | §6.5; §9.2's `PPP-30` |
| `PPP-Q-04` | **Does an in-country managed KMS exist that satisfies `SC-006` `ES-3`**, or is a physical HSM required? | CISO with Chief Architect | **W1** | §7.3; `CO-005` §5.3's 4× band on that line |
| `PPP-Q-05` | **Which `BD-R` facilities are shortlisted, and has Legal Counsel opined on `SEL-04`?** | CTO with Legal Counsel | **W0–W1** | §7.2; `PPP-24`; the Wave 1 critical path |
| `PPP-Q-06` | **What is the import duty and VAT treatment** of the device estate, and does it change the buy/lease decision? | CFO with a tax adviser | Before the T0 order | §12; §6.5 |
| `PPP-Q-07` | **Is the MinIO replacement commercial?** If so, `PPP-12`'s `L6-04` route applies | Chief Architect with CFO | **W0 — blocking Wave 1** | §5.3; `CO-004` `LIC-Q-01`; `BEA-16` |
| `PPP-Q-08` | **Has the `DEP-31` opinion been commissioned?** | Legal Counsel | **Now** | §8 item 1; `PPP-25`; `SC-007` `Q-01`; the W1 architecture freeze |
| `PPP-Q-09` | Does the device estate get a **line in `CO-005`**, and does `CO-005` §7.5's exclusion list get extended until it does? | CFO | **Before the Board paper** | `CVA-19`; `PPP-16` |

> All nine are escalated to `GV-005` RAID at issue. `PPP-Q-08` and `PPP-Q-05` sit on the Wave 1
> critical path and have the longest lead times; `PPP-Q-01` and `PPP-Q-03` gate a Tranche 0 order.

---

## 14. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `CO-006-D-01` | What this plan covers | L6 components only, as `02-05` §6 implies · **All seven categories** | **All seven** | Four categories of purchase are named across the estate with no owner. A plan covering only the four L6 components would leave the device estate — a Critical-risk mitigation — unowned for a second time | §3; `CVA-19` |
| `CO-006-D-02` | Whether authority is assessed on first invoice or whole term | First invoice, simpler · **Whole-of-term commitment** | **Whole of term** | A $500/month subscription on three years is an $18,000 commitment. `GV-008` `CB-09` already applies this test to the budget | `PPP-03`; several Category 7 purchases move above the CFO threshold |
| `CO-006-D-03` | When device procurement starts | On implementation-contract signature · **On charter approval, from Tranche 0** | **Tranche 0** | The lead time is 15–26 weeks and the devices are **not the implementation partner's to supply**. Waiting delays the first training cohort for no benefit | `PPP-18`, `PPP-44`; four procurements move into T0 |
| `CO-006-D-04` | BYOD for `P02` | Allow BYOD, cheaper · **Company-provided devices** | **Company-provided** | `RSK-008`'s mitigation says so explicitly, `NFR-076` requires measured performance on low-end Android, and BYOD makes both untestable | §6.5; the device estate is a real cost line that `CO-005` must carry |
| `CO-006-D-05` | Whether to take a sustainable-procurement position | Out of scope for a private company · **Four modest rules under ISO 20400 guidance** | **Four rules** | A company whose Category D business is e-waste and ESG reporting will be asked by brand partners and corporate clients how it buys its own hardware | §9; `CVA-22`; `PPP-30`…`PPP-33` |
| `CO-006-D-06` | L6 contract term | Multi-year for discount · **Annual with renewal options** | **Annual, unless a longer term buys a material discount and an exit right** | A three-year term on a component reviewed at every wave gate makes the review decorative | `PPP-10` |
| `CO-006-D-07` | Whether to route non-resident SaaS through Procurement | Allow card payment for small subscriptions · **Route through Procurement** | **Route** | A card payment bypasses imported-services VAT and withholding entirely, creating an unrecorded liability. It is how Category 7 becomes a compliance problem | `PPP-48` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | **Every category of purchase** the estate names has a route and an owner | §3 — seven categories |
| `AC-02` | `02-05` §6's *"CFO approval per L6 component"* has an **implementing instrument** | §5.1 — a seven-step route with evidence per step |
| `AC-03` | **`L6-01`…`L6-05` are each implemented** by a named rule | §5.1, §5.2, `PPP-08`…`PPP-13` |
| `AC-04` | The **device estate** has quantities, a lead time, a cost basis and a start date | §6; and `CVA-19` names what remains unsized |
| `AC-05` | **`BD-R` selection** implements `SEL-01`…`SEL-05` as a process, not a checklist | §7.2 |
| `AC-06` | The **four professional-services purchases** the risk budget funds have owners, dates and stated questions | §8; `PPP-27` |
| `AC-07` | **Lead times are stated against the wave plan**, and those exceeding their float are identified | §11; `PPP-44`, `PPP-45` |
| `AC-08` | An **approval matrix** exists with segregation of duties | §4 |
| `AC-09` | The **tax treatment** of each purchase type is stated, including the non-resident SaaS case | §12 |
| `AC-10` | A **sustainable-procurement position** exists, proportionate and honest about what it is not | §9; `PPP-34` |
| `AC-11` | Every finding raised — `CVA-19` through `CVA-22` — has a dated, owned action | §6, §6.2, §5.4, §9; §13 |
| `AC-12` | The local rule prefix `PPP-nn` was **verified to zero occurrences** workspace-wide before allocation | Header note |

**Definition of done.** This plan is complete when every criterion above is met, `PPP-Q-01`,
`PPP-Q-03`, `PPP-Q-05` and `PPP-Q-08` are answered, the four Tranche 0 procurements have start
dates in `GV-004`'s schedule, and `PGD-000` records `CO-006` as ✅ with a fresh enumeration date.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-05` §6 | The control this plan implements. **Referred for correction on `CVA-21`'s cadence** |
| Upstream | `AR-013` §7, §7.1 | `L6-01`…`L6-05`; the bounded set; `D-18` |
| Upstream | `CO-004` §8.1 | The entitlement register this plan acquires against; `PPP-11` makes a row a precondition to purchase |
| Upstream | `CO-005` §5.2, §5.3, §5.5 | The cost lines this plan commits. **`PPP-16` refers the missing device line back** |
| Upstream | `PE-001` §3.3–§3.5 | `BD-R`'s components and `SEL-01`…`SEL-05` |
| Upstream | `CH-002` §7.1, §9.1 | **Assigns learner devices and the classroom estate to this document** |
| Upstream | `SC-006` `ES-3`, `SC-007` `SC-007-D-01` | Key custody, and why `BD-R` is Wave 1 |
| Upstream | `GV-008` §6.2, §6.3 | The risk budget §8 draws on; the tranche gates `PPP-05` respects |
| Downstream | `GV-004` | `PPP-45` puts every lead time in the master schedule |
| Downstream | `CO-005` | `PPP-16` requires a device line; §7.5's exclusion list is extended until there is one |
| Downstream | `CO-004` | `PPP-11` and `LIC-26`'s approval record; `PPP-42`'s joint supplier and entitlement review |
| Downstream | `CH-002` | §6 and §9.2 fund and schedule what `CH-002` §7.1 marks unfunded |
| Downstream | `GV-005` | Nine open questions; `PPP-29` funds the treatment of Critical risks |
| Lateral | `SC-003`, `SC-009`, `GV-010` | The DPA pattern; penetration testing; independent assurance |
| Lateral | `M14`, `M18`, `cd_esg_report` | §9's refurbished-supply and disposal routes run through the Company's own modules |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` · `./_CATEGORY_OVERVIEW.md` ·
`./CO-002_Vendor_Evaluation_and_Selection_Report.md` ·
`./CO-003_Statement_of_Work_and_Deliverable_Acceptance_Schedule.md` ·
`./CO-004_Licence_and_Open_Source_Compliance_Register.md` ·
`./CO-005_Total_Cost_of_Ownership_Model.md` ·
`../00_Programme_Governance_and_Control/GV-004_Integrated_Programme_Plan_and_Master_Schedule.md` ·
`../00_Programme_Governance_and_Control/GV-005_RAID_Register.md` ·
`../00_Programme_Governance_and_Control/GV-007_Estimation_Model_and_Resource_Plan.md` ·
`../00_Programme_Governance_and_Control/GV-008_Programme_Budget_and_Cost_Baseline.md` ·
`../00_Programme_Governance_and_Control/GV-010_Programme_Assurance_and_Independent_Review_Plan.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md` ·
`../05_Security_Privacy_and_Compliance/SC-006_Cryptography_and_Key_Management_Standard.md` ·
`../05_Security_Privacy_and_Compliance/SC-007_Data_Residency_and_Cross_Border_Transfer_Design.md` ·
`../05_Security_Privacy_and_Compliance/SC-009_Vulnerability_Management_and_Penetration_Test_Plan.md` ·
`../07_Build_Engineering_and_Development_Standards/BE-007_Dependency_Licence_and_SBOM_Management_Standard.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-001_Infrastructure_and_Network_Architecture_Design.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-002_Environment_Strategy_and_Specification.md` ·
`../10_Infrastructure_DevOps_and_Environments/PE-006_Capacity_Plan_and_Performance_Engineering_Baseline.md` ·
`../13_Training_Change_and_Adoption/CH-002_Training_Plan_and_Delivery_Schedule.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` — §6, §8 ·
`../../primary-doc/1000FiX_ERP_System_Comprehensive_RFP.md` — §16.3 `OPT-12`, §20.6

**External standards** *(all verified 2026-08-19)*

| Source | Used for |
|---|---|
| **ISO 21502:2020** §7.14 | §3's routes; §10's administration |
| **ISO 37500:2014** §6 | §10.1's onboarding; §5's L6 route |
| **ISO 9001:2015 §8.4** | §4's evaluation criteria; §10.4's receipt and acceptance; §10.5's supplier performance. **Obligatory** under RFP §19.3 |
| **ISO 20400:2017**, *Sustainable procurement — Guidance* | §9. **Guidance only — there is no conformity assessment**, and none is claimed |
| **ISO/IEC 19770-1:2017** (Edition 3, reviewed and confirmed 2024) | §5's acquisition against `CO-004` §8.1's entitlements |
| **ISO 55000:2024**, asset management principles | §6.3's whole-life device view. Principles only |
| **ISO 31000:2018** §6.4 | §7.3's single-source risk; §11's lead-time risk |
| **CIPS** procurement practice | §4.1's segregation of duties; §10.2's three-quotation rule |
| Bangladesh VAT — imported services at 15% withheld at payment; input rebate requires a valid Mushak 6.3; Mushak 9.1 return | §12; `PPP-47`, `PPP-48` |
| Bangladesh withholding — non-resident technical/professional services **10%** (entities) / 20% (individuals); resident services generally **5%** | §12 |

> Verify every path resolves before issuing. Nine module files carried references to superseded
> filenames until the August 2026 audits corrected them.

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-19 | Head of Procurement, with the CFO and Enterprise Architecture | Initial issue. Implements `02-05` §6's CFO-approval control as a seven-step route, and extends to seven procurement categories. Raises **`CVA-19` (the device estate is unowned — High)**, `CVA-20` (the regional hub count is stated nowhere), `CVA-21` (two L6 review cadences) and `CVA-22` (no sustainable-procurement position in a circular-economy business). Identifies **four Tranche 0 procurements** whose lead times start before implementation-contract signature | Chief Financial Officer |

---

*`CO-006` · Category 14 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
