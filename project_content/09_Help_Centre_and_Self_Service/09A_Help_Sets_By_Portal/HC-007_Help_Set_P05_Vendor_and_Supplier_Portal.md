---
id: HC-007
title: Help Set — P05 Vendor and Supplier Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Procurement
reviewers: [Procurement Manager, Finance Manager, Legal Counsel, Quality Manager, Localisation Lead, Accessibility reviewer]
approver: Content Design Lead with Procurement Manager
content_class: D
purpose: >
  The self-service help set for vendors and suppliers covering onboarding, RFQ, purchase orders,
  delivery, invoicing, returns and scorecards. It serves the P05 target of a 60% reduction in
  vendor phone and email queries directly: every field a vendor does not understand is a phone call
  to a procurement officer, and there are 4–8 of those against hundreds of vendors.
traces_to: [P05, M16, M42, M52, M61, MD-016, MD-022, HC-001, HC-002, HC-016, UI-015, LG-006, TR-013]
priority: P2
wave: W3
bilingual: yes
bn_counterpart: HC-007_Help_Set_P05_Vendor_and_Supplier_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P05 targets over 90% of POs acknowledged and over 85% of invoices submitted through the portal, with a 60% cut in vendor phone and email queries
    verified: 2026-08-18
    class: P1
  - source: project_content/08_Training_and_Enablement/08B_Course_Packs/TR-013_Course_Pack_Procurement_Officer.md §4 — what the vendor sees in P05 determines whether they phone; every field left blank is a phone call
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P05 Vendor and Supplier Portal

| Item | Value |
|---|---|
| Portal | `P05` Vendor & Supplier |
| Audience | **Vendor / supplier** — audience 5 · 200–500 organisations |
| Article type | Help set specification — Task predominates |
| Reading level target | `CG-011`; small-business audience, mixed digital confidence |
| Languages | **Bengali primary** — most suppliers are local businesses |
| Related UI copy | `UI-015` `P05` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-015` | Labels quoted in steps (`HS-08`) |
| `LG-006` vendor portal terms and supplier code of conduct | Linked, never restated (`IA-14`) |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) | Compliance documents and approval states the articles explain |

**`PS-12`: this audience is paid by us and is not obliged to use the portal.** A vendor who finds
the portal harder than a phone call will use the phone call, and the 60% query-reduction target
will not be met by anything the procurement team does. The help set is the adoption mechanism.

---

## Steps — *the vendor's lifecycle*

### Block A — Becoming a supplier *(7 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Register as a supplier** | Task | **P0** |
| 2 | **The documents we need and why** | Concept | **P0** |
| 3 | Your approval status — what each state means | Concept | **P0** |
| 4 | Keep your documents current | Task | P1 |
| 5 | Add users from your company | Task | P1 |
| 6 | Your bank and payment details | Task | P1 |
| 7 | Tax status and VDS | Concept | P1 |

### Block B — Quoting and orders *(8 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 8 | Respond to a request for quotation | Task | **P0** |
| 9 | **Acknowledge a purchase order** | Task | **P0** |
| 10 | **Read a purchase order** — what each field means | Concept | **P0** |
| 11 | You cannot fulfil an order | Task | P1 |
| 12 | Propose a change to an order | Task | P1 |
| 13 | Partial delivery | Task | P1 |
| 14 | Your order was cancelled | Concept | P2 |
| 15 | Part specifications and substitutions | Concept | P2 |

### Block C — Delivery and receipt *(5 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 16 | Notify a delivery | Task | P1 |
| 17 | **What happens when we receive your goods** | Concept | **P0** |
| 18 | Your delivery failed inspection | Troubleshooting | **P0** |
| 19 | Returns and replacements | Task | P1 |
| 20 | Packaging and labelling requirements | Concept | P2 |

### Block D — Invoicing and payment *(8 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 21 | **Submit an invoice** | Task | **P0** |
| 22 | **Why your invoice was rejected** | Troubleshooting | **P0** |
| 23 | Match your invoice to a PO and receipt | Concept | **P0** |
| 24 | When you will be paid | Concept | **P0** |
| 25 | Track a payment | Task | P1 |
| 26 | Raise a payment query | Task | P1 |
| 27 | Credit notes | Task | P2 |
| 28 | Statements and reconciliation | Task | P2 |

### Block E — Performance and relationship *(4 articles)*

Your scorecard and how it is calculated · improve a low score · respond to a performance concern ·
raise a concern with us. **1 at P0, 2 at P1, 1 at P2.**

**Set total: 32 articles · 12 at P0 · 13 at P1 · 7 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Vendors acknowledge POs in the portal | PO acknowledgement rate | **> 90%** |
| Vendors submit invoices in the portal | Portal invoice rate | **> 85%** |
| Vendors stop phoning | **Vendor phone and email query volume** | **60% reduction** |
| Invoices are right first time | Invoice rejection rate | Falling |

**`PS-13`: articles 21, 22, 23 and 24 carry this set.** Every vendor query that is not about an
order is about money — whether an invoice was accepted, why it was rejected, and when payment
arrives. Four articles remove the majority of the call volume the 60% target depends on.

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Query volume unchanged | Vendors are not finding or trusting the portal | Check adoption before content; `PS-12` |
| Invoice rejection rate high | Article 23 (matching) not read, or the PO itself is incomplete | **Check `P05` field completeness first** — `TR-013` §4 |
| Vendors phone about payment timing | Article 24 states a promise rather than an expectation | `HS-13`, `IA-15` — correct it |
| Registration abandoned | Block A too long, or document requirements unclear | Article 2; measure the funnel |

---

## Related

`UI-015` · [`../../08_Training_and_Enablement/08B_Course_Packs/TR-013_Course_Pack_Procurement_Officer.md`](../../08_Training_and_Enablement/08B_Course_Packs/TR-013_Course_Pack_Procurement_Officer.md) — the internal counterpart ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-017_SOP_Procurement_to_Payment.md) ·
[`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-016_Vendor_and_Supplier_Master_Standard.md) · `LG-006` ·
Category 18 `EO` — vendor onboarding (**boundary, `HC-001` `O-06`**).

---

## Feedback

Helpfulness per `CG-014`, reported weekly alongside **vendor query volume by topic** — the only
measure that shows whether the set is doing its job.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **32** · written **0** |
| Effort | 32 × 2–3 h = **65–95 hours** |
| Sequencing | The 4 money articles (`PS-13`), then 12 P0 before W3 |
| Bengali | All 32, **authored in Bengali** — local supplier base (`HS-29`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-006` vendor portal terms is unwritten** (Category 10 unstarted); Block A links to it | Legal Counsel | **W3** |
| **O-02** | `MD-016` vendor master is unpopulated; Block A article 3 explains approval states that do not exist yet | MDM with Procurement | W3 |
| **O-03** | **`P05` lands at W3 alongside this set.** Article screenshots and label quotes cannot be finalised until the portal is stable | Content Design with `P05` team | W3 |
| **O-04** | The Category 18 `EO` boundary for vendor onboarding is undefined (`HC-001` `O-06`) | Programme Content Lead | W3 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] Audience's freedom not to use the portal stated as the design constraint (`PS-12`)
- [x] 32 articles enumerated with type and priority
- [x] The four articles carrying the 60% target identified (`PS-13`)
- [x] Payment timing stated as expectation, not promise (`HS-13`, `IA-15`)
- [x] All internal links resolve
- [x] `P05` targets cited to `04-00`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 32 articles authored — outstanding**
- [ ] **`O-01` `LG-006` — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and Procurement Manager**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
