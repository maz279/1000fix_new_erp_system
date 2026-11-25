# Bengali (bn_BD) UI Terminology Glossary

**Applies to**: every `addons/**/cd_*/i18n/bn_BD.po` (Odoo field labels, selection values, menus, actions, view terms)
**Requirements**: TR-07, DoD-08, AS-12, DE-17; measured by FF-25 / FF-24 (`tooling/fitness/check_translations.py`)
**Status**: DRAFT. The strings added on 22 October 2026 still need a native-speaker review (see section 6)
**Last Updated**: 22 October 2026

---

## 1. Purpose

The ERP is used in Bangladesh by front-desk staff, technicians, finance staff and
corporate customers. A label has to read the same way on every screen. When a
module translates *Technician* one way and the module next to it uses another word,
users see two different words for one thing. This glossary is the single
reference for translators and reviewers. It was built from the existing
`bn_BD.po` files, and where those files disagreed it fixes one canonical choice.

## 2. Style rules

| Rule | Example |
|---|---|
| Use standard colloquial Bengali (চলিত ভাষা). Never mix it with archaic literary forms (সাধু, e.g. *হইতে*). | From → **থেকে**, not হইতে |
| Keep acronyms, codes and statutory form IDs in Latin script, exactly as in the source. | VAT, BIN, TIN, e-TIN, NBR, TDS, SKU, OTP, IMEI, SLA, QC, GL, KYC, NID, BEFTN, PF, CAPA, PPE, RMA, ESD, DIFE, CFO, UTM, PII, SoD, FOB, GMV, ETA, TTL, JSON, SHA-256, `Mushak 9.1` |
| Keep product, brand and system names in Latin script. | 1000FiX, Odoo, OCA, Keycloak, Mayan, Dell, HP, Samsung, Walton |
| Keep internal register codes in Latin script. | M23, M24, R-nn, NFR-056, GV-005, AUD-2026-001 |
| Write money as **টাকা** for BDT. | Monthly Rent (BDT) → মাসিক ভাড়া (টাকা) |
| Use Bengali digits for plain quantities and legal citations. Keep ASCII digits inside codes and identifiers. | Aged > 30 Days → ৩০ দিনের বেশি পুরনো; (0-1) → (০-১); ITA 2023 §52 → আয়কর আইন ২০২৩ ধারা ৫২; but `UN 1219`, `EAN-13` |
| Mark a collection (One2many/Many2many) label with the suffix **-সমূহ**. | Repair Benches → মেরামত বেঞ্চসমূহ |
| Render language tags as (বাংলা) and (ইংরেজি). | Name (Bengali) → নাম (বাংলা) |
| A bilingual source label (`English / বাংলা`) translates to the Bengali part only, normalised to this glossary. | Operating Unit / অপারেটিং ইউনিট → পরিচালন ইউনিট |
| Translate a Boolean label as a statement, never as a question. | Is Statutory → সংবিধিবদ্ধ |
| Do not mark entries `fuzzy`. Odoo ignores fuzzy entries, and FF-24 counts only a non-empty `msgstr`. | — |

## 3. Core terms (canonical)

| English | বাংলা | Notes |
|---|---|---|
| Service Order | সার্ভিস অর্ডার | |
| Work Order | ওয়ার্ক অর্ডার | |
| Field Order | ফিল্ড অর্ডার | |
| Technician | টেকনিশিয়ান | Not কারিগর (harmonised) |
| Assigned Technician | নিয়োজিত টেকনিশিয়ান | |
| Customer | গ্রাহক | |
| Branch | শাখা | |
| Operating Unit | পরিচালন ইউনিট | |
| Entity (legal) | প্রতিষ্ঠান | Parent Entity → মূল (প্যারেন্ট) প্রতিষ্ঠান |
| Company | কোম্পানি | |
| Party | পার্টি | Parties → পার্টিসমূহ |
| Partner | পার্টনার | |
| Vendor / Supplier | ভেন্ডর / সরবরাহকারী | |
| Seller (marketplace) | বিক্রেতা | |
| Employee / Worker | কর্মী / শ্রমিক | শ্রমিক is used in statutory HSE and labour-law contexts |
| Department | বিভাগ | |
| Position (HR) | পদ | |
| Invoice | চালান | NBR usage is চালানপত্র. Treasury challan → ট্রেজারি চালান |
| Bill | বিল | |
| Warranty | ওয়ারেন্টি | |
| Device | ডিভাইস | |
| Part / Spare Part | যন্ত্রাংশ / খুচরা যন্ত্রাংশ | Older strings use পার্টস (see section 5) |
| Serial Number | সিরিয়াল নম্বর | |
| Stock / Inventory | মজুদ / ইনভেন্টরি | On Hand → হাতে থাকা |
| Warehouse / Location | গুদাম / অবস্থান | |
| Reorder Point / Safety Stock | রি-অর্ডার পয়েন্ট / নিরাপত্তা মজুদ | |
| Consumption | ব্যবহার | |
| Workshop / Bench / Job | ওয়ার্কশপ / বেঞ্চ / জব | |
| Repair / Rework | মেরামত / পুনঃকাজ | |
| Fault / Defect | ত্রুটি | |
| Evidence | প্রমাণ | |
| Document | দলিল | Repo-established. নথি also appears (see section 5) |
| Certificate | সনদ | Withholding certificate → উৎসে কর কর্তন প্রত্যয়নপত্র |
| Status / State | অবস্থা | |
| Type / Kind | ধরন | |
| Category | শ্রেণি | Older strings use বিভাগ (see section 5) |
| Reference / Ref | রেফারেন্স | Legacy Reference → লিগ্যাসি রেফারেন্স |
| Notes | নোট | |
| Reason / Justification | কারণ / যৌক্তিকতা | |
| Date / Timestamp / … At | তারিখ / টাইমস্ট্যাম্প / …-এর সময় | Started At → শুরুর সময় |
| Period (accounting/payroll) | পিরিয়ড | Not পর্যায় (harmonised) |
| Fiscal Year | অর্থবছর | |
| From / To (range) | থেকে / পর্যন্ত | Valid From / Valid To → বৈধতা শুরুর তারিখ / বৈধতার শেষ তারিখ |
| Amount / Quantity | পরিমাণ | Repo-established for both |
| Count | সংখ্যা | |
| Cost (operational) / Cost (accounting) | খরচ / ব্যয় | Standard Cost → আদর্শ ব্যয় |
| Price / Fee / Rate | মূল্য / ফি / হার | Daily/Monthly Rate (rental) → দৈনিক/মাসিক ভাড়া |
| Discount | ছাড় | |
| Total / Subtotal / Grand Total | মোট / উপমোট / সর্বমোট | |
| Gross / Net | মোট (গ্রস) / নিট | |
| Payable | প্রদেয় | |
| Payout / Settlement | পরিশোধ / নিষ্পত্তি | Payout Run → পরিশোধ চক্র |
| Reconciliation | সমন্বয় | Bare label → হিসাব সমন্বয় |
| Variance | তারতম্য | |
| Account (GL) / Account (customer) | হিসাব / অ্যাকাউন্ট | Bank Account No → ব্যাংক হিসাব নম্বর |
| Ledger / General Ledger | খতিয়ান / সাধারণ খতিয়ান | |
| Consolidation / Consolidated | একত্রীকরণ / একত্রিত | |
| Elimination (inter-company) | বাদকরণ | Inter-Company → আন্তঃকোম্পানি |
| Withholding / TDS | উৎসে কর কর্তন / TDS | |
| Taxpayer | করদাতা | |
| Nil Return | শূন্য রিটার্ন | |
| Statutory | সংবিধিবদ্ধ | Not সাংবিধানিক ("constitutional") |
| Compliance | কমপ্লায়েন্স | GRC context. See section 5 |
| Obligation / Control / Risk | বাধ্যবাধকতা / নিয়ন্ত্রণ | Risk → ঝুঁকি |
| Audit / Finding | নিরীক্ষা / পর্যবেক্ষণ | |
| Incident / Accident / Injury | ঘটনা / দুর্ঘটনা / আঘাত | |
| Inspection / Inspector | পরিদর্শন / পরিদর্শক | |
| Dispute / Arbitration | বিরোধ / সালিশ | |
| Quote / Quotation | কোটেশন | |
| Loyalty / Points / Tier / Voucher | লয়ালটি / পয়েন্ট / টায়ার / ভাউচার | Redeem → রিডিম |
| Campaign / Segment | প্রচারণা / দর্শক বিভাগ | |
| Rental / Deposit | ভাড়া / জামানত | |
| Trade-In / Refurbishment | ট্রেড-ইন / রিফার্বিশমেন্ট (রিফার্ব) | |
| Consignment | কনসাইনমেন্ট | |
| Dispatch / Route / Zone / Geofence | ডিসপ্যাচ / রুট / জোন / জিওফেন্স | |
| Priority / Scheduled | অগ্রাধিকার / নির্ধারিত | |
| Approved By / Requested By / Prepared By | অনুমোদনকারী / অনুরোধকারী / প্রস্তুতকারী | Use the agent-noun pattern -কারী for any "… By" label |
| Buttons (actions) | imperative with করুন / দিন | Start Diagnosis → ডায়াগনোসিস শুরু করুন; Cancel → বাতিল করুন; Submit to NBR → NBR-এ জমা দিন |
| Draft / Pending / In Progress / Done | খসড়া / অপেক্ষমাণ / চলমান / সম্পন্ন | Awaiting X → X-এর অপেক্ষায় |
| Open / Closed (state) | খোলা / বন্ধ | Not চালু (harmonised) |
| Cancelled / Rejected / Failed | বাতিলকৃত / প্রত্যাখ্যাত / ব্যর্থ | QC fail → অনুত্তীর্ণ |
| Severity: Critical / Major / Minor | সংকটজনক / গুরুতর / সামান্য | Low / Medium / High → নিম্ন / মাঝারি / উচ্চ; Urgent → জরুরি |
| Risk scales (1-5) | নগণ্য, সামান্য, মাঝারি, গুরুতর, মারাত্মক / বিপর্যয়কর | Likelihood: বিরল, অসম্ভাব্য, সম্ভব, সম্ভাব্য, প্রায় নিশ্চিত |
| Grade A–E | গ্রেড A–E | Like New → নতুনের মতো; For Parts → যন্ত্রাংশের জন্য |
| Placeholder text (e.g. …) | যেমন … | Keep sample codes, brands and model numbers as they are |
| Weekdays | রবিবার … শনিবার | |

## 4. Existing entries harmonised on 22 October 2026

These `msgstr` values were changed in the existing files, either for consistency
or because they were wrong:

- *Technician* কারিগর → টেকনিশিয়ান; *Technician Scorecard* → টেকনিশিয়ান স্কোরকার্ড; *Assigned Technician* (three variants) → নিয়োজিত টেকনিশিয়ান.
- *Legacy Reference* পূর্ববর্তী → লিগ্যাসি রেফারেন্স; *Parties* পক্ষসমূহ → পার্টিসমূহ; *Period / Period Close / Period End* পর্যায় → পিরিয়ড.
- *Evidence Pack* → প্রমাণ প্যাক; *Evidence Reference* → প্রমাণের রেফারেন্স; *Vendor Invoice* → ভেন্ডর চালান; *Reported Fault* → রিপোর্টকৃত ত্রুটি; *Parts Consumed* → ব্যবহৃত যন্ত্রাংশ.
- Fixed errors: *Deliver-to Branch* (typo ডেলিভি), *Statutory Notice* (সাংবিধানিক = "constitutional"), *Ordered* (অর্ডিত is not a word), *YTD Taxable Outside This Slip* (garbled), *To* (প্রতি means "per").
- Archaic হইতে replaced in *From*, *Since*, *Valid From*, *Generated From*, *Valid To*.
- Replaced 13 untranslated placeholders of the form `<English> (বাংলা)` (two of them written as literal `ব…` escape sequences). These were module and menu titles such as *Governance, Risk & Compliance* → গভর্নেন্স, ঝুঁকি ও কমপ্লায়েন্স.
- Second pass: *Open* চালু → খোলা; *Critical* সংকটাপন্ন → সংকটজনক; *Degraded* খারাপ → অবনমিত; *Healthy* সুস্থ → স্বাভাবিক; *Reported* প্রতিবেদনকৃত → রিপোর্টকৃত; *Settled* নিষ্পত্তি → নিষ্পত্তিকৃত; *CAPA Open* → CAPA খোলা; *Mark Delivered* → ডেলিভারি সম্পন্ন চিহ্নিত করুন. The collection labels *Leads*, *Incentives* and *Repair Orders* now end in -সমূহ.

## 5. Open points for the native-speaker review

1. **Acronym script.** Older strings transliterate some acronyms: ভ্যাট, মুশক, এনবিআর, এসকেইউ, কিউসি, জিএল, এসএলএ, বিইএফটিএন, এএমসি, এনসিআর. New strings keep them in Latin script (section 2). Pick one rule and convert the rest.
2. **Category.** Older strings use বিভাগ, which collides with *Division* and *Department*. New strings use শ্রেণি.
3. **Document.** দলিল often reads as "deed" in Bangladesh. Some source labels already say নথি. Consider moving to নথি repository-wide.
4. **Parts.** পার্টস (cd_service_order) or যন্ত্রাংশ (new strings and the catalogue).
5. **Compliance.** The older *Compliance Inspection* string uses সম্মতি, which is also the word for *Consent*. New GRC strings use কমপ্লায়েন্স. পরিপালন (Bangladesh Bank usage) is an alternative.
6. **Facility.** The older strings use সুবিধা (amenity sense). স্থাপনা may read better for a physical site.
7. **Others:** *Zones* অঞ্চলসমূহ vs *Zone* জোন; *Standard Cost* প্রচলিত ব্যয় (older) vs আদর্শ ব্যয় (new); *Amount* and *Quantity* both render as পরিমাণ.

## 6. Native-speaker review: files

There were two passes on 22 October 2026. Both need review.

### 6.1 First pass: field labels

932 entries added and 40 existing entries harmonised. Review in this order, largest first:

| Module | File | New | Harmonised |
|---|---|---|---|
| `cd_inventory` | `addons/domain/e_supply_chain/cd_inventory/i18n/bn_BD.po` | 74 | 1 |
| `cd_workshop` | `addons/domain/a_service_delivery/cd_workshop/i18n/bn_BD.po` | 67 | 3 |
| `cd_settlement_ext` | `addons/domain/g_finance/cd_settlement_ext/i18n/bn_BD.po` | 60 | 0 |
| `cd_field_service` | `addons/domain/a_service_delivery/cd_field_service/i18n/bn_BD.po` | 59 | 0 |
| `cd_loyalty` | `addons/domain/b_customer_engagement/cd_loyalty/i18n/bn_BD.po` | 59 | 0 |
| `cd_multi_entity` | `addons/platform/cd_multi_entity/i18n/bn_BD.po` (new file) | 56 | 0 |
| `cd_marketplace` | `addons/domain/d_circular/cd_marketplace/i18n/bn_BD.po` | 51 | 1 |
| `cd_hse` | `addons/domain/h_people/cd_hse/i18n/bn_BD.po` | 44 | 1 |
| `cd_service_order` | `addons/domain/a_service_delivery/cd_service_order/i18n/bn_BD.po` | 43 | 1 |
| `cd_grc` | `addons/domain/i_governance/cd_grc/i18n/bn_BD.po` | 41 | 1 |
| `cd_rental_asset` | `addons/domain/d_circular/cd_rental_asset/i18n/bn_BD.po` | 26 | 1 |
| `cd_storefront` | `addons/domain/b_customer_engagement/cd_storefront/i18n/bn_BD.po` | 24 | 0 |
| `cd_gl_ext` | `addons/domain/g_finance/cd_gl_ext/i18n/bn_BD.po` | 23 | 3 |
| `cd_tax_engine_bd` | `addons/domain/g_finance/cd_tax_engine_bd/i18n/bn_BD.po` | 23 | 1 |
| `cd_data_case` | `addons/domain/d_circular/cd_data_case/i18n/bn_BD.po` | 22 | 1 |
| `cd_tradein` | `addons/domain/d_circular/cd_tradein/i18n/bn_BD.po` | 22 | 1 |
| `cd_payroll_bd` | `addons/domain/h_people/cd_payroll_bd/i18n/bn_BD.po` | 18 | 1 |
| `cd_knowledge` | `addons/domain/i_governance/cd_knowledge/i18n/bn_BD.po` | 14 | 1 |
| `cd_talent` | `addons/domain/h_people/cd_talent/i18n/bn_BD.po` | 14 | 1 |
| `cd_hr_core` | `addons/domain/h_people/cd_hr_core/i18n/bn_BD.po` | 12 | 0 |
| `cd_dynamic_pricing` | `addons/domain/c_commercial/cd_dynamic_pricing/i18n/bn_BD.po` | 11 | 0 |
| `cd_facility` | `addons/domain/f_asset_facilities/cd_facility/i18n/bn_BD.po` | 11 | 0 |
| `cd_metric_registry` | `addons/domain/j_data_analytics/cd_metric_registry/i18n/bn_BD.po` | 11 | 0 |
| `cd_ppm` | `addons/domain/i_governance/cd_ppm/i18n/bn_BD.po` | 11 | 0 |
| `cd_attendance` | `addons/domain/h_people/cd_attendance/i18n/bn_BD.po` | 10 | 0 |
| `cd_billing_engine` | `addons/domain/g_finance/cd_billing_engine/i18n/bn_BD.po` | 10 | 0 |
| `cd_mdm_core` | `addons/platform/cd_mdm_core/i18n/bn_BD.po` | 10 | 0 |
| `cd_campaign` | `addons/domain/b_customer_engagement/cd_campaign/i18n/bn_BD.po` | 9 | 0 |
| `cd_device_registry` | `addons/domain/a_service_delivery/cd_device_registry/i18n/bn_BD.po` | 9 | 2 |
| `cd_ewaste` | `addons/domain/d_circular/cd_ewaste/i18n/bn_BD.po` | 8 | 0 |
| `cd_import_order` | `addons/domain/e_supply_chain/cd_import_order/i18n/bn_BD.po` | 8 | 1 |
| `cd_partner` | `addons/domain/b_customer_engagement/cd_partner/i18n/bn_BD.po` | 8 | 1 |
| `cd_stream_registry` | `addons/domain/j_data_analytics/cd_stream_registry/i18n/bn_BD.po` | 8 | 0 |
| `cd_entity_config` | `addons/platform/cd_entity_config/i18n/bn_BD.po` | 7 | 2 |
| `cd_fpa` | `addons/domain/g_finance/cd_fpa/i18n/bn_BD.po` | 7 | 1 |
| `cd_demand_plan` | `addons/domain/e_supply_chain/cd_demand_plan/i18n/bn_BD.po` | 6 | 1 |
| `cd_party_master` | `addons/platform/cd_party_master/i18n/bn_BD.po` | 6 | 1 |
| `cd_document_core` | `addons/platform/cd_document_core/i18n/bn_BD.po` | 4 | 2 |
| `cd_itsm` | `addons/domain/i_governance/cd_itsm/i18n/bn_BD.po` | 3 | 1 |
| `cd_msp_contract` | `addons/domain/a_service_delivery/cd_msp_contract/i18n/bn_BD.po` | 3 | 1 |
| `cd_warranty_claims` | `addons/domain/a_service_delivery/cd_warranty_claims/i18n/bn_BD.po` | 3 | 0 |
| `cd_cash_position` | `addons/domain/g_finance/cd_cash_position/i18n/bn_BD.po` | 2 | 0 |
| `cd_contact_centre` | `addons/domain/b_customer_engagement/cd_contact_centre/i18n/bn_BD.po` | 2 | 0 |
| `cd_equipment_register` | `addons/domain/f_asset_facilities/cd_equipment_register/i18n/bn_BD.po` | 2 | 0 |
| `cd_qms_process` | `addons/domain/i_governance/cd_qms_process/i18n/bn_BD.po` | 2 | 0 |
| `cd_ap_ext` | `addons/domain/g_finance/cd_ap_ext/i18n/bn_BD.po` | 1 | 1 |
| `cd_catalogue` | `addons/platform/cd_catalogue/i18n/bn_BD.po` | 1 | 0 |
| `cd_competency` | `addons/domain/h_people/cd_competency/i18n/bn_BD.po` | 1 | 1 |
| `cd_contract_core` | `addons/domain/c_commercial/cd_contract_core/i18n/bn_BD.po` | 1 | 0 |
| `cd_cx_feedback` | `addons/domain/b_customer_engagement/cd_cx_feedback/i18n/bn_BD.po` | 1 | 0 |
| `cd_fixed_asset_ext` | `addons/domain/g_finance/cd_fixed_asset_ext/i18n/bn_BD.po` | 1 | 0 |
| `cd_front_desk` | `addons/domain/a_service_delivery/cd_front_desk/i18n/bn_BD.po` | 1 | 1 |
| `cd_performance` | `addons/domain/h_people/cd_performance/i18n/bn_BD.po` | 1 | 1 |
| `cd_vehicle_ext` | `addons/domain/f_asset_facilities/cd_vehicle_ext/i18n/bn_BD.po` | 1 | 1 |

Fourteen more `bn_BD.po` files have no new strings. `cd_rate_card` and `cd_requisition` each have 2 harmonised entries. The other 12 changed format only (section 7) and need no review: `cd_consignment`, `cd_corporate_portal`, `cd_crm_ext`, `cd_employee_core`, `cd_esignature`, `cd_event_outbox`, `cd_quotation`, `cd_rbac_ext`, `cd_subscription`, `cd_vendor_portal`, `cd_wms_structure` and `cd_workflow_engine`.

### 6.2 Second pass: every template string

1,897 entries were added: 1,629 distinct strings across 63 modules, and 11 existing entries were harmonised (section 4). They cover selection values, buttons, page and group titles, placeholders, menus and actions. `cd_p03_portal` got its first `bn_BD.po`.

| Module | File | New |
|---|---|---|
| `cd_p03_portal` | `addons/platform/cd_p03_portal/i18n/bn_BD.po` (new file) | 281 |
| `cd_marketplace` | `addons/domain/d_circular/cd_marketplace/i18n/bn_BD.po` | 89 |
| `cd_grc` | `addons/domain/i_governance/cd_grc/i18n/bn_BD.po` | 80 |
| `cd_workshop` | `addons/domain/a_service_delivery/cd_workshop/i18n/bn_BD.po` | 67 |
| `cd_service_order` | `addons/domain/a_service_delivery/cd_service_order/i18n/bn_BD.po` | 66 |
| `cd_hse` | `addons/domain/h_people/cd_hse/i18n/bn_BD.po` | 63 |
| `cd_multi_entity` | `addons/platform/cd_multi_entity/i18n/bn_BD.po` | 62 |
| `cd_inventory` | `addons/domain/e_supply_chain/cd_inventory/i18n/bn_BD.po` | 57 |
| `cd_settlement_ext` | `addons/domain/g_finance/cd_settlement_ext/i18n/bn_BD.po` | 57 |
| `cd_field_service` | `addons/domain/a_service_delivery/cd_field_service/i18n/bn_BD.po` | 53 |
| `cd_loyalty` | `addons/domain/b_customer_engagement/cd_loyalty/i18n/bn_BD.po` | 51 |
| `cd_party_master` | `addons/platform/cd_party_master/i18n/bn_BD.po` | 49 |
| `cd_device_registry` | `addons/domain/a_service_delivery/cd_device_registry/i18n/bn_BD.po` | 47 |
| `cd_gl_ext` | `addons/domain/g_finance/cd_gl_ext/i18n/bn_BD.po` | 42 |
| `cd_payroll_bd` | `addons/domain/h_people/cd_payroll_bd/i18n/bn_BD.po` | 42 |
| `cd_tradein` | `addons/domain/d_circular/cd_tradein/i18n/bn_BD.po` | 38 |
| `cd_data_case` | `addons/domain/d_circular/cd_data_case/i18n/bn_BD.po` | 33 |
| `cd_mdm_core` | `addons/platform/cd_mdm_core/i18n/bn_BD.po` | 31 |
| `cd_entity_config` | `addons/platform/cd_entity_config/i18n/bn_BD.po` | 30 |
| `cd_storefront` | `addons/domain/b_customer_engagement/cd_storefront/i18n/bn_BD.po` | 30 |
| `cd_rental_asset` | `addons/domain/d_circular/cd_rental_asset/i18n/bn_BD.po` | 29 |
| `cd_cx_feedback` | `addons/domain/b_customer_engagement/cd_cx_feedback/i18n/bn_BD.po` | 26 |
| `cd_facility` | `addons/domain/f_asset_facilities/cd_facility/i18n/bn_BD.po` | 26 |
| `cd_talent` | `addons/domain/h_people/cd_talent/i18n/bn_BD.po` | 26 |
| `cd_tax_engine_bd` | `addons/domain/g_finance/cd_tax_engine_bd/i18n/bn_BD.po` | 26 |
| `cd_document_core` | `addons/platform/cd_document_core/i18n/bn_BD.po` | 25 |
| `cd_front_desk` | `addons/domain/a_service_delivery/cd_front_desk/i18n/bn_BD.po` | 25 |
| `cd_campaign` | `addons/domain/b_customer_engagement/cd_campaign/i18n/bn_BD.po` | 24 |
| `cd_catalogue` | `addons/platform/cd_catalogue/i18n/bn_BD.po` | 24 |
| `cd_knowledge` | `addons/domain/i_governance/cd_knowledge/i18n/bn_BD.po` | 24 |
| `cd_billing_engine` | `addons/domain/g_finance/cd_billing_engine/i18n/bn_BD.po` | 23 |
| `cd_ewaste` | `addons/domain/d_circular/cd_ewaste/i18n/bn_BD.po` | 21 |
| `cd_hr_core` | `addons/domain/h_people/cd_hr_core/i18n/bn_BD.po` | 21 |
| `cd_contract_core` | `addons/domain/c_commercial/cd_contract_core/i18n/bn_BD.po` | 19 |
| `cd_metric_registry` | `addons/domain/j_data_analytics/cd_metric_registry/i18n/bn_BD.po` | 19 |
| `cd_stream_registry` | `addons/domain/j_data_analytics/cd_stream_registry/i18n/bn_BD.po` | 19 |
| `cd_subscription` | `addons/domain/c_commercial/cd_subscription/i18n/bn_BD.po` | 18 |
| `cd_ppm` | `addons/domain/i_governance/cd_ppm/i18n/bn_BD.po` | 16 |
| `cd_attendance` | `addons/domain/h_people/cd_attendance/i18n/bn_BD.po` | 15 |
| `cd_itsm` | `addons/domain/i_governance/cd_itsm/i18n/bn_BD.po` | 15 |
| `cd_rbac_ext` | `addons/platform/cd_rbac_ext/i18n/bn_BD.po` | 14 |
| `cd_consignment` | `addons/domain/e_supply_chain/cd_consignment/i18n/bn_BD.po` | 13 |
| `cd_contact_centre` | `addons/domain/b_customer_engagement/cd_contact_centre/i18n/bn_BD.po` | 13 |
| `cd_event_outbox` | `addons/platform/cd_event_outbox/i18n/bn_BD.po` | 13 |
| `cd_partner` | `addons/domain/b_customer_engagement/cd_partner/i18n/bn_BD.po` | 12 |
| `cd_requisition` | `addons/domain/e_supply_chain/cd_requisition/i18n/bn_BD.po` | 12 |
| `cd_workflow_engine` | `addons/domain/i_governance/cd_workflow_engine/i18n/bn_BD.po` | 12 |
| `cd_cash_position` | `addons/domain/g_finance/cd_cash_position/i18n/bn_BD.po` | 10 |
| `cd_quotation` | `addons/domain/c_commercial/cd_quotation/i18n/bn_BD.po` | 9 |
| `cd_warranty_claims` | `addons/domain/a_service_delivery/cd_warranty_claims/i18n/bn_BD.po` | 9 |
| `cd_ap_ext` | `addons/domain/g_finance/cd_ap_ext/i18n/bn_BD.po` | 8 |
| `cd_dynamic_pricing` | `addons/domain/c_commercial/cd_dynamic_pricing/i18n/bn_BD.po` | 8 |
| `cd_crm_ext` | `addons/domain/b_customer_engagement/cd_crm_ext/i18n/bn_BD.po` | 7 |
| `cd_employee_core` | `addons/platform/cd_employee_core/i18n/bn_BD.po` | 7 |
| `cd_msp_contract` | `addons/domain/a_service_delivery/cd_msp_contract/i18n/bn_BD.po` | 7 |
| `cd_esignature` | `addons/platform/cd_esignature/i18n/bn_BD.po` | 6 |
| `cd_import_order` | `addons/domain/e_supply_chain/cd_import_order/i18n/bn_BD.po` | 6 |
| `cd_wms_structure` | `addons/domain/e_supply_chain/cd_wms_structure/i18n/bn_BD.po` | 6 |
| `cd_fpa` | `addons/domain/g_finance/cd_fpa/i18n/bn_BD.po` | 4 |
| `cd_rate_card` | `addons/domain/c_commercial/cd_rate_card/i18n/bn_BD.po` | 4 |
| `cd_demand_plan` | `addons/domain/e_supply_chain/cd_demand_plan/i18n/bn_BD.po` | 3 |
| `cd_fixed_asset_ext` | `addons/domain/g_finance/cd_fixed_asset_ext/i18n/bn_BD.po` | 3 |
| `cd_competency` | `addons/domain/h_people/cd_competency/i18n/bn_BD.po` | 2 |

Review first the strings that customers see (storefront, loyalty, front desk, the `cd_p03_portal` navigation), then the statutory wording (`cd_hse` BLA forms, `cd_tax_engine_bd` sections 52–56, `cd_payroll_bd`).

## 7. How Odoo 19 loads these files

These requirements were checked against `vendor/odoo/odoo/tools/translate.py`. The PO format is the part that is easy to break.

- **Every entry needs a `#. module: <module>` comment.** `PoFileReader` runs `re.match("(module[s]?): (\w+)", entry.comment)`. If the comment is missing, it raises `AttributeError` and the language load aborts. Before 22 October 2026, 62 of the 67 `bn_BD.po` files had no such comments, and none of them loaded.
- **An entry is applied only through its `#:` references.** For example:
  - `model:ir.model.fields,field_description:<module>.field_<model_with_underscores>__<field>` for a field label
  - `model:ir.model.fields.selection,name:<module>.selection__<model>__<field>__<value>` for a selection value
  - `model:ir.ui.menu,name:<module>.<menu_xmlid>` for a menu
  - `model:ir.actions.act_window,name:…` for an action
  - `model_terms:ir.ui.view,arch_db:<module>.<view_xmlid>` for a view term

  An entry with no reference is never applied.
- **`i18n/<module>.pot` is merged into the `.po` (polib `merge`).** Odoo takes the comments and references from the `.pot`, and it treats any `.po` entry that is missing from the `.pot` as obsolete. The `.pot` therefore has to be in the same Odoo form and contain every msgid the `.po` translates. `tooling/scripts/extract-translations.py` writes both files in this form: it regenerates the `.pot` and refreshes the `#:` references in `bn_BD.po`, never touching a translation and never adding an empty `msgstr`. `tests/test_extract_translations_odoo_po.py` parses its output with Odoo's own reader. The old one-shot writers (`generate-p06-po.py`, `generate-p07-po.py`, `generate-platform-po.py`, `generate-p09-modules.py`, `generate-p10-support.py`) are retired and exit without writing.
- **Templates are current.** `extract-translations.py --all` regenerated all 69 templates on 22 October 2026, and a re-run changes nothing. FF-24 passes against them: every template string in all 69 `bn_BD.po` files is translated. After changing a label, selection, button or menu, re-run the extractor and translate whatever it reports as untranslated.
- **Wrapped strings.** `check_translations.py` joins gettext continuation lines, so a wrapped `msgid`/`msgstr` (the form Odoo's own export writes) is read correctly. `audit-repo-formats.py` uses the same reader for its PO checks (`tests/test_audit_repo_formats_po.py`).

## 8. The bn_BD language and loading it

- **The language record.** Odoo 19 ships only `bn_IN` (inactive), and for `bn_IN` it reads `bn.po` and `bn_IN.po`. `cd_multi_entity` adds the `bn_BD` record in `data/res_lang_bn_bd.xml` (`cd_multi_entity.lang_bn_BD`, `noupdate`). Its values:
  - name *Bengali (Bangladesh) / বাংলা*; code, iso code and URL code all `bn_BD`; left-to-right
  - date `%d/%m/%Y`, 12-hour time
  - lakh/crore grouping `[3,2,0]`, so 12345678 renders as `1,23,45,678.00` (BN-007)
  - week starting Sunday (the weekend is Friday and Saturday)

  For `bn_BD`, Odoo reads `bn.po` and then `bn_BD.po`, so Odoo's own `base/i18n/bn.po` loads as well.
- **Why an explicit load is needed.** Odoo loads a language's PO files for a module when that module installs or updates. Creating the record therefore covers only the modules installed after `cd_multi_entity` in the same run. On a fresh build, `cd_entity_config` and `cd_event_outbox` had no `bn_BD` terms.
- **Fresh databases.** `tooling/scripts/build-test-db.py` runs `odoo-bin i18n loadlang -l bn_BD` after the install. The old `--i18n-import` and `--i18n-export` server flags no longer exist in Odoo 19; the `i18n` subcommand replaces them. The build fails if any module whose `bn_BD.po` translates field labels ends up with none loaded.
- **Existing databases (fix_dev, staging, …).** Run, from the codebase root:

  ```
  PYTHONPATH=. python vendor/odoo/odoo-bin -c infra/odoo-conf/local.runtime.conf -d fix_dev -u cd_multi_entity --stop-after-init
  PYTHONPATH=. python vendor/odoo/odoo-bin i18n loadlang -c infra/odoo-conf/local.runtime.conf -d fix_dev -l bn_BD
  ```

  Neither command changes any user's language; each user picks Bengali in their preferences.
- **After a translation changes.** `loadlang` and a plain `-u` keep the Bengali terms a database already has. To push edited `msgstr` values, import with overwrite:

  ```
  PYTHONPATH=. python vendor/odoo/odoo-bin i18n import -c infra/odoo-conf/local.runtime.conf -d fix_dev -l bn_BD -w <every addons/**/i18n/bn_BD.po>
  ```

  Alternatively, update the module with `--i18n-overwrite`.
