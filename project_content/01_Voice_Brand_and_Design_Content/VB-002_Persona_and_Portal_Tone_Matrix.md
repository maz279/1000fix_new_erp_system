---
id: VB-002
title: Persona and Portal Tone Matrix
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Localisation Lead, Business Owners Forum, Brand, portal owners P01–P12]
approver: Content Design Lead
content_class: E
purpose: >
  Calibrates tone for each of the eleven audiences the ERP serves across twelve surfaces. A
  technician working offline in the field and a CFO reading a board dashboard need different
  registers of the same voice; writing both to one calibration makes one of them wrong.
traces_to: [04-00 §2, 04-00 §P01-P12, VB-001, 05-04, CG-010]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: VB-002_Persona_and_Portal_Tone_Matrix_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview — users, volumes, technology, wave per portal
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01–§P12 capability sets, design requirements and KPI tables
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04 §1 role register R01–R38 with headcounts and portals
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# VB-002 — Persona and Portal Tone Matrix

> **One voice (`VB-001`), eleven calibrations.** Tone is not a different personality per
> audience; it is the same four principles weighted for the reader's situation — how much time
> they have, what is at stake for them, what device they hold, and whether they chose to be here.

---

## 1. Purpose

Twelve portals serve eleven distinct audiences with volumes ranging from **25 executives** to
**250,000+ customers a month**. Writing them all to one tone produces content that is too terse
for a first-time customer and too verbose for a rider mid-delivery.

This file gives every author a per-surface calibration they can apply without re-deriving it.

---

## 2. Scope

**In scope:** tone calibration for all twelve portals and the eleven audience types behind them.

**Out of scope:** voice itself (`VB-001`), mechanics (`CG-003`), terminology (`CG-004`),
component copy (`VB-006`), the actual strings (`UI-011`…`UI-022`).

---

## 3. The calibration dimensions

Every audience is placed on six dimensions. The combination determines tone.

| Dimension | Range | What it changes |
|---|---|---|
| **Time pressure** | Reflective ←→ Urgent | Length. Urgent readers get fewer words and the action first |
| **Stake** | Low ←→ High | Explicitness. High stake means stating consequences in full |
| **Expertise** | Novice ←→ Expert | Jargon budget. Experts want the technical term; novices need the plain one |
| **Choice** | Chose to be here ←→ Required to be here | Warmth. A required user does not need persuading, only enabling |
| **Device** | Desk ←→ One-handed mobile | Line length, chunking, scan pattern |
| **Language** | English-comfortable ←→ Bengali-first | Which language is authored first, and how much English is tolerable |

---

## 4. The matrix

### 4.1 Audience placement

| Audience | Portal | Volume | Time | Stake | Expertise | Choice | Device | Language |
|---|---|---:|---|---|---|---|---|---|
| **Customer** | `P01` | 250,000+/mo | Mixed | **High** | Novice | Chose | Mobile | **Bengali-first** |
| **Field technician** | `P02` | 200–400 | **Urgent** | Medium | Expert | Required | **One-handed mobile** | **Bengali, complete** |
| **Branch / back-office staff** | `P03` | 150–250 | **Urgent** | Medium | Trained | Required | Desk, 1366×768 | Bengali + English |
| **Corporate admin** | `P04` | 500–2,000 | Reflective | **High** | Trained | Required | Desk | English-comfortable |
| **Vendor / supplier** | `P05` | 200–500 | Reflective | Medium | Trained | Required | Desk | English |
| **Executive / manager** | `P06` | 25–60 | Reflective | **High** | Expert | Chose | Desk + mobile | English |
| **Marketplace seller** | `P07` | 500–2,000 | Mixed | **High** | Mixed | Chose | Mobile | **Bengali-first** |
| **Brand partner** | `P08` | 50–150 | Reflective | Medium | Expert | Required | Desk | English |
| **Rider** | `P09` | 50–200 | **Urgent** | Medium | Novice | Required | **One-handed mobile** | **Bengali** |
| **Contact centre agent** | `P10` | 30–80 | **Urgent** | Medium | Trained | Required | Desk, dual screen | Bengali + English |
| **Quality auditor** | `P11` | 20–60 | Reflective | Medium | Expert | Required | Tablet, offline | Bengali + English |
| **Referral partner** | `P12` | 100–500 | Reflective | Medium | Novice | Chose | Mobile + desk | Bengali + English |

### 4.2 Tone prescription

| Audience | Sentence budget | Jargon | Warmth | Explains consequences | Reads aloud |
|---|---|---|---|---|:--:|
| **Customer** | ≤ 20 words | **None** — plain terms only | Warm, plain | **Always, in full** | Sometimes |
| **Field technician** | ≤ 12 words | Full technical vocabulary | Neutral, respectful | Only where safety or cost | No |
| **Branch staff** | ≤ 15 words | Full operational vocabulary | Neutral | Where irreversible | No |
| **Corporate admin** | ≤ 25 words | Business vocabulary; no repair jargon | Professional | **Always** — they answer to their own management | No |
| **Vendor** | ≤ 20 words | Procurement vocabulary | Professional, plain | Where money or rejection | No |
| **Executive** | ≤ 15 words | Metric vocabulary, precisely | Neutral | Where the number could mislead | No |
| **Seller** | ≤ 18 words | Minimal — mixed literacy | Direct, respectful | **Always** — money and standing | Sometimes |
| **Brand partner** | ≤ 25 words | Technical and warranty vocabulary | Formal, precise | Where a claim decision follows | No |
| **Rider** | **≤ 8 words** | None | Direct | Only for custody and cash | No |
| **Contact centre agent** | ≤ 12 words | Full vocabulary + customer-safe paraphrase | Neutral | Where the agent must explain onward | **Yes** |
| **Auditor** | ≤ 20 words | Quality and ISO vocabulary, exactly | Neutral, formal | Where a finding classification follows | No |
| **Referral partner** | ≤ 20 words | Minimal | Warm | **Always** — commission and attribution | No |

---

## 5. Per-audience notes

### 5.1 Customer — `P01`

The only audience that can leave. Booking funnel conversion is `P01`'s primary design KPI at a
**> 72%** target, and copy is a principal lever on it.

| Rule | Detail |
|---|---|
| C-01 | Bengali is the default, English the toggle (`PS-03`). Author with Bengali in mind |
| C-02 | Never use an internal term. The customer does not know what a "work order" or a "dispatch job" is. See the registered surface pairs in `CG-004` §5 |
| C-03 | Always state what happens next and roughly when |
| C-04 | Their device and their money are at stake. Never be breezy about either |
| C-05 | Assume no prior visit. Do not rely on what a previous screen said |
| C-06 | Price is never implied. State it, or state that it is an estimate and what could change it |

> **Booking** is the customer's word; **service order** is ours. `CG-004` §10 records this as an
> open question (item 2). Until it is closed, `P01` uses "booking" for the *act* and shows the
> service order reference as "your reference".

### 5.2 Field technician — `P02`

The tightest constraint in the system. Bengali interface must be **complete, including error
messages** (`P02` non-negotiable #3). Read one-handed, outdoors, on a mid-range Android with
3 GB RAM, sometimes 24 hours offline.

| Rule | Detail |
|---|---|
| T-01 | Eight to twelve words. If it does not fit, the screen is wrong, not the copy |
| T-02 | Action first, context second. "Scan the part" before "to record consumption" |
| T-03 | Full technical vocabulary. They are experts; plain-language substitution insults and slows them |
| T-04 | Never require reading a previous screen. Every screen stands alone |
| T-05 | Offline states must be unambiguous: what is saved, what is not, what happens next (`UI-009`) |
| T-06 | Safety content is never abbreviated for length. It is the one exception to T-01 |
| T-07 | Their earnings and certification status are personal. Tone there is respectful and precise, never casual |

### 5.3 Branch and back-office staff — `P03`

150–250 people, fourteen workspaces, a **four-hour time-to-competence target** (`NFR-075`) and a
**three-minute walk-in intake target** (`NFR-076`). Both are copy outcomes as much as design ones.

| Rule | Detail |
|---|---|
| A-01 | Brevity is the courtesy. They will read this label thousands of times |
| A-02 | Keyboard-first roles — intake, dispatch, finance — get the shortest labels in the system |
| A-03 | Screen density is 1366×768. A label that wraps is a label that is too long |
| A-04 | Full operational vocabulary, used exactly as `CG-004` fixes it |
| A-05 | Irreversible actions get the consequential tone (`VB-001` §5.4) regardless of A-01 |
| A-06 | Fourteen workspaces share one vocabulary. A dispatcher moving to the branch console must not relearn words |

### 5.4 Corporate admin — `P04`

Unpaid users of our system, answerable to their own management, and the audience most likely to
**forward our content to people who never log in**.

| Rule | Detail |
|---|---|
| K-01 | Every message must make sense to someone who did not see the screen it came from |
| K-02 | State consequences fully. They must be able to justify a decision internally |
| K-03 | No repair jargon. They manage an estate; they do not fix devices |
| K-04 | Invoice and SLA language is contractual in effect. Reconcile exactly with `LG-015` and `DT-031` |
| K-05 | Bulk operations state scope explicitly: how many, which sites, what will happen |

### 5.5 Vendor and supplier — `P05`

Targets: **> 90%** of POs acknowledged and **> 85%** of invoices submitted through the portal,
with a **60% reduction** in vendor phone and email queries. Every ambiguity is a phone call.

| Rule | Detail |
|---|---|
| V-01 | Every screen answers "what do you need from me, and by when?" |
| V-02 | Rejection copy states the reason and the remedy. A rejected delivery with no reason becomes a call |
| V-03 | Payment and remittance language is precise about amounts, dates and what has been deducted |
| V-04 | Scorecard copy explains **how the score moves**, not only what it is (`EO-006`) |

### 5.6 Executive and manager — `P06`

Twenty-five to sixty people making decisions on numbers. `P06` commits management to making
**100% of decisions on live data** rather than compiled spreadsheets.

| Rule | Detail |
|---|---|
| X-01 | A metric name that is imprecise produces a confidently wrong decision. Names come from `RP-001` |
| X-02 | Every metric is one click from its definition, inclusions and exclusions |
| X-03 | Where a number could mislead — small denominator, partial period, changed definition — the content says so on the tile, not in a footnote |
| X-04 | Mobile dashboards carry the same words as desktop, not shortened variants |

### 5.7 Marketplace seller — `P07`

External, mixed literacy, Bengali-first, and their income depends on understanding us.
Onboarding completion target **> 60%** of started registrations.

| Rule | Detail |
|---|---|
| S-01 | Registration copy is the completion lever. Every field explains why it is needed |
| S-02 | Money copy — earnings, commission, fees, holds, payouts — is the trust surface. State the arithmetic |
| S-03 | Performance and sanction copy has contractual effect under `LG-004`. Precise, never threatening |
| S-04 | Never assume familiarity with platform concepts. "Boost" and "listing" are taught, not assumed |

### 5.8 Brand partner — `P08`

International, expert, reading our evidence to decide whether to pay us. Claim approval target
**> 92%**, decision time **< 10 days**.

| Rule | Detail |
|---|---|
| B-01 | Formal, precise, complete. This audience judges our professionalism by our documentation |
| B-02 | English only (`CG-010` §3.2). Do not part-translate |
| B-03 | Evidence language is factual and unarguable — what was found, what was done, by whom, when |
| B-04 | Never advocate in the content. Present the evidence; let the claim stand on it |

### 5.9 Rider — `P09`

**The shortest content in the system.** One-handed, moving, often in poor light, offline.
POD completeness target **100%**, custody breaks target **zero**.

| Rule | Detail |
|---|---|
| R-01 | Eight words maximum. Prefer four |
| R-02 | One action per screen. Never two decisions at once |
| R-03 | Custody and cash steps are the exception: they get the words they need |
| R-04 | Exception copy — customer absent, address wrong, refused, damaged — is a fixed list, not free text |
| R-05 | Offline status must be readable at a glance without reading (`VB-008` status semantics) |

### 5.10 Contact centre agent — `P10`

The only audience that **reads content aloud** while a customer waits. Targets: **< 3 screen
switches** per contact, **100%** disposition coding.

| Rule | Detail |
|---|---|
| G-01 | Content must be speakable. Read every string aloud before approving it |
| G-02 | Provide the customer-safe paraphrase alongside the internal term where they differ |
| G-03 | Disposition codes are short, distinct and mutually exclusive. Ambiguity here costs 100% completeness |
| G-04 | Knowledge and canned responses are scannable in under five seconds mid-call (`OP-003`) |

### 5.11 Quality auditor — `P11`

Twenty to sixty people whose **classification language is the standard**. Finding-to-CAPA cycle
target **< 5 days**, evidence attached **100%**.

| Rule | Detail |
|---|---|
| Q-01 | ISO 9001 vocabulary is used exactly and never paraphrased (`CG-004` §4.7) |
| Q-02 | Severity and classification descriptions must produce the same answer from different auditors |
| Q-03 | Offline-first. Every string available without connectivity |

### 5.12 Referral partner — `P12`

Chose to be here, motivated by commission, novice in our processes. Attribution disputes are the
normal failure mode of referral programmes.

| Rule | Detail |
|---|---|
| P-01 | Attribution rules stated plainly and identically in the portal, the agreement and the statement |
| P-02 | Commission arithmetic shown, not asserted |
| P-03 | Warm — they are advocates, not staff — but never vague about money |

---

## 6. Where one message serves two audiences

Common and dangerous. A single event often notifies a customer, a technician and a branch
manager.

| # | Rule |
|---|---|
| **M-01** | **Never write one message for two audiences.** Write two, from the same fact |
| **M-02** | The canonical fact lives in one place (`CG-003` §10 X-01). The tone differs; the fact does not |
| **M-03** | Where a customer-facing and internal message describe the same state, both use the `MD-027` label for that state — the customer-facing label for the customer, the internal one internally |
| **M-04** | A message forwarded outward — `P04` especially — is written as though the recipient has no context |

**Example — one event, three messages**

| Audience | Message |
|---|---|
| Customer (`P01`, SMS) | Your laptop repair is ready. Collect from 1000FiX Shewrapara, 10am–8pm. Ref SR-2026-114882. |
| Technician (`P02`, push) | SR-114882 QC passed. Move to ready-for-collection rack B. |
| Branch manager (`P03`) | SR-2026-114882 ready for collection. Uncollected ageing starts today. Outstanding BDT 3,200. |

---

## 7. Examples — do and do not

| Audience | Do not | Do |
|---|---|---|
| Customer | Your service order status has been updated to In Repair. | We have started repairing your laptop. We will message you when it is ready. |
| Technician | Please ensure that you have scanned all consumed parts before completing the job. | Scan all parts used. |
| Rider | The customer was not available at the delivery address provided. | Customer not present |
| Executive | TAT performance shows a slight negative variance this period. | Turnaround time 6.2 days. Target 5.0. Worst: Chattogram Agrabad at 9.1. |
| Seller | Your payout has been placed on hold pending resolution. | Your BDT 12,400 payout is held until the dispute on job MP-4417 is closed. Payouts resume automatically. |
| Corporate admin | Bulk upload processed. | 142 of 150 service requests created. 8 failed because the asset tag was not found. Download the failure list. |
| Brand partner | We think this claim should be approved. | Diagnosis: main board failure. Parts replaced: BN94-00123A. Technician: Samsung-certified, valid to 2027-03-31. Purchase proof attached. |

---

## 8. Dependencies

| Depends on | Why |
|---|---|
| `VB-001` | The voice this file calibrates |
| `CG-004` | Registered surface-specific pairs (`branch`/`service centre`, `application`/`app`) |
| `CG-010` | Which audiences read Bengali |
| `MD-027` | Internal state versus customer-facing label |
| `04-00` §2 and per-portal KPI tables | Volumes, devices and targets that drive the calibration |

---

## 9. Enforcement

| Mechanism | How |
|---|---|
| Gate G1 (`CG-007`) | Reviewer checks the calibration against §4.2 for the surface |
| Sentence-budget lint | Automated warning above the per-surface budget in §4.2 |
| Read-aloud check | Mandatory for all `P10` content (G-01) |
| Cross-audience check | `AUDIT_Checklist_Recurring.md` §F — one event's messages compared across audiences |
| Metrics | `CG-014` E-08 funnel conversion, E-11 language switching, E-28 seller onboarding — each tests a calibration |

---

## 10. Maintenance

| Item | Value |
|---|---|
| Review cadence | Every two waves |
| Out-of-cycle trigger | A new portal; a volume or device assumption changing; a per-portal KPI missing target where copy is implicated |
| Owner | Content Design Lead |
| Bengali counterpart | `VB-002_Persona_and_Portal_Tone_Matrix_BN.md` — required, not yet written |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`VB-001_ERP_Product_Voice_and_Tone_Guide.md`](VB-001_ERP_Product_Voice_and_Tone_Guide.md) | The voice being calibrated |
| [`VB-006_Design_System_Content_Standards.md`](VB-006_Design_System_Content_Standards.md) | Component copy that must respect these budgets |
| [`VB-008_Status_Colour_and_Label_Semantics_Register.md`](VB-008_Status_Colour_and_Label_Semantics_Register.md) | R-05 glanceable status |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Surface-specific registered pairs |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | Language column in §4.1 |
| `UI-011` … `UI-022` | The per-portal copy packs this calibrates |
| `04-00` | Portal suite specification |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Six calibration dimensions, placement and prescription for eleven audiences across twelve portals, per-audience rules, one-event-three-messages rule, worked examples | Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] All twelve portals and eleven audiences covered
- [x] Calibration is prescriptive — sentence budgets, jargon policy, warmth — not descriptive
- [x] Volumes, devices and targets sourced from `04-00`, verified 2026-08-15
- [x] The one-event-multiple-audiences failure addressed explicitly
- [x] All internal links resolve
- [ ] Bengali counterpart written and signed off in context — **outstanding; blocks `Approved` under `CM-R6`**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
