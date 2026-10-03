---
id: BN-011
title: Bengali String Bundle — P03 Admin
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
reviewers: [Content Design Lead, P03 owner, all fourteen workspace owners, Design System, Accessibility reviewer, Finance for ws.finance, Quality for ws.quality]
approver: Localisation Lead with Content Design Lead
content_class: D
purpose: >
  The Bengali bundle for the admin and operations portal, its fourteen workspaces, and — under
  the BN-001 LS-07 interim route — the shared common.* namespace that every one of the twelve
  portals renders. Branch and back-office staff across 51+ sites are not uniformly comfortable
  working in English, and P03 carries the largest string volume in the system. The common.*
  section exists here because no registered BN file owns it, and because P03 is the earliest
  wave and therefore precedes every consumer of those strings.
traces_to: [P03, UI-013, UI-023, UI-024, UI-025, UI-026, UI-027, UI-028, UI-029, UI-030, UI-031, UI-032, UI-033, UI-034, UI-035, UI-036, UI-002, UI-003, UI-004, UI-005, UI-006, UI-007, UI-008, UI-009, UI-010, UI-041, BN-001 LS-06, BN-001 LS-07, BN-002, BN-003, BN-005, BN-007, BN-018, MD-027]
priority: P1
wave: W1
bilingual: yes
bn_counterpart: self — this file is the Bengali counterpart of `UI-013`, `UI-023`…`UI-036`, and (interim) `UI-002`…`UI-010` and `UI-041`
i18n_namespace: "`p03.*`, `ws.*`, and — interim — `common.*` and `flow.search.*`"
pinned_to:
  surface: P03 and all twelve portals (for `common.*`)
  release: pending first build
  wave: W1
sources:
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-013 and 03C_Admin_Workspaces/UI-023…UI-036 — the English source packs for the portal shell and the fourteen workspaces
    verified: 2026-08-17
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-002…UI-010 — the common.* English packs whose Bengali has no registered owner
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §10 — minimum desktop resolution 1366×768, the common branch hardware
    verified: 2026-08-17
    class: P1
  - source: project_content/11_Localisation_Bengali/BN-001 §4 — the common.* namespace gap, LS-06 and the LS-07 interim route
    verified: 2026-08-17
    class: P1
supersedes: none
review_due: 2027-02-17
---

# BN-011 — Bengali String Bundle — P03 Admin

> **This bundle carries two things, and the second one is not in its title.**
>
> `p03.*` and `ws.*` are its registered scope. **`common.*` is here under the `BN-001` `LS-07`
> interim route**, because no registered `BN` file owns it, because it loads on **every** surface
> in the system, and because `P03` is the W1 wave and therefore reaches it first.
>
> §6 is consequently the most widely consumed section in Category 11. A defect there appears on
> twelve portals at once. When `BN-019` is registered, §6 moves out **whole** and this file keeps
> a pointer (`BN-001` `LS-09`).

---

## 1. Bundle summary

| Item | Value |
|---|---|
| Surface | `P03` — 150–250 agents and back-office users across 51+ branches; plus `common.*` on all twelve portals |
| Locale | **`bn-BD`** |
| Namespace | `p03.*`, `ws.*`, **`common.*` (interim)**, `flow.search.*` (interim) |
| Source packs | `UI-013`; `UI-023`…`UI-036`; **`UI-002`…`UI-010`**; `UI-041` |
| Default on this surface | **Bengali**, English toggle persisted to the user record |
| Framework | Odoo OWL |
| Screen | **1366×768** — the densest surface in the system (`05-06` §10) |
| Register | চলিত, neutral. Full technical vocabulary permitted |
| Address | আপনি / করুন |
| Numerals | **Arabic** — dense tables, financial values, identifiers (`BN-007` §3.3) |
| Sentence budget | ≤ 20 words |
| Strings in this issue | **181 — counted** (`p03.*` 17 · `ws.*` 17 · **`common.*` 138** · `flow.search.*` 9). See §10 |
| Content class | D — User-facing |

---

## 2. Namespace boundary

| Namespace | Owner | Status |
|---|---|---|
| `p03.*` | This file | Registered |
| `ws.*` | This file | Registered |
| **`common.*`** | **This file, §6** | **Interim (`LS-07`)** — moves to `BN-019` on registration |
| `flow.search.*` (`UI-041`) | **This file, §7** | **Interim** — admin-facing flow |
| `flow.booking/estimate/payment/register/consent.*` | `BN-009` | Customer-facing |
| `p01.*`, `p02.*`, `p04.*`…`p12.*` | `BN-009`, `BN-010`, `BN-012`, `BN-013` | Registered |

| # | Rule |
|---|---|
| **NB-01** | **A `common.*` key may exist in exactly one Bengali bundle.** Today that is §6 (`BN-001` `LS-08`) |
| **NB-02** | When `BN-019` is registered, §6 and §7 move **whole**. They are not split, and no portal bundle absorbs a subset (`LS-09`) |
| **NB-03** | Status strings are quoted from `MD-027`, in both the `internal_label_bn` and `customer_label_bn` columns as the surface requires (`BN-003` `ST-02`) |

---

## 3. Terminology in force

`P03` is the surface where the internal vocabulary is used in full (`CG-004` §5 internal column).

| Concept | Bengali (internal) | Customer-facing pair | `BN-003` |
|---|---|---|---|
| branch | **শাখা** | সার্ভিস সেন্টার | §2 |
| service order | সার্ভিস অর্ডার | আমার সার্ভিস | §4 |
| job | জব | — | §4 |
| work order | ওয়ার্ক অর্ডার | — | §4 |
| part | পার্টস | পার্টস | §7 |
| price | **মূল্য** on documents, **দাম** on customer-facing labels | দাম | §6 |
| role | রোল | — | §8 |
| approve / authorise | **অনুমোদন করুন / অথরাইজ করুন** | — | §9 — **the audit-control split** |
| reject / decline | প্রত্যাখ্যান করুন / ফিরিয়ে দিন | — | §9 |
| cancel / void | বাতিল করুন / রদ করুন | — | §9 |
| archive | আর্কাইভ করুন | — | §9 — never মুছে ফেলুন |

---

## 4. Portal shell — `p03.*`

| Key | English | **Bengali** |
|---|---|---|
| `p03.nav.dashboard` | Dashboard | **ড্যাশবোর্ড** |
| `p03.nav.workspaces` | Workspaces | **ওয়ার্কস্পেস** |
| `p03.nav.search` | Search | **সার্চ** |
| `p03.nav.notifications` | Notifications | **নোটিফিকেশন** |
| `p03.nav.approvals` | My approvals | **আমার অনুমোদন** |
| `p03.nav.profile` | My profile | **আমার প্রোফাইল** |
| `p03.nav.branch` | Branch: {branch} | **শাখা: {branch}** |
| `p03.nav.entity` | Entity: {entity} | **আইনি সত্তা: {entity}** |
| `p03.nav.language` | Language | **ভাষা** |
| `p03.nav.signout` | Sign out | **সাইন আউট** |
| `p03.home.today` | Today at {branch} | **{branch}-এ আজ** |
| `p03.home.open_orders` | Open service orders | **চলমান সার্ভিস অর্ডার** |
| `p03.home.sla_risk` | At SLA risk | **SLA ঝুঁকিতে** |
| `p03.home.awaiting_me` | Waiting for you | **আপনার জন্য অপেক্ষমাণ** |
| `p03.home.shift` | Shift {from}–{to} | **শিফট {from}–{to}** |
| `p03.switch.branch` | Change branch | **শাখা পরিবর্তন করুন** |
| `p03.switch.warning` | You are viewing {branch}. Actions apply to that branch. | **আপনি {branch} দেখছেন। কাজগুলো সেই শাখায় প্রযোজ্য হবে।** |

---

## 5. Workspaces — `ws.*`

One representative block per workspace. The full key set is generated from `UI-023`…`UI-036`;
the strings below fix the **vocabulary** each workspace uses.

| Workspace | Key | English | **Bengali** |
|---|---|---|---|
| **Intake** `ws.intake` | `.new` | New intake | **নতুন ইনটেক** |
| | `.device` | Which device? | **কোন ডিভাইস?** |
| | `.symptom` | What did the customer report? | **গ্রাহক কী জানিয়েছেন?** |
| | `.mode` | Delivery mode | **ডেলিভারি মোড** |
| | `.print_receipt` | Print the intake receipt | **ইনটেক রসিদ প্রিন্ট করুন** |
| **Dispatch** `ws.dispatch` | `.board` | Dispatch board | **ডিসপ্যাচ বোর্ড** |
| | `.column.unassigned` | Unassigned | **নির্ধারিত হয়নি** |
| | `.column.sla_risk` | SLA risk | **SLA ঝুঁকি** |
| | `.assign` | Assign a technician | **টেকনিশিয়ান নির্ধারণ করুন** |
| | `.reassign` | Reassign | **পুনরায় নির্ধারণ করুন** |
| **Branch** `ws.branch` | `.queue` | Counter queue | **কাউন্টার সারি** |
| | `.cash` | Cash position | **ক্যাশ অবস্থা** |
| | `.handover` | Shift handover | **শিফট হস্তান্তর** |
| **Workshop** `ws.workshop` | `.wip` | Work in progress | **চলমান কাজ** |
| | `.bench` | Bench assignment | **বেঞ্চ নির্ধারণ** |
| | `.level` | Repair level | **রিপেয়ার লেভেল** |
| **Inventory** `ws.inventory` | `.stock` | Stock on hand | **হাতে থাকা স্টক** |
| | `.transfer` | Stock transfer | **স্টক ট্রান্সফার** |
| | `.count` | Physical count | **ফিজিক্যাল কাউন্ট** |
| | `.van_recon` | Van reconciliation | **ভ্যান রিকনসিলিয়েশন** |
| **Procurement** `ws.procure` | `.requisition` | Requisition | **রিকুইজিশন** |
| | `.rfq` | Request for quotation | **কোটেশনের অনুরোধ** |
| | `.po` | Purchase order | **পারচেজ অর্ডার** |
| | `.grn` | Goods receipt | **গুডস রিসিট** |
| **Finance** `ws.finance` | `.invoice` | Invoice | **ইনভয়েস** |
| | `.mushak` | Mushak 6.3 | **Mushak 6.3** |
| | `.post` | Post to the ledger | **লেজারে পোস্ট করুন** |
| | `.void` | Void this document | **এই ডকুমেন্ট রদ করুন** |
| | `.receipt` | Money receipt | **মানি রসিদ** |
| **HR** `ws.hr` | `.attendance` | Attendance | **উপস্থিতি** |
| | `.leave` | Leave requests | **ছুটির আবেদন** |
| | `.payroll` | Payroll run | **পে-রোল রান** |
| **Quality** `ws.quality` | `.ncr` | Non-conformance | **অসঙ্গতি (NCR)** |
| | `.capa` | CAPA | **CAPA** |
| | `.rework` | Rework cases | **রিওয়ার্ক কেস** |
| | `.audit` | Internal audit | **অভ্যন্তরীণ অডিট** |
| **Contract** `ws.contract` | `.list` | Contracts | **চুক্তি** |
| | `.entitlement` | Entitlement balance | **প্রাপ্যতার ব্যালেন্স** |
| | `.covered` | Covered assets | **কভারভুক্ত ডিভাইস** |
| **Warranty** `ws.warranty` | `.claim` | Claims | **ক্লেইম** |
| | `.rate_card` | Rate card | **রেট কার্ড** |
| | `.evidence` | Claim evidence | **ক্লেইমের প্রমাণ** |
| **Marketplace** `ws.market` | `.sellers` | Sellers | **বিক্রেতা** |
| | `.payout` | Payouts | **পে-আউট** |
| | `.scorecard` | Seller scorecard | **বিক্রেতার স্কোরকার্ড** |
| **Managed services** `ws.msp` | `.estate` | Client estate | **ক্লায়েন্ট এস্টেট** |
| | `.remote` | Remote sessions | **রিমোট সেশন** |
| **System** `ws.system` | `.users` | Users | **ইউজার** |
| | `.roles` | Roles | **রোল** |
| | `.master_data` | Master data | **মাস্টার ডেটা** |
| | `.audit_log` | Audit log | **অডিট লগ** |

| # | Rule |
|---|---|
| **WS-01** | **`ws.finance.void` uses রদ করুন, never বাতিল করুন.** *Void* nullifies a posted financial document; *cancel* ends a record before completion. The distinction is a financial control (`BN-003` §9) |
| **WS-02** | **`ws.dispatch.assign` uses নির্ধারণ করুন, never বরাদ্দ করুন.** *Allocate* is reserved for stock, budget and identifiers |
| **WS-03** | `ws.finance.mushak` is **Tier 1 and untranslated** (`BN-004` §3.1) |
| **WS-04** | Every workspace column header appearing in a report must match the `RP` label for the same measure (`AUDIT_Checklist_Recurring` F2) |

---

## 6. `common.*` — interim, all twelve portals

> **This section is consumed by every surface in the system.** It is here under `LS-07` and moves
> to `BN-019` on registration (`NB-02`). Treat a change here as a change to twelve portals.

### 6.1 Global navigation and actions — `common.action.*`, `common.nav.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.action.save` | Save | **সংরক্ষণ করুন** |
| `common.action.cancel` | Cancel | **বাতিল করুন** |
| `common.action.confirm` | Confirm | **নিশ্চিত করুন** |
| `common.action.approve` | Approve | **অনুমোদন করুন** |
| `common.action.authorise` | Authorise | **অথরাইজ করুন** |
| `common.action.reject` | Reject | **প্রত্যাখ্যান করুন** |
| `common.action.submit` | Submit | **জমা দিন** |
| `common.action.create` | Create | **তৈরি করুন** |
| `common.action.edit` | Edit | **সম্পাদনা করুন** |
| `common.action.archive` | Archive | **আর্কাইভ করুন** |
| `common.action.print` | Print | **প্রিন্ট করুন** |
| `common.action.export` | Export | **এক্সপোর্ট করুন** |
| `common.action.attach` | Attach a file | **ফাইল সংযুক্ত করুন** |
| `common.action.back` | Back | **পেছনে** |
| `common.action.close` | Close | **বন্ধ করুন** |
| `common.action.retry` | Try again | **আবার চেষ্টা করুন** |

### 6.2 Field labels — `common.field.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.field.device.brand` | Brand | **ব্র্যান্ড** |
| `common.field.device.model` | Model | **মডেল** |
| `common.field.device.serial` | Serial number | **সিরিয়াল নম্বর** |
| `common.field.device.imei` | IMEI | **IMEI** |
| `common.field.device.purchase_date` | Purchase date | **কেনার তারিখ** |
| `common.field.amount.value` | Amount | **পরিমাণ** |
| `common.field.amount.discount` | Discount | **ছাড়** |
| `common.field.party.name` | Name | **নাম** |
| `common.field.party.mobile` | Mobile number | **মোবাইল নম্বর** |
| `common.field.party.address` | Address | **ঠিকানা** |
| `common.field.date.from` | From | **থেকে** |
| `common.field.date.to` | To | **পর্যন্ত** |
| `common.field.reason` | Reason | **কারণ** |
| `common.field.notes` | Notes | **নোট** |

### 6.3 Validation and field errors — `common.error.field.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.error.field.required` | This is required. | **এটি আবশ্যক।** |
| `common.error.field.imei_format` | IMEI must be 15 digits. | **IMEI ১৫ সংখ্যার হতে হবে।** |
| `common.error.field.mobile_format` | Enter an 11-digit mobile number starting 01. | **০১ দিয়ে শুরু ১১ সংখ্যার মোবাইল নম্বর দিন।** |
| `common.error.field.bin_format` | BIN must be 13 digits. | **BIN ১৩ সংখ্যার হতে হবে।** |
| `common.error.field.date_format` | Use DD/MM/YYYY. | **DD/MM/YYYY ফরম্যাটে লিখুন।** |
| `common.error.field.date_future` | This date cannot be in the future. | **এই তারিখ ভবিষ্যতের হতে পারে না।** |
| `common.error.field.amount_precision` | Use two decimal places. | **দশমিকের পর দুই ঘর ব্যবহার করুন।** |
| `common.error.field.max_length` | Keep this under {n} characters. | **{n} অক্ষরের মধ্যে রাখুন।** |

> **Every one of these describes the required form rather than the user's mistake**
> (`BN-002` `TN-03`). None says "আপনি ভুল দিয়েছেন".

### 6.4 Business-rule errors — `common.error.srm.*`, `.fin.*`, `.stock.*`, `.approval.*`

| Key | English | **Bengali** | Class |
|---|---|---|:--:|
| `common.error.srm.device_required` | A device must be identified before intake can continue. | **ইনটেক চালিয়ে যেতে আগে ডিভাইস শনাক্ত করতে হবে।** | **H** |
| `common.error.srm.tech_not_certified` | {tech} is not certified for {brand}. Choose another technician. | **{brand} ওয়ারেন্টি কাজের জন্য {tech}-এর সার্টিফিকেশন নেই। অন্য টেকনিশিয়ান বেছে নিন।** | **H** |
| `common.error.srm.parts_unapproved` | Parts cannot be issued until the paid repair is approved. | **পেইড মেরামত অনুমোদিত না হওয়া পর্যন্ত পার্টস ইস্যু করা যাবে না।** | **H** |
| `common.error.srm.qc_not_passed` | The quality checklist has not passed. | **কোয়ালিটি চেকলিস্ট পাস হয়নি।** | **H** |
| `common.error.srm.warranty_inactive` | This device has no active warranty. Continue as a paid repair? | **এই ডিভাইসের সক্রিয় ওয়ারেন্টি নেই। পেইড মেরামত হিসেবে চালিয়ে যাবেন?** | **A** |
| `common.error.srm.not_on_contract` | {device} is not covered by contract {ref}. | **{device} চুক্তি {ref}-এর আওতায় নেই।** | **H** |
| `common.error.srm.rework_flagged` | This is a repeat fault within {days} days. It will be recorded as rework. | **এটি {days} দিনের মধ্যে একই ত্রুটি। এটি রিওয়ার্ক হিসেবে রেকর্ড হবে।** | **S** |
| `common.error.srm.invoice_before_complete` | The job must be complete before invoicing. | **ইনভয়েস করার আগে জব সম্পন্ন হতে হবে।** | **H** |
| `common.error.fin.period_closed` | The accounting period is closed. | **হিসাব সময়কাল বন্ধ।** | **H** |
| `common.error.fin.bin_required` | A BIN is required for this customer before a Mushak 6.3 can be issued. | **Mushak 6.3 ইস্যু করার আগে এই গ্রাহকের BIN প্রয়োজন।** | **H** |
| `common.error.fin.no_tax_class` | {item} has no tax class. Finance must set one. | **{item}-এর কোনো ট্যাক্স ক্লাস নেই। ফাইন্যান্সকে এটি নির্ধারণ করতে হবে।** | **H** |
| `common.error.stock.unavailable` | {part} is not available at {location}. | **{location}-এ {part} নেই।** | **H** |
| `common.error.stock.negative` | This would make stock negative. | **এতে স্টক ঋণাত্মক হয়ে যাবে।** | **H** |
| `common.error.stock.incompatible` | {part} is not compatible with {model}. | **{part} {model}-এর সাথে সামঞ্জস্যপূর্ণ নয়।** | **H** |
| `common.error.stock.hazard_ack` | Confirm you have read the handling steps for {part}. | **{part}-এর হ্যান্ডলিং ধাপ পড়েছেন তা নিশ্চিত করুন।** | **H** |
| `common.error.approval.over_limit` | {amount} is above your limit of {limit}. {approver} must approve it. | **{amount} আপনার {limit} সীমার বেশি। {approver}-কে অনুমোদন করতে হবে।** | **A** |
| `common.error.approval.self` | You cannot approve your own request. | **আপনি নিজের অনুরোধ অনুমোদন করতে পারবেন না।** | **H** |
| `common.error.approval.reason_required` | Record a reason for this override. | **এই ওভাররাইডের কারণ লিখুন।** | **H** |
| `common.error.approval.override_available` | {role} can authorise this. | **{role} এটি অথরাইজ করতে পারেন।** | **A** |

| # | Rule |
|---|---|
| **CE-01** | Class **A** messages **name the authoriser** (`BR-STD-06`). In Bengali the authoriser must be the grammatical subject, not an afterthought |
| **CE-02** | `common.error.approval.override_available` uses **অথরাইজ**, not অনুমোদন — it is an override, and the audit trail must read differently (`BN-003` §9) |

### 6.5 System errors — `common.error.system.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.error.system.unexpected` | Something went wrong at our end. Try again. If it happens again, quote reference {ref}. | **আমাদের প্রান্তে একটি সমস্যা হয়েছে। আবার চেষ্টা করুন। আবার হলে রেফারেন্স {ref} জানান।** |
| `common.error.system.timeout` | That took too long. Your work is saved. Try again. | **এটি অনেক সময় নিয়েছে। আপনার কাজ সংরক্ষিত আছে। আবার চেষ্টা করুন।** |
| `common.error.system.unavailable` | This service is unavailable right now. We are working on it. | **এই সার্ভিসটি এখন পাওয়া যাচ্ছে না। আমরা এটি নিয়ে কাজ করছি।** |
| `common.error.system.conflict` | Someone else changed this while you were working. Review the changes. | **আপনি কাজ করার সময় অন্য কেউ এটি পরিবর্তন করেছেন। পরিবর্তনগুলো দেখুন।** |
| `common.error.system.string_missing` | This text could not be loaded. Refresh the page. If it happens again, quote reference {ref}. | **এই লেখাটি লোড করা যায়নি। পেজ রিফ্রেশ করুন। আবার হলে রেফারেন্স {ref} জানান।** |

### 6.6 Access and session — `common.access.*`, `common.session.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.access.denied_feature` | You do not have access to this. Ask {role} if you need it. | **এটিতে আপনার অ্যাক্সেস নেই। প্রয়োজন হলে {role}-কে বলুন।** |
| `common.access.denied_record` | This record is outside your branch. | **এই রেকর্ডটি আপনার শাখার বাইরে।** |
| `common.access.out_of_scope` | You can see {n} of {total} records. The rest are outside your scope. | **আপনি {total}টির মধ্যে {n}টি রেকর্ড দেখতে পাচ্ছেন। বাকিগুলো আপনার আওতার বাইরে।** |
| `common.access.read_only` | You can view this but not change it. | **আপনি এটি দেখতে পারবেন, পরিবর্তন করতে পারবেন না।** |
| `common.session.expiring` | You will be signed out in {n} minutes. | **{n} মিনিটে আপনি সাইন আউট হয়ে যাবেন।** |
| `common.session.expired` | You were signed out. Sign in again — your work is saved. | **আপনি সাইন আউট হয়েছেন। আবার সাইন ইন করুন — আপনার কাজ সংরক্ষিত আছে।** |

### 6.7 Empty states — `common.empty.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.empty.no_results.search` | Nothing matched "{query}". | **"{query}"-এর সাথে কিছু মেলেনি।** |
| `common.empty.no_results.search_script` | Nothing matched "{query}". Try the other script. | **"{query}"-এর সাথে কিছু মেলেনি। অন্য লিপিতে চেষ্টা করুন।** |
| `common.empty.no_results.filter` | No records match these filters. | **এই ফিল্টারের সাথে কোনো রেকর্ড মেলেনি।** |
| `common.empty.no_results.date` | Nothing in this date range. | **এই তারিখ পরিসরে কিছু নেই।** |
| `common.empty.no_permission.list` | You do not have access to any records here. | **এখানে কোনো রেকর্ডে আপনার অ্যাক্সেস নেই।** |
| `common.empty.not_configured.master_data` | {dataset} has not been set up yet. {role} must configure it. | **{dataset} এখনও সেট আপ করা হয়নি। {role}-কে এটি কনফিগার করতে হবে।** |
| `common.empty.not_configured.zone` | No dispatch zone covers this address. | **এই ঠিকানার জন্য কোনো ডিসপ্যাচ জোন নেই।** |
| `common.empty.not_configured.price_list` | No price list applies to this customer. | **এই গ্রাহকের জন্য কোনো মূল্য তালিকা প্রযোজ্য নয়।** |

> **`common.empty.no_results.search_script` is added here and has no English source row.**
> Bengali users search phonetically and often in the other script (`BN-003` `PS-05`,
> `05-06` NFR-074). An empty result with no suggestion is a dead end that English-language
> testing never encounters. Raised as `AUDIT-012` **BN-14**.

### 6.8 Confirmations and destructive actions — `common.confirm.*`

Consequence before the button, always (`BN-002` `TN-07`).

| Key | English | **Bengali** |
|---|---|---|
| `common.confirm.order.cancel` | Cancelling {ref} stops all work and notifies the customer. Record a reason. | **{ref} বাতিল করলে সব কাজ বন্ধ হবে এবং গ্রাহককে জানানো হবে। কারণ লিখুন।** |
| `common.confirm.order.ber` | Declaring beyond economic repair needs photos and a second technician's confirmation. | **অর্থনৈতিকভাবে অলাভজনক ঘোষণা করতে ছবি এবং দ্বিতীয় একজন টেকনিশিয়ানের নিশ্চিতকরণ প্রয়োজন।** |
| `common.confirm.order.close_no_qc` | Closing without a passed quality checklist will be recorded against this branch. | **কোয়ালিটি চেকলিস্ট পাস ছাড়া বন্ধ করলে তা এই শাখার বিপরীতে রেকর্ড হবে।** |
| `common.confirm.job.reassign` | {tech} will lose this job and {new_tech} will receive it. | **{tech} এই জব হারাবেন এবং {new_tech} এটি পাবেন।** |
| `common.confirm.fin.post` | Posting is permanent. The entry can be reversed but not removed. | **পোস্ট করা স্থায়ী। এন্ট্রি রিভার্স করা যাবে, মুছে ফেলা যাবে না।** |
| `common.confirm.fin.void` | Voiding {ref} nullifies a posted document. This is recorded in the audit log. | **{ref} রদ করলে একটি পোস্ট করা ডকুমেন্ট বাতিল হবে। এটি অডিট লগে রেকর্ড হয়।** |
| `common.confirm.fin.refund` | {amount} will be returned to the customer by {method}. | **{amount} {method}-এর মাধ্যমে গ্রাহককে ফেরত দেওয়া হবে।** |
| `common.confirm.fin.writeoff` | Writing off {amount} removes it from receivables permanently. | **{amount} রাইট-অফ করলে তা স্থায়ীভাবে প্রাপ্য থেকে বাদ যাবে।** |
| `common.confirm.data.archive` | {record} will be hidden from lists. It is not deleted and can be restored. | **{record} তালিকা থেকে লুকানো হবে। এটি মুছে ফেলা হয় না এবং ফিরিয়ে আনা যায়।** |
| `common.confirm.data.merge` | Merging keeps {survivor} and moves everything from {loser}. This cannot be undone. | **মার্জ করলে {survivor} থাকবে এবং {loser}-এর সবকিছু সরে যাবে। এটি ফেরানো যাবে না।** |
| `common.confirm.data.bulk` | This will change {n} records. | **এতে {n}টি রেকর্ড পরিবর্তিত হবে।** |
| `common.confirm.data.revoke` | {user} will lose access immediately. | **{user} সঙ্গে সঙ্গে অ্যাক্সেস হারাবেন।** |
| `common.confirm.override.request` | Ask {role} to authorise this. | **{role}-কে এটি অথরাইজ করতে বলুন।** |
| `common.confirm.override.authorise` | You are authorising an exception to {rule}. Your name is recorded. | **আপনি {rule}-এর একটি ব্যতিক্রম অথরাইজ করছেন। আপনার নাম রেকর্ড হবে।** |

| # | Rule |
|---|---|
| **CF-01** | **Buttons are verbs, never OK/Cancel** (`CG-008` UI-g). The Bengali confirm button repeats the verb: বাতিল করুন, রদ করুন, মার্জ করুন |
| **CF-02** | `common.confirm.data.archive` **states that nothing is deleted** — `05-02` DM-06 archives, never hard-deletes, and the Bengali must not imply otherwise (`BN-003` §9) |

### 6.9 Offline, sync and conflict — `common.offline.*`, `common.conflict.*`

Read on `P02`, `P09` and `P11` after up to 24 hours offline (`PS-08`).

| Key | English | **Bengali** |
|---|---|---|
| `common.offline.banner` | You are offline. You can keep working. | **আপনি অফলাইনে আছেন। আপনি কাজ চালিয়ে যেতে পারেন।** |
| `common.offline.queue` | {n} actions will be sent when you are back online. | **অনলাইনে ফিরলে {n}টি কাজ পাঠানো হবে।** |
| `common.offline.syncing` | Sending your work | **আপনার কাজ পাঠানো হচ্ছে** |
| `common.offline.synced` | Everything is up to date | **সবকিছু আপ টু ডেট** |
| `common.offline.sync_failed` | {n} actions could not be sent. They are safe. Try again or call dispatch. | **{n}টি কাজ পাঠানো যায়নি। সেগুলো নিরাপদে আছে। আবার চেষ্টা করুন বা ডিসপ্যাচকে কল করুন।** |
| `common.conflict.detected` | This changed while you were offline. Choose which version to keep. | **আপনি অফলাইনে থাকার সময় এটি পরিবর্তিত হয়েছে। কোন সংস্করণ রাখবেন বেছে নিন।** |
| `common.conflict.keep_mine` | Keep my version | **আমার সংস্করণ রাখুন** |
| `common.conflict.keep_theirs` | Keep the server version | **সার্ভারের সংস্করণ রাখুন** |
| `common.conflict.both_kept` | Both versions were kept. {role} will review them. | **দুটি সংস্করণই রাখা হয়েছে। {role} সেগুলো পর্যালোচনা করবেন।** |
| `common.conflict.manual` | This needs a person to resolve. Dispatch has been told. | **এটি সমাধানে একজন মানুষ প্রয়োজন। ডিসপ্যাচকে জানানো হয়েছে।** |

| # | Rule |
|---|---|
| **OF-B01** | **Every offline string reassures before it instructs.** "আপনার কাজ নিরাপদে আছে" precedes any action, because the technician's first question is whether the day's work is lost |
| **OF-B02** | These strings are **bundled at build** with the font (`BN-005` `BU-04`, `BU-05`) |
| **OF-B03** | Conflict strings receive the **same G4 in-context treatment as safety copy** (`BN-010` `OF-02`) |

### 6.10 Loading and long-running jobs — `common.loading.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.loading.default` | Loading | **লোড হচ্ছে** |
| `common.loading.slow` | This is taking longer than usual | **এটি স্বাভাবিকের চেয়ে বেশি সময় নিচ্ছে** |
| `common.loading.job_started` | Started. We will tell you when it is done. | **শুরু হয়েছে। শেষ হলে আমরা জানাব।** |
| `common.loading.job_progress` | {done} of {total} done | **{total}টির মধ্যে {done}টি সম্পন্ন** |
| `common.loading.job_done` | Finished. {n} records processed. | **শেষ হয়েছে। {n}টি রেকর্ড প্রক্রিয়া করা হয়েছে।** |
| `common.loading.job_failed` | {n} records could not be processed. Download the error list. | **{n}টি রেকর্ড প্রক্রিয়া করা যায়নি। ত্রুটির তালিকা ডাউনলোড করুন।** |

### 6.11 Accessibility strings — `common.a11y.*`

| Key | English | **Bengali** |
|---|---|---|
| `common.a11y.icon.close` | Close | **বন্ধ করুন** |
| `common.a11y.icon.search` | Search | **সার্চ** |
| `common.a11y.icon.filter` | Filter | **ফিল্টার** |
| `common.a11y.icon.sort` | Sort | **সাজান** |
| `common.a11y.icon.more` | More actions | **আরও অপশন** |
| `common.a11y.icon.expand` | Expand | **বড় করুন** |
| `common.a11y.icon.refresh` | Refresh | **রিফ্রেশ করুন** |
| `common.a11y.icon.scan` | Scan a barcode | **বারকোড স্ক্যান করুন** |
| `common.a11y.icon.torch` | Torch | **টর্চ** |
| `common.a11y.icon.call` | Call | **কল করুন** |
| `common.a11y.icon.navigate` | Navigate | **পথ দেখান** |
| `common.a11y.icon.copy` | Copy | **কপি করুন** |
| `common.a11y.icon.help` | Help | **সহায়তা** |
| `common.a11y.icon.next` | Next | **পরবর্তী** |
| `common.a11y.icon.fullscreen` | Full screen | **ফুল স্ক্রিন** |
| `common.a11y.live.saved` | Saved | **সংরক্ষিত হয়েছে** |
| `common.a11y.live.invalid` | {n} fields need attention | **{n}টি ঘরে সংশোধন প্রয়োজন** |
| `common.a11y.live.results` | {n} results | **{n}টি ফলাফল** |
| `common.a11y.live.status` | Status changed to {status} | **অবস্থা পরিবর্তিত হয়ে {status}** |
| `common.a11y.live.sync` | Sync complete | **সিঙ্ক সম্পন্ন** |
| `common.a11y.live.session` | Session expiring | **সেশনের মেয়াদ শেষ হচ্ছে** |
| `common.a11y.sr.skip` | Skip to main content | **মূল কনটেন্টে যান** |
| `common.a11y.sr.required` | Required | **আবশ্যক** |
| `common.a11y.sr.current` | Current page | **বর্তমান পেজ** |
| `common.a11y.sr.external` | Opens in a new tab | **নতুন ট্যাবে খুলবে** |
| `common.a11y.sr.file` | {type} file, {size} | **{type} ফাইল, {size}** |
| `common.a11y.sr.table` | Table, {rows} rows, {cols} columns | **টেবিল, {rows} সারি, {cols} কলাম** |

| # | Rule |
|---|---|
| **AY-01** | Accessible names are **strings and are translated** (`UI-001` §7, `CG-011` BA-04). An English `aria-label` on a Bengali surface is an untranslated string, not an implementation detail |
| **AY-02** | Live-region text is announced; **it is not read visually and must still be a complete Bengali sentence** |
| **AY-03** | Bengali screen-reader engine limitations are recorded in the accessibility statement, not silently accepted (`CG-011` §8.2, `VB-009` `AC-07`) |

---

## 7. Search, filter and bulk action — `flow.search.*` (interim)

| Key | English | **Bengali** |
|---|---|---|
| `flow.search.placeholder` | Search by reference, mobile, IMEI or name | **রেফারেন্স, মোবাইল, IMEI বা নাম দিয়ে সার্চ করুন** |
| `flow.search.scope` | Searching {scope} | **{scope}-এ সার্চ করা হচ্ছে** |
| `flow.search.filters` | Filters | **ফিল্টার** |
| `flow.search.clear` | Clear filters | **ফিল্টার মুছুন** |
| `flow.search.saved` | Saved views | **সংরক্ষিত ভিউ** |
| `flow.search.select_all` | Select all {n} | **সবগুলো {n}টি নির্বাচন করুন** |
| `flow.search.selected` | {n} selected | **{n}টি নির্বাচিত** |
| `flow.search.bulk` | Apply to selected | **নির্বাচিতগুলোতে প্রয়োগ করুন** |
| `flow.search.export` | Export these results | **এই ফলাফল এক্সপোর্ট করুন** |

| # | Rule |
|---|---|
| **SR-01** | Search accepts **both scripts and phonetic variants** (`BN-003` §14). The placeholder must not imply otherwise |
| **SR-02** | Export produces **UTF-8 with BOM** so that Bengali columns open correctly in Excel on branch machines (`BN-006` `EN-06`) |

---

## 8. Plurals

| Key | Bengali ICU |
|---|---|
| `common.count.results` | `{n, plural, =0 {কোনো ফলাফল নেই} one {{n}টি ফলাফল} other {{n}টি ফলাফল}}` |
| `common.count.selected` | `{n, plural, =0 {কিছু নির্বাচিত নয়} one {{n}টি নির্বাচিত} other {{n}টি নির্বাচিত}}` |
| `common.count.errors` | `{n, plural, =0 {কোনো ত্রুটি নেই} one {{n}টি ঘরে সংশোধন প্রয়োজন} other {{n}টি ঘরে সংশোধন প্রয়োজন}}` |
| `common.count.pending_approvals` | `{n, plural, =0 {কোনো অনুমোদন অপেক্ষমাণ নেই} one {{n}টি অনুমোদন অপেক্ষমাণ} other {{n}টি অনুমোদন অপেক্ষমাণ}}` |
| `common.count.people` | `{n, plural, =0 {কেউ নেই} one {{n} জন} other {{n} জন}}` — **জন for people** (`BN-005` `PL-06`) |

---

## 9. Density and budget — 1366×768

`P03` is the densest surface in the system and Bengali runs 20–40% longer than English.

| Slot | Budget (Bengali) | Risk |
|---|---:|---|
| Table column header | **14** | **Very high** — the tightest slot in the system |
| Status chip | 18 | **High** |
| Toolbar button | 20 | **High** — করুন verbs |
| Nav item | 22 | Medium |
| Dialog title | 45 | Low |
| Field label | 28 | Medium |
| Inline validation | 60 | Medium |
| Confirmation body | 140 | Low |

| # | Rule |
|---|---|
| **DN-B01** | **Table column headers are the first thing to break.** Where the Bengali does not fit at 15px in a dense cell (`VB-009` §3), the column widens or the header wraps to two lines — it is **never** truncated (`VB-007` `BL-04`) |
| **DN-B02** | An abbreviation is **not** the remedy. Bengali has no established abbreviation convention for these terms and an invented one is unreadable (`BN-002` §6) |
| **DN-B03** | Exceeding a budget is a **design conversation** (`VB-006` §8) |
| **DN-B04** | Verified at **1366×768 at 100% and at 125% OS scaling**, which is common on branch hardware |

---

## 10. Coverage ledger

**Counted by enumeration on 2026-08-17** (`CP-11`, `CM-R2`, F7). Both columns are counted.

| Namespace | Keys enumerated in the English packs | **Bengali strings authored here** | Scope |
|---|---:|---:|---|
| `p03.*` — `UI-013` | 15 | **17** | Registered |
| `ws.*` — `UI-023`…`UI-036` | **149** | **17** | Registered — **representative only, §5** |
| **`common.*` — `UI-002`…`UI-010`** | **154** | **138** | **Interim (`LS-07`)** |
| **`flow.search/filter/bulk.*` — `UI-041`** | **18** | **9** | **Interim** |
| **Total** | **336** | **181** | |

**Three corrections and one consequence.**

1. **The earlier issue of this table claimed 350 authored against 350 source. Both were written
   before the enumeration that should have produced them** — the `AUDIT-005` / F7 failure,
   reproduced here. Recorded as `AUDIT-012` **BN-19** rather than quietly fixed.
2. **`ws.*` is 17 of 149 — deliberately representative.** §5 says so in prose: it fixes the
   *vocabulary* each workspace uses, and the full key set is generated from `UI-023`…`UI-036`.
   **132 `ws.*` strings remain unauthored** and the prose and the ledger now agree.
3. **`common.*` is 138 of 154.** The interim scope is **substantially but not wholly** delivered;
   **16 `common.*` strings remain unauthored**, and they load on twelve portals.

> **The consequence for `LS-07`.** 147 of the 181 strings in this file — `common.*` plus
> `flow.*` — are **outside its registered scope**. That is the measured size of the `BN-001` §4
> gap, and it is what moves to `BN-019` on registration (`NB-02`). Recording it as a number now
> means the move is a known quantity rather than a discovery.

**One string authored with no English source:** `common.empty.no_results.search_script` —
`AUDIT-012` **BN-14**.

---

## 11. Sign-off status

| Gate | Required | Status |
|---|:--:|---|
| G1, G2 on the English | ● | Passed |
| G3 Technical | ● | **Not started — no build** |
| **G4 Linguistic, in context, at 1366×768** | **●** | **Not started. Unwaivable** |
| Workspace-owner review — fourteen owners | ● | **Not started** |
| Finance review of `ws.finance.*` and `common.error.fin.*` | ● | **Not started** |
| Independent native-speaker review | ● | **Not started** (`CO-05`) |
| **Branch-agent review** | ● | **Not started.** At least two agents from different divisions, on branch hardware |

---

## 12. Open items

| # | Item | Owner | Blocks |
|---|---|---|---|
| 1 | **`BN-019` registration** so that §6 and §7 can move out of an interim route | Programme Content Lead | `BN-001` `LS-06`; `P02` non-negotiable #3; every portal's completeness claim |
| 2 | `BN-002` and `BN-007` ratification | Programme Content Lead | Every string |
| 3 | `common.empty.no_results.search_script` has no English source row | Content Design Lead | `UI-006` completeness |
| 4 | Branch Bengali input survey (`BN-006` §10 item 3) — an agent who cannot type Bengali cannot use a Bengali-default intake | Platform Engineering with Operations | W1 go-live at branches |
| 5 | Roles R39–R46 are unregistered in `05-04` (`00-07` H2-07), so `{role}` in `common.access.*` and `common.error.approval.*` cannot always resolve to a registered Bengali role name | HR + Security | `MD-009`, `common.access.*` |

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md`](BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md) | `LS-06`, `LS-07`, `LS-09` — the interim route this file executes |
| [`BN-010_Bengali_String_Bundle_P02_Technician.md`](BN-010_Bengali_String_Bundle_P02_Technician.md) | Depends on §6 for its offline, conflict and validation strings |
| [`BN-009_Bengali_String_Bundle_P01_Customer.md`](BN-009_Bengali_String_Bundle_P01_Customer.md) | Depends on §6 |
| [`../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-004_Validation_and_Error_Message_Library.md) | The English source for §6.3 and §6.4 |
| [`../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md`](../03_UI_Copy_and_Microcopy/03A_Cross_Cutting/UI-009_Offline_Sync_and_Conflict_Resolution_Copy.md) | The English source for §6.9 |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | The G4 this bundle awaits |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. **181 Bengali strings counted**: 17 `p03.*`, 17 `ws.*` (representative of 149), and **138 `common.*` plus 9 `flow.*` carried under the `BN-001` `LS-07` interim route**; the অনুমোদন/অথরাইজ and বাতিল/রদ control splits applied in the shared error and confirmation libraries; one new string added for cross-script search with no English source; 1366×768 density budgets with the no-abbreviation rule; coverage ledger quantifying the interim scope at 147 of 181 | Localisation Lead with Content Design Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:`, `traces_to:` and `i18n_namespace:`
- [x] Every `p03.*` and `ws.*` key has a Bengali string
- [x] **The `common.*` interim scope is carried in full and is clearly marked as interim**, with the move condition stated
- [x] Reserved-verb splits (approve/authorise, cancel/void, reject/decline, archive/delete) held in the shared libraries where they matter most
- [x] Class **A** messages name the authoriser as the grammatical subject
- [x] Every validation message describes the required form, not the user's mistake
- [x] Offline and conflict strings reassure before instructing
- [x] Accessible names authored and translated, not left to the implementer
- [x] Explicit `=0` plural branches, with জন used for people
- [x] Density budgets stated for 1366×768 with the no-abbreviation rule
- [x] **Coverage ledger regenerated by enumeration on 2026-08-17 and quantifies the out-of-scope interim content (147 of 181) rather than absorbing it silently**
- [ ] **132 `ws.*`, 16 `common.*` and 9 `flow.*` strings remain unauthored** — outstanding; §10
- [x] All internal links resolve
- [ ] **G4 in-context sign-off at 1366×768** — **outstanding; blocks `Approved`, unwaivable**
- [ ] **Fourteen workspace-owner reviews** — outstanding
- [ ] **Branch-agent review on branch hardware** — outstanding
- [ ] `BN-019` registered and §6, §7 moved — **outstanding; this file is over-scoped until then**
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
