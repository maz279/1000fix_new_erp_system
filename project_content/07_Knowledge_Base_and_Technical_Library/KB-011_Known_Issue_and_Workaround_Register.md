---
id: KB-011
title: Known Issue and Workaround Register
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with Quality
author: Technical Services with Quality Management
reviewers: [Quality Manager, Technical Director, Warranty Claims Officer, Contact Centre Supervisor, Legal Counsel, Knowledge Manager, Localisation Lead]
approver: Quality Manager with Technical Director
content_class: C
purpose: >
  The register of recurring defects by model — the signature that identifies them, the interim
  workaround, the permanent-fix status and the agreed customer messaging. It stops 200–400
  technicians independently rediscovering the same fault, gives the contact centre one consistent
  answer instead of thirty, and gives the company the evidence base it needs to raise a defect with
  a brand partner rather than absorbing it repair by repair.
traces_to: [M23, M61, M31, M09, M01, M34, M26, P02, P03, P08, P10, MD-021, MD-022, MD-024, KB-001, KB-002, KB-008, KB-009, KB-010, KB-015, SP-029, SP-028]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-011_Known_Issue_and_Workaround_Register_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §3.1 item 2 known issue as an article type; §5.4 FR-KMS-028 draft articles from M23 verified fixes and recurring M09 claim-rejection causes; §11 AUT-KMS-15/16
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M23_Quality_Management_System.md §12 — failure patterns and verified fixes worth documenting as articles
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-06 a new order for the same device and fault category within 30 days is automatically flagged as rework and linked to the original; BRU-QMS-02 every non-conformance requires a root cause and a CAPA before closure; BRU-QMS-05 repeated non-conformance in the same process triggers a mandatory management review item
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §9 BRU-KMS-04 two contradictory articles cannot both be Published for the same model and fault; BRU-KMS-18 an article flagged for low usefulness is revised or retired within the declared period
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-011 — Known Issue and Workaround Register

| Item | Value |
|---|---|
| Article type | **Troubleshooting** (article type `known_issue`) |
| Device family | All — scoped per issue |
| Brand / model scope | Scoped per issue; **never family-wide without evidence across the family** |
| Skill level required | L1 to read and apply a workaround · R12 or Quality to raise and confirm an issue |
| Offline pack member | **Yes** — a workaround is worth nothing if it is not available where the repair happens |
| Review due | 2027-02-16 · **individual issue records carry a 6-month cycle** (`KB-001` §4.2) |

> **Template conformance.** Troubleshooting-type article applied at register level; all
> `TPL_Knowledge_Article.md` sections retained in order. Sections 11–13 are justified additions.

---

## 1. Purpose and Scope

**`KB-010` is what the brand tells us. This file is what we found out ourselves.**

The distinction matters operationally, not just editorially:

| | `KB-010` Bulletin archive | `KB-011` Known-issue register |
|---|---|---|
| Origin | The manufacturer | 1000FiX's own repair data |
| Authority | The brand's | Ours, and it must be evidenced |
| Certainty | High from receipt | **Grows with occurrences** |
| Customer messaging | Usually supplied | **We must write it, carefully** |
| Commercial consequence | Usually the brand's cost | **Ours until we can prove it is theirs** |
| Endpoint | Closed when actioned | Closed when a **permanent fix** exists, or when the model leaves service |

A known issue is the intermediate state between "one odd repair" and "a bulletin from the brand".
The whole value of the register is in holding that intermediate state honestly — neither
dismissing a pattern as coincidence nor declaring a defect the evidence does not support.

**In scope:** the issue record structure; defect-signature definition; the confidence and
occurrence thresholds that move an issue between states; workaround authoring; permanent-fix
tracking; customer messaging approval; the brand-escalation route; and the relationship to rework,
CAPA and claim rejection.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Manufacturer-originated bulletins and recalls | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) |
| The repair procedure itself | `KB-004`…`KB-007` |
| Manufacturer code interpretation | [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) |
| Part substitution consequences | [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) |
| Non-conformance, root cause and CAPA process | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) · `M23` |
| Complaint handling and compensation | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) · `M34` |
| Warranty claim submission | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) |
| Defects in **1000FiX's own** systems | `M66` internal IT · `SP-031` |

> **A boundary that will be tested.** A recurring defect in a device is a `KB-011` issue. A
> recurring defect in *our own repair work* is a non-conformance and belongs to `M23` and `SP-029`.
> The two look similar in the data — the same model failing repeatedly — and the distinction is
> **root cause**, not symptom. `KW-05` requires the register to state which it is, and to hand over
> to `M23` when the answer is "us".

---

## 2. Safety

> ⚠ **WARNING — a workaround is not a fix, and some defects are hazards.** A workaround that
> makes a device usable while leaving a defect in place can leave a safety condition active —
> a thermal protection that trips early, a seal that leaks intermittently, a battery that swells
> under a particular charging pattern (hazard). Applying the workaround and returning the device
> can put the customer at risk (consequence). **Every issue record carries a `safety_relevant`
> flag; a safety-relevant issue may not be closed with a workaround alone, and its record requires
> HSE approval** (avoidance) — `KW-06`.

> **NOTICE — an issue record is a factual claim about a third party's product.** It can be
> disclosed in a dispute, quoted to a brand partner, or read by a customer if the messaging is
> published. It must be evidenced, dated, proportionate and free of speculation about cause where
> cause is not established (`AU-20`, `CG-012`).

---

## 3. Symptoms — *the signals that a known issue exists and is not registered*

| Signal | Threshold worth investigating | Source |
|---|---|---|
| **Rework flags clustering on one model and fault category** | 3+ in 90 days | `BRU-SRM-06` auto-flag |
| The same fault code and model recurring across branches | 5+ in 90 days across ≥ 2 branches | `M01`, `M31` |
| A part consumed at a rate far above its model population | Consumption vs installed base | `M15`, `M43` |
| Claims rejected repeatedly for one model and cause | 3+ in 90 days | `M09` |
| Technicians asking each other about the same model | Qualitative — but real | Escalation and chat volume |
| Contact centre giving inconsistent answers about a model | Quality monitoring | `P10`, `M27` |
| A `no_fault_found` cluster on one model | 5+ in 90 days | `RES-04` records |
| A workaround circulating informally | Any occurrence | **This is the strongest signal and the worst one to ignore** |

**`KW-01`: an informal workaround in circulation is registered or refuted within 14 days.** An
undocumented workaround being passed technician to technician is a known issue that the company
already has and does not own — it is unversioned, unreviewed, possibly unsafe, and it will be
applied to models it does not fit.

---

## 4. Likely Causes — *why a recurring defect appears*

| # | Cause class | Who owns the fix | Evidence needed |
|---:|---|---|---|
| 1 | **Manufacturer design or component defect** | The brand | Occurrence data, serial/date-code correlation, failure analysis |
| 2 | Manufacturing batch defect | The brand | Serial or batch-range correlation |
| 3 | Firmware defect | The brand | Version correlation; check `KB-010` for advisories |
| 4 | **Environmental — heat, humidity, dust, monsoon, supply voltage** | Nobody, but it is predictable | Geographic and seasonal correlation |
| 5 | Installation defect pattern | The installer — possibly us | Installation-review findings (`KB-005` `TG-19`) |
| 6 | **Our own repair practice** | **1000FiX — hand to `M23`** (`KW-05`) | Correlation with our repairs, technicians, or parts used |
| 7 | Non-genuine part in the population | The supply chain | `part_class` correlation (`KB-009`) |
| 8 | Customer usage pattern | Nobody — but it changes the messaging | Usage correlation |

> **Cause 4 deserves more weight in this market than a generic register would give it.** Sustained
> heat, monsoon humidity, dust and unstable supply voltage produce genuine, repeatable failure
> patterns that are not manufacturer defects and never will be. Registering them as known issues is
> still correct — the workaround and the customer messaging are real — but escalating them to a
> brand as a defect claim wastes the relationship and weakens the next escalation that is genuine.

---

## 5. Diagnostic Procedure — *how an issue is raised, confirmed and stated*

| Step | Who | Action | Gate |
|---:|---|---|---|
| 1 | Any technician, or the system | Raise a candidate from a pattern (§3) or a single striking observation | No threshold to *raise* — `KW-02` |
| 2 | Technical analyst | Define the **defect signature** (§6.1) precisely enough to be matched, not merely described | Signature testable |
| 3 | Technical analyst | Query history against the signature; count occurrences; establish scope by model, generation, serial range, region, season | Occurrence data attached |
| 4 | Technical analyst | Assign confidence and state (§6.2) | Confidence displayed (`KW-03`) |
| 5 | R12 specialist | Author or verify the workaround (§6.3); the verifier is not the author | `BRU-KMS-02` pattern |
| 6 | HSE Lead | Approve if `safety_relevant` | `KW-06`, `BRU-KMS-03` |
| 7 | Quality Manager | Determine cause class (§4); **if cause 6, hand to `M23`** | `KW-05` |
| 8 | Quality Manager + Customer Service Manager | Approve customer messaging (§6.4) | `KW-07` — never published without both |
| 9 | Quality Manager + R28 | Decide whether to escalate to the brand (§6.5) | Evidence pack complete |
| 10 | System | Publish; distribute to affected technicians; add to offline packs; expose to `M32` if confidence permits | `KW-08` |
| 11 | Quality Manager | Track to permanent fix or model end-of-life | Closure criteria in §6.6 |

**`KW-02`: raising a candidate has no threshold; confirming one does.** A register that requires
evidence before an observation can be recorded will never receive the observation, because the
person who has it is holding a screwdriver and has four more jobs. Raise freely; confirm rigorously.

---

## 6. Repair Procedure — *the register's mechanics*

### 6.1 Defect signature

**A known issue without a testable signature is an anecdote.** The signature is what lets the
system match a new job to an existing issue, and it is the hardest part of the record to write well.

| Signature element | Required | Example of a good element | Example of a bad one |
|---|:--:|---|---|
| Model scope | ✔ | Specific `MDL-` codes plus generation qualifier | "This brand's laptops" |
| Fault code | ✔ | A specific `FLT-` code from `MD-024` | "Power problems" |
| Observable condition | ✔ | A measurable or visible state a technician can confirm | "Sometimes fails" |
| Onset pattern | Where known | "After 18–30 months" · "Under sustained load above 35 °C ambient" | "Randomly" |
| Serial / batch / date-code range | Where known | A stated range with its source | Guessed |
| Firmware version | Where relevant | A specific version or range | "Recent firmware" |
| Environmental correlation | Where established | "Coastal branches, monsoon months" | "Humidity probably" |
| Part correlation | Where relevant | A `PRT-` code and `part_class` | "Cheap parts" |
| **Exclusions** | ✔ | What this issue is **not** — the adjacent fault it is confused with | Absent |

**`KW-04`: every signature states its exclusions.** The commonest register failure is an issue
that grows to absorb every superficially similar fault, at which point it explains everything and
predicts nothing.

### 6.2 States and confidence

| State | Meaning | Occurrence basis | Workaround published | Customer messaging | AI corpus |
|---|---|---|:--:|:--:|:--:|
| `candidate` | Raised, not yet analysed | 1+ | ✖ | ✖ | ✖ |
| `investigating` | Signature defined, history being queried | Any | Internal only, marked provisional | ✖ | ✖ |
| `confirmed` | Signature matches a consistent, quantified population | **≥ 5 matched occurrences, ≥ 2 branches, verified by a second person** | ✔ | ✔ once approved | ✔ |
| `brand_raised` | Escalated to the brand with an evidence pack | As `confirmed` | ✔ | ✔ | ✔ |
| `brand_confirmed` | The brand has acknowledged, usually via a `BUL-` | — | ✔ | ✔ | ✔ |
| `permanent_fix` | A permanent remedy exists and is available | — | Superseded by the fix | Updated | ✔ |
| `refuted` | Investigation showed no pattern | — | Withdrawn | Withdrawn | ✖ |
| `closed` | Fixed, or the model has left service | — | Archived | Archived | ✖ |

**`KW-03`: the state and the occurrence count are displayed to every reader.** A technician
applying a workaround needs to know whether it rests on five cases or five hundred.

**`KW-08`: only `confirmed`, `brand_raised`, `brand_confirmed` and `permanent_fix` issues enter
the `M32` corpus**, consistent with `BRU-KMS-12` and with the confidence discipline in `KB-008`
§6.3. A customer-facing assistant must never describe an unconfirmed defect in a manufacturer's
product.

### 6.3 Workaround authoring

| # | Rule |
|---|---|
| **KW-09** | A workaround states plainly that it is **a workaround, not a fix**, and what remains unfixed |
| **KW-10** | It states its expected durability — "holds until the part is replaced", "holds for one season", "unknown" |
| **KW-11** | It states what it costs the customer — a disabled feature, reduced performance, a shorter interval before return |
| **KW-12** | A workaround that reduces or defeats a safety function is **prohibited**, not merely discouraged (`KB-009` §6.4 applies) |
| **KW-13** | It names the permanent fix where one exists, and the blocker where one does not |
| **KW-14** | It is superseded — not merely amended — when the permanent fix arrives, so that two answers never coexist (`BRU-KMS-04`) |
| **KW-15** | Charging the customer for a workaround on a defect we have raised with the brand requires Quality Manager approval; **the commercial position must be deliberate, not accidental** |

### 6.4 Customer messaging

**`KW-07`: customer messaging is approved by the Quality Manager and the Customer Service Manager
together, and never by either alone.** This mirrors `BRU-KMS-11` for customer derivatives.

| Element | Requirement |
|---|---|
| What we say happened | Factual, observable, no speculation about the manufacturer's cause unless the brand has confirmed it |
| What we did | The workaround or the fix, in plain language, bilingual |
| What the customer should expect | Durability, cost, what to watch for, when to return |
| What we do **not** say | Anything attributing blame that the evidence does not support; anything about other customers' devices; anything that pre-empts a brand's own statement |
| Consistency | **The contact centre, the branch, the technician and the portal say the same thing.** This is the reason the messaging is centrally approved rather than written per interaction |
| Channel | Distributed to `P10` scripts (`SP-034`), branch agents, and `P01` where published |

> **Why this is tighter than it may seem necessary.** A statement made to 250,000 customers a
> month about a named manufacturer's product is, in aggregate, a public statement. `AU-20`
> prohibits brand-disparaging or speculative language for exactly this reason, and `CG-013`
> escalates anything with legal consequence.

### 6.5 Brand escalation

| Step | Action |
|---:|---|
| 1 | Quality Manager and R28 agree the issue is `confirmed` and the cause class is 1, 2 or 3 (§4) |
| 2 | Assemble the evidence pack: signature, occurrence count and dates, serial/batch correlation, failure analysis, photographs, claim history |
| 3 | Raise through the brand channel — `P08` or the relationship route in `MD-017` |
| 4 | State what we are asking for: acknowledgement, a bulletin, a part change, claim acceptance, or a recall assessment |
| 5 | Track the response; a brand acknowledgement usually arrives as a `BUL-` and links back (`KB-010`) |
| 6 | **If the brand does not respond**, escalate through Account Management and `M40`; record the non-response — it is relevant to the commercial relationship and to any future dispute |
| 7 | If the brand identifies a safety condition, it becomes a `KB-010` matter and may become a recall — **`BRU-KMS-15` routing applies immediately** |

### 6.6 Closure

An issue is closed only when one of these is true, and the reason is recorded:

| Closure reason | Evidence |
|---|---|
| Permanent fix available and deployed | The fix, and occurrence rate falling to baseline |
| Brand recall or remediation completed | `KB-010` campaign closure |
| Model out of service across the population | `MD-021` `active = False` and no remaining installed base we service |
| Refuted | The analysis showing no pattern — **retained, not deleted**, so the same candidate is not re-raised annually |

**`KW-16`: an issue is never closed because it has gone quiet.** A defect with a 24-month onset
looks resolved for two years. Closure requires a reason from the table above.

---

## 7. Parts

| Situation | Handling |
|---|---|
| An issue is caused by a part | `KB-009` note created or amended; `MD-022` change raised with MDM |
| An issue drives abnormal part consumption | Inventory and `M43` planning informed — a known issue is a demand forecast |
| A workaround requires a part not normally stocked | Stocking decision with Inventory; the workaround states availability honestly |
| A non-genuine part is implicated | `KB-009` §6.2 behavioural note; supplier escalation to Procurement |
| A brand supplies a revised part | Supersession chain (`KB-009` §6.5); issue moves toward `permanent_fix` |

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every `confirmed` issue has a testable signature with exclusions | 100% (`KW-04`) | Weekly register review |
| State and occurrence count displayed on every record | 100% (`KW-03`) | Rendering check |
| `confirmed` state meets the ≥ 5 occurrence / ≥ 2 branch / second-verifier basis | 100% | Confirmation record |
| Safety-relevant issues carry HSE approval and are not closed on a workaround alone | 100% (`KW-06`) | Approval record |
| Customer messaging carries dual approval | 100% (`KW-07`) | Approval record |
| Workarounds state they are workarounds, with durability and cost | 100% (`KW-09`…`KW-11`) | Content review |
| No workaround defeats a safety function | Zero (`KW-12`) | Content review + HSE |
| `M32` corpus contains no `candidate`, `investigating` or `refuted` issues | Zero (`KW-08`) | Corpus audit |
| Informal workarounds registered or refuted within 14 days | 100% (`KW-01`) | Escalation review |
| Cause-class 6 issues handed to `M23` | 100% (`KW-05`) | CAPA linkage |
| **Rework rate on models with an active known issue** | Falling after workaround publication — **this is the test of whether the register works** | Monthly |
| Contact-centre answer consistency on issue models | Sampled monthly | `P10` quality monitoring |
| Issues closed with a recorded reason | 100% (`KW-16`) | Closure record |
| Brand escalations with a complete evidence pack | 100% | Escalation record |

> **The rework measure is the honest one.** Everything else in this table tests whether the
> register is well-formed. Only the rework rate tests whether it is *useful* — and if publishing a
> workaround does not reduce rework on that model, the workaround is not reaching the bench, which
> is a `KB-001` findability problem or a `KB-016` offline problem.

---

## 9. Resolution Coding

| Situation | Coding |
|---|---|
| Repair applying a published workaround | Ordinary `RES-` coding, plus the `KIS-` reference on the job |
| Repair applying a permanent fix | Ordinary coding; the `KIS-` reference closes the loop for measurement |
| A job that establishes a new occurrence of an issue | Coded normally; the signature match is computed, not hand-entered |
| Rework attributable to a known issue | Flagged as rework (`BRU-SRM-06`) and **attributed to the issue**, so that technician rework metrics are not distorted by a manufacturer defect |
| `no_fault_found` on a model with an intermittent known issue | Supervisor countersignature (`RES-04`); the `KIS-` reference records that the issue was considered |

**`KW-17`: rework attributable to a registered known issue is separated from technician-attributable
rework in reporting.** Failing to separate them punishes technicians for a defect they did not
cause and hides the defect inside a performance metric.

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| An issue appears `safety_relevant` | **HSE Lead immediately**; Quality Manager | Signature, occurrences, hazard description |
| An issue may warrant a recall | Quality Manager + Legal Counsel; brand notified (`KB-010` §6.6 routing) | Evidence pack |
| Cause class is 6 — our own practice | **`M23` non-conformance and CAPA** (`BRU-QMS-02`), `SP-029` | Correlation analysis |
| Repeated non-conformance in the same process | Mandatory management-review item (`BRU-QMS-05`) | `M23` record |
| A brand does not respond to an escalation | Account Management and `M40`; record the non-response | Escalation trail |
| Customer messaging is requested urgently and dual approval is unavailable | **Quality Manager may issue an interim internal-only holding statement**; customer-facing messaging still requires both | Interim statement, logged |
| A workaround is found circulating that defeats a safety function | HSE + Quality Manager; withdraw immediately, communicate the withdrawal | The workaround, where it was found |
| An issue's commercial cost is material and unrecovered | Finance and Commercial via Quality Manager | Cost accumulation |
| Media, regulator or corporate-client enquiry about a defect | **Legal Counsel — `CG-013` trigger.** Nobody else responds | The enquiry |

---

## 11. Record Structure *(addition — justified: the register's structure has no home in the template and is referenced by `KB-008`, `KB-009` and `KB-010`)*

| Column | Type | Req | Notes |
|---|---|:--:|---|
| `issue_code` | `KIS-nnnn` | ✔ | Permanent, never reused |
| `title_en` / `title_bn` | text | ✔ | Model + observable condition |
| `state` | enum | ✔ | §6.2 |
| `confidence_basis` | text | ✔ | Occurrence count, branches, date range |
| `occurrence_count`, `first_observed`, `last_observed` | | ✔ | Computed from signature matching |
| `signature_json` | structured | ✔ | §6.1, including **exclusions** |
| `model_scope`, `brand_code`, `fault_codes`, `part_codes` | multi-fk | ✔ / conditional | `MD-021`, `MD-017`, `MD-024`, `MD-022` |
| `serial_range`, `firmware_range`, `environmental_note` | | conditional | §6.1 |
| `cause_class` | enum | ✔ | §4 — including `unknown` |
| `safety_relevant` | bool | ✔ | `KW-06` |
| `workaround_ref` | fk → `KNW-` | conditional | §6.3 |
| `workaround_durability`, `workaround_cost_to_customer` | text | conditional | `KW-10`, `KW-11` |
| `permanent_fix_status` | enum | ✔ | none / brand_developing / available / deployed |
| `customer_message_en` / `_bn` | text | conditional | `KW-07` dual approval |
| `brand_escalation_ref`, `brand_response`, `bulletin_ref` | | conditional | §6.5, links to `BUL-` |
| `capa_ref` | fk | conditional | Where cause class 6 (`KW-05`) |
| `rework_attributed_count`, `claim_rejection_count` | int | | Measurement |
| `hse_approved_by`, `messaging_approved_by` | fk | conditional | `KW-06`, `KW-07` |
| `closure_reason`, `closed_at`, `closed_by` | | conditional | §6.6 |

---

## 12. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | The mirror image — brand-originated versus self-discovered |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | A code recurring on one model is a known-issue signal |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Part-caused issues and the substitution consequences |
| [`KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md`](KB-015_Knowledge_Review_Currency_and_Retirement_Policy.md) | The 6-month cycle on known-issue records |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | High-volume workarounds belong on offline cards |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) · [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) · [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) · [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | Every set escalates patterns here |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-029_SOP_Internal_Quality_Audit_and_CAPA.md) | Where cause-class-6 issues go |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-028_SOP_Complaint_Escalation_and_Compensation.md) | Complaints arising from a known issue |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-034_Call_and_Conversation_Script_Library.md) | Where approved customer messaging is delivered on a call |
| `M23` Quality Management System | Verified fixes as an authoring source (`FR-KMS-028`) |
| `M43` Demand Planning and Replenishment | A known issue is a parts-demand signal |
| `TR-016` Course Pack — Quality and Field Auditor · `TR-009` Field Technician | Train raising and applying |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M61` §3.1, §5.4 FR-KMS-028, §9 `BRU-KMS-02`, `-03`, `-04`, `-11`, `-12`, `-18`, §11 AUT-KMS-15/16 | 2026-08-16 | 2027-02-16 |
| `M23` §12 — failure patterns and verified fixes worth documenting | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-06`; `BRU-QMS-02`, `BRU-QMS-05` | 2026-08-16 | 2027-02-16 |
| `MD-021`, `MD-022`, `MD-024` — signature binding targets | 2026-08-16 | 2027-02-16 |

> **No specific defect, model or brand is named in this file.** The register holds those; this file
> governs how they are established, stated and closed. A defect claim about a named product is a
> factual assertion with commercial and legal consequence (`CG-012`, `CG-013`), and it does not
> belong in a governing document that will be read long after the defect is resolved.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **Signature matching requires structured job data that may not exist.** §6.1 assumes fault codes, part codes, serials, firmware versions and branch are all recorded as structured fields on every job. Where any is free text, occurrence counting is manual and the ≥ 5 threshold becomes unenforceable | CTO with BI Lead | **Before W2 build — the register's core mechanic depends on it** |
| **O-02** | The register is empty and stays empty until repair volume accumulates. **It is the one `KB` file that cannot be pre-authored** — its content is generated by operating | Technical analyst with Quality | Meaningful content from W3 |
| **O-03** | `KW-17` requires rework reporting to separate issue-attributable from technician-attributable rework. Whether `RP-001` defines rework that way is unconfirmed | BI Lead with Quality Manager | **W2 — affects technician performance measurement** |
| **O-04** | Customer messaging (§6.4) must reach `P10` scripts, branch agents and `P01` consistently. The distribution mechanism across those three surfaces is not specified in any file reviewed | Content Design with Contact Centre and Quality | W4 |
| **O-05** | The brand-escalation evidence-pack format (§6.5) does not exist. R28 will need one that brands accept, and it likely differs per brand | Warranty Claims Officer with Commercial | W4 |
| **O-06** | The `M23` handover for cause-class-6 issues (`KW-05`) needs a defined trigger in `SP-029`. `SP-029` was authored before this file and does not name it | Quality Manager with Business Process Lead | W3 |
| **O-07** | Bengali workaround and customer-messaging wording requires the terminology base `KB-002` `O-05` records as missing, plus a plain-language standard for customer-facing defect statements | Localisation Lead with Content Design | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§12 justified
- [x] The `KB-010` / `KB-011` boundary stated as origin and authority, not as subject matter
- [x] The "our own practice" cause class routed out to `M23` rather than absorbed (`KW-05`)
- [x] Raising has no threshold; confirming has a stated, evidenced one (`KW-02`, §6.2)
- [x] Defect signatures required to be testable and to state exclusions (`KW-04`)
- [x] State and occurrence count displayed to every reader (`KW-03`)
- [x] Workarounds required to declare themselves as workarounds, with durability and customer cost
- [x] Safety-defeating workarounds prohibited outright (`KW-12`)
- [x] Customer messaging under dual approval, with a stated prohibition on unsupported attribution
- [x] AI corpus boundary bound to state (`KW-08`)
- [x] Rework attribution separated so technicians are not penalised for manufacturer defects (`KW-17`)
- [x] Closure requires a reason; going quiet is not one (`KW-16`)
- [x] Environmental causes given proper weight for this market without being escalated as defects
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-SRM-*`, `BRU-QMS-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` structured job data confirmed — outstanding; the signature mechanic depends on it**
- [ ] **`O-03` rework attribution defined in `RP-001` — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Quality Manager and Technical Director**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
