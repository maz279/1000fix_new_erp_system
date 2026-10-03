---
id: KB-007
title: Troubleshooting Guide Set — Server, Network and CCTV
project: 1000FiX ERP System v2.0
content_type: Knowledge article
template: TPL_Knowledge_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-16
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Technical
author: Technical Services with Remote Support Engineering (R13)
reviewers: [Quality Manager, Technical Director, CTO, HSE Lead, Legal Counsel, Knowledge Manager, Account Management]
approver: Technical Director with CTO
content_class: C
purpose: >
  The governing specification and article inventory for enterprise infrastructure troubleshooting —
  rack servers, RAID and NAS storage, networking, large UPS and surveillance systems. This is
  corporate and managed-services work where an error does not break one device, it stops a client's
  business; where a wrong action during a RAID rebuild destroys data that cannot be recovered; and
  where touching a CCTV system engages surveillance and privacy obligations that a repair mindset
  does not naturally consider.
traces_to: [M05, M31, M61, M29, M17, M45, P02, P03, P04, MD-021, MD-022, MD-024, MD-025, MD-046, KB-001, KB-002, KB-008, KB-013, SP-011, SP-031, SP-012]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: KB-007_Troubleshooting_Guide_Set_Server_Network_and_CCTV_BN.md
sources:
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md — estate health, alerting, patch compliance, remote access to corporate estates
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M31_Workshop_and_Depot_Repair_Management.md — bench repair and escalation levels
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-SEC-01…08 security rules; BRU-SRM-14 L3 restriction; 05-04 role and access matrix
    verified: 2026-08-16
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P04 corporate estate management, SLA and compliance downloads; P03 Managed Services Console
    verified: 2026-08-16
    class: P1
  - source: ISO 9001:2015 clause 7.1.5 monitoring and measuring resources — where measurement traceability is required, equipment must be calibrated or verified at defined intervals against traceable standards and its status identified
    verified: 2026-08-16
    class: P1
supersedes: none
review_due: 2027-02-16
---

# KB-007 — Troubleshooting Guide Set: Server, Network and CCTV

| Item | Value |
|---|---|
| Article type | **Troubleshooting** (guide-set specification) |
| Device family | `DF-SRV` — server, storage and network · `DF-SEC` — CCTV, access control and security systems |
| Brand / model scope | All serviced `DF-SRV` and `DF-SEC` models in `MD-021` |
| Skill level required | L2 to L3; most articles require `R13` Remote Support Engineer competence rather than a bench repair level |
| Offline pack member | **Partially** — decision trees and safety cards yes; procedures requiring live console access no |
| Review due | 2027-02-16 |

> **Template conformance.** Troubleshooting-type article applied at guide-set level; all
> `TPL_Knowledge_Article.md` sections retained in order. Sections 11–14 are justified additions,
> consistent with [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) §11.

---

## 1. Purpose and Scope

**The organising principle of this set is blast radius.** Every other guide set optimises for
speed of repair. This one optimises for *not making it worse* — because the failure mode here is
not a device that stays broken, it is a client's operation that stops, a dataset that ceases to
exist, or a surveillance record that can no longer be produced when it is asked for.

**In scope:**

| Sub-family | `MD-021` family | Typical client | Dominant failure classes | Blast radius |
|---|---|---|---|---|
| Rack and tower servers | `DF-SRV` | `P04` corporate, MSP estates | PSU, memory, storage, thermal, firmware, RAID controller | A department or a business |
| RAID arrays and NAS | `DF-SRV` | Corporate, SME | Disk failure, controller, rebuild failure, filesystem | **Irreversible data loss** |
| Networking — switches, routers, firewalls, access points, structured cabling | `DF-SRV` | All corporate | Port, PSU, config, firmware, cabling, power over Ethernet | A site |
| Large UPS and power distribution | `DF-SRV` | Corporate, branch | Battery string, inverter, bypass, monitoring | **Everything downstream** |
| CCTV and surveillance — cameras, NVR/DVR, storage, PoE | `DF-SEC` | Corporate, retail, branch | Camera, PoE, storage, network, recording retention | Loss of a legally relevant record |
| Access control | `DF-SEC` | Corporate | Controller, reader, lock hardware, door position | **Life-safety egress** |

**Out of scope:**

| Subject | Owned by |
|---|---|
| Desktop-class PCs, laptops, printers, monitors, small UPS | [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) |
| Data recovery from a failed array as a chargeable service | `M06` · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) |
| The managed-services process — consent, session control, patching, alert handling | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) · `M05` |
| Internal IT change management and CAB | [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) · `M66` — **that governs 1000FiX's own systems, not a client's** |
| Identity, access and security policy | `M29` · `05-04` |
| Cloud and hosted infrastructure | **Not in the serviced range.** Recorded as a boundary — see `O-05` |

> **The `KB-004` / `KB-007` boundary** is resolved by blast radius, as stated in `KB-004` §1: a
> device that takes down one user is `KB-004`; a device that takes down a business is here. The
> Master Index descriptions for the two files overlap on "server and storage" and this is raised as
> audit finding **KB-01**.

---

## 2. Safety

> ⛔ **DANGER — three-phase supply, PDUs and large UPS.** Rack power distribution and large UPS
> systems carry currents and voltages far above the domestic case, and a UPS **presents live output
> with the mains isolated** (hazard). Contact causes death (consequence). **Isolate mains, isolate
> the battery string, engage maintenance bypass only per the manufacturer's documented sequence,
> prove dead at the point of work, and never assume an isolator has done what its label says**
> (avoidance). Work on the supply side of a client's installation is an **electrician's work, not a
> technician's** — see `TG-40`.

> ⚠ **WARNING — battery strings.** Large UPS battery strings store very high energy at low
> impedance; a dropped spanner across terminals produces an arc flash (hazard). Severe burns and
> blindness (consequence). **Insulated tools, no jewellery, eye protection, one hand where
> practicable, string isolated and links removed before work** (avoidance). Data in `KB-013` §4.

> ⚠ **WARNING — rack mechanics.** Servers and UPS units are heavy, and a rack with units extended
> on rails can topple (hazard). Crush injuries (consequence). **Stabilisers deployed, one unit
> extended at a time, two-person handling above the stated limit** (avoidance).

> ⚠ **WARNING — working at height and in ceiling voids for cameras and access points.** (hazard)
> Falls and contact with unidentified services (consequence). **Fall protection per `SP-030`;
> assume services in a void are live until proven otherwise** (avoidance).

> ⚠ **CAUTION — noise and airflow.** Data rooms run at high fan noise and low temperature (hazard).
> Hearing exposure over long sessions; hypothermia is not a joke on a night-long rebuild
> (consequence). **Hearing protection on extended work; plan breaks** (avoidance).

> ⚠ **CAUTION — fibre optics.** Fibre ends and cleave offcuts cause eye injury and skin
> penetration; active fibre carries invisible laser energy (hazard). **Never look into a fibre end
> or a transceiver port; contain offcuts; eye protection when cleaving** (avoidance).

> ⛔ **DANGER — data loss is irreversible.** This is a `DANGER` block deliberately, though the harm
> is not physical. On a degraded RAID array, a single wrong action — pulling the wrong disk,
> initialising instead of importing, forcing a rebuild onto a suspect member — destroys data that
> **no subsequent skill can recover** (hazard). A client's business records cease to exist
> (consequence). **Stop. Do not act on a degraded array without the `TG-36` sequence below and a
> recorded client decision** (avoidance).

> **NOTICE — surveillance and privacy.** Accessing CCTV footage, exporting recordings, or changing
> retention settings engages privacy obligations and can destroy evidence. See §6.2.

> **NOTICE — access control and life safety.** Door controllers and locks are part of a building's
> **egress** provision. A change that leaves a door secure but not openable from inside is a
> life-safety failure. See §6.3.

**`TG-01` applies.** **`TG-37`: no article in this set may be published without both HSE approval
(physical hazards) and CTO or delegate approval (data, security and privacy consequences)** — the
`M61` §9 `BRU-KMS-03` gate applied twice, because this set has two distinct classes of irreversible
harm.

---

## 3. Symptoms

| Sub-family | Symptom (EN) | Symptom (BN) | `SYM-` binding | First route |
|---|---|---|---|---|
| Server | Will not power on | চালু হচ্ছে না | `SYM-00101` | On-site |
| Server | Powers on, no POST / halts at boot | পাওয়ার আছে, বুট হচ্ছে না | `SYM-` post-fail | On-site — **`KB-008`** |
| Server | Amber health LED / alert on management controller | হেলথ অ্যালার্ট দেখাচ্ছে | `SYM-` health-alert | **Remote first** |
| Server | Unexpected reboots | নিজে নিজে রিস্টার্ট হচ্ছে | `SYM-` stability | Remote first |
| Server | Overheating / fans at maximum | অতিরিক্ত গরম, ফ্যান ফুল স্পিড | `SYM-` thermal | On-site |
| Server | Performance degradation | ধীর গতি | `SYM-` performance | Remote |
| RAID / NAS | **Array degraded — disk failure reported** | **ডিস্ক ফেইল, অ্যারে ডিগ্রেডেড** | `SYM-` array-degraded | **Remote assessment — `TG-36` before any action** |
| RAID / NAS | Array offline / will not mount | অ্যারে অফলাইন | `SYM-` array-offline | **Stop — escalate** |
| RAID / NAS | Rebuild failing or stalling | রিবিল্ড হচ্ছে না | `SYM-` rebuild-fail | **Stop — escalate** |
| RAID / NAS | Share not accessible | শেয়ার অ্যাক্সেস হচ্ছে না | `SYM-` access | Remote |
| Network | Site or segment down | নেটওয়ার্ক ডাউন | `SYM-` link-down | Remote then on-site |
| Network | Intermittent connectivity / packet loss | মাঝে মাঝে সংযোগ চলে যায় | `SYM-` intermittent | Remote |
| Network | Slow throughput | নেটওয়ার্ক ধীর | `SYM-` throughput | Remote |
| Network | PoE device not powering | PoE ডিভাইস চালু হচ্ছে না | `SYM-` poe | On-site |
| Network | Switch or AP unreachable | সুইচ / এপি পাওয়া যাচ্ছে না | `SYM-` unreachable | Remote then on-site |
| UPS | On battery with mains present | মেইন আছে তবু ব্যাটারিতে চলছে | `SYM-` transfer | On-site |
| UPS | Battery fault / no runtime | ব্যাকআপ দিচ্ছে না | `SYM-` runtime | On-site |
| UPS | Alarm / fault code | অ্যালার্ম বাজছে | `SYM-` coded-fault | **`KB-008`** |
| UPS | On bypass | বাইপাসে আছে | `SYM-` bypass | **On-site urgently — no protection** |
| CCTV | Camera offline | ক্যামেরা অফলাইন | `SYM-` camera-offline | Remote then on-site |
| CCTV | No recording / gaps in footage | রেকর্ডিং হচ্ছে না | `SYM-` recording | **Remote — evidence implications** |
| CCTV | Poor image, night-vision failure | ছবি পরিষ্কার নয় | `SYM-` image-quality | On-site |
| CCTV | Storage full or failing | স্টোরেজ ভরে গেছে | `SYM-` storage | Remote |
| CCTV | Cannot export footage | ফুটেজ রপ্তানি হচ্ছে না | `SYM-` export | **Remote — §6.2 applies** |
| Access control | Door will not unlock / will not secure | দরজা খুলছে না / লক হচ্ছে না | `SYM-` door | **On-site urgently — life safety** |
| Access control | Reader not responding | রিডার কাজ করছে না | `SYM-` reader | On-site |

**`TG-02` applies.**

---

## 4. Likely Causes

| Symptom | # | Likely cause | Frequency | Confirming test |
|---|---:|---|---|---|
| Server no POST | 1 | Memory module or seating | High | Single-module boot; management-controller log |
| | 2 | PSU or power path | High | Redundant PSU isolation; PSU LED |
| | 3 | Firmware / BIOS corruption | Medium | Management-controller recovery |
| | 4 | CPU or board | Low | Escalate — do not swap speculatively |
| Server health alert | 1 | Predictive disk failure | **Highest** | Management-controller log; SMART data |
| | 2 | Fan or thermal sensor | High | Log + physical check |
| | 3 | Memory correctable-error threshold | Medium | Log |
| | 4 | Battery on the RAID cache module | Medium | Controller status |
| **Array degraded** | 1 | Single member disk failure | **Highest** | Controller status; **do not touch until `TG-36` is complete** |
| | 2 | Cable or backplane fault presenting as disk failure | High | Slot and cable swap **only after assessment** |
| | 3 | Controller fault | Medium | Log |
| | 4 | Multiple ageing disks from one batch reaching end of life together | **Underestimated and dangerous** | Purchase dates and hours across all members |
| Rebuild failing | 1 | A second member with unreadable sectors | **Highest** | Controller log; media-error counts |
| | 2 | Insufficient array health for the rebuild load | High | Pre-rebuild assessment |
| | 3 | Wrong disk replaced | **Catastrophic when it happens** | Serial-to-slot record from `TG-36` |
| Network intermittent | 1 | Cabling — termination, bend, damage, length | **Highest** | Certification test |
| | 2 | Duplex or speed mismatch | High | Interface counters |
| | 3 | Failing transceiver or port | Medium | Port and optic swap |
| | 4 | Power or thermal instability on the switch | Medium | Environment check |
| | 5 | Loop or broadcast storm | Medium | Topology and counters |
| PoE not powering | 1 | Power budget exceeded on the switch | **Highest** | Budget vs allocation |
| | 2 | Cable length or quality | High | Certification test |
| | 3 | Standard mismatch — device requires more than the port supplies | Medium | Device rating vs port class |
| UPS on battery with mains present | 1 | Input supply out of tolerance | High | Input voltage and frequency log |
| | 2 | Input breaker or fuse | Medium | Physical check |
| | 3 | Transfer relay or rectifier | Medium | Log |
| UPS no runtime | 1 | Battery string at end of life | **Highest** | Load test; string age |
| | 2 | Single weak block dragging the string | High | Per-block voltage |
| | 3 | Charger fault | Medium | Charge voltage |
| Camera offline | 1 | PoE / power | **Highest** | Port status |
| | 2 | Cable or connector, often outdoor water ingress | High | Certification test; visual |
| | 3 | Camera failure | Medium | Bench test |
| | 4 | Network or NVR configuration | Medium | Config review |
| No recording / gaps | 1 | Storage disk failure | **Highest** | NVR log; SMART |
| | 2 | Retention setting shorter than believed | **High — and often the real answer** | Retention configuration vs client expectation |
| | 3 | Motion-detection configuration | Medium | Config review |
| | 4 | NVR overload — too many streams for the hardware | Medium | Stream count vs rating |

---

## 5. Diagnostic Procedure

The five-phase shape (`TG-03`) applies, preceded by a phase unique to this set.

| Phase | Requirement |
|---:|---|
| **−1 — Authorisation and window** *(this set only)* | Confirm the client's authorisation for the work, the agreed **maintenance window**, the change record, the rollback plan and who the client's decision-maker is. Consent and session logging per `SP-011` and `M05` |
| **0 — Safety and blast radius** | Electrical isolation plan · **what stops if this goes wrong, and who is told** · data-at-risk assessment · backup status verified **before** any change |
| **1 — Reproduce** | Reproduce from logs and monitoring first. On production infrastructure, reproducing by re-triggering the fault is often unacceptable — say so |
| **2 — Isolate** | Configuration → environment → cabling → component. **Cheapest and least destructive first, always** |
| **3 — Measure** | Interface counters, cable certification, per-block battery voltage, thermal readings, controller logs |
| **4 — Conclude** | Coded fault, resolution, parts, **and a client-facing statement of what happened and what changed** |
| **5 — Restore and verify** *(this set only)* | Return to full redundancy, confirm monitoring is reporting healthy, confirm the client can see it, close the change record |

**`TG-38`: no change to production infrastructure without a recorded rollback plan.** An article
that describes a change without describing how to undo it is incomplete and fails review.

**`TG-39`: verify the backup before touching the data path.** Not "ask whether there is a backup" —
verify its existence, its age and its restorability to whatever degree the situation allows, and
record what was verified. Most catastrophic data-loss incidents in this class of work were
survivable until someone acted on an assumption about a backup.

### 5.1 `TG-36` — the degraded-array sequence

**This is the most important procedure in this guide set.** It is stated here, at set level, rather
than only in an article, because it must be identical everywhere and because a technician meeting a
degraded array for the first time will not know which article to open.

| Step | Action | Never |
|---:|---|---|
| 1 | **Stop. Change nothing.** Photograph the front of the array showing every drive LED | Never pull a disk to "see which one it is" |
| 2 | Record the controller's view: array status, member serials, slot positions, media-error counts, rebuild history | — |
| 3 | **Record the physical serial of the disk in every slot**, matched to the controller's logical view | Never rely on slot numbering alone; slot maps are not universal |
| 4 | Verify the backup: exists, age, scope, restorability (`TG-39`) | Never proceed on "the client says there's a backup" |
| 5 | Assess whether the array is **degraded but readable**. If it is, the priority is **copying data off, not rebuilding** | Never start a rebuild before considering a copy |
| 6 | Assess the remaining members' health. Multiple disks from one batch age together — a rebuild loads every surviving disk hardest at exactly the wrong moment | Never assume the other members are fine because they are not flagged |
| 7 | Present the client with the options and the risk of each **in writing**, and obtain a recorded decision | Never make the risk decision on the client's behalf |
| 8 | If replacing: replace **only** the disk whose serial was recorded as failed in step 3 | Never remove a disk that is not the recorded failed member |
| 9 | Monitor the rebuild; record its progress; do not power-cycle the array during it | Never interrupt a rebuild to "reset" it |
| 10 | If the rebuild fails or a second member fails: **stop and escalate to data recovery (`M06`, `SP-012`)** | Never retry a failed rebuild without escalation |
| 11 | Record everything on the job, including photographs and serials | — |

> **Step 7 is the step that gets skipped, and it is the one that matters most.** The technician's
> judgement about whether to copy first or rebuild first is a *business risk decision about the
> client's data*, and it belongs to the client. Making it for them — even correctly — transfers the
> consequence of an unlucky outcome onto 1000FiX.

---

## 6. Repair Procedure

Rules `TG-05`…`TG-14` apply. This set adds:

| # | Rule |
|---|---|
| **TG-36** | The degraded-array sequence in §5.1 is mandatory and is not abbreviated |
| **TG-37** | Articles require both HSE and CTO-side approval |
| **TG-38** | No production change without a recorded rollback plan |
| **TG-39** | Verify the backup before touching the data path |
| **TG-40** | **Work on the client's fixed electrical installation is out of scope.** Articles state where the company's responsibility ends — at the plug, the isolator or the demarcation point named in the contract — and require an electrician referral beyond it |
| **TG-41** | Firmware updates on production infrastructure state the rollback path **before** the update step, and are performed only in an agreed window |
| **TG-42** | Configuration changes are captured before and after; the before-state is stored as the rollback artefact |
| **TG-43** | Any credential used is the client's issued account under `SP-011`; **shared or personal credentials are never used**, and no credential is recorded in an article, a job note or a photograph (`BRU-SEC-*`, `M29`) |
| **TG-44** | Articles state the maintenance-window requirement for the class of change they describe |
| **TG-45** | CCTV articles follow §6.2; access-control articles follow §6.3 |

### 6.2 CCTV, footage and privacy

| Situation | Required handling |
|---|---|
| Any access to recorded footage | Only under the client's written authorisation, for a stated purpose, logged. Viewing footage because it is on the screen in front of you is not authorised access |
| Export of footage | Only to the client's named recipient, by the agreed method, with a record of what was exported and to whom. **1000FiX does not retain a copy** |
| A change that reduces retention | **Requires explicit client authorisation in writing.** Reducing retention destroys records the client may be legally required to hold |
| A fault that has already caused a recording gap | Report it to the client immediately and in writing, with the period affected. Do not quietly repair and move on — the gap may matter to a claim or an investigation |
| A request from anyone other than the client for footage | **Refuse and escalate to Legal.** Including a request that appears to come from an authority |
| Camera placement changes | Placement can create privacy exposure. Advise; do not decide |

### 6.3 Access control and egress

| Situation | Required handling |
|---|---|
| Any work on a door controller or lock | Establish the **fail-safe / fail-secure** behaviour of that door **before** touching it, and confirm it matches the building's fire strategy |
| Testing | Test egress from inside on every door worked on, before leaving. Every time |
| A door that cannot be made both secure and egress-capable | **Leave it egress-capable and report it.** Life safety outranks security, and this is not a judgement call for the technician to weigh |
| Fire-alarm interface | Do not disconnect or override a fire-alarm release interface. Escalate |

---

## 7. Parts

| Rule | Detail |
|---|---|
| Identification and class | `MD-022` codes and `part_class`; enterprise hardware frequently requires vendor-specific firmware on the part itself |
| **Disk handling** | Disks arriving or leaving may hold client data. Custody, handling and disposal follow `SP-012` and the erasure/destruction rule `BRU-ESG-01` |
| Hazard class | UPS batteries — `chemical`, high stored energy; boards — `esd_sensitive` |
| Calibration | Cable certification testers and electrical test instruments are controlled equipment under `MD-046`; **ISO 9001:2015 clause 7.1.5 requires calibration or verification at defined intervals against traceable standards, with status identified** |
| Consignment and spares pools | Corporate contracts often carry a dedicated spares pool; it is not general stock |
| Serialisation | Enterprise parts are serialised; serial captured at receipt and issue (`BRU-INV-08`) |

**High-movement part families**

| Family | Note |
|---|---|
| Enterprise disks (SAS/SATA/NVMe) | **Client data.** Never leave site with one without a custody record |
| Server PSUs and fans | Hot-swap; verify redundancy restored |
| Memory modules | Vendor-qualified parts matter |
| RAID controllers and cache batteries | Configuration must be preserved |
| Transceivers and patch leads | Highest-frequency network part |
| Switch and AP units | Configuration restore is the real work |
| UPS battery blocks and strings | **Arc-flash hazard**; disposal route mandatory (`MD-047`) |
| Cameras, lenses, housings, PoE injectors | Outdoor water ingress is the dominant failure |
| NVR storage disks | Retention and evidence implications |
| Door controllers, readers, locks, REX devices | **Life-safety components** |

---

## 8. Verification and QC

| Repair class | Test | Pass criterion | Recorded in |
|---|---|---|---|
| Server hardware | Post-repair health | Management controller reports all subsystems healthy; **redundancy restored**; no outstanding alerts | Repair order + controller log export |
| **Array rebuild** | Rebuild completion | Array reports optimal; **all member serials match the `TG-36` record**; a post-rebuild verification pass completes; **client informed in writing** | Repair order + photographs + client acknowledgement |
| Network cabling | Certification test | Passes to the installed cabling standard for its category and length | Certification report attached |
| Switch / AP replacement | Configuration and traffic | Configuration restored from the `TG-42` before-state; all ports and clients as before; counters clean over an observed period | Repair order + config diff |
| PoE | Budget and delivery | Device powers and holds; switch power budget within limit | Repair order |
| UPS battery | Load test | Achieves rated runtime at rated load within tolerance; **clean transfer on simulated mains loss**; per-block voltages within spread | Repair order + readings |
| UPS on bypass | Return to normal | Returned to normal operation, **not left on bypass**; alarms cleared and understood | Repair order |
| CCTV camera | Image and recording | Live image to specification day and night; **recording verified present in the NVR for a test period**; retention setting confirmed against the client's stated requirement | Repair order + screenshot |
| CCTV storage | Retention verification | Actual retained duration measured, not assumed; client informed if it differs from expectation | Repair order |
| Access control | **Egress test** | **Door opens from inside under normal and power-fail conditions**; secures correctly; fire interface intact | Repair order — **mandatory, no exceptions** |
| **All** | Monitoring restored | The client's monitoring shows the device healthy and the alert cleared | `M05` estate view |
| **All** | Change closed | Change record closed with what changed, what was verified, and the rollback artefact retained | `SP-011` |

---

## 9. Resolution Coding

| `action_class` | Note for this set |
|---|---|
| `configure` | **The most common genuine resolution in this family** and the most under-recorded. Configuration is the work |
| `replace_part` | Hot-swap components; part issue required (`RES-02`) |
| `repair` | Component-level work is rarer here; most enterprise hardware is replaced at module level |
| `replace_unit` | Whole-unit replacement under a support contract |
| `clean` | Filters, fans, dust in racks and outdoor camera housings |
| `calibrate` | Cable certification and electrical instruments — the **instrument** is calibrated, not the client's device (`MD-046`, ISO 9001 clause 7.1.5) |
| `no_fault_found` | Common on intermittent network complaints. Supervisor countersignature (`RES-04`); record what was measured so the next visit starts further along |
| `beyond_economic_repair` | End-of-support enterprise hardware; `BRU-SRM-12` evidence and second-technician confirmation |

---

## 10. Escalation

| Escalate when | To | With what evidence |
|---|---|---|
| **A degraded array is found** | Do not act. R13 senior + client decision-maker (`TG-36` step 7) | Photographs, serials, controller log |
| **A rebuild fails or a second member fails** | **Data recovery (`M06`, `SP-012`) — stop all further action** | Full `TG-36` record |
| Data has been or may have been lost | Immediately: Account Manager, Quality Manager, CTO. **Client informed the same day** | Complete timeline |
| Work required on the client's fixed electrical installation | Client's electrician (`TG-40`) | Findings, photographs |
| A door cannot be made both secure and egress-capable | Leave egress-capable; branch manager and client immediately (`§6.3`) | Door state, photographs |
| Any request for CCTV footage from a party other than the client | **Legal Counsel** (`§6.2`) | The request, recorded |
| A recording gap is discovered | Client, in writing, the same day | Period affected |
| Change window exceeded or rollback needed | Client decision-maker; execute the `TG-38` rollback | Change record |
| Credentials found shared, hard-coded or exposed | Security (`M29`); do not use them | Finding, no credential values recorded |
| Certification or competence not held for the work | Reassign (`BRU-SRM-09`, `BRU-SRM-14`) | Competence status |
| A pattern appears across a client estate | [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) and the Account Manager | Occurrence data |
| Any injury, arc event, fall or electrical shock | **HSE immediately** (`SP-030`) | Incident record |

---

## 11. Guide Set Inventory *(addition — justified as in `KB-004` §11)*

**34 articles.**

### 11.1 Governing and safety — 6 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 1 | **The degraded-array sequence (`TG-36`) — stop, record, verify, decide** | `procedure` | L2 | **P0** |
| 2 | **Rack, PDU and large-UPS electrical safety** | `safety_note` | L2 | **P0** |
| 3 | **UPS battery string safety and arc-flash control** | `safety_note` | L2 | **P0** |
| 4 | Blast-radius assessment and the maintenance-window rule | `procedure` | L2 | P1 |
| 5 | Backup verification before any data-path work (`TG-39`) | `procedure` | L2 | **P0** |
| 6 | Rollback planning and configuration capture (`TG-38`, `TG-42`) | `procedure` | L2 | P1 |

### 11.2 Server — 6 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 7 | Server will not power on or POST | `fault_fix` | L2 | P1 |
| 8 | Management-controller health alerts and their interpretation *(links `KB-008`)* | `fault_fix` | L2 | P1 |
| 9 | Memory and CPU fault diagnosis | `fault_fix` | L2→L3 | P2 |
| 10 | Thermal and airflow faults in a rack | `fault_fix` | L2 | P2 |
| 11 | Firmware update and rollback on production hardware | `procedure` | L2 | P1 |
| 12 | Hot-swap component replacement and redundancy verification | `procedure` | L2 | P1 |

### 11.3 Storage and RAID — 5 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 13 | Disk failure and member replacement | `procedure` | L2 | P0 |
| 14 | Rebuild management, monitoring and failure handling | `procedure` | L2→L3 | P0 |
| 15 | Array offline or unmountable — **escalation, not repair** | `procedure` | L2 | **P0** |
| 16 | NAS share and permission faults | `fault_fix` | L2 | P2 |
| 17 | Disk custody, erasure and disposal | `procedure` | L1 | P1 |

### 11.4 Network — 8 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 18 | Site or segment down — structured isolation | `fault_fix` | L2 | P1 |
| 19 | Intermittent connectivity and packet loss | `fault_fix` | L2 | P1 |
| 20 | Cable certification, faults and remediation | `procedure` | L2 | P1 |
| 21 | Switch and access-point replacement with configuration restore | `procedure` | L2 | P1 |
| 22 | PoE budget, standards and delivery faults | `fault_fix` | L2 | P1 |
| 23 | Fibre and transceiver faults — **with optical safety** | `fault_fix` | L2 | P2 |
| 24 | Loops, storms and topology faults | `fault_fix` | L2→L3 | P2 |
| 25 | Wireless coverage and interference diagnosis | `fault_fix` | L2 | P2 |

### 11.5 UPS and power — 3 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 26 | UPS alarm and fault-code interpretation *(links `KB-008`)* | `fault_fix` | L2 | P1 |
| 27 | Battery string testing and block replacement | `procedure` | L2 | P1 |
| 28 | Bypass, transfer and return-to-normal procedures | `procedure` | L2 | **P0** |

### 11.6 CCTV and access control — 6 articles

| # | Article | Type | Level | Pri |
|---:|---|---|:--:|:--:|
| 29 | **Footage access, export and privacy handling (`§6.2`)** | `procedure` | L1 | **P0** |
| 30 | Camera offline diagnosis — power, cable, network, device | `fault_fix` | L2 | P1 |
| 31 | Recording gaps, retention verification and client notification | `procedure` | L2 | P1 |
| 32 | NVR storage failure and capacity faults | `fault_fix` | L2 | P1 |
| 33 | Image quality, night vision and outdoor ingress | `fault_fix` | L2 | P2 |
| 34 | **Access control — fail-safe, fail-secure and the mandatory egress test (`§6.3`)** | `procedure` | L2 | **P0** |

**Set totals:** 34 articles · 10 at P0 · 15 at P1 · 9 at P2 · 0 at P3 ·
**all 34 require the dual approval under `TG-37`**.

---

## 12. Authoring Plan, Coverage and Orphans

| Item | Position |
|---|---|
| Articles required | **34** |
| Articles written | **0** |
| Authoring effort, estimated | 34 × 5–10 hours of R13 time = **170–340 hours**, plus dual review and translation |
| **Author population** | `05-04` records **15–40 R13 Remote Support Engineers**. They are also the people delivering MSP contracts, so authoring competes directly with billable work |
| Wave | The register places `KB-007` at **W4**, aligned with `P04` corporate and MSP depth. The 10 P0 articles are needed **before the first corporate estate is taken under management**, which may be earlier than W4 — see `O-01` |
| Bilingual | This set is the strongest candidate in the category for **English-primary** authoring, because the working language of enterprise infrastructure and its vendor documentation is English. `CG-010` nonetheless places `KB-007` among the 13 bilingual files, and `AU-29` requires Bengali before field technicians read it. The tension is real and is recorded as `O-04` |

---

## 13. Related Documents

| Document | Relationship |
|---|---|
| [`KB-013_ESD_Chemical_and_Battery_Safety_Data.md`](KB-013_ESD_Chemical_and_Battery_Safety_Data.md) | §4 battery data including large stationary strings |
| [`KB-008_Fault_Code_Library_and_Interpretation_Guide.md`](KB-008_Fault_Code_Library_and_Interpretation_Guide.md) | Management-controller, UPS and NVR codes |
| [`KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md`](KB-012_Tool_Jig_and_Test_Equipment_Operating_Guides.md) | Cable certifiers and electrical instruments |
| [`KB-011_Known_Issue_and_Workaround_Register.md`](KB-011_Known_Issue_and_Workaround_Register.md) | Estate-wide recurring defects |
| [`KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md`](KB-004_Troubleshooting_Guide_Set_IT_and_Computing.md) | Shared rules; the blast-radius boundary |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-011_SOP_Remote_Support_and_Managed_Services.md) | Consent, session control and evidence |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | Escalation target for failed arrays |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-031_SOP_IT_Service_Desk_and_Change_Management.md) | Change discipline — for 1000FiX's own estate |
| [`../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md`](../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-046_Test_Equipment_and_Calibration_Master.md) | Calibration of certifiers and instruments |
| `LG-016` Managed Services and Remote Access Consent Terms | Contractual basis for §6.2 and `TG-43` |
| `TR-021` Course Pack — System Administrator | Nearest existing course; **no R13-specific pack exists** — see `O-03` |

---

## Sources and Currency

| Source | Verified | Next review |
|---|---|---|
| `M05` Remote Support and Managed Services; `M31`; `M29` | 2026-08-16 | 2027-02-16 |
| `05-05` §2 `BRU-SRM-09`, `-12`, `-14`; `BRU-SEC-01`…`-08`; `BRU-INV-08`; `BRU-ESG-01` | 2026-08-16 | 2027-02-16 |
| `05-04` role and access matrix — R13 population 15–40 | 2026-08-16 | 2027-02-16 |
| `04-00` `P04` corporate estate management and compliance downloads; `P03` Managed Services Console | 2026-08-16 | 2027-02-16 |
| ISO 9001:2015 clause 7.1.5 — monitoring and measuring resources calibrated or verified at defined intervals against traceable standards, with status identified | 2026-08-16 | 2027-08-16 |
| `MD-046` calibration register; `MD-047` disposal routes | 2026-08-16 | 2027-02-16 |

> **Deliberate omission.** No cabling standard, PoE class table, UPS runtime figure or retention
> period is stated in this file. Those are installation- and client-specific and belong in the
> authored articles with their own sources (`AU-16`). Stating one here and citing it 34 times would
> propagate a single unverified figure across an entire corporate service line.

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The register places this set at W4, but the 10 P0 articles are needed before the first corporate or MSP estate is taken under management.** If any corporate contract starts before W4, this set is late by definition | Technical Director with Account Management | **Before the first MSP contract goes live** |
| **O-02** | The 34 articles are unwritten; 170–340 R13 hours unallocated, competing with billable MSP delivery | Technical Director with PMO | 10 P0 before the first estate |
| **O-03** | **There is no `TR` course pack for R13 Remote Support Engineers.** `AUDIT-006` finding SP-02 already records six SOPs with no course pack; this set adds a role-level gap. `TR-021` System Administrator is the nearest and is not the same role | Training Lead with HR Director | W4 |
| **O-04** | **The bilingual position for this set is unresolved.** `CG-010` §3.2 counts `KB-007` among the 13 bilingual `KB` files; the working language of the domain and its vendor documentation is English. Either the count changes or the translation burden is accepted knowingly | Localisation Lead with Programme Content Lead | **Before authoring — it changes the effort estimate** |
| **O-05** | Cloud and hosted infrastructure is declared out of scope in §1. If MSP contracts include cloud estates, a further set is required | Technical Director with Account Management | W4 |
| **O-06** | The client-facing wording for a discovered CCTV recording gap (§6.2) has legal consequence and does not exist. It belongs in `LG-016` or a `NT` template, not invented per incident | Legal Counsel with Content Design | W4 |
| **O-07** | `MD-024` symptom codes unallocated for most §3 entries; placeholders shown, **not minted** (`KA-02`) | Technical analyst (MDM) | Before authoring |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Knowledge_Article.md`; additions §11–§13 justified
- [x] Blast radius established as the organising principle and as the `KB-004` boundary rule
- [x] Safety blocks cover electrical, arc flash, mechanical, height, optical **and irreversible data loss**
- [x] The degraded-array sequence stated in full at set level, with the client-decision step called out
- [x] Backup verification and rollback planning made mandatory rules
- [x] CCTV privacy and access-control egress handled as distinct obligation classes
- [x] Verification includes a mandatory egress test and a measured CCTV retention check
- [x] Credentials rule stated with no credential values ever recorded
- [x] Article inventory enumerated — 34 articles with type, level and priority
- [x] Author-population constraint stated against `05-04`
- [x] All internal links resolve
- [x] `BRU-KMS-*` cited to `M61` §9; `BRU-SRM-*`, `BRU-SEC-*`, `BRU-INV-*`, `BRU-ESG-*` cited to `05-05`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 34 articles authored — outstanding**
- [ ] **`O-01` wave alignment against the first MSP contract resolved — outstanding**
- [ ] **`O-04` bilingual position resolved — outstanding; changes the effort estimate**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Dual approval recorded under `TG-37` — **pending HSE Lead and CTO**
- [ ] Named approvers recorded — **pending Technical Director and CTO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
