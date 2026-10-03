---
id: KB-006
title: Troubleshooting Guide Set — Mobile and Tablet
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical Services with Specialist Technicians (R12, mobile / board-level)
reviewers: [Quality Manager, Technical Director, HSE Lead, Legal Counsel, Knowledge Manager, Localisation Lead, Data Services Lead]
approver: Technical Director with Quality Manager
content_class: C
purpose: >
  The governing specification and article inventory for the mobile and tablet troubleshooting
  library — board-level, display, battery, charging, water damage and software recovery. These are
  high-value, high-risk repairs where the difference between an L2 escalation and an L3 escalation
  is knowledge, where every device holds the customer's entire personal life, and where a mainboard
  replacement changes the device's IMEI and therefore its right to connect to a Bangladeshi network.
traces_to: [M31, M01, M06, M17, M61, P02, P03, MD-021, MD-022, MD-024, MD-025, MD-031, KB-001, KB-002, KB-008, KB-013, SP-033, SP-012, SP-025]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md and M06_Data_Services_and_Secure_Data_Handling.md — bench repair and the separate data-handling service with its own custody chain
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-12 BER evidence and second technician; BRU-SRM-14 L3 board-level work restricted to equipped workshops and certified specialists; 05-04 T5 data-services access restricted to assigned cases
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/F_Asset_Equipment_and_Facilities/M17_Device_and_Customer_Asset_Registry.md and MD-021 MDL-02 — imei_applicable TRUE requires a 15-digit IMEI at intake
    verified: 2026-08-16
    class: P1
  - source: Bangladesh Telecommunication Regulatory Commission (BTRC) National Equipment Identity Register (NEIR) — handsets verified against a national IMEI registry, IMEI linked to SIM and NID; enforcement blocking unregistered and cloned-IMEI handsets from local networks from 16 December 2025
    verified: 2026-08-16
    class: P1
    note: Operational effect on mainboard replacement must be confirmed with BTRC or a named legal source before articles rely on it — see Open Item O-02
  - source: Lithium-battery handling — damaged, defective or recalled cells carry a materially higher risk of short circuit, heat release and thermal runaway than undamaged cells; damaged or defective lithium batteries are forbidden for transport by air
    verified: 2026-08-16
    class: P2
supersedes: none
review_due: 2027-02-16
---

# KB-006 — Troubleshooting Guide Set: Mobile and Tablet

| Item | Value |
|---|---|
| Article type | **Troubleshooting** (guide-set specification) |
| Device family | `DF-MB` — mobile and tablet |
| Brand / model scope | All serviced `DF-MB` models in `MD-021`; `imei_applicable` is TRUE for this family |
| Skill level required | L1 to **L3_board**; board-level restricted under `BRU-SRM-14` |
| Offline pack member | **Yes** |
| Review due | 2027-02-16 |

> **Template conformance.** Troubleshooting-type article applied at guide-set level; all
> `TPL_Knowledge_Article.md` sections retained in order. Sections 11–14 are justified additions,
> consistent with [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) §11.

---

## 1. Purpose and Scope

Three things make this family different from every other set in the library, and all three are
reasons the guidance must be written down rather than carried in a few people's heads.

| Distinguishing factor | Consequence for the guide set |
|---|---|
| **The device holds the customer's entire personal life** | Photographs, messages, banking apps, identity documents. Data handling is not a footnote to the repair; it is a parallel obligation with its own custody chain (`SP-012`, `05-04` T5) |
| **The repair economics are compressed** | A board-level repair can cost a large fraction of the device's value. The BER judgement is made on almost every job, not occasionally, and it must be consistent across 51+ branches |
| **The device's identity is regulated** | `imei_applicable` is TRUE for this family (`MD-021` `MDL-02`), and Bangladesh operates a national IMEI registry. **A mainboard replacement changes the IMEI.** See §6.1 |

**In scope:**

| Sub-family | `MD-021` category | Dominant failure classes |
|---|---|---|
| Smartphone | `CAT-SMARTPHONE` | Display, battery, charging, water damage, board-level, software |
| Feature phone | `CAT-FEATUREPHONE` | Charging, keypad, display, battery |
| Tablet | `CAT-TABLET` | Display, battery, charging, connector, software |
| Smartwatch and wearable | `CAT-WEARABLE` | Battery, display, water ingress, charging contact |

**Out of scope:**

| Subject | Owned by |
|---|---|
| Laptops, desktops, printers, monitors, projectors, UPS | [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) |
| Data recovery as a chargeable service, and secure erasure | `M06` · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) |
| Trade-in grading, refurbishment and resale | `M14` · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) |
| Manufacturer diagnostic codes and DFU/recovery states | [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) |
| Battery chemistry, storage and incident data | [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) §4 |
| Intake triage and routing | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) |

---

## 2. Safety

> ⚠ **WARNING — lithium cells in a thin, glued, curved package.** Smartphone and tablet batteries
> are pouch cells held by adhesive and are punctured easily during removal (hazard). A punctured or
> crushed cell can enter thermal runaway within seconds, producing fire and toxic gas in a
> workshop with other devices on the bench (consequence). **Use the manufacturer's removal method —
> adhesive-release tabs, isopropyl alcohol, or a controlled-heat pad — never a metal pry tool
> against the cell; discharge below 30% before removal where practicable; keep the steel battery
> container within arm's reach** (avoidance). Full data in `KB-013` §4.

> ⚠ **WARNING — a swollen battery is a live hazard, not a fault to be fixed.** A swollen cell is
> already failing (hazard). Charging it, puncturing it, or leaving it in a general bin risks fire
> (consequence). **Isolate immediately in the steel container, record it, do not recharge, do not
> re-fit, route to the e-waste stream under `SP-026`** (avoidance). **Damaged, defective or
> recalled lithium batteries are forbidden for transport by air**, which constrains inter-branch
> movement — see §7.

> ⚠ **CAUTION — hot-air rework and glued assemblies.** Display and back-glass removal uses
> controlled heat close to a lithium cell and to flex cables (hazard). Burns, cell damage and
> destroyed flex circuits (consequence). **Use the model's stated temperature and dwell; shield the
> battery; never apply heat over the cell area** (avoidance).

> ⚠ **CAUTION — ESD.** Every board in this family is ESD-sensitive, and micro-scale components are
> the least tolerant in the library (hazard). Latent failures that return as rework (consequence).
> **Grounded ESD workstation per `KB-013` §3, IEC 61340-5-1 / ANSI-ESD S20.20** (avoidance).

> ⚠ **CAUTION — glass and display shards.** Cracked displays shed fine glass (hazard). Cuts and
> eye injury (consequence). **Tape the panel before removal; eye protection; contained disposal**
> (avoidance).

> ⚠ **CAUTION — flux, solvents and IPA.** Rework chemicals are flammable and produce fumes
> (hazard). Respiratory irritation and fire (consequence). **Fume extraction at the rework station;
> no ignition sources; storage per `KB-013` §6** (avoidance).

> **NOTICE — customer data is the default state of this family.** Every device arrives holding the
> customer's data. Do not browse, copy, photograph or retain it. Access is restricted to assigned
> cases (`05-04` T5) and any recovery is a separate consented service (`SP-012`).

> **NOTICE — device identity.** IMEI is a regulated identifier. See §6.1 before any mainboard
> replacement.

**`TG-01` applies.** **`TG-27` (this set): every article involving battery removal, hot-air work or
chemicals requires the `M61` §9 `BRU-KMS-03` safety approval.**

---

## 3. Symptoms

| Symptom (EN) | Symptom (BN) | `SYM-` binding | Level | First route |
|---|---|---|:--:|---|
| Does not power on | চালু হচ্ছে না | `SYM-00101` | L2→L3 | Bench |
| Not charging | চার্জ নিচ্ছে না | `SYM-` power-charge | L1→L3 | Bench |
| Battery drains rapidly | চার্জ দ্রুত শেষ হয়ে যায় | `SYM-` battery-life | L1 | Bench |
| **Battery swollen / back cover lifting** | ব্যাটারি ফুলে গেছে | `SYM-` battery-swell | **L1 — safety stop** | **Immediate isolation** |
| Screen cracked | স্ক্রিন ভেঙে গেছে | `SYM-` display-physical | L1 | Bench |
| Display blank, device responds | ডিসপ্লে কালো, কিন্তু চালু আছে | `SYM-` display-blank | L2 | Bench |
| Touch not responding | টাচ কাজ করছে না | `SYM-` touch | L2 | Bench |
| Lines or discolouration on screen | স্ক্রিনে দাগ / রঙ সমস্যা | `SYM-` display-artefact | L1→L2 | Bench |
| **Liquid damage** | পানি পড়েছে | `SYM-` liquid | **L2→L3** | **Bench, immediate, do not power on** |
| No network / no SIM detected | নেটওয়ার্ক পাচ্ছে না | `SYM-` network | L2→L3 | Bench |
| No sound / speaker or mic fault | শব্দ আসছে না | `SYM-` audio | L1→L2 | Bench |
| Camera not working | ক্যামেরা কাজ করছে না | `SYM-` camera | L1→L2 | Bench |
| Overheating | অতিরিক্ত গরম হচ্ছে | `SYM-` thermal | L2→L3 | Bench |
| Stuck on logo / boot loop | লোগোতে আটকে আছে | `SYM-` boot | L2 | Bench, software first |
| Very slow / apps crashing | ধীর গতি / অ্যাপ বন্ধ হয়ে যায় | `SYM-` performance | L1 | Remote triage first |
| Charging port loose or damaged | চার্জিং পোর্ট আলগা | `SYM-` connector | L2 | Bench |
| Buttons unresponsive | বাটন কাজ করছে না | `SYM-` input | L1→L2 | Bench |
| Water-resistance lost after repair | মেরামতের পর পানি ঢুকছে | `SYM-` seal | L2 | Bench — **see `TG-30`** |
| Device locked / credentials unknown | ডিভাইস লক, পাসওয়ার্ড জানা নেই | `SYM-` locked | L1 | **Ownership verification — §10** |

**`TG-02` applies.**

---

## 4. Likely Causes

| Symptom | # | Likely cause | Frequency | Confirming test |
|---|---:|---|---|---|
| Not charging | 1 | Charging port lint, wear or damage | **Highest** | Visual under magnification; clean and retest |
| | 2 | Cable or adapter fault | High | Known-good cable and adapter |
| | 3 | Battery at end of life | High | Cycle count and health reading |
| | 4 | Charging IC / PMIC fault | Medium | Current draw on bench PSU; rail measurement |
| | 5 | Board corrosion from prior liquid ingress | Medium | Visual under microscope |
| Does not power on | 1 | Battery fully depleted or failed | High | Bench PSU boot with battery isolated |
| | 2 | Power-rail short | Medium | Rail resistance to ground |
| | 3 | Software / firmware failure | Medium | Recovery or DFU-equivalent mode responds |
| | 4 | Liquid corrosion on the power path | Medium | Visual + rail measurement |
| Display blank, device responds | 1 | Display flex seating or damage | High | Reseat; external indication of activity |
| | 2 | Panel failure | High | Known-good panel test |
| | 3 | Display driver on board | Medium | Signal presence at connector |
| Touch not responding | 1 | Digitiser damage | High | Known-good panel |
| | 2 | Touch IC — commonly after a drop | Medium | Board-level test |
| | 3 | Non-genuine panel incompatibility | **Rising** | Genuine panel test (`KB-009`) |
| Liquid damage | 1 | Corrosion on board and connectors | **Highest** | Microscope inspection after cleaning |
| | 2 | Battery compromised by ingress | High | Cell inspection — **safety first** |
| | 3 | Latent failure appearing weeks later | High | Set expectation with the customer at intake |
| No network | 1 | SIM tray, contacts or SIM itself | High | Known-good SIM |
| | 2 | Antenna flex or connector | Medium | Continuity |
| | 3 | Baseband / RF section | Medium | L3 board-level |
| | 4 | **IMEI not registered / device blocked on the network** | **Rising — see §6.1** | Check on another network; NEIR verification |
| Boot loop | 1 | Software or update failure | **Highest** | Recovery mode; reflash after consent |
| | 2 | Storage (UFS/eMMC) failure | Medium | Board-level test |
| | 3 | Power-rail instability under load | Medium | Rail measurement |
| Overheating | 1 | Runaway app or background process | High | Behaviour in safe mode |
| | 2 | Battery degradation | High | Health reading |
| | 3 | Board-level short drawing excess current | Medium | Current draw measurement |

---

## 5. Diagnostic Procedure

The five-phase shape (`TG-03`, `KB-004` §5) applies, with two mandatory additions.

| Phase | Mobile-specific requirement |
|---:|---|
| **0 — Safety and custody** | Battery swelling and heat check · liquid-indicator check · **ownership and data-consent capture** · warranty check · condition capture with photographs |
| **0b — Identity capture** *(this set only)* | **Record the IMEI at intake, before any work** (`MDL-02`). Photograph it from the device, the tray, or the packaging. This is the baseline against which any post-repair identity question is answered |
| **1 — Reproduce** | With the customer's own accessories where possible; a large share of "not charging" is a cable |
| **2 — Isolate** | Accessory → software → assembly → board, in that order. Software isolation before disassembly saves the majority of unnecessary teardowns |
| **3 — Measure** | Bench PSU current draw, rail resistance, board-level signal tracing under magnification |
| **4 — Conclude** | Coded fault, resolution, parts, estimate, **BER assessment where indicated** |
| **5 — Post-repair identity and seal check** *(this set only)* | IMEI unchanged or, if changed, handled per §6.1; water-resistance integrity stated honestly (`TG-30`) |

### 5.1 Worked diagnostic — device does not power on

| Step | Phase | Action | Expected | If not |
|---:|:--:|---|---|---|
| 1 | 0 | Inspect for swelling, heat, liquid indicator, burning smell | None | **Stop.** Isolate per `KB-013` §4; `SP-030` if a thermal event; inform the customer of special handling |
| 2 | 0b | **Record and photograph the IMEI** | Captured | If unreadable, record that fact — it becomes material later |
| 3 | 0 | Capture ownership evidence and data-handling consent | Recorded | Do not proceed on a device whose ownership is unestablished — §10 |
| 4 | 1 | Charge on a known-good adapter and cable for 20 minutes; observe any indication | Any sign of life | Go to step 5 |
| 5 | 2 | Force-restart / recovery-mode entry per the model's procedure | Enters recovery | **Software fault** — go to the software article; consent required before any reflash |
| 6 | 2 | Open per the model procedure; **battery inspection and isolation first** | Battery sound | Swollen or damaged → article 3, safety route |
| 7 | 2 | Test with a known-good battery | Boots | Fault isolated to **battery** |
| 8 | 3 | **ESD station.** Board on bench PSU at rated voltage, current limited | Current draw within the model's stated range | Go to step 9 |
| 9 | 3 | Zero draw | — | Open circuit — check charging port, filters, fuses |
| 10 | 3 | High draw at rest | — | Short — measure each rail to ground; localise under a microscope with thermal camera or freeze spray |
| 11 | 3 | Localised | — | If not, **escalate to a second L3** (§10); do not remove components speculatively |
| 12 | 4 | Assess repair cost against device value; if BER likely, **photographic evidence and second-technician confirmation** (`BRU-SRM-12`) | Customer decision recorded (`RES-05`) | — |
| 13 | 5 | If the mainboard was replaced, **§6.1 applies before the device is returned** | IMEI position resolved and recorded | Do not return the device with an unresolved identity question |
| 14 | 4 | Record `FLT-`, `RES-`, parts, standard time | Coded outcome | `FLT-UNK` permitted (`SP-033` `DT-02`) |

---

## 6. Repair Procedure

Rules `TG-05`…`TG-14` from `KB-004` §6 apply. This set adds:

| # | Rule |
|---|---|
| **TG-27** | Battery, hot-air and chemical articles carry the `BRU-KMS-03` safety approval |
| **TG-28** | Battery removal states the model's adhesive-release method; **prying a pouch cell with a metal tool is prohibited in every article in this set** |
| **TG-29** | Any procedure that erases customer data requires recorded consent before it starts (`SP-012`); a reflash is never performed "to test" without it |
| **TG-30** | **Water resistance is not restored by a repair unless the manufacturer's seal, adhesive and pressure-test procedure is followed in full.** Every article opening a sealed device states this plainly, and the customer is told. Claiming restored ingress protection without the test is a misrepresentation |
| **TG-31** | Non-genuine display and battery assemblies may disable features, trigger warnings or fail pairing. The article states the known effect per model family and the `part_class` implication (`KB-009`) |
| **TG-32** | **`TG-33` (identity) is mandatory reading before any mainboard-level article is executed** |
| **TG-33** | **IMEI is never altered, reprogrammed, cloned or masked, under any circumstances, by any person, for any reason.** See §6.1 |
| **TG-34** | Liquid-damage articles set the expectation of latent failure with the customer in writing before work begins |
| **TG-35** | Micro-soldering articles state the required equipment; `BRU-SRM-14` restricts execution to an equipped workshop and a certified specialist |

### 6.1 Device identity, mainboard replacement and NEIR

**This is the rule in this guide set most likely to be broken by a technically competent
technician acting in good faith.**

The IMEI is bound to the mainboard, not to the chassis. Replacing a mainboard therefore returns to
the customer a device with a **different IMEI from the one they brought in**. Bangladesh operates a
national IMEI verification regime — the BTRC **National Equipment Identity Register (NEIR)** —
which checks handset IMEIs against a national registry and links them to SIM and NID records, with
enforcement blocking unregistered and cloned-IMEI handsets from local networks from 16 December
2025.

| Situation | Required handling |
|---|---|
| Mainboard replaced under manufacturer warranty | The brand's own replacement process governs; record both IMEIs on the job and on the `DT-007` service report |
| Mainboard replaced outside warranty | **Inform the customer before work begins** that the IMEI will change and what that means for their registration. Record their acknowledgement. Record both IMEIs |
| Device presents with an IMEI that appears blocked or unregistered | **Do not proceed on the assumption it is a fault to be fixed.** Escalate per §10; this is an ownership and registration matter, not a repair |
| Any request — from a customer, a colleague, or anyone else — to change, restore, clone or mask an IMEI | **Refuse. Escalate to the branch manager and Quality Manager immediately.** `TG-33` admits no exception |
| Device whose IMEI is unreadable at intake | Record the fact at intake with a photograph of the attempt. Do not "reconstruct" it |

> **Why this sits in a knowledge article and not only in a policy.** A policy that a technician
> reads once at induction does not reach the bench at 7 p.m. when a customer is upset that their
> repaired phone has no signal. The rule belongs in the article the technician is actually reading
> at that moment, which is what `KB-016` reference card **`REF-` IMEI and device identity** exists
> to guarantee.

> **Currency caution (`CG-012`).** NEIR is a live regulatory programme with a recent enforcement
> date and an implementation history that has shifted. **The precise operational consequence of a
> warranty mainboard swap under NEIR has not been confirmed with BTRC or with named legal counsel
> for this programme** — `O-02`. The prohibition in `TG-33` does not depend on that confirmation
> and stands regardless.

---

## 7. Parts

| Rule | Detail |
|---|---|
| Identification and class | `MD-022` `part_code`, `manufacturer_part_no`, `part_class`. **`part_class` matters more in this family than any other** — non-genuine displays and batteries change device behaviour (`TG-31`) |
| Genuine-part effects | Feature loss, warning messages, failed pairing, disabled biometrics. Documented per model family in [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) |
| Hazard class | `lithium` batteries and `esd_sensitive` boards; handling per `KB-013` §3 and §4 |
| **Transport constraint** | **Damaged, defective or recalled lithium batteries are forbidden for transport by air.** Inter-branch and reverse-logistics movement of swollen or damaged cells must use surface routes with the packaging and segregation rules in `KB-013` §4 — this constrains `SP-009` reverse logistics |
| Consignment | Brand-supplied warranty parts cannot be consumed on non-warranty jobs (`BRU-WTY-04`) |
| Serialisation | Boards and some display assemblies are serialised; serial captured at receipt and issue (`BRU-INV-08`) |

**High-movement part families**

| Family | Note |
|---|---|
| Display assemblies (OLED and LCD) | Highest-value, highest-volume part; `part_class` effects are significant |
| Batteries | `hazard_class: lithium`; storage state-of-charge and container rules apply |
| Charging port / flex sub-boards | Highest-frequency L2 part |
| Back glass and adhesive/seal kits | Required for any `TG-30` claim of restored sealing |
| Cameras and camera flexes | Model-specific |
| Speakers, receivers, microphones | Low value, high frequency |
| SIM trays and readers | Interacts with the identity issues in §6.1 |
| Board-level components — PMIC, charging IC, touch IC, filters | **L3_board only** |
| Adhesives, flux, solvents, IPA | `hazard_class: chemical`; `KB-013` §6 |

---

## 8. Verification and QC

| Repair class | Test | Pass criterion | Recorded in |
|---|---|---|---|
| Battery replacement | Charge cycle | Charges to full; health reading within the manufacturer's tolerance; **no heat, no swelling over a 30-minute observed charge** | Repair order |
| Display replacement | Full function sweep | Touch across the whole surface, brightness, colour, biometrics (where display-bound), proximity and ambient sensors, no dead pixels beyond tolerance | Photograph attached |
| Charging port | Charge and data | Charges at rated current; data connection enumerates; connector mechanically secure | Repair order |
| Board-level (L3) | Rail and load | All rails in specification; current draw in range; device runs a sustained load for **30 minutes** without thermal excursion | Repair order + photograph |
| Liquid damage | Extended soak test | Full function after **48 hours** of powered observation where the customer's timeline allows; latent-failure expectation restated at handover | Repair order + customer acknowledgement |
| Software / reflash | Function and data | Device boots, network registers, customer's declared critical functions verified; **consent record present** | Repair order + consent |
| Network / RF | Registration test | Registers on network with a known-good SIM; signal within expected range | Repair order |
| **Sealed devices** | **Seal integrity** | Manufacturer's pressure test passed **or the customer is told in writing that water resistance is not warranted** (`TG-30`) | `DT-007` service report |
| **All** | **Identity** | IMEI recorded at intake matches at handover; if changed, §6.1 handling recorded | Repair order + `DT-007` |
| **All** | Data | Customer data intact where the repair did not require erasure; erasure consented and recorded where it did | `SP-012` |
| **All** | Cosmetic and completeness | Condition matches or improves on the intake capture; all screws and seals fitted | `DT-004` condition report |

---

## 9. Resolution Coding

| `action_class` | Mobile-specific note |
|---|---|
| `replace_part` | The dominant outcome. Part issue required — `RES-02` blocks closure otherwise |
| `repair` | Board-level and connector repair. `standard_minutes` feeds [`KB-014_Repair_Time_Standards_and_Labour_Norms.md`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) |
| `configure` | Software resolution, reflash, settings. **Frequently under-recorded because it feels like "not a repair"** — it is a resolution and must be coded |
| `clean` | Charging-port cleaning is a very common genuine resolution; code it |
| `no_fault_found` | Common on intermittent and performance complaints. Supervisor countersignature (`RES-04`) |
| `beyond_economic_repair` | **The most frequently used BER route in the library.** `BRU-SRM-12` photographic evidence and second-technician confirmation; customer decision recorded (`RES-05`); offer the trade-in route (`SP-025`) where appropriate |
| `customer_declined` | Reason from `MD-026`; very common when the estimate approaches device value |

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| Board fault does not localise after phase 3 | Second L3 specialist | Rail readings, current draw, microscope and thermal images |
| L3 required and no certified specialist or equipped bench is available | Equipped workshop (`BRU-SRM-14`) | Diagnosis and codes |
| **Any request to alter, restore or clone an IMEI** | **Branch manager and Quality Manager immediately** (`TG-33`) | The request, recorded |
| Device presents with a blocked or unregistered IMEI | Branch manager; treat as a registration and ownership matter | Intake IMEI photograph |
| **Ownership cannot be established** on a locked device | Branch manager; do not attempt bypass | Intake record |
| Customer requests bypass of a lock or account credential | **Refuse and escalate.** This is not a technical judgement | Request, recorded |
| Swollen or thermally damaged battery | Isolate; HSE informed if any thermal event (`SP-030`) | Photograph, container record |
| BER likely | Second technician confirms (`BRU-SRM-12`); then customer decision | Photographs, cost build-up |
| Data on the device may have been accessed beyond need | Data Services and Security (`SP-012`, `05-04` T5) | Access record |
| Repeat of the same device and fault within 30 days | Rework flag (`BRU-SRM-06`) | Both jobs |
| A pattern appears across a model | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | Occurrence data |

---

## 11. Guide Set Inventory *(addition — justified as in `KB-004` §11)*

**36 articles.**

### 11.1 Safety and identity — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 1 | **Lithium pouch-cell handling, removal and swollen-battery isolation** | `safety_note` | L1 | **P0** |
| 2 | **IMEI and device identity — capture, mainboard replacement, and the absolute prohibition** | `safety_note` | L1 | **P0** |
| 3 | **Ownership verification and locked-device handling** | `procedure` | L1 | **P0** |
| 4 | Customer-data handling during mobile repair — consent, access limits, erasure | `procedure` | L1 | **P0** |
| 5 | Hot-air, flux and solvent safety at the rework bench | `safety_note` | L2 | P1 |

### 11.2 Power, battery and charging — 7 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 6 | Device does not power on — full isolation path | `fault_fix` | L2→L3 | P0 |
| 7 | Not charging — port, cable, battery, charging IC | `fault_fix` | L1→L3 | P0 |
| 8 | Battery replacement by adhesive type and chassis family | `procedure` | L1→L2 | P0 |
| 9 | Battery health assessment and honest life expectation | `procedure` | L1 | P1 |
| 10 | Charging-port and sub-board replacement | `procedure` | L2 | P1 |
| 11 | Board-level power-rail diagnosis on a bench PSU | `technique` | **L3_board** | P1 |
| 12 | Charging IC and PMIC replacement | `technique` | **L3_board** | P2 |

### 11.3 Display and touch — 6 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 13 | Display assembly replacement — OLED and LCD, by chassis family | `procedure` | L1→L2 | P0 |
| 14 | Blank display with device responding — flex, panel, driver | `fault_fix` | L2 | P1 |
| 15 | Touch faults and touch-IC diagnosis | `fault_fix` | L2→L3 | P1 |
| 16 | **Non-genuine display effects by model family** | `known_issue` | L1 | P1 |
| 17 | Back-glass removal and re-sealing | `procedure` | L2 | P2 |
| 18 | Display verification sweep | `reference_card` | L1 | P1 |

### 11.4 Liquid damage — 4 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 19 | **Liquid-damage first response — what not to do, and what to tell the customer** | `procedure` | L1 | **P0** |
| 20 | Ultrasonic cleaning and corrosion assessment | `procedure` | L2 | P1 |
| 21 | Board-level corrosion repair and trace reconstruction | `technique` | **L3_board** | P2 |
| 22 | Latent-failure expectation setting and follow-up | `how_to` | L1 | P1 |

### 11.5 Board-level and RF — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 23 | Micro-soldering fundamentals — equipment, technique, limits | `technique` | **L3_board** | P1 |
| 24 | No network / no SIM — SIM path, antenna, baseband | `fault_fix` | L2→L3 | P1 |
| 25 | Overheating and excess current draw | `fault_fix` | L2→L3 | P2 |
| 26 | Storage (UFS/eMMC) failure diagnosis and the data consequence | `fault_fix` | **L3_board** | P2 |
| 27 | When **not** to attempt a board-level repair — the BER and escalation boundary | `procedure` | L2 | P1 |

### 11.6 Software — 4 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 28 | Boot loop and recovery-mode diagnosis | `fault_fix` | L2 | P1 |
| 29 | Reflash and firmware recovery — **consent first** | `procedure` | L2 | P1 |
| 30 | Performance and battery-drain diagnosis without reinstalling | `how_to` | L1 | P2 |
| 31 | Update-failure and storage-full faults | `fault_fix` | L1 | P2 |

### 11.7 Components and assemblies — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 32 | Camera and camera-flex replacement | `procedure` | L1→L2 | P2 |
| 33 | Speaker, receiver and microphone faults | `fault_fix` | L1→L2 | P2 |
| 34 | Button, vibration and sensor faults | `fault_fix` | L1→L2 | P2 |
| 35 | Tablet-specific disassembly and display handling | `procedure` | L2 | P2 |
| 36 | Wearable battery, seal and charging-contact service | `procedure` | L2 | P3 |

**Set totals:** 36 articles · 8 at P0 · 15 at P1 · 12 at P2 · 1 at P3 ·
**11 require `L3_board` competence** and are restricted under `BRU-SRM-14` ·
**8 carry the `BRU-KMS-03` safety gate**.

---

## 12. Authoring Plan, Coverage and Orphans

| Item | Position |
|---|---|
| Articles required | **36** |
| Articles written | **0** |
| Authoring effort, estimated | 36 × 4–12 hours of R12 mobile-specialist time = **145–430 specialist hours**, plus review and translation |
| **Author scarcity** | `05-04` records **15–30 R12 specialists across the whole company** and `M61` §2 states the board-level capability sits with perhaps fifteen to thirty people. The 11 `L3_board` articles can only be written by that group, who are simultaneously the people doing the hardest repairs |
| Sequencing | 8 P0 before W2 · 15 P1 before W4 · remainder before W6 |
| Bengali | All bilingual; safety and identity articles human-translated and re-approved |
| Coverage | `DF-MB` is expected to be a large share of the top-100 fault codes by volume |

> **This set is the clearest illustration of `M61`'s founding argument.** The module exists because
> *"senior technicians retire with undocumented expertise"* and because that expertise is
> concentrated in fifteen to thirty people. The eleven `L3_board` articles here **are** that
> expertise. Every month they remain unwritten is a month the company carries a capability risk it
> has already identified, rated High, and not yet resourced.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | §3 ESD, §4 lithium, §6 chemicals — the data behind every safety block |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Non-genuine part effects (`TG-31`) |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | Recovery states and diagnostic codes |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | Model-level recurring defects |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | The IMEI and battery-safety cards |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) | Shared rules `TG-01`…`TG-16` |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | Data consent and custody |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-025_SOP_TradeIn_Refurbishment_and_Resale.md) | The BER alternative |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) | Constrained by the damaged-battery transport rule in §7 |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-021_Device_Category_Make_and_Model_Catalogue.md) | `imei_applicable` and `MDL-02` |
| `TR-009` Course Pack — Field Technician · `TR-005` Question Bank | Train and assess this set |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M31`, `M06`, `M17` module specifications | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-06`, `-12`, `-14`; `BRU-INV-08`; `BRU-WTY-04` · `05-04` T5 data-services restriction | 2026-08-16 | 2027-02-16 |
| `MD-021` `MDL-02` — `imei_applicable` TRUE requires a 15-digit IMEI at intake | 2026-08-16 | 2027-02-16 |
| BTRC **NEIR** — national IMEI registry, IMEI linked to SIM and NID; enforcement blocking unregistered and cloned-IMEI handsets from local networks from **16 December 2025** | 2026-08-16 | **2027-02-16 — live regulatory programme, currency check required** |
| Lithium-battery risk and transport — damaged, defective or recalled cells carry materially higher short-circuit and thermal-runaway risk; **forbidden for transport by air** | 2026-08-16 | 2027-08-16 |
| IEC 61340-5-1 / ANSI-ESD S20.20 | 2026-08-16 | 2027-08-16 |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The 36 articles are unwritten; 145–430 specialist hours unallocated, and the 11 `L3_board` articles can only be authored by the 15–30 people who are the capability risk `M61` was created to address** | Technical Director with PMO | **8 P0 before W2** |
| **O-02** | **The operational effect of NEIR on a mainboard replacement is unconfirmed with BTRC or named counsel.** §6.1 states the handling conservatively; the customer-communication wording needs a legal review before publication. `CG-013` escalation applies | Legal Counsel with Technical Director | **W2 — before article 2 is published** |
| **O-03** | `MD-024` symptom codes unallocated for most §3 entries; placeholders shown, **not minted** (`KA-02`) | Technical analyst (MDM) | Before authoring |
| **O-04** | The damaged-battery surface-transport packaging standard is not specified anywhere in the content set. §7 states the air prohibition; the permitted route needs a named standard in `KB-013` §4 | HSE Lead with Logistics | **W3 — before reverse logistics carries damaged cells** |
| **O-05** | Non-genuine part effects (`TG-31`) require per-model-family documentation that does not exist. `KB-009` owns it; the data must be gathered from actual repairs | Technical Director with Inventory | W4 |
| **O-06** | Ownership-verification evidence standards for locked devices are not defined in any `LG` or `SP` file reviewed. Article 3 needs them and cannot invent them | Legal Counsel with Operations Director | **W2 — blocks article 3** |
| **O-07** | Bengali technical terminology for board-level mobile repair is the least-established of any family (`KB-002` O-05) | Localisation Lead with R12 | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] The three distinguishing factors of this family stated and carried through the set
- [x] Safety blocks in three-part form, covering lithium, hot-air, ESD, glass and chemicals
- [x] **Device-identity rule stated as an absolute prohibition with an escalation route (`TG-33`)**
- [x] NEIR position sourced, dated, and explicitly marked as requiring legal confirmation
- [x] Water-resistance honesty rule stated (`TG-30`)
- [x] Data consent required before any erasing operation (`TG-29`)
- [x] Damaged-battery air-transport prohibition carried into the parts and logistics rules
- [x] Verification criteria numeric or observable, including an identity check
- [x] Article inventory enumerated — 36 articles with type, level, priority and gating
- [x] Author-scarcity constraint stated against the `05-04` R12 population
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-SRM-*`, `BRU-INV-*`, `BRU-WTY-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 36 articles authored — outstanding**
- [ ] **`O-02` NEIR legal position confirmed — outstanding; blocks the identity article**
- [ ] **`O-06` ownership-verification standard defined — outstanding; blocks the locked-device article**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Technical Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
