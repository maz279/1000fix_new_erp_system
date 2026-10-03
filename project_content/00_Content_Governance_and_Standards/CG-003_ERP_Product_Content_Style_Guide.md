---
id: CG-003
title: ERP Product Content Style Guide
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Content Design Lead
author: Content Design
reviewers: [Enterprise Architecture, Localisation Lead, Brand, Design System]
approver: Programme Content Lead
purpose: >
  Fixes the mechanical conventions of English content across twelve portals, fourteen admin
  workspaces and five frameworks. Enterprise UI copy is written by developers, BAs and vendors
  simultaneously; without one style guide the same action is labelled four ways across four
  workspaces and none of them translates cleanly into Bengali.
traces_to: [04-00 PS-06, 04-00 PS-09, 05-05 BR-STD-04, CG-004, CG-011, BN-005]
priority: P0
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §3 cross-portal standards PS-01…PS-12
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 §1 BR-STD-04
    verified: 2026-08-15
  - source: Microsoft Writing Style Guide — capitalization and UI text conventions (learn.microsoft.com/style-guide)
    verified: 2026-08-15
  - source: 1000_fix_corporate_website project_content CB-005 Brand Voice Guidelines v1.0
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-003 — ERP Product Content Style Guide

> **Scope.** English content in the ERP and its twelve portals: UI copy, notifications,
> documents, help, SOPs, training and reports. Bengali conventions are in `BN-002`; brand voice
> and tone are in `VB-001`; terminology is in `CG-004`. This file governs **mechanics** —
> spelling, case, punctuation, numbers, structure and sentence construction.
>
> **This guide does not apply** to the corporate website content set, which has its own
> conventions. Where the two conflict, §1.2 states which wins and why.

---

## 1. The three decisions that everything else follows from

### 1.1 Decision 1 — British English (en-GB)

**All ERP content is written in British English.**

This is not a new choice; it ratifies what the specification repository already does. The 67
module specifications, the 12 portal specifications and every cross-cutting document use
*localisation*, *catalogue*, *organisation*, *prioritisation*, *recognise*, *centre*,
*licence* (noun) and *authorised*. Adopting American English now would require rewriting 123
approved documents.

| Use | Not |
|---|---|
| localisation, localise | localization, localize |
| catalogue | catalog |
| organisation, organise | organization, organize |
| authorised, authorisation | authorized, authorization |
| centre (a place) | center |
| licence (noun) / license (verb) | license (both) |
| prioritise, recognise, minimise | prioritize, recognize, minimize |
| analyse | analyze |
| enrolment, fulfilment | enrollment, fulfillment |
| defence, offence | defense, offense |
| programme (an initiative) / program (software) | programme for both |

**Exceptions that stay American or invariant:**

| Term | Why |
|---|---|
| `authorized` inside a quoted brand designation — "Samsung Authorized Service Center" | It is the brand's registered designation, not our prose |
| Code identifiers, model names, field names — `fix.service.order`, `operating_unit_id` | Technical identifiers are never spelled for style |
| Third-party product names — Odoo *Inventory*, Metabase *Dashboard* | Reproduce the vendor's own spelling |
| Direct quotations from statute or a contract | Quote exactly, including spelling |

> ⚠ **Known conflict — corporate website content set.** The website's 431-file content set uses
> American English throughout, including its folder name `LOCALIZATION`. The two sets are
> deliberately separate (Master Index §11) and this conflict is accepted, not resolved. **The
> four interface points** between them — booking entry, service catalogue, pricing statements
> and legal terms — are owned on the ERP side and therefore use en-GB. Anyone porting text
> between the sets must re-spell it. Logged as a content decision in `RF-006`.

### 1.2 Decision 2 — Sentence case everywhere

**Capitalise the first word and proper nouns. Nothing else.** This applies to headings, buttons,
labels, menu items, tabs, table headers, tooltips, error messages, notification subjects,
document titles and report names.

| Write | Not |
|---|---|
| Create service order | Create Service Order |
| Estimate approved | Estimate Approved |
| Parts and consumables | Parts And Consumables |
| Van stock reconciliation | Van Stock Reconciliation |
| Warranty claim submitted to Samsung | Warranty Claim Submitted To Samsung |

**Why sentence case, given that the brand voice guide for the website uses title case for
headings:** an ERP presents thousands of labels at high density on a 1366×768 branch screen
(`04-00` §P03). Title case slows scanning, makes it impossible to tell a proper noun from an
emphasised word, and produces meaningless results when the same string is machine-transformed
for Bengali, which has no letter case at all.

**Exceptions:**

| Exception | Form | Example |
|---|---|---|
| Proper nouns | Capitalised | Dhaka, Samsung, bKash, Mushak, Odoo |
| Product and plan names (`VB-010`) | Capitalised as registered | Privilege Gold, RAMC Premium |
| Statutory form names | As the instrument writes them | Mushak 6.3, Mushak 9.1 |
| Acronyms | Upper case | SLA, AMC, VAT, NID, TIN, GRN, POD |
| Status badges in UI | Upper case, ≤ 12 characters | OVERDUE, ON HOLD, BREACHED |
| Document titles on printed statutory output | As the instrument requires | VALUE ADDED TAX INVOICE |

### 1.3 Decision 3 — Second person, active voice, present tense

| Convention | Rule | Example |
|---|---|---|
| **Person** | Address the user as **you**. The system is **the system** or names itself in the third person. Never **we** in UI. | "You cannot approve your own estimate." Not: "We cannot let you approve…" |
| **Voice** | Active. Name the actor. | "The dispatcher reassigned this job." Not: "This job was reassigned." |
| **Tense** | Present for state, past for completed events, future only for scheduled things. | "Payment is pending." / "Estimate approved on 12 Aug." / "The visit is scheduled for 14 Aug." |
| **Mood** | Imperative for actions. | "Select a technician." Not: "Please select a technician." |

**"We" is permitted** in customer-facing marketing-adjacent content (`CM`, `EO` kits) and in
help articles where the company is genuinely the actor ("We hold your device for 90 days").
It is never permitted in UI labels, error messages or system notifications.

---

## 2. Sentence construction

| # | Rule | Why |
|---|---|---|
| **S-01** | One idea per sentence. Maximum 25 words in UI, 30 in help and SOPs. | Bengali translation of a compound English sentence produces a clause order the reader must re-assemble |
| **S-02** | Lead with the outcome, not the mechanism. | "Your device is ready for collection" beats "Repair status has been updated to Ready" |
| **S-03** | Front-load the important word. Users scan the first two words of a label. | "Serial number" not "Number (serial)" |
| **S-04** | No nominalisation. Use the verb. | "Approve the estimate" not "Perform estimate approval" |
| **S-05** | No string concatenation across translatable boundaries. | See `BN-005`. "You have {n} {items}" is untranslatable into Bengali; author the whole sentence per plural form |
| **S-06** | No idiom, metaphor, humour or cultural reference. | It does not survive translation and it does not survive a customer reading it during a complaint |
| **S-07** | No negatives stacked. Avoid "not un-", "cannot be disabled unless". | Double negatives are the most common source of misread business rules |
| **S-08** | Prefer the specific number to the vague quantifier. | "3 parts on hold" not "several parts on hold" |
| **S-09** | Never use "please" in UI, and never apologise for normal system behaviour. | It adds a word to every label and reads as insincere at the thousandth repetition |
| **S-10** | State what to do next in every failure state. | `BR-STD-04` and `PS-09` make this contractual, not stylistic |

---

## 3. Error, warning and confirmation messages

`BR-STD-04` requires that **every rule violation produces a message stating what is wrong and
what to do, in the user's language.** `PS-09` extends the same obligation to every user-visible
error on every portal. This section is how that obligation is met mechanically. The full library
is `UI-004`; the accessibility requirements are `CG-011` §5.

### 3.1 The three-part structure

```
[What happened]  [Why, if it is not obvious]  [What to do next]
```

| Bad | Good |
|---|---|
| Error 4032. | This estimate cannot be approved. Estimates above BDT 25,000 need branch manager approval. Send it to <branch manager> for approval. |
| Invalid input. | Enter the IMEI as 15 digits with no spaces. |
| Operation failed. | The part could not be issued. Job SR-2026-114882 has no approved estimate. Approve the estimate first, then issue the part. |
| You do not have permission. | You cannot void a posted invoice. Ask a Finance Manager to raise a credit note instead. |

### 3.2 Rules

| # | Rule |
|---|---|
| **E-01** | Never expose an error code alone. A code may accompany plain language, never replace it. |
| **E-02** | Never expose internal detail — table names, stack traces, model names, SQL, server names, internal user IDs. This is a security requirement as well as a style one (`UI-005`). |
| **E-03** | Never blame the user. "Enter a valid date" not "You entered an invalid date". |
| **E-04** | Name the specific field, record or rule that failed, using its exact on-screen label. |
| **E-05** | Where a role can resolve it, name the role — not the person, which changes. |
| **E-06** | Where the rule has an identifier (`BRU-XXX-nn`), reference it in the log, never in the user-facing text. |
| **E-07** | A hard rule (class **H**) message says the action cannot be done. An approved-override rule (class **A**) says who can authorise it. A soft rule (class **S**) says the user may proceed and what the consequence is. Match the message to the rule class from `05-05`. |
| **E-08** | Confirmation dialogs state the consequence, not the question. Button label is the verb, not "OK". |

### 3.3 Confirmation dialog pattern

| Element | Rule | Example |
|---|---|---|
| Title | The action, sentence case, no question mark | Cancel this service order |
| Body | What will happen, including anything irreversible | The customer will be notified and the reserved parts will be released. This cannot be undone. |
| Reason capture | Required wherever `BR-STD-06` applies | Reason for cancellation (required) |
| Primary button | The verb of the action | Cancel order |
| Secondary button | The verb of not doing it | Keep order |

Never label buttons **OK / Cancel** on a destructive action — a user reading fast cannot tell
which "cancel" means what.

---

## 4. Numbers, dates, money and units

Aligned to `05-06` §9 Localisation Standards. Where this guide and `05-06` differ, `05-06`
governs and this guide is corrected.

| Element | English (en) | Bengali (bn-BD) | Notes |
|---|---|---|---|
| Number grouping | 1,234,567 | 12,34,567 | Lakh/crore grouping in the Bengali locale (`05-06` §9) |
| Decimal | 1,234.56 | ১,২৩৪.৫৬ | Two decimals for money |
| Currency | BDT 12,500.00 | ৳ ১২,৫০০.০০ | BDT primary; symbol ৳ in Bengali locale. Never "Tk" in system content |
| Date | 14/08/2026 | ১৪/০৮/২০২৬ | DD/MM/YYYY (`05-06` §9). Never MM/DD |
| Date, long form | 14 August 2026 | ১৪ আগস্ট ২০২৬ | Bengali month names in the Bengali locale |
| Time | 2:30 PM | ২:৩০ PM equivalent | 12-hour; stored UTC, displayed Asia/Dhaka |
| Duration | 2 h 30 min | — | Stored in minutes (`05-02` DM-08) |
| Percentage | 12.5% | ১২.৫% | No space before % |
| Phone | 16743 · +8801XXXXXXXXX | same | Hotline as five digits, no formatting |
| Ranges | 5–10 days | — | En dash, no spaces |
| Ordinals | 1st, 2nd, 3rd | — | No superscript |

**Rules**

| # | Rule |
|---|---|
| **N-01** | Spell out zero to nine in prose; use numerals in UI, tables, data and anything a user scans. |
| **N-02** | Always use numerals with a unit: "3 parts", "5 minutes", "2 branches". |
| **N-03** | Never abbreviate the currency to "Tk" or "৳" without a number. Never write "BDT ৳". |
| **N-04** | Never write a bare date without a year in content that is retained (documents, records, contracts). |
| **N-05** | Financial figures are never rounded in content; state the exact value or state the rounding rule (`MD-039`). |
| **N-06** | A number that appears in both a document and a system field must come from the field, never be typed. |

---

## 5. Punctuation

| Mark | Rule |
|---|---|
| Full stop | End full sentences everywhere, including tooltips, error messages and dialog body text. **Omit** on labels, buttons, headings, table cells and single-phrase list items. |
| Comma | Use the serial (Oxford) comma: "parts, labour, and VAT". It removes ambiguity in itemised lists, which this system produces constantly. |
| Colon | Use to introduce a list or a value: "Status: In repair". No capital after a colon unless a proper noun. |
| Semicolon | Avoid in UI. Permitted in SOPs and legal content. |
| Em dash | Avoid in UI. Use in prose sparingly, spaced en dash `–` in tables and ranges. |
| Ellipsis | Only on a control that opens a further step requiring input: "Reassign…". Never for suspense or omission in UI. |
| Ampersand | Only inside a registered name. Write "and" everywhere else. **Never in a file or folder name** (`AF-12`). |
| Slash | Avoid. "Approve or reject", not "Approve/Reject". Permitted in dates and technical paths. |
| Exclamation mark | Never in ERP content. Not in success messages, not in notifications, not in training. |
| Question mark | Only on an actual question to the user. Not on dialog titles (§3.3). |
| Quotation marks | Double for quoted text; single inside double. Never for emphasis. |
| Parentheses | Sparingly. If the content only works with the parenthetical, rewrite the sentence. |
| Apostrophe | Possessive on singular nouns ending in s takes 's: "the business's". |

---

## 6. Capitalisation of business objects

The single most common style failure in ERP content is capitalising business objects for
emphasis. **Do not.**

| Write | Not |
|---|---|
| Create a service order for this device. | Create a Service Order for this Device. |
| The estimate is awaiting customer approval. | The Estimate is awaiting Customer Approval. |
| Assign a technician from the dispatch board. | Assign a Technician from the Dispatch Board. |

**Capitalise only when:**

| Case | Example |
|---|---|
| It is the exact on-screen label being cited in help or training | Select **Create service order**. |
| It is a proper noun | Dhaka, Samsung, Odoo, Mushak 6.3 |
| It is a registered product, plan or programme name (`VB-010`) | Privilege Diamond, RAMC Standard |
| It is a defined term inside a legal document, declared in that document's definitions clause | "the Services" as defined in clause 2 |

---

## 7. Lists, tables and structure

| # | Rule |
|---|---|
| **L-01** | Introduce every list with a stem sentence ending in a colon. |
| **L-02** | Keep list items grammatically parallel — all verbs, or all nouns, never mixed. |
| **L-03** | Numbered lists for sequence and procedure. Bulleted lists for unordered sets. Never bullet a procedure. |
| **L-04** | One action per numbered step in an SOP or help article. A step containing "and then" is two steps. |
| **L-05** | Sentence case and no terminal punctuation on list items that are fragments; full stops on items that are sentences. Never mix within one list. |
| **L-06** | Table headers are sentence case, terse, and name the unit where one applies: "Effort (PW)". |
| **L-07** | Never use a table for layout. Tables carry data; screen readers announce them as data (`CG-011`). |
| **L-08** | Headings are a hierarchy, not a font size. Never skip a level (H2 → H4). |
| **L-09** | A heading describes the content beneath it well enough that a reader scanning only headings understands the document (WCAG SC 2.4.6). |
| **L-10** | Maximum three heading levels in help articles, five in specifications. |

---

## 8. Words and phrases

### 8.1 Banned

| Banned | Use instead | Why |
|---|---|---|
| please, kindly | (nothing) | Adds length to every label; insincere at scale |
| sorry, we apologise | (state the fact and the remedy) | Apology in a system message reads as evasion |
| simply, just, easily, quickly | (nothing) | Tells a struggling user their difficulty is their fault |
| oops, whoops, uh-oh | (state what happened) | Trivialises failure in a system handling money and customer property |
| please note, it should be noted | (state the thing) | Filler |
| in order to | to | Filler |
| utilise | use | |
| leverage (as a verb) | use | |
| facilitate | help, allow, do | |
| terminate | end, cancel, close | Ambiguous against the employment sense |
| execute (of a user action) | run, do, complete | Ambiguous |
| invalid, illegal (of user input) | (state the required format) | Blames the user; "illegal" has a legal meaning here |
| abort, kill | cancel, stop | |
| whitelist / blacklist | allowlist / blocklist | |
| master / slave | primary / replica | |
| sanity check | validation check | |
| the customer is required to | you must / the customer must | |
| N/A alone in a data field | (state why, or leave empty by design) | "N/A" hides whether the value is unknown, not applicable or not yet captured |

### 8.2 Preferred forms

| Prefer | Over | Note |
|---|---|---|
| service order | job, ticket, case, request | `CG-004` binds this to `fix.service.order` |
| technician | engineer, tech, mechanic | "engineer" is reserved for marketplace freelance engineers (`M12`) |
| branch / service centre | shop, outlet, store | "service centre" for customer-facing content; "branch" internally |
| device | unit, item, product, machine | "product" means a catalogue item (`M37`) |
| part | spare, component, item | |
| estimate | quote, quotation | "quotation" is reserved for `M36` commercial quotations to organisations |
| customer | client, consumer, user | "client" is reserved for contracted corporate accounts |
| sign in / sign out | log in / login / logout | "login" is a noun only |
| set up (verb) / setup (noun) | — | |
| email | e-mail | |
| online / offline | on-line / off-line | |
| back end / front end (nouns) | backend / frontend | Adjectival forms are hyphenated: back-end service |
| cannot | can not, can't | No contractions in UI, notifications or documents |

### 8.3 Contractions

**No contractions** in UI labels, error messages, notifications, documents, SOPs or legal
content. Contractions are permitted in help articles, training material and change
communications, where a conversational register aids comprehension.

---

## 9. Formatting and emphasis

| Element | Convention |
|---|---|
| UI element cited in help or training | **Bold**: Select **Create service order**. |
| Field value or user input | `Code font`: enter `SR-2026-114882` |
| File name, path, identifier, model | `Code font`: `fix.service.order`, `MD-021` |
| Emphasis in prose | *Italic*, used rarely |
| Key term on first use | **Bold** once, then plain |
| Never | ALL CAPS for emphasis, underline for emphasis, colour as the only signal (`CG-011`) |
| Link text | Describes the destination. Never "click here", "read more", "this link" (WCAG SC 2.4.4) |

---

## 10. Content that appears in more than one place

The same fact appears in a UI label, a notification, a printed document, a help article, an SOP
and a training slide. **Divergence between them is the most damaging content defect this
programme can produce**, because each surface is authoritative to whoever is reading it.

| # | Rule |
|---|---|
| **X-01** | One canonical wording per fact, owned by one file. Every other surface quotes it. |
| **X-02** | The canonical owner by content type: status labels → `MD-027`; field labels → `UI-003`; error messages → `UI-004`; SLA definitions → `MD-028`; legal terms → the `LG` file; statutory document wording → the `DT` file. |
| **X-03** | Help and training **cite** UI labels verbatim, in bold. They never paraphrase them. When a label changes, every citation is updated in the same release. |
| **X-04** | A notification that reports a state uses the state's canonical customer-facing label from `MD-027`, not the internal state name. |
| **X-05** | Where a legal position is stated in more than one place — service terms, warranty certificate, intake receipt, help article — the `LG` file is canonical and the others quote it. |

---

## 11. Applying this guide by content type

| Content type | Case | Person | Contractions | Full stops on fragments | Notes |
|---|---|---|:--:|:--:|---|
| UI labels, buttons, menus | Sentence | — | No | No | Terse; front-load |
| Error and validation messages | Sentence | Second | No | Yes | Three-part structure (§3) |
| Empty states and first-run | Sentence | Second | No | Yes | State the next action |
| Notifications — SMS | Sentence | Second | No | Yes | Character budget governs (`NT-004`) |
| Notifications — email | Sentence | Second | No | Yes | Subject ≤ 55 characters |
| Printed documents | Sentence, except statutory titles | Third | No | Yes | `DT-001` layout standard |
| Legal documents | Sentence for headings | Third | No | Yes | Numbered clauses; defined terms capitalised |
| SOPs | Sentence | Imperative | No | Yes | One action per step |
| Help articles | Sentence | Second | Yes | Yes | Cite UI labels in bold |
| Training | Sentence | Second | Yes | Yes | Conversational register permitted |
| Knowledge articles | Sentence | Imperative | No | Yes | Safety warnings before procedure |
| Reports and dashboards | Sentence | — | No | No | Metric names from `RP-001` |
| API and developer content | Sentence | Second | No | Yes | Code identifiers verbatim |
| Change communications | Sentence | Second/first plural | Yes | Yes | "We" permitted |

---

## 12. Enforcement

| Mechanism | How |
|---|---|
| Template conformance | Every file is authored from `_templates/` (`CP-09`) |
| Definition of Done | `CG-008` includes a style check as a gate item |
| Automated linting | Banned-word list (§8.1), sentence length (S-01), spelling dictionary set to en-GB, heading-level skip detection. Run in CI on the content repository |
| Review | Class D content is style-reviewed by Content Design (`CG-002` §5.4) |
| Audit | `AUDIT_Checklist_Recurring.md` §E6 samples terminology and style conformance; target defect rate under 2% |

**Waivers.** A style rule may be waived only by the Content Design Lead, time-boxed, and logged
in `RF-006`. A waiver never applies to §3 error message structure or §10 cross-surface
consistency — those are contractual (`PS-09`, `BR-STD-04`) rather than stylistic.

---

## 13. Related documents

| Document | Relationship |
|---|---|
| [`CG-004_Terminology_and_Controlled_Vocabulary_Standard.md`](CG-004_Terminology_and_Controlled_Vocabulary_Standard.md) | Which word; this file governs how it is written |
| [`CG-010_Bilingual_Content_Policy.md`](CG-010_Bilingual_Content_Policy.md) | Which content is bilingual |
| [`CG-011_Accessibility_Content_Standard.md`](CG-011_Accessibility_Content_Standard.md) | Reading level, link text, alt text, error-message accessibility |
| `VB-001` ERP Product Voice & Tone Guide | Voice and tone; this file governs mechanics |
| `VB-006` Design System Content Standards | Component-bound copy rules |
| `BN-002` Bengali Translation Standard | The Bengali counterpart of this guide |
| `BN-005` i18n Key, Placeholder & Pluralisation Rules | Why S-05 exists |
| `UI-004` Validation & Error Message Library | Where §3 is applied at scale |
| `05-06` §9 | Localisation standards this guide implements |

---

## 14. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Ratifies en-GB and sentence case as programme conventions, defines the three-part error structure, banned-word list and cross-surface consistency rules | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Conforms to the standard template
- [x] en-GB decision evidenced against the existing 123-file specification repository
- [x] Number, date and currency conventions reconcile to `05-06` §9
- [x] Error message rules trace to `BR-STD-04` and `PS-09`
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; Bengali conventions are `BN-002`
- [ ] Named approver recorded — **pending**
- [x] Registered in the Content Master Index
- [x] Website en-US conflict logged as a decision in `RF-006`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
