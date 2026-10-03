---
id: KB-013
title: ESD, Chemical and Battery Safety Data
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: HSE
author: HSE Lead with Technical Services and Sustainability
reviewers: [Quality Manager, Technical Director, Legal Counsel, Facilities Manager, Logistics Manager, Knowledge Manager, Localisation Lead]
approver: HSE Lead with Quality Manager and Legal Counsel
content_class: A
purpose: >
  The single authoritative hazard-data source for electrostatic discharge control, lithium and
  stationary battery handling, refrigerant handling, and workshop chemicals across 51+ sites. Every
  safety block in every knowledge article cites this file rather than restating hazard data, so
  that a change to a hazard control propagates from one place instead of being chased through two
  hundred articles. Lithium and refrigerant handling carry statutory duties and genuine physical
  risk; getting them wrong injures people and breaches law.
traces_to: [M59, M18, M61, M45, M31, M02, P02, P09, P11, MD-022, MD-046, MD-047, KB-001, KB-002, KB-004, KB-005, KB-006, KB-007, KB-009, KB-012, KB-016, SP-030, SP-026, SP-009, SP-016]
priority: P1
wave: W5
bilingual: yes
bn_counterpart: KB-013_ESD_Chemical_and_Battery_Safety_Data_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/H_People_and_Workforce/M59_Health_Safety_and_Wellbeing.md — duty of care, hazard reporting, incident investigation and corrective action
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-ESG-04 — hazardous items follow their specific handling, storage and transport rules without exception; BRU-ESG-01/02/03 wipe or destruction record, certified partner, retrievable disposal certificate
    verified: 2026-08-16
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md — hazard_class enum none / lithium / refrigerant / chemical / sharp / esd_sensitive drives handling and transport
    verified: 2026-08-16
    class: P1
  - source: IEC 61340-5-1 and ANSI/ESD S20.20 — technically equivalent standards giving administrative and technical requirements for establishing, implementing and maintaining an ESD control programme, including grounding, protective equipment and controlled environments; facility certification programmes assess against them
    verified: 2026-08-16
    class: P2
  - source: UN Manual of Tests and Criteria section 38.3 — lithium cells and batteries offered for transport must have passed the design tests; damaged, defective or recalled lithium batteries have greater potential to short circuit, release heat and enter thermal runaway, and are forbidden for transport by air
    verified: 2026-08-16
    class: P1
  - source: Montreal Protocol HCFC phase-out — Bangladesh HPMP Stage II with UNDP as lead implementing agency; commitment to reduce HCFC consumption by 67.5% of baseline by 2025; HCFC-22 conversion to R-290 and R-32 in domestic and commercial air-conditioner manufacturing; substantial HCFC-22 bank remains in installed commercial refrigeration
    verified: 2026-08-16
    class: P1
  - source: Hazardous Waste (E-waste) Management Rules 2021 (Bangladesh), made under the Bangladesh Environment Conservation Act 1995 and effective from 10 June 2021 — registration of manufacturers, importers, recyclers and sellers with the Department of Environment, waste management plans, phased collection targets rising from 10% in the first year to 50% in the fifth year and thereafter, restriction of ten hazardous substances aligned to the EU RoHS list, and penalties up to two years imprisonment or BDT 200,000 for a first offence with higher penalties for repeat offences
    verified: 2026-08-16
    class: P1
    note: Applicability of the producer obligations to a service and repair business, as distinct from a manufacturer or importer, must be confirmed by Legal Counsel — see Open Item O-02
supersedes: none
review_due: 2027-02-16
---

# KB-013 — ESD, Chemical and Battery Safety Data

| Item | Value |
|---|---|
| Article type | **Reference** (`safety_note` article class) |
| Device family | All |
| Brand / model scope | Not device-scoped — **hazard-scoped**, bound to `MD-022` `hazard_class` |
| Skill level required | **L1 — every technician, every branch, no exceptions** |
| Offline pack member | **Yes — mandatory and non-removable.** A safety data source that requires connectivity has failed |
| Review due | 2027-02-16 · **6-month cycle** for `safety_note` content (`KB-001` §4.2) |

> **Template conformance — the one deliberate adaptation in this category.**
> `TPL_Knowledge_Article.md` places Symptoms, Likely Causes and Diagnostic Procedure at §3–§5.
> This file places its four **hazard-data sections** there instead, because twelve other files in
> Category 07 cite it by section number — `KB-013 §3` for ESD, `§4` for battery, `§5` for
> refrigerant, `§6` for chemicals. Renumbering to satisfy the template would break thirteen inbound
> references in a safety document. **No template section is removed**; Symptoms, Likely Causes,
> Diagnostic Procedure, Repair Procedure, Parts, Verification and QC, Resolution Coding and
> Escalation all appear, at §7–§13, in template order.
> The underlying defect is that `TPL_Knowledge_Article.md` has no hazard-data variant and
> `CG-009` §3 allocates template 7 to all thirteen non-governance `KB` files regardless of shape.
> Raised as audit finding **KB-05** rather than resolved unilaterally (`CM-R1`).

---

## 1. Purpose and Scope

**This file exists so that hazard data is written once.**

`KB-002` `AU-06e` requires every article with a `hazard_class` other than `none` to carry a safety
block *and a link to this file*. That is a deliberate division of labour:

| Layer | Holds | Changes when |
|---|---|---|
| The article's safety block | The hazard **as it arises in that procedure** — three-part hazard, consequence, avoidance | The procedure changes |
| **This file** | The hazard **data** — why it is dangerous, the numbers, the statutory position, the storage and transport rules, the incident response | The science, the law or the equipment changes |

Without the split, a change to lithium storage practice would require editing every battery-touching
article in the library, and the ones that were missed would be the ones a technician happened to
open. With it, the data changes here and every article inherits it.

**Consequence of absence (`CP-03`).** No single source for hazard data means each author writes
their own from memory; safety guidance diverges between articles; the statutory position is stated
differently in different places; and there is nothing for HSE to approve, review or update as
regulation moves.

**In scope:** ESD control (§3), lithium and stationary batteries (§4), refrigerants (§5), workshop
chemicals (§6); the storage, transport, disposal and incident-response rules for each; the
statutory anchors; and the PPE and facility requirements that follow.

**Out of scope:**

| Subject | Owned by |
|---|---|
| Incident reporting, investigation and corrective action **process** | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-030_SOP_Health_Safety_and_Incident_Reporting.md) · `M59` |
| E-waste collection, segregation and partner transfer **process** | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md) · `M18` |
| Material categories, hazard classes and approved disposal partners | [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) |
| Instrument operation | [`KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md) |
| Part-level hazard classification | [`../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md`](../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-022_Spare_Part_Catalogue_and_Compatibility_Matrix.md) `hazard_class` |
| Reverse-logistics routing and packaging **operations** | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-009_SOP_Pick_and_Drop_and_Reverse_Logistics.md) |
| Employee safety training delivery | `TR-009` · `M22` |

---

## 2. Safety — the rules that govern this file itself

> ⛔ **DANGER — this file is not a substitute for the manufacturer's safety data sheet.** Where a
> chemical, refrigerant or battery has an SDS, **the SDS governs** (hazard: relying on a summary).
> A summary that disagrees with an SDS is wrong (consequence). **§6.4 requires the SDS to be held,
> accessible and current for every chemical on site** (avoidance).

> ⚠ **WARNING — a hazard control that is not verified is not a control.** An untested wrist strap,
> an unweighed recovery cylinder, an SDS nobody can find, a battery container in a store room
> nobody can reach — each provides the appearance of control and none of the substance.

| # | Governing rule | Class |
|---|---|:--:|
| **SD-01** | Every article with `hazard_class` ≠ `none` links to the relevant section of this file (`AU-06e`, `KA-07`) | **H** |
| **SD-02** | Hazard data is stated **here only**; articles state the hazard *in their procedure*, not the underlying data | **H** |
| **SD-03** | Where a manufacturer SDS exists, it governs over this file | **H** |
| **SD-04** | Every section names its statutory or standards anchor and the date it was verified (`CG-012`) | **H** |
| **SD-05** | This file requires HSE Lead, Quality Manager **and Legal Counsel** approval — content class A (`CG-007`, `CG-013`) | **H** |
| **SD-06** | Bengali is human-translated in context and **re-approved by HSE after translation**; machine translation is prohibited (`AU-06f`, `CG-010`) | **H** |
| **SD-07** | This file is non-removable from the `P02` offline pack; pack-size pressure never displaces it (`KB-016`) | **H** |
| **SD-08** | Any change to a hazard control is distributed as an S1 or S2 notice, not left to the next sync (`KB-010` §6.2 severity model applied internally) | **C** |
| **SD-09** | A control that cannot be verified is not claimed as a control | **H** |
| **SD-10** | Review is **6-monthly**, and out-of-cycle on any regulatory change, incident or equipment change | **C** |

---

## 3. ESD Control Data

**Statutory / standards anchor:** IEC 61340-5-1 and ANSI/ESD S20.20 — technically equivalent
standards setting the administrative and technical requirements of an ESD control programme.
Verified 2026-08-16.

### 3.1 Why it matters here specifically

ESD is the hazard technicians most often disregard because **its harm is invisible and delayed**.
A discharge well below the human perception threshold can damage a semiconductor junction without
causing immediate failure. The device passes verification, returns to the customer, and fails weeks
later — where it appears in our data as **rework**, attributed to the repair rather than to the
handling.

| Damage type | Symptom | Cost to 1000FiX |
|---|---|---|
| **Catastrophic** | Immediate failure at the bench | A part, and bench time |
| **Latent** | Degraded junction, fails later | **A rework flag (`BRU-SRM-06`), a second customer visit, a warranty claim, and a reputation** |

Latent damage is why ESD control is a *programme* rather than a wrist strap.

### 3.2 The controlled environment — EPA requirements

An ESD Protected Area is a defined workspace in which all conductive and dissipative items,
including people, are bonded to a common ground reference.

| Element | Requirement | Verification |
|---|---|---|
| **Common ground point** | All ESD elements bonded to one ground reference; no floating elements | Continuity check at commissioning and after any bench change |
| **Work surface** | Dissipative mat, grounded through the specified resistor path | Mat tested at defined interval |
| **Personnel grounding** | Wrist strap with cord, worn skin-contact, tested **at shift start**; heel straps and dissipative flooring where mobility is required | **Strap tester at every station** — `SD-09` |
| **Boundary marking** | The EPA is physically demarcated so that people know when they are inside it | Visual |
| **Handling** | ESD-sensitive items in shielding bags outside the EPA; opened only inside it | Observation |
| **Prohibited inside the EPA** | Common plastics, polystyrene, adhesive tape rolls, personal items generating charge, ungrounded tools | Housekeeping check |
| **Humidity** | Low relative humidity increases charge generation; controls are specified for the site's actual conditions, not assumed | Environmental monitoring where available |
| **Tools** | Soldering irons and rework stations with grounded tips; dissipative handles | `KB-012` |
| **Training** | Every person entering the EPA understands the controls | `M22`, `TR-009` |

> **The Bangladeshi climate cuts both ways.** High ambient humidity for much of the year reduces
> charge generation, which is genuinely protective. **Air-conditioned workshops and the dry
> winter months remove that protection** — and those are precisely the conditions in the newest,
> best-equipped benches doing the most board-level work. The control set must not be relaxed on
> the assumption that "it is humid here".

### 3.3 The shift check — `SD-11`

| Step | Check | Fail action |
|---:|---|---|
| 1 | Wrist strap and cord tested with the station tester | **Replace before work.** A failed strap is not adjusted, it is replaced |
| 2 | Mat ground path continuous | Station out of service |
| 3 | Bench free of prohibited materials | Clear before starting |
| 4 | Shielding bags available and undamaged | Restock |
| 5 | Ionisers, where fitted, powered and within service interval | Report |

**Recorded on the branch shift checklist under `SP-032`.** A check that is performed and not
recorded cannot be evidenced at an ISO or brand audit.

### 3.4 Which parts are ESD-sensitive

Bound to `MD-022` `hazard_class: esd_sensitive`. In practice: all bare boards, all board-level
components, memory, storage, display driver assemblies, camera modules, and any assembly with an
exposed connector to a board.

---

## 4. Lithium and Battery Safety Data

**Statutory / standards anchor:** UN Manual of Tests and Criteria section 38.3 for cells and
batteries offered for transport; the established position that damaged, defective or recalled
lithium batteries carry materially greater potential to short circuit, release heat and enter
thermal runaway, and are **forbidden for transport by air**. Verified 2026-08-16.

### 4.1 The hazard

Thermal runaway is a self-sustaining exothermic reaction. Once initiated it cannot be extinguished
by removing the ignition source, because the cell supplies its own oxidiser. It produces intense
heat, flame, and toxic and flammable gases.

| Initiator | Where it happens in our work |
|---|---|
| **Mechanical damage — puncture, crush, bend** | Pouch-cell removal with a metal tool (`KB-006` `TG-28`); a device dropped in transit |
| **Internal short from manufacturing or age** | A swollen cell presenting for service |
| **External short** | Terminals contacting metal in a parts bin, a van, or a shipping carton |
| **Overcharge / charging a damaged cell** | "Testing" a swollen battery to confirm the fault |
| **Thermal — external heat** | Hot-air work over the cell area; a device left in a vehicle |
| **Water ingress reacting with cell chemistry** | Liquid-damaged devices |

### 4.2 Handling rules — `SD-12`

| # | Rule |
|---|---|
| 1 | **A swollen, punctured, deformed, leaking or heat-damaged cell is a live hazard, not a fault to be diagnosed.** Isolate it first, investigate never |
| 2 | **Never re-charge a damaged cell.** Not to test it, not to discharge it, not "just to check" |
| 3 | **Never re-fit a damaged cell**, even temporarily, even to demonstrate a fault to a customer |
| 4 | Remove cells using the manufacturer's stated method — adhesive-release tabs, isopropyl alcohol, or controlled heat. **Metal prying against a cell is prohibited** |
| 5 | Discharge below approximately 30% state of charge before removal where practicable and safe |
| 6 | Never apply hot air over the cell area; shield the cell during adjacent rework |
| 7 | Terminals are taped or capped before a cell is placed in any container |
| 8 | **The steel battery isolation container is within arm's reach of every bench doing battery work.** Not in a store room |
| 9 | Never place a battery — damaged or sound — in general waste or general recycling |
| 10 | A device with a suspect cell is not left charging unattended, overnight, or in a vehicle |

### 4.3 Storage

| Requirement | Detail |
|---|---|
| **Sound stock cells** | Stored at partial state of charge per the manufacturer's guidance, cool, dry, terminals protected, away from combustibles |
| **Damaged / defective / recalled cells** | **Segregated immediately** in a non-combustible, electrically non-conductive, absorbent-lined container with a lid; quantity limits per container; located away from occupied areas and escape routes |
| Segregation | Damaged cells are never stored with sound stock |
| Quantity | Site limits set by HSE with Facilities; **not yet established — see `O-04`** |
| Fire provision | Appropriate extinguishing media and a means of isolating a container that begins to vent; the workshop fire plan accounts for battery storage |
| Records | Every isolated cell recorded — device, date, technician, container, disposal route |

### 4.4 Transport — the constraint that reaches logistics

| Movement | Position |
|---|---|
| **Damaged, defective or recalled cells by air** | **Forbidden.** This is not a company policy, it is the transport regime |
| Damaged cells by road, inter-branch | Permitted with the packaging, segregation and quantity controls in §4.3, declared, and with the receiving site's agreement. **The packaging standard is not yet specified — `O-03`** |
| Sound cells as stock | Per the applicable transport provisions for the cell type and quantity |
| Devices containing installed cells | Ordinary handling; damaged devices with damaged cells follow the damaged-cell rule |
| Customer-carried | A customer bringing a swollen-battery device to a branch is not turned away — they are met at the counter, the device is isolated, and the reason is explained |

**This constrains `SP-009` reverse logistics directly.** A pick-and-drop network that moves devices
between branches must know which consignments contain damaged cells and route them accordingly.

### 4.5 Stationary and lead-acid batteries — UPS

| Hazard | Control |
|---|---|
| **Very high short-circuit current at low impedance** — arc flash | Insulated tools, no jewellery or watches, eye protection, one hand where practicable, string links removed before work |
| Sulphuric acid electrolyte | Eye and skin protection; eyewash provision; spill absorbent |
| Hydrogen evolution during charging | Ventilation; no ignition sources at the battery |
| Weight | Two-person handling above the stated limit; correct lifting aids |
| Stored energy present with mains isolated | **A UPS presents live output with the mains off** (`KB-007` §2) |
| Disposal | Regulated waste stream; `MD-047` route; certificate required (`BRU-ESG-03`) |

### 4.6 Incident response — thermal event

| Step | Action |
|---:|---|
| 1 | **Raise the alarm and evacuate the immediate area.** Do not attempt to move a venting cell |
| 2 | Do not inhale the vapour — it is toxic as well as flammable |
| 3 | Isolate power to the bench if it can be done without approach |
| 4 | Use the extinguishing media specified in the site fire plan; **large volumes of water are the recognised approach for cooling adjacent cells**, but the site's own plan and the fire service govern |
| 5 | Do not return to the area — cells can re-ignite after apparent extinction |
| 6 | Ventilate before re-entry, on the fire service's or HSE's direction |
| 7 | **Report as a safety incident** (`SP-030`, `M59`), with photographs and the device and cell identity |
| 8 | Quarantine any cells from the same batch or source pending investigation |
| 9 | If a supplied part was involved, escalate to Procurement and to `KB-009` / `KB-010` |

---

## 5. Refrigerant Safety Data

**Statutory / policy anchor:** the Montreal Protocol HCFC phase-out as implemented in Bangladesh
through the HCFC Phase-out Management Plan Stage II, with UNDP as lead implementing agency; the
Government's commitment to reduce HCFC consumption by 67.5% of baseline by 2025; conversion of
HCFC-22 to R-290 and R-32 in domestic and commercial air-conditioner manufacturing; and the
substantial HCFC-22 bank that remains in installed commercial refrigeration. Verified 2026-08-16.

### 5.1 Why this changed, and why it matters now

For most of the working lives of the company's senior technicians, "refrigerant" meant R-22 — an
A1 refrigerant: non-flammable. **The installed base is converting to R-32 (A2L, mildly flammable)
and R-290 propane (A3, higher flammability), while the R-22 bank persists.** A technician's habits,
tools and instincts were formed on a refrigerant class that is being replaced underneath them.

| Class | Flammability | Practical consequence |
|---|---|---|
| **A1** (e.g. R-22) | Non-flammable | Brazing and arcing tolerated in the historic practice |
| **A2L** (e.g. R-32) | **Mildly flammable** | Ignition sources controlled; charge limits by room volume; class-rated tools |
| **A3** (e.g. R-290 propane) | **Higher flammability** | Strict ignition control; smaller charge limits; dedicated equipment |

**`SD-13`: identify the refrigerant from the nameplate before any intervention. Never assume from
the model, the age, or what was in it last time.** A converted or retrofitted system does not
announce itself.

### 5.2 Hazards

| Hazard | Consequence | Control |
|---|---|---|
| **Ignition of a flammable charge** | Explosion, fatal burns | No brazing, smoking, arcing switches, mobile phones or other ignition sources in a space with a leaked A2L/A3 charge; ventilate; class-rated equipment |
| **Cryogenic burn** | Immediate tissue damage from liquid contact | Gloves and eye protection at **every** connection |
| **Asphyxiation** | Refrigerant is heavier than air and displaces oxygen in enclosed and low spaces | Ventilate; never work alone in a confined space; be aware of basements, ducts and pits |
| **Pressure** | Injury from a released connection or an over-pressurised cylinder | Correct manifold for the class; never overfill a recovery cylinder; observe cylinder fill limits |
| **Decomposition products** | Refrigerant contacting a flame or hot surface produces toxic products | Never leak-test with a flame |
| **Environmental release** | Ozone and climate harm; unlawful | **Recover, never vent** — `SD-14` |

### 5.3 Handling rules — `SD-14`

| # | Rule |
|---|---|
| 1 | **Recover. Never vent.** Recovery equipment rated for the refrigerant class, and recovered weight recorded |
| 2 | Identify the class from the nameplate before connecting anything (`SD-13`) |
| 3 | Equipment is class-specific — manifold, hoses, recovery machine, vacuum pump, scale. **Cross-use is prohibited** |
| 4 | Charge by **weight**, to the nameplate charge, not by pressure or by feel |
| 5 | **Never top up without locating the leak** (`KB-005` `TG-18`) |
| 6 | Cylinders: secured upright, valve caps fitted, stored out of direct sun, not above their fill limit, segregated by refrigerant, never in an occupied or below-ground space |
| 7 | Recovery cylinders are labelled with their contents and never mixed |
| 8 | Refrigerant is tracked **by weight** as a hazardous consumable, with recovered and charged quantities recorded per job |
| 9 | Certification required for refrigerant work is held in `MD-011` and checked before assignment (`BRU-SRM-09`) |
| 10 | Work in ventilated space; where ventilation is inadequate, the job is rescheduled, not attempted |

### 5.4 Incident response — release

| Step | Action |
|---:|---|
| 1 | Evacuate and ventilate; keep people out of low-lying and enclosed spaces |
| 2 | **Eliminate ignition sources** — for A2L and A3 this is the priority action |
| 3 | Do not attempt to stop a large release; isolate at a safe point if it can be done safely |
| 4 | Cryogenic contact: flush with tepid water, do not rub, seek medical attention |
| 5 | Suspected inhalation exposure: fresh air, medical attention |
| 6 | Report as a safety incident (`SP-030`) **and record the released quantity** — it is an environmental as well as a safety event |
| 7 | Investigate the cause; a release is almost always a procedure or equipment failure |

---

## 6. Chemical Safety Data

**Anchor:** the manufacturer's safety data sheet for each substance, which governs (`SD-03`);
GHS-aligned classification and labelling as the reference framework. Verified 2026-08-16.

### 6.1 Substances in normal workshop use

| Substance class | Typical use | Principal hazards |
|---|---|---|
| **Isopropyl alcohol (IPA)** | Board cleaning, adhesive release | Highly flammable; vapour; eye and skin irritation |
| **Flux — rosin and no-clean** | Soldering and rework | Respiratory sensitisation from fume; skin irritation |
| **Solder — including leaded** | Soldering | **Lead exposure by ingestion and fume**; hand-to-mouth is the dominant route |
| **Solvent cleaners, contact cleaner** | Contact and assembly cleaning | Flammable; vapour; some are harmful to the nervous system |
| **Ultrasonic cleaning solutions** | Liquid-damage board recovery | Alkaline or solvent-based; skin and eye damage |
| **Thermal paste and adhesives** | Reassembly | Irritant; some cyanoacrylates bond skin instantly |
| **Compressed air / duster** | Cleaning | Pressure injury; some propellants are flammable; **never used on skin or into the body** |
| **Battery electrolyte** | Leaked cells | Corrosive; §4 applies |
| **Refrigerant oils** | Refrigeration work | Irritant; hygroscopic; §5 applies |
| **Cleaning chemicals — facility** | Housekeeping | Per their own SDS; some produce toxic gas if mixed |

### 6.2 Handling rules — `SD-15`

| # | Rule |
|---|---|
| 1 | **The SDS governs** (`SD-03`). This list is an index, not a substitute |
| 2 | Fume extraction at every soldering and rework position, in use, and serviced |
| 3 | **No eating, drinking or smoking at the bench** — the principal lead-exposure route is hand-to-mouth |
| 4 | Hand washing before eating and at the end of every shift, whether or not hands look dirty |
| 5 | Flammables in the minimum working quantity at the bench; bulk in the designated flammables store, away from ignition sources and hot tools |
| 6 | **Never mix cleaning chemicals**; some combinations produce toxic gas |
| 7 | Decanted containers are labelled with contents and hazard — an unlabelled bottle of clear liquid is an incident waiting for a new starter |
| 8 | PPE per the SDS: eye protection, gloves of the correct material, respiratory protection where specified |
| 9 | Spill kit appropriate to the substances held, accessible, and stocked |
| 10 | Waste chemicals and contaminated absorbents go to the regulated waste stream (`MD-047`), never to general waste or to drain |

### 6.3 Facility requirements

| Requirement | Detail |
|---|---|
| Ventilation | General ventilation plus local extraction at rework positions |
| Flammables storage | Designated, ventilated, away from ignition sources and escape routes |
| Eyewash and first aid | Accessible from every bench; **stocked and in date** (`SD-09`) |
| Fire provision | Media appropriate to the substances and to §4 battery storage |
| Spill containment | Kit sized to the largest single container held |
| Segregation | Incompatible substances stored apart |
| **SDS accessibility** | Current SDS for every substance on site, **accessible to the technician at the point of use — including offline** |

### 6.4 The SDS obligation — `SD-16`

| Rule | Detail |
|---|---|
| Held | An SDS is held for every chemical on every site |
| Current | Reviewed when a supplier or formulation changes |
| **Accessible** | Reachable by the person using the substance, at the time they are using it. A binder in a manager's office fails this test |
| Offline | The SDS set for a branch's substances is part of the offline pack (`KB-016`) |
| Bilingual | **Where the SDS is English-only, a Bengali hazard summary is produced and HSE-approved.** A safety data sheet the reader cannot read is not a control (`SD-09`) |
| Training | Substance-specific briefing before first use (`M22`) |

---

## 7. Symptoms *(template section — the observable signs of a hazard-control failure)*

| Observation | Hazard section | Indicates |
|---|:--:|---|
| Rework clustering on board-level repairs from one bench | §3 | ESD control failing — latent damage |
| Wrist straps worn loose, or cords taped | §3 | Control defeated; strap testing not happening |
| A swollen battery on a bench rather than in the container | §4 | Isolation rule not reaching the bench |
| Batteries in a general waste bin | §4 | Disposal route unknown or inaccessible |
| Refrigerant topped up without a leak found | §5 | `TG-18` breached; venting likely |
| Recovered weights not recorded | §5 | **Venting is invisible without the record** |
| Unlabelled bottles at a bench | §6 | Decanting rule not followed |
| Food or drink at a rework bench | §6 | Lead-exposure control failing |
| An SDS that cannot be produced within a minute at the bench | §6 | `SD-16` failing |
| Eyewash unstocked or out of date | §6 | `SD-09` — a control claimed but not verified |

---

## 8. Likely Causes *(template section)*

| # | Cause of control failure | Frequency | Confirming test |
|---:|---|---|---|
| 1 | The control equipment is not present where the work happens | **Highest** | Walk the bench; is the container, the tester, the extraction, the SDS within reach? |
| 2 | The control is present but not verified — untested strap, unstocked eyewash | High | Verification records |
| 3 | The technician was never briefed on that substance or hazard | High | `M22` competence record vs work performed |
| 4 | Time pressure — the safe route takes longer | **High and rarely admitted** | Compare control adherence at peak vs off-peak |
| 5 | Guidance exists but is not readable in Bengali | High | `SD-06` compliance |
| 6 | Guidance exists online only and the bench has no signal | Medium | `SD-07` pack contents |
| 7 | The hazard changed and the practice did not — the A1→A2L/A3 transition | **Medium and rising** | Nameplate audit vs technician assumption |
| 8 | The control was designed for a different site layout | Medium | Site-specific review |

---

## 9. Diagnostic Procedure *(template section — the hazard assessment before any work)*

**`SD-17`: this runs before the technical phase-0 check in every guide set.**

| Step | Question | If the answer is adverse |
|---:|---|---|
| 1 | Does this device contain a lithium cell, and is it sound? | §4.2 isolation |
| 2 | Does this system contain refrigerant, and of which class? | §5.1 identification; stop if unknown |
| 3 | Will this work require chemicals, and is the SDS accessible? | §6.4 |
| 4 | Is this work ESD-sensitive, and is the station verified this shift? | §3.3 |
| 5 | Is there stored energy — capacitors, UPS, battery string? | `KB-004` §2, `KB-007` §2 |
| 6 | Is the working environment adequate — ventilation, access, height, lighting? | Reschedule; do not improvise |
| 7 | Do I hold the competence and certification this work requires? | `MD-011`; reassign (`BRU-SRM-09`) |
| 8 | If this goes wrong, what is the response, and is the equipment for it within reach? | Correct before starting |

---

## 10. Repair Procedure *(template section — not applicable)*

This is a hazard-data reference. It contains no repair procedure. The procedures that consume it
are in `KB-004`…`KB-007` and `KB-012`, each of which carries its own safety block citing the
relevant section here (`SD-01`, `SD-02`).

---

## 11. Parts *(template section — hazard-classified parts)*

Bound to `MD-022` `hazard_class`:

| `hazard_class` | This file | Storage | Transport | Disposal |
|---|:--:|---|---|---|
| `esd_sensitive` | §3 | Shielding bags | Ordinary | Ordinary / e-waste |
| `lithium` | §4 | §4.3 | **§4.4 — air prohibition on damaged cells** | `MD-047` route, certificate |
| `refrigerant` | §5 | §5.3 rule 6 | Cylinder rules | Recovery, never venting |
| `chemical` | §6 | §6.3 | Per SDS | Regulated stream |
| `sharp` | — | Contained | Contained | Sharps route |
| `none` | — | Ordinary | Ordinary | Ordinary / e-waste |

**`SD-18`: a part's `hazard_class` in `MD-022` determines its handling; a part whose class is
wrong is a safety defect, not a data defect.** Corrections are raised with MDM as urgent.

---

## 12. Verification and QC *(template section)*

| Control | Verification | Frequency | Evidence |
|---|---|---|---|
| ESD strap and mat | Station tester | **Every shift** | Shift checklist (`SP-032`) |
| ESD ground path | Continuity measurement | Commissioning + after bench change | Facilities record |
| Battery isolation container present and within reach | Visual | Every shift | Shift checklist |
| Isolated cells recorded | Record vs container contents | Weekly | Battery register |
| Battery disposal certificates retrievable | Sample | Monthly | `BRU-ESG-03`, `M24` |
| Refrigerant recovered vs charged weights recorded | Job records | **Every refrigerant job** | Repair order |
| **Declared venting** | Job records | Monthly | **Target: zero** |
| Class-specific refrigerant equipment in use | Observation + equipment register | Monthly | `MD-046` |
| Refrigerant certifications current | `MD-011` | Monthly | Assignment block (`BRU-SRM-09`) |
| SDS accessible at the bench within one minute | Spot test | Monthly | HSE walk |
| Bengali hazard summaries present for English-only SDS | Review | Quarterly | `SD-16` |
| Fume extraction operating and serviced | Airflow check | Quarterly | Facilities |
| Eyewash, first aid, spill kit stocked and in date | Visual | Monthly | Shift checklist |
| Flammables stored within quantity limits | Visual | Monthly | HSE walk |
| **Incidents and near misses** | `SP-030` records | Continuous | `M59` |
| This file reviewed | HSE + Quality + Legal | **6-monthly** (`SD-10`) | Review record |

---

## 13. Resolution Coding *(template section)*

A hazard-data file carries no `MD-025` resolution code. Two coding consequences:

| Consequence | Detail |
|---|---|
| **Safety-severity faults** | `MD-024` `FLT-04` — a safety-severity fault triggers the HSE process and blocks routine closure. Swollen cells, refrigerant leaks and earth faults are the common cases |
| **Rework attribution** | Rework traceable to an ESD-control failure is attributed to the control, not to the technician — the same principle as `KB-011` `KW-17` and `KB-012` §9 |

---

## 14. Escalation *(template section)*

| Escalate when | To | Within |
|---|---|---|
| **Any thermal event, fire, venting cell, refrigerant release, arc flash or electric shock** | **HSE Lead immediately**; `SP-030` | Immediately |
| A swollen or damaged cell is found outside the isolation container | Workshop Supervisor + HSE | Same shift |
| Refrigerant class cannot be identified | Supervisor; do not open the system | Before work |
| Venting is suspected from weight records | **Quality Manager + HSE Lead** — treat as a serious matter | Same week |
| An SDS cannot be produced for a substance in use | HSE Lead; **withdraw the substance until it can be** | Same day |
| A control is claimed but cannot be verified (`SD-09`) | HSE Lead | Same week |
| A branch has no battery isolation container | **Facilities + HSE — stop battery work at that branch** | Immediately |
| Disposal certificates cannot be produced | Quality Manager + Sustainability; `BRU-ESG-03` | Same week |
| A regulatory change affects any section | **Legal Counsel + HSE Lead**; `CG-013` escalation; out-of-cycle review (`SD-10`) | Same week |
| A `MD-022` `hazard_class` is wrong | MDM as urgent (`SD-18`) | Same day |
| Any doubt at all about a hazard | **HSE Lead. There is no threshold for this one** | Immediately |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| IEC 61340-5-1 / ANSI-ESD S20.20 — technically equivalent ESD control programme standards covering grounding, protective equipment and controlled environments | 2026-08-16 | **2027-02-16** |
| UN Manual of Tests and Criteria §38.3; damaged, defective or recalled lithium batteries carry materially greater short-circuit and thermal-runaway potential and are **forbidden for transport by air** | 2026-08-16 | **2027-02-16** |
| Montreal Protocol HCFC phase-out — Bangladesh HPMP Stage II, UNDP lead implementing agency; 67.5% reduction against baseline committed by 2025; HCFC-22 conversion to R-290 and R-32 in domestic and commercial AC manufacturing; substantial HCFC-22 bank in installed commercial refrigeration | 2026-08-16 | **2027-02-16** |
| Refrigerant flammability classes — A1 non-flammable, A2L mildly flammable, A3 higher flammability | 2026-08-16 | 2027-08-16 |
| Hazardous Waste (E-waste) Management Rules 2021 (Bangladesh), under the Environment Conservation Act 1995, effective 10 June 2021 — DoE registration, waste management plans, collection targets rising 10%→50% over five years, restriction of ten RoHS-aligned substances, penalties up to 2 years or BDT 200,000 for a first offence and higher for repeat offences | 2026-08-16 | **2027-02-16 — `O-02` applicability to a service business unconfirmed** |
| `05-05` §2 `BRU-ESG-01`…`-04`; `BRU-SRM-09` | 2026-08-16 | 2027-02-16 |
| `MD-022` `hazard_class`; `MD-046`; `MD-047`; `M59`; `M18` | 2026-08-16 | 2027-02-16 |

> **Statutory caution — `CG-012` and `CG-013`.** This file states the general position from the
> sources above. **It is not a legal opinion and it is not a compliance assertion.** Three
> questions in particular are open (`O-01`, `O-02`, `O-05`) and until they are answered by named
> counsel or a named authority, nothing here should be read as establishing that current practice
> is compliant. Content class **A** requires external verification before `Approved` (`CG-002` §4).

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The wave placement is wrong and should be challenged.** The register places `KB-013` at `P1`/`W5`. **The hazards are present from the first day a technician opens a device**, and twelve other `KB` files — several needed at W2 — cite this file as the source of their safety blocks. A safety data source that arrives three waves after the work it governs is a control that does not exist when it is needed. Raised as audit finding **KB-06** | Programme Content Lead with HSE Lead and Operations Director | **W1 — the ESD, battery and refrigerant sections at minimum** |
| **O-02** | **Whether the Hazardous Waste (E-waste) Management Rules 2021 producer obligations — DoE registration, waste management plans, collection targets — apply to 1000FiX as a service and repair business rather than as a manufacturer or importer is unconfirmed.** The rules address manufacturers, assemblers, collectors, sellers and consumers; the company's position across those categories has not been determined | **Legal Counsel** with Sustainability | **W2 — `CG-013` escalation trigger** |
| **O-03** | **The damaged-cell surface-transport packaging standard is unspecified.** §4.4 states the air prohibition and the general controls; the actual packaging, labelling, quantity and declaration standard for road movement between branches does not exist. `KB-006` `O-04` records the same gap | HSE Lead with Logistics Manager | **W3 — before reverse logistics carries damaged cells** |
| **O-04** | Site-level quantity limits for damaged-cell storage and for flammables are not established (§4.3, §6.3). Without them, "within limits" is unverifiable and `SD-09` fails | HSE Lead with Facilities Manager | W2 |
| **O-05** | **The refrigerant technician-certification and cylinder-custody regime applicable in Bangladesh is not confirmed by a named authority.** `MD-011` assumes a certification exists to register and `BRU-SRM-09` blocks assignment without it. Same gap as `KB-005` `O-02` | HSE Lead with Legal Counsel and Technical Director | **W2 — blocks refrigerant article publication** |
| **O-06** | Bengali hazard summaries for English-only SDS (`SD-16`) and Bengali translation of this entire file require HSE-competent translation, not general translation. **`SD-06` prohibits machine translation and the capability is not identified** | Localisation Lead with HSE Lead | **W2 — a safety file the reader cannot read is not a control** |
| **O-07** | The battery isolation container specification — material, lining, lid, capacity, siting — is not defined. §4.2 rule 8 requires one at every bench doing battery work; 51+ branches need a specified, procurable item | HSE Lead with Facilities and Procurement | **W2 — procurement lead time** |
| **O-08** | The microwave radiation-leakage acceptance limit and instrument remain unspecified (`KB-005` `O-04`, `KB-012` `O-05`). It is a radiation-safety limit and belongs in this file once a named standard is identified | HSE Lead with Technical Director | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Template adaptation declared explicitly, with the reason, and raised as a finding rather than resolved unilaterally (`CM-R1`)
- [x] All template sections retained — Symptoms §7, Likely Causes §8, Diagnostic Procedure §9, Repair Procedure §10, Parts §11, Verification and QC §12, Resolution Coding §13, Escalation §14
- [x] Section numbering §3–§6 preserved to match thirteen inbound cross-references from twelve files
- [x] Hazard data separated from procedural safety blocks, with the division of labour stated (`SD-01`, `SD-02`)
- [x] SDS declared to govern over this file (`SD-03`)
- [x] Every hazard section names a statutory or standards anchor with a verification date (`SD-04`)
- [x] The A1→A2L/A3 refrigerant transition treated as the live, current hazard it is
- [x] "Recover, never vent" tied to a weight record that makes the behaviour visible
- [x] Damaged-lithium air-transport prohibition stated and its logistics consequence carried through
- [x] Lead-exposure route (hand-to-mouth) named explicitly rather than left to a generic hygiene line
- [x] Controls that cannot be verified declared not to be controls (`SD-09`)
- [x] Bengali stated as a safety requirement, not a translation task (`SD-06`, `SD-16`)
- [x] Non-removable from the offline pack (`SD-07`)
- [x] All internal links resolve
- [x] `BRU-ESG-*`, `BRU-SRM-*` cited to `05-05`; `BRU-KMS-*` not used in this file
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` W5 placement challenged — outstanding; the safety subset is needed at W1**
- [ ] **`O-02` e-waste rules applicability confirmed by Legal — outstanding**
- [ ] **`O-05` refrigerant certification regime confirmed — outstanding**
- [ ] **`O-06` Bengali safety translation capability identified — outstanding**
- [ ] **External verification obtained — required for content class A (`CG-002` §4) — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending HSE Lead, Quality Manager and Legal Counsel**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
