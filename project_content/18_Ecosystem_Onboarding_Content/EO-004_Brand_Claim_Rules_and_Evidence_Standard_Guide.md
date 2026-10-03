---
id: EO-004
title: Brand Claim Rules and Evidence Standard Guide
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Warranty
author: Warranty Officer with Quality and Content Design
reviewers: [Finance Director, Chief Commercial Officer, Quality Manager, Workshop Supervisor, Field Service Manager, Learning & Development Lead, Content Design Lead]
approver: Content Design Lead with Finance Director
content_class: D
purpose: >
  The per-brand claim rule set, the evidence standard every claim must meet, and the rejection
  reasons that actually cause claims to fail — with the specific action that prevents each one.
  The first-submission approval target is above 90%, warranty revenue leakage runs at 15–20% today
  against a target below 2%, and most rejections are evidence defects created at the bench by a
  technician who did not know what the brand required. A rejected claim is unpaid work already
  performed; this guide is the difference between a claim pack assembled correctly once and the
  same pack assembled three times.
traces_to: [P08, M09, M22, M23, M24, M15, M17, 04-00 P08, FR-WTY-052, FR-WTY-053, FR-WTY-054, FR-WTY-055, FR-WTY-056, FR-WTY-057, FR-WTY-058, FR-WTY-059, FR-WTY-060, FR-WTY-061, BRU-SRM-09, BRU-PCM-08, KPI-037, KPI-038, KPI-039, KPI-040, KPI-041, KPI-063, G4-01, G4-02, MD-011, MD-017, MD-021, MD-022, MD-024, MD-025, MD-026, MD-029, MD-031, DT-033, SP-014, SP-010, SP-029, UI-018, UI-033, HC-010, NT-013, TR-019, KB-016, EO-003, EO-011, EO-014]
priority: P1
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P08 Evidence capability "view photographs, diagnostic reports, parts replaced, technician certification and purchase proof for any claim"; KPI "claim approval rate > 92%", "average claim decision time < 10 days", "days from service to reimbursement < 45"
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M09_Warranty_Protection_Plans_and_Claims.md §5.5 FR-WTY-052…061 — claim receivable, remittance matching, period reconciliation, write-off governance, consignment parts governance, defective part return linked to claim payability, old-part retention and destruction rules with evidence, recall and campaign execution, campaign claim treatment, brand partner performance measured on decision time, approval rate, rejection reasons, payment time and short payments
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §2.5 — KPI-037 claims submitted within 72 hours (baseline ~50% at 30–90 days), KPI-038 warranty revenue leakage 15–20% baseline to < 2%, KPI-039 first-submission approval rate 90% at W4 and 92% at W8, KPI-040 days from service to reimbursement 60–120 baseline to < 45, KPI-041 claims with complete evidence at submission 96% at W4 and 98% at W8; §2.8 KPI-063 claims rejected for uncertified technician — zero; §4 Gate 4 G4-01, G4-02
    verified: 2026-08-18
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md §2 claim_window_days, rate_card_owner, requires_certified_tech, authorised_categories, authorised_models; §4 BRD-02 a claim may not be raised outside agreement dates, BRD-03 certification requirement, BRD-04 model must fall in an authorised category
    verified: 2026-08-18
    class: P1
  - source: ISO 9001:2015 clause 8.5.1 control of production and service provision; 8.5.2 identification and traceability; 7.5.3 control of documented information — the basis on which retained evidence is treated as a record rather than a working file
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Brand Claim Rules and Evidence Standard Guide

| Item | Value |
|---|---|
| Audience | **Internal first** — technicians, workshop supervisors, warranty officers — and brand partners second |
| Population served | 17+ brands · 200–400 technicians · 4–10 Warranty Officers (`R28`) |
| Portal | `P08` for the brand view; `UI-033` Warranty Console for the internal view |
| Language | **English only** (`CG-010` §3.2) — **but see `O-05`; the people who create the evidence read Bengali** |
| Wave | W4 · Months 14–18 |
| KPIs served | `KPI-038` leakage 15–20% → < 2% · `KPI-039` first-submission approval 90% → 92% · `KPI-041` evidence complete 96% → 98% · `KPI-063` uncertified-technician rejections **zero** |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3), all
> six sections in order. The `EO` additions are applied to the claim rather than to a person:
> §4.2 is the **journey** an evidence pack travels from bench to reimbursement, §4.4 is the
> **checklist**, and §4.8 is the **first 90 days** of rejection-reason feedback. The adaptation is
> declared because this is the one `EO` file whose primary audience is internal.

---

## 1. Purpose

`KPI-038` says the quiet part out loud: **warranty revenue leakage is running at 15–20%.** One
pound in six of work already performed under a brand authorisation is not being recovered from the
brand that authorised it. The target is under 2%.

Leakage has three causes, and only one of them is commercial:

| Cause | Share this guide addresses |
|---|---|
| Claims never raised — the job was warranty and nobody classified it as such | Partly — §4.3 |
| **Claims raised and rejected** — the evidence did not meet the brand's requirement | **Directly. This is the guide's subject** |
| Claims raised, approved and never paid | Not here — `EO-003` §4.5 reconciliation |

`KPI-039` targets **90% first-submission approval** at W4. The Master Index states the case in one
line: *"most rejections are evidence defects that a standard guide prevents."* An evidence defect
is created at the bench, minutes after the repair, by a technician who did not know that this
brand requires the serial plate in the same frame as the fault, or that the old part must be
retained for 90 days, or that a photograph taken after the casing was refitted proves nothing.

**The guide is therefore written for the technician first and the brand second.** A brand-facing
document that the people creating the evidence never read cannot move `KPI-041`.

---

## 2. Scope

**In scope.** The universal evidence standard applying to every brand claim; the per-brand rule
matrix and how each brand's variations are recorded; the evidence artefacts, with what each one
must show and the three ways each is commonly wrong; the claim window and its consequences;
certification gating; parts, provenance and purchase proof; old-part retention and defective
return; the rejection-reason taxonomy with the preventive action for each; part-approval and
resubmission; recall and campaign claims; and the feedback loop from rejection reasons back into
practice and training.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Portal access, contacts, transition and reconciliation | **`EO-003`** |
| Portal terms and confidentiality | `LG-005` |
| The internal claim submission and reconciliation procedure, step by step | `SP-014` |
| The claim submission document layout | `DT-033` |
| Reimbursement rates and rate cards | `MD-029`; change communication `EO-011` |
| Warranty types, coverage terms and exclusions as data | `MD-031` |
| Fault, symptom, diagnostic and resolution code values | `MD-024`, `MD-025` |
| Rejection **reason-code values** in the system | `MD-026`; this guide states what each reason *means and how to avoid it* |
| Workshop repair procedure | `SP-010` |
| Technical repair knowledge | `KB-016` and the `KB` library |
| Nonconformity and CAPA where a rejection reveals a process defect | `M23`, `SP-029` |
| Technician training delivery | `TR-019` and the `TR` course packs |

---

## 3. Audience

| Reader | Uses it for | Where they read it |
|---|---|---|
| **Field technician / workshop technician** | What to photograph, in what state, before reassembly | `P02`, at the bench — **in Bengali, `O-05`** |
| **Workshop supervisor** | Checking a pack before it leaves the bench | `P03` Workshop Console |
| **Warranty Officer (`R28`)** | Assembling, submitting, and diagnosing a rejection | `UI-033` Warranty Console |
| **Warranty Manager / Finance Director** | Leakage analysis and brand-level rejection patterns | Reports |
| **Brand warranty contact** | Confirming that what 1000FiX believes the rules are, is what they are | `P08` |
| **L&D (`TR-019`, `TR` packs)** | The source of the practical assessment on evidence capture | Course design |
| **Quality Manager (`R32`)** | Where a rejection pattern becomes a nonconformity | `M23` |

---

## 4. Content

### 4.1 The universal standard — what every claim must show

Nine assertions. A claim pack exists to prove them; a rejection is almost always a failure to
prove one.

| # | The claim asserts | Proved by |
|---|---|---|
| 1 | **This device** — identified beyond doubt | Serial / IMEI capture, legible, matched to `MD-021` model and to the registered asset (`M17`) |
| 2 | **Is covered** — by this brand, on this date, in an authorised category | `MD-017` `authorised_categories` / `authorised_models`, agreement dates (`BRD-02`, `BRD-04`), warranty term (`MD-031`) |
| 3 | **Was bought** — where the brand requires proof of purchase | Purchase proof per the brand's rule (§4.5) |
| 4 | **Failed in this way** — a real, in-warranty fault | Diagnostic record; fault code (`MD-024`); **before** evidence |
| 5 | **Not excluded** — not physical damage, liquid, unauthorised repair, or an excluded cause | Evidence showing the excluded causes are absent, not merely unmentioned |
| 6 | **Was repaired by an authorised person** | Technician certification where `requires_certified_tech` is true (`BRD-03`, `BRU-SRM-09`) |
| 7 | **With these parts** | Part numbers against `MD-022`; provenance; consignment or purchased origin |
| 8 | **To this standard** | Resolution code (`MD-025`); QC checklist; **after** evidence; test results |
| 9 | **At this cost** | Labour and parts at the applicable rate card (`MD-029`, `MD-017` `rate_card_owner`) |

> **Assertion 5 is the one technicians under-serve.** A brand rejects for "physical damage" not
> because damage was found but because the evidence does not exclude it. A wide shot of an intact
> casing takes four seconds and closes the commonest rejection reason in the taxonomy.

### 4.2 The evidence journey

| Stage | Who | What is created | Where it can go wrong |
|---|---|---|---|
| **Intake** | Front desk / field (`SP-007`, `SP-008`) | Serial capture, customer-reported fault, purchase proof, device condition on receipt | Serial transcribed rather than photographed; no condition-on-receipt shot |
| **Diagnosis** | Technician | Fault code, diagnostic record, **before** photographs | Photographs taken after disassembly began |
| **Authorisation check** | System / `R28` | Coverage, category, dates, certification | Bypassed under time pressure; caught later as a rejection |
| **Repair** | Technician (`SP-010`) | Parts consumed, in-progress evidence where the brand requires it, old part retained | Old part discarded — **unrecoverable** |
| **Completion** | Technician | **After** photographs, test results, QC checklist, resolution code, customer sign-off | Casing refitted before the after shot |
| **Assembly** | `R28` | The pack, against **this brand's** §4.3 rules | Assembled against the wrong brand's rules |
| **Submission** | System | Claim submitted **within 72 hours** (`G4-01`, `KPI-037`) | Late submission; `claim_window_days` breached |
| **Decision** | Brand | Approve / part-approve / reject / request information | — |
| **Rejection handling** | `R28` | Reason recorded against `MD-026`; corrected and resubmitted where possible | Reason recorded as free text — **the feedback loop dies here** (§4.8) |
| **Reimbursement** | Finance | Receivable, remittance, reconciliation | `EO-003` §4.5 |

### 4.3 The per-brand rule matrix

**Brands differ, and the differences are where claims die.** This guide holds one matrix row per
brand, populated from `MD-017` and from the rules capture at `EO-003` stage 3.

| Field | Source | Why it changes the pack |
|---|---|---|
| `claim_window_days` | `MD-017` | Days from service to submission. **A claim outside it is unrecoverable, not merely late** |
| `authorised_categories` / `authorised_models` | `MD-017` | A model outside the authorised category cannot be claimed (`BRD-04`) |
| `requires_certified_tech` | `MD-017` | Determines whether the job may be allocated at all; `KPI-063` targets zero rejections on this ground |
| `rate_card_owner` and `rate_card_code` | `MD-017` → `MD-029` | Whether the brand, 1000FiX or negotiation sets labour and parts values |
| `consignment_parts` | `MD-017` | Whether parts come from brand consignment stock, changing the parts evidence entirely |
| Purchase-proof requirement | Rules capture | Some brands accept serial-based coverage lookup; some require the retail invoice |
| Old-part retention period and destination | Rules capture, `FR-WTY-058` | Retention with evidence, or return to the brand |
| Defective-part return requirement | Rules capture, `FR-WTY-057` | **Linked to claim payability** — no return, no payment |
| Photograph specification | Rules capture | Count, angles, whether serial-in-frame is required, whether in-progress shots are required |
| Diagnostic report format | Rules capture | Some brands accept the 1000FiX report; some require their own tool's output |
| Accepted rejection reasons | Rules capture → `MD-026` | The reason set the brand actually uses — the basis of §4.7 |
| Resubmission rules | Rules capture | Whether a corrected claim may be resubmitted, and how often |
| Campaign and recall rules | `FR-WTY-060` | Campaign claims carry distinct rules, rates and reporting |

> **The matrix is empty today.** `MD-017` holds no brand rows until brand master data is loaded,
> and the rules capture happens at `EO-003` stage 3 — **which is the same wave as this file.**
> Recorded as `O-01`.

### 4.4 The evidence checklist

Universal minimum. Brand-specific additions come from §4.3.

| # | Artefact | Must show | Three ways it is commonly wrong |
|---|---|---|---|
| 1 | **Serial / IMEI** | The identifier, legible, on the device | Typed not photographed · glare · a label photographed detached from the device |
| 2 | **Device condition on receipt** | The whole device, all faces | Only the faulty area · after cleaning · after the customer's own attempted repair was concealed |
| 3 | **Before — fault evidence** | The fault itself, in situ | Taken after disassembly · out of focus · no scale or context |
| 4 | **Diagnostic record** | The test performed and its result | A conclusion with no test · a symptom restated as a diagnosis · the brand's own tool not used where required |
| 5 | **Exclusion evidence** | That excluded causes are absent | Omitted entirely · a shot too close to show liquid or impact · internal shot missing on a liquid-exclusion brand |
| 6 | **Technician identity and certification** | Who did the work and their authorisation | Certification lapsed on the service date · a certified technician named but an uncertified one performed the work |
| 7 | **Parts consumed** | Part number, quantity, origin | A description instead of a part number · consignment part not identified as consignment · non-genuine part used |
| 8 | **Purchase proof** | Where the brand requires it | Illegible receipt · a receipt for a different unit · outside the warranty term |
| 9 | **Old part** | Retained or returned per §4.3 | **Discarded.** No recovery is possible · returned without a tracking reference |
| 10 | **After — repair evidence** | The repair, before reassembly | **Taken after the casing was refitted** · same angle as the before shot but nothing visibly changed |
| 11 | **Test results** | The device working, against the fault | A power-on shot standing in for a functional test |
| 12 | **QC checklist** | Completed, against the job type | Ticked in bulk · not the checklist for this job type |
| 13 | **Customer sign-off** | Acceptance of the completed repair | Missing · signed before completion |

**`KPI-041` targets 96% of claims with complete evidence at submission at W4.** Thirteen artefacts
at 96% completeness means roughly one claim in twenty-five is short of something — which is the
level at which a rejection is an exception rather than a routine.

### 4.5 Parts, provenance and consignment

| Situation | Evidence required | Rule |
|---|---|---|
| Part from 1000FiX stock | Part number, batch or serial where tracked, issue record | `M15` |
| Part from **brand consignment** stock | Consumption reported against the consignment record; replenishment requested | `FR-WTY-056`; terms in `M42` `FR-SRM2-024` |
| Part purchased for the job | Purchase proof and provenance grade | `MD-022` |
| **Non-genuine part** | **Not claimable, and a quality event** | A counterfeit finding suspends the listing or supplier and opens an investigation |
| Old part retained | Retention evidence, location, retention period | `FR-WTY-058` |
| Old part returned to brand | Return tracking; **claim payability depends on it** | `FR-WTY-057` |

### 4.6 Timing, and the two windows that are not the same

Confused more often than any other rule in this guide:

| Window | What it measures | Consequence of breach |
|---|---|---|
| **72 hours** | Service completion → claim submission. A 1000FiX internal target (`G4-01`, `KPI-037`; baseline ~50% at 30–90 days) | Internal performance; the claim is still submissible |
| **`claim_window_days`** | Service date → the brand's deadline for receiving the claim. **Per brand**, from `MD-017` | **The claim is refused. The work is unrecoverable** |

The 72-hour target exists to protect the second window with a wide margin. A brand with a 30-day
window forgives a slow week; a brand with a 7-day window does not, and the guide flags those
brands explicitly in the §4.3 matrix.

### 4.7 Rejection reasons, and the action that prevents each

The taxonomy below is the guide's operative content. **Reason values live in `MD-026`**; what each
one means and how to prevent it lives here.

| Rejection reason | What the brand is actually saying | Preventive action | Prevented at |
|---|---|---|---|
| **Outside claim window** | It arrived after our deadline | Submit within 72 h; flag short-window brands at intake | Intake / submission |
| **Not covered — model** | This model is not in your authorised category | Coverage check at intake, not at claim assembly (`BRD-04`) | Intake |
| **Not covered — date** | Service fell outside the agreement or warranty term | Automated check (`BRD-02`); `MD-031` term lookup | Intake |
| **No proof of purchase** | We require the retail invoice | Capture at intake for brands that require it — **it cannot be obtained later** | Intake |
| **Uncertified technician** | The person who repaired it is not authorised on our brand | Allocation-time gate (`BRU-SRM-09`). **`KPI-063` targets zero. Any occurrence is a control failure, not a claim failure** | Allocation |
| **Physical damage / liquid / excluded cause** | Your evidence does not exclude it | Assertion 5 evidence: wide shots, internal shot on liquid-exclusion brands | Diagnosis |
| **Insufficient diagnostic evidence** | You told us the conclusion, not the test | Diagnostic record with the test and its result; brand's own tool where required | Diagnosis |
| **Before/after inadequate** | We cannot see what changed | After shot **before reassembly**; matched angles that show a difference | Completion |
| **Part not approved / not genuine** | That part is not one we reimburse | Part number against `MD-022`; provenance declared | Repair |
| **Old part not returned / not retained** | We require the part | §4.5; retention is a physical act nobody can retrofit | Repair |
| **Duplicate claim** | We have already paid for this | Claim-to-job uniqueness; check before resubmission | Assembly |
| **Rate not agreed** | You have billed outside the rate card | `MD-029` at the version effective on the service date | Assembly |
| **Repeat repair within period** | This is rework, not a new failure | Rework detection and routing (`M01`); claim it as rework where the brand permits | Assembly |
| **Insufficient information** | Not a rejection — a request | Answer within the brand's window; this outcome preserves the claim | Assembly |

**Two rejection reasons are control failures rather than evidence failures** — *uncertified
technician* and *duplicate claim*. Both are hard-blockable in the system, and both appearing in a
rejection report means a block is not operating. They are routed to `M23` as nonconformities, not
back to the technician.

### 4.8 The first 90 days of rejection-reason feedback

A guide written once and never corrected by outcome is a guess with a version number. `FR-WTY-061`
measures each brand on *"decision time, approval rate, rejection reasons, payment time and short
payments"*; this section makes the rejection-reason half of that a loop.

| Days | What happens | Output |
|---|---|---|
| **0–30** | Every rejection coded against `MD-026` — **no free text** | A first distribution of reasons per brand |
| **31–60** | The top three reasons per brand are traced to their §4.7 prevention point | Whether the cause is intake, diagnosis, repair, allocation or assembly |
| **61–90** | Prevention actions issued where the cause is practice; nonconformities raised where the cause is a control | Guide revision; `TR-019` and `TR` pack updates; `M23` items |
| **Thereafter** | Monthly per brand; quarterly across brands | `KPI-039` movement attributable to a named cause |

**The loop's single point of failure is the coded reason.** A rejection recorded as free text
cannot be counted, and a reason distribution that cannot be counted cannot direct a prevention
action. `BC-06` makes coding mandatory.

### 4.9 Rules

| # | Rule |
|---|---|
| **BC-01** | The universal standard (§4.1) applies to every brand. Per-brand rules **add**; they never subtract |
| **BC-02** | A per-brand rule is recorded in the §4.3 matrix from `MD-017` or the `EO-003` stage-3 capture. **A rule known only to one Warranty Officer is not a rule** |
| **BC-03** | Evidence is captured **in the order of §4.2** and never reconstructed. A photograph taken after reassembly is not an after shot |
| **BC-04** | The old part is retained or returned per §4.3 **before** the job is closed. This is the only evidence item that cannot be recovered later |
| **BC-05** | Coverage, category and certification are checked **at intake and allocation**, not at claim assembly (`BRD-02`, `BRD-03`, `BRD-04`, `BRU-SRM-09`) |
| **BC-06** | **Every rejection is coded against `MD-026`. Free-text rejection reasons are not accepted into the record** — they break §4.8 |
| **BC-07** | *Uncertified technician* and *duplicate claim* rejections are raised as nonconformities in `M23`, not returned to the technician as coaching |
| **BC-08** | No rate, reimbursement value or commercial term appears in this guide. `MD-029` holds them at the version effective on the **service date**, not the submission date |
| **BC-09** | A short-window brand is flagged at intake, so the window is protected at the point the job starts, not at the point the claim is assembled |
| **BC-10** | *Insufficient information* is treated as a live claim with a deadline, never as a rejection to be triaged later |
| **BC-11** | Where a rejection reveals that 1000FiX's understanding of a brand rule is wrong, the §4.3 matrix is corrected **and the brand confirms the correction in writing** (`EO-003` §4.6 level 2) |
| **BC-12** | Campaign and recall claims follow `FR-WTY-060` rules and are never assembled against the standard claim rules |
| **BC-13** | The guide is written for the bench. Any instruction a technician cannot execute in under a minute at the bench is a specification defect, not a technician failure |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| [`MD-017`](../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Every per-brand field in §4.3; `BRD-02`, `BRD-03`, `BRD-04` |
| [`EO-003`](EO-003_Brand_Partner_Onboarding_Pack.md) | The stage-3 rules capture that populates §4.3, and the escalation route in `BC-11` |
| [`MD-026`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-026_Reason_Code_Register.md) | Rejection reason codes — **§4.8 fails without them** |
| [`MD-022`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md), [`MD-024`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md), [`MD-025`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md), `MD-031`, `MD-011`, `MD-021` | Parts, fault codes, resolution codes, warranty terms, certifications, models |
| [`MD-029`](../02_Master_Data_and_Configuration/02D_Commercial_and_Pricing/MD-029_Price_List_and_Rate_Card_Seed.md) | Rate cards, effective-dated on the service date (`CG-006` §3.4) |
| `M09` §5.5 | Reconciliation, consignment, defective return, retention, campaign |
| `M22` | Certification currency behind `BRU-SRM-09` and `KPI-063` |
| `M23`, [`SP-029`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Where a control-failure rejection becomes a nonconformity |
| [`SP-014`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) | The internal claim procedure; §4.2 must reconcile with it |
| [`SP-007`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-007_SOP_Walk_In_Intake_and_Front_Desk.md), [`SP-008`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md), [`SP-010`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | Where the evidence is actually created |
| [`DT-033`](../05_Document_and_Print_Templates/05D_Commercial_and_Contract/DT-033_Warranty_Claim_Evidence_Pack.md) | The claim submission document |
| [`UI-033`](../03_UI_Copy_and_Microcopy/03C_Admin_Workspaces/UI-033_Workspace_Warranty_Console_Copy.md), [`UI-018`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-018_P08_Brand_Partner_Portal_UI_Copy_Pack.md), [`HC-010`](../09_Help_Centre_and_Self_Service/09A_Help_Sets_By_Portal/HC-010_Help_Set_P08_Brand_Partner_Portal.md), `NT-013` | Internal console, brand portal, help and notices |
| [`TR-019`](../08_Training_and_Enablement/08B_Course_Packs/TR-019_Course_Pack_Marketplace_and_Seller_Operations.md) and the `TR` technician packs | Where §4.4 becomes a practical assessment |
| [`KB-016`](../07_Knowledge_Base_and_Technical_Library/KB-016_Technician_Field_Reference_Card_Set.md) | Technical repair knowledge; this guide is evidence, not repair method |

> **Rule-citation attribution.** **BRU-PCM-\***  → `M40` §9 — these are **module-scoped** rule families and **`05-05` carries none of them**. The families this file cites that **do** resolve in `05-05` are `BRU-SRM-*`. Stated per `AUDIT-015` R-11, which asked that the convention be recorded once rather than rediscovered by each extraction.

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Monthly per brand for the first 90 days** (§4.8), then quarterly; the universal standard annually |
| Trigger for out-of-cycle review | A brand changing a claim rule, window, evidence requirement or rate card; a new brand onboarded; a rejection reason appearing that §4.7 does not list; a `KPI-039` fall of more than 3 points; a recall or campaign; a change to `MD-026` |
| Owner | Warranty Officer (`R28`), with the Quality Manager for the nonconformity routes |
| Change control | The per-brand matrix changes on written brand confirmation only (`BC-11`); the universal standard changes with Finance Director sign-off |
| Effectiveness measure | `KPI-039` first-submission approval and `KPI-041` evidence completeness, **decomposed by rejection reason** — an aggregate that improves while one reason worsens is not an improvement |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The §4.3 per-brand matrix is empty and its two inputs both arrive in the same wave as this file.** `MD-017` holds no brand rows until brand master data is loaded, and the rules capture is `EO-003` stage 3 — also W4. **A guide whose operative content is a matrix with no rows cannot yet prevent a rejection**, and `KPI-039`'s 90% target is set at W4 | Warranty Officer with Commercial and the Master Data Owner | **W4 — the matrix must precede the first portal claim** |
| **O-02** | **`KPI-038`'s 15–20% leakage baseline has no decomposition.** The target is under 2% and this guide addresses one of three causes (§1). **Nothing in the repository states how the 15–20% splits between claims never raised, claims rejected and claims unpaid**, so no one can say what share this file can move. A guide accountable for an undecomposed number is accountable for everything and measurable on nothing | Finance Director with BI Lead | **W4 — before `KPI-038` is reported against** |
| **O-03** | **Old-part retention has a physical requirement with no operational owner.** `FR-WTY-058` requires brand-specific retention and destruction with evidence; `BC-04` makes it the one unrecoverable artefact. **No storage location, retention register, capacity or destruction procedure is specified in any `SP`, `MD` or `OP` file**, across 51+ branches and a workshop network. `MD-004` holds storage locations and none is designated for retained warranty parts | Supply Chain Director with Warranty Officer | **W4 — before the first retention-required brand goes live** |
| **O-04** | **`KPI-063` targets zero uncertified-technician rejections and the gate is at allocation, in `M02` dispatch.** `BRU-SRM-09` is cited across the warranty content and **`05-05` does not carry a `BRU-SRM-09`** — the `SRM` prefix belongs to `M01` (`02-02` §code note), and the rule as used here is a *dispatch* constraint. The identifier needs resolving to its owning module before this guide cites it in training | Enterprise Architecture with Quality Manager | **W4** |
| **O-05** | **The primary audience reads Bengali and this file is English-only.** `CG-010` §3.2 classes `EO` brand material as English because brand partners are international. **That rationale does not survive §3 of this file**: the technicians and supervisors who create every artefact in §4.4 are the 200–400 Bengali-reading field and workshop staff `CG-010` §3.3 explicitly answers "**Yes**" for. Either this file is bilingual — taking `EO` to 9/5 and breaking the `CG-010` allocation — **or §4.4 must be re-issued inside `TR-019` and the `TR` technician packs, which are bilingual**. The second is the cheaper answer and is not yet agreed | Localisation Lead with L&D Lead and Programme Content Lead | **W4 — before technician training is built** |
| **O-06** | **Resubmission rules are unstated for every brand.** §4.3 lists the field; `M09` §5.5 has no resubmission requirement; `04-00` P08 offers "request more information" as a brand action but no resubmission cycle. **Whether a corrected claim may be resubmitted, how often, and whether resubmission restarts `claim_window_days`, is undefined** — and it is the difference between a recoverable rejection and a written-off one | Warranty Officer with Commercial | **W4 — before the first rejection** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; the `EO` additions applied to the claim and the adaptation declared
- [x] **`KPI-038`'s 15–20% leakage stated, and the guide's share of it scoped honestly to one of three causes**
- [x] Nine universal assertions stated, with the artefact that proves each
- [x] Evidence journey mapped stage by stage with the failure at each stage
- [x] Per-brand rule matrix specified field by field, each traced to `MD-017` or the `EO-003` capture
- [x] Thirteen-artefact checklist with **three specific failure modes each** — the guide's most usable content
- [x] The 72-hour target and `claim_window_days` distinguished, with the consequence of each breach
- [x] Fourteen rejection reasons with the preventive action and the stage it is prevented at
- [x] **Two rejection reasons identified as control failures and routed to `M23` rather than to the technician**
- [x] First-90-days rejection-reason feedback loop, with the coded-reason single point of failure named
- [x] Thirteen rules, including the bench-executability test
- [x] All internal links resolve
- [x] Six open items recorded
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` per-brand matrix empty — outstanding; the guide's operative content has no rows**
- [ ] **`O-03` old-part retention has no location, register or destruction procedure — outstanding**
- [ ] **`O-05` the audience that creates the evidence cannot read the file — outstanding; a `CG-010` allocation decision**
- [ ] **`O-06` resubmission rules undefined for every brand — outstanding**
- [ ] Named approver recorded — **pending Content Design Lead with Finance Director**
- [ ] Bengali counterpart — n/a per `CG-010` §3.2, **contested by `O-05`**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
