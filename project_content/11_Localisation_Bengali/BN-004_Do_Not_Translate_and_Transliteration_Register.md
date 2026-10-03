---
id: BN-004
title: Do-Not-Translate and Transliteration Register
project: 1000FiX ERP System v2.0
content_type: Register
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Enterprise Architecture, Finance and Brand
reviewers: [Enterprise Architecture, Brand Lead, Finance, Legal & Compliance, MDM Lead, Platform Engineering]
approver: Programme Content Lead
content_class: D
purpose: >
  Lists every string that must survive translation unchanged — statutory form names, regulator
  identifiers, brand and product names, technical identifiers, codes, units and standards — and
  fixes the rules by which names of people and places are transliterated between Bengali and
  Latin script. "Mushak 6.3", "bKash" and a model number rendered in Bengali script cannot be
  transcribed into a government system, matched against a brand partner's claim portal, or found
  by search. Customer names transliterated inconsistently produce duplicate party records, which
  is the failure mode M33 exists to prevent.
traces_to: [CG-004 T-05, BN-002 §4 Tier 1, BN-003, MD-006, MD-013, MD-021, MD-035, VB-009 MX-01, VB-009 BR-01, 05-06 §9, 05-06 NFR-074, DT-010]
priority: P1
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-004 T-05 — "Statutory terms are never paraphrased. Where an instrument names a thing — Mushak 6.3, VDS, BIN — that name is used exactly, in both languages, and appears in the do-not-translate register"
    verified: 2026-08-17
    class: P1
  - source: project_content/01_Voice_Brand_and_Design_Content/VB-009 MX-01, MX-05, BR-01 — do-not-translate items stay in Latin script inside Bengali text; never transliterate a technical identifier; the wordmark is never transliterated
    verified: 2026-08-17
    class: P1
  - source: project_content/02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006 §9 sample rows — geo_code, name_en, name_bn, alt_names_en showing Chattogram/Chittagong and Jashore/Jessore already carried as current and alternate forms
    verified: 2026-08-17
    class: P1
  - source: 1000_fix_corporate_website project_content LOCALIZATION/Bengali Language/BN-002 §7 Brand Names (DO NOT TRANSLATE) — established brand list for computer, mobile and appliance manufacturers
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §9 — National ID 10-digit and 17-digit formats validated; phone +880 with Bangladesh mobile operator validation
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-004 — Do-Not-Translate and Transliteration Register

> **Two failures, one register.**
>
> **Translate what must not be translated** and the output stops working: `মুশক ৬.৩` is not a
> form the NBR recognises, `বিকাশ` is not the merchant name on a payment gateway, and a model
> number in Bengali digits cannot be matched against a brand partner's parts catalogue.
>
> **Transliterate inconsistently** and the data stops working: করিম হোসেন, Karim Hossain and
> Kareem Hussain become three customers, three loyalty balances and three warranty histories for
> one person.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Which strings never change form in either direction; how names of people, places and organisations are transliterated; how identifiers are entered, stored and displayed |
| **What it does not govern** | Which Bengali term is used for a translatable concept (`BN-003`); how the surrounding sentence is written (`BN-002`); numeral glyphs in ordinary numbers (`BN-007`) |
| **What breaks without it** | Rejected statutory filings, unmatched warranty claims, unsearchable device records, duplicate party records, and a payment reference no gateway recognises |

---

## 2. Governing rules

| # | Rule |
|---|---|
| **DN-01** | **A Tier 1 item appears in Latin script, unchanged, in Bengali content** (`BN-002` `LW-02`, `VB-009` `MX-01`) |
| **DN-02** | Tier 1 items are **never transliterated**, in either direction. `মুশক`, `বিকাশ` and `স্যামসাং` are defects in ERP content, whatever the surrounding language |
| **DN-03** | **Every Tier 1 item inside Bengali text carries `lang="en"`** (WCAG SC 3.1.2, `CG-011` BA-02, `VB-009` `MX-04`). Without it a screen reader applies Bengali phonology to "Mushak" |
| **DN-04** | **Identifiers are entered and stored in Latin script and Arabic numerals**, whatever the interface language (`BN-001` `IN-09`) |
| **DN-05** | An identifier is **never reformatted for display** — no thousands separators in a reference number, no lakh grouping in an IMEI (`BN-007` `FM-12`) |
| **DN-06** | Where a Tier 1 item must be **spoken** — IVR, voice note, agent script — it is spoken as it is said in Bengali usage, not spelled out (`BN-017` `VP-06`) |
| **DN-07** | **The 1000FiX wordmark is never transliterated** (`VB-009` `BR-01`). It is a mark, not a word |
| **DN-08** | A brand's own preferred rendering governs. Where a brand publishes a Bengali form of its own name, that form is used **only if the brand publishes it**, never if we invent it |
| **DN-09** | Adding an entry to this register is a **register-first** action (`CG-004` `T-08` applied to Tier 1). A new brand, form or standard is registered before it appears in content |
| **DN-10** | This register is enforced by automated scan on every commit (§8). It is not a guideline |

---

## 3. Class A — Statutory and regulatory

**The highest-consequence class.** These strings are prescribed by an instrument or an authority.
Rendering them differently does not make them harder to read; it makes them wrong.

### 3.1 NBR forms and tax terms

| String | What it is | Note |
|---|---|---|
| **Mushak 6.1** | Purchase register | `DT-012` |
| **Mushak 6.2** | Sales register | `DT-011` |
| **Mushak 6.3** | VAT tax invoice | `DT-010`. The most-cited statutory string in the system |
| **Mushak 6.6** | VDS certificate | `DT-013` |
| **Mushak 9.1** | VAT return | `DT-014` |
| **VAT** | Value Added Tax | Never মূসক in ERP content, even though the Bengali form exists in the instrument |
| **VDS** | VAT Deducted at Source | `CG-004` §4.5 |
| **AIT** | Advance Income Tax | Registered here on first cross-module use |
| **BIN** | Business Identification Number | `fix.entity` field |
| **TIN** | Taxpayer Identification Number | Sensitive under `05-06` NFR-086 |
| **NBR** | National Board of Revenue | Never জাতীয় রাজস্ব বোর্ড in a document that cites a form |

> **The `VAT` / মূসক decision.** The Bengali মূসক is the statutory term and appears on the forms
> themselves. **The form's own printed wording is not ours to change** (`CG-004` `T-05`) — where
> we reproduce a prescribed layout, we reproduce it as prescribed. **In our own prose, labels and
> messages, `VAT` is used in both languages**, so that one string is searchable, one term is
> trained and one label appears on every surface. `BN-015` §4 holds the exact treatment per
> document. Raised as open decision 2 in §10 for Tax Manager confirmation.

### 3.2 Identity, registration and regulator

| String | What it is |
|---|---|
| **NID** | National ID. 10-digit and 17-digit formats (`05-06` §9) |
| **BRC** | Birth Registration Certificate |
| **RJSC** | Registrar of Joint Stock Companies and Firms |
| **BIDA** | Bangladesh Investment Development Authority |
| **Bangladesh Bank** | The central bank |
| **BTRC** | Bangladesh Telecommunication Regulatory Commission |
| **BSTI** | Bangladesh Standards and Testing Institution |
| **Trade Licence** | The municipal instrument. en-GB spelling in content |
| **Bangla Bhasha Prachalan Ain, 1987** | Cited by its Bengali name transliterated into Latin, with the year. Never translated into English as a title (`BN-001` §6.4) |

### 3.3 Standards

| String | Note |
|---|---|
| **ISO 9001:2015** | The company's certification; the version number is part of the name |
| **ISO 14001**, **ISO 45001**, **ISO 27001** | Registered for future use |
| **WCAG 2.1 AA** | `PS-04` contractual target |
| **BDS 1738:2018**, **BDS 1935:2018** | Bangladesh keyboard layout and coding standards (`BN-006` `EN-05`) |
| **Unicode**, **UTF-8**, **ICU** | Technical standards |

---

## 4. Class B — Brand, product and organisation names

### 4.1 1000FiX's own names

| String | Note |
|---|---|
| **1000FiX** | Capitalisation is exact: digit-digit-digit-digit-F-i-X. Never 1000Fix, 1000FIX, ১০০০FiX |
| **1000FiX Services Limited** | The registered entity name, used in Class A/B documents |
| **Privilege** | The loyalty programme (`CG-004` §5). Never প্রিভিলেজ |
| **16743** | The hotline number. Arabic digits always, in both languages (`DN-05`) |
| **fix.bd** | The short-link domain (`NT-004` §2.2) |
| **info@1000fix.com** | Addresses are never transliterated or translated |

> The tagline **may** exist as an approved Bengali translation registered in `VB-010`
> (`VB-009` `BR-02`). The tagline is not a Tier 1 item; the wordmark is.

### 4.2 Payment providers

| String | Note |
|---|---|
| **bKash** | Lower-case b, capital K. **Never বিকাশ in ERP content** — the payment reference and merchant name are Latin |
| **Nagad** | Never নগদ |
| **Rocket**, **Upay**, **SureCash** | |
| **Visa**, **Mastercard**, **American Express** | Card scheme names |
| **SSLCOMMERZ** | Gateway |

> **This diverges from the corporate website glossary**, which lists বিকাশ and নগদ as Bengali
> forms for marketing prose. The divergence is deliberate and is recorded: **marketing may name a
> brand in Bengali script; a transaction record may not.** The ERP set and the website set are
> separate by design (Master Index §11). Where an ERP surface is purely descriptive — a help
> article explaining what bKash is — the Latin form is still used, because the same article names
> the button the user must tap.

### 4.3 Device and appliance manufacturers

Brand names are Tier 1 in every language. The list below is the registered set; `MD-021` is the
operational catalogue and this register governs the **form**, not the membership.

| Category | Brands |
|---|---|
| Computing | Dell, HP, Lenovo, ASUS, Acer, MSI, Apple, Microsoft, Toshiba, Sony, VAIO, Chromebook |
| Mobile | Samsung, Apple, Xiaomi, Redmi, Realme, Oppo, Vivo, OnePlus, Nokia, Motorola, Infinix, Tecno, Symphony, Walton |
| Appliance | Samsung, LG, Walton, Singer, Vision, Minister, Marcel, Gree, Midea, Haier, Sharp, Panasonic, Hitachi, Rangs, Transcom, Whirlpool |
| Print & peripheral | HP, Canon, Epson, Brother, Xerox, Ricoh, Kyocera, Logitech |
| Network | TP-Link, D-Link, Cisco, Ubiquiti, Mikrotik |

| # | Rule |
|---|---|
| **BR-01** | **Model names and model numbers are Tier 1.** `Galaxy A54`, `Inspiron 15 3520`, `AR12TXHZ` (`MD-021`) |
| **BR-02** | A brand's **category word** may be Bengali where it is not part of the name: *Samsung এসি*, not *Samsung Air Conditioner* transliterated |
| **BR-03** | **Walton, Singer, Vision, Minister, Marcel and Rangs are Bangladeshi brands whose names are commonly written in Bengali script in consumer media.** In the ERP they remain Latin, because the same string is a warranty-claim key against the manufacturer's system |
| **BR-04** | Where a brand partner's claim portal requires a specific casing, that casing governs (`DT-033`, `M09`) |

---

## 5. Class C — Technical identifiers, codes and units

| Item | Form | Example | Note |
|---|---|---|---|
| Service order reference | Latin + Arabic digits | `SR-2026-114882` | Read aloud digit by digit (`NT-019` §2.3) |
| Job, work order, claim, invoice references | Latin + Arabic digits | `JB-…`, `WO-…`, `CL-…`, `INV-…` | Per `CG-005` sequences |
| **IMEI** | 15 Arabic digits, no grouping | `356938035643809` | `DN-05` |
| **Serial number** | Manufacturer's form, unchanged | | Case-sensitive |
| **MAC address** | Latin hex, colon-separated | | |
| Part number / SKU | Manufacturer's form | | `MD-022` |
| Barcode / QR payload | Unchanged | | `DT-044` |
| Mobile number | `+880` international form | `+8801XXXXXXXXX` | `05-06` §9 operator validation |
| Email, URL, domain | Unchanged | | Never transliterated |
| Bank account, routing number | Arabic digits, no grouping | | `MD-035` |
| Currency code | **BDT** | | The symbol `৳` is a `BN-007` matter, not this register |
| Units | `GB`, `TB`, `MHz`, `kWh`, `mm`, `kg`, `V`, `A` | | Unit symbols are Latin. The **quantity** follows `BN-007` |
| Technical abbreviations | `USB`, `HDMI`, `SSD`, `HDD`, `RAM`, `GPS`, `OTP`, `API`, `PDF`, `CSV`, `QR` | | Expanded on first use only where the audience needs it |
| Repair level | `L1`, `L2`, `L3` | | The website glossary's লেভেল ১ form is **marketing only**; ERP uses `L1` (`MD-010`) |
| Programme identifiers | `M01`…`M67`, `P01`…`P12`, `R01`…`R38`, `W1`…`W9`, `FR-…`, `NFR-…`, `BRU-…` | | `CG-004` `T-12` |
| Content identifiers | `CG-001`…`RF-012` | | `CG-005` |
| i18n keys | `p02.job.parts.scan.help` | | Lower snake_case, never Bengali script (`UI-001` `K-02`) |

---

## 6. Transliteration

Transliteration is needed in three places, and each has a different rule.

### 6.1 Person names

| # | Rule |
|---|---|
| **TL-01** | **The person's own stated spelling governs.** Where a Latin spelling is captured from an NID, passport, bank record or the customer's own entry, it is authoritative and is not "corrected" |
| **TL-02** | **Both forms are stored.** `fix.party` carries `name_bn` and `name_en`; whichever the user supplied is primary and the other is derived (`MD-013`) |
| **TL-03** | A **derived** transliteration is marked as derived. It is never printed on a statutory or legal document without confirmation |
| **TL-04** | Party matching searches **both** columns and tolerates the variation classes in `BN-003` `PS-03` |
| **TL-05** | **Statutory documents use the form on the identity document**, not the derived form (`DT-010`, `DT-032`) |
| **TL-06** | Honorifics — জনাব, মিসেস, ডঃ — are **not** part of the name and are stored separately |
| **TL-07** | Where a name contains a Tier 1 element — a company name inside a party name — that element stays Latin |

**Standard derivation conventions**, used only where no stated spelling exists:

| Bengali | Latin | Note |
|---|---|---|
| মোহাম্মদ / মোঃ | Mohammad / Md. | Both accepted; `Md.` is the common Bangladeshi form |
| হোসেন | Hossain | Not Hussain, Hosen |
| রহমান | Rahman | Not Rehman |
| আহমেদ | Ahmed | Not Ahmad |
| ইসলাম | Islam | |
| চৌধুরী | Chowdhury | Not Choudhury |
| খাতুন | Khatun | |
| বেগম | Begum | |
| আক্তার | Akter | Not Aktar |

> These conventions **reduce** variation; they do not eliminate it, and they are not applied
> retroactively to names a person has already given. `MD-013` matching rules, not this table, are
> what prevent duplicates.

### 6.2 Place names

| # | Rule |
|---|---|
| **TL-08** | **`MD-006` is the sole authority for place names in both scripts.** No content transliterates a place name independently |
| **TL-09** | The **current official Latin form** is used: Chattogram, Barishal, Bogura, Cumilla, Jashore, Netrokona. Superseded forms — Chittagong, Barisal, Bogra, Comilla, Jessore — live in `MD-006` `alt_names_en` and are **searchable but not displayed** |
| **TL-10** | Bengali place names use the **Bangla Academy standard spelling** (`BN-002` `OR-01`) |
| **TL-11** | Informal and colloquial address elements — a market name, a landmark — are stored as entered and are not normalised (`MD-007`) |
| **TL-12** | A postcode is Arabic digits in both languages (`DN-04`) |

### 6.3 Organisation names

| # | Rule |
|---|---|
| **TL-13** | A **registered** organisation name is Tier 1 in the form in which it is registered, in either script |
| **TL-14** | A corporate client's name on an invoice is **the name on their trade licence**, unchanged (`DT-020`, `MD-015`) |
| **TL-15** | A government body cited in a Class A document uses **its own official Bengali name** where the document is Bengali, and its official English name where the document is English. This is the one class where a body's name is not Tier 1 in both directions — because both official forms exist |

---

## 7. Reverse direction — Bengali content leaving the system

Often forgotten, and the source of the worst failures, because the defect appears in someone
else's system.

| Destination | Rule |
|---|---|
| **Statutory filing** | Identifiers Latin and Arabic digits (`DN-04`); prescribed form wording as prescribed; party name as on the identity document (`TL-05`) |
| **Brand partner claim portal** | Model, serial, part number and claim reference exactly as the partner's system expects (`BR-04`, `M09`) |
| **Payment gateway** | Merchant name, reference and amount in Latin and Arabic digits. **A Bengali-digit amount is a failed transaction, not a display preference** |
| **Courier / logistics API** | Address in the partner's required script; `MD-007` records which |
| **SMS gateway** | Bengali body is UCS-2 (`BN-014`); the sender mask `1000FiX` is Latin |
| **Data export — CSV, XLSX** | **UTF-8 with BOM** for Excel on Windows, or Bengali columns render as mojibake on branch machines (`RP-014`, `BN-006` `EN-06`) |
| **PDF** | Font embedded (`VB-009` `TF-05`); text layer must be extractable Bengali, not outlines |
| **Barcode / QR** | Payload Latin. **Bengali is never encoded into a barcode** (`DT-044`) |
| **File names** | Latin only. Bengali file names break on some printers, mail gateways and legacy Windows shares |

---

## 8. Enforcement

| Check | Mechanism | When |
|---|---|---|
| A Class A string transliterated into Bengali script | **Automated scan** against §3 | Every commit |
| A brand name in Bengali script | Automated scan against §4 | Every commit |
| An identifier containing Bengali digits | Automated regex | Every commit |
| An identifier with thousands separators | Automated regex | Every commit |
| A Tier 1 item without `lang="en"` | Automated | Every commit |
| Bengali in a file name, barcode payload or i18n key | Automated | Every commit |
| Place name not resolving to `MD-006` | Cross-check | Every `MD` load and every wave audit |
| Derived transliteration printed on a Class A document | Manual, at G6 | Per statutory document |
| Export encoding | Automated file-header check | Every export template release |

| # | Rule |
|---|---|
| **EN-01** | A `DN-01`/`DN-02` violation is a **blocking** defect. It is not a style finding |
| **EN-02** | The scan runs against **both** the English and Bengali bundles. A brand name misspelled in English fails equally |
| **EN-03** | The scan excludes files whose `content_type` is `Standard`, `Policy` or `Register` **within do-not tables and worked examples only** — this file cannot forbid `মুশক ৬.৩` without naming it. Same waiver structure as `CG-004` §9 case 5 |

---

## 9. Adding an entry

| Step | Action | Who |
|---|---|---|
| 1 | Establish the class — A statutory, B brand, C technical | Requester |
| 2 | Capture the **exact** form, including casing, punctuation and version number | Requester |
| 3 | Name the authority for that form — the instrument, the brand's own usage, the manufacturer's catalogue | Requester |
| 4 | Confirm no conflicting entry exists | Localisation Lead |
| 5 | Add to this register and to the term base as a **non-translatable** entry (`BN-008` §5) | Localisation |
| 6 | Add to the automated scan list | Platform Engineering |
| 7 | Log in `RF-006` | Programme Content Lead |

> **Class A additions require Finance or Legal confirmation of the authority (step 3).** A
> statutory string added on someone's recollection of a form is exactly the failure `CG-012` and
> audit `00-07` H2-13 exist to prevent.

---

## 10. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Is the complete brand list in §4.3 correct and complete against `MD-021` and `MD-017`?** The "17+ brands" figure is recorded as unverified (`00-07` H2-12, `MD-017`) | Commercial with MDM | Before W1 `MD-021` load | `MD-021`, `BN-003` §12 |
| 2 | **`VAT` versus মূসক in our own prose** (§3.1) | **Tax Manager** with Legal Counsel | Before the first Bengali statutory document | `BN-015` §4, `DT-010`…`DT-014` |
| 3 | Does any brand partner's claim portal require a **non-Latin** rendering? (`BR-04`) | `M09` owner | Before W4 | `DT-033`, `BN-015` |
| 4 | Are derived transliterations (`TL-03`) acceptable on a **repair warranty certificate**, which is contractual but not statutory? | Legal Counsel | Before W2 | `DT-032`, `TL-05` |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`BN-002_Bengali_Translation_Standard.md`](BN-002_Bengali_Translation_Standard.md) | Tier 1 is defined there; membership is defined here |
| [`BN-003_Bilingual_Terminology_Glossary.md`](BN-003_Bilingual_Terminology_Glossary.md) | Every Tier 1 row in `BN-003` §6 is also an entry here |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | Mixed-script rendering and export encoding |
| [`BN-007_Date_Time_Number_Currency_and_Address_Formats.md`](BN-007_Date_Time_Number_Currency_and_Address_Formats.md) | Numeral glyphs for ordinary numbers; `DN-05` for identifiers |
| [`../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](../00_Content_Governance_and_Standards/CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | `T-05` routes statutory terms here |
| [`../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md`](../01_Voice_Brand_and_Design_Content/VB-009_Bengali_Typography_and_Brand_Standard.md) | `MX-01`, `MX-05`, `BR-01` |
| [`../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md`](../02_Master_Data_and_Configuration/02A_Organisation_and_Network/MD-006_Bangladesh_Geographic_Hierarchy.md) | The place-name authority (`TL-08`) |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Ten governing rules; three do-not-translate classes covering NBR forms, regulators, standards, own brand, payment providers, 60+ manufacturer brands, identifiers, units and programme codes; transliteration rules for person, place and organisation names with standard derivation conventions; the reverse-direction export rules; nine automated enforcement checks; four open decisions including the `VAT`/মূসক question | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Every statutory string named in `CG-004` `T-05` registered, plus the wider NBR, regulator and standards sets
- [x] Brand list registered with the Bangladeshi-brand exception stated and reasoned (`BR-03`)
- [x] Identifier rules stated for entry, storage and display, including the no-reformatting rule
- [x] Transliteration rules cover person, place and organisation names, with the stated-spelling-governs principle first
- [x] **Reverse direction covered** — the failures that appear in someone else's system
- [x] Enforcement specified as automated where possible, with the self-reference waiver stated (`EN-03`)
- [x] The website-glossary divergence on বিকাশ / নগদ recorded and reasoned, not silently overridden
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal register, English-only by `CG-010` §3.2
- [ ] **Brand list verified against `MD-021` and `MD-017`** — outstanding; §10 item 1, and `00-07` H2-12 remains open
- [ ] **`VAT` / মূসক decision** — outstanding; §10 item 2, routed to Tax Manager
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
