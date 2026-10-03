---
id: RP-014
title: Export, Watermark and Confidentiality Marking Rules
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-20
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Security with BI
author: Security Lead with BI Lead and the Chief Data Officer
reviewers: [CTO, Chief Data Officer, Legal Counsel, CFO delegate, HR Manager, Quality Manager, Content Design Lead]
approver: CTO with Chief Data Officer
content_class: D
purpose: >
  How exported data is classified, marked, watermarked and redacted, and which roles may export what.
  Every dashboard export leaves the controlled environment permanently: row-level security, field
  permissions and audit logging all stop at the moment a file lands in a downloads folder, and from
  then on marking is the only control that travels with the data. An unmarked spreadsheet of branch
  margin forwarded to a competitor is indistinguishable from a public document.
traces_to: [05-02, 05-02 §10, 05-04, 05-04 §5, 05-04 §8, 05-06 §4, 05-06 §6.3, 05-06 NFR-088, 05-06 NFR-095, M24, M29, M62, M62 §9, P06, RP-002, RP-003, RP-004, RP-005, RP-006, RP-010, RP-013, VB-004, LG-001, TS-017, CG-013]
priority: P2
wave: W4
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md §10 Data Classification — four classes S0 Public, S1 Internal, S2 Confidential, S3 Restricted with their controls; and the S3 field inventory of nine field groups with their additional controls
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/P06_Analytics_and_Executive_Dashboard.md §9 PRU-P06-11 — every export is logged with user, view, row count and timestamp; §11 AUT-P06-07 an export exceeding the configured row threshold requires justification, is logged and notifies the data owner, blocking pending justification
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §5 field-level permissions with thirteen field groups; §8 EA-12 bulk export by external parties is limited, rate-controlled and logged
    verified: 2026-08-20
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §4 NFR-011 field-level RBAC, NFR-014 immutable audit trail, NFR-061 field-level encryption for S3 with separate key material; §6.3 NFR-099 restrict large-scale transfer of Sensitive Personally Identifiable Data and disclose safeguards; NFR-088 records retention, NFR-095 processing records five years
    verified: 2026-08-20
    class: P1
supersedes: none
review_due: 2027-02-20
---

# Export, Watermark and Confidentiality Marking Rules

| Item | Value |
|---|---|
| Classification source | **`05-02` §10** — `S0` Public · `S1` Internal · `S2` Confidential · `S3` Restricted |
| `S3` exports | **Prohibited** (`WM-04`) |
| Every export logged | User, view, row count, timestamp — `PRU-P06-11` |
| Watermarking | `S2` and above, per-recipient (§4.4) |
| Wave | W4 · `P2` |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3) with the
> `RP` table addition applied as the marking matrix in §4.3. All six sections retained in order.

---

## 1. Purpose

The register states the position exactly: *"every dashboard export leaves the controlled environment;
marking is the only remaining control."*

Inside the platform, four controls operate: row-level security (`BRU-DAT-12`), field-level restriction
(`PRU-P06-04`), audit logging (`NFR-014`) and session policy (`NFR-069`). **All four stop at the
download.** What survives is whatever is written on the file, plus the log entry recording that it
left — and the log entry is retrospective.

Two obligations make this more than good practice. `NFR-099` restricts large-scale transfer of
Sensitive Personally Identifiable Data and requires disclosed safeguards; `NFR-095` requires processing
records retained for five years. **An export is processing, and an unrecorded export of personal data is
a gap in a statutory record**, not merely a governance lapse.

**What stops working without this file:**

| Absent | Consequence |
|---|---|
| Marking rules | An `S2` export is indistinguishable from an `S0` one, and the recipient treats it accordingly |
| Watermarking | A leaked export cannot be traced to the person who took it, so there is no deterrent and no investigation |
| Export permission by role | Every role that can see data can extract it in bulk |
| Redaction rules | A view a role may see in aggregate is exported at row level with fields they may not see individually |
| A row threshold | Bulk extraction is indistinguishable from normal use |
| A prohibition on `S3` | The nine `05-02` §10 `S3` field groups leave the platform in a spreadsheet |

---

## 2. Scope

**In scope.** Classification of exported artefacts; marking and watermarking; export permission by
role and by classification; row thresholds and justification; redaction; format rules; logging;
retention of the export record; and the external-party export regime.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| Field classification itself | **`05-02` §10** — this file applies it and defines nothing new |
| Field-level permissions | `05-04` §5 |
| Row-level security | `RP-006`, `M62` `BRU-DAT-12` |
| Print and PDF brand layout | **`VB-004`** — this file specifies the marking; `VB-004` specifies the page |
| Document templates given to customers | Category 05 `DT` — an invoice is issued, not exported |
| Statutory filings | `RP-009` — a filing is submitted under `ST-08`, not exported |
| Subscription delivery | `RP-013` — which applies this file's marking (`SB-06`) |
| Retention of the underlying record | `M24`, `NFR-088` |
| The proof that export controls hold | **`TS-017`** Block E and Block I |
| Data-loss prevention tooling and endpoint control | `M29`; §4.8 states the boundary |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Security Lead** (accountable with BI) | The export control regime |
| **Chief Data Officer** (approver) | `S3` prohibition, `NFR-099` and the processing record |
| **BI Lead** | Implementation in `P06` and the portals |
| **Every exporting role** | What they may export and how it will be marked |
| **Legal Counsel** | The evidentiary value of a watermark in a dispute |
| **QA** (`TS-017`) | The controls the tests verify |

---

## 4. Content

### 4.1 Rules

| # | Rule |
|---|---|
| **WM-01** | **Classification is inherited from the data, not chosen by the exporter.** An export carries the **highest** classification of any field in it (`05-02` §10) |
| **WM-02** | **Every export is marked**, in every format, including CSV (§4.5) |
| **WM-03** | **`S2` and above carry a per-recipient watermark** identifying who exported it and when (§4.4) |
| **WM-04** | **`S3` data is never exported**, in any format, by any role, from any surface. `BRU-DAT-11` already excludes it from the analytical estate; this closes the transactional route |
| **WM-05** | **Every export is logged with user, view, row count and timestamp** (`PRU-P06-11`), and the log is retained as a **processing record** for five years (`NFR-095`) |
| **WM-06** | **An export above the row threshold requires justification before it proceeds** (`AUT-P06-07`), and the data owner is notified |
| **WM-07** | **Export permission is a separate grant from view permission.** A role that may see a view does not automatically may export it (§4.6) |
| **WM-08** | **Redaction on export follows `05-04` §5 field permissions exactly.** A field a role may not see is absent from their export, not masked — consistent with `PRU-P06-04` |
| **WM-09** | **An aggregate a role may see does not entitle them to its rows.** Export at a grain finer than the role's view grain is refused |
| **WM-10** | **External-party exports are limited, rate-controlled and logged** (`EA-12`), and carry the external marking in §4.4 |
| **WM-11** | **A watermark is not a security control**; it is a deterrent and an investigative aid. Stated so it is not relied on as prevention (§4.8) |
| **WM-12** | **Marking is applied by the platform, never by the exporter.** A manual marking step is not a control |
| **WM-13** | **An export of personal data is a processing event** with a lawful basis (`NFR-090`), and bulk export of personal data requires approval (`BRU-SEC-05`) |
| **WM-14** | **Large-scale transfer of Sensitive Personally Identifiable Data is restricted and its safeguards disclosed** (`NFR-099`); cross-border transfer requires an Authority notification record before it executes (`NFR-086b`) |
| **WM-15** | **Every export format is treated equally.** A screenshot is an export of the pixels but not of the data; a copy-paste is an export the platform cannot see — §4.8 records both honestly |

### 4.2 Classification of an export

`WM-01`. The classification is derived, not declared.

| Export contains | Class | Basis |
|---|:--:|---|
| Service catalogue, branch directory, published prices | `S0` | `05-02` §10 |
| Operational data — orders, stock, schedules, queues | `S1` | `05-02` §10 |
| **Customer contact, pricing, margin, aggregate salary, branch financials, league detail** | **`S2`** | `05-02` §10 |
| **NID, bank details, individual payroll, recovered-data index, call recordings, biometric templates, seller KYC, identity documents, integration credentials** | **`S3` — export prohibited** | `05-02` §10 `S3` inventory, nine field groups (`WM-04`) |

**Most analytic exports will be `S2`**, because margin, pricing and branch financials appear across
`RP-003` and `RP-004`, and `05-02` §10 classifies them `S2`. Treating an analytic export as `S1` by
default is the commonest misclassification, and `WM-01`'s highest-field rule prevents it.

### 4.3 The marking matrix

| Class | Header marking | Footer marking | Watermark | Row threshold |
|:--:|---|---|---|---:|
| `S0` | *"1000FiX Services Limited — Public"* | Generated timestamp, source view | None | — |
| `S1` | *"CONFIDENTIAL — Internal Use Only"* | Timestamp, source view, exporter | None | 5,000 |
| `S2` | *"CONFIDENTIAL — Restricted Distribution"* | Timestamp, source view, exporter, **scope rendered** | **Per-recipient, §4.4** | **1,000** |
| `S3` | — | — | — | **Export prohibited** |

**Every marking carries four elements** for `S1` and above: the classification, the generation
timestamp, the source view, and the exporter's identity. **`S2` adds the scope the export was rendered
under**, so a recipient can see whether they are holding one branch or the network — which is the
single most useful line on a forwarded spreadsheet.

### 4.4 Watermarking

| Element | Rule |
|---|---|
| Applies to | `S2` and above (`WM-03`) |
| Content | Exporter's name, role, timestamp, and an export reference tying to the `WM-05` log entry |
| PDF | Diagonal repeating watermark at low opacity, **plus** the header and footer marking; must not obscure data (`VB-004` layout) |
| Excel | Header rows, a footer on every printed page, **and** document properties; a hidden sheet carrying the export reference |
| CSV | **A leading comment block and a trailing marker row** (§4.5) |
| Screen | Not applicable — but `PRU-P06-11` logs the view |
| Per-recipient | A scheduled `S2` delivery to 51+ branch managers carries **51+ distinct watermarks**, one per recipient (`RP-013` `SB-01`) |
| Removal | **Trivially possible, and that is accepted** (`WM-11`) |

> **Per-recipient watermarking is what makes a leak traceable.** `RP-013` `SUB-01` renders once per
> branch manager; identical files would make a leaked copy untraceable to one of 51 people, and a
> watermark naming the recipient makes it traceable to one.

### 4.5 Format rules, including the CSV problem

| Format | Marking method | Note |
|---|---|---|
| **PDF** | Header, footer, diagonal watermark, document properties | The only format where marking is genuinely robust; **preferred for `S2`** |
| **Excel** | Header rows, print footer, document properties, hidden reference sheet | Marking survives most handling; a paste into a new workbook loses it |
| **CSV** | Leading `#`-prefixed comment block and a trailing marker row | **CSV has no metadata**, so marking is data. It breaks naïve parsers, which is a real cost |
| **Screenshot** | Not markable | `WM-15`; the view is logged, the pixels are not controlled |
| **Copy-paste** | Not markable and **not detectable** | `WM-15`; stated rather than pretended otherwise |

> **The CSV problem is genuine and this file does not pretend otherwise.** A comment block is either
> stripped by the consuming tool — losing the marking — or it breaks the parse. **The resolution is to
> restrict `S2` CSV export to roles with a stated analytical need** (§4.6) and to prefer Excel or PDF
> otherwise. Recorded as `O-03` rather than resolved by asserting that CSV marking works.

### 4.6 Export permission by role

`WM-07`: a separate grant. Derived from `05-04` §5 field access and `05-04` §2 portal access.

| Role group | May export | Max class | Row limit |
|---|---|:--:|---:|
| `R01`–`R05` executive | Any view within scope | `S2` | 5,000 |
| `R06` branch manager | Own branch, own league detail | `S2` | 1,000 |
| `R26`, `R27`, `R03` finance | Financial views within scope | `S2` | 5,000 |
| `R17`, `R19` supply chain | Stock, vendor, procurement | `S2` | 5,000 |
| `R28` warranty | Claims and evidence packs | `S2` | 1,000 |
| `R30`, `R31` HR | HR views — **excluding individual pay** (`S3`) | `S2` | 1,000 |
| `R32` quality | Quality views, audit evidence | `S2` | 1,000 |
| `R33` IT admin | Operational and platform views; **not business data** | `S1` | 5,000 |
| `R08`, `R09`, `R18`, `R29` operational | **In-product views only — no export** | — | 0 |
| `R10`–`R12`, `R16` field | **No export** | — | 0 |
| `R34`, `R35` contact centre | **No export** | — | 0 |
| **`R36`, `R37`, `R38` external** | Own-scope views only, per `RP-005` | `S2` own data | **500**, rate-limited (`EA-12`) |

**Operational and field roles have no export permission, and that is deliberate.** `R08` is 150–250
people who need to *act* on data, not extract it; `R10`–`R12` are 215–430 people on personal devices.
`NFR-077`'s four-click access and `RP-004`'s actionable counts are the alternative — **an export
requirement from an operational role usually indicates a missing panel** (`O-05`).

### 4.7 Thresholds, justification and bulk export

| Trigger | Action |
|---|---|
| Export within the role's row limit | Proceeds; logged (`WM-05`) |
| **Above the limit** | **Blocked pending justification**; the data owner is notified (`AUT-P06-07`, `WM-06`) |
| **Any bulk export of personal data** | Requires approval and is logged (`BRU-SEC-05`); step-up authentication applies (`BRU-SEC-02`) |
| **Large-scale transfer of Sensitive PII** | Restricted; safeguards disclosed (`NFR-099`); **cross-border requires an Authority notification record before execution** (`NFR-086b`) |
| Repeated at-limit exports by one user | Reviewed as a pattern, not per event — the signal of an undeclared extraction routine |
| External party above their limit | Rate-limited and logged (`EA-12`); no justification path — **they use the portal** |

### 4.8 What marking does not do — stated plainly

`WM-11` and `WM-15` exist so that marking is not mistaken for prevention.

| Marking does not | Consequence |
|---|---|
| Prevent removal | A watermark is croppable, a header deletable, a CSV comment strippable |
| Prevent copy-paste | Undetectable by the platform |
| Prevent a photograph of the screen | Not markable |
| Prevent onward forwarding | Once exported, distribution is outside every control |
| Substitute for endpoint DLP | **`M29` owns endpoint and DLP controls; this file does not** |

**What marking does do:** it removes the excuse. A recipient of a marked `S2` file cannot claim they did
not know its status, and a watermarked file ties a leak to a person — which is the deterrent and the
investigative route. `CG-013` escalation applies where an export appears outside its intended
distribution.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| **`05-02` §10** | The four classes and the nine `S3` field groups |
| **`05-04` §5, §2, §8** | Field permissions for `WM-08`, portal access for §4.6, `EA-12` for external |
| `M62` `BRU-DAT-11`, `BRU-DAT-12` | `S3` exclusion and query-engine scope |
| `P06` `PRU-P06-04`, `PRU-P06-11`, `AUT-P06-07` | Column exclusion, export logging, row threshold |
| `M29` | Step-up authentication, endpoint controls, DLP (§4.8) |
| `M24`, `NFR-088`, `NFR-095` | Retention of the export record as a processing record |
| `NFR-099`, `NFR-086b` | Sensitive PII transfer and cross-border notification |
| **`VB-004`** | Print and PDF layout the marking sits within |
| [`RP-002`](RP-002_Report_Catalogue_by_Role_and_Module.md), `RP-003`, `RP-004`, `RP-005`, `RP-010`, `RP-013` | The surfaces and deliveries this file marks |
| **[`TS-017`](../13_Test_and_Acceptance_Content/TS-017_Security_and_Privacy_Test_Case_Pack.md)** | Where export control is verified |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Annually; and on any change to `05-02` §10 or `05-04` §5 |
| Trigger for out-of-cycle review | A new `S3` field; a leak or suspected leak; a row-limit dispute; a new export format; a PDPA guidance change |
| Owner | Security Lead with BI Lead; Chief Data Officer approves |
| Data file | `RP-014_Marking_Matrix.csv` · `RP-014_Export_Permissions.csv` · `RP-014_Export_Log_Schema.csv` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`WM-04` prohibits `S3` export and nothing enforces it at the transactional surfaces.** `BRU-DAT-11` excludes `S3` from the **analytical** estate, so `P06` is covered; **`P03` shows `nid_number` to `R26`, `R27`, `R30`, `R31` and `R33` under `05-04` §5, and a list view with an export button is the uncontrolled route.** This is the gap between the analytical and transactional export paths | Security Lead with `M29` owner | **W4 — before any export button ships** |
| **O-02** | **Export permission as a separate grant (`WM-07`) does not exist in `05-04`.** The matrix has portal access, module CRUD and field permissions; **there is no export right.** §4.6 proposes one derived from the others, and it needs registering in `05-04` or it will be implemented as "can see, can export" | Enterprise Architecture with Security Lead | **W4 — a `05-04` addition** |
| **O-03** | **CSV marking is unreliable and §4.5 says so.** A comment block is stripped or breaks the parse. **The proposal — restrict `S2` CSV to stated analytical need, prefer Excel or PDF — narrows a capability `04-00` offers** (*"export to PDF, Excel and CSV"*) and needs agreement | Chief Data Officer with BI Lead | **W4** |
| **O-04** | **`WM-05` requires the export log retained as a processing record for five years (`NFR-095`), and no retention is configured for it.** `TS-001` `O-06` records the same unratified retention question for test evidence. **An export log is the evidence that a PDPA subject-access response is complete**, so its retention is not a housekeeping matter | Chief Data Officer with Quality Manager | **W4** |
| **O-05** | **Operational and field roles have no export permission (§4.6), and that will generate requests.** The intended answer is that an export need indicates a missing `RP-004` panel. **Nothing routes such a request to `RP-004` rather than to an export grant**, and the path of least resistance is to grant the export | BI Lead with Operations Director | W4 |
| **O-06** | **`NFR-086b` requires an Authority notification record before a cross-border transfer executes, and the split-residency legal opinion is overdue** (`DEP-31`/`D-13`; `TS-017` `O-04`, `RP-006` `O-05`). **Whether an `S2` export sent to a group address outside Bangladesh is a cross-border transfer of residency-classified data is exactly the unanswered question** | CTO with Legal Counsel | **W4 — `DEP-31` overdue** |
| **O-07** | **`WM-12` requires platform-applied marking, and neither Metabase nor Grafana applies it natively.** `RP-007` `O-05` records the same enforcement gap for chart standards. **Marking applied by convention is `WM-12`'s prohibited manual step in a different form** | Platform Engineering with BI Lead | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to template 1 with the `RP` table addition applied as the marking matrix
- [x] **The four in-platform controls named, and the fact that all four stop at the download stated as the file's premise**
- [x] Fifteen rules stated, including classification-inherited-not-chosen and `S3`-never-exported
- [x] Classification derived from `05-02` §10 with the `S2`-by-default point made for analytic exports
- [x] Marking matrix with four elements for `S1`+ and scope-rendered added at `S2`
- [x] **Per-recipient watermarking specified, and why it makes a 51-recipient leak traceable**
- [x] Format rules per format, **with the CSV marking problem stated honestly rather than asserted solved**
- [x] Export permission by role group, with operational and field roles at zero and the reason
- [x] Thresholds, justification, bulk-export approval and the Sensitive PII regime
- [x] **§4.8 states plainly what marking does not do, so it is not mistaken for prevention**
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **`O-01` transactional `S3` export route unenforced — outstanding**
- [ ] **`O-02` no export right exists in `05-04` — outstanding; will default to can-see-can-export**
- [ ] **`O-07` neither tool applies marking natively — outstanding; `WM-12` unenforceable**
- [ ] Named approvers recorded — **pending CTO and Chief Data Officer**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
