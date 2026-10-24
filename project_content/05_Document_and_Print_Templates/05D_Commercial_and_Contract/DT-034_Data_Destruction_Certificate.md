---
id: DT-034
title: Data Destruction Certificate
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Data Services with Legal & Compliance
author: Data Services with Legal & Compliance, Security and Content Design
reviewers: [Legal Counsel, Chief Technology Officer, Quality, Internal Audit, Localisation Lead]
approver: Chief Technology Officer with Legal Counsel
content_class: A
statutory_tier: S
statutory_pin: FY2026-27
purpose: >
  Device identity, destruction method, standard applied, operator, witness, date and certificate
  number. Corporate and government clients require destruction certificates for audit and
  regulatory purposes, and both P01 and P04 promise the customer can download one. It is also the
  document that proves we discharged a data-protection obligation on somebody else's personal data.
traces_to: [M06, M14, M18, P01, P04, DT-001, DT-009, DT-035, DT-036, DT-038, LG-008, LG-009, MD-021, MD-040, MD-047, BRU-ESG-01, BRU-TRF-01, BRU-SEC-03, BRU-SEC-04, 05-06 NFR-086]
priority: P1
wave: W2
bilingual: yes
bn_counterpart: DT-034_Data_Destruction_Certificate_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-ESG-01 — no device may leave for recycling without a certified wipe or physical destruction record
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-TRF-01 — no trade-in device proceeds to refurbishment or resale without a certified data destruction record
    verified: 2026-08-15
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 NFR-086 — data-protection regime obligations referenced by the programme
    verified: 2026-08-15
    class: P1
  - source: NIST SP 800-88 Rev.1 Guidelines for Media Sanitization — clear, purge and destroy categories with method-per-media guidance. **Adoption as our reference standard is a decision pending at G6**
    verified: 2026-08-15
    class: P2
supersedes: none
review_due: 2027-02-15
---

# DT-034 — Data Destruction Certificate

> ⚠ **Tier S — statutory and contractual. Gate G6 mandatory and unwaivable (`WV-02`).**
>
> **This certificate is an assertion about something that cannot be seen.** A customer cannot
> verify that data was destroyed; they can only rely on the document. That makes every element of
> it — method, standard, operator, witness, verification — a control, and a certificate issued
> without those controls actually operating is a false statement, not a formality.
>
> **`BRU-ESG-01` and `BRU-TRF-01`: no device goes to recycling, refurbishment or resale without
> one.** Those two rules are what make this document unavoidable rather than optional.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | **Data destruction / media sanitisation certificate** |
| Owning module | `M06` Data Services and Secure Data Handling |
| Statutory | **Yes — Tier S.** Data-protection discharge; contractual and audit requirement |
| Recipient(s) | Customer (corporate and consumer), auditors, regulators on request, internal records |
| Languages | **Bilingual — parallel columns for the declaration** |
| Output formats | A4 portrait · PDF for portal download (`P01`, `P04`) · **PDF/A-3 archive at issue** |
| Numbering mask | `MD-040` — `DDC-{entity}-{yy}-{seq:06d}`, **`no_gaps`** |
| Retention period | **Long.** `LG-009`; not less than the customer contract's audit window and the tax retention |
| Fiscal pin | **FY2026-27** — pinned because the standard applied is version-dated |

### 1.1 When one is issued

| Trigger | Rule | Certificate to |
|---|---|---|
| Trade-in accepted | `BRU-TRF-01` | Customer, before refurbishment proceeds |
| Device to e-waste | `BRU-ESG-01` | Customer where identified; internal record otherwise |
| Corporate decommissioning engagement | `M06`, contract | Customer, per asset |
| Customer requests destruction as a service | `M06` | Customer |
| Data-recovery case closed and data purged | `BRU-SEC-04` | Customer, as purge evidence |
| Repair requiring board or storage replacement | Where the removed media leaves our custody | Customer |
| Device abandoned and disposed of | `DT-009` §6.1, `UC-03` | Internal record; customer where contactable |

---

## 2. Statutory Requirements

| Mandated element | Source | Verified | Where it appears |
|---|---|---|---|
| Evidence of personal-data erasure | Data-protection regime, `05-06` NFR-086; `LG-008` — **pending G6** | pending | Whole document |
| Identity of the data controller and processor | Data-protection regime — **pending G6** | pending | Party block |
| Description of the media and data destroyed | Contractual; audit | 2026-08-15 | Device block |
| Method and standard applied | NIST SP 800-88 or equivalent — **adoption pending G6** | pending | Method block |
| Date, operator and witness | Audit practice | 2026-08-15 | Signature zone |
| Verification of destruction | NIST SP 800-88 §4.7 verification — **pending G6** | pending | Verification block |

### 2.1 G6 questions

| # | Question |
|---|---|
| **DD1** | What does the Bangladeshi data-protection regime require of an erasure record, and for how long must it be kept? |
| **DD2** | Do we adopt NIST SP 800-88 Rev.1 as our reference standard, or another? The certificate must name a standard, and it must be one we can actually meet |
| **DD3** | Are there sector-specific requirements — financial, healthcare, government — for clients in those sectors? |
| **DD4** | Where a customer's device is destroyed by a sub-contracted partner, who certifies, and what is our residual liability? |
| **DD5** | What is required where destruction fails or is incomplete — for example, a drive that cannot be wiped or physically destroyed on site? |
| **DD6** | Is a certificate required for a device we cannot access (locked, dead) and therefore cannot verify? |

> **DD6 is the honest question.** A dead or locked device cannot be wiped. What we can certify is
> physical destruction. The certificate must not claim erasure it did not perform — §5.2 states
> the position taken until G6 answers.

---

## 3. Layout

| Zone | Content | Bilingual |
|---|---|---|
| Header | **DATA DESTRUCTION CERTIFICATE**, certificate number, issue date | Title stacked |
| Party block | Customer (data controller) left; 1000FiX (processor), engagement and case reference right | Labels stacked |
| Body | Device and media identity → method → standard → verification → chain of custody | Labels stacked |
| Totals | Where a batch: device count, media count, by method | Arabic numerals |
| Statutory block | **The destruction declaration** and the data-protection statement | **Parallel columns** |
| Signature | **Operator and witness**, both named with employee IDs | Labels stacked |
| Footer | Certificate reference, `page n of m`, verification URL / QR | English |
| Machine-readable | QR: certificate reference resolving to a verification page (`DT-044`) | — |

| # | Rule |
|---|---|
| **L-34-a** | **Operator and witness are two different named people**, both with employee IDs. A single-signature destruction certificate is an assertion by one person about an unobservable act |
| **L-34-b** | The method and the standard print together. "Securely wiped" without a named method and standard means nothing to an auditor |
| **L-34-c** | The verification result prints — how destruction was confirmed, and by whom |
| **L-34-d** | The declaration never splits across a page |
| **L-34-e** | The QR resolves to a **verification page** where the certificate's authenticity can be confirmed. Certificates are forged; a verifiable one is worth more |
| **L-34-f** | Batch certificates list every device by serial. **A batch certificate with a count but no serials certifies nothing about any particular device** |

---

## 4. Field Mapping

### 4.1 Parties and engagement

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Certificate no. | সনদ নং | `MD-040` sequence | Monospace | ✔ |
| Issue date | ইস্যুর তারিখ | `ddc.issued_at` | `DD/MM/YYYY` | ✔ |
| Customer / data controller | গ্রাহক / ডেটা নিয়ন্ত্রক | `party` / `MD-015` | Text | ✔ |
| Customer reference | গ্রাহক সূত্র | `party.po_ref` / contract | Monospace | Corporate |
| Processor | প্রক্রিয়াকারী | `MD-002.entity_legal_name` | Text | ✔ |
| Engagement / case reference | কেস সূত্র | `M06.case_ref` | Monospace | ✔ |
| Service order reference | সার্ভিস অর্ডার | `service_order.order_ref` | Monospace | Where applicable |

### 4.2 Media and method

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Device make / model | ডিভাইস | `MD-021` | Text | ✔ |
| **Device serial / IMEI** | সিরিয়াল | `device.serial_no` | Monospace | ✔ |
| Asset tag | অ্যাসেট ট্যাগ | `device.asset_tag` | Monospace | Corporate |
| Media type | মিডিয়ার ধরন | `ddc.media_type` | Enum: HDD / SSD / eMMC / NVMe / flash / optical / tape / mobile storage | ✔ |
| Media serial | মিডিয়া সিরিয়াল | `ddc.media_serial` | Monospace | ✔ where separable |
| Media capacity | ধারণক্ষমতা | `ddc.media_capacity` | GB / TB | ✔ |
| **Destruction method** | ধ্বংসের পদ্ধতি | `ddc.method` | Enum: overwrite / cryptographic erase / secure erase command / degauss / shred / disintegrate | ✔ |
| **Standard applied** | প্রযোজ্য মান | Per **G6 DD2** | Text + version | ✔ |
| Sanitisation category | শ্রেণি | Enum: clear / purge / destroy | ✔ per the standard |
| Software / equipment used | ব্যবহৃত সফটওয়্যার / যন্ত্র | `MD-046` / tool + version | Text | ✔ |
| Passes / parameters | প্যারামিটার | `ddc.parameters` | Text | Where the method has them |
| Start / end time | শুরু / শেষ | `ddc.started_at`, `.completed_at` | `DD/MM/YYYY HH:mm` | ✔ |
| **Verification method** | যাচাইয়ের পদ্ধতি | `ddc.verification_method` | Enum: tool report / sampled read-back / visual (physical) | ✔ |
| **Verification result** | যাচাইয়ের ফলাফল | `ddc.verification_result` | Enum: verified / partial / failed | ✔ |
| Tool report reference | টুল রিপোর্ট | `M24` reference | Monospace | ✔ where a tool report exists |
| Photographic evidence | ছবির প্রমাণ | `M24` count | Integer | ✔ **for physical destruction** |

### 4.3 Custody, people and declaration

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Received from | গ্রহণ করা হয়েছে | `DT-002` / `DT-027` reference | Monospace | ✔ |
| Custody chain | হেফাজতের ধারা | Custody event list | Table | ✔ |
| Location of destruction | ধ্বংসের স্থান | `MD-003` / `MD-004` / partner site | Text | ✔ |
| Sub-contracted to | উপ-ঠিকাদার | `MD-016` partner + certification | Text | ✔ where applicable |
| **Operator** | পরিচালনাকারী | `employee.display_name` + ID | Text | ✔ |
| **Witness** | সাক্ষী | `employee.display_name` + ID | Text | ✔ **different person (`L-34-a`)** |
| Declaration | ঘোষণা | Static approved text | Text | ✔ |
| Data-protection statement | ডেটা সুরক্ষা বিবৃতি | `LG-008` derived | Text | ✔ |
| Onward disposition | পরবর্তী গতি | Enum: returned to customer / refurbishment / e-waste / retained | ✔ |
| Related certificate | সম্পর্কিত সনদ | `DT-035` / `DT-036` / `DT-038` | Monospace | Where applicable |

| # | Rule |
|---|---|
| **FM-34-a** | The method must be **appropriate to the media type**. An overwrite pass on an SSD does not sanitise it; the system rejects a method/media combination the standard does not endorse |
| **FM-34-b** | Verification result `partial` or `failed` **cannot produce a certificate of destruction**. It produces an exception and the `DD5` path |
| **FM-34-c** | Operator ≠ witness, enforced by identity (`BRU-SEC-07` discipline) |
| **FM-34-d** | Physical destruction requires photographic evidence — media before, and the destroyed remains after |
| **FM-34-e** | Where destruction is sub-contracted, the partner's certification is checked as current at the destruction date (`BRU-ESG-02` discipline) and the partner's own certificate is attached. **Our certificate never asserts something we did not witness** |
| **FM-34-f** | Access to the case is restricted and every access logged (`BRU-SEC-03`) |
| **FM-34-g** | The certificate is issued for **the media**, and lists the device it came from. Where media are removed and pooled before destruction, the chain is recorded per media serial, not per device |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-ESG-01` | No device to recycling without a certified wipe or destruction record |
| `BRU-TRF-01` | No trade-in device to refurbishment or resale without one |
| `BRU-SEC-03` | Data-case access restricted to the assigned team; every access logged |
| `BRU-SEC-04` | Recovered customer data purged at the agreed date unless a documented hold applies |
| `BRU-AIM-03` | Recovered customer data is never used as training data |
| `BRU-SRM-20` | Access notes purged at handover; the purge is separately confirmed on `DT-009` |
| `BRU-DMS-02` | A legal hold overrides scheduled destruction |

### 5.1 A certificate is not a formality

| # | Rule |
|---|---|
| **DC-34-a** | The certificate is generated **from the destruction record**, which is created by the tool or the witnessed physical process — never typed after the fact |
| **DC-34-b** | A certificate cannot be issued for a device with no recorded custody arrival. We cannot destroy what we cannot show we received |
| **DC-34-c** | Certificate issue is a **`no_gaps` statutory sequence**. A gap invites the question of what was destroyed and not certified |
| **DC-34-d** | Certificates are reconciled monthly against devices dispositioned to refurbishment, resale and e-waste. **Any disposition without a certificate is an incident** |
| **DC-34-e** | Forgery resistance: the QR verification page (`L-34-e`), the gap-free sequence and the two-person signature together make a fabricated certificate detectable |

### 5.2 Where destruction cannot be completed — the position until G6 DD5/DD6

| Situation | What we certify |
|---|---|
| Device is dead or locked; media accessible | Media removed and physically destroyed. **Certificate states physical destruction, not erasure** |
| Media is physically destroyed on site | Physical destruction, with photographic evidence |
| Media cannot be removed or destroyed on site | **No certificate.** An exception is raised and the customer is told, with options |
| Erasure tool reports failure | **No certificate.** Escalate to physical destruction or return to the customer |
| Device leaves for a partner to destroy | Certificate issued **only** on receipt of the partner's evidence, and it names the partner |

> **We never certify erasure we did not perform or verify.** That principle survives whatever G6
> answers, because it is not a legal question.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Single device** | Consumer trade-in, individual service | The base certificate |
| **Batch / schedule** | Corporate decommissioning | One certificate with a per-serial schedule (`L-34-f`) |
| **Physical destruction** | Shred, disintegrate, degauss | Photographic evidence mandatory; no tool report |
| **Cryptographic erase** | Self-encrypting media | Key destruction evidence; states that recovery depends on the key being unrecoverable |
| **Sub-contracted** | Partner performs destruction | Partner certificate attached; our certificate states what we witnessed (`FM-34-e`) |
| **Data-recovery purge** | `M06` case closure (`BRU-SEC-04`) | Certifies purge of recovered data from our systems, not of the customer's device |
| **Abandoned device** | `DT-009` §6.1 disposal | Internal record; customer copy where contactable |
| **Government / regulated sector** | Per **G6 DD3** | Sector-specific standard and additional attestation |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-034-S1` | Single SSD, cryptographic erase, verified | Base bilingual certificate |
| `DT-034-S2` | Corporate batch, 84 devices | `L-34-f` per-serial schedule |
| `DT-034-S3` | Locked device, media physically destroyed | §5.2 accurate claim |
| `DT-034-S4` | Erasure failed, no certificate issued | `FM-34-b` exception path |
| `DT-034-S5` | Sub-contracted destruction | `FM-34-e` partner evidence |
| `DT-034-S6` | QR verification page | `L-34-e` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Data Services with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Chief Technology Officer | *pending* | | |
| Reviewer — Quality | *pending* | | |
| Reviewer — Internal Audit | *pending* | | |
| **G6 — Legal Counsel and, where applicable, a security assessor (DD1–DD6)** | *pending* | | **Unwaivable (`WV-02`)** |
| Approver — CTO with Legal Counsel | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `DDC-{entity}-{yy}-{seq:06d}`, **`no_gaps`** (`DC-34-c`) |
| Archive format | **PDF/A-3 at issue** |
| Retention | `LG-009`; **not less than the customer contract's audit window and the tax retention** — a corporate client may audit years later |
| Evidence | Tool reports and photographs retained in `M24` with the certificate's retention |
| Re-render | **Prohibited.** The certificate asserts facts as at destruction |
| Reprint | Watermarked **COPY**, logged; the verification page always resolves to the original |
| Verification page | Maintained for the full retention period. **A verification URL that stops resolving destroys the value of every certificate that carries it** |
| Reconciliation | Monthly against dispositions (`DC-34-d`) |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md`](DT-035_EWaste_Disposal_and_Material_Recovery_Certificate.md) | Devices going to e-waste require both |
| [`DT-036_Refurbishment_Grading_and_Certification_Record.md`](DT-036_Refurbishment_Grading_and_Certification_Record.md) | Refurbishment cannot proceed without this certificate (`BRU-TRF-01`) |
| [`DT-038_TradeIn_Offer_and_Acceptance_Record.md`](DT-038_TradeIn_Offer_and_Acceptance_Record.md) | Trade-in data-erasure confirmation |
| [`../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md`](../05A_Service_and_Operations/DT-009_Device_Release_and_Collection_Receipt.md) | `UC-03` — abandoned data-bearing devices |
| [`../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md`](../05A_Service_and_Operations/DT-002_Service_Intake_Receipt_and_Device_Handover_Form.md) | Custody arrival (`DC-34-b`) |
| [`../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md`](../../02_Master_Data_and_Configuration/02F_Workforce_and_Asset/MD-047_EWaste_Material_and_Disposal_Route_Register.md) | Disposal routes and partners |
| `LG-008` Privacy Notice and Consent Copy | The data-protection statement |
| `LG-009` Data Retention and Deletion Schedule | Retention |
| `LG-017` Data Recovery and Secure Destruction Terms | Operator procedures |
| [`SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-012_SOP_Data_Recovery_and_Secure_Data_Handling.md) | The witnessed process |
| `TR-009` Course Pack — Field Technician | Operator certification |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Seven issue triggers, method-appropriate-to-media rule, mandatory two-person operator/witness, verification result gating issue, QR verification page, and the §5.2 never-certify-what-we-did-not-do position | CTO with Legal Counsel (pending) |

---

## Definition of Done

- [x] Front matter complete, including `statutory_tier:` and `statutory_pin:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Two-person operator/witness rule stated and enforced
- [x] Method-to-media appropriateness enforced (`FM-34-a`)
- [x] Failed or partial verification cannot produce a certificate (`FM-34-b`)
- [x] The never-certify-what-we-did-not-perform position stated (§5.2)
- [x] Verification page and gap-free sequence specified as anti-forgery controls
- [x] All internal links resolve
- [ ] **G6 DD1 — data-protection erasure-record requirements and retention** — **outstanding, unwaivable (`WV-02`)**
- [ ] **G6 DD2 — reference standard adopted** — **outstanding; the certificate cannot name a standard we have not adopted**
- [ ] G6 DD3–DD6 — sector requirements, sub-contracting liability, failure and inaccessible-device positions — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Verification page built and its permanence guaranteed by Platform Engineering — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
