---
id: LG-011
title: Cookie and Tracking Policy
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the Chief Data Officer
author: Legal & Compliance with the Chief Data Officer, Platform Engineering and Content Design
reviewers: [Legal Counsel, Chief Data Officer, CTO delegate, Content Design Lead, Localisation Lead, Accessibility reviewer, BI Lead]
approver: Legal Counsel with the Chief Data Officer
content_class: B
purpose: >
  The cookie and tracking inventory, the consent categories, the banner and preference-centre
  positions and the rules that keep the inventory accurate across six web portals and two mobile
  applications. An inaccurate cookie inventory is one of the few compliance breaches an outsider can
  evidence in a browser in under a minute, which makes accuracy an operational discipline rather
  than a drafting exercise.
traces_to: [P01, P03, P04, P05, P06, P07, P08, P10, P12, M25, M28, M29, M35, M62, LG-001, LG-008, LG-009, LG-010, LG-012, UI-042, VB-002, CG-011, PS-04, PS-07, PS-10, BRU-CPM-07, BRU-CPM-08, BRU-CPM-09, BRU-SEC-24, NFR-081, NFR-091, NFR-092]
priority: P2
wave: W2
bilingual: yes
bn_counterpart: LG-011_Cookie_and_Tracking_Policy_BN.md
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §2 suite overview — six Next.js web portals (P01, P04, P07, P08, P10, P12), Odoo Web for P03, Odoo Portal plus Next.js for P05, embedded Metabase and Grafana for P06; §3 PS-04 WCAG 2.1 AA, PS-07 critical paths under 400 KB, PS-10 analytics instrumentation on every critical funnel feeding M25
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.3 NFR-091 consent must be clear, explicit, specific and freely given; NFR-092 the transparency notice must state the withdrawal procedure
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33 §9 BRU-CPM-07 recorded consent or documented legitimate ground per purpose; BRU-CPM-08 consent invalid unless the notice version presented is recorded; BRU-CPM-09 withdrawal immediate across every channel and module
    verified: 2026-08-18
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md §3.3 preference centre and §3.1 consent capture — the surfaces this policy's banner and preference copy attach to
    verified: 2026-08-18
    class: P1
  - source: Personal Data Protection Act 2026 — consent standard applied to cookies and similar technologies, as summarised by published legal analysis. **Secondary source. Whether a distinct cookie-consent rule exists beyond the general consent standard is unverified and is pending G5**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-011 — Cookie and Tracking Policy

| Item | Value |
|---|---|
| Document class | **Policy + notice** — with the banner and preference-centre positions |
| Counterparty | Any visitor to a company web surface, and any user of a company mobile application |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending approval* |
| Acceptance capture method | **`AC-1` consent per category** through the banner and preference centre, with the policy version recorded (`BRU-CPM-08`) |
| Version accepted by users | Recorded in `LG-001` §4.5 per visitor, per category, per policy version |
| External counsel review | **Required** — whether a distinct cookie-consent standard applies (`CK1`) |
| Bengali version | **Required.** The banner is presented in Bengali by default on customer surfaces (`PS-03`) |

> ⚠ **Class B, and the easiest breach in this category to prove from outside the company.**
>
> Anyone can open a browser's developer tools, list the cookies a page sets, and compare it to the
> published inventory. **A single undeclared tracker makes the notice false**, and the evidence is
> a screenshot.
>
> **This is therefore not a document problem. §4.6 is the whole file:** the inventory is generated
> from a scan, not maintained by hand, and a scan that finds something undeclared **fails the
> release**.
>
> **Conformance note.** All ten template sections retained in order. The inventory is §4.3 and the
> generation discipline §4.6, within §4 Terms. Gate questions and open items are §1.2 and §1.3
> (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with CDO and Platform Engineering | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CTO delegate with BI Lead | *pending* | | |
| G4 Linguistic — independent reviewer, in context (`BN-018`) | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| Approved by — Legal Counsel with CDO | *pending* | | |

### 1.2 Questions for Legal Counsel (G5)

| # | Question | Why it matters |
|---|---|---|
| **CK1** | Does a **distinct cookie-consent rule** apply in Bangladesh beyond the general consent standard, and does the general standard extend to non-cookie tracking — SDKs, pixels, fingerprinting, local storage? | Determines whether §4.4's category model is required or merely good practice |
| **CK2** | Is **strictly necessary** a valid no-consent category, and how narrowly must it be read? | If read narrowly, session and security cookies may still need disclosure without consent, which §4.4 assumes |
| **CK3** | Is **analytics** a legitimate ground or does it require consent? `PS-10` mandates analytics instrumentation on every critical funnel | If consent is required, funnel measurement drops to consented traffic and every conversion KPI becomes a partial measure |
| **CK4** | Must **refusal be as easy as acceptance** — a visible "reject all" of equal prominence? | §4.5.3 assumes yes |
| **CK5** | Is a **cookie wall** — blocking access until consent — permitted? | §4.5.6 prohibits it as a matter of policy; confirmation makes it a legal position |
| **CK6** | Do **internal portals** (`P03`, `P05`, `P06`, `P08`, `P10`) require a banner, given users are authenticated and acting in a work capacity? | §4.2 takes a position that would otherwise put a consent banner in front of a branch agent 200 times a day |
| **CK7** | What consent applies to **mobile-application** identifiers and SDK telemetry in `P01`, `P02`, `P09`, `P11`? | §4.7 |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | `CK1`–`CK7` unanswered | **Yes — blocks `Approved`** | Legal Counsel |
| **O-02** | **The inventory in §4.3 is a specification, not an observation.** No build exists, so nothing has been scanned. **Every row is what the company intends to set, not what it sets** | **Yes — the policy cannot be published against an unscanned estate** | CTO |
| **O-03** | **No consent-management mechanism is in any module's feature register.** `M29` owns identity and session; `M33` owns consent per purpose; **nothing owns the browser-side banner, the category store, or the enforcement that a rejected category does not load** | **Yes — blocks W2** | CTO |
| **O-04** | **`CK3` versus `PS-10` is a genuine conflict of commitments.** `PS-10` requires analytics on every critical funnel; if analytics needs consent, the funnel KPIs in `04-00` — booking conversion above 72%, seller onboarding completion above 60% — are measured on consented traffic only, and the baseline is not comparable | **Yes** | BI Lead with Legal |
| **O-05** | **A consent banner on `P01` competes with `NFR-081`** — critical customer paths under 400 KB first load, on 3G. A heavy consent platform is a performance regression on the exact path the company measures | No — a design constraint, stated | CTO with Content Design |
| **O-06** | **`P06` embeds Metabase and Grafana**; embedded third-party analytics tools set their own storage. That is a third-party inventory the company does not control by writing this file | Yes — blocks the `P06` rows | CTO with BI Lead |

---

## 2. Scope and Parties

**In scope:** cookies, local and session storage, SDK identifiers, pixels, tags, beacons,
fingerprinting signals and any other client-side storage or identification, across every company web
surface and mobile application; the consent categories; the banner and preference-centre positions;
the inventory; and the generation discipline that keeps it true.

**Applies to:**

| Surface | Banner required? | Position |
|---|:--:|---|
| **`P01` Customer portal and app** | **Yes** | Public, consumer-facing, the highest-traffic surface |
| **`P04` Corporate portal** | **Yes** | External users, authenticated but not employees |
| **`P07` Seller portal and app** | **Yes** | External users |
| **`P12` Partner portal** | **Yes** | External users |
| **`P08` Brand partner portal** | **Yes** | External users |
| **`P05` Vendor portal** | **Yes** | External users |
| **`P03` Admin operations portal** | **No — internal, subject to `CK6`** | Employees on company systems; **`LG-020` is the notice that covers them** |
| **`P06` Analytics dashboard** | **No — internal, subject to `CK6` and `O-06`** | Employees; embedded third-party tools disclosed in §4.3 |
| **`P10` Contact centre console** | **No — internal, subject to `CK6`** | Employees; call recording is `LG-008` `P-12`, not a cookie question |
| **`P02`, `P09`, `P11` mobile applications** | **Consent, not a banner** | §4.7; `CK7` |
| **Corporate marketing website** | **Out of scope** | A separate content set with its own approval authority (Master Index §11) |

**Out of scope:**

| Subject | Owned by |
|---|---|
| Purposes, lawful bases and the notice as a whole | [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) |
| How long cookie-derived data is kept | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) `RC-04`, `RC-24` |
| Where analytics data is stored and whether it leaves Bangladesh | [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) |
| Withdrawal as a rights request | [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) |
| **Banner and preference-centre wording, keys and Bengali strings** | [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) — the `LG-008` §4.7 boundary applies |
| Internal system monitoring of employees | [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Cookie** | A small file a site stores in the browser. **In this policy the word covers every client-side storage and identification technology**, because a policy about cookies alone is a policy with a loophole |
| **First-party** | Set by a company domain |
| **Third-party** | Set by another party's domain or SDK, including an embedded tool |
| **Strictly necessary** | Required for the surface to function or to be secure. **Not "useful", not "we would rather have it"** |
| **Category** | The consent unit. A visitor consents by category, never to a list of individual cookies |
| **Session** | Deleted when the browser closes |
| **Persistent** | Survives the session, with a stated duration |
| **Scan** | An automated enumeration of what a built surface actually sets (§4.6) |

---

## 4. Terms

### 4.1 The commitment

| # | Clause |
|---|---|
| **4.1.1** | The company sets only what §4.3 declares |
| **4.1.2** | **Nothing outside "strictly necessary" is set before consent.** Not on page load, not "pending consent", not on the first navigation |
| **4.1.3** | The visitor may accept all, reject all, or choose by category, **with equal prominence** (§4.5.3, `CK4`) |
| **4.1.4** | A choice may be changed at any time, and **withdrawal takes effect immediately** (`BRU-CPM-09`) |
| **4.1.5** | **The policy version presented is recorded with the consent** (`BRU-CPM-08`) |
| **4.1.6** | Access is never conditioned on accepting a non-necessary category (§4.5.6) |

### 4.2 Internal portals — the position and why

> **`CL-01`.** Putting a consent banner in front of a branch agent who opens `P03` forty times a
> day is a compliance ritual with no privacy benefit: they are not a visitor exercising a choice,
> they are an employee using a work system whose monitoring is disclosed to them under `LG-020`.

| # | Clause |
|---|---|
| **4.2.1** | Internal portals set **strictly necessary storage only** — session, authentication, CSRF, UI preference, and the workspace state that makes the console usable |
| **4.2.2** | **No advertising, no marketing, and no cross-site tracking on any internal portal.** Ever |
| **4.2.3** | Product analytics on internal portals is **first-party, aggregated, and disclosed in `LG-020`**, not consent-gated |
| **4.2.4** | The internal inventory is published to employees in the same §4.3 table, so the position is inspectable |
| **4.2.5** | **This position is subject to `CK6`.** If confirmation is refused, internal portals get a banner and §4.2 is withdrawn |

### 4.3 The inventory — **a specification pending scan (`O-02`)**

> **`CK-R1`: this table is the notice.** A surface that sets anything not in it is in breach of its
> own notice. Duration is a maximum; a shorter actual duration is compliant, a longer one is not.

**Category N — Strictly necessary (no consent)**

| Purpose | Type | Surfaces | Duration |
|---|---|---|---|
| Session and authentication (`M29`, `PS-01`) | First-party | All | Session |
| CSRF and request-integrity token | First-party | All | Session |
| Load balancing and routing | First-party | All | Session |
| Security — rate limiting, bot and abuse signals | First-party | All | Up to 12 months |
| **Consent record itself** — which categories were chosen and against which policy version | First-party | All external | **12 months**, then re-asked |
| Language selection (`PS-03`) | First-party | All | 12 months |
| Accessibility preference — contrast, text size (`CG-011`) | First-party | All | 12 months |
| Cart and checkout state (`P01` shop) | First-party | `P01` | Session, or 7 days where the cart persists |

**Category F — Functional (consent)**

| Purpose | Type | Surfaces | Duration |
|---|---|---|---|
| Remembered device for faster sign-in | First-party | `P01`, `P04`, `P07`, `P12` | 90 days |
| Saved address or branch preference | First-party | `P01` | 12 months |
| Workspace layout and column preference | First-party | `P03`, `P05`, `P08`, `P10` — **necessary in practice; declared functional** | 12 months |
| Live-chat session continuity (`M27`) | First-party + third-party where the chat is embedded | `P01`, `P04` | Session |
| Embedded video or map | Third-party | `P01` help surfaces | Per provider — **disclosed, not controlled** |

**Category A — Analytics and performance (consent — subject to `CK3`)**

| Purpose | Type | Surfaces | Duration |
|---|---|---|---|
| Funnel and conversion measurement (`PS-10`, feeding `M25`) | First-party | `P01`, `P04`, `P07`, `P12` | 13 months, aligned to `LG-009` `RC-04` |
| Error and crash reporting | First-party | All | 90 days |
| Performance timing against `NFR-081` | First-party | `P01`, `P07` | 90 days |
| **Embedded Metabase / Grafana storage** | **Third-party** | **`P06`** | **Per provider — `O-06`** |
| Search-term analytics feeding help coverage (`HC-001`) | First-party | `P01` | 13 months |

**Category M — Marketing (consent)**

| Purpose | Type | Surfaces | Duration |
|---|---|---|---|
| Campaign attribution (`M35`) | First-party | `P01` | 90 days |
| **Referral attribution** (`M40`, `LG-007` §4.2) | First-party | `P01`, `P12` | **The attribution window — `LG-007` `O-02`** |
| Advertising and remarketing pixels | Third-party | `P01` only, **and only where a campaign is live** | Per provider, maximum 12 months |
| Social sharing widgets | Third-party | `P01` | Per provider |

| # | Rule |
|---|---|
| **CK-R2** | **No cross-context behavioural profiling of a customer's repair history for advertising.** A person's device failures are not advertising signal, and the company does not treat them as such |
| **CK-R3** | **Referral attribution is Category M, not necessary.** `LG-007` §4.2.4 already provides that a lead outside its window attributes to no partner; **a rejected marketing category has the same effect and the partner is not owed a different outcome** |
| **CK-R4** | A third-party row is disclosed with the provider named in the published version of this policy. **"A third-party analytics provider" is not a disclosure** |
| **CK-R5** | **No fingerprinting** — canvas, font, audio or device-signal fingerprinting — is used for identification on any surface |

### 4.4 The category model

| Category | Consent | Reject consequence | Notes |
|---|:--:|---|---|
| **N** Strictly necessary | **None** | Cannot be rejected. **Disclosed, not offered** | Narrowly read (`CK2`) |
| **F** Functional | Required | The surface works; conveniences are lost | Never used to smuggle analytics |
| **A** Analytics | Required — `CK3` | **Measurement drops to consented traffic** (`O-04`) | First-party where possible |
| **M** Marketing | Required | No attribution, no remarketing | Independent of `LG-008` `CN-01` message consent |

| # | Rule |
|---|---|
| **CK-R6** | **Categories are independent.** Accepting analytics is not accepting marketing |
| **CK-R7** | **Cookie category consent and messaging consent are different consents.** Rejecting Category M does not withdraw `CN-01`, and withdrawing `CN-01` does not clear Category M. **Both are stated to the visitor**, because the opposite assumption is the one people make |
| **CK-R8** | A new cookie in an existing category is covered by that consent. **A new *purpose* is a new category or a re-consent** |
| **CK-R9** | **Consent is re-asked every 12 months**, and on any MAJOR change to this policy |

### 4.5 Banner and preference centre — positions, not wording

| # | Position |
|---|---|
| **4.5.1** | The banner appears on first visit, before any non-necessary storage is set |
| **4.5.2** | It states, in one screen: that the company uses cookies, the categories, the link to this policy, and the choices |
| **4.5.3** | **Accept all and reject all are equally prominent** — same size, same weight, same contrast, neither pre-selected (`CK4`) |
| **4.5.4** | No category is pre-ticked except **N** |
| **4.5.5** | Dismissing the banner without choosing is **not consent**. Non-necessary storage stays off |
| **4.5.6** | **No cookie wall.** Content is not withheld pending consent (`CK5`) |
| **4.5.7** | The preference centre is reachable from every page footer and from the account area, and shows the **current** choices |
| **4.5.8** | The banner meets **WCAG 2.1 AA** (`PS-04`): keyboard reachable, focus trapped and returned, announced to a screen reader, and **not colour-only** for the selected state (`VB-008`) |
| **4.5.9** | **Bengali by default on customer surfaces** (`PS-03`), with the Bengali rendered length budgeted (`UI-042` §8) |
| **4.5.10** | The banner is **lightweight**, because it sits on the path `NFR-081` measures (`O-05`) |
| **4.5.11** | Wording is `UI-042`; **meaning is here** (`LG-008` `UB-01`…`UB-04`) |

### 4.6 Keeping the inventory true — the operational discipline

> **`CL-02`. This is the section that decides whether the policy is accurate a year from now.**
> `AUDIT-005` found a derived figure restated in eleven places and reconciled in none. A cookie
> inventory maintained by hand will drift the same way, except that this drift is externally
> visible in a browser.

| # | Rule |
|---|---|
| **CK-R10** | **The inventory is generated by an automated scan of each built surface**, not maintained by hand |
| **CK-R11** | **The scan runs in the release pipeline. A surface that sets something undeclared fails the release**, in the same way an accessibility scan gates a release under `CG-011` |
| **CK-R12** | The scan runs against a **consent-rejected** session as well as an accepted one. **The rejected-session scan is the one that matters**: it proves §4.1.2 |
| **CK-R13** | A third-party script added by any team requires a §4.3 row and a category **before** it ships. **No script is added "temporarily"** |
| **CK-R14** | An embedded tool's own storage is scanned too, and where it cannot be controlled it is **disclosed as uncontrolled** (`O-06`) |
| **CK-R15** | The published policy states its **inventory-generation date**, the way completion figures do under `CP-11` and `EV-06` |
| **CK-R16** | A discrepancy between the scan and this file is a **compliance defect**, escalated under `CG-013` `T-C05` — not a documentation backlog item |
| **CK-R17** | The scan result is retained as evidence for the period in `LG-009` `RC-19` |

### 4.7 Mobile applications

| # | Clause |
|---|---|
| **4.7.1** | `P01`, `P02`, `P09` and `P11` do not use cookies but do use device identifiers, local storage and SDK telemetry. **The same category model applies** (`CK7`) |
| **4.7.2** | The consumer app (`P01`) presents the same choices at first run, in the platform's own permission model where one exists |
| **4.7.3** | **`P02`, `P09` and `P11` are work applications** issued to staff and contractors. Their telemetry is disclosed under `LG-020`, not consent-gated — **and location tracking during a shift is disclosed explicitly there, because it is the most intrusive processing in the estate** |
| **4.7.4** | **No advertising identifier is collected in any application** |
| **4.7.5** | Offline caches on `P02`, `P09` and `P11` hold operational data, not tracking data, and are cleared per `LG-009` |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This policy creates no contractual limitation |
| **5.2** | **An inaccurate inventory makes the notice false**, and a false transparency notice is a breach exposed to the penalties in `LG-008` §5.2 |
| **5.3** | **A third party's script is the company's responsibility on the company's surface.** "The vendor set it" is not a defence, which is why `CK-R13` gates it before it ships |
| **5.4** | The company does not warrant a third-party provider's own compliance, and where it cannot control an embedded tool's storage it **says so** rather than implying control it does not have (`CK-R14`) |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| Axis | This file | Reconciles with |
|---|---|---|
| Consent standard and per-purpose recording | §4.1, `CK-R9` | **`LG-008` `CN-06`, `CN-R1`, `CN-R2`; `BRU-CPM-07`, `BRU-CPM-08`** |
| Withdrawal effect | Immediate (§4.1.4) | **`BRU-CPM-09`; `LG-008` `CN-R3`** |
| Anti-bundling | `CK-R7` — cookie category consent and messaging consent are distinct | **`LG-008` `CN-01`; `LG-001` `LR-07`** |
| Retention of cookie-derived data | 13 months analytics; 90 days error and performance | **`LG-009` `RC-04`, `RC-24`** |
| Where analytics data goes | §4.3 third-party rows | **`LG-012` §4.5 transfer register and §4.6 sub-processor register — a third-party tag is a transfer** |
| Internal-portal position | §4.2 | **`LG-020` monitoring notice — the disclosure that replaces the banner** |
| Wording versus meaning | §4.5.11 | **`UI-042`; `LG-008` `UB-01`…`UB-04`** |

| # | Rule |
|---|---|
| **F6-06** | **Every third-party row in §4.3 must appear in the `LG-012` §4.6 sub-processor register.** A tag that sends data abroad is a cross-border transfer and needs a registered basis (`BRU-SEC-14`) |
| **F6-07** | **No cookie or tracker collects or stores a residency-restricted identifier.** Not in a cookie value, not in local storage, not in an SDK payload (`BRU-SEC-13`, `BRU-SEC-24`) |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **A visitor rejects a category** | Nothing in that category is set. **A rejected-session scan proves it** (`CK-R12`) |
| **A visitor withdraws consent** | Storage in that category is deleted and stops being set, immediately (`BRU-CPM-09`) |
| **12 months pass** | Consent is re-asked (`CK-R9`) |
| **A MAJOR change to this policy** | Consent is re-asked; the new version is recorded with the new consent |
| **A third-party provider is dropped** | Its rows are removed, its storage is expired, and the version is republished |
| **A scan finds an undeclared tracker** | **The release fails** (`CK-R11`). If it is already in production, it is removed or declared within one working day and reported as a defect (`CK-R16`) |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — Query or complaint** | The Chief Data Officer contact in `LG-008` §4.9 |
| **2 — As a rights request** | `LG-010`, where the visitor asks what was collected |
| **3 — The Authority** | The National Data Management Authority |
| **4 — Courts** | The courts of Dhaka, Bangladesh |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft. **Inventory is specified, not scanned (`O-02`)** | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | Adding a **category** or a **purpose** is MAJOR: republish and re-ask consent |
| **9.2** | Adding a cookie within an existing category and purpose is MINOR: republish the inventory with a new generation date (`CK-R15`), no re-consent (`CK-R8`) |
| **9.3** | **A third-party provider change is MAJOR**, because the recipient changes and `F6-06` applies |
| **9.4** | Every published version is retained (`LG-009` `DC-23`), because a consent was given against it |
| **9.5** | **`CK3`'s answer is a MAJOR change and may require the `PS-10` commitment to be restated** (`O-04`) |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) | `CN-06`; the consent standard; the `UB` boundary | Check **F6** |
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | `RC-04`, `RC-24` durations | Cookie-derived data periods |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | **`F6-06` — every third-party row is a transfer** | The sub-processor register |
| [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | A visitor asking what was collected | Access response content |
| [`LG-020_Acceptable_Use_and_Internal_Access_Policy.md`](LG-020_Acceptable_Use_and_Internal_Access_Policy.md) | **§4.2 and §4.7.3 — the disclosure that replaces the banner for staff** | Monitoring and location disclosure |
| [`LG-007_Referral_and_Alliance_Partner_Agreement.md`](LG-007_Referral_and_Alliance_Partner_Agreement.md) | `CK-R3` — a rejected Category M means no attribution | Attribution expectations |
| [`../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md`](../03_UI_Copy_and_Microcopy/03D_Critical_Flows/UI-042_Consent_Privacy_and_Preference_Centre_Copy.md) | Banner and preference wording | §4.5 positions versus its strings |
| [`../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md`](../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md) | Banner tone per surface and audience | Tone on a consumer surface versus an external business one |
| [`../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md`](../00_Content_Governance_and_Standards/CG-011_Accessibility_Content_Standard.md) | §4.5.8 | WCAG 2.1 AA on the banner |
| `AP-*` integration content · `TS-017` security and privacy test pack | Where `CK-R11` and `CK-R12` scans are specified and verified | The scan gate |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **Four-category model with reject consequences stated**, and cookie consent distinguished from messaging consent (`CK-R7`)
- [x] **Inventory declared per category, per surface, with duration and first- or third-party status**
- [x] **Internal-portal position reasoned rather than defaulted** (§4.2, `CL-01`), with the fallback if `CK6` refuses it
- [x] **Accuracy made an automated release gate, including a rejected-session scan** (§4.6, `CL-02`)
- [x] Mobile applications covered, with work-app telemetry routed to `LG-020` rather than consent-gated
- [x] Explicit prohibitions: no repair-history advertising profiling, no fingerprinting, no cookie wall, no advertising identifier in any app
- [x] All internal links resolve
- [x] Accessibility standard `CG-011` applied to the banner (§4.5.8)
- [ ] **`CK1`–`CK7` answered at G5** — outstanding, blocks `Approved`
- [ ] **Inventory generated from a scan of a built surface** — outstanding, `O-02`; **the policy cannot be published until it is observed rather than intended**
- [ ] **Consent-management mechanism owned by a module** — outstanding, `O-03`
- [ ] **`CK3` versus `PS-10` conflict resolved** — outstanding, `O-04`
- [ ] **Bengali counterpart authored and signed off in context** — outstanding
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
