---
id: KB-012
title: Tool, Jig and Test Equipment Operating Guides
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical with HSE
author: Technical Services with HSE and Facilities
reviewers: [Quality Manager, Technical Director, HSE Lead, Facilities Manager, Knowledge Manager, Localisation Lead]
approver: Technical Director with HSE Lead
content_class: C
purpose: >
  Operating, safety and calibration-check guidance for every tool, jig and item of test equipment
  the company issues. Misused test equipment produces false diagnoses and injures people — a
  meter on the wrong range across a live circuit, an uncalibrated instrument giving a confident
  wrong reading, a hot-air station at the wrong profile destroying the board it was meant to save.
  ISO 9001:2015 requires measurement equipment to be calibrated and its status identifiable; that
  obligation only means something if the person holding the instrument knows how to read it.
traces_to: [MD-046, MD-044, M45, M23, M59, M61, M31, P02, P03, P11, KB-001, KB-002, KB-013, KB-004, KB-005, KB-006, KB-007, SP-030, SP-032]
priority: P3
wave: W5
bilingual: yes
bn_counterpart: KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md — equipment_type enum, requires_calibration, calibration_interval_months, next_calibration_due computed, calibration_certificate_ref as ISO audit evidence, tolerance_spec, status enum including out_of_calibration
    verified: 2026-08-16
    class: P1
  - source: ISO 9001:2015 clause 7.1.5 — monitoring and measuring resources; where measurement traceability is a requirement, equipment shall be calibrated or verified at defined intervals against traceable measurement standards, be identifiable as to calibration status, and be safeguarded from adjustments that would invalidate the calibration status
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M45_Enterprise_Asset_and_Test_Equipment.md — equipment register, calibration control and custody
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M59_Health_Safety_and_Wellbeing.md — duty of care, incident reporting
    verified: 2026-08-16
    class: P1
  - source: IEC 61010-1 measurement-category (CAT II / III / IV) principle for test and measurement equipment — an instrument's category and voltage rating must match the circuit it is applied to
    verified: 2026-08-16
    class: P2
supersedes: none
review_due: 2027-02-16
---

# KB-012 — Tool, Jig and Test Equipment Operating Guides

| Item | Value |
|---|---|
| Article type | **Procedure** (`tool_guide` article type) |
| Device family | Not device-scoped — **equipment-scoped**, bound to `MD-046` `equipment_code` |
| Brand / model scope | Per instrument make and model |
| Skill level required | Stated per instrument; some require competence before issue |
| Offline pack member | **Yes** — a bench card for each instrument the technician holds |
| Review due | 2027-02-16 · individual guides on a 24-month cycle (`KB-001` §4.2) |

> **Template conformance.** Procedure-type article applied at guide-set level; all
> `TPL_Knowledge_Article.md` sections retained in order. Sections 11–13 are justified additions,
> consistent with `KB-004` §11.

---

## 1. Purpose and Scope

**This is the only guide set in the category that is not about the customer's device.** It is about
the instrument in the technician's hand — and it exists because two failure modes cost the company
more than they appear to.

| Failure mode | Consequence | Why guidance fixes it |
|---|---|---|
| **The instrument injures the person using it** | A meter on the current range applied across a live supply; a probe rated below the circuit it touches; an unrated lead on a UPS DC bus | The instrument's own limits are the guidance; almost nobody reads the manual that came with it |
| **The instrument gives a confident wrong reading** | An out-of-calibration meter, a probe with a broken lead, a thermal camera with the wrong emissivity, a hot-air station whose sensor has drifted | A false reading is worse than no reading, because it terminates the diagnosis |

`MD-046` already governs the register: what equipment exists, who holds it, when it is due for
calibration, what its tolerance is, and whether it is `in_service` or `out_of_calibration`. **What
it cannot hold is how to use the thing.** That is this file.

**In scope:** the guide inventory by instrument class; the mandatory structure of a tool guide; the
pre-use check; measurement-category and rating rules; the calibration-status obligation on the
user; jig and fixture guidance; and the equipment-fault escalation route.

**Out of scope:**

| Subject | Owned by |
|---|---|
| The equipment register, calibration intervals, certificates and custody | [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) · `M45` |
| Asset classes, depreciation and capitalisation | `MD-044` · `M49` |
| Hazard data — ESD, chemical, battery, refrigerant | [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) |
| The repair procedures that use the instruments | `KB-004`…`KB-007` |
| Safety incident response | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) · `M59` |
| Branch equipment checks as a shift routine | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) |
| Purchasing and vendor selection of equipment | `M16` |

> **On the `P3` priority.** The register assigns this file `P3`/`W5` — the lowest priority in the
> category. That reflects when a *complete* guide set is needed. **It does not reflect the urgency
> of the safety subset**: the measurement-category rule (§6.3) and the pre-use check (§6.2) matter
> from the first day a technician holds a meter, which is W1. §12 splits the set accordingly, and
> the split is raised as an open item rather than left implicit in a priority code.

---

## 2. Safety

> ⛔ **DANGER — measurement category and voltage rating.** Applying an instrument, probe or lead
> rated below the circuit's measurement category and voltage to a live circuit can cause an arc
> flash inside the instrument and in the operator's hand (hazard). Severe burns, blindness, death
> (consequence). **Match the instrument's CAT rating and voltage to the circuit before touching it;
> never use a lead with damaged insulation; never use an instrument whose rating you cannot read**
> (avoidance). The principle is IEC 61010-1; the applicable rating is on the instrument.

> ⛔ **DANGER — a meter left on the current range.** Applying a multimeter still set to a current
> range across a voltage source creates a near-short through the meter (hazard). Arc flash and
> instrument destruction (consequence). **Return the meter to the voltage range after every current
> measurement; confirm the range and the lead positions before every connection** (avoidance). This
> is the single most common test-equipment injury mechanism and it is a two-second habit.

> ⚠ **WARNING — out-of-calibration equipment.** An instrument past its calibration due date may
> read confidently and wrongly (hazard). A wrong reading produces a wrong diagnosis, an unnecessary
> part, an unsafe pass on a verification test, or a missed insulation fault (consequence).
> **`MD-046` computes `next_calibration_due`; an instrument with `status: out_of_calibration` is
> withdrawn from use, not used carefully** (avoidance) — `TE-04`.

> ⚠ **WARNING — hot tools.** Soldering irons, hot-air stations, heat guns and preheaters operate at
> temperatures that ignite solvents and cause immediate burns (hazard). **Dedicated stand, fume
> extraction, no solvents on the bench in use, cool-down before storage** (avoidance).

> ⚠ **WARNING — refrigerant manifolds and recovery equipment.** Equipment must match the
> refrigerant class; A2L and A3 systems require class-appropriate equipment (hazard).
> **See `KB-013` §5 and `KB-005` `TG-20`** (avoidance).

> ⚠ **CAUTION — ESD equipment that is not working.** A wrist strap with a broken cord or a mat with
> a failed ground gives the *appearance* of ESD control while providing none (hazard). Latent
> component failures that return as rework (consequence). **Test the strap and mat at every shift
> start with the tester; a station that fails the test is out of service** (avoidance) — `KB-013` §3.

---

## 3. Symptoms — *the signals that equipment guidance is failing*

| Signal | What it indicates |
|---|---|
| Diagnoses reversed at a second bench with a different instrument | Instrument error, calibration drift, or misuse |
| A technician borrows a colleague's meter rather than using their own | Their own instrument is faulty, flat, or they do not trust it |
| Instruments failing calibration repeatedly at the same branch | Handling, storage or transport problem |
| Verification tests passing that should have failed | An instrument reading optimistically — **the most dangerous signal here** |
| Blown fuses in meters | The current-range mistake (§2) |
| Damaged leads still in use | No pre-use check |
| A jig produced locally with no drawing or approval | Uncontrolled tooling |
| A calibration certificate that cannot be produced at audit | `MD-046` `calibration_certificate_ref` empty — an ISO finding |

---

## 4. Likely Causes

| # | Cause | Frequency | Confirming test |
|---:|---|---|---|
| 1 | No guide exists for that instrument | **Highest initially** | Query `MD-046` against guide coverage (§12) |
| 2 | Guide exists but is not on the technician's device | High | Offline pack contents vs equipment issued |
| 3 | Calibration due date passed unnoticed | High | `MD-046` `next_calibration_due` vs use records |
| 4 | Instrument physically damaged in transit or in a van | **High for field instruments** | Pre-use check records |
| 5 | Wrong instrument for the measurement | Medium | Reading vs `tolerance_spec` |
| 6 | Settings wrong — range, emissivity, probe type, reference | Medium | Repeat measurement with a second instrument |
| 7 | Technician never trained on that instrument | Medium | `M22` competence vs equipment issued |
| 8 | Locally made jig with no specification | Medium | Jig register (§6.6) |

---

## 5. Diagnostic Procedure — *the pre-use sequence, and what to do with a suspect reading*

### 5.1 Pre-use check — `TE-02`

**Runs before the first measurement of every shift, and after any transport, drop or impact.**

| Step | Check | Fail action |
|---:|---|---|
| 1 | **Calibration status** — is `next_calibration_due` in the future, and is the status label on the instrument current? | **Withdraw from use** (`TE-04`) |
| 2 | Physical condition — case, display, leads, probes, insulation, connectors | Withdraw; report |
| 3 | Battery / power state | Replace; a low battery causes drift before it causes a warning |
| 4 | Function check against a known reference — a known voltage, a known resistance, a known temperature | Fails → withdraw and escalate |
| 5 | Range, mode and lead positions set for the intended measurement | Correct before connecting |
| 6 | For ESD stations: wrist strap and mat tested | Station out of service |
| 7 | For refrigerant equipment: correct class for the system | Do not connect |

### 5.2 When a reading is suspect

| Step | Action |
|---:|---|
| 1 | **Do not act on it.** A wrong reading that drives a part replacement costs more than the ten minutes to confirm it |
| 2 | Repeat with a fresh connection — most anomalies are connection, not component |
| 3 | Verify the instrument against a known reference |
| 4 | Repeat with a second instrument if one is available |
| 5 | If the instrument is suspect: withdraw it, record it, and **flag every measurement taken with it since its last verified check** |
| 6 | Escalate per §10 |

**`TE-03`: an instrument found faulty triggers a look-back.** Jobs measured with it since its last
known-good check are reviewed. This is uncomfortable and it is the only honest response — an
instrument that was wrong today was probably wrong yesterday.

---

## 6. Repair Procedure — *the structure and rules of a tool guide*

### 6.1 Mandatory guide structure

Every `tool_guide` article carries these blocks, in addition to the `KB-002` §4.2 skeleton:

| # | Block | Content |
|---:|---|---|
| 1 | Instrument identity | `MD-046` `equipment_code`, make, model, `equipment_type` |
| 2 | **Ratings and limits** | Measurement category, maximum voltage and current, temperature range, load limits — **stated before anything else** |
| 3 | What it is for, and what it is **not** for | The commonest misuse is applying a right instrument to a wrong job |
| 4 | Pre-use check | The §5.1 sequence, instrument-specific |
| 5 | Setup | Ranges, modes, references, emissivity, probe selection, zeroing |
| 6 | Operation | Numbered steps for the measurements this instrument is actually used for |
| 7 | Reading interpretation | **What a good reading looks like, and what the tolerance is** (`MD-046` `tolerance_spec`) |
| 8 | Calibration-check by the user | The field check the user performs between formal calibrations |
| 9 | Care, storage and transport | Field instruments live in vans; this block is why they survive |
| 10 | Consumables | Probes, tips, filters, batteries, fuses — **with the correct rating for fuses** |
| 11 | Fault symptoms of the instrument itself | How to tell it is failing |
| 12 | Competence required | Whether training is required before issue |

### 6.2 Governing rules

| # | Rule | Class |
|---|---|:--:|
| **TE-01** | Every instrument in `MD-046` with `requires_calibration: true` has a guide before it is issued | **H** |
| **TE-02** | The pre-use check runs at shift start and after transport or impact | **H** |
| **TE-03** | An instrument found faulty triggers a look-back on measurements since its last known-good check | **H** |
| **TE-04** | `status: out_of_calibration` means **withdrawn**, not "use with caution" | **H** |
| **TE-05** | Ratings and limits appear before operating instructions in every guide | **H** |
| **TE-06** | A guide states what the instrument is **not** for | **H** |
| **TE-07** | Fuse replacement states the exact rating and type; a general fuse in a meter defeats its protection (`KB-009` §6.4 class 1) | **H** |
| **TE-08** | Calibration adjustment is performed only by the accredited body in `MD-046` `calibration_body`; **a user never adjusts an instrument to make it agree** — ISO 9001 clause 7.1.5 requires safeguarding against adjustments that would invalidate calibration status | **H** |
| **TE-09** | Guides state the competence required, and equipment requiring competence is not issued without it (`M22`) | **H** |
| **TE-10** | Locally produced jigs and fixtures are registered, drawn and approved before use (§6.6) | **H** |
| **TE-11** | Guides are equipment-scoped, not device-scoped; the same meter serves every family | **H** |
| **TE-12** | Reading interpretation states the tolerance from `MD-046` `tolerance_spec`, not a remembered figure | **H** |
| **TE-13** | Every guide is available offline on the device of every technician issued that instrument | **C** |
| **TE-14** | Calibration status is visible to the user at the point of use, not only in the register | **C** |

### 6.3 Measurement category and rating — the rule that must be in every electrical guide

| Requirement | Detail |
|---|---|
| Match the instrument's category to the circuit | The higher the energy available at the measurement point, the higher the category required |
| Match the voltage rating to the circuit, not to the expected reading | A meter rated for the expected voltage but not the supply's fault energy is inadequate |
| Leads and probes carry their own ratings | **The assembly is only as good as its weakest part** — a CAT-rated meter with unrated leads is unrated |
| Damaged insulation voids the rating | Any nick, crack or exposed conductor withdraws the lead from service |
| Never exceed the stated limits to "just check" | The stated limit is where the protection was designed to hold |

**`TE-05` places this block before operating instructions in every guide** because a technician
reads the first screen and skims the rest.

### 6.4 Calibration — the user's obligations

`MD-046` owns the calibration programme. The user owns four things:

| Obligation | Detail |
|---|---|
| **Check the status before use** | `TE-02` step 1; ISO 9001 clause 7.1.5 requires calibration status to be identifiable, and identifiable means *someone identifies it* |
| **Perform the field check** | The between-calibration verification in guide block 8 |
| **Never adjust** | `TE-08` |
| **Report drift, damage or doubt** | §10; drift found early prevents the `TE-03` look-back being large |

### 6.5 Instrument classes and their guides

Bound to `MD-046` `equipment_type`:

| `equipment_type` | Typical instruments | Calibration | Guide priority |
|---|---|:--:|:--:|
| `multimeter` | Handheld DMM, clamp meter, insulation tester | ✔ | **P1 — safety-critical** |
| `oscilloscope` | Bench and handheld scopes | ✔ | P2 |
| `power_supply` | Bench PSU with current limit | ✔ | **P1 — used in every board diagnosis** |
| `rework_station` | Soldering iron, hot-air, preheater, IR station | ✔ (temperature) | **P1 — burn and damage risk** |
| `gauge` | Refrigerant manifold, pressure gauge, vacuum gauge | ✔ | **P1 — refrigerant safety** |
| `scale` | Refrigerant charging scale | ✔ | **P1 — charge by weight (`KB-005`)** |
| `thermometer` | Thermal camera, IR thermometer, probe thermometer | ✔ | P2 |
| `manifold` | Refrigerant service manifold, recovery machine | ✔ | **P1 — class-specific** |
| `other` | Cable certifier, network tester, microscope, ESD tester, torque driver, microwave leakage meter | ✔ where measuring | Varies — **microwave leakage meter is P1** |

### 6.6 Jigs, fixtures and locally made tooling

Workshops make things. A holding fixture, a test harness, a board support, a charging jig. This is
good practice and it is uncontrolled unless it is registered.

| Rule | Detail |
|---|---|
| **`TE-10`** | A jig used on customer devices is registered in `MD-046` as `equipment_type: other`, with a drawing or photograph, its purpose, its limits and its approver |
| Approval | Workshop Supervisor (R09) with Technical Director for anything electrical or load-bearing |
| Safety review | HSE Lead where it involves electrical, thermal, pressure or mechanical energy |
| Guide | A short guide is written before issue, even if it is one screen |
| Replication | A jig replicated to other branches carries its drawing and guide with it — **not a photograph in a chat message** |
| Withdrawal | A jig that causes damage is withdrawn network-wide, not locally |

---

## 7. Parts — *consumables, not spares*

Test equipment consumes items that are not `MD-022` spare parts for customer devices but are stock
nonetheless:

| Consumable | Note |
|---|---|
| Meter fuses | **Exact rating and type only** (`TE-07`) |
| Test leads and probes | Rated assemblies; replaced, not repaired |
| Soldering tips and nozzles | Wear affects thermal transfer and therefore repair quality |
| Solder, flux, wick, paste | `hazard_class: chemical`; `KB-013` §6 |
| ESD wrist cords, mats, testers | Consumable and testable; `KB-013` §3 |
| Refrigerant hoses, gaskets, filters | **Class-specific**; `KB-013` §5 |
| Calibration reference standards | Held by the accredited body, not by branches |
| Instrument batteries | Low battery causes drift before it causes a warning |

---

## 8. Verification and QC

| Test | Pass criterion | Recorded in |
|---|---|---|
| Every `requires_calibration` instrument has a guide | 100% (`TE-01`) | Coverage report (§12) |
| Guides carry ratings and limits before operation | 100% (`TE-05`) | Content review |
| Guides state what the instrument is not for | 100% (`TE-06`) | Content review |
| Reading tolerances match `MD-046` `tolerance_spec` | 100% (`TE-12`) | Cross-check |
| Pre-use checks recorded | Sampled; branch checklist under `SP-032` | Shift record |
| Instruments in use past `next_calibration_due` | **Zero** (`TE-04`) | `MD-046` exception report |
| Calibration certificates retrievable | 100% — **ISO audit evidence** (`MD-046` `calibration_certificate_ref`) | `M24` |
| `TE-03` look-backs performed when an instrument is found faulty | 100% | Quality record |
| ESD stations passing the shift test | 100% | Shift record |
| Registered jigs with drawing, approval and guide | 100% (`TE-10`) | `MD-046` |
| Guides present in the offline pack of every holder | > 98% (`TE-13`) | Pack telemetry |
| Equipment-related injuries | **Zero** | `M59`, `SP-030` |

---

## 9. Resolution Coding

A tool guide produces no `MD-025` resolution code. Two indirect effects:

| Effect | Detail |
|---|---|
| `calibrate` resolutions | Where a job's resolution is calibration of a **customer's** device, the instrument used must itself be calibrated and identifiable — the traceability chain ISO 9001 clause 7.1.5 requires |
| Rework attribution | Rework traced to a faulty or uncalibrated instrument is attributed to equipment, not to the technician — the same principle as `KB-011` `KW-17` |

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| An instrument is found out of calibration and in use | **Withdraw immediately**; Quality Manager; `TE-03` look-back | Instrument, use records |
| A reading cannot be trusted and no second instrument is available | Workshop Supervisor; **do not proceed on the doubtful reading** | The readings taken |
| An instrument fails its field check | Facilities/Asset custodian for calibration or repair; Quality informed | Check result |
| A lead, probe or instrument is damaged | Withdraw and replace; report — **never tape a lead** | Photograph |
| A meter fuse has blown | Investigate why before replacing; usually the current-range mistake (§2) | Circumstances |
| An instrument is used beyond its rating | **HSE Lead + Quality Manager**; treat as a near miss under `SP-030` | Circumstances |
| A locally made jig is found in use unregistered | Workshop Supervisor + Technical Director; register or withdraw | Photograph, usage |
| Calibration certificates cannot be produced at audit | Quality Manager — **this is an ISO 9001 finding** | `MD-046` records |
| Any injury involving equipment | **HSE immediately** (`SP-030`, `M59`) | Incident record |

---

## 11. Guide Inventory *(addition — justified: consistent with `KB-004` §11; a guide set with no enumerated membership cannot be resourced or measured)*

**22 guides**, scoped by `MD-046` `equipment_type` rather than by device family (`TE-11`).

| # | Guide | Class | Pri | Safety-gated |
|---:|---|---|:--:|:--:|
| 1 | **Digital multimeter — ratings, ranges, and the current-range rule** | `multimeter` | **P1** | ✔ |
| 2 | **Clamp meter and current measurement** | `multimeter` | P1 | ✔ |
| 3 | **Insulation resistance tester** | `multimeter` | **P1** | ✔ |
| 4 | **Bench power supply with current limiting — board diagnosis** | `power_supply` | **P1** | ✔ |
| 5 | Oscilloscope — setup, probing and safe connection | `oscilloscope` | P2 | ✔ |
| 6 | **Soldering iron — temperature, tips, fume extraction** | `rework_station` | **P1** | ✔ |
| 7 | **Hot-air rework station — profiles, shielding, damage limits** | `rework_station` | **P1** | ✔ |
| 8 | Preheater and IR station | `rework_station` | P2 | ✔ |
| 9 | Stereo microscope — setup and inspection technique | `other` | P2 | ✖ |
| 10 | **Refrigerant service manifold — class matching and connection** | `manifold` | **P1** | ✔ |
| 11 | **Refrigerant recovery machine — recovery, never venting** | `manifold` | **P1** | ✔ |
| 12 | **Vacuum pump and micron gauge — evacuation standard** | `gauge` | **P1** | ✔ |
| 13 | **Refrigerant charging scale — charge by weight** | `scale` | **P1** | ✔ |
| 14 | Leak detector — electronic, bubble and UV methods | `other` | P1 | ✔ |
| 15 | Thermal camera — emissivity, reflection and false readings | `thermometer` | P2 | ✖ |
| 16 | IR and probe thermometers | `thermometer` | P2 | ✖ |
| 17 | **ESD wrist strap, mat and tester — the shift check** | `other` | **P1** | ✔ |
| 18 | **Microwave leakage meter** | `other` | **P1** | ✔ |
| 19 | Cable certifier — network cabling test and report | `other` | P2 | ✖ |
| 20 | Network and PoE tester | `other` | P2 | ✖ |
| 21 | Torque driver and screwdriver sets — torque discipline | `other` | P2 | ✖ |
| 22 | **Battery isolation container and handling tools** | `other` | **P1** | ✔ |

**Set totals:** 22 guides · **13 at P1, all safety-gated** · 9 at P2 ·
**15 require HSE approval** under `BRU-KMS-03`.

---

## 12. The Priority Split *(addition — justified: the register's `P3`/`W5` placement does not match the safety subset's urgency, and the discrepancy must be stated rather than silently worked around)*

| Subset | Guides | Needed by | Rationale |
|---|---:|---|---|
| **Electrical safety subset** | 1, 2, 3, 4, 17 | **W1** | A technician holds a meter from the first week. The measurement-category and current-range rules are the difference between a safe measurement and an arc flash |
| **Refrigerant subset** | 10, 11, 12, 13, 14 | **W2**, with `KB-005` | Certification-gated work cannot begin without them |
| **Rework subset** | 6, 7, 8, 22 | **W2**, with `KB-006` | Board work and battery handling |
| **Verification subset** | 18, 19, 20 | W4 | Microwave leakage with `KB-005`; cabling with `KB-007` |
| **Remainder** | 5, 9, 15, 16, 21 | W5 | Matches the register's placement |

> **Stated openly under `CP-03`.** The Master Index places `KB-012` at `P3`/`W5` and this file does
> not change that unilaterally — `CM-R1` makes the register authoritative. What this section does
> is record that **five of the twenty-two guides are needed four waves earlier than the file is
> scheduled**, and route the discrepancy to the register owner as `O-01` and audit finding
> **KB-04**. A content file that quietly rewrote its own priority would be the drift this
> programme's audits exist to catch.

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | The register these guides serve; names `KB-012` as a consumer |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-044_Asset_Class_and_Depreciation_Schedule_Register.md) | Asset classification of equipment |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | §3 ESD station, §5 refrigerant, §6 chemicals |
| [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) | Refrigerant instruments and the microwave leakage test |
| [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) | Rework station and bench PSU |
| [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | Cable certifier and electrical instruments |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | §6.4 class 1 — fuses are never substituted |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-032_Operational_Checklist_Library.md) | Equipment check as a shift routine |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Equipment incidents and near misses |
| `M45` Enterprise Asset and Test Equipment · `M23` Quality Management System | Calibration control and ISO evidence |
| `TR-009` Course Pack — Field Technician · `TR-016` Quality and Field Auditor | Competence under `TE-09` |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `MD-046` — `equipment_type` enum, `requires_calibration`, `calibration_interval_months`, computed `next_calibration_due`, `calibration_certificate_ref` as ISO audit evidence, `tolerance_spec`, `status` enum; `KB-012` named as a consumer | 2026-08-16 | 2027-02-16 |
| ISO 9001:2015 clause 7.1.5 — calibration or verification at defined intervals against traceable standards, identifiable calibration status, safeguarding against invalidating adjustments | 2026-08-16 | 2027-08-16 |
| IEC 61010-1 measurement-category principle — instrument, probe and lead ratings must match the circuit | 2026-08-16 | 2027-08-16 |
| `M45`, `M23`, `M59` module specifications | 2026-08-16 | 2027-02-16 |

> **No instrument-specific figure is stated in this file** — no voltage rating, no temperature
> profile, no tolerance, no torque. All of those are instrument- and model-specific and belong in
> the authored guides with their own manufacturer sources (`AU-16`). `TE-12` requires tolerances to
> come from `MD-046` `tolerance_spec`, which is the controlled value.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The `P3`/`W5` register placement does not match the safety subset's urgency** (§12). Five guides are needed at W1. Either the register row is amended or a documented exception is recorded. Raised as audit finding **KB-04** | Programme Content Lead with Technical Director and HSE Lead | **W1** |
| **O-02** | **`MD-046` is not populated**, so §11 is scoped by `equipment_type` rather than by actual holdings. The guide count will change once the real equipment list exists | Facilities with Quality | Before authoring |
| **O-03** | `TE-14` requires calibration status to be visible **at the point of use**, not only in the register. Whether `P02`/`P03` surface it is unconfirmed; ISO 9001 clause 7.1.5 requires status to be identifiable | CTO with Quality Manager | **W2 — it is a certification requirement, not a convenience** |
| **O-04** | The accredited calibration bodies available in Bangladesh for each instrument class are not identified. `MD-046` has a `calibration_body` field and no populated list; without one, `TE-08` cannot be complied with | Facilities Manager with Quality Manager | **W2 — blocks the calibration programme** |
| **O-05** | The microwave radiation-leakage acceptance limit is unspecified — the same gap `KB-005` `O-04` records. Guide 18 cannot be written without it | HSE Lead with Technical Director | Before guide 18 |
| **O-06** | The 22 guides are unwritten. Estimated **90–200 hours** of technical and HSE time, lighter than the device guide sets but requiring HSE review on 15 of 22 | Technical Director with HSE Lead | Per the §12 split |
| **O-07** | Jig registration (`TE-10`) requires `MD-046` to accept locally produced tooling with a drawing reference. Whether the register's `equipment_type: other` and `M45` support that is unconfirmed | Facilities with MDM | W5 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] Scoped to equipment, not to device family (`TE-11`), and the boundary with `MD-046` stated
- [x] Safety blocks in three-part form, leading with measurement category and the current-range rule
- [x] Out-of-calibration defined as withdrawn, not "use with caution" (`TE-04`)
- [x] Look-back on faulty instruments made a rule, not a judgement (`TE-03`)
- [x] User calibration obligations stated against ISO 9001 clause 7.1.5, including the no-adjustment rule
- [x] Locally made jigs brought under control without prohibiting them
- [x] Guide inventory enumerated — 22 guides with class, priority and safety gating
- [x] **The register's `P3`/`W5` placement challenged openly and routed to its owner rather than silently overridden**
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9
- [x] No instrument-specific figure asserted without a controlled source
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` priority split resolved with the register owner — outstanding**
- [ ] **`O-04` accredited calibration bodies identified — outstanding; blocks the calibration programme**
- [ ] **The 22 guides authored — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director and HSE Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
