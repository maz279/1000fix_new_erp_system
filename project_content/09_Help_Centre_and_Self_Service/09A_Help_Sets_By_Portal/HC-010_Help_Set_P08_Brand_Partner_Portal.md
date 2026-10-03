---
id: HC-010
title: Help Set — P08 Brand Partner Portal
project: 1000FiX ERP System v2.0
content_type: Help article
template: TPL_Help_Article.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design
author: Content Design with Warranty and Commercial
reviewers: [Chief Commercial Officer, Warranty Claims Officer, Quality Manager, Legal Counsel, Finance Manager, Localisation Lead]
approver: Content Design Lead with Chief Commercial Officer
content_class: D
purpose: >
  The self-service help set for brand partners covering claim review, evidence, reconciliation,
  consignment, rate cards, performance and audits. It reduces claim decision time toward the
  sub-10-day target by removing process ambiguity — and it is the one help set read by
  organisations that can withdraw the authorisation the warranty revenue depends on.
traces_to: [P08, M09, M40, M15, M23, M61, MD-017, MD-022, HC-001, HC-002, HC-008, UI-018, LG-005, KB-010, SP-014, TR-014]
priority: P2
wave: W4
bilingual: yes
bn_counterpart: HC-010_Help_Set_P08_Brand_Partner_Portal_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00_Portal_Suite_Overview.md — P08 serves 17+ international brand partners reviewing claims; copy quality here is a reputational surface with commercial consequence
    verified: 2026-08-18
    class: P1
  - source: project_content/07_Knowledge_Base_and_Technical_Library/KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md §1 — P08 allows brands to push bulletins and recall notifications; BRU-KMS-15 routes recalls to M09 and M01 and never actions them in M61
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §2 BRU-WTY-01 claim evidence requirements; BRU-WTY-05 claims valued at the rate prevailing on service completion date
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2027-02-18
---

# Help Set — P08 Brand Partner Portal

| Item | Value |
|---|---|
| Portal | `P08` Brand Partner |
| Audience | **Brand partner** — audience 7 · 17+ organisations *(figure recorded as unverified — `MD-017`, `00-07` H2-12)* |
| Article type | Help set specification — Task and Concept |
| Reading level target | `CG-011`; professional audience, **often not Bengali-speaking** |
| Languages | **English primary**, Bengali parallel (`HS-30`) |
| Related UI copy | `UI-018` `P08` copy pack |

> **Template conformance.** As `HC-003`, applied at set level.

---

## Before you start

| Prerequisite | Why |
|---|---|
| [`../HC-001_Help_Centre_Information_Architecture.md`](../HC-001_Help_Centre_Information_Architecture.md) · [`../HC-002_Help_Article_Template_and_Style_Rules.md`](../HC-002_Help_Article_Template_and_Style_Rules.md) | Architecture and shape |
| `UI-018` | Labels quoted in steps |
| `LG-005` brand partner portal terms | Linked, never restated (`IA-14`) |
| [`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) | Authorisation scope and rate-card ownership |

**`PS-19`: this is the only help set whose readers hold power over the company.** A brand partner
can withdraw authorisation, and `BRU-SRM-09` makes that authorisation the precondition for warranty
work. The register's own words for `UI-018` apply here: *"copy quality here is a reputational
surface with commercial consequence."* Every article is written as if it will be quoted back.

---

## Steps — *the brand partner's interactions*

### Block A — Claims *(9 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 1 | **Review a submitted claim** | Task | **P0** |
| 2 | **What evidence we attach and why** | Concept | **P0** — `BRU-WTY-01` |
| 3 | Approve, reject or query a claim | Task | **P0** |
| 4 | **Raise a query and what happens next** | Task | **P0** |
| 5 | Bulk review and filters | Task | P1 |
| 6 | Claim valuation and currency | Concept | P1 — `BRU-WTY-05` |
| 7 | Duplicate and re-submitted claims | Concept | P1 |
| 8 | Claim aging and your decision window | Concept | P1 |
| 9 | Export claims for your systems | Task | P2 |

### Block B — Reconciliation and settlement *(5 articles)*

Your statement · reconcile claims to payments · dispute a settlement line · credit notes and
adjustments · payment timing. **1 at P0, 3 at P1, 1 at P2.**

### Block C — Consignment and parts *(5 articles)*

Your consignment stock with us · consumption reporting · **parts we may and may not substitute** ·
replenishment · stock reconciliation. **1 at P0, 3 at P1, 1 at P2.**

### Block D — Rate cards and authorisation *(4 articles)*

Your rate card and how it applies · propose a rate change · **which technicians are certified for
your brand** · authorisation scope. **1 at P0, 2 at P1, 1 at P2.**

### Block E — Bulletins, recalls and quality *(6 articles)*

| # | Article | Type | Pri |
|---:|---|---|:--:|
| 24 | **Send us a technical bulletin** | Task | **P0** |
| 25 | **Send us a recall notice** | Task | **P0** |
| 26 | **How we distribute and acknowledge what you send** | Concept | **P0** — `KB-010` |
| 27 | Track acknowledgement across our network | Task | P1 |
| 28 | Your quality and performance view | Task | P1 |
| 29 | Request an audit or a site visit | Task | P2 |

**Set total: 29 articles · 10 at P0 · 13 at P1 · 6 at P2.**

---

## What happens next

| Outcome | Measure | Target |
|---|---|---|
| Claims decided faster | **Claim decision time** | **Under 10 days** |
| Fewer queries caused by unclear evidence | Query-to-claim ratio | Falling |
| Bulletins and recalls arrive through the governed channel | **Bulletins received via `P08` vs other routes** | Rising to 100% |
| Acknowledgement is evidenced | `KPI-C61-11` bulletin acknowledgement | 90% W7, **100% W9** |

**`PS-20`: articles 2, 24, 25 and 26 carry this set.** Article 2 removes the commonest cause of
claim queries — the brand not knowing what our evidence pack contains. Articles 24–26 make `P08`
the channel of record for bulletins and recalls, which `KB-010` §11.3 identifies as the single
clearest indicator of channel health: *recalls where we were not the first to know, target zero.*

---

## If it does not work

| Symptom | Cause | What to do |
|---|---|---|
| Claim decision time above 10 days | Evidence unclear, or query loop slow | Article 2 first; then measure the query round-trip |
| Bulletins still arriving by email | The portal path is unknown or harder | Articles 24–26; **and fix the path, not the help** |
| Brand disputes our technician certification | Article 22 unclear, or `MD-011` data wrong | `BRU-SRM-09`; check the data before the content |
| A recall is discovered from a public source first | **Channel failure with liability implications** | `KB-010` §10 — Quality Manager and Legal, same day |

---

## Related

`UI-018` · [`../../07_Knowledge_Base_and_Technical_Library/KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md`](../../07_Knowledge_Base_and_Technical_Library/KB-010_Brand_Technical_Bulletin_and_Recall_Archive.md) — **the receiving end of Block E** ·
[`../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-014_SOP_Warranty_Claim_Submission_and_Reconciliation.md) ·
[`../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md`](../../02_Master_Data_and_Configuration/02B_Party_and_Ecosystem/MD-017_Brand_Partner_Master_Register.md) · `LG-005` ·
[`HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md`](HC-008_Help_Set_P06_Analytics_and_Executive_Dashboard.md) — brand partners see scoped analytics.

---

## Feedback

Helpfulness per `CG-014`. **`PS-21`: feedback from this audience is treated as commercial
intelligence, not only as content signal** — a brand partner reporting an article as unhelpful is
reporting friction in a revenue relationship, and it is routed to the account owner as well as to
Content Design.

---

## Coverage and Authoring Plan *(addition)*

| Item | Position |
|---|---|
| Articles required | **29** · written **0** |
| Effort | 29 × 2–3 h = **60–90 hours**, plus Warranty and Legal review on Blocks A and E |
| Sequencing | Articles 2, 24, 25, 26 (`PS-20`), then 10 P0 before W4 |
| Bengali | Both; **English primary** for international partners (`HS-30`) |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **`LG-005` brand partner portal terms is unwritten** (Category 10 unstarted) | Legal Counsel | **W4** |
| **O-02** | **Brand-specific claim requirements are unknown** — `TR-004` `O-01` records that no brand's terms are held and `BRU-SRM-09` cannot be configured. Article 2 explains an evidence pack whose acceptability is unverified | Commercial with Warranty | **W4** |
| **O-03** | **`KB-010` is `P1`/`W4` and `M61` lands at `W6`**, so Block E describes a bulletin and acknowledgement mechanism that will not exist when this set publishes (`KB-010` `O-01`) | Quality Manager with CTO | **W4** |
| **O-04** | The "17+ brands" figure remains unverified (`00-07` H2-12, `MD-017`); the audience size in the header inherits that uncertainty | Commercial with MDM | W4 |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Help_Article.md` at set level; additions justified
- [x] The audience's power over the company stated as the writing constraint (`PS-19`)
- [x] 29 articles enumerated with type and priority
- [x] The four articles carrying claim speed and channel health identified (`PS-20`)
- [x] Feedback routed as commercial intelligence (`PS-21`)
- [x] The unverified "17+" figure inherited with its caveat rather than silently asserted
- [x] All internal links resolve
- [x] `BRU-WTY-01`/`-05`, `BRU-SRM-09` cited to `05-05`; `BRU-KMS-15` and `KPI-C61-11` to `M61`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 29 articles authored — outstanding**
- [ ] **`O-02` brand claim requirements — outstanding**
- [ ] **`O-03` bulletin mechanism at W4 versus `M61` at W6 — outstanding**
- [ ] Bengali counterpart complete and signed off in context (`BN-018`) — **outstanding**
- [ ] Named approvers recorded — **pending Content Design Lead and CCO**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
