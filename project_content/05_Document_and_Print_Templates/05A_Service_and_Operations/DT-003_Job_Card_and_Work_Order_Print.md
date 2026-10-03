---
id: DT-003
title: Job Card and Work Order Print
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Operations
author: Operations with Workshop Management and Content Design
reviewers: [Workshop Management, Field Service, Quality, Inventory, Localisation Lead, Platform Engineering]
approver: Chief Operating Officer
content_class: C
purpose: >
  The physical artefact that travels with a device through the workshop and into the field: job
  context, device history, assigned parts, the work checklist and the time record. Required even
  in a digital-first design, because bench work happens with hands in a device and because the
  offline field case has no other authoritative record.
traces_to: [M01, M31, M02, M15, P02, DT-001, DT-002, DT-004, DT-008, DT-044, MD-024, MD-025, MD-027, MD-028, BRU-SRM-11, BRU-INV-08]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: DT-003_Job_Card_and_Work_Order_Print_BN.md
sources:
  - source: project_content/05_Document_and_Print_Templates/DT-001 Document Template Standard §3, §4 — layout declaration and field-mapping obligations
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-11 — parts cannot be issued against an unapproved paid repair
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-INV-08 — serialised parts must have their serial captured at both receipt and issue
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-SRM-14 — Level 3 board-level repairs only at an equipped workshop by a certified specialist
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-003 — Job Card and Work Order Print

> **This is a working document, not an issued one.** It goes into the workshop, gets marked up,
> and comes back. It is never given to a customer, never sent to a brand, and never used as
> evidence of what was agreed — those are `DT-004`, `DT-005` and `DT-007`.
>
> Its job is to make sure the right work happens on the right device with the right parts, when
> the technician cannot see a screen.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Internal work order / travelling job card |
| Owning module | `M01` Service Request and Order Management, with `M31` Workshop and Depot Repair |
| Statutory | No |
| Recipient(s) | Technician, workshop supervisor, QC inspector. **Never the customer** |
| Languages | **Bilingual — stacked labels.** Field technicians work in Bengali (`PS-03`) |
| Output formats | A4 portrait (primary) · A5 portrait (bench card variant) · PDF for offline device sync |
| Numbering mask | Not separately numbered — it prints the `service_order` reference from `MD-040` |
| Retention period | `LG-009` operational schedule; the **digital** record in `M01` is the retained artefact, not the paper |

### 1.1 Why a paper artefact exists in a digital-first system

| Reason | Consequence if it did not exist |
|---|---|
| Bench work is hands-in-device | A technician cannot hold a tablet and a soldering iron |
| Offline field work (`M02`, `P02`) | Rural coverage gaps mean the app syncs, the job card does not need to |
| Physical device queuing | A device on a workshop rack is identified by the card attached to it |
| Multi-technician handover | The card carries what the previous shift did, without a login |
| QC inspection (`DT-008`) | The inspector checks the physical device against a physical record |

> **It is a mirror, never a master.** Every mark on the card is transcribed into `M01` before
> the order can advance. The system record governs (`CP-01`).

---

## 2. Statutory Requirements

Not a statutory document. No mandated elements.

Two constraints nevertheless bind it, both arising from documents that *are* statutory:

| Constraint | Source | Effect |
|---|---|---|
| Personal data minimisation | `LG-008`, `05-06` NFR-086 | The card carries the **customer's first name and the last four digits of the mobile number only**. A job card left on a bench is an uncontrolled disclosure |
| Access notes never print | `BRU-SRM-20` | Passcodes and unlock codes are never printed on the card, in any variant, for any reason |

---

## 3. Layout

**Primary format: A4 portrait**, geometry per `VB-004` §4.

```
┌──────────────────────────────────────────────────┐
│ [LOGO]  JOB CARD / জব কার্ড      SR-2026-114882  │  Header
│ Branch Shewrapara · Workshop Bench 04            │
│ [BARCODE: service order ref — DT-044]            │
├───────────────────────────┬──────────────────────┤
│ DEVICE                    │ JOB                  │
│ Brand · Model             │ Type  Paid repair    │
│ Serial / IMEI             │ Priority  P2         │
│ Intake ref  INT-…-000482  │ SLA due  17/08 17:00 │
│ Condition at intake ▸     │ Assigned  Md. Karim  │
├───────────────────────────┴──────────────────────┤
│ REPORTED FAULT / জানানো সমস্যা                     │
├──────────────────────────────────────────────────┤
│ DEVICE HISTORY — last 3 jobs on this serial      │
├──────────────────────────────────────────────────┤
│ WORK CHECKLIST / কাজের তালিকা          ☐ ☐ ☐    │
├──────────────────────────────────────────────────┤
│ PARTS ISSUED / ইস্যুকৃত যন্ত্রাংশ                    │
│ Part · Qty · Serial · Issued by · Returned       │
├──────────────────────────────────────────────────┤
│ TIME RECORD / সময় রেকর্ড                          │
│ Start · Stop · Hold reason · Technician          │
├──────────────────────────────────────────────────┤
│ FINDINGS AND ACTIONS — free text, both languages │
├──────────────────────────────────────────────────┤
│ Technician sign     │ Supervisor sign   │ QC ☐   │
├──────────────────────────────────────────────────┤
│ SR-2026-114882 · Page 1 of 1 · INTERNAL          │  Footer
└──────────────────────────────────────────────────┘
```

| Zone | Content | Bilingual treatment |
|---|---|---|
| Header | Order reference, branch, bench, barcode | Title stacked |
| Party block | **Device left, job metadata right.** No customer address, no full mobile number | Labels stacked |
| Body | Fault, history, checklist, parts, time, findings | Labels stacked; free text in the technician's language |
| Totals | Not used — this document carries no money | — |
| Statutory block | Not used | — |
| Signature | Technician, supervisor, QC tick-through | Labels stacked |
| Footer | Order reference, page n of m, **INTERNAL** marking | English reference |
| Machine-readable | Barcode: service-order reference (`DT-044`) | Payload not translated |

| # | Rule |
|---|---|
| **L-03-a** | Every page is marked **INTERNAL — NOT FOR CUSTOMER** in the footer. This is the control that stops it being handed over by mistake |
| **L-03-b** | The parts table and the time record are printed with **blank rows** — 6 and 4 respectively — because they are written on by hand |
| **L-03-c** | The checklist prints one line per required step from `MD-025`, with a printed tick box. An unticked box is a visible defect |
| **L-03-d** | Device history prints the **last three** jobs on the same serial, or "No prior jobs on this device" |

---

## 4. Field Mapping

### 4.1 Header and job context

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Service order no. | সার্ভিস অর্ডার নং | `service_order.order_ref` | Monospace | ✔ | |
| Branch / workshop | শাখা / ওয়ার্কশপ | `MD-003.branch_name` | Text | ✔ | |
| Bench / bay | বেঞ্চ | `M31.bench_code` | Monospace | | Workshop jobs |
| Order type | অর্ডারের ধরন | `service_order.order_type` | Enum | ✔ | |
| Priority | অগ্রাধিকার | `MD-028.priority_code` | Code + label | ✔ | |
| SLA due | এসএলএ সময়সীমা | `service_order.sla_due_at` | `DD/MM/YYYY HH:mm` | ✔ | |
| Current status | বর্তমান অবস্থা | `MD-027.status_label` | Label per `VB-008` | ✔ | |
| Assigned technician | নিযুক্ত টেকনিশিয়ান | `employee.display_name` + ID | Text | ✔ | |
| Certification held | সনদ | `MD-011.certification_code` | Code | | **✔ on brand warranty jobs (`BRU-SRM-09`)** |
| Repair level | মেরামতের স্তর | `service_order.repair_level` | Enum: L1 / L2 / L3 | ✔ | |

### 4.2 Device and customer (minimised)

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Brand | ব্র্যান্ড | `MD-021.make` | Text | ✔ | |
| Model | মডেল | `MD-021.model` | Text | ✔ | |
| Serial / IMEI | সিরিয়াল / আইএমইআই | `device.serial_no` | Monospace | ✔ | |
| Intake reference | গ্রহণ রসিদ নং | `DT-002` reference | Monospace | ✔ | |
| Condition at intake | গ্রহণকালীন অবস্থা | `DT-002` §6.1 enumeration | Summary line | ✔ | |
| Accessories held | রক্ষিত আনুষঙ্গিক | `intake.accessories[]` | List | ✔ | Prints "None" |
| Customer | গ্রাহক | `party.first_name` + last 4 of mobile | Text | ✔ | **Minimised — see §2** |
| Warranty | ওয়ারেন্টি | `M09.warranty_state` | Enum | ✔ | |
| Brand claim | ব্র্যান্ড দাবি | `M09.claim_ref` | Monospace | | Warranty jobs |

### 4.3 Work, parts and time

| Label EN | Label BN | Source field | Format | Required | Conditional |
|---|---|---|---|:--:|---|
| Reported fault | জানানো সমস্যা | `service_order.reported_fault` | Free text | ✔ | |
| Symptom code | উপসর্গ কোড | `MD-024.symptom_code` | Code + label | ✔ | |
| Checklist step | ধাপ | `MD-025.repair_action_code` | One row per step | ✔ | |
| Part code | যন্ত্রাংশ কোড | `MD-022.part_code` | Monospace | | Where parts issued |
| Part description | যন্ত্রাংশের বিবরণ | `MD-022.part_name` | Text | | |
| Quantity | পরিমাণ | `stock_issue.qty` | Integer + `MD-023` UoM | | |
| Part serial | যন্ত্রাংশ সিরিয়াল | `stock_issue.serial_no` | Monospace | | **✔ for serialised parts (`BRU-INV-08`)** |
| Issued by | ইস্যুকারী | `employee.display_name` | Text | | |
| Old part returned | পুরাতন যন্ত্রাংশ ফেরত | `stock_issue.old_part_returned` | Bool | | **✔ on warranty jobs** |
| Start / stop | শুরু / শেষ | `time_log[]` | `HH:mm` | ✔ | Handwritten rows permitted |
| Hold reason | বিরতির কারণ | `MD-026.reason_code` | Code + label | | **✔ where the SLA clock is suspended (`BRU-SRM-15`)** |
| Findings and actions | পর্যবেক্ষণ ও কার্যক্রম | `service_order.work_notes` | Free text | ✔ | |

| # | Rule |
|---|---|
| **FM-03-a** | The card prints **only the parts already issued**. It is not a picking list and cannot authorise an issue — `BRU-SRM-11` blocks issue against an unapproved paid repair, and the card has no authority to override it |
| **FM-03-b** | Serialised parts print an empty serial box for handwriting where the serial is captured at fitting, not at issue |
| **FM-03-c** | An `L3` repair level prints the `BRU-SRM-14` banner: *"Level 3 — certified specialist and equipped workshop only"* |
| **FM-03-d** | A reprint after work has started prints the marks already transcribed, so the physical and system records converge rather than diverge |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-SRM-09` | The assigned technician's brand certification prints on brand warranty jobs; an expired certification blocks assignment before the card can print |
| `BRU-SRM-11` | Parts issue requires an approved estimate. The card records issues; it never authorises them |
| `BRU-SRM-12` | A beyond-economic-repair declaration requires photographic evidence and a **second technician's** confirmation — the card carries a second signature line for it |
| `BRU-SRM-14` | `L3` board-level work prints the specialist banner |
| `BRU-SRM-15` | Hold reasons print from `MD-026`; a hold without a reason code does not suspend the SLA clock |
| `BRU-SRM-17` | Warranty jobs print the mandatory before/after photograph reminder; the job cannot close without them |
| `BRU-SRM-18` | Repairs above BDT 25,000 print a **second-person QC** block, not a self-check tick |
| `BRU-INV-08` | Serialised parts carry a serial capture box at both issue and fit |
| `BRU-FSM-05` | GPS is captured by the app during working hours only; the printed card carries no location data |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Workshop A4** | Bench repair (`M31`), the default | Full document, six parts rows, four time rows |
| **Bench card A5** | High-throughput benches | Header, device, checklist and time only; parts recorded in the system |
| **Field A4** | On-site job (`M02`), printed before departure | Adds customer address and access instructions; drops bench/bay; adds travel time rows |
| **Offline PDF** | `P02` app, no connectivity | Identical to Field A4, rendered on device, syncs marks on reconnect (`UI-009`) |
| **Multi-device batch** | Corporate on-site sweep (`P04`) | One card per device, printed as a set with a batch cover sheet |
| **Rework** | Order linked as rework (`BRU-SRM-06`) | Prints the **original** order reference, its findings, and a prominent `REWORK` banner |
| **Marketplace seller** | Job awarded to a seller (`P07`) | Seller identity replaces technician; customer minimisation is stricter — no name at all, only the job reference (`BRU-ECM-05`) |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-003-S1` | Handset, paid, L2 workshop, 3 parts | Base bilingual rendition |
| `DT-003-S2` | Warranty job, brand certification printed | `BRU-SRM-09` and `BRU-SRM-17` bindings |
| `DT-003-S3` | L3 board repair above BDT 25,000 | Specialist banner and second-person QC block |
| `DT-003-S4` | Field job, offline render | Address block, travel time, sync marking |
| `DT-003-S5` | Rework linked to a prior order | `REWORK` banner and original-order carry-through |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Operations with Workshop Management | 2026-08-15 | Draft issue |
| Reviewer — Workshop Management | *pending* | | |
| Reviewer — Field Service | *pending* | | |
| Reviewer — Quality | *pending* | | |
| Approver — COO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | **None of its own.** Prints the `service_order` reference from `MD-040` |
| Gap policy | n/a — reprinting a job card consumes no number |
| Archive format | Not archived as a rendition. The **system record** in `M01` is the retained artefact |
| Retention | `LG-009` operational schedule, applied to the `M01` record |
| Reprint | Unrestricted and unwatermarked — it is a working copy by nature. Reprint **count** is logged for waste monitoring, not control |
| Disposal | Completed paper cards are destroyed at the branch under the confidential-waste rule in `LG-009`, because they carry a partial customer identifier |

> **Why reprint is unrestricted here and controlled everywhere else.** Reprint control exists to
> stop a second "original" circulating. This document has no original status, carries no money
> and no signature of legal effect. Applying `RC-01`…`RC-03` to it would add friction to the
> highest-frequency print in the estate for no control benefit. This is a deliberate, stated
> exception to `DT-001` §5.1 and is the only one in the category.

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard; §5.1 exception stated in §9 above |
| [`DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Supplies the intake condition and accessories this card carries |
| [`DT-004_Diagnostic_and_Condition_Report.md`](DT-004_Diagnostic_and_Condition_Report.md) | The customer-facing findings; this card is where they are first written down |
| [`DT-007_Service_Completion_Report.md`](DT-007_Service_Completion_Report.md) | Built from this card's parts and work record |
| [`DT-008_Quality_Checklist_Record.md`](DT-008_Quality_Checklist_Record.md) | The QC step this card ends with |
| [`../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md`](../05E_People_Quality_and_Labelling/DT-044_Label_Barcode_and_QR_Format_Specification.md) | Barcode payload |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-025_Repair_Action_and_Resolution_Code_Taxonomy.md) | The checklist steps |
| [`../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md`](../../02_Master_Data_and_Configuration/02C_Catalogue_and_Technical/MD-028_Priority_Severity_and_SLA_Definition_Register.md) | Priority and SLA due |
| `UI-009` Offline Sync and Conflict Resolution Copy | What the technician sees when the offline card and the system disagree |
| [`SP-010_SOP_Workshop_and_Depot_Repair.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-010_SOP_Workshop_and_Depot_Repair.md) | How a technician uses it |
| `TR-009` Course Pack — Field Technician | Where its use is taught |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven variants, data-minimisation constraint, handwriting-row rules, and the stated reprint exception to `DT-001` §5.1 | COO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] §2 states why it is not statutory and what nevertheless binds it
- [x] Field mapping resolves every printed field to a source (`FM-01`)
- [x] Data minimisation specified — no full mobile, no address on workshop variants, never an access code
- [x] The `DT-001` §5.1 reprint exception is stated and justified, not silently taken
- [x] All internal links resolve
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding; blocks `Approved`**
- [ ] Bengali rendering tested on branch A4 and A5 printers (`VB-004` BL-08) — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
