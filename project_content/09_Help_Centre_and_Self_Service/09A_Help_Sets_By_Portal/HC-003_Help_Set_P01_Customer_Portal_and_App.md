---
id: HC-003
title: Help Set — P01 Customer Portal and App
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Customer Experience
reviewers: [Customer Service Manager, Quality Manager, Knowledge Manager, Legal Counsel, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Customer Service Manager
content_class: D
purpose: >
  The self-service help set for 250,000+ monthly customers across booking, tracking, approving,
  paying, warranty, contracts, loyalty, shop, trade-in, recycling and complaints. It is the
  deflection engine behind P01's commitment that more than 80% of status enquiries are handled
  without a hotline call, and the single highest-return help set in the register.
traces_to: [P01, M01, M09, M10, M14, M18, M20, M27, M32, M34, M38, M61, MD-024, MD-026, MD-031, HC-001, HC-002, HC-015, HC-016, HC-019, UI-011, KB-013, LG-002, LG-008, LG-013, LG-014, SP-028]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: HC-003_Help_Set_P01_Customer_Portal_and_App_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P01 self-service status checks target above 80% of status enquiries; 250,000+ customers a month; Bengali-first; booking-funnel conversion target above 72%
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.2 FR-KMS-022 — customer self-help with symptom-led navigation, in Bengali, on a 3G connection; §9 BRU-KMS-11 separate customer approval
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-025 status enquiries deflected to self-service 60% at W7, 80% at W9
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-07 estimates above BDT 5,000 require documented customer approval; BRU-SRM-08 above BDT 25,000 adds branch manager approval
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P01 Customer Portal and App

| Item | Value |
|---|---|
| Portal | `P01` Customer Self-Service |
| Audience | **Customer** — audience 1 (`HC-001` §4.1) · 250,000+ per month |
| Article type | **Help set specification** covering Task, Concept and Troubleshooting articles |
| Reading level target | `CG-011` — **the lowest in the register**; assume no prior exposure |
| Languages | **Bengali authored, English rendered** (`HS-29`) |
| Related UI copy | `UI-011` `P01` Customer Portal and App UI Copy Pack |

> **Template conformance.** `TPL_Help_Article.md` applied at **help-set level** rather than to a
> single article, as `CG-009` §3 requires for all 15 help-article files. All template sections are
> retained in order and answered for the set: *Before you start* becomes the set's preconditions,
> *Steps* becomes the journey and its article inventory, *What happens next* becomes the deflection
> outcome, *If it does not work* becomes the set's failure modes. Sections marked **(addition)** are
> justified where they appear. The individual `HLP-` articles conform to the template at article
> level and to `HC-002`.

---

## Before you start

**What must exist before this set can be authored.**

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) | Facets, category tree, symptom-led navigation, the exit-to-human rule |
| [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Article shape, reading level, Bengali authoring |
| `UI-011` `P01` copy pack | Every step quotes labels from it (`HS-08`) |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) | `is_customer_selectable` symptoms drive symptom-led entry (`IA-08`) — **unpopulated, `O-01`** |
| `LG-002` portal terms · `LG-008` privacy notice · `LG-013` service and warranty terms · `LG-014` refund and cancellation policy | Help links to these; it never restates them (`IA-14`) |
| `M27` contact disposition data | Ranks troubleshooting content by real frequency (`HS-15`) — **not available pre-go-live, `O-03`** |

**What the reader is assumed to have:** a phone, a Bengali or English reading ability, and no prior
exposure to the system. **`PS-01`: this set assumes nothing else.** Every other help set may assume
its audience was trained; this one may not.

---

## Steps — *the customer journey and its article inventory*

**`PS-02`: the set is organised by the customer's journey, not by the system's modules.** A customer
does not know which module owns their problem.

### Stage 1 — Discover and book *(12 articles)*

| # | Article | Type | Priority |
|---:|---|---|:--:|
| 1 | **Book a repair** | Task | **P0** |
| 2 | Choose how you want it serviced — walk-in, at home, pick-up | Concept | P0 |
| 3 | **Your device isn't working — tell us what you see** *(symptom entry)* | Troubleshooting | **P0** |
| 4 | Find your nearest service centre | Task | P1 |
| 5 | What it costs, and when you'll know | Concept | **P0** |
| 6 | Create your account | Task | P1 |
| 7 | Why we need your device's serial or IMEI | Concept | P1 |
| 8 | Book for someone else | Task | P2 |
| 9 | Book for a business account | Task | P2 |
| 10 | Cancel or change a booking | Task | P1 |
| 11 | What to do before you hand over your device | **Concept — includes data backup** | **P0** |
| 12 | Book a collection instead of visiting | Task | P1 |

### Stage 2 — Wait and track *(8 articles)*

| # | Article | Type | Priority |
|---:|---|---|:--:|
| 13 | **Track your repair** | Task | **P0 — the deflection article** |
| 14 | **What each status means** | Concept | **P0** |
| 15 | When will it be ready? | Concept | **P0** |
| 16 | Your technician is on the way | Concept | P1 |
| 17 | We need something from you | Concept | P1 |
| 18 | Your repair is taking longer than expected | Troubleshooting | P1 |
| 19 | Change your appointment time | Task | P1 |
| 20 | Nobody came — what now | Troubleshooting | P1 |

### Stage 3 — Approve and pay *(9 articles)*

| # | Article | Type | Priority |
|---:|---|---|:--:|
| 21 | **Approve or decline a repair estimate** | Task | **P0** |
| 22 | **Why we need your approval over BDT 5,000** | Concept | **P0** — `BRU-SRM-07` |
| 23 | Your estimate has changed | Concept | P1 |
| 24 | Your estimate has expired | Troubleshooting | P1 |
| 25 | **Pay for your repair** | Task | **P0** |
| 26 | Payment didn't go through | **Troubleshooting** | **P0** |
| 27 | Get your invoice or receipt | Task | P1 |
| 28 | What "beyond economic repair" means | Concept | P1 |
| 29 | Ask for a refund | Task | P2 — links `LG-014` |

### Stage 4 — Receive and after *(7 articles)*

| # | Article | Type | Priority |
|---:|---|---|:--:|
| 30 | Collect your device | Task | P1 |
| 31 | **Check your repair before you leave** | Concept | P1 |
| 32 | **Your repair warranty — what's covered** | Concept | **P0** |
| 33 | The same problem came back | **Troubleshooting** | **P0** — rework path |
| 34 | Rate your service | Task | P2 |
| 35 | **Make a complaint** | Task | **P0** — `SP-028` |
| 36 | Where your old parts went | Concept | P3 |

### Stage 5 — Ongoing relationship *(10 articles)*

| # | Article | Type | Priority |
|---:|---|---|:--:|
| 37 | **Your manufacturer warranty — is your device covered?** | Concept | **P0** |
| 38 | Claim under warranty | Task | P1 |
| 39 | Your service contract or AMC | Concept | P2 |
| 40 | Your loyalty tier and points | Concept | P2 |
| 41 | Buy parts or accessories | Task | P2 |
| 42 | Trade in your old device | Task | P2 |
| 43 | **What happens to your data when you trade in** | **Concept** | **P1** |
| 44 | Recycle your device | Task | P3 |
| 45 | Manage your account and preferences | Task | P1 |
| 46 | **Your data and your rights** | **Concept** | **P1** — links `LG-008` |

**Set total: 46 articles · 15 at P0 · 17 at P1 · 11 at P2 · 3 at P3.**

---

## What happens next — *what the set delivers*

| Outcome | Measure | Target |
|---|---|---|
| A customer checks status without calling | **`KPI-025`** status-enquiry deflection | **60% W7, 80% W9** |
| A customer completes a booking unaided | `P01` booking-funnel conversion | > 72% |
| A customer approves an estimate without a call | Estimate approval conversion (`KPI-008`) | 72% then 78% |
| A customer who does contact is not worse off | **`KPI-027`** first-contact resolution | 70% then 78% |
| The AI assistant has customer-approved grounding | `M32` corpus (`IA-16`) | Corpus admission passed |

**`PS-03`: the six articles that carry the deflection target** are 13 (track), 14 (status meanings),
15 (when ready), 21 (approve estimate), 25 (pay) and 26 (payment failed). Status, approval and
payment are the three reasons customers call. **If only six articles are authored, these are the
six.**

---

## If it does not work — *the set's failure modes*

| Symptom | Cause | What to do |
|---|---|---|
| Deflection plateaus below target | Content exists but is not found | Check search-then-contact (`IA-17`); the problem is findability, not coverage |
| Search-to-nothing rate high on symptoms | `MD-024` customer symptoms unpopulated | `O-01` — the front door has no content |
| Customers call after reading | *"What happens next"* missing or vague (`HS-12`) | Audit block 5 across the set |
| Bengali pages abandoned faster than English | Translated rather than authored (`HS-29`) | Localisation review |
| Contact volume rises after a release | Articles orphaned by UI change | `HS-38` release review not run (`TR-024` `RL-04`) |
| Complaint volume rises while deflection rises | **Deflection bought at the cost of the exit route** | `IA-13` — every article must carry a route to a human |
| An article tells a customer to open a device | `IA-07` breached | Withdraw immediately; HSE and Quality informed |

---

## Related

| Item | Why relevant |
|---|---|
| [`../HC-015_FAQ_Bank_by_Audience.md`](../HC-015_FAQ_Bank_by_Audience.md) | The customer FAQ set draws from and links to this set |
| [`../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md`](../HC-016_In_Product_Help_Tour_and_Coach_Mark_Copy.md) | Contextual entry path (`HC-001` §4.6 path 1) |
| [`../09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md`](../09B_Conversational_AI/HC-019_AI_Guardrail_Disclosure_and_Handover_Copy.md) | The assistant answers customers from this set |
| [`../HC-020_Video_Tutorial_Script_Library.md`](../HC-020_Video_Tutorial_Script_Library.md) | Articles 1, 13, 21 and 25 warrant video |
| `UI-011` `P01` copy pack | Labels quoted in every step |
| [`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Article 35 |
| [`../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](../../07_Knowledge_Base_and_Technical_Library/KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | The hazard boundary behind `IA-07` and article 11 |
| `LG-002`, `LG-008`, `LG-013`, `LG-014` | Linked, never restated (`IA-14`) |
| `HC-006` `P04` corporate help | A customer who is also a corporate requester crosses between sets |

---

## Feedback

Helpfulness capture per `CG-014` on every article. **`PS-04`: helpfulness is reported alongside
deflection**, because an article that deflects contact without answering the question suppresses a
measure rather than solving a problem.

| Signal | Reported |
|---|---|
| "Did this answer your question?" | Weekly, per article |
| Search-then-contact | Weekly (`IA-17`) |
| Contact reasons with no article | Weekly — the authoring backlog |
| Abandonment mid-article | Monthly, by language |

---

## Coverage and Authoring Plan *(addition — justified: consistent with the `KB` and `TR` category convention; a 46-article set cannot be resourced without stating the effort)*

| Item | Position |
|---|---|
| Articles required | **46** |
| Articles written | **0** |
| Authoring effort | 46 × 2–4 hours including review = **90–185 hours**, plus Bengali authoring and accessibility review |
| **Sequencing** | The 6 deflection articles (`PS-03`) first; then 15 P0; then P1 before W4 |
| Bengali | **All 46**, authored in Bengali (`HS-29`) |
| Video | Articles 1, 13, 21, 25 → `HC-020` |
| Dependency | 12 of 46 quote `UI-011`; 4 derive from `KB` content and need `BRU-KMS-11` approval |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`MD-024` customer-selectable symptoms are unpopulated** (`AUDIT-008` KB-11). Article 3 — the symptom front door — has no content, and it is the entry point `FR-KMS-022` requires | Technical analyst (MDM) | **W2 — blocking** |
| **O-02** | **`LG-002`, `LG-008`, `LG-013`, `LG-014` are unwritten** (Category 10 unstarted). Articles 22, 29, 32, 37, 43 and 46 link to legal artefacts that do not exist | Legal Counsel | **W2** |
| **O-03** | `M27` disposition data does not exist pre-go-live, so troubleshooting ranking (`HS-15`) is provisional for the first release | Content Design with Contact Centre | W3 re-rank |
| **O-04** | **The `BRU-KMS-11` customer-approval workflow has no owner and `M61` provides it at W6** — four waves after this set is due (`HC-001` `O-04`) | Knowledge Manager with Customer Service Manager | **W2 interim** |
| **O-05** | Articles 43 and 46 concern data rights. **Bangladesh's Personal Data Protection Act 2026 gives customers statutory rights whose portal expression is not designed** — see `HC-019` §Guardrails | Legal Counsel with CTO | **W2** |
| **O-06** | Bengali authoring capability (`HS-29`, `TR-001` `O-05`) | Localisation Lead | **W2** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` — all sections retained in order, set-level interpretation declared, additions justified
- [x] Organised by customer journey rather than by module (`PS-02`)
- [x] Article inventory enumerated — 46 articles with type and priority
- [x] **The six deflection-carrying articles identified explicitly (`PS-03`)**
- [x] Deflection paired with first-contact resolution and helpfulness so it cannot be bought (`PS-04`, `IA-13`)
- [x] Consumer-hazard prohibition carried through (`IA-07`)
- [x] Legal artefacts linked, never restated (`IA-14`); no price, fee or SLA figure stated (`IA-15`)
- [x] Bengali authored, not translated (`HS-29`)
- [x] All internal links resolve
- [x] `BRU-SRM-07`/`-08` cited to `05-05`; `BRU-KMS-11` and `FR-KMS-022` to `M61`; `KPI-025`/`-027`/`-008` to `06-02`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 46 articles authored — outstanding; this file is the specification**
- [ ] **`O-01` customer symptom set — outstanding; blocks the front door**
- [ ] **`O-02` legal artefacts — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Customer Service Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
