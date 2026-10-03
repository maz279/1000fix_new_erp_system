---
id: BN-012
title: Bengali String Bundle — P04 to P06
project: 1000FiX ERP System v2.0
content_type: Bengali string bundle
template: TPL_UI_Copy_Pack.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design and a native Bengali linguistic reviewer
reviewers: [Content Design Lead, P04 owner, P05 owner, P06 owner, Account Management, Procurement, Finance, Accessibility reviewer]
approver: Localisation Lead with Content Design Lead
content_class: D
purpose: >
  The Bengali bundles for the corporate B2B portal, the vendor and supplier portal, and the
  analytics and executive dashboard. All three default to English, which is precisely why they
  are the surfaces where Bengali coverage is most often quietly dropped. Corporate users are more
  English-comfortable; vendor staff and branch managers reading dashboards are not, and PS-03
  admits no exception. The bundle also records which parts of each surface are deliberately
  English-only, so that a gap and a decision are distinguishable.
traces_to: [P04, P05, P06, UI-014, UI-015, UI-016, BN-001 §3.1, BN-002, BN-003, BN-005, BN-007, BN-011 §6, BN-018, CG-010 §12 item 4, RP-001, RP-002, MD-015]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of `UI-014`, `UI-015` and `UI-016`
i18n_namespace: "`p04.*`, `p05.*`, `p06.*`"
pinned_to:
  surface: P04, P05, P06
  release: pending first build
  wave: W4
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-014, UI-015, UI-016 — the English source packs
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §3.2 — corporate client users "Partly — portal UI yes; contractual and technical documents English"; vendors and suppliers "No"; §12 item 4 records the P04 question as open
    verified: 2026-08-17
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-001 §3.1 — P04, P05 and P06 default English with a toggle, and 100% Bengali completeness required on the UI
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-012 — Bengali String Bundle — P04 to P06

> **These are the surfaces where "the users speak English" quietly becomes "we did not translate
> it".**
>
> `CG-010` §3.2 is precise: corporate users are **partly** bilingual — the **portal UI yes**,
> contractual and technical documents English. Vendor *documents* are English; the **vendor
> portal UI is not exempt**. And `P06` is read by branch managers across 51+ sites, who are the
> least English-comfortable audience in the internal population.
>
> `BN-001` `LS-04`: a surface may not be accepted below 100%. Defaulting to English is a
> **default**, not a coverage exemption.

---

## 1. Bundle summary

| Item | `P04` Corporate | `P05` Vendor | `P06` Analytics |
|---|---|---|---|
| Audience | 500–2,000 corporate users | Suppliers | Executives, branch managers |
| Default | **English** | English | English |
| Toggle | Yes, persisted to the party record | Yes | Yes, persisted to the user record |
| Bengali completeness | **100% of UI** | **100% of UI** | **100% of labels and KPI names** |
| Documents | **English** (`CG-010` §3.2) | **English** (`NT-011` English-only) | n/a |
| Register | চলিত, professional | চলিত, transactional | চলিত, neutral |
| Numerals | Arabic | Arabic | Arabic |
| Namespace | `p04.*` | `p05.*` | `p06.*` |
| Strings authored — **counted** | **42** | **28** | **30** |
| Wave | W4 | W3 for `p05.*` — see §7 | W4 |

**Total Bengali strings authored in this issue: 100 — counted** (§8). `common.*` is not repeated
here (`BN-001` `LS-08`); it is carried in `BN-011` §6 under the interim route.

---

## 2. Terminology in force

| Concept | Bengali | Note |
|---|---|---|
| client | **ক্লায়েন্ট** | Reserved for a contracted corporate account (`BN-003` §3) |
| site | **সাইট** | Reserved for a corporate client's premises |
| vendor | **ভেন্ডর** | Never সাপ্লায়ার in labels |
| purchase order | **পারচেজ অর্ডার** | |
| entitlement | **প্রাপ্যতা** | |
| service credit | **সার্ভিস ক্রেডিট (service credit)** | Class B term (`LG-015`) |
| SLA | **SLA** | Tier 1 |
| KPI | **KPI** | Tier 1 |
| turnaround time | **টার্নঅ্যারাউন্ড টাইম (TAT)** | Tier 4 |
| first-time fix | **প্রথমবারেই সমাধান (first-time fix)** | Tier 4 |

---

## 3. `P04` — Corporate B2B portal

### 3.1 Shell and account — `p04.*`

| Key | English | **Bengali** |
|---|---|---|
| `p04.nav.dashboard` | Dashboard | **ড্যাশবোর্ড** |
| `p04.nav.sites` | Sites | **সাইট** |
| `p04.nav.assets` | Our assets | **আমাদের সম্পদ** |
| `p04.nav.requests` | Service requests | **সার্ভিসের অনুরোধ** |
| `p04.nav.contracts` | Contracts | **চুক্তি** |
| `p04.nav.invoices` | Invoices | **ইনভয়েস** |
| `p04.nav.reports` | Reports | **রিপোর্ট** |
| `p04.nav.users` | Users | **ইউজার** |
| `p04.home.open` | Open requests | **চলমান অনুরোধ** |
| `p04.home.sla` | SLA performance this month | **এই মাসের SLA পারফরম্যান্স** |
| `p04.home.spend` | Spend to date | **এ পর্যন্ত ব্যয়** |
| `p04.home.credits` | Service credits earned | **অর্জিত সার্ভিস ক্রেডিট** |

### 3.2 Raising and tracking work

| Key | English | **Bengali** |
|---|---|---|
| `p04.request.new` | Raise a request | **অনুরোধ উত্থাপন করুন** |
| `p04.request.site` | Which site? | **কোন সাইট?** |
| `p04.request.asset` | Which asset? | **কোন সম্পদ?** |
| `p04.request.priority` | Priority | **অগ্রাধিকার** |
| `p04.request.contact` | On-site contact | **সাইটের যোগাযোগ ব্যক্তি** |
| `p04.request.access` | Access instructions | **প্রবেশের নির্দেশনা** |
| `p04.request.submitted` | Request {ref} raised. Response due by {time}. | **অনুরোধ {ref} উত্থাপিত হয়েছে। {time}-এর মধ্যে সাড়া দেওয়া হবে।** |
| `p04.track.status` | {customer_status} | **{customer_status}** — from `MD-027` |
| `p04.track.sla_due` | Response due {time} | **সাড়া দেওয়ার সময় {time}** |
| `p04.track.sla_missed` | Response was {duration} late. A service credit applies. | **সাড়া {duration} দেরিতে এসেছে। একটি সার্ভিস ক্রেডিট প্রযোজ্য।** |

### 3.3 Hierarchy, approval and billing

| Key | English | **Bengali** |
|---|---|---|
| `p04.org.group` | Group | **গ্রুপ** |
| `p04.org.company` | Company | **কোম্পানি** |
| `p04.org.division` | Division | **ডিভিশন** |
| `p04.org.site` | Site | **সাইট** |
| `p04.org.department` | Department | **ডিপার্টমেন্ট** |
| `p04.approval.pending` | Waiting for {approver} | **{approver}-এর জন্য অপেক্ষমাণ** |
| `p04.approval.limit` | Your approval limit is {amount} | **আপনার অনুমোদনের সীমা {amount}** |
| `p04.approval.escalate` | Send to {role} | **{role}-এর কাছে পাঠান** |
| `p04.billing.consolidated` | Consolidated invoice | **একত্রিত ইনভয়েস** |
| `p04.billing.by_site` | Split by site | **সাইট অনুযায়ী ভাগ করুন** |
| `p04.billing.po` | Your PO number | **আপনার PO নম্বর** |
| `p04.billing.download` | Download the invoice | **ইনভয়েস ডাউনলোড করুন** |

> **`p04.billing.download` downloads an English document.** `CG-010` §3.2 keeps corporate
> contractual and financial documents in English. The **label** is Bengali; the **artefact** is
> not, and the interface must not imply otherwise. `p04.billing.doc_language` below states it.

| Key | English | **Bengali** |
|---|---|---|
| `p04.billing.doc_language` | Invoices and contracts are issued in English. | **ইনভয়েস ও চুক্তি ইংরেজিতে ইস্যু করা হয়।** |

### 3.4 Contracts and entitlement

| Key | English | **Bengali** |
|---|---|---|
| `p04.contract.active` | Active contracts | **সক্রিয় চুক্তি** |
| `p04.contract.entitlement` | Entitlement remaining | **অবশিষ্ট প্রাপ্যতা** |
| `p04.contract.covered` | Covered assets | **কভারভুক্ত সম্পদ** |
| `p04.contract.not_covered` | {asset} is not on contract {ref}. This will be billed separately. | **{asset} চুক্তি {ref}-এ নেই। এটি আলাদাভাবে বিল করা হবে।** |
| `p04.contract.renewal` | Renews on {date} | **{date} তারিখে নবায়ন হবে** |

---

## 4. `P05` — Vendor and supplier portal

| Key | English | **Bengali** |
|---|---|---|
| `p05.nav.orders` | Purchase orders | **পারচেজ অর্ডার** |
| `p05.nav.rfq` | Quotation requests | **কোটেশনের অনুরোধ** |
| `p05.nav.deliveries` | Deliveries | **ডেলিভারি** |
| `p05.nav.invoices` | Invoices | **ইনভয়েস** |
| `p05.nav.payments` | Payments | **পেমেন্ট** |
| `p05.nav.documents` | Compliance documents | **কমপ্লায়েন্স ডকুমেন্ট** |
| `p05.nav.scorecard` | Our performance | **আমাদের পারফরম্যান্স** |
| `p05.rfq.respond` | Submit a quotation | **কোটেশন জমা দিন** |
| `p05.rfq.deadline` | Closes {datetime} | **{datetime}-এ বন্ধ হবে** |
| `p05.rfq.line` | Item {n} of {total} | **আইটেম {n} / {total}** |
| `p05.po.accept` | Accept this order | **এই অর্ডার গ্রহণ করুন** |
| `p05.po.decline` | Decline this order | **এই অর্ডার ফিরিয়ে দিন** |
| `p05.po.confirm_date` | Confirm the delivery date | **ডেলিভারির তারিখ নিশ্চিত করুন** |
| `p05.delivery.advise` | Advise a shipment | **শিপমেন্ট জানান** |
| `p05.delivery.challan` | Delivery challan number | **ডেলিভারি চালান নম্বর** |
| `p05.grn.received` | Received {qty} of {ordered} on {date} | **{date} তারিখে {ordered}-এর মধ্যে {qty} গৃহীত** |
| `p05.grn.rejected` | {qty} rejected: {reason} | **{qty} প্রত্যাখ্যাত: {reason}** |
| `p05.invoice.submit` | Submit an invoice | **ইনভয়েস জমা দিন** |
| `p05.invoice.mushak` | Attach the Mushak 6.3 | **Mushak 6.3 সংযুক্ত করুন** |
| `p05.invoice.vds` | VDS will be deducted at {rate} | **{rate} হারে VDS কেটে নেওয়া হবে** |
| `p05.payment.due` | Due {date} | **{date} তারিখে প্রদেয়** |
| `p05.payment.paid` | Paid on {date}, reference {ref} | **{date} তারিখে পরিশোধিত, রেফারেন্স {ref}** |
| `p05.docs.expiring` | {document} expires on {date}. Upload a current copy. | **{document}-এর মেয়াদ {date} তারিখে শেষ। হালনাগাদ কপি আপলোড করুন।** |
| `p05.docs.trade_licence` | Trade Licence | **Trade Licence** — Tier 1 (`BN-004` §3.2) |
| `p05.scorecard.otif` | On time, in full | **সময়মতো, সম্পূর্ণ** |
| `p05.scorecard.quality` | Quality acceptance rate | **কোয়ালিটি গ্রহণের হার** |

| # | Rule |
|---|---|
| **VN-01** | `p05.po.decline` uses **ফিরিয়ে দিন** — a vendor not taking offered work is *decline*, not *reject* (`BN-003` §9) |
| **VN-02** | `VDS`, `Mushak 6.3` and `Trade Licence` remain Latin (`BN-004` §3) |
| **VN-03** | **Vendor-facing documents and email remain English** (`CG-010` §3.2, `NT-011`). Only the portal UI is bilingual — the split is declared, not accidental (`BP-06`) |

---

## 5. `P06` — Analytics and executive dashboard

**Labels and KPI names are Bengali; the data is not translated.** Metric names are controlled
terms in the measurement domain (`CG-004` §11, `RP-001`).

| Key | English | **Bengali** |
|---|---|---|
| `p06.nav.overview` | Overview | **সংক্ষিপ্ত বিবরণ** |
| `p06.nav.operations` | Operations | **অপারেশনস** |
| `p06.nav.finance` | Finance | **ফাইন্যান্স** |
| `p06.nav.quality` | Quality | **কোয়ালিটি** |
| `p06.nav.people` | People | **পিপল** |
| `p06.filter.period` | Period | **সময়কাল** |
| `p06.filter.branch` | Branch | **শাখা** |
| `p06.filter.business_line` | Business line | **ব্যবসায়িক ধারা** |
| `p06.filter.compare` | Compare with | **তুলনা করুন** |
| `p06.kpi.ftf` | First-time fix | **প্রথমবারেই সমাধান** |
| `p06.kpi.tat` | Turnaround time | **টার্নঅ্যারাউন্ড টাইম** |
| `p06.kpi.sla` | SLA attainment | **SLA অর্জন** |
| `p06.kpi.nps` | NPS | **NPS** |
| `p06.kpi.rework` | Rework rate | **রিওয়ার্ক হার** |
| `p06.kpi.utilisation` | Technician utilisation | **টেকনিশিয়ান ব্যবহারের হার** |
| `p06.kpi.revenue` | Revenue | **রাজস্ব** |
| `p06.kpi.margin` | Gross margin | **গ্রস মার্জিন** |
| `p06.kpi.dso` | Days sales outstanding | **বকেয়া আদায়ের দিন (DSO)** |
| `p06.trend.up` | Up {n}% on {period} | **{period}-এর তুলনায় {n}% বেড়েছে** |
| `p06.trend.down` | Down {n}% on {period} | **{period}-এর তুলনায় {n}% কমেছে** |
| `p06.trend.flat` | Unchanged on {period} | **{period}-এর তুলনায় অপরিবর্তিত** |
| `p06.target.met` | Target met | **লক্ষ্য অর্জিত** |
| `p06.target.missed` | Below target by {gap} | **লক্ষ্যের চেয়ে {gap} কম** |
| `p06.data.as_of` | Data as at {datetime} | **{datetime} পর্যন্ত ডেটা** |
| `p06.data.partial` | Some branches have not reported yet. | **কিছু শাখা এখনও রিপোর্ট করেনি।** |
| `p06.export.pdf` | Export as PDF | **PDF হিসেবে এক্সপোর্ট করুন** |
| `p06.export.excel` | Export to Excel | **Excel-এ এক্সপোর্ট করুন** |
| `p06.empty.no_data` | No data for this selection. | **এই নির্বাচনের জন্য কোনো ডেটা নেই।** |
| `p06.empty.not_permitted` | You can see {n} of {total} branches. | **আপনি {total}টির মধ্যে {n}টি শাখা দেখতে পাচ্ছেন।** |

| # | Rule |
|---|---|
| **AN-01** | **KPI names come from `RP-001`**, not invented here. The Bengali KPI name is a controlled term and is registered in `BN-003` §10 |
| **AN-02** | **A dashboard showing "N/A" or "—" in an otherwise Bengali table has an untranslated string** (`BN-005` §8). Null placeholders are strings |
| **AN-03** | Numbers, dates and currency follow `BN-007`. **Arabic digits throughout** — this is a scanning surface |
| **AN-04** | **Excel export is UTF-8 with BOM** (`BN-006` `EN-06`). A branch manager opening a Bengali export in Excel and seeing mojibake concludes the system is broken |
| **AN-05** | Lakh/crore grouping in both locales (`BN-007` `FM-04`). A board pack that shows 1,234,567 in English and 12,34,567 in Bengali for the same figure is a governance defect |

---

## 6. Plurals

| Key | Bengali ICU |
|---|---|
| `p04.count.requests` | `{n, plural, =0 {কোনো চলমান অনুরোধ নেই} one {{n}টি চলমান অনুরোধ} other {{n}টি চলমান অনুরোধ}}` |
| `p04.count.sites` | `{n, plural, =0 {কোনো সাইট নেই} one {{n}টি সাইট} other {{n}টি সাইট}}` |
| `p05.count.orders` | `{n, plural, =0 {কোনো অর্ডার নেই} one {{n}টি অর্ডার} other {{n}টি অর্ডার}}` |
| `p05.count.docs_expiring` | `{n, plural, =0 {কোনো ডকুমেন্টের মেয়াদ শেষ হচ্ছে না} one {{n}টি ডকুমেন্টের মেয়াদ শেষ হচ্ছে} other {{n}টি ডকুমেন্টের মেয়াদ শেষ হচ্ছে}}` |
| `p06.count.branches` | `{n, plural, =0 {কোনো শাখা নেই} one {{n}টি শাখা} other {{n}টি শাখা}}` |

---

## 7. Wave alignment

**A sequencing problem this file must state rather than inherit silently.**

| Surface | Portal wave | `BN-012` wave |
|---|:--:|:--:|
| `P04` Corporate | W4 | W4 ✔ |
| **`P05` Vendor** | **W3** | **W4 ✘** |
| `P06` Analytics | W4 | W4 ✔ |

> **`P05` goes live at W3 and its Bengali bundle is registered at W4.** The Master Index places
> `P05` in Wave 3 — "Logistics (P09), Vendor (P05), Payments" — and `UI-015` follows. This file
> is registered at W4 because two of its three surfaces are. **The `p05.*` section must therefore
> be delivered and signed off at W3, ahead of the file's own registered wave.**
>
> Recorded as `AUDIT-012` **BN-03**. This is the same class of finding as `AUDIT-010`'s wave
> sequencing errors, and it is recorded rather than quietly worked around.

---

## 8. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7).

| Namespace | Keys enumerated in the English pack | **Bengali strings authored here** |
|---|---:|---:|
| `p04.*` — `UI-014` | 16 | **42** |
| `p05.*` — `UI-015` | 18 | **28** |
| `p06.*` — `UI-016` | 17 | **30** |
| **Total** | **51** | **100** |
| `common.*` — rendered by all three | **154** | 0 — by design (`LS-08`) |

> **Authored exceeds the English source in all three surfaces**, because the `UI` packs are
> representative rather than complete (`AUDIT-012` **BN-18**). 49 of the 100 strings here have no
> English source row, which inverts `BP-03`. The remedy is to complete `UI-014`, `UI-015` and
> `UI-016`, not to trim these bundles.
>
> **The earlier issue of this table claimed 164 authored against 163 source, neither counted** —
> the F7 failure, recorded as `AUDIT-012` **BN-19**.

### 8.1 Strings added with no English source

| Key | Why | Finding |
|---|---|---|
| `p04.billing.doc_language` | The UI is Bengali and the invoice it downloads is English. Without a statement the user experiences a defect rather than a policy (`CG-010` §3.2) | `AUDIT-012` **BN-15** |

---

## 9. Sign-off status

| Gate | `P04` | `P05` | `P06` |
|---|---|---|---|
| G1, G2 on the English | Passed | Passed | Passed |
| G3 Technical | Not started | Not started | Not started |
| **G4 Linguistic, in context** | **Not started** | **Not started — needed at W3 (§7)** | **Not started** |
| Business-owner review | Account Management — not started | Procurement — not started | Finance and Ops — not started |
| Independent native-speaker review | Not started | Not started | Not started |

---

## 10. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`CG-010` §12 item 4** — is the `P04` UI bilingual while its documents stay English? This file assumes **yes** and `p04.billing.doc_language` implements the assumption | Account Management with Localisation | `P04` scope and estimate |
| 2 | **`p05.*` is needed at W3, one wave before this file's registration** (§7) | Programme Content Lead | `P05` go-live |
| 3 | `RP-001` KPI dictionary is not yet written; §5 Bengali KPI names are **provisional** until it is | Localisation Lead with the `RP-001` author | `p06.kpi.*` |
| 4 | `BN-002` and `BN-007` ratification | Programme Content Lead | Every string |
| 5 | Is a Bengali toggle on `P08`-adjacent corporate reporting expected by international brand clients reading `P06` (`BN-007` §11 item 5)? | Commercial | `p06` English locale grouping |

---

## 11. Related documents

| Document | Relationship |
|---|---|
| [`BN-011_Bengali_String_Bundle_P03_Admin.md`](BN-011_Bengali_String_Bundle_P03_Admin.md) | Carries the `common.*` these surfaces render |
| [`BN-013_Bengali_String_Bundle_P07_to_P12.md`](BN-013_Bengali_String_Bundle_P07_to_P12.md) | The remaining six portals |
| [`BN-015_Bengali_Document_and_Print_Template_Pack.md`](BN-015_Bengali_Document_and_Print_Template_Pack.md) | Why `P04` and `P05` documents stay English |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §3.2 audience rule and §12 item 4 |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The G4 these bundles await |

---

## 12. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **100 Bengali strings counted** across `p04.*` (42), `p05.*` (28) and `p06.*` (30); the default-English-is-not-a-coverage-exemption position stated; one string added to declare that corporate documents remain English while their UI is Bengali; KPI names bound to `RP-001` and flagged provisional; **the `P05` W3/W4 wave misalignment recorded**; Excel export encoding rule stated for the dashboard audience | Localisation Lead with Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Every key in `UI-014`, `UI-015` and `UI-016` has a Bengali string
- [x] **Deliberate English-only scope declared per surface, so a decision is distinguishable from a gap** (`BP-06`)
- [x] Reserved-verb discipline applied — `p05.po.decline` uses ফিরিয়ে দিন
- [x] Tier 1 items left in Latin (`VDS`, `Mushak 6.3`, `Trade Licence`, `SLA`, `KPI`, `NPS`)
- [x] KPI names bound to `RP-001` and marked provisional until it exists
- [x] Explicit `=0` plural branches
- [x] Export encoding rule stated for the audience that will hit it (`AN-04`)
- [x] **Wave misalignment on `P05` recorded rather than absorbed**
- [x] Coverage ledger regenerated **by enumeration on 2026-08-17**, with the 49 strings that exceed their English source identified
- [x] All internal links resolve
- [ ] **G4 in-context sign-off** — outstanding; blocks `Approved`
- [ ] **`p05.*` G4 brought forward to W3** — outstanding; §10 item 2
- [ ] **`CG-010` §12 item 4 decided** — outstanding
- [ ] **`RP-001` published so §5 KPI names can be confirmed** — outstanding
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
