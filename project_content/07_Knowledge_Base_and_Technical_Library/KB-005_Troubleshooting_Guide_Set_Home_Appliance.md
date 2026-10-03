---
id: KB-005
title: Troubleshooting Guide Set — Home Appliance
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical Services with Specialist Technicians (R12, refrigerant-certified)
reviewers: [Quality Manager, Technical Director, HSE Lead, Knowledge Manager, Localisation Lead, Warranty Claims Officer]
approver: Technical Director with Quality Manager and HSE Lead
content_class: C
purpose: >
  The governing specification and article inventory for the home-appliance troubleshooting library —
  air conditioning, refrigeration, laundry, cooking, water heating and display appliances. Seasonal
  demand spikes are staffed by newly trained technicians who need reference material rather than
  tribal knowledge, and this is the family where getting it wrong releases refrigerant, floods a
  customer's home, or electrocutes somebody.
traces_to: [M31, M02, M01, M61, M59, M09, P02, P03, MD-021, MD-022, MD-024, MD-025, MD-011, KB-001, KB-002, KB-008, KB-013, SP-033, SP-008, SP-030]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: KB-005_Troubleshooting_Guide_Set_Home_Appliance_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md and M02_Field_Service_and_Dispatch_Management.md — most appliance work is on-site, not bench
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SRM-09 certification required for brand warranty work; BRU-SRM-12 BER evidence; BRU-ESG-04 hazardous items follow their specific handling, storage and transport rules without exception
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M59_Health_Safety_and_Wellbeing.md — safety incident reporting and duty of care for field technicians
    verified: 2026-08-16
    class: P1
  - source: Montreal Protocol HCFC phase-out — Bangladesh HPMP Stage II, implemented with UNDP as lead agency; commitment to reduce HCFC consumption by 67.5% of baseline by 2025; HCFC-22 conversion to R-290 and R-32 in the domestic and commercial air-conditioner manufacturing sector; a large HCFC-22 refrigerant bank remains in installed commercial refrigeration
    verified: 2026-08-16
    class: P1
  - source: Refrigerant flammability classification — R-32 (A2L, mildly flammable) and R-290 propane (A3, higher flammability) require different handling, charge limits and ignition-source control from R-22 (A1, non-flammable)
    verified: 2026-08-16
    class: P2
supersedes: none
review_due: 2027-02-16
---

# KB-005 — Troubleshooting Guide Set: Home Appliance

| Item | Value |
|---|---|
| Article type | **Troubleshooting** (guide-set specification) |
| Device family | `DF-HA` — home appliance |
| Brand / model scope | All serviced `DF-HA` models in `MD-021`; brand-authorised procedures carry a `brand` facet and a certification requirement |
| Skill level required | L1 to L3; **refrigerant work requires a certification held in `MD-011`, not merely a level** |
| Offline pack member | **Yes — and it is the set most read offline**, because appliance work is on-site in customers' homes |
| Review due | 2027-02-16 |

> **Template conformance.** Troubleshooting-type article applied at guide-set level; all
> `TPL_Knowledge_Article.md` sections retained in order and answered for the set. Sections 11–14
> are justified additions, consistent with [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md).

---

## 1. Purpose and Scope

**This is the most physically dangerous guide set in the library.** Every other set risks a
destroyed board or a lost file. This one involves mains electricity in wet environments, gases
under pressure, some of them flammable, working at height on outdoor units, and heavy appliances in
domestic spaces where a customer's family is present.

**In scope:**

| Sub-family | `MD-021` category | Demand pattern | Dominant failure classes | Certification gate |
|---|---|---|---|---|
| Air conditioning — split, window, cassette | `CAT-SPLIT-AC` and siblings | **Sharp pre-monsoon and summer peak** | Refrigerant loss, compressor, PCB, fan motor, drainage, capacitor | **Refrigerant handling** |
| Refrigeration — domestic and small commercial | `CAT-REFRIGERATOR` | Steady, summer-weighted | Refrigerant loss, compressor, thermostat, defrost, door seal, gas leak at joints | **Refrigerant handling** |
| Laundry — washing machine, dryer | `CAT-WASHING-MACHINE` | Steady, monsoon-weighted | Drain, inlet valve, drum bearing, PCB, motor, door lock, imbalance |  |
| Cooking — oven, microwave, hob, rice cooker | `CAT-COOKING` | Steady, festival-weighted | Element, thermostat, magnetron, ignition, timer, door interlock | **Microwave: HV capacitor** |
| Water heating — instant and storage geyser | `CAT-GEYSER` | **Winter-weighted** | Element, thermostat, thermal cut-out, tank corrosion, earthing |  |
| Display appliance — television | `CAT-TV` | Steady | Backlight, panel, power board, main board, T-CON |  |

**Out of scope:**

| Subject | Owned by |
|---|---|
| IT and computing devices, monitors, projectors | [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) — note that **monitors are `DF-IT`, televisions are `DF-HA`**, despite similar internals |
| Mobile and tablet | [`KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md`](KB-006_Troubleshooting_Guide_Set_Mobile_and_Tablet.md) |
| Large commercial and industrial refrigeration, chillers, cold rooms | **Not currently in the serviced range.** Recorded as a scope boundary, not an omission — see `O-06` |
| Manufacturer error-code interpretation | [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) |
| The on-site visit process itself | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) |
| Safety incident response and reporting | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) · `M59` |
| Refrigerant recovery, storage and disposal routes | [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) §5 · `MD-047` · `SP-026` |

---

## 2. Safety

> ⛔ **DANGER — mains electricity in wet environments.** Washing machines, geysers and outdoor AC
> units combine mains voltage with water and with earth paths through a customer's building
> (hazard). Contact causes death (consequence). **Isolate at the consumer unit, not at the
> appliance switch; verify dead with a proving unit; lock or tag the isolation point; confirm the
> appliance earth before re-energising** (avoidance). A geyser with a failed element and a
> compromised earth can energise a customer's plumbing — test earth continuity before touching
> pipework.

> ⛔ **DANGER — microwave high-voltage capacitor.** A microwave HV capacitor stores a lethal charge
> and can remain charged after disconnection (hazard). Contact causes death (consequence).
> **Discharge the capacitor through a resistor and verify with a meter before any work inside the
> cabinet — every time, including on a unit worked on ten minutes earlier** (avoidance).

> ⛔ **DANGER — flammable refrigerants.** Bangladesh's HCFC phase-out is converting the
> air-conditioning stock from R-22 (A1, non-flammable) to **R-32 (A2L, mildly flammable)** and
> **R-290 propane (A3, higher flammability)** (hazard). Brazing, arcing switches, mobile phones and
> cigarettes in a room with a leaked A2L or A3 charge can cause explosion and fatal burns
> (consequence). **Identify the refrigerant from the nameplate before any intervention; never
> assume; use the correct recovery equipment and charge limits for that class; eliminate ignition
> sources; ventilate** (avoidance). See `KB-013` §5.

> ⚠ **WARNING — refrigerant under pressure and frostbite.** Liquid refrigerant contacting skin or
> eyes causes immediate cryogenic burns; a released charge displaces oxygen in an enclosed space
> (hazard). Serious injury or asphyxiation (consequence). **Gloves and eye protection at every
> connection; recover, never vent; work ventilated** (avoidance). Venting is also unlawful under
> the ozone and climate regime the HPMP implements.

> ⚠ **WARNING — working at height and on outdoor units.** Split-AC outdoor units are commonly
> mounted on brackets above ground on building façades (hazard). Falls cause death or serious
> injury (consequence). **No work on an outdoor unit without the fall-protection measures in
> `SP-030`; refuse the job and escalate if the mounting is unsafe** (avoidance). A technician has
> the authority to refuse — this is stated in the article set because a technician alone at a
> customer's home under time pressure needs to have read it before the moment arrives.

> ⚠ **WARNING — stored energy in AC and refrigeration capacitors.** Run and start capacitors retain
> charge after isolation (hazard). Serious injury (consequence). **Discharge and verify before
> handling** (avoidance).

> ⚠ **CAUTION — heavy appliances and manual handling.** Washing machines, refrigerators and
> outdoor units are heavy and awkward (hazard). Crush and back injuries (consequence). **Two-person
> handling above the stated limit; never take the weight on a staircase alone** (avoidance).

> **NOTICE — customer property and water damage.** A disconnected inlet hose or an unsealed drain
> pan can flood a customer's home. Isolate the water supply, place containment, and test before
> leaving.

**`TG-01` applies:** every article in this set repeats the hazard blocks relevant to its own
procedure. **`TG-17` (this set only): no article in this set may be published without HSE approval**
— every sub-family in §1 carries at least one `DANGER` or `WARNING` class hazard, so the
`M61` §9 `BRU-KMS-03` safety gate applies to the whole set rather than article by article.

---

## 3. Symptoms

| Sub-family | Symptom (EN) | Symptom (BN) | `SYM-` binding | First route |
|---|---|---|---|---|
| AC | Not cooling | ঠান্ডা হচ্ছে না | `SYM-00220` | On-site |
| AC | Cooling poorly / takes too long | ঠিকমতো ঠান্ডা হচ্ছে না | `SYM-` cooling-weak | On-site |
| AC | Water dripping indoors | ভিতরে পানি পড়ছে | `SYM-` drainage | On-site L1 |
| AC | Ice on the indoor coil | কয়েলে বরফ জমছে | `SYM-` icing | On-site |
| AC | Outdoor unit not starting | আউটডোর ইউনিট চালু হচ্ছে না | `SYM-` outdoor-fail | On-site |
| AC | Noise or vibration | শব্দ / কাঁপুনি | `SYM-` acoustic | On-site L1 |
| AC | Bad smell from the unit | দুর্গন্ধ আসছে | `SYM-` odour | On-site L1 |
| AC | Error code on the display | ডিসপ্লেতে এরর কোড | `SYM-` coded-fault | **`KB-008`** |
| Refrigerator | Not cooling at all | একদম ঠান্ডা হচ্ছে না | `SYM-00220` | On-site |
| Refrigerator | Freezer works, fridge does not | ফ্রিজার ঠান্ডা, নিচে হচ্ছে না | `SYM-` partial-cool | On-site |
| Refrigerator | Excess frost / ice build-up | অতিরিক্ত বরফ জমছে | `SYM-` defrost | On-site |
| Refrigerator | Water pooling inside or underneath | পানি জমছে | `SYM-` drainage | On-site L1 |
| Refrigerator | Runs continuously / high bill | সবসময় চলে, বিল বেশি | `SYM-` duty-cycle | On-site |
| Washing machine | Not draining | পানি বের হচ্ছে না | `SYM-` drain | On-site L1 |
| Washing machine | Not filling | পানি ঢুকছে না | `SYM-` inlet | On-site L1 |
| Washing machine | Not spinning | ঘুরছে না | `SYM-` drive | On-site |
| Washing machine | Loud noise on spin | স্পিনে বিকট শব্দ | `SYM-` bearing | On-site → bench |
| Washing machine | Leaking water | পানি লিক করছে | `SYM-` leak | On-site — **containment first** |
| Washing machine | Door will not open | দরজা খুলছে না | `SYM-` door-lock | On-site L1 |
| Oven / hob | Not heating | গরম হচ্ছে না | `SYM-` heating | On-site |
| Microwave | Runs but does not heat | চলে কিন্তু গরম করে না | `SYM-` magnetron | **On-site L2 — HV hazard** |
| Microwave | Sparking inside | ভিতরে স্পার্ক করছে | `SYM-` arcing | **Stop use immediately** |
| Geyser | No hot water | গরম পানি আসছে না | `SYM-` heating | On-site |
| Geyser | Tripping the breaker | সার্কিট ব্রেকার ট্রিপ করছে | `SYM-` earth-fault | **On-site L2 — do not reset repeatedly** |
| Geyser | Leaking | পানি লিক করছে | `SYM-` leak | On-site — isolate supply |
| Television | No picture, sound present | ছবি নেই, শব্দ আছে | `SYM-` backlight | On-site → bench |
| Television | No power | চালু হচ্ছে না | `SYM-00101` | Bench |
| Television | Lines or patches on screen | স্ক্রিনে দাগ | `SYM-` panel | Bench — assess BER |

**`TG-02` applies:** every symptom above resolves to at least one article in §11 or is registered
as an orphan in §12.

> **A symptom worth its own note.** *"Tripping the breaker"* on a geyser is not an electrical
> nuisance — it is usually an element that has failed to earth through water. **Repeated resetting
> of the breaker by the customer or the technician is the behaviour that turns a protected fault
> into an electrocution.** Every geyser article opens with that statement.

---

## 4. Likely Causes

| Symptom | # | Likely cause | Frequency | Confirming test |
|---|---:|---|---|---|
| AC not cooling | 1 | **Refrigerant loss through a joint, flare or coil corrosion** | **Highest** | Pressure test; leak detection; **find the leak — never simply top up** |
| | 2 | Dirty filter / condenser coil restricting airflow | High — seasonal | Visual; delta-T across coil |
| | 3 | Compressor not starting — capacitor, contactor, overload | High | Capacitance measurement; start current |
| | 4 | Indoor or outdoor PCB fault | Medium | Sensor and relay checks; error code (`KB-008`) |
| | 5 | Fan motor failure | Medium | Current draw, bearing check |
| | 6 | Undersized unit or building change | Low, but a real answer | Load estimate versus rated capacity |
| AC icing | 1 | Low charge | High | Superheat measurement |
| | 2 | Restricted airflow — filter, blower | High | Airflow measurement |
| | 3 | Sensor fault holding the compressor on | Medium | Sensor resistance vs temperature |
| AC water indoors | 1 | Blocked or mis-sloped drain line | **Highest** | Flush and slope check |
| | 2 | Drain pan crack or displaced insulation | Medium | Visual |
| Fridge not cooling | 1 | Refrigerant loss / capillary blockage | High | Pressure and temperature profile |
| | 2 | Compressor or start relay | High | Start current; relay test |
| | 3 | Defrost system — heater, timer, thermostat | High | Manual defrost recovery test |
| | 4 | Door seal failure causing continuous run and icing | Medium | Paper-pull seal test |
| Washer not draining | 1 | **Blocked pump filter — foreign objects** | **Highest** | Filter inspection |
| | 2 | Drain pump failure | High | Pump current and continuity |
| | 3 | Blocked drain hose or house drain | Medium | Hose flow test |
| | 4 | PCB drive to pump | Low | Voltage at pump terminals |
| Washer noise on spin | 1 | Drum bearing wear | High | Drum play and rotation by hand |
| | 2 | Foreign object between drum and tub | High | Rotate and listen; inspect |
| | 3 | Shock absorber / suspension wear | Medium | Damping test |
| Microwave no heat | 1 | Magnetron failure | High | **HV discharge first**, then output test |
| | 2 | HV diode or capacitor | High | Component test after discharge |
| | 3 | Door interlock switch | Medium | Switch continuity |
| Geyser no hot water | 1 | Element failure | **Highest** | Continuity and resistance |
| | 2 | Thermostat or thermal cut-out tripped | High | Continuity; **find why it tripped** |
| | 3 | Scale build-up reducing transfer | Medium | Tank inspection |
| Geyser tripping breaker | 1 | **Element earth leakage** | **Highest** | Insulation resistance to earth |
| | 2 | Wiring or connector degradation in a wet environment | Medium | Visual + insulation test |
| TV no picture, sound present | 1 | Backlight LED string open | **Highest** | Torch test at an angle |
| | 2 | Power board supplying backlight driver | High | Driver voltage |
| | 3 | T-CON or panel | Medium | Self-test pattern; assess BER |

> **The most consequential rule in this table.** *"Refrigerant loss"* is the top cause of AC and
> refrigerator failure and the top cause of **repeat visits**. `TG-18`: **no article in this set
> may present topping up a charge as a resolution without leak identification.** A recharge without
> a leak repair is a device that fails again inside a season, a warranty exposure, a rework flag
> under `BRU-SRM-06`, and an unlawful emission.

---

## 5. Diagnostic Procedure

The five-phase shape from `KB-004` §5 (`TG-03`) applies unchanged, with one addition specific to
this family.

| Phase | Home-appliance specifics |
|---:|---|
| **0 — Safety and custody** | Electrical isolation and proving · **refrigerant identification from the nameplate** · height and access assessment · water isolation · customer and family present in the space |
| **1 — Reproduce** | Observe the appliance in the customer's actual installation. Half of "not cooling" is a room, a door seal, or a supply voltage problem, not the appliance |
| **2 — Isolate** | Airflow, water path, electrical supply and control signal, in that order — the cheap checks first, because they are also the most frequent causes |
| **3 — Measure** | Pressures, superheat and subcooling, delta-T, current draw, insulation resistance, capacitance |
| **4 — Conclude** | Coded fault, resolution, parts, estimate — **and for any refrigerant fault, the leak location** |
| **5 — Installation review** *(this set only)* | Confirm the installation itself is not the fault: pipe run length, drainage slope, mounting, supply voltage, earthing, ventilation | 

**`TG-19`: phase 5 is mandatory for AC and refrigeration.** A large share of "faulty appliance"
callouts in this market are installation defects. Diagnosing the appliance and ignoring the
installation produces a technically correct repair and a customer who calls again in a week.

### 5.1 Worked diagnostic — split AC not cooling

| Step | Phase | Action | Expected | If not |
|---:|:--:|---|---|---|
| 1 | 0 | Read the nameplate: model, refrigerant type, charge weight | **Refrigerant class identified** — A1, A2L or A3 | **Stop.** Do not open the system. Treat as flammable until proven otherwise (`KB-013` §5) |
| 2 | 0 | Isolate electrically at the consumer unit; prove dead | Dead | Do not proceed |
| 3 | 0 | Assess outdoor unit access and mounting | Safe to work | **Refuse and escalate** (`SP-030`) |
| 4 | 1 | Run the unit; measure supply voltage and room/discharge temperatures | Delta-T across the indoor coil within the model's range | Continue |
| 5 | 2 | Inspect filter and condenser coil | Clean | Clean, re-measure, and **stop here if resolved** — code as `clean` (`TG-16`) |
| 6 | 2 | Check indoor blower and outdoor fan operation | Both run at rated speed | Fan motor or capacitor path |
| 7 | 2 | Check compressor start and run | Starts and holds | Capacitor, contactor, overload, or compressor |
| 8 | 3 | Connect gauges **only with the correct manifold for the refrigerant class**; measure pressures | Within the model's operating envelope | Go to step 9 |
| 9 | 3 | Calculate superheat / subcooling | Within specification | Low charge or restriction indicated |
| 10 | 3 | **Leak-detect: electronic detector, bubble solution, or UV where the manufacturer permits** | Leak located | **Do not recharge.** Escalate; a system that will not hold a charge is not repaired by adding gas (`TG-18`) |
| 11 | 4 | Recover the charge with recovery equipment rated for the class; repair; evacuate; weigh in the nameplate charge | Recorded recovered and charged weights | Recovery equipment unavailable → reschedule, never vent |
| 12 | 5 | Review pipe run, drainage slope, mounting, earthing, ventilation | Compliant | Record as an installation finding and quote separately |
| 13 | 4 | Record `FLT-`, `RES-`, parts, standard time, refrigerant weights | Coded outcome | `FLT-UNK` permitted (`SP-033` `DT-02`) |

> **Step 11 records recovered and charged weights.** That record is the evidence base for
> refrigerant accounting, for the environmental reporting corporate clients ask for, and for
> detecting the technician who is quietly venting instead of recovering. It costs one field on a
> form and it is the only way the behaviour is ever visible.

---

## 6. Repair Procedure

Rules `TG-05`…`TG-14` from `KB-004` §6 apply. This set adds:

| # | Rule |
|---|---|
| **TG-18** | Topping up a refrigerant charge is never presented as a resolution without leak identification |
| **TG-19** | Phase 5 installation review is mandatory for AC and refrigeration articles |
| **TG-20** | **Every refrigerant article states the refrigerant class it applies to and prohibits its application to another class.** R-22, R-32 and R-290 procedures are not interchangeable — charge limits, tools, brazing practice and ignition control all differ |
| **TG-21** | Refrigerant is **recovered, never vented**. Every article says so in its own words, at the step where the temptation arises |
| **TG-22** | Any article involving mains work in a wet environment states the isolation-and-prove sequence explicitly, not by reference |
| **TG-23** | Microwave articles open with the HV discharge step. It is step 1, not a note |
| **TG-24** | Articles state the **two-person handling threshold** for the appliance class |
| **TG-25** | Articles involving a customer's plumbing or electrical installation state where the company's responsibility ends and record the finding rather than remedying it uninstructed |
| **TG-26** | Certification-gated procedures name the `MD-011` certification required; assignment without it is blocked (`BRU-SRM-09`) |

---

## 7. Parts

| Rule | Detail |
|---|---|
| Identification, class, compatibility | As `KB-004` §7 — `MD-022` codes, `part_class`, `compatible_models` |
| Hazard class | `refrigerant` and `chemical` classes carry handling references to `KB-013` §5 |
| Refrigerant as a stocked item | Refrigerant is a **hazardous consumable** with storage, transport and cylinder-custody rules (`BRU-ESG-04`), tracked by weight, not by unit |
| Brand consignment | Brand-supplied warranty parts cannot be consumed on non-warranty jobs (`BRU-WTY-04`) |
| Van stock | This family drives the largest seasonal van-stock swing; see `SP-016` |

**High-movement part families**

| Family | Sub-family | Note |
|---|---|---|
| Run and start capacitors | AC, refrigeration, laundry | Highest-frequency part in the family; **stored energy** |
| Compressors | AC, refrigeration | High value; check warranty before replacing |
| Fan motors — indoor and outdoor | AC | Seasonal |
| PCBs — indoor, outdoor, display | AC, laundry, refrigeration | Model-specific, high SKU count |
| Thermostats, thermistors, sensors | All | Low value, high frequency |
| Drain pumps and filters | Laundry | Highest-frequency laundry part |
| Drum bearings and seals | Laundry | Labour-heavy; assess against BER |
| Inlet valves and hoses | Laundry | **Water-damage risk if wrong** |
| Door locks / interlocks | Laundry, microwave | **Safety component — never bypass** |
| Heating elements | Cooking, geyser, dryer | Earth-leakage failure mode |
| Thermal cut-outs | Geyser, cooking | **Never bypass to prove a fault** |
| Magnetrons, HV diodes, HV capacitors | Microwave | **Lethal stored energy** |
| Backlight strips, power boards, T-CON | Television | Panel replacement usually BER |
| Refrigerant — R-22, R-32, R-290 | AC, refrigeration | **Hazardous; class-specific equipment; recovered, weighed and recorded** |
| Door seals / gaskets | Refrigeration, laundry | Cheap fix for an expensive symptom |

---

## 8. Verification and QC

| Repair class | Test | Pass criterion | Recorded in |
|---|---|---|---|
| AC refrigerant repair | Pressure hold, then run | **Holds vacuum/pressure per the manufacturer's stated hold test**; superheat and subcooling in specification; delta-T across the indoor coil in range after 20 minutes | Repair order + charge weights |
| AC clean / service | Airflow and delta-T | Delta-T restored to range; drain flows freely under test volume | Repair order |
| AC electrical | Run test | Starts on demand, holds 30 minutes, current within nameplate | Repair order |
| Refrigeration | Temperature pull-down | Cabinet reaches set point within the model's stated pull-down time and holds through one cycle | Repair order |
| Laundry drain / pump | Full cycle | **Complete wash cycle with no leak and no error**, drain within stated time | Repair order |
| Laundry bearing | Spin test | Full spin at maximum speed with vibration and noise within tolerance | Repair order |
| Microwave | Water-heat test | Standard water load reaches the expected temperature rise in the stated time; **door interlock and leakage test pass** | Repair order + leakage reading |
| Geyser | Insulation and function | **Insulation resistance to earth above the stated minimum**; earth continuity confirmed; water reaches set temperature; thermal cut-out resets correctly | Repair order + insulation reading |
| Cooking | Function and thermostat | Element reaches temperature; thermostat cycles at set point | Repair order |
| Television | Extended run | 2 hours with no flicker, shutdown or artefact | Repair order |
| **All on-site** | Site made good | No water, no debris, appliance level and secure, customer shown the repair | `DT-007` service report + customer signature |
| **All refrigerant** | **Refrigerant account** | Recovered weight and charged weight recorded; **zero declared venting** | Repair order — feeds environmental reporting |

> **The microwave leakage test is not optional and not a formality.** It is the only check that
> distinguishes a repaired microwave from a radiation hazard placed back in a family kitchen.

---

## 9. Resolution Coding

`MD-025` `action_class` usage follows `KB-004` §9, with these family-specific notes:

| `action_class` | Home-appliance note |
|---|---|
| `clean` | Filter and coil cleaning is the single most frequent AC resolution. **It must carry a fault code**, or the seasonal capacity pattern is invisible to planning |
| `repair` | Includes leak repair. `standard_minutes` for refrigerant work must include recovery and evacuation time — see [`KB-014_Repair_Time_Standards_and_Labour_Norms.md`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) |
| `replace_part` | Compressor and PCB replacements are the high-value cases; check warranty and contract coverage first |
| `configure` | Settings, timers, modes — a real and under-recorded outcome, especially on inverter AC |
| `calibrate` | Sensor and thermostat calibration; requires calibrated instruments (`MD-046`) |
| `no_fault_found` | Frequently an installation or usage issue. **Supervisor countersignature required** (`RES-04`); record the installation finding rather than closing blank |
| `beyond_economic_repair` | Common on drum bearings, compressors on old units, and TV panels. `BRU-SRM-12` evidence and second-technician confirmation required |

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| Refrigerant class cannot be identified | Do not open the system. Supervisor, then brand or manufacturer enquiry | Nameplate photograph |
| A leak cannot be located | Second technician, or workshop for a pressure-decay test | Pressures, detector readings, photographs |
| Recovery equipment for the class is unavailable | Reschedule — **never vent** (`TG-21`) | Job note |
| Outdoor unit mounting or access is unsafe | Refuse and escalate to the branch manager; `SP-030` | Photographs |
| A geyser or appliance has energised customer pipework or casing | **Immediate isolation, customer warned, HSE notified** (`SP-030`), electrician referral | Insulation readings, photographs |
| Microwave leakage exceeds the limit after repair | Do not return the unit. Quality Manager | Leakage reading |
| Certification is not current for brand warranty work | Reassign — blocked (`BRU-SRM-09`, `BRU-HRM-01`) | Certification status |
| Repeat of the same device and fault within 30 days | Rework flag (`BRU-SRM-06`); Quality review | Both jobs |
| A pattern appears across a model | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md); consider a brand query | Occurrence data |
| A brand bulletin or recall may apply | [`KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) | Model, serial range |
| Any injury, near miss, fire, refrigerant release or electrical shock | **HSE immediately** (`SP-030`, `M59`) | Incident record |

---

## 11. Guide Set Inventory *(addition — justified as in `KB-004` §11)*

**48 articles.**

### 11.1 Air conditioning — 14 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 1 | **Refrigerant class identification and the rules that follow from it (A1 / A2L / A3)** | `safety_note` | L1 | **P0** |
| 2 | AC not cooling — the full diagnostic path | `fault_fix` | L1→L2 | P0 |
| 3 | Filter, coil and drain service | `procedure` | L1 | P0 |
| 4 | Leak detection, repair, recovery, evacuation and weighed recharge | `procedure` | L2 + certification | **P0** |
| 5 | Capacitor, contactor and overload diagnosis | `fault_fix` | L1→L2 | P1 |
| 6 | Compressor failure assessment and replacement | `procedure` | L2 | P1 |
| 7 | Indoor and outdoor fan motor replacement | `procedure` | L1→L2 | P1 |
| 8 | Inverter AC PCB and sensor diagnosis | `fault_fix` | L2 | P1 |
| 9 | Icing and airflow faults | `fault_fix` | L1 | P1 |
| 10 | Drainage faults and water ingress indoors | `fault_fix` | L1 | P1 |
| 11 | **Installation review checklist for AC** | `reference_card` | L1 | P1 |
| 12 | AC error-code interpretation *(links `KB-008`)* | `fault_fix` | L1→L2 | P1 |
| 13 | **Working safely on outdoor units at height** | `safety_note` | L1 | **P0** |
| 14 | Seasonal pre-monsoon AC service standard | `procedure` | L1 | P2 |

### 11.2 Refrigeration — 8 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 15 | Refrigerator not cooling — sealed system vs electrical isolation | `fault_fix` | L1→L2 | P0 |
| 16 | Defrost system diagnosis — heater, timer, thermostat, sensor | `fault_fix` | L1→L2 | P1 |
| 17 | Compressor and start-relay diagnosis | `fault_fix` | L2 | P1 |
| 18 | Sealed-system leak repair and recharge by weight | `procedure` | L2 + certification | P1 |
| 19 | Door seal assessment and replacement | `procedure` | L1 | P2 |
| 20 | Drainage and internal water accumulation | `fault_fix` | L1 | P2 |
| 21 | Continuous-run and high-consumption diagnosis | `fault_fix` | L1→L2 | P2 |
| 22 | Refrigerator error-code interpretation *(links `KB-008`)* | `fault_fix` | L1 | P2 |

### 11.3 Laundry — 10 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 23 | Not draining — pump, filter, hose, control | `fault_fix` | L1 | P0 |
| 24 | Not filling — inlet valve, pressure switch, supply | `fault_fix` | L1 | P1 |
| 25 | Not spinning — motor, belt, control, imbalance | `fault_fix` | L1→L2 | P1 |
| 26 | Drum bearing replacement and the BER decision | `procedure` | L2 | P1 |
| 27 | **Leak diagnosis and water-damage containment** | `procedure` | L1 | **P0** |
| 28 | Door lock and interlock faults — **never bypass** | `fault_fix` | L1 | P1 |
| 29 | Laundry PCB and sensor diagnosis | `fault_fix` | L2 | P2 |
| 30 | Excessive vibration — suspension, shock absorbers, levelling | `fault_fix` | L1 | P2 |
| 31 | Dryer heating and airflow faults | `fault_fix` | L1→L2 | P2 |
| 32 | Laundry error-code interpretation *(links `KB-008`)* | `fault_fix` | L1 | P1 |

### 11.4 Cooking and microwave — 7 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 33 | **Microwave HV discharge — the mandatory first step** | `safety_note` | L2 | **P0** |
| 34 | Microwave runs but does not heat — magnetron, diode, capacitor | `fault_fix` | L2 | P1 |
| 35 | **Microwave door interlock and radiation leakage test** | `procedure` | L2 | **P0** |
| 36 | Microwave arcing — waveguide cover, cavity, foreign object | `fault_fix` | L1→L2 | P1 |
| 37 | Oven and hob element and thermostat diagnosis | `fault_fix` | L1→L2 | P2 |
| 38 | Gas hob ignition and flame-failure device faults | `fault_fix` | L2 | P2 |
| 39 | Small cooking appliance diagnosis and the BER threshold | `fault_fix` | L1 | P3 |

### 11.5 Water heating — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 40 | **Geyser tripping the breaker — earth leakage and why it must never be repeatedly reset** | `safety_note` | L1 | **P0** |
| 41 | Element and thermostat diagnosis and replacement | `procedure` | L1→L2 | P1 |
| 42 | Thermal cut-out — why it tripped, and never bypassing it | `fault_fix` | L2 | P1 |
| 43 | Tank corrosion, scale and leak assessment | `procedure` | L1 | P2 |
| 44 | Instant water heater faults | `fault_fix` | L1→L2 | P2 |

### 11.6 Television — 4 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 45 | No picture with sound — backlight and driver isolation | `fault_fix` | L2 | P1 |
| 46 | **Power board service and stored-energy safety** | `procedure` | L2 | P1 |
| 47 | Backlight LED strip replacement | `procedure` | L2 | P2 |
| 48 | Panel defect assessment and the BER decision | `procedure` | L1 | P2 |

**Set totals:** 48 articles · 9 at P0 · 20 at P1 · 17 at P2 · 2 at P3 ·
**all 48 require HSE approval under `TG-17`** · 8 are certification-gated for refrigerant work.

---

## 12. Authoring Plan, Coverage and Orphans

| Item | Position |
|---|---|
| Articles required | **48** |
| Articles written | **0** |
| Authoring effort, estimated | 48 × 5–12 hours of refrigerant-certified R12 time = **240–575 specialist hours**, plus HSE review on every article and translation |
| Sequencing | 9 P0 before W2 · 20 P1 before W4 · remainder before the following pre-monsoon season |
| **Seasonal constraint** | AC and refrigeration articles must be published **before** the pre-monsoon peak, not during it. Publishing in June is publishing after the demand that needed them |
| Bengali | All 48 bilingual; **all safety blocks human-translated and HSE re-approved** (`AU-06f`) |
| Certification dependency | 8 articles cannot be authored without a refrigerant-certified R12 author and cannot be *acted on* without `MD-011` certification |

> **`M61` §14 and the seasonal argument.** Demand in this family is not flat, and neither is
> competence: `M61` records that seasonal spikes are staffed by newly trained technicians. The
> value of an article in this set is concentrated in the weeks when the least experienced people
> are doing the most work. An authoring plan that treats all 48 as equally urgent misses that.

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | §5 refrigerant data underpinning every safety block here |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | Appliance error codes |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) | `TG-01`…`TG-16` shared rules and the five-phase shape |
| [`KB-014_Repair_Time_Standards_and_Labour_Norms.md`](KB-014_Repair_Time_Standards_and_Labour_Norms.md) | Standard times, including recovery and evacuation |
| [`KB-016_Technician_Field_Reference_Card_Set.md`](KB-016_Technician_Field_Reference_Card_Set.md) | Which articles become offline cards — this family dominates the card set |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-008_SOP_On_Site_Field_Service_Visit.md) | The visit process these guides run inside |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) | Every safety escalation route |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md) | Refrigerant and appliance disposal routes |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-011_Certification_and_Brand_Authorisation_Register.md) | Refrigerant and brand certifications gating §11 |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) | Hazard classes and approved disposal partners |
| `TR-009` Course Pack — Field Technician | Trains this set; the seasonal intake is trained on it |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M31`, `M02`, `M59` module specifications | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-06`, `-09`, `-12`; `BRU-ESG-04`; `BRU-WTY-04`; `BRU-HRM-01` | 2026-08-16 | 2027-02-16 |
| `M61` §9 `BRU-KMS-03` safety approval gate | 2026-08-16 | 2027-02-16 |
| Bangladesh HCFC Phase-out Management Plan Stage II — UNDP lead implementing agency; 67.5% reduction against baseline committed by 2025; HCFC-22 conversion to R-290 and R-32 in domestic and commercial AC manufacturing; substantial HCFC-22 bank remains in installed commercial refrigeration | 2026-08-16 | **2027-02-16 — statutory currency check required** |
| Refrigerant flammability classes — R-22 (A1), R-32 (A2L), R-290 (A3) | 2026-08-16 | 2027-08-16 |
| `MD-021`, `MD-022`, `MD-025`, `MD-011`, `MD-047` | 2026-08-16 | 2027-02-16 |

> **Statutory caution (`CG-012`, `CG-013`).** The refrigerant regime is a live regulatory area
> implemented through the Department of Environment and the HPMP. **The technician-certification
> and cylinder-handling requirements applicable to a service business in Bangladesh have not been
> confirmed by a named authority for this programme** — see `O-02`. Nothing in this file should be
> read as establishing that the company's current practice is compliant.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The 48 articles are unwritten; 240–575 refrigerant-certified specialist hours are unallocated.** Seasonally constrained — AC content is worth far less published after the peak | Technical Director with PMO | **9 P0 before W2; AC set before the pre-monsoon peak** |
| **O-02** | **The statutory position on refrigerant handling, technician certification and cylinder custody in Bangladesh is not confirmed by a named authority.** `MD-011` assumes a certification exists to register. This is a `CG-013` legal-escalation trigger | HSE Lead with Legal Counsel and Technical Director | **W2 — before refrigerant articles are published** |
| **O-03** | `MD-024` symptom codes are unallocated for most §3 entries; bindings are shown as placeholders and **may not be minted here** (`KA-02`) | Technical analyst (MDM) | Before authoring |
| **O-04** | The microwave radiation-leakage limit and the test instrument are not specified. §8 requires the test; the acceptance figure must come from a named standard, not from this file | HSE Lead with Technical Director | Before article 35 |
| **O-05** | Refrigerant is not yet modelled as a weight-tracked hazardous consumable in `MD-022`/`M15`. §7 assumes it is | Inventory Manager with MDM | W3 |
| **O-06** | Large commercial refrigeration, chillers and cold rooms are declared out of scope in §1. If `P04` corporate contracts include them, the scope statement is wrong and a further set is needed | Technical Director with Account Management | W4 |
| **O-07** | Bengali technical terminology for refrigeration and electrical safety is not established (`KB-002` O-05). Safety wording in a second language is not a translation task; it is a safety task | Localisation Lead with HSE Lead | **W2 — blocks Bengali safety articles** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] Scope boundary stated, including the monitor-vs-television family split
- [x] Safety blocks in three-part form, covering electrical, refrigerant, HV, height and handling hazards
- [x] Flammable-refrigerant transition treated as a live hazard with a sourced basis, not a footnote
- [x] `TG-18` prohibits recharge without leak identification
- [x] `TG-21` requires recovery, never venting, with a weight record that makes the behaviour visible
- [x] Installation review made a mandatory diagnostic phase for AC and refrigeration (`TG-19`)
- [x] Verification criteria numeric or observable, including insulation resistance and microwave leakage
- [x] Article inventory enumerated — 48 articles with type, level, priority and certification gating
- [x] Seasonal authoring constraint stated
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-SRM-*`, `BRU-ESG-*`, `BRU-WTY-*`, `BRU-HRM-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 48 articles authored — outstanding**
- [ ] **`O-02` refrigerant statutory position confirmed — outstanding; blocks publication of refrigerant articles**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] HSE approval recorded for the set under `TG-17` — **pending**
- [ ] Named approvers recorded — **pending Technical Director, Quality Manager and HSE Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
