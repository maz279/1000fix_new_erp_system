---
id: FIX-ERP2-M65
module_id: M65
module_code: GLO
module_name: Multi-Entity, Multi-Country & Localisation
category: K — Platform & Technology
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-13
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
business_owner: Chief Technology Officer
system_owner: Platform Squad
priority: P2
wave: W9
---

# M65 — Multi-Entity, Multi-Country & Localisation
### Category K · Code `GLO` · ★ New in v2.1

---

## 1. Module Identity

| Attribute | Value |
|---|---|
| **Module ID** | M65 |
| **Module code** | `GLO` |
| **Category** | K — Platform & Technology |
| **Status** | ★ **New** — split out of M30 after enterprise benchmarking |
| **Priority** | **P2** |
| **Delivery wave** | **W9** (the expansion wave) — **with mandatory W1 design obligations, see §16.3** |
| **Business owner** | Chief Technology Officer |
| **System owner** | Platform Squad |
| **Delivery layers** | L1 Odoo multi-company and `res.currency` · L2 OCA `l10n-bangladesh`, `operating-unit` · L5 custom country pack, locale pack, translation and consolidation engines |
| **Custom modules** | `cd_country_pack`, `cd_locale_pack`, `cd_multi_entity` |
| **Requirement range** | FR-GLO-001 … FR-GLO-036 |
| **Requirement count** | **36** *(measured — supersedes the 30 estimate in `02-02`; **new range allocation** under `05-01` §1.3a)* |
| **Effort estimate** | **23 person-weeks** *(measured — supersedes the 20 PW estimate)* |
| **Depends on** | M30 Platform Admin · M29 Identity · M64 MDM · M19 Financial Accounting · M51 Tax · M56 Payroll · M54 FP&A |
| **Depended on by** | **All 66 other modules** — every one carries entity, country, currency and locale context |

---

## 2. Purpose

M65 makes 1000FiX **operable in a second country without rebuilding it**.

Today the Company runs one legal entity in one country, in Bengali and English, on a July–June
fiscal year, filing Mushak returns to the NBR and collecting through bKash. Every one of those
is a *jurisdiction fact*, and every one of them is different in India, Myanmar or Nepal — the
three expansion markets the portal roadmap already identifies through their localised payment
gateways: **Razorpay, KBZPay and eSewa**.

M65 packages everything that varies by jurisdiction into an **installable country pack**, and
everything that varies by language and region into an **installable locale pack**. The Wave 9
gate criterion is stated precisely in the category overview: **a new country pack authored and
live in ≤ 12 weeks, with zero changes to core module code.**

It also owns the multi-entity dimension itself — the legal entity, its currency, its fiscal
calendar, its statutory obligations, its isolation from its siblings, and the consolidation
that reports them together.

### Why It Exists

**Because retrofitting multi-country costs three to five times what designing for it costs.**
This is the category's own risk statement, and it is why M65's *design obligations* land in
Wave 1 even though its *delivery* lands in Wave 9. Entity, country, currency and locale
dimensions must be carried on every record from the first module built. A module written in
Wave 2 without a country dimension is a module that must be rewritten in Wave 9.

**Because Bengali is not a translation, it is the primary language.** NFR-016 requires full
Bengali and English support in interfaces, notifications, reports and data entry. AS-12 makes
Bengali translation a definition-of-done item. The category KPI is **100% Bengali translation
completeness**. This is not an expansion concern — it is a Wave 1 concern that M65 owns the
infrastructure for.

**Because compliance is jurisdiction-shaped.** VAT at 15% with Mushak 6.3 invoices and a Mushak
9.1 return filed by the 15th; TDS and VDS categories; provident fund and gratuity under the
Labour Act; the Personal Data Protection Act 2026 and its residency rules; a July–June fiscal
year; moon-dependent public holidays. None of these are universal, and all of them are wired
into modules across Categories G, H and I.

**Because a second entity may come before a second country.** A franchise arm, a separate
trading company, or a regulated subsidiary would each need entity isolation, intercompany
handling and consolidation — inside Bangladesh, and potentially long before Wave 9.

### Evidence Basis

| Source | What It Establishes |
|---|---|
| `_CATEGORY_OVERVIEW.md` §2 | M65 owns "legal entities, country packs, locale packs, currency, translation, jurisdiction isolation, expansion readiness" |
| `_CATEGORY_OVERVIEW.md` §6 | M65 owns legal entity, country pack, locale, currency and translation; **M30 owns organisation structure and M65 adds the country dimension** |
| `_CATEGORY_OVERVIEW.md` §7 promises 5, 7 | Every module inherits multi-branch, multi-entity and multi-currency context (M30, M65); every module gets consistent Bengali and English localisation infrastructure (M65) |
| `_CATEGORY_OVERVIEW.md` §8 | **The country pack specification** — nine components, the Bangladesh reference pack, and the **≤ 12 week Wave 9 gate criterion with zero core code changes** |
| `_CATEGORY_OVERVIEW.md` §8 | Expansion markets identified through their payment gateways: **India (Razorpay), Myanmar (KBZPay), Nepal (eSewa)** |
| `_CATEGORY_OVERVIEW.md` §9 | **Bengali translation completeness 100%**; time to stand up a new legal entity **< 10 days**; time to stand up a new country pack **≤ 12 weeks** |
| `_CATEGORY_OVERVIEW.md` §11 | Risk: "Multi-country deferred, then retrofitted into a live single-entity system — typically **3–5× the cost** of designing for it". Mitigation: dimensions carried on every record **from Wave 1** |
| `02-01` §8 | The eight-dimension model including `country_id`, `currency_id` and `lang`, and the data isolation tiers |
| `05-06` §9 | **The full localisation standard** — Bengali primary, ICU `bn-BD` collation, lakh/crore grouping, DD/MM/YYYY, July–June fiscal year, Division→District→Upazila→Union/Ward, +880 validation, 100% translation before acceptance, professional translation only |
| `05-06` NFR-016, NFR-074, AS-12 | Bengali and English everywhere; Bengali phonetic input and voice-to-text; all strings translatable and translated |
| `05-06` NFR-059 | **10 legal entities across 5 countries** |
| `05-06` NFR-086, NFR-099 | Split residency and restriction on cross-border transfer of sensitive identifiers — a jurisdiction rule M29 enforces and M65 defines |
| `05-06` §6.1, §6.2 | The Bangladesh statutory set: VAT and SD Act 2012, ICT Act 2006, Cyber Security Ordinance 2025, Labour Act 2006, PDPA 2026, NFR-100 Mushak 9.1 by the 15th |
| `05-02` §M30 | `fix.locale.pack`, `fix.country.pack`, `fix.translation.entry` allocated to M30 — **reallocated to M65 in v2.1** |
| `06-02` BO-18 | "Be ready to operate in a second country — time to stand up a country pack ≤ 12 weeks", owner CTO |

---

## 3. Scope Boundary

> **The rule:** M65 owns **everything that varies because of where you are**. It does not own
> the business processes that consume those variations, and it does not own the organisation
> structure inside a jurisdiction.

### 3.1 In Scope

| # | Capability |
|---|---|
| 1 | Legal entity definition with country, base currency, fiscal calendar and statutory identity |
| 2 | Multi-entity operations: entity isolation, cross-entity visibility rules, entity-scoped configuration |
| 3 | **Country pack architecture** — the installable unit containing everything that varies by jurisdiction |
| 4 | Country pack authoring, versioning, installation, activation and retirement |
| 5 | Country pack component model: tax rules, statutory reports, payroll rules, address structure, holidays, payment methods, language, regulatory obligations, fiscal calendar |
| 6 | The **Bangladesh reference pack** — the canonical implementation every future pack is derived from |
| 7 | **Locale pack architecture** — language, formats, collation, input methods, number and date presentation |
| 8 | **Translation infrastructure**: string extraction, translation workflow, review, completeness measurement, release gating |
| 9 | Bengali-specific support: ICU `bn-BD` collation, font rendering, phonetic and Unicode input, voice-to-text, lakh/crore grouping |
| 10 | Text-expansion resilience in layouts across all 12 portals |
| 11 | Currency master, exchange rates, rate sources, revaluation basis and rounding rules |
| 12 | Multi-currency transaction, reporting and presentation currency handling |
| 13 | **Address structure per country**, including Bangladesh's Division → District → Upazila → Union/Ward hierarchy |
| 14 | Phone, national identifier, tax identifier and postcode validation per country |
| 15 | Public holiday calendars, including **moon-dependent dates** |
| 16 | Fiscal calendar and period structure per entity |
| 17 | **Jurisdiction rule register** — which statutory obligations apply to which entity |
| 18 | **Data residency and cross-border rules per jurisdiction**, consumed and enforced by M29 |
| 19 | Statutory report definition per country, executed by the owning finance and HR modules |
| 20 | Payment method availability per country |
| 21 | Intercompany transaction identification, matching and elimination support |
| 22 | Consolidation support: currency translation, entity roll-up, minority interest structure |
| 23 | Transfer-pricing documentation support |
| 24 | **Country onboarding**: the governed process that stands up a new jurisdiction in ≤ 12 weeks |
| 25 | Expansion readiness assessment and the core-code-change gate |
| 26 | Entity lifecycle: creation, activation, dormancy, closure and statutory retention |

### 3.2 Explicitly Out of Scope

| Capability | Owned By | Why the Boundary Sits Here |
|---|---|---|
| Organisation structure inside a jurisdiction — branch, zone, cost centre, business line | **M30** | M30 owns the structure; **M65 adds the country dimension to it**. Stated in the category boundary map |
| Technical configuration, feature flags, environments, jobs | **M30** | — |
| Master data governance, stewardship, quality rules | **M64** | M64 governs *changes* to jurisdiction reference data; M65 owns its content |
| Business rule parameters and thresholds | **M64** stores, **M63** executes | A VAT *rate* is jurisdiction content (M65); an approval *threshold* is a business parameter (M64) |
| **Tax calculation, VAT return preparation, Mushak filing, TDS/VDS computation** | **M51** Tax & Regulatory Compliance | M65 supplies the *rules and rates*; M51 *computes and files*. This is the sharpest boundary in the module |
| General ledger, chart of accounts content, posting rules | **M19** | M65 defines the fiscal calendar and currency; M19 owns the accounting |
| **Financial consolidation execution and reporting** | **M54** FP&A (with M19) | M65 supplies translation rates, entity roll-up structure and elimination identification; M54 produces the consolidated statements |
| **Payroll calculation, tax slabs, provident fund, gratuity** | **M56** Payroll | M65 supplies the country's payroll *rules*; M56 *calculates and pays* |
| Statutory report *content and submission* | **M19** / **M51** / **M56** / **M60** | M65 defines which reports apply and their structure; the owning module produces and files them |
| **Residency enforcement at write time, encryption, cross-border transfer gate** | **M29** | **M65 defines the jurisdiction rule; M29 enforces it.** Definition and enforcement are deliberately separated |
| Consent, lawful basis, data-subject request lifecycle | **M33** | — |
| Payment gateway integration and transaction processing | **M20** / **M50** | M65 declares which methods are available in a jurisdiction; the finance modules integrate them |
| Import, customs, duty and landed cost | **M44** | A cross-border *goods* discipline, not a cross-border *operating* one |
| Customer, supplier and employee records | **M33** / **M42** / **M21** | — |
| Country expansion as a **business project** — market entry, licensing, premises, hiring | **M67** PPM | M65 makes the system ready; M67 manages the programme around it |
| Country market strategy and commercial model | Executive / **M40** Partner & Franchise | — |

### 3.3 Shared Concepts

| Concept | M65's Role | Owning Module |
|---|---|---|
| Legal entity | **Owns** the country, currency, fiscal calendar and statutory attributes; M30 owns the object | M65 / M30 |
| Branch, zone, cost centre | Adds the country dimension; M30 owns them | M30 / M65 |
| Country pack | **Owns** | M65 |
| Locale pack and translation | **Owns** | M65 |
| Currency and exchange rate | **Owns** the master and rate sourcing; M19 owns accounting treatment, M50 owns treasury policy | M65 / M19 / M50 |
| Tax rule and rate | **Owns** the jurisdiction rule; **M51 computes and files** | M65 / M51 |
| Payroll rule | **Owns** the jurisdiction rule; **M56 calculates** | M65 / M56 |
| Public holiday | **Owns**; M30 applies it to working calendars | M65 / M30 |
| Address structure | **Owns** per country; M33 owns the address records | M65 / M33 |
| Data residency rule | **Owns** the definition; **M29 enforces** | M65 / M29 |
| Consolidation | **Owns** translation rates and roll-up structure; **M54 consolidates** | M65 / M54 |
| Statutory report | **Owns** the definition and applicability; the owning module produces it | M65 / M19, M51, M56 |

---

## 4. Benchmark Basis

| Reference System | Equivalent Capability | What We Adopted | What We Rejected |
|---|---|---|---|
| **Microsoft Dynamics 365 localisation and country/region packs** | Vendor- and partner-certified localisation packs incorporating regionally mandated features and regulations; country packs manage tax and legal requirements **without modifying the core system** | **The country pack as an installable unit that never modifies core code is the defining pattern of M65**, and it is what makes the ≤ 12 week Wave 9 gate achievable. Adopted directly, including the principle that a pack is versioned and certified rather than hand-configured | Vendor-supplied packs — no vendor supplies a Bangladesh pack of the depth 1000FiX needs, so the Bangladesh pack is authored and becomes the reference implementation |
| **Oracle Fusion / NetSuite multi-entity architecture** | A legal entity per country with a chart of accounts configured to local standards; **standard account structure across entities for straightforward consolidation with local mapping where statutory reporting requires different groupings**; automatic currency revaluation and consolidation | **The standard-core-plus-local-mapping pattern for the chart of accounts** — a shared structure that consolidates cleanly, with a jurisdiction mapping layer for statutory presentation. Also adopted: automatic revaluation and translation rather than manual adjustment | NetSuite's OneWorld subsidiary hierarchy depth; at 10 entities across 5 countries a two-level structure suffices |
| **SAP multi-country / global template practice** | A global template with local extensions; country versions carrying statutory content | The **global-template discipline**: a capability is built once in the core and varied by pack, never forked per country. This is the difference between one system in five countries and five systems |
| **Multi-country ERP rollout practice (2025–26)** | Identify jurisdictions, determine mandatory legal and tax reporting per country, embed transfer-pricing documentation from day one rather than bolting it on | **Transfer-pricing documentation designed in rather than added later**, and a jurisdiction obligation register that is explicit rather than assumed | A phased big-bang country rollout methodology; 1000FiX will enter one country at a time |
| **ICU / CLDR internationalisation standards** | Locale-aware collation, formatting, pluralisation and calendar handling | **ICU `bn-BD` collation as the standard** (`05-06` §9), lakh/crore number grouping, and locale-driven date and currency presentation. Getting Bengali sorting wrong is a daily irritation that erodes trust in the whole system | — |
| **Translation management practice** | Extraction, translation memory, review workflow, completeness gating in CI | **Translation completeness as a release gate** (AS-12): a module with untranslated strings does not ship. Also adopted: **professional translation with native-speaker review; machine translation is not acceptable for release** (`05-06` §9) | Continuous localisation tooling licences; the string volume is manageable with an in-house workflow |
| **OCA `l10n-bangladesh`** | Bangladesh chart of accounts and VAT foundation on Odoo | Adopted as the L2 seed for the Bangladesh pack, extended substantially — the OCA module covers a fraction of what `_CATEGORY_OVERVIEW.md` §8 specifies | Relying on it as the pack; it is a starting point, not a solution |

**Design position.** Five deliberate differences.

First, **M65's delivery is Wave 9 but its design obligations are Wave 1, and this is the single
most important thing about the module**. The category risk is unambiguous: retrofitting
multi-country typically costs three to five times what designing for it costs. Every module
built in Waves 1–8 must therefore carry `country_id`, `currency_id` and `lang`, must read tax
rates and holidays from a pack rather than a constant, and must externalise every user-facing
string. **M65 in Wave 9 assembles and proves a capability that Waves 1–8 must not foreclose.**
§16.3 states these obligations as testable Wave 1 requirements.

Second, **the Bangladesh pack is a real pack, not a hard-coded default**. The tempting shortcut
is to hard-code Bangladesh and introduce the pack abstraction when a second country appears.
That shortcut guarantees the retrofit. Bangladesh is authored as **country pack `BD` version 1**
from Wave 1, and the platform reads it exactly as it will read `IN`, `MM` or `NP`. The
abstraction is proved continuously by the only country in production.

Third, **definition and enforcement are separated throughout**. M65 declares that Bangladesh
restricts large-scale transfer of sensitive identifiers; M29 blocks the write. M65 declares that
VAT is 15% with Mushak 6.3 invoices; M51 computes and files. M65 declares the provident fund
rule; M56 calculates it. This keeps jurisdiction knowledge in one place while keeping execution
with the module that owns the process — and it means a country pack can be authored by people
who understand the jurisdiction rather than the codebase.

Fourth, **Bengali is treated as a first-class primary language, not a translation target**.
`05-06` §9 makes Bengali the primary field and customer language with English secondary. Layouts
are designed for Bengali text expansion, sorting uses ICU `bn-BD`, numbers group in lakh and
crore, and translation quality requires native-speaker review. A system that works in English
and is "also available in Bengali" fails 250,000 customers a month and 400 technicians.

Fifth, **entity separation is designed before it is needed**. A second Bangladeshi legal entity
— a franchise arm, a trading company, a regulated subsidiary — is materially more likely in the
near term than a second country. The multi-entity capability is therefore built to be usable
independently of the country capability, and the < 10 day new-entity KPI reflects that.

---

## 5. Functional Areas & Features

### 5.1 Legal Entity & Multi-Entity Operations

| FR ID | Feature | Function — "The system shall…" | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GLO-001 | Legal entity definition | Extend the M30 entity with country, base currency, fiscal calendar, statutory identifiers, registered address, regulatory registrations and its country pack assignment | **P0** | L1/L5 |
| FR-GLO-002 | **Entity provisioning** | Stand up a new legal entity in one governed action — chart of accounts, fiscal periods, currency, tax configuration, statutory obligations, numbering sequences and access scoping — targeting **under 10 days end to end** | **P0** | L5 |
| FR-GLO-003 | Entity isolation | Isolate entity data by default, with cross-entity visibility granted explicitly and auditable (isolation tier T1) | **P0** | L1/L5 |
| FR-GLO-004 | Entity-scoped configuration | Allow configuration, reference data and business parameters to be scoped per entity, inheriting from global where not overridden | **P0** | L5 |
| FR-GLO-005 | Entity lifecycle | Create, activate, make dormant and close an entity, with statutory record retention preserved after closure | P1 | L5 |
| FR-GLO-006 | Fiscal calendar | Define the fiscal year and period structure per entity — **July–June for Bangladesh** — with period open, close and lock states consumed by M19 | **P0** | L1/L5 |
| FR-GLO-007 | Numbering sequences | Provide entity- and country-scoped document numbering that satisfies statutory format requirements | **P0** | L1/L5 |

### 5.2 Country Pack Architecture

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GLO-008 | **Country pack model** | Define a country pack as a versioned, installable unit containing tax rules and rates, statutory reports, payroll rules, address structure, public holidays, payment methods, language and locale, regulatory obligations and fiscal calendar (`_CATEGORY_OVERVIEW.md` §8) | **P0** | L5 |
| FR-GLO-009 | Pack authoring and validation | Author a pack through a structured definition, validate its completeness against the nine-component model, and reject an incomplete pack | **P0** | L5 |
| FR-GLO-010 | Pack versioning and installation | Version, install, activate, upgrade and retire a pack per entity, with the active version visible and change-controlled | **P0** | L5 |
| FR-GLO-011 | **Zero-core-change gate** | Verify that installing a pack requires no change to core module code, and fail the country onboarding gate if any core change is required | **P0** | L5 |
| FR-GLO-012 | **Bangladesh reference pack** | Deliver the Bangladesh pack as the canonical implementation: VAT 15% with Mushak formats, TDS/VDS categories, Labour Act payroll rules, Division→District→Upazila→Union/Ward addressing, moon-dependent holidays, bKash/Nagad/SSLCOMMERZ/BEFTN, Bengali locale, ICT Act and Cyber Security Ordinance 2025 obligations, July–June fiscal year | **P0** | L2/L5 |
| FR-GLO-013 | **Jurisdiction obligation register** | Hold every statutory obligation per country — what must be filed, to whom, in what format, by when, with what penalty — and expose it to the owning modules and to M60 | **P0** | L5 |
| FR-GLO-014 | Statutory report definitions | Define which statutory reports apply per country and their structure, so that **M19, M51 and M56 produce them without country-specific code** | **P0** | L5 |
| FR-GLO-015 | **Data residency rules per jurisdiction** | Declare which data classes are residency-restricted, which cross-border transfers require notification, and what safeguards apply — **consumed and enforced by M29** (NFR-086, NFR-099) | **P0** | L5 |
| FR-GLO-016 | Payment method availability | Declare which payment methods are available and mandated per country — bKash, Nagad, SSLCOMMERZ, BEFTN for Bangladesh; **Razorpay, KBZPay, eSewa for the identified expansion markets** | P1 | L5 |
| FR-GLO-017 | Address structure per country | Define the administrative address hierarchy, validation rules and presentation format per country | **P0** | L5 |
| FR-GLO-018 | Identifier validation per country | Validate phone numbers, national identifiers, tax identifiers and postcodes per country — **+880 with operator validation, 10- and 17-digit NID for Bangladesh** | **P0** | L5 |
| FR-GLO-019 | Public holiday calendars | Maintain holiday sets per country including **moon-dependent dates**, versioned annually, consumed by M30 working calendars, M02 dispatch and M55 workforce scheduling | **P0** | L5 |

### 5.3 Localisation & Translation

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GLO-020 | **Locale pack model** | Define a locale pack containing language, character encoding, collation, number grouping, date and time format, currency presentation, calendar and input method | **P0** | L5 |
| FR-GLO-021 | **Bengali locale** | Deliver `bn-BD` as the primary locale: UTF-8, **ICU `bn-BD` collation**, **lakh/crore grouping (12,34,567)**, DD/MM/YYYY with Bengali month names, 12-hour time with Bengali AM/PM, BDT with ৳ symbol, Gregorian calendar with Bangladesh holidays | **P0** | L5 |
| FR-GLO-022 | **Translation infrastructure** | Extract every user-facing string, manage translation through a review workflow, store translations versioned per locale, and serve them to all modules and all 12 portals | **P0** | L5 |
| FR-GLO-023 | **Translation completeness gate** | Measure completeness per module and per portal and **block release below 100%** (AS-12, `05-06` §9) | **P0** | L5 |
| FR-GLO-024 | Translation quality control | Require professional translation with native-speaker review; **reject machine translation for release** | **P0** | L5 |
| FR-GLO-025 | Bengali rendering and input | Guarantee correct Bengali font rendering across Android, iOS, Windows, thermal printers and PDF output; support phonetic and Unicode keyboard input and voice-to-text on mobile (NFR-074) | **P0** | L5 |
| FR-GLO-026 | Text expansion resilience | Verify that layouts across all 12 portals remain usable under Bengali and other-language text expansion, as a release gate | P1 | L5 |
| FR-GLO-027 | Locale resolution | Resolve the effective locale per user, per document and per notification from user preference, entity default and channel, and apply it consistently | **P0** | L5 |
| FR-GLO-028 | Localised document output | Produce invoices, service reports, contracts and statutory documents in the correct language and format per recipient and jurisdiction, including Bengali rendering in PDF/A | **P0** | L5 |

### 5.4 Currency & Multi-Currency Operations

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GLO-029 | Currency master | Maintain currencies with symbol, decimal places, rounding rule and active status | **P0** | L1 |
| FR-GLO-030 | Exchange rates and sources | Maintain exchange rates with declared source, rate type (spot, average, closing) and effective date; import from a nominated source on a schedule | **P0** | L1/L5 |
| FR-GLO-031 | Transaction, base and reporting currency | Support a transaction currency, an entity base currency and a group reporting currency on every monetary record, with the rate and rate date stored (AS-10) | **P0** | L1/L5 |
| FR-GLO-032 | Revaluation and translation | Provide the rate basis for period-end revaluation and consolidation translation, executed by M19 and M54 | P1 | L5 |
| FR-GLO-033 | Currency presentation | Present amounts per locale — ৳ with lakh/crore grouping in Bengali, international grouping in English — without changing the stored value | **P0** | L5 |

### 5.5 Intercompany, Consolidation & Expansion Readiness

| FR ID | Feature | Function | Pri | Layer |
|---|---|---|:--:|:--:|
| FR-GLO-034 | **Intercompany and consolidation support** | Identify intercompany transactions between entities, match counterparties, flag imbalances, supply elimination candidates and provide the entity roll-up structure and translation rates that **M54 and M19 use to consolidate**; support transfer-pricing documentation with the arm's-length basis recorded per intercompany arrangement | P1 | L5 |
| FR-GLO-035 | **Country onboarding process** | Provide the governed onboarding workflow that stands up a new jurisdiction: obligation discovery, pack authoring, translation, integration selection, validation, pilot and activation — instrumented against the **≤ 12 week** target | **P0** | L5 |
| FR-GLO-036 | Expansion readiness assessment | Assess and report readiness per candidate country: pack completeness, translation coverage, integration availability, residency feasibility, obligations understood and open gaps | P1 | L5 |

> **Note on grouping.** FR-GLO-034 aggregates intercompany identification, consolidation support
> and transfer pricing because all three are M65 *supplying inputs* to M19 and M54 rather than
> performing the accounting. Each sub-obligation is separately testable and appears individually
> in §17.

---

## 6. Technical Functions

| # | Technical Function | Requirement |
|---|---|---|
| T-01 | **Dimension carried from Wave 1** | `country_id`, `currency_id` and `lang` are present on every relevant model from the first module built, verified by the model-registry check in CI alongside AS-03. **This is the technical expression of the whole module's design position** |
| T-02 | **Pack-driven, never hard-coded** | No module contains a jurisdiction constant — no literal VAT rate, no hard-coded address level, no embedded holiday. Verified by static analysis for known jurisdiction literals |
| T-03 | **Zero core change on pack install** | Installing a country pack touches only pack data and configuration. A pack requiring a core code change fails the onboarding gate and is a design defect, not an acceptable outcome |
| T-04 | **Pack resolution performance** | Jurisdiction rule and reference lookup resolves in ≤ 2 ms from cache, invalidated on pack version change |
| T-05 | **Locale resolution determinism** | The effective locale for any user, document or notification resolves by a single declared precedence chain, so the same content never renders inconsistently across channels |
| T-06 | **ICU-backed collation and formatting** | Sorting, comparison, number grouping and date formatting use ICU with the `bn-BD` locale, not application-level approximations |
| T-07 | **Bengali rendering verification** | Bengali conjunct rendering is verified on Android, iOS, Windows, thermal receipt and label printers, and PDF/A output as a release gate — not assumed from a font declaration |
| T-08 | **Translation completeness in CI** | Completeness is computed per module and per portal in CI; below 100% the build fails (AS-12) |
| T-09 | **Text expansion testing** | Layout tests run with a pseudo-locale producing controlled text expansion, so truncation is caught before translation rather than after |
| T-10 | **Currency precision** | All money uses decimal with an explicit currency (AS-10, DI-01); presentation never alters the stored value; rounding follows the currency's declared rule |
| T-11 | **Rate immutability** | The exchange rate applied to a transaction is stored with its source and date and is never re-derived later |
| T-12 | **Entity isolation at the record rule** | Entity isolation is enforced by M29 record rules at tier T1, not by application filtering |
| T-13 | **Residency rule as data** | Residency rules are pack data consumed by M29's enforcement engine; adding a jurisdiction adds data, not code |
| T-14 | **Moon-dependent holidays** | Holiday sets support dates confirmed close to the event; a provisional date is marked as such and the system tolerates its change without breaking scheduled work |
| T-15 | **Scale envelope** | **10 legal entities across 5 countries** (NFR-059); ~20,000 translatable strings per locale; 5 locales at Wave 9 |
| T-16 | **Pack versioning and rollback** | A pack version can be rolled back; historical documents continue to resolve against the pack version in force when they were created |

---

## 7. Business Functions & Benefits to 1000FiX

### 7.1 What Changes for Each Role

| Role | Today | With M65 |
|---|---|---|
| **Technician** | Uses a system that is mostly English with some Bengali | Works entirely in Bengali, with correct rendering, sorting and number formats |
| **Customer** | Receives invoices and notifications in inconsistent language | Receives everything in their preferred language, formatted correctly |
| **Branch agent** | Sorts a Bengali customer list and finds it in the wrong order | Correct ICU `bn-BD` sorting, correct lakh/crore amounts |
| **Finance** | Bangladesh tax rules are embedded in code; a rate change is a release | Rates and rules live in the pack; a change is a pack version |
| **CFO** | Cannot model a second entity or country without a rebuild | New entity in under 10 days; new country in 12 weeks |
| **CEO** | Expansion is an aspiration with an unknown system cost | Expansion is a bounded, instrumented process with a stated gate |
| **Developer** | Would embed a jurisdiction assumption without noticing | Static analysis blocks jurisdiction literals; the pack is the only source |
| **Compliance / M60** | Obligations live in people's knowledge | A jurisdiction obligation register naming what is filed, to whom and by when |

### 7.2 Quantified Business Benefit

| Benefit | Mechanism | Value |
|---|---|---|
| **Retrofit cost avoided** | Entity, country, currency and locale dimensions designed in from Wave 1 | The category states retrofitting multi-country typically costs **3–5× designing for it**. Against a **$455K–780K** programme, avoiding a retrofit of the multi-entity layer is the largest single sum M65 protects |
| **Expansion capability** | Country pack live in **≤ 12 weeks** with zero core code change | **BO-18** — the Wave 9 gate criterion. Without it, entering India, Myanmar or Nepal means a second implementation, not a configuration |
| **New entity speed** | Single-action entity provisioning | **< 10 days**, against "not possible" today. A franchise arm or trading subsidiary becomes a commercial option rather than an IT project |
| **Bengali adoption** | 100% translation, correct rendering, correct sorting, correct number formats, phonetic input | Adoption is the precondition for **every** benefit in the programme. A system 400 technicians and 250,000 monthly customers cannot use comfortably delivers none of the BDT 876 lac |
| **Compliance rate change agility** | Tax rates, thresholds and statutory formats in a versioned pack | A VAT or TDS change becomes a pack version rather than a code release — and Bangladesh changes these regularly. Supports **BO-10 (zero compliance findings)** |
| **Consolidation readiness** | Entity roll-up, translation rates, intercompany identification | Makes multi-entity reporting possible on day one of the second entity rather than months later |
| **Transfer-pricing defensibility** | Arm's-length basis recorded per intercompany arrangement from the start | Retrofitting transfer-pricing documentation after the fact is expensive and weakly defensible |
| **Statutory filing reliability** | Obligation register with deadlines and penalties, feeding M51, M56 and M60 | Protects against the class of failure where an obligation is discovered by a penalty notice |
| **Franchise and partner model** | Entity isolation and entity-scoped configuration | A precondition for the franchise capability in **M40 Partner, Channel, Alliance & Franchise** |

### 7.3 Non-Business (Institutional) Benefits

| Benefit | Why It Matters |
|---|---|
| **Linguistic dignity** | Bengali as the primary language, properly rendered and sorted, is a statement about who the system is built for. Staff notice, and it affects adoption more than any feature |
| **Regulatory credibility** | An explicit obligation register per jurisdiction is what a regulator, an auditor or a prospective partner asks to see |
| **Architectural discipline** | The no-jurisdiction-literals rule forces a cleanliness that benefits the codebase generally |
| **Corporate and government tender qualification** | Multi-entity capability and demonstrable localisation are procurement criteria for larger clients |
| **Strategic optionality** | A company that can enter a market in 12 weeks makes different strategic choices from one that needs 12 months |
| **Knowledge codification** | Bangladesh regulatory knowledge captured as a pack rather than held by individuals |
| **Reference implementation value** | The Bangladesh pack, authored to this standard, is itself an asset — there is no comparable open-source Bangladesh localisation |

---

## 8. Lifecycle & State Models

### 8.1 Country Pack Lifecycle

```
        ┌──────────────┐
        │   DRAFTED    │  nine components authored (`_CATEGORY_OVERVIEW.md` §8):
        └──────┬───────┘  tax · statutory reports · payroll · address ·
               │          holidays · payment methods · locale ·
               │          regulatory obligations · fiscal calendar
               │ completeness validated (FR-GLO-009)
        ┌──────▼───────┐
        │  VALIDATED   │  ✖ incomplete ──► returned with missing components named
        └──────┬───────┘
               │ **zero-core-change gate** (FR-GLO-011)
               │  ✖ requires a core code change ──► **GATE FAILED**
               │                                    (design defect; escalate)
        ┌──────▼───────┐
        │   CERTIFIED  │  legal and tax review signed off
        └──────┬───────┘
               │ installed against an entity in a non-production environment
        ┌──────▼───────┐
        │   PILOTED    │  transactions run end to end; statutory outputs verified
        └──────┬───────┘
               │ activation approved
        ┌──────▼───────┐
        │    ACTIVE    │◄────────────────┐
        └──┬────────┬──┘                 │
           │        │ new version        │ upgrade validated
           │        └────────────────────┤
           │                             │
           │ superseded by a new version │
        ┌──▼───────────┐                 │
        │  SUPERSEDED  │ historical docs │
        │              │ still resolve   │
        └──┬───────────┘ against it (T-16)
           │
           │ jurisdiction exited
        ┌──▼───────────┐
        │   RETIRED    │  no new transactions; statutory retention preserved
        └──────────────┘
```

| From | To | Guard | Actor |
|---|---|---|---|
| — | Drafted | Country onboarding initiated | CTO / country lead |
| Drafted | Validated | All nine components present and structurally complete | System |
| Validated | **Gate failed** | Installing the pack would require a core code change | System (**hard gate**) |
| Validated | Certified | Legal and tax review of the jurisdiction content signed off | Legal / CFO |
| Certified | Piloted | Installed in a non-production entity; transactions and statutory outputs verified | Country lead |
| Piloted | Active | Activation approved; entity assigned | CTO + CFO |
| Active | Superseded | A new version activated; the prior version remains resolvable historically | CTO |
| Active | Retired | Jurisdiction exited; statutory retention preserved | CFO + CEO |

### 8.2 Legal Entity Lifecycle

```
   PLANNED ──► registration in progress; country pack identified
       │
       │ **single-action provisioning** (FR-GLO-002):
       │ chart of accounts · fiscal periods · currency · tax configuration ·
       │ statutory obligations · numbering sequences · access scoping
       ▼
   PROVISIONED ──► configured; not yet transacting          target: **< 10 days**
       │
       │ statutory registrations complete; opening balances loaded
       ▼
   ACTIVE ──► transacting; consolidated into group reporting
       │
       ├──► trading ceased, records retained ──► DORMANT ──┐
       │                                                    │ resumed
       │◄───────────────────────────────────────────────────┘
       │
       │ wound up
       ▼
   CLOSED ──► no new transactions; **statutory retention preserved
              for the jurisdiction's required period; never deleted**
```

### 8.3 Translation Lifecycle

```
   String added in code with a translation key
        │
   ┌────▼──────────┐
   │  EXTRACTED    │  automatically at build
   └────┬──────────┘
        │
   ┌────▼──────────┐
   │  UNTRANSLATED │ ──► appears on the completeness report;
   └────┬──────────┘     **counts against the release gate**
        │ professional translation
   ┌────▼──────────┐
   │  TRANSLATED   │
   └────┬──────────┘
        │ native-speaker review (`05-06` §9)
        │  ✖ machine translation detected ──► REJECTED
   ┌────▼──────────┐
   │   REVIEWED    │
   └────┬──────────┘
        │ text-expansion layout check (T-09)
   ┌────▼──────────┐
   │   APPROVED    │ ──► served to modules and portals
   └────┬──────────┘
        │ source string changes
   ┌────▼──────────┐
   │    STALE      │ ──► returns to untranslated; gate reapplies
   └───────────────┘
```

---

## 9. Business Rules

Classification: **H** hard block · **A** approved override · **S** soft warning · **C** computed

| ID | Rule | Class | Owner |
|---|---|:--:|---|
| BRU-GLO-01 | **No module contains a jurisdiction literal** — no hard-coded tax rate, address level, holiday, identifier format or currency assumption. All resolve from a country pack | **H** | CTO |
| BRU-GLO-02 | **Installing a country pack must require no change to core module code**; a pack that does fails the onboarding gate | **H** | CTO |
| BRU-GLO-03 | Every relevant model carries `country_id`, `currency_id` and `lang` **from Wave 1**, verified in CI | **H** | CTO |
| BRU-GLO-04 | Bangladesh is implemented as country pack `BD`, not as a hard-coded default | **H** | CTO |
| BRU-GLO-05 | A country pack cannot be activated without all nine components present and legal and tax review signed off | **H** | CFO / Legal |
| BRU-GLO-06 | A module cannot be released below 100% translation completeness for every active locale (AS-12) | **H** | CTO |
| BRU-GLO-07 | Machine translation is not acceptable for release; professional translation with native-speaker review is required | **H** | CTO |
| BRU-GLO-08 | Bengali is the primary language; English is secondary. A capability available only in English is incomplete | **H** | CTO |
| BRU-GLO-09 | Entity data is isolated by default; cross-entity visibility is granted explicitly and is auditable | **H** | CFO / CTO |
| BRU-GLO-10 | The exchange rate applied to a transaction is stored with its source and date and is never re-derived | **H** | CFO |
| BRU-GLO-11 | All money uses decimal with an explicit currency; presentation formatting never alters the stored value | **H** | CFO |
| BRU-GLO-12 | **M65 defines jurisdiction rules; M51 computes tax, M56 calculates payroll, M29 enforces residency, M54 consolidates.** M65 performs none of these | **H** | CTO |
| BRU-GLO-13 | Residency and cross-border rules are pack data consumed by M29; adding a jurisdiction adds data, not code | **H** | CTO |
| BRU-GLO-14 | A superseded pack version remains resolvable so that historical documents render and compute as they did when created | **H** | CFO / CTO |
| BRU-GLO-15 | A closed entity's records are retained for the jurisdiction's statutory period and are never deleted | **H** | CFO / Legal |
| BRU-GLO-16 | A provisional moon-dependent holiday is marked as such, and its confirmation must not break scheduled work | **C** | CTO |
| BRU-GLO-17 | Intercompany transactions are identified and matched; an unmatched intercompany balance blocks period close | **H** | CFO |
| BRU-GLO-18 | Every intercompany arrangement records its arm's-length basis for transfer-pricing documentation | **H** | CFO |
| BRU-GLO-19 | The statutory obligation register is the authoritative source of what must be filed, to whom and by when; a missing obligation is a compliance defect | **H** | CFO / M60 |
| BRU-GLO-20 | A country pack change follows M64's governed change process; jurisdiction reference data is governed master data | **H** | CTO |

---

## 10. Data Entities

### 10.1 Owned Entities

Includes the three entities reallocated from M30 (`05-02` §M30) under the v2.1 re-scope.

| Entity | Table | Purpose | Key Attributes |
|---|---|---|---|
| `fix.country.pack` | `fix_country_pack` | **The installable jurisdiction unit** *(from M30)* | country_code, name, version, state, components_complete, core_change_required, certified_by, certified_at, activated_at, superseded_by_id, retired_at |
| `fix.country.pack.component` | `fix_country_pack_component` | One of the nine components | pack_id, component_type (tax/statutory_report/payroll/address/holiday/payment/locale/obligation/fiscal), definition_json, owner_module, authored_by, reviewed_by |
| `fix.jurisdiction.obligation` | `fix_jurisdiction_obligation` | **The statutory obligation register** | pack_id, obligation_code, description, statute_reference, verified_on, owning_module, filing_frequency, due_rule, submission_channel, penalty_summary, active |
| `fix.jurisdiction.tax.rule` | `fix_jurisdiction_tax_rule` | Tax rules and rates supplied to M51 | pack_id, tax_type (vat/sd/rd/tds/vds/withholding), code, rate, basis, applies_to, invoice_format, effective_from, effective_to, statute_reference |
| `fix.jurisdiction.payroll.rule` | `fix_jurisdiction_payroll_rule` | Payroll rules supplied to M56 | pack_id, rule_type (tax_slab/provident_fund/gratuity/bonus/overtime), definition_json, effective_from, effective_to, statute_reference |
| `fix.jurisdiction.residency.rule` | `fix_jurisdiction_residency_rule` | **Residency and transfer rules enforced by M29** | pack_id, data_class, residency_required, cross_border_permitted, notification_required, safeguard_required, authority_name, statute_reference, effective_from |
| `fix.address.structure` | `fix_address_structure` | Address hierarchy per country | pack_id, level_sequence, level_name_local, level_name_en, mandatory, validation_rule, presentation_order |
| `fix.address.node` | `fix_address_node` | Administrative geography values | structure_id, level, code, name_local, name_en, parent_node_id, postcode_range, active |
| `fix.identifier.format` | `fix_identifier_format` | Per-country validation | pack_id, identifier_type (phone/national_id/tax_id/postcode/bank), pattern, length_options, checksum_rule, example, operator_prefixes |
| `fix.holiday.set` | `fix_holiday_set` | Holiday calendars | pack_id, year, name, region_scope, published_at, version |
| `fix.holiday` | `fix_holiday` | A holiday date | set_id, date, name_local, name_en, type, **moon_dependent**, provisional, confirmed_at, working_day_impact |
| `fix.fiscal.calendar` | `fix_fiscal_calendar` | Fiscal year and periods | entity_id, pack_id, year_start_month, year_end_month, period_count, periods_json, current_period, locked_through |
| `fix.payment.method.availability` | `fix_payment_method_availability` | Methods per country | pack_id, method_code, provider, method_type, mandatory, integration_ref, active_from |
| `fix.locale.pack` | `fix_locale_pack` | **The locale unit** *(from M30)* | locale_code (bn-BD/en/hi-IN/my-MM/ne-NP), name, encoding, collation, number_grouping, decimal_separator, thousands_separator, date_format, time_format, currency_position, calendar, input_methods, is_primary, active |
| `fix.translation.entry` | `fix_translation_entry` | **Translation store** *(from M30)* | key, source_string, locale_code, translated_string, module, context, state (untranslated/translated/reviewed/approved/stale), translated_by, reviewed_by, machine_translated_flag, updated_at |
| `fix.translation.completeness` | `fix_translation_completeness` | Release gate measurement | module_or_portal, locale_code, total_keys, translated, reviewed, approved, completeness_pct, gate_passed, measured_at |
| `fix.rendering.verification` | `fix_rendering_verification` | Bengali rendering assurance | locale_code, target (android/ios/windows/thermal/label/pdf), test_set_ref, verified_at, verified_by, result, issues |
| `fix.entity.jurisdiction` | `fix_entity_jurisdiction` | Entity ↔ country pack assignment | entity_id, country_pack_id, pack_version, locale_default, base_currency, reporting_currency, assigned_at, assigned_by |
| `fix.exchange.rate` | `fix_exchange_rate` | Rates with provenance | from_currency, to_currency, rate, rate_type (spot/average/closing), source, source_reference, effective_date, imported_at |
| `fix.intercompany.arrangement` | `fix_intercompany_arrangement` | Transfer-pricing basis | entity_a_id, entity_b_id, arrangement_type, description, **arm_length_basis**, documentation_ref, effective_from, reviewed_at |
| `fix.intercompany.transaction` | `fix_intercompany_transaction` | Identified intercompany flow | source_document_type, source_document_id, entity_from_id, entity_to_id, amount, currency, arrangement_id, matched_counterpart_id, matched, elimination_candidate, period |
| `fix.consolidation.structure` | `fix_consolidation_structure` | Entity roll-up | parent_entity_id, child_entity_id, ownership_pct, consolidation_method, minority_interest_pct, effective_from |
| `fix.country.onboarding` | `fix_country_onboarding` | **The ≤ 12 week process instance** | country_code, initiated_at, phase, obligations_discovered, pack_id, translation_status, integrations_selected, residency_assessed, piloted_at, activated_at, elapsed_weeks, core_changes_required, gate_result |
| `fix.expansion.readiness` | `fix_expansion_readiness` | Readiness assessment | country_code, assessed_at, pack_completeness_pct, translation_coverage_pct, integration_availability, residency_feasible, obligations_understood, open_gaps, recommendation |

### 10.2 Referenced Entities

| Entity | Owned By | Access |
|---|---|---|
| `fix.entity`, `fix.branch`, `fix.zone`, `fix.working.calendar` | **M02** / **M30** / **M63** | Extend with the country dimension; M30 owns the objects |
| `fix.data.classification`, residency enforcement | **M29** | **M65 defines the rule; M29 enforces it** |
| Tax computation, VAT return, Mushak filing | **M51** | M65 supplies rules and rates |
| Payroll calculation, tax slabs, PF, gratuity | **M56** | M65 supplies rules |
| Chart of accounts, GL, fiscal period control | **M19** | M65 supplies the fiscal calendar and currency |
| Consolidation and management reporting | **M54** | M65 supplies roll-up structure and translation rates |
| `fix.party`, `fix.address` | **M33** | M65 supplies the structure; M33 owns the records |
| Governed change process for jurisdiction reference data | **M64** | Country pack changes follow M64's workflow |
| Payment gateway integrations (bKash, Nagad, SSLCOMMERZ, Razorpay, KBZPay, eSewa) | **M20** / **M50** / **M28** | M65 declares availability; the finance modules integrate |
| Statutory obligation tracking and compliance calendar | **M60** GRC | Consumes the obligation register |
| `fix.business.parameter` | M64 | Boundary reference — a threshold is M64's, a rate is M65's |

---
## 11. Automations

| ID | Trigger | Action | Failure Behaviour |
|---|---|---|---|
| AUT-GLO-01 | Country pack submitted for validation | Check all nine components present and structurally complete; report anything missing | Return to draft with the gaps named |
| AUT-GLO-02 | Country pack validated | **Run the zero-core-change gate**; detect any core code dependency the pack would require | **Fail the gate**; escalate to CTO as a design defect |
| AUT-GLO-03 | Country pack certified and activated | Install against the assigned entities; invalidate jurisdiction caches; notify every consuming module | Roll back; alert |
| AUT-GLO-04 | Country pack superseded | Retain the prior version as resolvable; re-point new transactions to the new version | Retain both; alert on ambiguity |
| AUT-GLO-05 | Entity provisioning requested | Create chart of accounts, fiscal periods, currency configuration, tax setup, statutory obligations, numbering sequences and access scoping atomically | **Roll back completely**; report the failing step |
| AUT-GLO-06 | Build executed | Extract translatable strings; compute completeness per module and locale | — |
| AUT-GLO-07 | **Translation completeness below 100% for an active locale** | **Fail the build** with the untranslated keys listed (AS-12) | Hard block |
| AUT-GLO-08 | Source string changed | Mark its translations stale; return them to the untranslated queue; reapply the gate | — |
| AUT-GLO-09 | Translation submitted | Route for native-speaker review; **flag suspected machine translation for rejection** | Hold in review |
| AUT-GLO-10 | Portal or module layout changed | Run text-expansion layout tests with a pseudo-locale; report truncation and overflow | Fail the release gate on critical truncation |
| AUT-GLO-11 | Scheduled (daily) | Import exchange rates from the nominated source per currency pair with provenance | Retain the previous rate; alert Finance |
| AUT-GLO-12 | Annual, or on gazette publication | Load the holiday set for the coming year; mark moon-dependent dates provisional | Alert; retain the previous year as reference |
| AUT-GLO-13 | Moon-dependent holiday confirmed | Update the date, notify M30 working calendars, M02 dispatch and M55 scheduling, and re-evaluate affected scheduled work | Alert affected modules |
| AUT-GLO-14 | Statutory obligation due date approaches | Notify the owning module and M60 at the configured lead time | Escalate to CFO |
| AUT-GLO-15 | Jurisdiction statute changes | Flag the affected pack components for review with the verification date; require re-certification | Alert CFO and Legal |
| AUT-GLO-16 | Intercompany transaction posted | Identify the counterparty entity, attempt matching, flag imbalances and mark elimination candidates | Report as unmatched; block close on imbalance |
| AUT-GLO-17 | Period close attempted with unmatched intercompany balances | **Block the close**; present the unmatched items | Hard block |
| AUT-GLO-18 | Country onboarding initiated | Open the process instance, start the 12-week clock, sequence the phases and track elapsed time | Report; escalate on overrun |
| AUT-GLO-19 | Country onboarding phase completes | Advance the phase, recompute readiness, report against the ≤ 12 week target | Report only |
| AUT-GLO-20 | Jurisdiction literal detected in code by static analysis | **Fail the build** naming the module, file and literal | Hard block |
| AUT-GLO-21 | Quarterly | Re-verify statutory references with dated confirmation, mirroring the `05-06` §6.1 discipline | Alert CFO and Legal on stale verification |

---

## 12. Interfaces

### 12.1 Upstream — M65 Consumes

| Source | What | Mechanism |
|---|---|---|
| **M30 Platform Admin** | Entity, branch, zone and working calendar objects that M65 extends | REST |
| **M64 MDM** | Governed change process for jurisdiction reference data; hierarchy governance | REST + events |
| **M29 Identity** | Entity isolation record rules; classification register for residency mapping | REST |
| **M28 Integration** | Event distribution; exchange rate and holiday feed connectors | Framework |
| M19 / M51 / M56 / M54 | Confirmation that supplied rules are consumable; statutory output verification during pilot | REST |
| M60 GRC | Obligation tracking and compliance calendar feedback | REST |
| External: exchange rate source | Daily rates with provenance | Connector (M28) |
| External: government gazette / holiday publication | Annual holiday sets and moon-dependent confirmations | Manual + connector |

### 12.2 Downstream — M65 Provides

| Consumer | What | Mechanism |
|---|---|---|
| **Every module (all 66)** | Country, currency and locale context; jurisdiction rules; translated strings | REST + framework |
| **All 12 portals** | Locale packs, translations, formatting, address structures, identifier validation | REST |
| **M29 Identity** | **Residency and cross-border transfer rules that M29 enforces** | REST |
| **M51 Tax** | Tax types, rates, bases, invoice formats and filing obligations | REST |
| **M56 Payroll** | Tax slabs, provident fund, gratuity, bonus and overtime rules | REST |
| **M19 Financial Accounting** | Fiscal calendar, period structure, currency, exchange rates, numbering sequences | REST |
| **M54 FP&A** | Entity roll-up structure, translation rates, elimination candidates | REST |
| M30 Platform Admin | Holiday sets applied to working calendars; country dimension on the entity | Events |
| M33 Party Master | Address structure, identifier validation, locale preference | REST |
| M20 / M50 | Payment method availability per jurisdiction | REST |
| M60 GRC | The statutory obligation register | Events |
| M55 Workforce Scheduling | Holiday and working-day impact | Events |
| M24 Documents | Localised document output and retention by jurisdiction | REST |
| M25 BI / M62 | Entity, country and currency dimensions for reporting | Warehouse extract |
| M67 PPM | Country onboarding phases as project milestones | Events |

### 12.3 Domain Events Published

| Event | Payload Summary | Consumers |
|---|---|---|
| `country_pack.activated` | country, version, entities affected, components | **All modules**, M51, M56, M19, M29 |
| `country_pack.superseded` | country, old version, new version, changed components | All modules |
| `country_pack.gate_failed` | country, core changes required, detail | **CTO**, M67 |
| `jurisdiction.tax_rule_changed` | country, tax type, old rate, new rate, effective from | **M51**, M19, M20, M11 |
| `jurisdiction.payroll_rule_changed` | country, rule type, effective from | **M56**, M21 |
| `jurisdiction.residency_rule_changed` | country, data class, residency, transfer conditions | **M29**, M60 |
| `jurisdiction.obligation_registered` | country, obligation, owning module, due rule, penalty | **M60**, M51, M56, M19 |
| `jurisdiction.obligation_due` | obligation, entity, due date, owning module | M60, owning module |
| `entity.provisioned` | entity, country, currency, fiscal calendar, pack version | **All modules**, M19, M29 |
| `entity.status_changed` | entity, state, effective from | All modules, M19, M54 |
| `holiday_set.published` | country, year, holidays, provisional dates | **M30**, M02, M55, M21 |
| `holiday.confirmed` | country, provisional date, confirmed date, affected scheduling | M30, M02, M55 |
| `exchange_rate.published` | currency pair, rate, type, source, effective date | M19, M20, M44, M50, M54 |
| `translation.completeness_changed` | module or portal, locale, completeness, gate result | CI, CTO |
| `locale_pack.activated` | locale, formats, collation, input methods | All portals, all modules |
| `intercompany.unmatched` | entities, amount, period, source documents | **M19**, M54, CFO |
| `consolidation.structure_changed` | parent, child, ownership, method | **M54**, M19 |
| `country_onboarding.phase_completed` | country, phase, elapsed weeks, readiness | M67, CTO, CEO |
| `country_onboarding.completed` | country, elapsed weeks, core changes required, gate result | **CTO, CEO** (the BO-18 measure) |

### 12.4 External Integrations

| INT ID | System | Direction | Purpose |
|---|---|---|---|
| INT-GLO-01 | **Exchange rate source** (Bangladesh Bank / AD bank rates, and per-country equivalents) | Inbound | Daily rates with provenance for M19, M44, M50 and M54 |
| INT-GLO-02 | Bangladesh government gazette / holiday publication | Inbound | Annual holiday sets and **moon-dependent date confirmations** |
| INT-GLO-03 | Bangladesh administrative geography (Division → District → Upazila → Union/Ward) | Inbound | Address structure reference data, maintained as governed data through M64 |
| INT-GLO-04 | **NBR tariff and VAT rate publications** | Inbound | Tax rule updates to the `BD` pack, consumed by M51 and M44 |
| INT-GLO-05 | Bangladesh mobile operator prefix register | Inbound | +880 phone validation |
| **INT-008** | International payment gateway (Stripe / PayPal) | Bidirectional | Cross-border customer payments (`05-03` §2.1, W9) |
| INT-GLO-06 | **Razorpay (India)** *(expansion)* | Bidirectional | Payment method availability for the India pack |
| INT-GLO-07 | **KBZPay (Myanmar)** *(expansion)* | Bidirectional | Payment method availability for the Myanmar pack |
| INT-GLO-08 | **eSewa (Nepal)** *(expansion)* | Bidirectional | Payment method availability for the Nepal pack |
| INT-GLO-09 | Translation service provider | Bidirectional | Professional translation with native-speaker review |

### 12.5 API Surface

| Endpoint | Method | Purpose | Consumer |
|---|---|---|---|
| `/api/v1/jurisdiction/{country}/pack` | GET | The active country pack and its version | All modules |
| `/api/v1/jurisdiction/{country}/tax-rules` | GET | Tax types, rates, bases and invoice formats | **M51**, M19, M20, M11 |
| `/api/v1/jurisdiction/{country}/payroll-rules` | GET | Tax slabs, PF, gratuity, bonus, overtime | **M56** |
| `/api/v1/jurisdiction/{country}/residency-rules` | GET | **Residency and cross-border transfer rules** | **M29** |
| `/api/v1/jurisdiction/{country}/obligations` | GET | The statutory obligation register | **M60**, M51, M56, M19 |
| `/api/v1/jurisdiction/{country}/address-structure` | GET | Address hierarchy and validation | M33, all portals |
| `/api/v1/jurisdiction/{country}/identifier-formats` | GET | Phone, NID, TIN, postcode validation | M33, all portals |
| `/api/v1/jurisdiction/{country}/holidays/{year}` | GET | Holiday set including provisional dates | M30, M02, M55, M21 |
| `/api/v1/jurisdiction/{country}/payment-methods` | GET | Available and mandated methods | M20, M50, portals |
| `/api/v1/locales/{locale}` | GET | Locale pack: formats, collation, input methods | All portals, all modules |
| `/api/v1/translations/{locale}/{module}` | GET | **Translation bundle** | All portals, all modules |
| `/api/v1/translations/completeness` | GET | Completeness by module, portal and locale | CI, P03 |
| `/api/v1/entities` | GET/POST | Legal entity register with jurisdiction assignment | P03, M19, M29 |
| `/api/v1/entities/{id}/provision` | POST | **Single-action entity provisioning** | P03 |
| `/api/v1/entities/{id}/fiscal-calendar` | GET | Fiscal year and period structure | M19, M54 |
| `/api/v1/currencies/rates` | GET | Exchange rates with source and date | M19, M20, M44, M50, M54 |
| `/api/v1/consolidation/structure` | GET | Entity roll-up, ownership and method | **M54**, M19 |
| `/api/v1/intercompany/unmatched` | GET | Unmatched intercompany balances blocking close | M19, M54, P03 |
| `/api/v1/country-packs` | GET/POST | Pack authoring, validation and lifecycle | P03 |
| `/api/v1/country-packs/{id}/gate` | POST | **Run the zero-core-change gate** | P03, CI |
| `/api/v1/expansion/readiness/{country}` | GET | Readiness assessment | P03, P06, executive |

---

## 13. Roles & Permissions

| Role | Access | Scope |
|---|---|---|
| R02 Chief Technology Officer | C R U D A | All; approves pack activation and owns the zero-core-change gate |
| R03 Chief Financial Officer | C R U A | Entity lifecycle, fiscal calendars, tax rules, currency, consolidation structure, intercompany, transfer pricing |
| R33 IT / System Administrator | C R U | Pack installation, locale configuration, translation operations; **no certification authority** |
| R26 Finance Manager | R U | Exchange rates, fiscal periods, intercompany matching |
| R27 Finance Officer | R | Rates, obligations, statutory calendar |
| R30 HR Manager | R U | Payroll rules and holiday sets for workforce impact |
| R32 Quality Manager / ISO Coordinator | R | Translation quality, rendering verification, obligation register as ISO evidence |
| R05 Operations Director | R | Holiday sets and working-day impact; branch country assignment |
| R01 Chief Executive Officer | R A | Country pack activation and market entry; expansion readiness |
| All internal users | R | Their own locale; translated content |

**Country lead** *(a role that does not exist in `05-04`)*. Country onboarding requires an
accountable owner per jurisdiction covering obligation discovery, pack authoring coordination
and pilot verification. Currently modelled as a **CTO-delegated grant**; whether it becomes a
distinct role is an open question (Q-08) and an audit action.

**Field-level restrictions.** Transfer-pricing arrangements and arm's-length bases are visible
to R01, R02, R03 and R26 only. Intercompany balances are visible to finance roles and the CTO.

**Segregation of duties.**
- The author of a country pack cannot be its sole certifier; legal and tax review is a separate authority (BRU-GLO-05).
- The translator cannot be the reviewer (BRU-GLO-07).
- Entity provisioning and entity activation require different actors.
- Exchange-rate import is automated; manual rate override requires CFO approval and is separately reported.
- The person who identifies an intercompany elimination cannot be the sole approver of the consolidated result — M54 holds the reciprocal control.

---

## 14. Reports & Analytics

| Report / Dashboard | Audience | Frequency | Key Content |
|---|---|---|---|
| **Translation completeness** | CTO, module owners, Quality Manager | Per build | Completeness by module, portal and locale against the **100% gate**; untranslated and stale keys |
| **Bengali rendering assurance** | CTO, Quality Manager | Per release | Verification results across Android, iOS, Windows, thermal, label and PDF/A output |
| Text expansion and layout | CTO, portal owners | Per release | Truncation and overflow found under pseudo-locale expansion |
| **Country pack register** | CTO, CFO, Legal | On change | Every pack, version, state, components, certification, entities assigned |
| **Statutory obligation calendar** | CFO, M60, owning modules | Monthly | Every obligation by entity: what, to whom, by when, penalty, owner, filing status |
| Jurisdiction rule currency | CFO, Legal | Quarterly | Statutory references with verification dates; stale verifications flagged (mirroring `05-06` §6.1) |
| **Entity register** | CFO, CEO, CTO | On change | Every entity: country, currency, fiscal calendar, pack version, status, provisioning date |
| Entity provisioning performance | CTO, CFO | Per entity | Time from request to active — **against the < 10 day target** |
| **Country onboarding progress** | CEO, CTO, CFO | Weekly during onboarding | Phase, elapsed weeks against the **≤ 12 week target**, core changes required, open gaps |
| **Expansion readiness** | CEO, executive | Quarterly | Per candidate country: pack completeness, translation coverage, integration availability, residency feasibility, recommendation |
| Exchange rate register | Finance Manager, CFO | Daily | Rates by pair with source, type and date; manual overrides |
| **Intercompany and consolidation** | CFO, Finance Manager | Monthly | Intercompany balances, matched and unmatched, elimination candidates, close blockers |
| Transfer-pricing documentation | CFO, Legal, external adviser | Annually | Arrangements, arm's-length bases, documentation completeness |
| Holiday calendar | Operations Director, HR Director | Annually + on confirmation | Published holidays, provisional moon-dependent dates, working-day impact |
| Jurisdiction literal violations | CTO | Per build | Hard-coded jurisdiction values detected and blocked — the design-integrity measure |

---

## 15. KPIs

| KPI ID | Metric | Baseline | W4 Target | W9 Target |
|---|---|---|---|---|
| — | **Bengali translation completeness** | partial | **100%** | **100%** |
| — | **Time to stand up a new legal entity** | not possible | < 15 days | **< 10 days** |
| — | **Time to stand up a new country pack** | not possible | — | **≤ 12 weeks** |
| — | **Core code changes required to install a country pack** | n/a | — | **Zero** |
| — | Jurisdiction literals detected in code | unknown | **Zero** | **Zero** |
| — | Models missing country, currency or locale dimensions | unknown | **Zero** | **Zero** |
| — | Modules released below 100% translation completeness | unknown | **Zero** | **Zero** |
| — | Machine translations reaching release | unknown | **Zero** | **Zero** |
| — | Bengali rendering defects reaching production | unmeasured | **Zero** | **Zero** |
| — | Statutory obligations with a current verification date | 0% | **100%** | **100%** |
| — | Statutory filings missed or late | unknown | **Zero** | **Zero** |
| — | Tax or payroll rate changes requiring a code release | 100% | **Zero** | **Zero** |
| — | Unmatched intercompany balances at period close | n/a | **Zero** | **Zero** |
| — | Exchange rates imported on schedule with provenance | n/a | 99% | **100%** |
| — | Intercompany arrangements with a recorded arm's-length basis | n/a | **100%** | **100%** |

> **Register note.** `_CATEGORY_OVERVIEW.md` §9 names **Bengali translation completeness (100%)**,
> **time to stand up a new legal entity (< 10 days)** and **time to stand up a new country pack
> (≤ 12 weeks)** as the category KPIs owned by M65. **None has a canonical `KPI-0nn`
> identifier** — `06-02` §2.6 ends at KPI-049. **BO-18** in `06-02` §1 carries the country-pack
> target as a business objective without a KPI id. Allocation for all fifteen metrics is an
> audit action.

---

## 16. Delivery

### 16.1 Layer Allocation

| Layer | Component | Coverage |
|---|---|---|
| L1 | Odoo multi-company, `res.currency`, `res.country`, `res.lang`, translation framework | 16% |
| L2 | **OCA `l10n-bangladesh`** (chart of accounts and VAT seed), OCA `operating-unit`, `server-tools` | 10% |
| L5 | `cd_country_pack`, `cd_locale_pack`, `cd_multi_entity` | 74% |

The custom share is high because no vendor or community supplies a Bangladesh pack of the depth
`_CATEGORY_OVERVIEW.md` §8 specifies. OCA `l10n-bangladesh` provides two modules covering the
chart of accounts and basic VAT; the remaining eight pack components are authored.

### 16.2 Custom Development

> ⚠ **CD identifiers in this table are PROVISIONAL and currently collide.** 1 of 3 identifiers below are claimed by another module: **CD-162** also claimed by M20, M45. `CD-` is a programme-wide identifier space; under RG-01 (extended) it must be allocated by `02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md`, which is the sole allocating authority. **Do not create a build backlog item, repository or work package from any identifier in this table until `02-05` has reissued it.** *(Audit finding H2-05; re-verified 2026-08-13 as A3-05.)*

| CD ID | Component | Type | Effort |
|---|---|---|---|
| CD-137 | `cd_country_pack` — pack model and lifecycle, nine-component structure, **zero-core-change gate**, jurisdiction obligation register, tax and payroll rule supply, residency rule supply, address structures, identifier formats, holiday sets, payment method availability, **the Bangladesh reference pack**, country onboarding process | Odoo module + service | 10 PW |
| CD-136 | `cd_locale_pack` — locale model, **Bengali locale with ICU collation and lakh/crore grouping**, translation store and workflow, **completeness gate**, rendering verification, text-expansion testing, locale resolution, localised document output | Odoo module + service | 7 PW |
| **CD-162** | `cd_multi_entity` — entity jurisdiction extension, **single-action entity provisioning**, entity isolation and scoping, fiscal calendars, numbering sequences, currency and exchange rates, intercompany identification and matching, consolidation structure, transfer-pricing documentation, expansion readiness | Odoo module | 6 PW |

> CD-136 `cd_locale_pack` and CD-137 `cd_country_pack` are **reallocated from M30**, where
> `02-05` §5.2 originally placed them. CD-162 is claimed from the extension block for modules
> M31–M67. **All CD IDs remain provisional** pending the unified CD register required by audit
> finding M-01 in `02-05`.

### 16.3 Sequencing

> **M65 is delivered in Wave 9. Its design obligations are Wave 1, and they are not optional.**
> The category risk states that retrofitting multi-country costs 3–5× designing for it. The
> obligations below are therefore **testable requirements on Waves 1–8**, owned by M65 but
> discharged by every module built before it.

| # | Wave 1–8 obligation | Verified by |
|---|---|---|
| **W1-A** | Every relevant model carries `country_id`, `currency_id` and `lang` | Model-registry check in CI, alongside AS-03 (BRU-GLO-03) |
| **W1-B** | **Bangladesh is authored as country pack `BD` v1 from Wave 1** — not as a hard-coded default | Pack existence and consumption test (BRU-GLO-04) |
| **W1-C** | No module contains a jurisdiction literal — no tax rate, address level, holiday, identifier format or currency assumption | Static analysis for jurisdiction literals; **build fails** (BRU-GLO-01, AUT-GLO-20) |
| **W1-D** | Every user-facing string is externalised and translatable | Translation extraction coverage (AS-12) |
| **W1-E** | Translation completeness is 100% for `bn-BD` and `en` at every module's release gate | CI gate (BRU-GLO-06) |
| **W1-F** | All money uses decimal with an explicit currency; the applied rate is stored | Linter rule and financial test suite (AS-10, DI-01) |
| **W1-G** | Bengali rendering is verified on every output surface a module produces | Rendering verification per release |

| Prerequisite for W9 delivery | Reason |
|---|---|
| **M30 Platform Admin (W1)** | The entity, branch and calendar objects M65 extends; holiday sets feed working calendars |
| **M29 Identity (W1)** | Entity isolation record rules; **M29 enforces the residency rules M65 defines** |
| **M64 MDM (W2)** | Jurisdiction reference data is governed master data |
| **M19 Financial Accounting (W3)** | Consumes fiscal calendar, currency and rates; the pilot verifies statutory output |
| **M51 Tax (W4)** | Consumes tax rules; the Bangladesh pack's tax component is proved through M51 |
| **M56 Payroll (W5)** | Consumes payroll rules |
| **M54 FP&A (W6)** | Consolidation execution using M65's roll-up structure and translation rates |
| **M60 GRC (W6)** | Consumes the statutory obligation register |
| Legal and tax advisory per target country | Pack certification requires jurisdiction expertise that must be procured |

> **A second entity may arrive before Wave 9.** The multi-entity capability (`cd_multi_entity`,
> 6 PW) is deliberately separable from the country capability. If a franchise arm, trading
> company or regulated subsidiary is required inside Bangladesh before W9, that component can be
> pulled forward independently. Raised as Q-01.

### 16.4 Data Migration

| Source | Volume | Target Entity | Wave |
|---|---|---|---|
| Bangladesh tax rules and rates | Statutory publications | `fix.jurisdiction.tax.rule` | **W1, authored** (BD pack v1) |
| Bangladesh payroll rules | Labour Act, NBR slabs | `fix.jurisdiction.payroll.rule` | W1–W5, authored |
| Bangladesh administrative geography | 8 divisions, 64 districts, ~495 upazilas | `fix.address.node` | W1, loaded from the official register |
| Public holidays | Annual gazette | `fix.holiday.set` | W1, loaded and maintained annually |
| Existing translations | Partial, inconsistent | `fix.translation.entry` | W1, **assessed then largely re-translated professionally** |
| Statutory obligations | Held in finance and HR knowledge | `fix.jurisdiction.obligation` | W1–W4, **discovered and authored** |
| Currency and exchange rates | Bangladesh Bank / AD bank | `fix.exchange.rate` | W1, connector |
| Legal entity details | 1 entity | `fix.entity.jurisdiction` | W1 |

> **Position on existing translations.** Whatever Bengali strings exist today were produced
> without a review process and to no stated standard. They are **assessed, not trusted**: strings
> passing native-speaker review are retained, the remainder are re-translated. Importing
> unreviewed translations to reach a completeness number quickly would defeat the purpose of the
> gate.
>
> **Position on the obligation register.** The statutory obligation set is **discovered, not
> migrated** — today it lives in the knowledge of the finance and HR teams. Capturing it is a
> multi-week exercise with external advisory input, and it is the highest-value non-software
> deliverable in M65.

---

## 17. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| AC-01 | No module in production contains a jurisdiction literal; the build fails on detection | Static analysis over the full codebase plus a build-failure demonstration |
| AC-02 | Every relevant model carries `country_id`, `currency_id` and `lang` | CI model-registry check plus full-schema assertion |
| AC-03 | Bangladesh operates as country pack `BD`, and disabling the pack demonstrably breaks jurisdiction behaviour | Pack-removal test in a non-production environment |
| AC-04 | Installing a country pack requires zero core code changes | Gate executed on a second, non-Bangladesh pack |
| AC-05 | A pack cannot be activated without all nine components and legal and tax certification | Negative test |
| AC-06 | A module cannot be released below 100% translation completeness for `bn-BD` and `en` | Negative test plus release-gate records |
| AC-07 | A source string change marks its translations stale and reapplies the gate | Scripted scenario |
| AC-08 | Suspected machine translation is flagged and cannot be approved without native-speaker review | Negative test |
| AC-09 | Bengali renders correctly on Android, iOS, Windows, thermal receipt, label printer and PDF/A | Verification set across all six surfaces |
| AC-10 | Bengali sorting uses ICU `bn-BD` and produces correct order for a defined test set | Collation test |
| AC-11 | Amounts display in lakh/crore grouping in the Bengali locale and international grouping in English, without altering the stored value | Formatting test |
| AC-12 | A new legal entity is provisioned end to end in under 10 days, atomically | One real or rehearsed entity provisioning, plus fault-injection rollback test |
| AC-13 | Entity data is isolated by default; cross-entity access requires an explicit, audited grant | Negative test at isolation tier T1 |
| AC-14 | A tax rate change takes effect through a pack version with no code release, and M51 computes correctly against it | End-to-end scenario with M51 |
| AC-15 | A payroll rule change takes effect through a pack version and M56 calculates correctly | End-to-end scenario with M56 |
| AC-16 | M29 enforces a residency rule that M65 defines, and changing the rule changes the enforcement | Integration test with M29 |
| AC-17 | A superseded pack version remains resolvable, and a historical document renders and computes as it did when created | Historical resolution test |
| AC-18 | A moon-dependent holiday confirmed at short notice updates calendars and re-evaluates affected scheduled work without failure | Scripted scenario |
| AC-19 | The exchange rate applied to a transaction is stored with source and date and is never re-derived | Negative test |
| AC-20 | Unmatched intercompany balances block period close | Negative test with M19 |
| AC-21 | Every intercompany arrangement records an arm's-length basis | Full-population assertion |
| AC-22 | The statutory obligation register is complete for Bangladesh, verified with dates, and consumed by M60, M51 and M56 | Register review with Legal and CFO sign-off |
| AC-23 | A country onboarding completes within 12 weeks with zero core code changes | **The Wave 9 gate**: one full onboarding executed end to end |
| AC-24 | Layouts across all 12 portals remain usable under text expansion | Pseudo-locale layout test per portal |
| AC-25 | CTO, CFO and CEO sign off UAT and the Wave 9 expansion gate | Signed UAT and gate records |

**Definition of done:** all 15 criteria in `02_Architecture/02-02` §7 plus the 25 criteria above.

---

## 18. Open Questions

| # | Question | Owner | Needed By |
|---|---|---|---|
| Q-01 | **Is a second Bangladeshi legal entity expected before Wave 9** — a franchise arm, trading company or regulated subsidiary? If so, `cd_multi_entity` (6 PW) must be pulled forward independently of the country capability. | CEO / CFO | **W3** |
| Q-02 | **Which expansion market is first, and when?** India, Myanmar and Nepal are identified through their payment gateways, but the pack authoring effort, legal advisory cost and residency analysis differ substantially between them. | CEO / CFO | W7 |
| Q-03 | **Who authors the Bangladesh statutory obligation register**, and is external tax and legal advisory budgeted? This is the highest-value non-software deliverable and it cannot be produced internally. | CFO / Legal | **W1 minus 1 month** |
| Q-04 | Is professional Bengali translation budgeted at the volume required — roughly 20,000 strings across 67 modules and 12 portals — and is a provider selected? | CTO / CFO | **W1 minus 2 months** |
| Q-05 | What is the retention obligation for a closed entity's records in each jurisdiction, and does it exceed the general retention schedule in M24? | Legal / CFO | W9 |
| Q-06 | Do the expansion markets' data protection regimes permit the split-residency architecture, or does each require its own resident store? This multiplies infrastructure cost per country and interacts with **M29 Q-01** and **M29 Q-05**. | Legal / CTO | W8 |
| Q-07 | Is the chart of accounts a shared global structure with local mapping, or a separate structure per country? The Oracle/NetSuite pattern favours the former; the answer determines consolidation complexity in M54. | CFO | W3 |
| Q-08 | **Is Country Lead a distinct role in `05-04`**, or a CTO-delegated grant? Country onboarding needs an accountable owner per jurisdiction. | HR Director / CTO | W8 |
| Q-09 | How are moon-dependent holidays handled operationally when confirmation arrives with 24–48 hours' notice and technician schedules, SLAs and rosters are already committed? | Operations Director / HR Director | W1 build |
| Q-10 | Does 1000FiX intend to franchise, and if so does the franchise operate as a separate legal entity, a separate branch, or a partner under M40? The entity model must accommodate the answer. | CEO / CCO | W7 |

---

## 19. References

**Internal**
`_CATEGORY_OVERVIEW.md` §2, §6 (boundary map — **M30 owns structure, M65 adds the country
dimension**), §7 promises 5 and 7, **§8 (the country pack specification, the Bangladesh
reference pack, the ≤ 12 week gate, and the India/Myanmar/Nepal expansion markets)**,
§9 (category KPIs), §11 (**the 3–5× retrofit risk**) ·
`M30_Platform_Administration_and_Configuration.md` §3.2, §16.3 (**the W9 hand-off of locale,
country pack and translation**) · `M29_Identity_Access_and_Information_Security.md`
(**M65 defines residency rules; M29 enforces them**) ·
`M64_Master_Data_Management_and_Configuration.md` (governed change process for jurisdiction data) ·
`M28_Integration_API_and_Event_Platform.md` (distribution, connectors) ·
`M51` Tax & Regulatory Compliance *(Category G — computes and files)* ·
`M56` Payroll, Benefits & Statutory Compliance *(Category H — calculates)* ·
`M54` Cost Accounting, Budgeting & FP&A *(Category G — consolidates)* ·
`M19` Financial Accounting & General Ledger *(Category G — fiscal calendar and currency)* ·
`M60` Governance, Risk & Compliance *(Category I — consumes the obligation register)* ·
`02_Architecture/02-01_ERP_Module_Architecture_and_System_Map.md` §8 (**the eight-dimension
model and isolation tiers**), §10 (AS-03, AS-10, AS-11, AS-12) ·
`02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3 (OCA `l10n-bangladesh`),
§5.2 (CD-136, CD-137 reallocated from M30) ·
`05_Cross_Cutting_Specifications/05-06_NonFunctional_Requirements_and_Standards.md`
**§9 (the full localisation standard)**, NFR-016, NFR-059, NFR-074, NFR-086, NFR-099, NFR-100,
§6.1 (regulatory currency and the verified-on discipline), §6.2, AS-10, AS-11, AS-12, DI-01 ·
`05_Cross_Cutting_Specifications/05-02_Data_Model_and_Entity_Catalogue.md` §M30
(`fix.locale.pack`, `fix.country.pack`, `fix.translation.entry` — **reallocated to M65**) ·
`05_Cross_Cutting_Specifications/05-03_Integration_and_API_Catalogue.md` §2.1 (INT-008), §8 (W9 integrations) ·
`06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md` **BO-18** ·
`04_Portals_and_Applications/04-00_Portal_Suite_Overview.md`

**Workspace evidence**
`1000FiX_Services_Company_Profile.md` §Future Outlook, §Growth Initiatives ·
`ERP system for 1000 fix/1000FiX_ERP_System_Comprehensive_BRD.md` (localisation requirements)

**External benchmark and regulatory basis**
[Microsoft Dynamics 365 localisation — country packs manage tax and legal requirements without modifying the core system](https://www.saglobal.com/int/insights/microsoft-dynamics-localization-guide.html) ·
[ERP for international expansion — multi-country operations](https://ecosire.com/blog/international-expansion-erp) ·
[ERP framework for multi-country operations — architecture guide](https://medium.com/@dynamicnetsoft/erp-framework-for-multi-country-operations-the-complete-architecture-guide-64b795408a2f) ·
[NetSuite multi-entity accounting — legal entity per country, chart of accounts with local mapping, consolidation](https://www.anchorgroup.tech/blog/netsuite-multi-entity-accounting) ·
[Global ERP — multi-entity, multi-currency and local tax](https://www.business-software.com/blog/global-erp-done-right-multi-entity-multi-currency-and-local-tax-without-the-headache/) ·
[Global ERP implementation — multi-country rollout strategy](https://sysgenpro.com/resources/global-erp-implementation-multi-country-rollout-strategy-explained-complete-guide-2026) ·
[Bangladesh Personal Data Protection Act 2026 — localisation narrowed to restricted and CII data](https://www.security.land/bangladesh-data-protection-law-localization/) ·
[Bangladesh cross-border data transfer regulation — ITIF](https://itif.org/publications/2025/05/16/bangladesh-cross-border-data-transfer-regulation/) ·
ICU / CLDR internationalisation standards — `bn-BD` collation and formatting ·
Bangladesh VAT and Supplementary Duty Act 2012 · Bangladesh Labour Act 2006 ·
OCA `l10n-bangladesh`

---

*Module M65 · Category K · 1000FiX ERP System v2.0 · CONFIDENTIAL*
