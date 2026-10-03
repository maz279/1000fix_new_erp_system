---
id: KB-004
title: Troubleshooting Guide Set — IT and Computing
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical Services with Specialist Technicians (R12, computing)
reviewers: [Quality Manager, Technical Director, HSE Lead, Knowledge Manager, Localisation Lead, Inventory Manager]
approver: Technical Director with Quality Manager
content_class: C
purpose: >
  The governing specification and article inventory for the IT and computing troubleshooting
  library — laptop, desktop, printer, monitor, projector and UPS. This is the largest service
  category by volume, so consistency here is the single largest determinant of the first-time-fix
  rate. Without a governed guide set, 200–400 technicians diagnose the same fault by personal habit
  and the fault taxonomy records five different causes for one failure.
traces_to: [M31, M01, M61, M17, P02, P03, MD-021, MD-022, MD-024, MD-025, KB-001, KB-002, KB-008, KB-013, SP-033, SP-010]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-004_Troubleshooting_Guide_Set_IT_and_Computing_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md — bench diagnosis, WIP control, L1/L2/L3 escalation, QC gate
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61 §5.1 FR-KMS-001/011 — article types and required sections; §9 BRU-KMS-02/03 review and safety gates
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-12 beyond economic repair requires photographic evidence and a second technician; BRU-SRM-14 L3 board-level work restricted to equipped workshops and certified specialists
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02 — KPI-004 first-time fix 70% baseline, 82% W7, 88% W9
    verified: 2026-08-16
    class: P1
  - source: IEC 61340-5-1 / ANSI-ESD S20.20 — ESD control programme requirements for handling electrostatic-discharge-sensitive devices; the two standards are technically equivalent
    verified: 2026-08-16
    class: P2
supersedes: none
review_due: 2027-02-16
---

# KB-004 — Troubleshooting Guide Set: IT and Computing

| Item | Value |
|---|---|
| Article type | **Troubleshooting** (guide-set specification) |
| Device family | `DF-IT` — IT and computing |
| Brand / model scope | All serviced `DF-IT` models in `MD-021`; brand-specific procedures carry a `brand` facet |
| Skill level required | L1 to L3_board, stated per article |
| Offline pack member | **Yes** — this set is the largest single contributor to the `P02` pack |
| Review due | 2027-02-16 |

> **Template conformance.** Troubleshooting-type article, applied at **guide-set level**. All
> `TPL_Knowledge_Article.md` sections are retained in order and answered for the set rather than
> for one fault. Sections 11–14 are additions and are justified where they appear. The individual
> `KNW-` articles this file governs each conform to the template at article level and to `KB-002`.

---

## 1. Purpose and Scope

**In scope:** the six `DF-IT` sub-families below; the symptom-to-article map; the governing rules
`TG-01`…`TG-14` shared by all four guide sets; the diagnostic sequences that every article in this
set must follow; the article inventory (§11); and the authoring plan (§12).

| Sub-family | `MD-021` category | Typical monthly volume driver | Dominant failure classes |
|---|---|---|---|
| Laptop | `CAT-LAPTOP` | Highest single volume in the category | Power, display, thermal, storage, liquid damage |
| Desktop and all-in-one | `CAT-DESKTOP` | Corporate estates, `P04` contracts | PSU, storage, memory, thermal, OS |
| Printer and imaging | `CAT-PRINTER` | Branch and corporate estates | Paper feed, print quality, fuser, cartridge, firmware |
| Monitor and display | `CAT-MONITOR` | Moderate | Backlight, panel, T-CON, power board |
| Projector | `CAT-PROJECTOR` | Low volume, high value | Lamp/laser, optical block, thermal, colour wheel |
| UPS (desktop and small rack) | `CAT-UPS` | Rising with corporate estates | **Battery — see `KB-013`**, inverter, charging circuit |

**Out of scope, with the boundary stated explicitly:**

| Subject | Owned by | Where the line sits |
|---|---|---|
| Rack servers, RAID and NAS arrays, enterprise networking, CCTV, large UPS | [`KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md`](KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV.md) | **Form factor and blast radius.** A device that, when it fails, takes down one user is here. A device that takes down a client's business is in `KB-007` |
| Smartphones and tablets | [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) | `DF-MB` family |
| Televisions, AC, refrigeration, laundry, cooking | [`KB-005_Troubleshooting_Guide_Set_Home_Appliance.md`](KB-005_Troubleshooting_Guide_Set_Home_Appliance.md) | `DF-HA` family |
| Manufacturer fault-code interpretation | [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | Codes are mapped there; guides *use* the mapping |
| Triage before diagnosis — counter, phone, remote | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | `SP-033` routes; `KB-004` repairs |
| Workshop process — bench assignment, WIP, QC gate, release | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | Process vs technical content |
| Data recovery from a failed drive | `M06` · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | A separate chargeable service with its own custody chain |

> **The `KB-004` / `KB-007` boundary is stated because the Master Index register description for
> `KB-004` names "server and storage" and the description for `KB-007` names "rack server,
> RAID/NAS".** Read literally, both own the same device. The blast-radius rule above resolves it,
> and it is recorded here rather than left to the two authoring teams to discover. This is raised
> as audit finding **KB-01**.

---

## 2. Safety

> ⛔ **DANGER — mains and stored energy.** Desktop PSUs, monitor power boards, printer fusers and
> UPS units retain lethal charge on primary-side capacitors after disconnection, and UPS inverters
> can present mains voltage **with the unit unplugged** (hazard). Contact causes death or serious
> injury (consequence). Isolate, wait the discharge interval stated in the model's `LIB-` service
> manual, and confirm with a meter before touching any primary-side component. On a UPS, **isolate
> the battery as well as the mains** (avoidance).

> ⚠ **WARNING — lithium and sealed lead-acid batteries.** Laptop and UPS batteries can enter
> thermal runaway if punctured, crushed, short-circuited or charged while damaged (hazard). Fire
> and toxic gas release (consequence). Handle per
> [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md)
> §4; a swollen cell is isolated in the steel container immediately and never re-charged
> (avoidance).

> ⚠ **WARNING — printer fuser.** A fuser assembly operates above 180 °C and remains dangerous for
> several minutes after power-off (hazard). Contact burns (consequence). Allow the manufacturer's
> stated cool-down before opening the fuser path (avoidance).

> ⚠ **CAUTION — ESD.** Every board-level component in this family is ESD-sensitive (hazard). A
> discharge below the human perception threshold can cause a *latent* failure that returns as
> rework weeks later (consequence). Work at a grounded ESD workstation with wrist strap and mat
> per `KB-013` §3, in line with IEC 61340-5-1 / ANSI-ESD S20.20 (avoidance).

> **NOTICE — customer data.** Do not power on, image, or browse a customer's storage beyond what
> diagnosis requires. Data access is governed by `SP-012` and `05-04`; unnecessary access is a
> data-protection matter, not a technical shortcut.

> **NOTICE — warranty.** Opening a sealed device outside the manufacturer's authorised procedure
> can void the customer's manufacturer warranty. Check `MD-031` coverage before disassembly and
> record the check.

**`TG-01`: every article in this set repeats the hazard blocks relevant to its own procedure.**
A technician reads the article, not this file.

---

## 3. Symptoms

The set's symptom index. Every entry binds to an `MD-024` `SYM-` code (`KA-02`); Bengali is the
customer-facing wording and is authoritative for `P01` selection.

| Sub-family | Symptom (EN) | Symptom (BN) | `SYM-` binding | First route (`SP-033`) |
|---|---|---|---|---|
| Laptop | Does not power on | চালু হচ্ছে না | `SYM-00101` | Bench |
| Laptop | Powers on, no display | চালু হয় কিন্তু স্ক্রিনে কিছু আসে না | `SYM-` display-blank | Bench |
| Laptop | Shuts down under load / overheats | গরম হয়ে বন্ধ হয়ে যায় | `SYM-` thermal | Bench |
| Laptop | Battery not charging / drains quickly | চার্জ হচ্ছে না / দ্রুত শেষ হয়ে যায় | `SYM-` power-charge | Bench, **battery safety check first** |
| Laptop | Keyboard or trackpad unresponsive | কীবোর্ড / টাচপ্যাড কাজ করছে না | `SYM-` input | Bench, L1 |
| Laptop | Liquid spilled | পানি / তরল পড়েছে | `SYM-` liquid | **Bench L2, immediate, do not power on** |
| Laptop / Desktop | Very slow / freezes | খুব ধীর গতি / আটকে যায় | `SYM-` performance | Remote triage first |
| Laptop / Desktop | Noisy fan | ফ্যানের শব্দ | `SYM-` acoustic | Bench L1 |
| Desktop | No power, no fan | কোনো পাওয়ার নেই | `SYM-00101` | Bench |
| Desktop | Beep codes / POST failure | বিপ শব্দ হয়, চালু হয় না | `SYM-` post-fail | Bench — **see `KB-008`** |
| Desktop | Random restarts | নিজে নিজে রিস্টার্ট হয় | `SYM-` stability | Bench |
| Printer | Paper jam, repeated | বারবার কাগজ আটকে যায় | `SYM-` feed | On-site or bench |
| Printer | Print quality — streaks, banding, fading, ghosting | প্রিন্ট পরিষ্কার হচ্ছে না | `SYM-` print-quality | On-site L1 |
| Printer | Not detected on network | নেটওয়ার্কে পাওয়া যাচ্ছে না | `SYM-` connectivity | Remote first |
| Printer | Error code on panel | প্যানেলে এরর কোড দেখাচ্ছে | `SYM-` coded-fault | **`KB-008` lookup** |
| Monitor | No display, power LED on | পাওয়ার আছে কিন্তু ছবি নেই | `SYM-` display-blank | Bench |
| Monitor | Dim / flickering backlight | স্ক্রিন অস্পষ্ট / কাঁপে | `SYM-` backlight | Bench L2 |
| Monitor | Lines, dead pixels, discolouration | স্ক্রিনে দাগ / রঙ ঠিক নেই | `SYM-` panel | Bench — usually panel, assess BER |
| Projector | No image / lamp fault | ছবি আসছে না | `SYM-` optical | Bench L2 |
| Projector | Colour wheel noise, image shadow | রঙ ঠিক নেই / ছায়া পড়ে | `SYM-` optical | Bench L2 |
| UPS | Beeping continuously | অনবরত বিপ শব্দ | `SYM-` alarm | On-site — **`KB-008` code lookup** |
| UPS | No backup time | ব্যাকআপ দিচ্ছে না | `SYM-` runtime | On-site L1, battery test |
| UPS | Output dead, mains present | মেইন আছে কিন্তু আউটপুট নেই | `SYM-` output | Bench L2 |

> **`TG-02`: the symptom index is the set's contract with `MD-024`.** Every symptom a customer can
> select in `P01`, or an agent can record at intake, resolves to at least one article in this set,
> or is explicitly recorded as an orphan in §12. There is no third state.

---

## 4. Likely Causes

Ranked by observed frequency where history exists, and marked `estimated` where it does not.
**Every article inherits the obligation to rank and to name a confirming test (`AU-08`).**

| Symptom | # | Likely cause | Frequency | Confirming test |
|---|---:|---|---|---|
| Laptop no power | 1 | Charger or DC jack failure | High | Known-good charger; jack continuity and mechanical play |
| | 2 | Battery failure preventing boot | High | Boot on mains with battery removed |
| | 3 | Board power-rail fault (short, load switch, PMIC) | Medium | Rail resistance to ground; current draw on bench PSU |
| | 4 | Liquid damage corrosion | Medium in monsoon | Visual + liquid indicator |
| | 5 | Firmware / EC lock-up | Low | EC reset per model procedure |
| Laptop no display | 1 | Display cable seating or damage | High | External monitor test |
| | 2 | Backlight or panel failure | High | Torch test at an angle |
| | 3 | GPU / VRAM fault | Medium | External output also fails |
| | 4 | RAM seating or failure | Medium | Reseat, single-module test |
| Laptop thermal shutdown | 1 | Dust-blocked heatsink | **Highest — seasonal** | Visual; airflow test |
| | 2 | Degraded thermal paste / pad | High | Temperature curve under load |
| | 3 | Fan failure or bearing wear | Medium | Fan RPM under load |
| | 4 | Malware or runaway process | Medium | Load profile before/after clean boot |
| Battery not charging | 1 | **Cell degradation — check for swelling first** | High | Cycle count, design vs full charge capacity |
| | 2 | Charging circuit / sense resistor | Medium | Charge current measurement |
| | 3 | Non-genuine charger negotiation failure | Medium | Genuine charger test |
| Printer repeated jam | 1 | Worn pickup roller / separation pad | **Highest** | Roller surface, page count vs service interval |
| | 2 | Paper stock — humidity, weight, curl | High in monsoon | Fresh sealed ream test |
| | 3 | Registration or fuser drive fault | Medium | Jam location mapping |
| | 4 | Foreign object in path | Medium | Full path inspection |
| Print quality | 1 | Cartridge / toner at end of life or non-genuine | **Highest** | Genuine cartridge swap |
| | 2 | Drum or transfer roller wear | High | Defect repeat interval measurement |
| | 3 | Fuser wear | Medium | Smear test |
| | 4 | Laser / scanner optics contamination | Medium | Optical path inspection |
| Monitor no display | 1 | Power board capacitors | **Highest** | Visual bulge + ESR |
| | 2 | Backlight LED string open | High | Torch test; string voltage |
| | 3 | T-CON board | Medium | Panel self-test pattern |
| | 4 | Panel — usually **beyond economic repair** | Medium | Assess per `BRU-SRM-12` |
| UPS no backup | 1 | Battery end of life | **Highest** | Load test against rated runtime |
| | 2 | Charging circuit fault | Medium | Charge voltage measurement |
| | 3 | Inverter / relay fault | Medium | Transfer test |

---

## 5. Diagnostic Procedure

**`TG-03`: every article in this set follows the same five-phase shape.** Phases are not optional
and are not reordered. A technician who has read one article in this set can read any of them.

| Phase | What happens | Why it is in this position |
|---:|---|---|
| **0 — Safety and custody** | Hazard check (swelling, liquid, burning smell, heat), warranty check, data-sensitivity check, condition capture | A hazardous device must never reach the bench queue. Mirrors `SP-033` `DT-03` and `SP-007` intake |
| **1 — Reproduce** | Confirm the reported symptom with the customer's own accessories where possible | Half of "no power" is a charger the customer left at home. Reproducing prevents a no-fault-found that costs a full bench slot |
| **2 — Isolate** | Substitution and division: known-good charger, external display, single RAM module, minimal boot | Isolation before instrumentation. It is faster and needs no L3 competence |
| **3 — Measure** | Instrumented tests: bench PSU current draw, rail resistance, temperature curve, ESR, load test | Only where phase 2 has narrowed the field. Measurement without a hypothesis is how bench hours disappear |
| **4 — Conclude** | A `FLT-` fault code, a `RES-` resolution, a parts list, an estimate input, or a BER assessment | The article's outcome must be codeable, or the taxonomy learns nothing from the repair |

### 5.1 Worked diagnostic — laptop does not power on

Illustrating the five phases at the depth every `procedure` and `fault_fix` article in this set
must reach. **This is the pattern; the authored articles carry the model-specific values.**

| Step | Phase | Action | Expected | If not |
|---:|:--:|---|---|---|
| 1 | 0 | Inspect for swelling, liquid ingress, burning smell, heat | None present | **Stop.** Isolate per `KB-013` §4; notify customer of special handling; `SP-030` if a battery event |
| 2 | 0 | Check `MD-031` warranty coverage and record it | Coverage state recorded | Proceed, but disassembly may void manufacturer warranty — inform the customer first |
| 3 | 1 | Connect a known-good charger of correct wattage and polarity; observe charge LED for 15 minutes | LED indicates charging | Go to step 5 |
| 4 | 1 | Attempt power-on | Boots | **Not a fault** — customer's charger. Resolve at counter; do not raise a bench job |
| 5 | 2 | Remove battery (where removable); attempt boot on mains only | Boots | Fault isolated to **battery**; go to §6 battery procedure |
| 6 | 2 | Perform the model's EC / power reset per its `LIB-` entry | Boots | Continue |
| 7 | 2 | Reseat RAM and storage; attempt single-module boot | Boots | Continue |
| 8 | 3 | **ESD station required.** Board on bench PSU at rated voltage, current limited | Current draw within the model's stated idle range | Go to step 9 |
| 9 | 3 | Zero or near-zero current draw | — | Open circuit — check DC jack continuity, input protection, fuse |
| 10 | 3 | High current draw at rest | — | Short — measure each rail's resistance to ground; identify the shorted rail |
| 11 | 3 | Localise the short: thermal camera or freeze spray under limited current | A single component heats | If nothing localises, escalate to a second L3 (§10) |
| 12 | 4 | Record the `FLT-` code, `RES-` code, `repair_level`, parts and standard time | Coded outcome | **`FLT-UNK` is permitted** (`SP-033` `DT-02`); an honest unknown beats a fabricated code |

> **Step 4 exists to protect capacity.** A branch that raises a bench job for every customer who
> forgot their charger consumes the workshop slots the SLA depends on. `TG-04` requires every
> article in this set to contain at least one explicit **not-a-fault** exit.

---

## 6. Repair Procedure

**`TG-05`: repair content lives in the individual `KNW-` articles, never in this file.** This
section states the rules those articles obey; §11 lists them.

| # | Rule for every repair article in this set |
|---|---|
| **TG-06** | State `repair_level` as the level competent for the **hardest** step, not the average (`KA-06`) |
| **TG-07** | L3_board procedures state the equipment required; `BRU-SRM-14` restricts them to an equipped workshop and a certified specialist |
| **TG-08** | Every step carries its specification where one exists — torque, temperature, dwell, voltage, clearance — with a source (`AU-16`) |
| **TG-09** | Reassembly is written as its own numbered sequence, never "reverse the above". Reassembly is where cables are pinched and screws are mislocated |
| **TG-10** | Screw maps are mandatory for any procedure with more than one screw length. A long screw in a short hole punctures a board |
| **TG-11** | Firmware and BIOS steps state the recovery path **before** the update step |
| **TG-12** | Any procedure that erases or may erase customer data carries a `NOTICE` block and requires the customer consent recorded under `SP-012` |
| **TG-13** | Consumable and wear-part service intervals are stated where the manufacturer publishes them (printer rollers, fusers, projector filters) |
| **TG-14** | Where the economically correct answer is replacement rather than repair, the article says so — with the BER route under `BRU-SRM-12` |

### 6.1 Battery-specific procedure rule

A swollen, punctured or heat-damaged battery is **never** re-charged, never re-fitted, and never
placed in general waste. It is isolated per `KB-013` §4, recorded, and routed to the e-waste stream
under `SP-026` with the disposal certificate required by `BRU-ESG-03`. This is repeated in every
battery-touching article in this set.

---

## 7. Parts

| Rule | Detail |
|---|---|
| Part identification | Every part named by `MD-022` `part_code` and `manufacturer_part_no`, never by description alone |
| Part class | `part_class` stated — `oem` / `oem_equivalent` / `compatible` / `refurbished`. **It affects warranty and claim eligibility** |
| Compatibility | Compatibility comes from `MD-022` `compatible_models`; substitution notes from [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) |
| Hazard class | `lithium` and `esd_sensitive` parts carry their handling reference to `KB-013` |
| Issue control | Parts cannot be issued against an unapproved paid repair (`BRU-SRM-11`, `BRU-INV-01`) |
| Brand consignment | Brand-supplied warranty parts cannot be consumed on non-warranty jobs (`BRU-WTY-04`) |
| Serialised parts | Serial captured at both receipt and issue (`BRU-INV-08`) |

**High-movement part families in this set** — used for van stock and branch min/max seeding, and
for the pre-monsoon and academic-season stocking review:

| Family | Sub-family | Note |
|---|---|---|
| Laptop batteries | Laptop | `hazard_class: lithium`; storage state-of-charge rules in `KB-013` |
| DC jacks and charging boards | Laptop | Highest-frequency L2 part |
| Keyboards and trackpad flexes | Laptop | Model-specific; high SKU count |
| Thermal paste and pads | Laptop, Desktop | Consumable; not a warranty part |
| Cooling fans | Laptop, Desktop, Projector | Seasonal demand spike |
| SSD / HDD | Laptop, Desktop | **Data-handling implications — `SP-012`** |
| Power supply units | Desktop | |
| Pickup rollers and separation pads | Printer | Wear part with a published service interval |
| Fuser assemblies | Printer | High value; check economics against replacement |
| Backlight LED strips, T-CON, power boards | Monitor | Panel replacement is usually BER |
| Projector lamps / laser modules, filters | Projector | High value; count hours |
| UPS batteries (SLA) | UPS | `hazard_class: chemical`; disposal route mandatory |

---

## 8. Verification and QC

**`TG-15`: no article in this set is complete without a numeric or observable pass criterion**
(`AU-12`). Verification feeds the `SP-010` QC gate; a repair that passes the article but fails the
gate indicates the article's criterion is too weak.

| Repair class | Test | Pass criterion | Recorded in |
|---|---|---|---|
| Power (laptop / desktop) | Load test | Boots and holds under sustained load for **30 minutes**; current draw within the model's stated range | Repair order |
| Board-level (L3) | Rail measurement | All rails within specification, unpowered and powered | Repair order + photograph |
| Battery replacement | Charge cycle | Charges to full and reports design capacity within the manufacturer's tolerance; **no heat, no swelling** | Repair order |
| Thermal | Temperature curve | Sustained load temperature below the manufacturer's throttle threshold for **20 minutes** | Repair order |
| Display / panel | Test-pattern sweep | Full pattern set with no dead pixels in the agreed tolerance, no backlight bleed beyond tolerance | Photograph attached |
| Printer feed | Duplex run | **50 pages duplex, zero jams** | Repair order |
| Print quality | Reference print | Manufacturer test page matches the reference at the agreed tolerance | Print attached or photographed |
| Monitor power board | Extended run | 2 hours with no flicker, no shutdown | Repair order |
| Projector | Optical check | Full brightness and uniformity, lamp/laser hours reset where applicable | Repair order |
| UPS | Runtime test | Achieves rated runtime at rated load within tolerance; clean transfer on mains loss | Repair order |
| **All** | Cosmetic and completeness | All screws fitted, no missing covers, condition matches or improves on intake capture | `DT-004` condition report |
| **All** | Data integrity | Customer data intact where the repair did not require replacement; erasure consented and recorded where it did | `SP-012` |

---

## 9. Resolution Coding

| `MD-025` `action_class` | When to use in this set | Notes |
|---|---|---|
| `repair` | Component-level repair on an existing part | The `standard_minutes` on the code feeds [`KB-014_Repair_Time_Standards_and_Labour_Norms.md`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) |
| `replace_part` | A part was replaced | Part issue must exist — `RES-02` blocks closure otherwise |
| `replace_unit` | Whole-unit replacement under warranty or contract | Usually a brand or contract decision, not a technical one |
| `configure` | Software, firmware, driver, network or settings resolution | The commonest printer and performance outcome |
| `clean` | Dust, thermal service, optical path, paper path | Very common; **must still carry a fault code** |
| `calibrate` | Colour, registration, sensor calibration | Requires calibrated equipment — `MD-046` |
| `no_fault_found` | Symptom not reproducible after full diagnosis | **Requires a supervisor countersignature** (`RES-04`) |
| `customer_declined` | Estimate declined | Record the reason from `MD-026` |
| `beyond_economic_repair` | Repair cost exceeds the agreed threshold against value | **Photographic evidence and a second technician's confirmation** (`BRU-SRM-12`); customer decision recorded (`RES-05`) |

> **`TG-16`: `clean` is a resolution, not an absence of one.** A dust-blocked heatsink is the most
> frequent cause of laptop thermal shutdown in this market and it must be coded, or the analytics
> will show thermal faults with no cause and capacity planning will never see the seasonal spike.

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| Board fault does not localise after phase 3 | A second L3 specialist (`R12`) | Rail readings, current draw, thermal image |
| Repair requires L3 and no certified specialist is on site | An equipped workshop (`BRU-SRM-14`) | Diagnosis, codes, customer expectation reset |
| Brand warranty work and the technician's certification is not current | Reassign — the assignment is blocked (`BRU-SRM-09`, `BRU-HRM-01`) | Certification status |
| BER appears likely | Second technician confirms; then customer decision (`BRU-SRM-12`) | Photographs, cost build-up |
| Repeat of the same device and fault within 30 days | Auto-flagged as rework (`BRU-SRM-06`); Quality review | Original and current job |
| Estimate exceeds BDT 5,000 / BDT 25,000 | Customer approval / customer + branch manager approval (`BRU-SRM-07`, `BRU-SRM-08`) | Estimate record |
| A pattern appears across units of the same model | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md); consider a brand query | Occurrence count, serials, dates |
| A manufacturer fault code is unmapped | [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) — map it before closing | Code, model, observed behaviour |
| A battery, thermal or electrical safety event occurs | **HSE immediately** (`SP-030`), then Quality | Incident record, photographs |
| Customer data is at risk or has been accessed beyond need | Data Services + Security (`SP-012`, `05-04`) | Access record |

---

## 11. Guide Set Inventory *(addition — justified: the register entry for `KB-004` names a "guide set"; a set with no enumerated membership cannot be scoped, resourced or measured)*

**42 articles.** Priorities are for authoring order, on the `P0`–`P3` module scale.

### 11.1 Laptop — 14 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 1 | Laptop does not power on — isolation to charger, battery, jack or board | `fault_fix` | L1→L3 | P0 |
| 2 | Laptop powers on, no display — panel, cable, backlight, GPU | `fault_fix` | L1→L2 | P0 |
| 3 | Laptop thermal shutdown and throttling — clean, repaste, fan | `procedure` | L1 | P0 |
| 4 | Laptop battery does not charge — safety check, cell, circuit, charger | `fault_fix` | L1→L2 | P0 |
| 5 | **Swollen or damaged laptop battery — isolation and disposal** | `safety_note` | L1 | **P0** |
| 6 | Liquid-damaged laptop — first response, ultrasonic clean, corrosion repair | `procedure` | L2→L3 | P1 |
| 7 | Keyboard and trackpad replacement by chassis type | `procedure` | L1 | P1 |
| 8 | Display panel and hinge replacement | `procedure` | L1→L2 | P1 |
| 9 | Storage replacement, cloning and data-handling consent | `procedure` | L1 | P1 |
| 10 | DC jack and charging board replacement | `procedure` | L2 | P1 |
| 11 | Board-level power-rail diagnosis on a bench PSU | `technique` | **L3_board** | P1 |
| 12 | Reballing and BGA rework — when it is and is not appropriate | `technique` | **L3_board** | P2 |
| 13 | BIOS/EC recovery and firmware failure handling | `procedure` | L2 | P2 |
| 14 | Post-repair verification and QC for laptops | `procedure` | L1 | P1 |

### 11.2 Desktop and all-in-one — 7 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 15 | Desktop no power — PSU, board, front panel isolation | `fault_fix` | L1→L2 | P1 |
| 16 | POST failure and beep-code interpretation *(links `KB-008`)* | `fault_fix` | L1→L2 | P1 |
| 17 | Random restart and stability faults — PSU, thermal, memory | `fault_fix` | L2 | P1 |
| 18 | Memory and storage diagnosis and replacement | `procedure` | L1 | P1 |
| 19 | Desktop thermal service | `procedure` | L1 | P2 |
| 20 | All-in-one disassembly and display service | `procedure` | L2 | P2 |
| 21 | OS, driver and performance resolution without reinstalling | `how_to` | L1 | P2 |

### 11.3 Printer and imaging — 9 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 22 | Repeated paper jam — roller, pad, path, stock | `fault_fix` | L1 | P0 |
| 23 | Print-quality diagnosis by defect signature and repeat interval | `fault_fix` | L1→L2 | P0 |
| 24 | **Fuser service and safe handling** | `procedure` | L2 | P1 |
| 25 | Pickup roller and separation pad replacement by model family | `procedure` | L1 | P1 |
| 26 | Network printer not detected — discovery, driver, firewall, firmware | `fault_fix` | L1 | P1 |
| 27 | Cartridge, toner and consumable authenticity and end-of-life | `procedure` | L1 | P1 |
| 28 | Panel error-code interpretation *(links `KB-008`)* | `fault_fix` | L1→L2 | P1 |
| 29 | Inkjet head cleaning, purge and when to stop | `procedure` | L1 | P2 |
| 30 | Scanner and ADF feed and image faults | `fault_fix` | L1 | P2 |

### 11.4 Monitor and display — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 31 | Monitor no display — power board, backlight, T-CON isolation | `fault_fix` | L2 | P1 |
| 32 | **Power-board capacitor replacement and stored-energy safety** | `procedure` | L2 | P1 |
| 33 | Backlight LED strip replacement | `procedure` | L2 | P2 |
| 34 | Panel defect assessment and the BER decision | `procedure` | L1 | P2 |
| 35 | Display test-pattern verification set | `reference_card` | L1 | P2 |

### 11.5 Projector — 3 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 36 | Lamp and laser module service, hour reset, thermal path | `procedure` | L2 | P2 |
| 37 | Optical block, colour wheel and filter service | `procedure` | L2 | P2 |
| 38 | Projector image-fault diagnosis | `fault_fix` | L2 | P3 |

### 11.6 UPS (desktop and small rack) — 4 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 39 | **UPS safety — isolation, stored energy, battery handling** | `safety_note` | L1 | **P0** |
| 40 | Battery end-of-life test and replacement | `procedure` | L1 | P1 |
| 41 | UPS alarm-code interpretation *(links `KB-008`)* | `fault_fix` | L1 | P1 |
| 42 | Inverter, charger and transfer-relay diagnosis | `fault_fix` | L2 | P2 |

**Set totals:** 42 articles · 4 at P0 · 20 at P1 · 17 at P2 · 1 at P3 · **3 safety-gated**
(articles 5, 24, 32, 39 carry `hazard_class` ≠ `none` and require the `BRU-KMS-03` second
approval — four articles, and the count is stated as four here because article 24 is fuser-thermal
rather than battery-electrical; see `KB-013`).

---

## 12. Authoring Plan, Coverage and Orphans *(addition — justified: `M61` §16.4 states the content is a separate programme from the build; the plan must exist somewhere and this is the file that owes it)*

| Item | Position |
|---|---|
| Articles required | **42** |
| Articles written | **0** — this file is the set's specification |
| Authoring effort, estimated | 42 articles × 4–10 hours of R12 specialist time = **170–420 specialist hours**, plus review and translation |
| Sequencing | The 4 P0 articles before W2 `P02` release; the 20 P1 before W4; remainder by W6 |
| Bengali | Every article bilingual; safety articles human-translated and HSE re-approved (`AU-06f`, `AU-33`) |
| Coverage target | Contributes to `M61` KPI-C61-01 top-100 fault-code coverage; `DF-IT` is the largest share of that 100 |
| Orphan register | Symptoms in §3 with no article at the review date are listed here and ranked by job volume |

> **The honest position.** `M61` §16.4 states that reaching the coverage KPI requires 150–250
> authored articles across all families and that *"a knowledge module delivered empty will be
> judged a failure regardless of how well it works."* This set is 42 of those. The specialist time
> to write them is **not currently allocated** — the same gap `SP-033` records as O-01 for the 36
> diagnostic trees, and the same one `M61` Q-01 raises as blocking for its KPI targets. Recorded
> here as `O-01` rather than absorbed silently.

---

## 13. Related Documents *(addition — justified: category convention)*

| Document | Relationship |
|---|---|
| [`KB-001_Knowledge_Architecture_and_Tagging_Standard.md`](KB-001_Knowledge_Architecture_and_Tagging_Standard.md) | Facets every article in this set carries |
| [`KB-002_Article_Template_and_Authoring_Standard.md`](KB-002_Article_Template_and_Authoring_Standard.md) | The shape each article takes |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | Beep codes, panel codes, UPS alarms |
| [`KB-009_Parts_Compatibility_and_Substitution_Notes.md`](KB-009_Parts_Compatibility_and_Substitution_Notes.md) | Substitution decisions in §7 |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | Model-level recurring defects found through this set |
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | Every safety block's underlying data |
| [`KB-014_Repair_Time_Standards_and_Labour_Norms.md`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) | Standard times for these procedures |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | Which of these 42 become offline cards |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | The process these guides run inside |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-033_Diagnostic_and_Triage_Decision_Tree_Library.md) | Triage that routes into this set |
| [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-024_Fault_Symptom_and_Diagnostic_Code_Taxonomy.md) · [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | Codes every outcome resolves to |
| `TR-009` Course Pack — Field Technician · `TR-005` Question Bank — Technician Certification | Train and assess against this set |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M31` Workshop and Depot Repair Management — bench diagnosis, L1/L2/L3 escalation, QC gate | 2026-08-16 | 2027-02-16 |
| `M61` §5.1 FR-KMS-001/011, §9 `BRU-KMS-02`/`-03` | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-06`, `-07`, `-08`, `-09`, `-11`, `-12`, `-14`; `BRU-INV-01`, `-08`; `BRU-WTY-04` | 2026-08-16 | 2027-02-16 |
| `06-02` `KPI-004` first-time fix 70% → 82% (W7) → 88% (W9) | 2026-08-16 | 2027-02-16 |
| IEC 61340-5-1 / ANSI-ESD S20.20 — technically equivalent ESD control programme standards | 2026-08-16 | 2027-08-16 |
| `MD-021` §2.1 device families; `MD-022` `part_class` and `hazard_class`; `MD-025` `action_class` | 2026-08-16 | 2027-02-16 |

> **Model-specific values are deliberately absent from this file.** Torque figures, rail voltages,
> current ranges, service intervals and discharge times belong in the authored articles with their
> own `LIB-` sources, per `AU-16`. Publishing an unsourced number here and citing it 42 times would
> propagate one unverified figure across the whole set.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The 42 articles are unwritten and the specialist authoring time is unallocated** — 170–420 R12 hours. Same root cause as `M61` Q-01 and `SP-033` O-01 | Technical Director with PMO | **4 P0 articles before W2; 20 P1 before W4** |
| **O-02** | The `KB-004` / `KB-007` boundary contradicts the Master Index descriptions (§1). The blast-radius rule is proposed here; it needs ratifying and the register descriptions correcting | Programme Content Lead with Technical Director | Before either set is authored — raised as **KB-01** |
| **O-03** | `MD-021` is not populated with the actual serviced model range, so §11 sub-family scoping is provisional. Same dependency as `SP-033` O-02 | MDM with Technical | Before authoring |
| **O-04** | `MD-024` symptom codes are not yet allocated for the display, thermal, feed and print-quality symptoms in §3; the table shows `SYM-` bindings as placeholders where the code does not yet exist. **`KA-02` prohibits minting them here** | Technical analyst (MDM) | **Before article authoring — blocking `TG-02`** |
| **O-05** | Bengali technical terminology for computing repair is not established (`KB-002` O-05); §3 Bengali symptom wording is drafted and needs linguistic sign-off in context (`BN-018`) | Localisation Lead with R12 | W2 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md` — all sections retained in order; additions §11–§13 justified
- [x] Scope boundary against `KB-005`, `KB-006`, `KB-007` stated explicitly, including the register contradiction
- [x] Safety blocks in three-part hazard/consequence/avoidance form (`AU-06c`)
- [x] Symptom index bound to `MD-024`, with unallocated codes flagged rather than minted (`KA-02`)
- [x] Causes ranked with confirming tests (`AU-08`)
- [x] Five-phase diagnostic shape defined and worked through at article depth
- [x] Not-a-fault exit mandated (`TG-04`)
- [x] Verification criteria are numeric or observable (`TG-15`, `AU-12`)
- [x] Resolution coding mapped to `MD-025` `action_class`
- [x] Article inventory enumerated — 42 articles with type, level and priority
- [x] Authoring effort estimated and the resourcing gap stated openly
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-SRM-*`, `BRU-INV-*`, `BRU-WTY-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 42 articles authored — outstanding; this file is the specification, the articles are the deliverable**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] `MD-024` symptom codes allocated — **outstanding; blocks `TG-02`**
- [ ] Named approvers recorded — **pending Technical Director and Quality Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
