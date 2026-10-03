---
id: TS-002
title: Test Data Pack and Persona Set
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: QA Lead with Data Migration Lead
author: QA Lead with Data Migration, MDM and Localisation
reviewers: [Data Migration Lead, MDM Lead, Localisation Lead, Chief Data Officer, Security Lead, L&D Lead, Content Design Lead]
approver: Content Design Lead with QA Lead
content_class: D
purpose: >
  The single synthetic dataset every test, every training exercise and every screenshot on this
  programme draws from — eleven personas mapped to the eleven registered audiences, Bangladeshi
  names with their transliteration variants and deliberate near-duplicates, real-shaped addresses
  down to upazila, valid-format phone numbers, reserved synthetic statutory identifiers, device
  identities, amounts that cross every approval threshold, and a Bengali text stress set. Without
  it testing runs on `test1@test.com` and Ratan Kumar, which never surfaces a Bengali rendering
  fault, an address-parsing failure, a name-matching false negative or a lakh-grouping error —
  and every one of those reaches production on day one, in front of 250,000 customers a month.
traces_to: [MD-006, MD-007, MD-012, MD-013, MD-019, MD-021, MD-022, MD-024, MD-029, MD-037, MD-039, MD-041, 05-04, 05-04 §7, 05-06 §9, 05-06 NFR-016, 05-06 NFR-035, 05-06 NFR-071, 05-06 NFR-086c, 05-06 NFR-099, BRU-SEC-08, HC-001, VB-009, TR-001, TR-003, TR-004, TR-005, DM-011, DM-012, TS-001, TS-003, TS-006, TS-011, TS-015, TS-016, TS-017]
priority: P0
wave: W1
bilingual: yes
bn_counterpart: TS-002_Test_Data_Pack_and_Persona_Set_BN.md
sources:
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md §1, §4 GEO-04, §6 — 8 divisions and 64 districts are stable and authoritative; upazila counts vary between published sources and five new upazilas were created in May 2026; Bengali names must be confirmed by the Localisation Lead, not accepted from an English source's transliteration
    verified: 2026-08-19
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-012_Employee_Master_Data_Template.md §intro and §SIT/UAT row — test data comes from TS-002, never from a production extract; 30 records with synthetic NIDs
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md §9 Localisation Standards (lakh/crore grouping 12,34,567; ICU bn-BD collation; +880 with operator validation; 10-digit and 17-digit NID formats validated; DD/MM/YYYY; July–June fiscal year); NFR-071; NFR-086c; §6.4 residency-classified field list
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1 (38 roles with headcounts), §7 Approval Authority Matrix (BDT thresholds 5,000 / 25,000 / 100,000 / 10% / 20% / 35% / 50,000 / 500,000 / 2,000,000 / 10,000 / 30,000)
    verified: 2026-08-19
    class: P1
  - source: Bangladesh national numbering plan — mobile operator prefixes 013 and 017 Grameenphone, 014 and 019 Banglalink, 015 Teletalk, 016 Airtel, 018 Robi, allocated by BTRC. https://en.wikipedia.org/wiki/Telephone_numbers_in_Bangladesh and https://www.telecompaper.com/news/grameenphone-banglalink-to-launch-numbers-with-prefixes-013-014--1258183
    verified: 2026-08-19
    class: P2
  - source: Bangladesh National ID formats — 10-digit Smart NID (final digit a checksum), with legacy 17-digit and 13-digit forms; issued by the Bangladesh Election Commission National Identity Registration Wing. https://en.wikipedia.org/wiki/National_identity_card_(Bangladesh) and https://docs.go.gbgplc.com/docs/go-v1/digital-id-portal/supported-digital-ids/bangladesh-nid
    verified: 2026-08-19
    class: P2
  - source: Bangladesh Business Identification Number — the 13-digit e-BIN is the only legally accepted form for VAT invoicing, import/export, tender participation and bank facilities under the VAT and Supplementary Duty Act 2012. https://lookuptax.com/docs/tax-identification-number/bangladesh-tax-id-guide
    verified: 2026-08-19
    class: P2
supersedes: none
review_due: 2027-02-19
---

# Test Data Pack and Persona Set

| Item | Value |
|---|---|
| Test level | **All** — every level draws from this pack (`TX-05`) |
| Role executing | Consumed by every `Rnn`; owned by QA Lead and Data Migration Lead |
| Modules covered | All 67 — the pack is dimensioned by `MD` masters, not by module |
| Portals covered | All 12 |
| Environment | `SIT`, `UAT`, `PERF`, `TRAIN` (`TS-001` §4.7) |
| Test data set | **This is it.** There is no second source |
| Wave | W1 · `P0` — nothing in W1 can be tested or trained on before it exists |

> **Template conformance.** `TPL_Content_File_Front_Matter.md` (template 1 per `CG-009` §3). All
> six sections retained in order. §4 is subdivided by data domain; the subdivision is the addition
> and is justified — eleven personas and nine data domains do not fit one section.

---

## 1. Purpose

`test1@test.com`, `John Smith`, `123 Main Street` and `1234567890` will pass every test this
programme writes and prove nothing. Nine specific classes of defect are invisible to placeholder
data and every one of them is a day-one production failure on this system:

| Placeholder data hides | Real consequence |
|---|---|
| Bengali rendering, conjuncts, and mixed-script strings | Illegible labels on the exact low-end Android devices technicians use (`VB-009`) |
| Bengali text expansion of 20–40% (`VB-007`) | Truncated buttons and broken icon-plus-label layouts at 1366×768 branch resolution |
| Lakh/crore grouping (`12,34,567`) | An invoice showing `1,234,567` to a Bangladeshi customer, and a finance team that cannot tie it out |
| Bangladeshi address structure and informality | Address validation that rejects half of real Dhaka, or a rider sent to the wrong Mirpur |
| Bengali and English name variants of the same person | `MD-013` duplicate matching produces either mass false merges or none at all |
| Operator-specific phone prefixes | OTP delivery failing on one network only, discovered by customers |
| NID / TIN / BIN format variety | A Mushak 6.3 challan rejected by the NBR, or a BIN field that silently truncates |
| Amounts on approval boundaries | `BRU-SRM-07`/`-08` and the `05-04` §7 matrix untested at the value where they bite |
| ICU `bn-BD` collation | Bengali search that returns nothing, against `NFR-035`'s 600 ms target |

**And one obligation.** Under `NFR-071`, `NFR-086c` and `BRU-SEC-08`, non-production environments
may not hold unmasked personal data — and since the Personal Data Protection Act 2026, holding a
copy of real customer data in a test environment is *processing* it. This pack is how the
programme tests without processing.

---

## 2. Scope

**In scope.** The persona set; the generation rules and the reserved synthetic blocks; the data
domains in §4.3–§4.9; volume profiles per environment; refresh, freeze and reset policy; and the
prohibition on production extracts.

**Out of scope.**

| Out of scope | Owned by |
|---|---|
| The master data itself — branches, catalogue, fault codes, price lists | Category 02 `MD`. This pack **references** `MD` values; it never invents a code |
| Migration mapping and cleansing rules | `DM-004`…`DM-011`; `DM-011` owns match-and-merge logic. This pack supplies the near-duplicates that *exercise* it |
| Load templates and column definitions | `DM-012`, `MD-048` |
| Masking of production data | Not permitted for this pack — §4.2 `TD-03` |
| Bengali wording quality | `BN-003` terminology, `BN-018` sign-off. This pack supplies *strings that stress rendering*, not approved copy |
| The 38 role login accounts | §4.10 states the requirement; provisioning is `M29` and `O-04` |

---

## 3. Audience

| Reader | Uses it for |
|---|---|
| **Test analysts** | Every script's test-data column resolves here |
| **Business super-users** | Recognising the data as plausible — an unrecognisable persona is not executed carefully |
| **Data Migration** | The near-duplicate and dirty-data set that exercises `DM-011` |
| **L&D and instructional designers** | Every practical exercise and every screenshot (`TR-003` `DS-14`) |
| **Localisation** | The Bengali stress set and its expected rendering |
| **Security and the Chief Data Officer** | Evidence that no production personal data leaves production |
| **Engineers** | Fixture seeds for `CI` |

---

## 4. Content

### 4.1 The eleven personas

**These are the eleven audiences registered in `HC-001` §4.1, not a new list.** `IA-01` there
establishes that `P06` analytics consumers are a *mode of use* by audiences 3, 4 and 7, not a
twelfth audience; the same holds here, so there is no separate "executive" persona — executives
are senior instances of persona 3.

| # | Persona | Audience (`HC-001` §4.1) | Roles (`05-04`) | Why this persona exists in the data |
|---:|---|---|---|---|
| 1 | **Nasrin, Dhanmondi householder** | 1 Customer | `R36` | Bengali-preferring, two registered appliances and a laptop, Privilege Silver, pays by bKash. The default customer path |
| 2 | **Rafiq, senior technician** | 2 Field technician | `R10` | Bengali-only reading, mid-range Android, works Gazipur where coverage drops. Carries van stock. The offline path |
| 3 | **Shirin, service centre agent** | 3 Internal operations | `R08` | Branch counter at 1366×768, keyboard-first, 40 intakes a shift. The `NFR-076` three-minute path |
| 4 | **Mr Haque, corporate IT administrator** | 4 Corporate administrator | `R37` | 340-asset estate across four sites, bulk CSV upload, approval chain, consolidated invoice disputes |
| 5 | **Meghna Traders, parts vendor** | 5 Vendor / supplier | `R38` | Responds to RFQs, submits invoices against POs, has one deliberately mismatched three-way-match case |
| 6 | **Jamal, marketplace freelance engineer** | 6 Marketplace seller | `R38` | Registration with NID and trade licence, one expired certification, one open dispute |
| 7 | **Brand partner "Anvica"** | 7 Brand partner | `R38` | 17-partner cohort representative; claim approvals, consignment stock, a rate-card version change mid-test |
| 8 | **Sujon, rider** | 8 Rider / logistics | `R16` | Offline manifest, OTP-and-signature handover, cash on delivery, one seal-break exception |
| 9 | **Tania, contact centre agent** | 9 Contact centre | `R34` | Screen-pop on caller identification, cross-channel history, disposition coding |
| 10 | **Kamal, field auditor** | 10 Field auditor | `R32` | Offline checklists, evidence capture, CAPA verification on site |
| 11 | **Shomobay Cooperative, referral partner** | 11 Referral / channel partner | `R38` | Referral links, lead conversion, commission statement |

**Each persona is a data cluster, not a name.** Persona 1 is a party record, three device records,
a warranty registration, a loyalty balance, an address with GPS, two historical jobs, one open job,
an invoice, a payment and a survey response — all internally consistent. A persona that is only a
name tests only the login screen.

#### Persona coverage matrix

| Persona | Bilingual surface | Offline | Payment | Statutory doc | Approval chain | Negative case built in |
|---:|:--:|:--:|:--:|:--:|:--:|---|
| 1 Nasrin | ● | | ● | ● | | Declines an estimate above `BDT 25,000` |
| 2 Rafiq | ● | ● | ● | ● | | Sync conflict; expired brand certification |
| 3 Shirin | ● | | ● | ● | ● | Attempts a 22% discount against a 10% limit |
| 4 Mr Haque | | | ● | ● | ● | Bulk upload with 6 invalid rows of 40 |
| 5 Meghna Traders | | | ● | ● | ● | PO/GRN/invoice mismatch outside tolerance |
| 6 Jamal | ● | ● | ● | | | Lists in an uncertified category (`BRU-ECM-07`) |
| 7 Anvica | | | ● | ● | ● | Rejects a claim for missing evidence (`BRU-WTY-01`) |
| 8 Sujon | ● | ● | ● | ● | | Customer absent; seal-break |
| 9 Tania | ● | | ● | | | Cannot see `internal_note` on a `P01` view |
| 10 Kamal | ● | ● | | ● | | Audits a branch with a cash variance |
| 11 Shomobay | | | ● | | | Referral that converts then refunds (`BRU-BIL-04`) |

### 4.2 Rules

| # | Rule |
|---|---|
| **TD-01** | **The pack is synthetic by construction, never masked production data.** Masking preserves distribution but also preserves the record; synthesis creates records that were never anyone's |
| **TD-02** | Every value is **format-valid** against the owning `MD` validation rule and **semantically impossible** as a real record — a real-shaped address at a non-existent holding number, an NID in a reserved block |
| **TD-03** | A production extract is never the source of test data, in any environment, at any volume, masked or not. `NFR-071` permits masked production data; **this pack does not use that permission** — the reason is recorded in `O-01` |
| **TD-04** | Every code value (branch, fault, resolution, reason, status, tax, UoM, part) is **taken from its `MD` file**, never invented. A test that passes on an invented code proves nothing about the configured system |
| **TD-05** | Bengali strings are **authored by the Localisation Lead**, not transliterated by a tester or a tool (`MD-006` §6 makes the same rule for geography) |
| **TD-06** | The pack contains **deliberate dirt**: near-duplicates, informal addresses, missing fields, wrong-format entries and one unparseable case per validated field. Clean data tests the happy path only |
| **TD-07** | Every approval threshold in `05-04` §7 has three values in the pack: **below, exactly at, and above**. Boundary defects live at "exactly at" |
| **TD-08** | Every persona has at least one built-in negative case (§4.1 matrix). A persona who only succeeds cannot exercise a hard rule |
| **TD-09** | Amounts, dates and quantities are internally consistent across the whole pack. A device warranty that expires before its purchase date creates test noise indistinguishable from a defect |
| **TD-10** | Financial data reconciles: the pack's invoices, receipts and journal effects tie to a stated control total, so `DM-013`-style reconciliation can be rehearsed on it |
| **TD-11** | The pack carries **no real person's name, photograph, voice, address, phone number or identifier** — including employees' and including the authors' |
| **TD-12** | The reserved synthetic blocks (§4.6) are **registered in `MD-048`** and a production write of a reserved-block value is a hard error, not a warning |
| **TD-13** | The pack is **versioned and release-pinned** like any content (`CG-006`). A defect reproduced on `TS-002 v1.3` states the version |
| **TD-14** | The `UAT` copy is **frozen for the duration of a UAT cycle** (`TS-001` §4.7); a data change mid-cycle voids every expected result already agreed (`TX-08`) |
| **TD-15** | The `TRAIN` copy is **resettable per cohort** — trainees destroy data by design (`TR-003` §4.5) |
| **TD-16** | Bengali and English variants of the same entity are **linked in the pack's own manifest**, so a name-matching test knows the right answer before it runs |
| **TD-17** | Volume profiles differ per environment (§4.10); a `PERF` profile in `UAT` makes UAT unusable, and a `UAT` profile in `PERF` makes `TS-014` meaningless |
| **TD-18** | Every file in the pack carries a header row, a UTF-8 BOM-free encoding declaration and a row count, matching `DM-012` load-template conventions |
| **TD-19** | Screenshots for training and help (`TR-003` `DS-14`, `HC-002`) are captured from this pack, so a screenshot can never leak a customer |
| **TD-20** | The pack is **not** a fixture library for unit tests. `CI` fixtures are engineering-owned and narrower; the boundary prevents a 12,000-party pack from being loaded on every commit |

### 4.3 Names — Bengali, English and the variants between them

Bangladeshi naming defeats naïve matching in five specific ways, and the pack carries a worked set
for each. Names below are **constructed patterns**, not people; the populated set is authored by
the Localisation Lead under `TD-05` and `TD-11`.

| # | Pattern | Why it breaks the system | Records in pack |
|---:|---|---|---:|
| N-01 | The same person written in Bengali script and in Latin transliteration | `MD-013` matching must treat them as one party; ICU `bn-BD` collation must sort them adjacently | 40 pairs |
| N-02 | **Multiple valid transliterations of one Bengali name** — the `Mohammad` / `Muhammad` / `Md.` / `Mohd` family, `Chowdhury` / `Choudhury` / `Chaudhury` | The most common false-negative in Bangladeshi customer matching | 60 records across 15 name families |
| N-03 | Honorific and prefix variance — `Md.`, `Mst.`, `Begum`, `Alhaj` as a stored prefix versus part of the given name | Determines whether "Md. Karim" and "Karim" are the same customer | 30 records |
| N-04 | Very common surname clusters with different addresses and phones | Blocking key on surname alone produces mass false merges | 8 clusters of 6 |
| N-05 | Single-word legal names, and names longer than a 60-character field | Truncation and `NOT NULL` on a non-existent surname | 12 records |
| N-06 | Corporate names with legal-form variance — `Ltd.` / `Limited` / `Ltd` / `PLC` and Bengali-script trade names | `MD-015` corporate hierarchy and consolidated invoicing | 20 records |

**The pack states the right answer.** For each of the 40 `N-01` pairs and 15 `N-02` families the
manifest records `is_same_party: true|false`, so `DM-011` match-and-merge can be scored rather than
inspected. **A matching test without a labelled answer set is a demonstration.**

### 4.4 Addresses

`MD-006` fixes the hierarchy at **8 divisions and 64 districts** as stable, with upazila counts
that differ between published sources and five upazilas created in May 2026. `MD-007` fixes the
format. The pack exercises both, plus the informality that real Bangladeshi addressing carries.

| # | Address class | Content | Records |
|---:|---|---|---:|
| A-01 | Fully structured, verified, GPS-present | All 8 divisions; ≥ 2 districts per division; urban and rural upazilas | 120 |
| A-02 | Dhaka metropolitan density | Dhanmondi, Mirpur, Uttara, Gulshan, Motijheel, Mohammadpur — with **road/block/house** patterns that only Dhaka uses | 80 |
| A-03 | **Ambiguous area names that repeat across districts** | "Mirpur" exists in Dhaka and in Kushtia; a zone assignment keyed on area name alone misroutes | 12 pairs |
| A-04 | Informal but real | "beside the mosque, third gate", landmark-only, no holding number, no postcode | 40 |
| A-05 | **Deliberately unparseable** | Free-text single-line addresses of the kind a legacy system holds | 20 |
| A-06 | Postcode mismatched to upazila | Tests whether validation cross-checks or merely format-checks the 4 digits | 15 |
| A-07 | New-upazila cases (May 2026) | Proves the geography load is current, not a 2024 snapshot (`MD-006` §6 known issue) | 5 |
| A-08 | Cross-zone edge | Addresses within 500 m of a `MD-005` dispatch-zone boundary | 10 |

**GPS coordinates** are supplied for A-01 and A-02 and deliberately absent for A-04 and A-05,
because `BRU-FSM-06` (geofence arrival) and `BRU-FSM-09` (geotagged failed visit) must be tested
both with and without a reliable pin.

### 4.5 Phone numbers

Bangladesh mobile numbers are `+880` followed by an operator prefix. **All seven live prefixes are
represented**, because OTP and SMS delivery fails per-operator and a single-operator test set
discovers that in production:

| Prefix | Operator | In pack |
|---|---|---:|
| `013`, `017` | Grameenphone | 60 |
| `014`, `019` | Banglalink | 40 |
| `015` | Teletalk | 20 |
| `016` | Airtel | 25 |
| `018` | Robi | 35 |

| # | Case | Purpose |
|---|---|---|
| P-01 | Stored with `+880`, without `+880`, with a leading `0`, with spaces and with hyphens | `MD-007` normalisation, and duplicate detection across formats |
| P-02 | Landline `+8802…` Dhaka numbers | Corporate contacts; `NFR` validation must not reject them |
| P-03 | The hotline `16743` as a short code | Never a customer number; must not be accepted as one |
| P-04 | Invalid: 10 digits, 12 digits, prefix `012`, alphabetic | Validation negative cases |
| P-05 | **Two personas sharing one number** | Household members (`P01` capability); tests that phone alone is not the party key |
| P-06 | One persona with three numbers, one marked primary | Notification routing (`NT-001` matrix) |

> **Deliverability.** Numbers in the pack are format-valid and **not routable** — SMS and OTP
> delivery is tested against a gateway sandbox with a whitelisted test MSISDN set, not against the
> pack. Sending an OTP to a format-valid number that belongs to a real subscriber is a nuisance at
> best and a data-protection question at worst. Recorded as `O-03`.

### 4.6 Statutory identifiers — reserved synthetic blocks

This is the highest-risk section of the pack and it is deliberately conservative.

| Identifier | Real format | Pack approach |
|---|---|---|
| **NID** | 10-digit Smart NID with a checksum final digit; legacy 17-digit and 13-digit forms | **Reserved block**, format-valid, allocated from a range registered in `MD-048`. Both the 10-digit and 17-digit forms are represented because `05-06` §9 requires both to validate |
| **TIN** | 12-digit taxpayer identification number | Reserved block, format-valid |
| **BIN** | **13-digit e-BIN** — the only legally accepted form for VAT invoicing under the VAT and SD Act 2012 | Reserved block. The pack also carries the **9-digit legacy form** as a negative case, because legacy data contains it and a Mushak 6.3 challan carrying it is non-compliant |
| **Passport** | Alphanumeric | Reserved prefix |
| **Trade licence, VAT registration** | Issuer-formatted | Reserved block for `R38` seller and vendor onboarding |

**Four hard rules apply to every value in this section.**

| # | Rule |
|---|---|
| **SI-01** | Values are drawn from a **registered reserved block** recorded in `MD-048`, never generated ad hoc by a tester |
| **SI-02** | The reserved block is chosen so that no value in it can be a currently issued identifier. **The Election Commission publishes no reserved test range**, so the block is an *internal* reservation and its safety rests on the write-blocking rule below, not on the numbering authority |
| **SI-03** | **A write of a reserved-block value to production is a hard error** (`TD-12`), enforced at the model layer per `BR-STD-01`, not by a warning |
| **SI-04** | These are **residency-classified fields** (`NFR-086`, `NFR-099`). Even synthetic, they are stored in the Bangladesh-resident store in every environment, so the residency enforcement of `NFR-086a` is itself exercised by the test data |

> **Why no complete example identifiers appear in this file.** A document that prints
> checksum-valid NID, TIN and BIN numbers becomes a source of plausible identifiers regardless of
> intent, and it will be copied. The **generation specification and the reserved ranges live in the
> data files** (`TS-002_*.csv`, access-controlled), not in the prose. `TD-11` and `CG-012` both
> point the same way.

### 4.7 Device and asset identity

Device identity is mandatory at intake (`BRU-SRM-01`), so the pack must make every intake path
reachable.

| # | Case | Purpose | Records |
|---|---|---|---:|
| D-01 | Serialised devices across all `MD-021` categories — mobile, tablet, laptop, desktop, printer, AC, refrigerator, washing machine, TV, server, network, CCTV, medical | Category-specific intake, fault trees and repair levels | 200 |
| D-02 | **Luhn-valid IMEI from a reserved TAC block**, 15-digit, plus dual-SIM pairs | `M17` registry, `P01` device registration, stolen-device screening path (`BRU-TRF-02`) | 60 |
| D-03 | Devices with **no serial or an illegible one** | The intake exception path — a real and frequent case |  25 |
| D-04 | Warranty states: in-warranty, expired, expiring in 3 days, void, extended, never registered | `BRU-SRM-02` gate and `BRU-WTY-07` eligibility | 48 |
| D-05 | Devices with prior service history including a **rework case within 30 days** | `BRU-SRM-06` automatic rework flag | 20 |
| D-06 | Devices on an active AMC covered-asset list, and one deliberately *not* on it | `BRU-SRM-03` hard gate | 30 |
| D-07 | Duplicate serials across two parties | Ownership-transfer and data-quality path (`DM-011`) | 8 |
| D-08 | Corporate estate: 340 assets under persona 4 across four sites and three departments | `P04` bulk operations and `NFR-041` 1,000-record bulk target |  340 |
| D-09 | Rental fleet units with condition reports, and trade-in units at each `MD` grade | `BRU-RNT-01`, `BRU-TRF-03` | 40 |
| D-10 | Hazardous items — lithium battery, refrigerant-bearing unit | `BRU-LOG-05` restricted-carriage rule; `KB-013` safety data | 12 |

### 4.8 Money, tax and thresholds

| # | Set | Content |
|---|---|---|
| M-01 | **Approval-boundary triples** | For every threshold in `05-04` §7 — estimates at 5,000 / 25,000 / 100,000; discounts at 10 / 20 / 35%; requisitions at 50,000 / 500,000 / 2,000,000; credit notes at 10,000; write-offs at 25,000; trade-ins at 30,000 — one value **below**, one **exactly at**, one **above**. 33 thresholds × 3 = **99 amounts** |
| M-02 | VAT cases | Standard-rated, exempt, zero-rated, supplementary-duty-bearing and mixed-line invoices, per `MD-037`. Includes an input-credit case with **no valid Mushak 6.3** to exercise `NFR-101` |
| M-03 | Rounding | Amounts that expose two-decimal rounding and `MD-039` policy, including a 3-way split that cannot divide evenly |
| M-04 | Grouping | Values above 99,999 to force **lakh/crore grouping** (`12,34,567`) in the Bengali locale and international grouping in English — the same number, two renderings, one invoice |
| M-05 | Payment channels | bKash, Nagad, card, bank transfer and cash, each with a success, a failure, a timeout and a duplicate-callback case (`NFR-042`, `BRU-FIN-03`) |
| M-06 | Cash controls | A receipt above `BDT 50,000` requiring an NID (`BRU-FIN-02`), and an unclosed shift blocking the next (`BRU-FIN-10`) |
| M-07 | Multi-currency | A brand claim valued in USD at the completion-date rate (`BRU-WTY-05`) and a period-end revaluation case (`BRU-FIN-07`) |
| M-08 | Opening balances | A trial-balance-consistent opening set so `G3-08` reconciliation can be rehearsed before cutover |

### 4.9 The Bengali text stress set

This is the part of the pack that no generic test-data tool produces.

| # | Stress case | What it breaks | Items |
|---|---|---|---:|
| B-01 | **Complex conjuncts** (যুক্তাক্ষর) and the ligature-heavy clusters | Font fallback on Android 11; print rendering on thermal printers (`05-06` §10) | 40 strings |
| B-02 | Zero-width joiner and non-joiner sequences | Copy, search and truncation behaviour; two visually identical strings that are not equal | 15 |
| B-03 | Vowel signs and reph above the line box | Line-height clipping at `VB-009` sizes | 20 |
| B-04 | **Longest-expansion strings** — Bengali equivalents of the shortest English labels | The `VB-007` 20–40% expansion allowance, at button and icon-label width | 30 label pairs |
| B-05 | Bengali numerals (`০১২৩`) versus Arabic digits in the same record | `VB-009` numeral policy; sorting; amount parsing |  20 |
| B-06 | Mixed-script strings — Bengali with embedded English model numbers | The commonest real technician note; also `HC-017` `IL-05` romanised input | 40 |
| B-07 | **Romanised Bengali** ("obosthai ki", "kaj hoise") | `NFR-074` phonetic input; search; `M32` intent matching | 40 |
| B-08 | ICU `bn-BD` collation ordering set with the **expected sort order stated** | `NFR-035` Bengali search at ≤ 600 ms p95, and any sorted list view | 60 items |
| B-09 | Bengali month names and DD/MM/YYYY in the Bengali locale | `MD-041` calendar; `NFR` date display | 12 |
| B-10 | Voice-note filenames and transcripts in Bengali | `P02` voice capture, `BN-017` IVR path | 10 |
| B-11 | Strings at the exact field length limit, and one over | Truncation versus rejection | 15 |

**B-08 carries its own answer key.** A collation test without a stated expected order is a
screenshot.

### 4.10 Volume profiles and role accounts

| Environment | Parties | Devices | Historical jobs | Open jobs | Employees | Rationale |
|---|---:|---:|---:|---:|---:|---|
| `CI` | 40 | 60 | 100 | 20 | 15 | Fast; fixtures only (`TD-20`) |
| `SIT` | 1,200 | 1,800 | 6,000 | 400 | 120 | Enough for list views, pagination and a 500-job dispatch board (`NFR-033`) |
| `UAT` | 2,000 | 3,000 | 10,000 | 500 | 200 | Recognisable to a business user; frozen per cycle (`TD-14`) |
| `PERF` | **500,000** | **750,000** | **3,000,000** | **5,000** | 1,000 | Production-shaped against `NFR-053` (5 m orders/year) and `NFR-054` (5 m assets); `TS-014` §3 sets the growth profile |
| `TRAIN` | 2,000 | 3,000 | 10,000 | 500 | 200 | Same shape as `UAT`, resettable per cohort (`TD-15`) |

**Role accounts are a separate deliverable from the persona data.** Eleven personas describe *whom
the data is about*; **38 roles** describe *who executes*. Every `Rnn` in `05-04` §1 needs at least
one account per environment, with the correct record rules, field-level restrictions and SoD
constraints applied — `TS-017` cannot run otherwise, and `05-04` §10 criterion 6 makes negative
testing a role-release condition. **The accounts do not exist and are not specified anywhere.**
`O-04`.

### 4.11 Refresh, freeze and reset

| Event | Action |
|---|---|
| New pack version | Regenerate, revalidate against every `MD` rule, republish with a version and a manifest diff |
| `MD` change (new fault code, new branch, tax-rate change) | Pack is re-validated within 5 working days; a stale code makes a passing test wrong |
| UAT cycle start | `UAT` copy **frozen**; changes queue for the next cycle (`TD-14`) |
| UAT cycle end | Refresh from the current pack version |
| Training cohort end | `TRAIN` reset (`TD-15`) |
| Wave gate | Pack version recorded in the gate evidence pack (`TS-018`) |
| Defect reproduction | Reproduce on the **recorded** pack version, never on the latest |

### 4.12 What this pack is not

| Not | Because |
|---|---|
| A masked production copy | `TD-01`, `TD-03`; and see `O-01` |
| A source of approved Bengali copy | `BN-003` and the `UI` packs own wording; this owns *stress strings* |
| A performance dataset by default | Only the `PERF` profile is; loading it elsewhere is `TD-17` |
| A `MD` substitute | `TD-04`; every code comes from its `MD` file |
| A migration test | `DM-013` reconciles the real load; this pack rehearses the method |
| Complete at v1.0 | The `PERF` profile at 3 m jobs requires generation tooling that does not exist — `O-05` |

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `MD-006`, `MD-007` | Geography and address format — §4.4 is derived from them, not parallel to them |
| `MD-013`, `DM-011` | The matching rules the near-duplicate set exists to exercise |
| `MD-021`, `MD-022` | Device categories, models and part compatibility |
| `MD-024`, `MD-025`, `MD-026`, `MD-027` | Fault, resolution, reason and status codes (`TD-04`) |
| `MD-029`, `MD-037`, `MD-039` | Price lists, tax codes and Mushak mapping, rounding |
| `MD-041` | Fiscal and holiday calendar for date-sensitive cases |
| `MD-048` | **Where the reserved synthetic blocks are registered** (`TD-12`, `SI-01`) |
| `05-04` §1, §7 | Roles and every approval threshold in `M-01` |
| `05-06` §9, §10 | Localisation and device standards |
| `VB-007`, `VB-009` | Expansion allowance and Bengali typography, which `B-04` tests |
| `HC-001` §4.1 | The eleven audiences the personas map to (`CP-01`) |
| `TR-003` `DS-14`, `TR-005` | Practical exercises and screenshots draw from this pack |
| `M29` | Role account provisioning — `O-04` |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | Per wave, and within 5 working days of any `MD` change |
| Trigger for out-of-cycle review | A new `MD` code set; a tax-rate or Finance Act change; a new upazila; a new portal; a residency reclassification; a defect traced to unrealistic test data |
| Owner | QA Lead with Data Migration Lead; Localisation Lead owns every Bengali string in it |
| Data files | `TS-002_Personas.csv` · `TS-002_Parties.csv` · `TS-002_Addresses.csv` · `TS-002_Devices.csv` · `TS-002_Amounts.csv` · `TS-002_Bengali_Stress_Set.csv` · `TS-002_Reserved_Blocks.csv` *(access-controlled)* · `TS-002_Manifest.json` |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`NFR-071` permits masked production data in non-production; this pack refuses that permission** (`TD-03`). The refusal needs ratification, because it is stricter than the NFR and adds generation effort. The argument: under the Personal Data Protection Act 2026 a masked copy is still a copy, `NFR-086c` forbids unmasked residency-classified data in any region, and `MD-012` already requires synthetic NIDs. **If the programme intends to allow masking, `NFR-071` and this rule must be reconciled once, not per test cycle** | Chief Data Officer with CTO | **W1** |
| **O-02** | **No reserved synthetic block is registered.** `MD-048` is the declared home (`TD-12`, `SI-01`) and carries no such entry; the Election Commission publishes no test range (`SI-02`), so the safety of every synthetic NID rests entirely on a production write-block that is also unimplemented | MDM Lead with Security Lead | **W1 — before the first record is generated** |
| **O-03** | **SMS/OTP deliverability path undefined** (§4.5). Format-valid numbers in the pack are not routable, and no gateway sandbox or whitelisted test MSISDN set is specified. `NT-004`…`NT-007` and every OTP-gated flow depend on it | Platform Engineering with Contact Centre | **W2** |
| **O-04** | **The 38 role accounts do not exist and are unspecified** (§4.10). `TS-017` cannot run, `05-04` §10 criterion 6 cannot be discharged, and no UAT script can name an executor. This is `TS-001` `O-09` seen from the data side | `M29` owner with QA Lead | **W1 — blocking `TS-017`** |
| **O-05** | **The `PERF` profile requires generation tooling nobody owns** — 500,000 parties and 3 million historical jobs, internally consistent and reconciling (`TD-09`, `TD-10`). Hand authoring is not possible; `TS-014` is unexecutable without it | QA Lead with Platform Engineering | **W2 — before `TS-014`** |
| **O-06** | **Bengali authoring capability is unresourced** — `TD-05` requires the Localisation Lead to author every Bengali string including the 60-item collation set with its expected order. The same gap is recorded at `TR-001` `O-05`, `KB-002` `O-05` and `HC-004` `O-03` | Localisation Lead | **W1** |
| **O-07** | **This pack is `P0`/W1 and Category 08 already depends on it.** `TR-001` `O-06` and `TR-003` `O-01` both record that every practical exercise and every screenshot assumes it exists. Writing this specification does not create the data; **generation must be scheduled, not assumed** | QA Lead with L&D Lead | **W1 — before the first `TR` pack is produced** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; §4 subdivision justified by domain volume
- [x] **Eleven personas mapped to the eleven `HC-001` §4.1 audiences rather than a new audience list (`CP-01`)**
- [x] Every persona is a data cluster with a built-in negative case, not a name
- [x] Twenty rules stated, including the synthetic-not-masked position and its rationale
- [x] Bangladeshi name, address, phone, identifier, device, money and Bengali-text domains specified with record counts
- [x] Approval-boundary triples derived from `05-04` §7 — 33 thresholds, 99 amounts
- [x] **No complete statutory identifier printed in the prose, and the reason recorded**
- [x] Matching and collation sets carry stated answer keys
- [x] Volume profiles per environment, with the role-account distinction made explicit
- [x] Freeze and reset policy stated for `UAT` and `TRAIN`
- [x] External facts sourced with verification dates (`CG-012`, `CM-R8`): operator prefixes, NID forms, 13-digit e-BIN
- [x] All internal links resolve
- [x] Seven open items recorded with owners and blocking consequences
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The data files themselves generated — outstanding; this file is the specification**
- [ ] **`O-02` reserved synthetic block unregistered — outstanding; blocks generation**
- [ ] **`O-04` role accounts unspecified — outstanding; blocks `TS-017`**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and QA Lead**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
