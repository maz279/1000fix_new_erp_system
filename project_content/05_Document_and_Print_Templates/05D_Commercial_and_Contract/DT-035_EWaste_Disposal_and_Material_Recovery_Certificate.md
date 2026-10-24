---
id: DT-035
title: E-Waste Disposal and Material Recovery Certificate
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Sustainability
author: Sustainability with Legal & Compliance, Inventory and Content Design
reviewers: [Legal Counsel, Quality, Inventory, Finance, Corporate Affairs, Localisation Lead]
approver: Chief Operating Officer with Legal Counsel
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Batch composition, disposal route, partner identity, recovery outcome and the environmental
  declaration. It is the environmental compliance evidence a regulator asks for and the evidence
  a corporate client needs for their own ESG reporting — which means it is read by two audiences
  with different questions and must answer both.
traces_to: [M18, M14, M15, P04, DT-001, DT-026, DT-027, DT-034, DT-036, MD-016, MD-040, MD-047, LG-009, BRU-ESG-01, BRU-ESG-02, BRU-ESG-03, BRU-ESG-04]
priority: P2
wave: W5
bilingual: yes
bn_counterpart: DT-035_EWaste_Disposal_and_Material_Recovery_Certificate_BN.md
sources:
  - source: Hazardous Waste (E-waste) Management Rules 2021, made under the Bangladesh Environment Conservation Act 1995, published by the Department of Environment on 10 June 2021 — registration obligations for manufacturers, assemblers, importers, recyclers, transporters, repairers, dismantlers, traders and exporters; environmental clearance under the Environment Conservation Rules 1997. **All obligations must be verified against the enacted text at G6**
    verified: 2026-08-15
    class: P2
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-ESG-02 — e-waste may be transferred only to a partner whose certification is current at the transfer date
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-ESG-03 — every recycled unit must have a retrievable disposal certificate
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-035 — E-Waste Disposal and Material Recovery Certificate

> ⚠ **Tier S — the Hazardous Waste (E-waste) Management Rules 2021 apply. Gate G6 mandatory and
> unwaivable (`WV-02`).**
>
> **We are a repairer and a dismantler**, which the 2021 Rules name as registrable categories.
> Whether we are registered, and under which categories, is a question with a compliance answer,
> not a documentation answer — and it must be settled before the first certificate is issued.
>
> **`BRU-ESG-03`: every recycled unit must have a retrievable disposal certificate.** Not every
> batch. Every unit.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **E-waste disposal and material recovery certificate** |
| Owning module | `M18` E-Waste, Recycling and Circular Economy |
| Statutory | **Yes — Tier S.** Hazardous Waste (E-waste) Management Rules 2021 |
| Recipient(s) | Corporate client (ESG evidence), Department of Environment on request, internal records, auditor |
| Languages | **Bilingual — parallel columns for the environmental declaration** |
| Output formats | A4 portrait · PDF for portal download (`P04`) · **PDF/A-3 archive at issue** |
| Numbering mask | `MD-040` — `EWC-{entity}-{yy}-{seq:06d}`, **`no_gaps`** |
| Retention period | Per the Rules — **pending G6**; not less than the tax retention and the client's audit window |
| Fiscal pin | **FY2026-27** |

### 1.1 The two audiences

| Audience | Their question | What the certificate must therefore show |
|---|---|---|
| **Regulator** | Was this waste handled lawfully, by a registered party, on an approved route? | Partner registration, route, quantities, hazardous fractions, our own registration |
| **Corporate client (ESG)** | What happened to our assets, and what can we report? | Per-asset traceability, recovery outcome by material, diversion from landfill, data destruction linkage |

> **One certificate, both answers.** Producing two documents creates the risk that they disagree.

---

## 2. Statutory Requirements

> All rows **unverified pending G6**.

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Handler registration with the Department of Environment | E-waste Rules 2021 — **pending G6** | pending | Header and partner block |
| Environmental clearance where required | Environment Conservation Rules 1997 — **pending G6** | pending | Partner block |
| Description and quantity of e-waste | E-waste Rules 2021 — **pending G6** | pending | Batch composition |
| Category of waste per the Schedule | E-waste Rules 2021 Schedule — **pending G6** | pending | Batch composition |
| Transfer records between handlers | E-waste Rules 2021 — **pending G6** | pending | Chain of custody |
| Recovery / disposal outcome | E-waste Rules 2021 — **pending G6** | pending | Recovery block |
| Hazardous fraction handling | E-waste Rules 2021 — **pending G6** | pending | Hazardous block |
| Record retention | E-waste Rules 2021 — **pending G6** | pending | §9 |

### 2.1 G6 questions

| # | Question |
|---|---|
| **EW1** | **Under which categories of the 2021 Rules must 1000FiX register** — repairer, dismantler, trader, others — and are we registered? |
| **EW2** | Does environmental clearance under the 1997 Rules apply to any of our sites? |
| **EW3** | What records and returns must a registered handler maintain and submit, and on what cycle? |
| **EW4** | What documentation must accompany an e-waste transfer between handlers, and does it replace or supplement `DT-027`? |
| **EW5** | Which of the products we handle fall inside the Schedule? |
| **EW6** | What are the obligations for hazardous fractions — batteries, CRT, mercury lamps, refrigerant? |
| **EW7** | Is there an extended-producer-responsibility or take-back obligation that applies to us? |
| **EW8** | What retention applies to disposal records? |

> **EW1 is a compliance exposure, not a content question.** If registration is required and we do
> not hold it, that is a matter for immediate escalation under `CG-013`, independent of this
> template.

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | **E-WASTE DISPOSAL CERTIFICATE**, certificate number, issue date, batch reference | Title stacked |
| Party block | Client (waste generator) left; our entity, registration, and the disposal partner right | Labels stacked |
| Body | Batch composition → per-asset schedule → hazardous fractions → route and custody → recovery outcome | Labels stacked |
| Totals | Weight by material category; diversion and recovery percentages | Arabic numerals |
| Statutory block | **Environmental declaration** and the regulatory-compliance statement | **Parallel columns** |
| Signature | Our authorised officer and the disposal partner's authorised officer | Labels stacked |
| Footer | Certificate reference, `page n of m`, verification QR | English |

| # | Rule |
|---|---|
| **L-35-a** | The **per-asset schedule is mandatory** where the client is identified (`BRU-ESG-03`). A weight-only certificate cannot tell a client what happened to their asset |
| **L-35-b** | Hazardous fractions are itemised separately with their handling route. Aggregating them into "e-waste" hides the part that is actually regulated |
| **L-35-c** | The disposal partner's registration number and its **validity at the transfer date** print (`BRU-ESG-02`) |
| **L-35-d** | Recovery outcome is stated as **measured or estimated**, and which. An estimated recovery rate presented as measured is a false ESG claim by the client who republishes it |
| **L-35-e** | The declaration never splits across a page |
| **L-35-f** | Where devices carried data, the `DT-034` certificate reference prints per asset |

---

## 4. Field Mapping

### 4.1 Parties, batch and assets

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Certificate no. | সনদ নং | `MD-040` sequence | Monospace | ✔ |
| Issue date | ইস্যুর তারিখ | `ewc.issued_at` | `DD/MM/YYYY` | ✔ |
| Batch reference | ব্যাচ সূত্র | `M18.batch_ref` | Monospace | ✔ |
| Client / waste generator | গ্রাহক | `party` / `MD-015` | Text | ✔ where identified |
| Our entity and registration | আমাদের নিবন্ধন | `MD-002` + DoE registration | Text + monospace | ✔ **pending EW1** |
| **Disposal partner** | নিষ্পত্তি অংশীদার | `MD-016` / `MD-047.partner` | Text | ✔ |
| **Partner registration no.** | অংশীদারের নিবন্ধন নং | `MD-047.partner_registration` | Monospace | ✔ **`BRU-ESG-02`** |
| Partner registration valid to | মেয়াদ | `MD-047.registration_expiry` | `DD/MM/YYYY` | ✔ |
| Transfer date | হস্তান্তরের তারিখ | `M18.transferred_at` | `DD/MM/YYYY` | ✔ |
| Asset serial / tag | সিরিয়াল / ট্যাগ | `device.serial_no` / `asset_tag` | Monospace | ✔ **per asset (`L-35-a`)** |
| Asset make / model | মেক / মডেল | `MD-021` | Text | ✔ per asset |
| Asset category per Schedule | শ্রেণি | Per **G6 EW5** | Code | ✔ per asset |
| Data destruction certificate | ডেটা ধ্বংস সনদ | `DT-034` reference | Monospace | ✔ **where the asset carried data** |
| Weight per asset or batch | ওজন | `M18.weight_kg` | kg, 2 dp | ✔ |

### 4.2 Composition, hazardous fractions and recovery

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Material category | উপাদানের শ্রেণি | `MD-047.material_code` | Code + label | ✔ |
| Weight by material | শ্রেণিভিত্তিক ওজন | `M18.material_weight` | kg, 2 dp | ✔ |
| **Hazardous fraction** | বিপজ্জনক অংশ | `MD-047.hazardous_flag` | Bool + type | ✔ |
| Hazardous handling route | বিপজ্জনক অংশের গতি | `MD-047.hazard_route` | Text | ✔ **per fraction (`BRU-ESG-04`)** |
| Disposal route | নিষ্পত্তির পথ | `MD-047.route_code` | Enum: recycle / recover / refurbish / energy recovery / landfill | ✔ |
| **Recovered material** | পুনরুদ্ধারকৃত উপাদান | `M18.recovered_weight` | kg, 2 dp | ✔ |
| Recovery rate | পুনরুদ্ধারের হার | Computed | %, 1 dp | ✔ |
| **Measured or estimated** | পরিমাপকৃত / আনুমানিক | `M18.recovery_basis` | Enum | ✔ **`L-35-d`** |
| Diverted from landfill | ভরাট থেকে রক্ষা | Computed | kg + % | ✔ |
| Residual to landfill | অবশিষ্ট | Computed | kg + % | ✔ |
| Carbon / environmental estimate | পরিবেশগত হিসাব | `M18` methodology | Value + method | Where claimed |
| Environmental declaration | পরিবেশগত ঘোষণা | Static approved text | Text | ✔ |
| Our authorised officer | আমাদের কর্মকর্তা | `employee.display_name` + designation | Text | ✔ |
| Partner authorised officer | অংশীদারের কর্মকর্তা | Partner signatory | Text | ✔ |

| # | Rule |
|---|---|
| **FM-35-a** | Transfer is blocked where the partner's registration is not current **at the transfer date** (`BRU-ESG-02`). The certificate prints the validity so a later reader can check it too |
| **FM-35-b** | Hazardous fractions are declared with their route (`BRU-ESG-04`). A battery going to general recycling is the single most common e-waste compliance failure |
| **FM-35-c** | Data-bearing assets require a `DT-034` reference (`BRU-ESG-01`). Without it the transfer is blocked |
| **FM-35-d** | Recovery figures state their basis. Where the partner supplies the figure, the certificate says so and names them — **we do not present a partner's estimate as our measurement** |
| **FM-35-e** | Any carbon or environmental claim states its methodology. An unqualified environmental figure republished in a client's ESG report becomes their exposure and, eventually, ours |
| **FM-35-f** | Weight is reconciled between dispatch (`DT-026`/`DT-027`) and partner receipt. An unexplained difference is an incident (`BRU-LOG-04` discipline) |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-ESG-01` | No device leaves for recycling without a certified wipe or destruction record |
| `BRU-ESG-02` | Partner certification must be current at the transfer date |
| `BRU-ESG-03` | **Every recycled unit** must have a retrievable disposal certificate |
| `BRU-ESG-04` | Hazardous items follow their specific handling, storage and transport rules without exception |
| `BRU-LOG-05` | Restricted items — lithium batteries in particular — only with a certified carrier |
| `BRU-TRF-01` | Trade-in devices require data destruction before any onward route |
| `BRU-INV-06` | Stock written off to e-waste follows the adjustment approval path (`DT-029`) |

### 5.1 Claims discipline

The certificate makes environmental claims. Claims attract scrutiny.

| # | Rule |
|---|---|
| **CL-35-a** | Every quantitative claim states whether it is measured, calculated or estimated, and by whom |
| **CL-35-b** | No claim is made that the partner's evidence does not support |
| **CL-35-c** | "Zero landfill", "100% recycled" and similar absolutes require evidence per batch, not a partner's general policy statement |
| **CL-35-d** | Methodology for any carbon or equivalent figure is stated or referenced |
| **CL-35-e** | A claim republished by a client in their own ESG report should be defensible **on our evidence alone**. That is the test applied before any figure prints |
| **CL-35-f** | Marketing must not restate these figures more strongly than the certificate does (`CG-013` escalation trigger) |

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Client batch certificate** | Corporate decommissioning | Per-asset schedule, ESG figures, `DT-034` linkage |
| **Internal batch** | Our own scrap and failed stock | No client; internal records and regulatory evidence only |
| **Single asset** | Consumer device, trade-in reject | Short form, still with route and recovery |
| **Hazardous-only** | Batteries, CRT, lamps | Handling route foremost; carrier certification referenced |
| **Take-back programme** | Where **G6 EW7** identifies an EPR obligation | Programme reference and reporting linkage |
| **Partner-issued** | Partner certifies to us | Attached as evidence; our certificate references it and does not restate its claims as ours |
| **Regulatory return extract** | DoE reporting per **G6 EW3** | Aggregated extract; not a client document |

---

## 7. Worked Example

> **Specimens follow G6 EW1 and EW5.**

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-035-S1` | Corporate batch, 120 assets | Per-asset schedule and ESG figures |
| `DT-035-S2` | Batch containing lithium batteries | `FM-35-b` hazardous routing |
| `DT-035-S3` | Data-bearing assets | `FM-35-c` `DT-034` linkage per asset |
| `DT-035-S4` | Recovery figures supplied by the partner | `FM-35-d` attribution |
| `DT-035-S5` | Weight discrepancy at partner receipt | `FM-35-f` incident |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Sustainability with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Quality | *pending* | | |
| Reviewer — Inventory | *pending* | | |
| Reviewer — Corporate Affairs (ESG claims) | *pending* | | |
| **G6 — Legal Counsel with an environmental adviser (EW1–EW8)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — COO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `EWC-{entity}-{yy}-{seq:06d}`, **`no_gaps`** |
| Archive format | **PDF/A-3 at issue** |
| Retention | Per the Rules — **pending G6 EW8**; not less than the tax retention and the client's audit window |
| Partner evidence | Partner certificates, weighbridge tickets and receipt confirmations archived with ours |
| Re-render | Prohibited |
| Reprint | Watermarked **COPY**, logged |
| Traceability | **Every unit is retrievable by serial to its certificate** (`BRU-ESG-03`). The index supporting this is a system obligation, not a filing habit |
| Regulatory returns | Where **G6 EW3** requires periodic returns, the extract and its submission evidence are archived with the period |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-034_Data_Destruction_Certificate.md`](DT-034_Data_Destruction_Certificate.md) | **Required before any data-bearing asset moves to disposal** |
| [`DT-036_Refurbishment_Grading_and_Certification_Record.md`](DT-036_Refurbishment_Grading_and_Certification_Record.md) | The alternative route — refurbish rather than dispose |
| [`../05C_Supply_Chain_and_Logistics/DT-026_Stock_Transfer_Note_and_Gate_Pass.md`](../05C_Supply_Chain_and_Logistics/DT-026_Stock_Transfer_Note_and_Gate_Pass.md) | Scrap leaving site |
| [`../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md`](../05C_Supply_Chain_and_Logistics/DT-027_Delivery_Challan_and_Logistics_Manifest.md) | Transport to the partner |
| [`../05C_Supply_Chain_and_Logistics/DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md`](../05C_Supply_Chain_and_Logistics/DT-029_Physical_Count_and_Stock_Adjustment_Sheet.md) | Stock written off to e-waste |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) | Materials, routes, partners and their registrations |
| `LG-018` E-Waste, EPR and Environmental Compliance Statements | The compliance position this evidences |
| [`SP-026_SOP_EWaste_Collection_and_Disposal.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-026_SOP_EWaste_Collection_and_Disposal.md) | The operational process |
| `RP-005` Dashboard Specification Pack — External Audiences | Where aggregate figures are reported |
| `LG-018` E-Waste, EPR and Environmental Compliance Statements | Where marketing restatement is controlled (`CL-35-f`) |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Two-audience design, per-asset traceability per `BRU-ESG-03`, hazardous-fraction itemisation, measured-versus-estimated disclosure, six claims-discipline rules, registration question raised as escalating G6 EW1 | COO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Per-asset traceability required, not batch weight alone (`L-35-a`)
- [x] Hazardous fractions itemised with routes
- [x] Measured/estimated basis disclosed on every figure (`L-35-d`, `CL-35-a`)
- [x] `DT-034` linkage enforced for data-bearing assets
- [x] All internal links resolve
- [ ] **G6 EW1 — our registration status under the 2021 Rules** — **outstanding; if registration is required and absent, escalate under `CG-013` immediately**
- [ ] G6 EW3–EW8 — records, transfer documentation, Schedule scope, hazardous obligations, EPR, retention — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] `MD-047` partner registrations and expiry dates populated — **outstanding, dependency for `BRU-ESG-02`**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
