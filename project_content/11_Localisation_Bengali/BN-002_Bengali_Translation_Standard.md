---
id: BN-002
title: Bengali Translation Standard
project: 1000FiX ERP System v2.0
content_type: Standard
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-17
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Localisation Lead
author: Localisation with Content Design and a native Bengali linguistic reviewer
reviewers: [Content Design Lead, Programme Content Lead, Enterprise Architecture, Legal & Compliance, Brand, Contact Centre Manager]
approver: Programme Content Lead
content_class: E
purpose: >
  Closes the register question that CG-010 §12 item 1 and CG-004 §10 item 1 leave open, and
  fixes the writing rules every Bengali string in the system must follow: register, honorific
  address, verb form, loanword and code-mixing policy, sentence construction, punctuation and
  tone under failure. Bengali technical writing has genuine register choices. Making them
  inconsistently — one portal formal, one colloquial, one machine-flavoured — makes the product
  feel foreign to its own users, and no amount of terminology control fixes it afterwards.
traces_to: [CG-010 §7, CG-010 §12 item 1, CG-004 §7, CG-004 §10 item 1, CG-003, VB-001, VB-002, UI-012 §9 item 1, BN-001, BN-003, BN-018, 04-00 PS-03]
priority: P0
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: project_content/00_Content_Governance_and_Standards/CG-010 §7 — the register question stated as open, with the proposed position of modern standard Bengali (চলিত) plus a declared formal register for Class A and B
    verified: 2026-08-17
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-004 §7 — "BN-002 must decide whether one register serves all ERP surfaces"; §10 item 1
    verified: 2026-08-17
    class: P1
  - source: 1000_fix_corporate_website project_content LOCALIZATION/Bengali Language/BN-001 Bengali Translation Guidelines v1.0 §1.2 — modern colloquial Bengali (চলিত ভাষা) selected for the consumer audience; §2 four brand voice traits in Bengali
    verified: 2026-08-17
    class: P1
  - source: project_content/03_UI_Copy_and_Microcopy/03B_Portals/UI-012 §9 open question 1 — "Bengali imperative register — করুন (formal) or কর (informal)? BN-002 decides", marked blocking on every string
    verified: 2026-08-17
    class: P1
  - source: 1000fix_ERP_Module/04_Portals_and_Applications/04-00 §P01 Design Requirements and §P02 non-negotiable #3
    verified: 2026-08-17
    class: P1
  - source: Bengali grammatical convention — three second-person registers, সম্ভ্রমাত্মক (আপনি / করুন), সাধারণ (তুমি / করো) and তুচ্ছার্থ (তুই / কর); সাধু ভাষা is the archaic literary register displaced by চলিত ভাষা in modern standard prose
    verified: 2026-08-17
    class: P2
supersedes: none
review_due: 2026-11-17
---

# BN-002 — Bengali Translation Standard

> **This file answers a question three approved documents have left open and one blocking
> question a copy pack raised.** `CG-010` §12 item 1, `CG-004` §10 item 1 and `UI-012` §9 item 1
> all defer to `BN-002`. No `BN` string bundle may be produced until §2 and §3 are ratified.
>
> The decision is not a preference. Bengali distinguishes three grades of second-person address,
> and one of them — **তুই / কর** — is what an adult says to a child or a servant. Applied to
> 200–400 field technicians on a company device, it is not informality. It is an insult
> delivered several hundred times a day by the employer.

---

## 1. Purpose

| | |
|---|---|
| **What this governs** | Register, address, verb form, loanwords and code-mixing, sentence construction, punctuation, tone under failure, and the writing rules for every Bengali string, document and script in the system |
| **What it does not govern** | Which content is Bengali (`CG-010`, `BN-001`); which **term** is used (`BN-003`); what is never translated (`BN-004`); typography (`BN-006`); formats (`BN-007`); how it is reviewed (`BN-018`) |
| **What breaks without it** | A product where the technician app addresses the user as an inferior, the customer portal as a stranger and the invoice as a court summons — all technically correct Bengali, all from different translators |

**Relationship to `CG-003`.** `CG-003` is the English style guide. This file is its Bengali
counterpart, not its translation: the two languages have different problems. `CG-003` legislates
sentence case, which Bengali does not have; this file legislates honorific grade, which English
does not have. Rules that are language-independent — one canonical wording per fact, no
concatenation, remedy-bearing errors — are stated once in `CG-003` and are **not** repeated here.

---

## 2. The register decision — CLOSED

### 2.1 The decision

| # | Decision |
|---|---|
| **RD-A** | **Modern standard Bengali — চলিত ভাষা — is the register for every ERP surface.** UI, notifications, documents, help, training, knowledge, IVR and legal alike |
| **RD-B** | **সাধু ভাষা is not used anywhere in the ERP.** No exception, no legal carve-out |
| **RD-C** | Class A (statutory) and Class B (legal) content uses a **formal sub-register within চলিত** — §2.3. It is a change of *diction and sentence construction*, not of grammatical register |
| **RD-D** | Regional dialect is not used. Standard Bengali serves all eight divisions (`MD-006`) |
| **RD-E** | The decision applies to **every language pair direction**, including Bengali-native content whose English is the translation (`BN-001` §6) |

> **`CG-010` §7 proposed "modern standard Bengali (চলিত) with a declared formal register for
> Class A and B". `RD-A` and `RD-C` adopt that proposal with one correction:** the formal
> treatment is a sub-register, not a separate register. Stating it as a separate register invites
> a translator to reach for সাধু ভাষা, which is what `RD-B` forbids. The distinction is the whole
> reason `RD-C` is worded as it is.

### 2.2 Why a single register, and why not সাধু

| Consideration | Effect on the decision |
|---|---|
| The corporate website already selected চলিত for consumer content (`BN-001` website set) | Continuity. A customer who reads the website in চলিত and the portal in সাধু experiences two companies |
| The same customer reads website, portal, SMS, invoice and warranty | One register or a visibly seamed product |
| সাধু ভাষা has been out of general use in Bangladeshi prose for decades | It reads as archaic, not as authoritative. Government forms that use it do so by inertia |
| Branch and field staff have mixed formal education | Register complexity is a comprehension cost paid by the least advantaged users |
| Mixing registers within one product is itself a defect | Argues for one decision plus a narrow, declared exception — `RD-C` |
| Statutory documents sit alongside government forms | Argues for formality of **diction**, which `RD-C` gives, not archaism of **grammar**, which it does not |

### 2.3 The Class A / B formal sub-register

Applies to Class A statutory and Class B legal content only — `LG-002`, `LG-008`, `LG-013`,
`LG-015`, the `DT` statutory set, contract and warranty documents.

| Aspect | Standard surfaces | **Class A / B** |
|---|---|---|
| Grammatical register | চলিত | চলিত — **unchanged** |
| Address | আপনি | আপনি, or the impersonal third person for obligations of the company |
| Diction | Everyday word choice — সময়, টাকা, শুরু | Precise legal-administrative vocabulary — মেয়াদ, প্রদেয়, কার্যকর |
| Sentence length | ≤ 20 words | May exceed where the obligation requires it; clarity still governs |
| Contraction and ellipsis | Permitted | Not used |
| Statutory terms | As `BN-004` | As `BN-004`, **and never paraphrased** (`CG-004` `T-05`) |
| Precedence clause | n/a | Present, stating that English governs in a dispute (`CG-010` §4.1) |

| # | Rule |
|---|---|
| **FR-01** | The formal sub-register changes **word choice and construction**, never grammar or honorific grade |
| **FR-02** | A Class A or B string that appears on a **UI surface** — a consent line, a warranty note in the booking flow — uses the **standard** register. The formality belongs to the instrument, not to the interface (`UI-042`) |
| **FR-03** | Where a formal Bengali word has no clear meaning to a general reader, the standard word is used and the formality is achieved by construction instead |

---

## 3. Address and verb form — CLOSED

### 3.1 The decision

**`UI-012` §9 item 1 asked: করুন or কর. The answer is করুন, and it is not close.**

| Grade | Pronoun | Imperative | Who it addresses | Use in the ERP |
|---|---|---|---|:--:|
| সম্ভ্রমাত্মক — honorific | **আপনি** | **করুন** | An adult addressed with respect | **Everywhere. The only permitted grade** |
| সাধারণ — familiar | তুমি | করো | A friend, a younger relative | **Never** |
| তুচ্ছার্থ — intimate/diminutive | তুই | কর | A small child, an intimate, or an inferior | **Never** |

| # | Rule |
|---|---|
| **AD-01** | **আপনি and its verb forms are used on every surface, to every audience, without exception** — customers, technicians, riders, sellers, agents, auditors, employees |
| **AD-02** | Imperatives take the **-উন / -ন** honorific form: করুন, দিন, পাঠান, নির্বাচন করুন, সংগ্রহ করুন |
| **AD-03** | **তুমি and তুই forms are prohibited in all content, including voice, chatbot and marketing.** A chatbot that adopts তুমি to sound friendly is a defect, not a personality |
| **AD-04** | The system **never** addresses itself in the first person plural in a way that assigns blame to the user. See §7 |
| **AD-05** | Where English uses a bare noun label — "Parts", "Payment" — Bengali uses a bare noun too. Do not inflate every label into a sentence with করুন attached |
| **AD-06** | The honorific **-জন / -গণ** plural is used for people (গ্রাহকগণ), never the inanimate plural (গুলো) |

> **Why `AD-03` matters more than it looks.** A technician application that says "কাজ শুরু কর"
> is grammatically correct and socially unacceptable. `P02` targets daily active usage above 95%
> among a workforce with high turnover. Adoption failures of this kind are never reported as
> language defects; they are reported as "the technicians prefer paper".

### 3.2 Reference to the company and the user

| Concept | Bengali | Note |
|---|---|---|
| The company, in customer content | **আমরা** | First person plural. Warm, accountable |
| The company, in Class A/B | **কোম্পানি** or the registered entity name | Impersonal; matches the instrument's voice |
| The user | **আপনি** | Never the third person about a present reader |
| The user's possessions | **আপনার ডিভাইস**, **আপনার সার্ভিস** | Possession makes the sentence concrete and short |
| A third party — technician, rider | Their role name from `BN-003` + honorific verb | টেকনিশিয়ান আসছেন, not আসছে |

---

## 4. Loanwords and code-mixing

Bengali as spoken in Bangladeshi technical and commercial life contains English. Pretending
otherwise produces Bengali that is correct and unreadable. The policy is **four tiers**, and the
tier is a property of the term, recorded in `BN-003`.

| Tier | Treatment | When | Examples |
|:--:|---|---|---|
| **1** | **Keep in Latin script** | Statutory names, brands, product names, technical identifiers, codes, units | `Mushak 6.3`, `BIN`, `bKash`, `Samsung`, `SR-2026-114882`, `IMEI`, `GPS`, `SLA`, `L1/L2/L3` |
| **2** | **Transliterate into Bengali script** | An English word that is the term Bangladeshi users actually say, with no settled Bengali equivalent | ল্যাপটপ, এসি, প্রিন্টার, ব্যাটারি, স্ক্যান, ভ্যান স্টক, ইনভয়েস, ওয়ারেন্টি |
| **3** | **Translate** | A settled Bengali term exists and is in ordinary use | মেরামত (repair), গ্রাহক (customer), রসিদ (receipt), স্বাক্ষর (signature), বাতিল (cancel), অনুমোদন (approve) |
| **4** | **Translate with the English in brackets on first use** | A term that is unfamiliar in both languages, or an abbreviation the user must recognise on a document | বার্ষিক রক্ষণাবেক্ষণ চুক্তি (AMC), পরিষেবা ক্রেডিট (service credit) |

| # | Rule |
|---|---|
| **LW-01** | **The tier is decided once, in `BN-003`, per term.** A translator does not choose the tier at translation time |
| **LW-02** | **Never transliterate a Tier 1 item.** `মুশক ৬.৩` is a defect: the form's name is `Mushak 6.3` (`CG-004` `T-05`, `BN-004` `DN-01`) |
| **LW-03** | **Never translate a Tier 2 item into an invented Bengali coinage.** Replacing ল্যাপটপ with কোলে-বসানো-কম্পিউটার is not localisation |
| **LW-04** | **Never leave a Tier 3 term in English** because the translator finds it faster. "Approve করুন" is code-mixing where a settled term exists — অনুমোদন করুন |
| **LW-05** | Tier 4 brackets appear **on first use per surface**, not on every occurrence. On a document, first use per page |
| **LW-06** | A Latin-script term inside Bengali carries a **`lang` attribute** (`VB-009` `MX-04`, `CG-011` BA-02). Without it a screen reader pronounces "Mushak" with Bengali phonology |
| **LW-07** | Latin inside Bengali sets in Inter, one step smaller (`VB-009` `MX-02`, `MX-03`) |
| **LW-08** | **Code-mixing is more restricted in Class A and B than in UI.** A statutory document uses Tier 1 and Tier 3 only; Tier 2 is permitted only where the transliterated form is itself the established term |

### 4.1 The English-verb-plus-করুন pattern

The single most common defect in Bangladeshi software Bengali.

| Defect | Correct | Why |
|---|---|---|
| Approve করুন | **অনুমোদন করুন** | Tier 3 term exists |
| Cancel করুন | **বাতিল করুন** | Tier 3 |
| Submit করুন | **জমা দিন** | Tier 3 |
| Scan করুন | **স্ক্যান করুন** | **Not a defect** — স্ক্যান is Tier 2 in `BN-003`; no settled Bengali equivalent is in use |
| Sync করুন | **সিঙ্ক করুন** | Tier 2 |
| Download করুন | **ডাউনলোড করুন** | Tier 2 |

> The pattern is only a defect when a Tier 3 term exists. `BN-003` is the arbiter; a translator
> who cannot find the term raises it rather than guessing (`BN-003` §10).

---

## 5. Sentence construction

| # | Rule |
|---|---|
| **SC-01** | **Bengali is subject–object–verb.** The verb goes last. A translation that preserves English word order reads as machine output even when every word is right |
| **SC-02** | **Active voice.** Bengali passive constructions are heavy and evasive; they are also how translated software Bengali usually sounds |
| **SC-03** | One idea per sentence. Bengali tolerates long sentences grammatically and readers do not |
| **SC-04** | **Sentence budgets are `VB-002` budgets applied to Bengali**: ≤ 12 words on `P02`, ≤ 20 on `P01`. Bengali runs 20–40% longer than English (`CG-010` `BC-01`), so the English must be shorter still |
| **SC-05** | **Never build a sentence from fragments.** Bengali word order makes concatenation untranslatable (`CG-003` S-05, `BN-005` `KP-05`) |
| **SC-06** | Avoid conjunct-heavy synonyms where a plainer word exists. Conjuncts break at small sizes on the `P02` device class (`BN-006` §3) |
| **SC-07** | **Do not translate English idiom.** "We've got you covered" has no Bengali; write the obligation instead |
| **SC-08** | Bengali has **no letter case**. Never let meaning rest on capitalisation in the English source (`CG-010` `BC-02`) |
| **SC-09** | Bengali has **no grammatical gender on verbs or adjectives**. Gendered English constructions have no Bengali counterpart and must not be reintroduced by naming a gender |
| **SC-10** | Prefer the **-ছে / -ছেন** present continuous for in-progress states and the **-হয়েছে** perfect for completed ones. Status labels are a state, not an action (`MD-027`) |

### 5.1 Worked examples

| English | Machine-flavoured Bengali | **Approved Bengali** | What changed |
|---|---|---|---|
| Scan the part | পার্টস স্ক্যান কর | **পার্টস স্ক্যান করুন** | Honorific grade (`AD-02`) |
| Your device is ready for collection | আপনার ডিভাইস সংগ্রহের জন্য প্রস্তুত করা হয়েছে | **আপনার ডিভাইস প্রস্তুত। সংগ্রহ করুন।** | Passive removed, split into two short sentences (`SC-02`, `SC-03`) |
| You are not certified for {brand} | আপনি {brand} এর জন্য সার্টিফাইড না | **{brand} ওয়ারেন্টি কাজের জন্য আপনার সার্টিফিকেশন নেই। ডিসপ্যাচকে পুনরায় বরাদ্দ করতে বলুন।** | Remedy added (`PS-09`); blame removed (§7) |
| Approve {amount} | Approve করুন {amount} | **{amount} অনুমোদন করুন** | Tier 3 term (`LW-04`); placeholder before verb (`SC-01`) |
| Something went wrong | কিছু ভুল হয়েছে | **আমাদের প্রান্তে একটি সমস্যা হয়েছে। আবার চেষ্টা করুন। সমস্যা থাকলে রেফারেন্স {ref} জানান।** | Ownership, remedy, reference (§7) |
| No slots on {date} | {date} এ কোন স্লট নেই | **{date} তারিখে কোনো সময় খালি নেই। সবচেয়ে কাছের সময় {next_date}।** | Next action given; কোন → কোনো spelling (§6) |

---

## 6. Orthography and punctuation

| Item | Standard |
|---|---|
| Sentence terminator | **দাঁড়ি — `।`** (U+0964). Never a Latin full stop at the end of a Bengali sentence |
| Question and exclamation | `?` and `!` as in English. Bengali has no distinct forms |
| Comma, colon, semicolon | Latin `,` `:` `;` |
| Quotation | Bengali convention uses `“ ”`. Straight quotes are not used |
| Parentheses | Latin `( )` |
| Hyphen and dash | Latin. An en dash in a range: {from}–{to} |
| Ellipsis | `…` single character, never three dots |
| Abbreviation | Bengali abbreviations take দাঁড়ি only at sentence end; do not invent Bengali abbreviations for English acronyms |
| **Spelling authority** | **Bangla Academy** modern standard orthography |
| কোন / কোনো | **কোনো** for "any/some"; কোন only for "which". The most frequent spelling defect in Bengali UI |
| Chandrabindu | Retained where the Bangla Academy form retains it (চাঁদ, দাঁড়ি) |
| ZWJ / ZWNJ | Only where the Bangla Academy form requires it. See `BN-006` `EN-03` — joiner misuse is a rendering and search defect, not a style choice |
| Numerals | Governed by `BN-007`. **Not** decided per string |

| # | Rule |
|---|---|
| **OR-01** | **Bangla Academy orthography is the spelling authority.** Where a translator's habitual spelling differs, the Academy form governs |
| **OR-02** | Text is stored **Unicode NFC** (`BN-006` `EN-02`). Two visually identical spellings that differ in normalisation are two strings to a search index |
| **OR-03** | A dedicated Bengali spell check runs on every bundle before G4 (`BN-018` `LQ-04`) |
| **OR-04** | Never use a Latin full stop to end a Bengali sentence and never use দাঁড়ি to end an English one, including in mixed-script strings |

---

## 7. Tone under failure

`VB-001` sets the English tone principles. Bengali adds a specific risk: **the most natural
Bengali construction for an error assigns fault to the reader**, and the honorific register makes
that assignment sound formal rather than rude — which is worse.

| # | Rule |
|---|---|
| **TN-01** | **Never write "আপনি ভুল করেছেন"** or any construction that makes the user the grammatical agent of the failure |
| **TN-02** | Where the system failed, **say so in the first person plural** — আমাদের প্রান্তে সমস্যা হয়েছে |
| **TN-03** | Where the input was invalid, **describe the required form**, not the user's error: "IMEI ১৫ সংখ্যার হতে হবে", not "আপনি ভুল IMEI দিয়েছেন" |
| **TN-04** | **Every error names the next action** (`PS-09`, `NFR-078`). A Bengali error without a remedy is the same defect as an English one |
| **TN-05** | **দুঃখিত is used once, where the company is at fault, and never as decoration.** An apology on every message devalues the one that matters |
| **TN-06** | Safety and custody content is **direct and unhedged**. Politeness particles that soften an instruction are removed (`UI-012` §3.5, `VB-002` T-06) |
| **TN-07** | Destructive confirmations state the **consequence**, in Bengali, before the verb — the reader must reach the consequence before reaching the button (`UI-007`) |
| **TN-08** | Financial and legal outcomes are stated **plainly and without softening**. A refund deduction is named as a deduction |

---

## 8. Register by surface — the quick table

| Surface | Register | Address | Sentence budget | Notable rule |
|---|---|---|:--:|---|
| `P01` customer | চলিত, warm | আপনি | ≤ 20 words | `TN-05` — one apology, where earned |
| `P02` technician | চলিত, direct | আপনি | ≤ 12 words | `TN-06` safety exception; `AD-03` is the adoption risk |
| `P03` admin | চলিত, neutral | আপনি | ≤ 20 words | Full technical vocabulary permitted |
| `P09` rider | চলিত, very direct | আপনি | ≤ 10 words | Read in motion; shortest budget in the system |
| `P10` contact centre | চলিত, spoken | আপনি | Spoken cadence | Authored natively (`BN-017`) |
| Notifications, SMS | চলিত, terse | আপনি | 70-character segment reality (`BN-014`) | Every character costs money |
| `DT` customer documents | চলিত | আপনি | — | Field labels are nouns, not sentences |
| `DT` statutory, `LG` | **চলিত + formal sub-register** (`RD-C`) | আপনি / impersonal | — | Precedence clause; `LW-08` |
| Help, training, knowledge | চলিত, instructional | আপনি | — | Often Bengali-native (`BN-001` §6) |
| IVR | চলিত, spoken | আপনি | ≤ 12 spoken words | Description before option (`NT-019` `IV-01`) |
| Chatbot | চলিত, conversational | আপনি | ≤ 20 words | `AD-03` — never তুমি to sound friendly |

---

## 9. What a translator must be given

A translator handed a spreadsheet of strings produces defects that no review can economically
remove. `BN-018` catches them; this section prevents them.

| Item | Required |
|---|---|
| The English source | Yes |
| **The key** | Yes — it names the surface, component and slot (`UI-001` §3.1) |
| **A context note** | Yes — what the string is, where it appears, who reads it (`BN-005` `KP-07`) |
| **A screenshot or the running surface** | Yes for any string in a constrained slot |
| **The character or word budget** | Yes, as a **Bengali** budget (`VB-006` `DS-04`) |
| **Placeholder documentation** | Yes — name, source field, example value, and whether it may be empty |
| **The `BN-003` term extract** for the strings in scope | Yes |
| **The `BN-004` do-not-translate list** | Yes |
| **The tier** for each in-scope loanword | Yes (`LW-01`) |
| The previous approved translation, if one exists | Yes, from the TM (`BN-008`) |

| # | Rule |
|---|---|
| **TX-01** | **A string sent for translation without a context note is a defect by the requester**, not by the translator |
| **TX-02** | A translator may **refuse** a batch that does not meet §9 and the refusal is not a service-level breach |
| **TX-03** | Questions are raised as **queries against the English source**, not resolved silently in the Bengali. A recurring query means the English is wrong (`CG-003`) |

---

## 10. Prohibited

| # | Prohibited | Why |
|---|---|---|
| **PR-01** | Machine translation on any published surface | `CG-010` MT-01; `04-00` §P01; never waivable (`CG-008` B-09) |
| **PR-02** | Post-edited machine translation on customer- and field-facing content | `CG-010` MT-03 |
| **PR-03** | তুমি or তুই forms | `AD-03` |
| **PR-04** | সাধু ভাষা | `RD-B` |
| **PR-05** | Regional dialect | `RD-D` |
| **PR-06** | Transliterating a Tier 1 item | `LW-02`, `BN-004` |
| **PR-07** | Inventing a Bengali coinage for an established Tier 2 term | `LW-03` |
| **PR-08** | Rendering Bengali as an image to guarantee a font | `VB-009` `BR-06`, `CG-011` AT-07 |
| **PR-09** | Mixing numeral systems within one value | `VB-009` `NU-01`, `BN-007` |
| **PR-10** | Translating a string list without context | `TX-01` |
| **PR-11** | Softening a safety, financial or legal statement to sound polite | `TN-06`, `TN-08` |
| **PR-12** | Two different English strings given the same Bengali, or one English string given two Bengali forms | `BN-018` `LQ-11` |

---

## 11. Dependencies

| Depends on | Why |
|---|---|
| `CG-003` ERP Product Content Style Guide | The English rules that make the Bengali possible |
| `CG-004` §7 | Records the register question this file closes |
| `CG-010` §7, §12 item 1 | The proposal `RD-A`/`RD-C` adopt |
| `BN-001` §3 | Which surface uses which row of §8 |
| `BN-003` | The tier decision per term (`LW-01`) |
| `BN-004` | Tier 1 membership |
| `BN-006` | Conjunct and normalisation consequences of `SC-06`, `OR-02` |
| `BN-007` | The numeral decision `PR-09` refers to |
| `VB-001`, `VB-002` | English tone principles this extends |

---

## 12. Enforcement

| Check | Mechanism | When |
|---|---|---|
| তুমি / তুই verb forms | **Automated pattern scan** on every bundle | Every commit |
| English verb + করুন where a Tier 3 term exists | Automated, against the `BN-003` tier column | Every commit |
| Latin full stop ending a Bengali sentence | Automated | Every commit |
| কোন used for "any" | Automated | Every commit |
| Tier 1 item transliterated | Automated, against `BN-004` | Every commit |
| Sentence budget in Bengali | Automated word count per slot | Every commit |
| Register conformance and tone | **G4 human review** (`BN-018`) | Per surface |
| Bangla Academy spelling | Bengali spell check plus G4 | Per bundle |
| Machine translation | Translator attestation plus G4 (`CG-010` §10) | Per file |

> **The automated checks catch the frequent defects; they do not catch the expensive ones.**
> Register drift, wrong tier and a technically correct sentence that no Bangladeshi would say are
> found only at G4, in context. That is why `BN-018` exists and why `B-09` is unwaivable.

---

## 13. Open decisions

| # | Decision | Owner | Needed by | Blocks |
|---|---|---|---|---|
| 1 | **Ratify `RD-A`–`RD-E` and `AD-01`–`AD-06`** | Programme Content Lead on the Localisation Lead's recommendation | **Before W1** | Every `BN` bundle; `UI-012` §9 item 1; `CG-004` §10 item 1; `CG-010` §12 item 1 |
| 2 | Is a Bengali-language style authority named beyond Bangla Academy orthography — a house dictionary for the 4,000+ terms not in `BN-003`? | Localisation Lead | Before W2 | `BN-008` term base scope |
| 3 | Does the formal sub-register (`RD-C`) require a **separate reviewer** with legal-Bengali experience, distinct from the UI reviewer? | Localisation Lead with Legal | Before the first Class A Bengali document | `BN-015`, `BN-018` §3 reviewer roster |

---

## 14. Related documents

| Document | Relationship |
|---|---|
| [`BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md`](BN-001_Localisation_Strategy_and_Language_Coverage_Matrix.md) | Which surface uses which register row |
| [`BN-003_Bilingual_Terminology_Glossary.md`](BN-003_Bilingual_Terminology_Glossary.md) | The tier and the term |
| [`BN-004_Do_Not_Translate_and_Transliteration_Register.md`](BN-004_Do_Not_Translate_and_Transliteration_Register.md) | Tier 1 membership |
| [`BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`](BN-006_Bengali_Typography_Font_and_Numeral_Standard.md) | `SC-06`, `OR-02` |
| [`BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md`](BN-018_Localisation_QA_and_Linguistic_Signoff_Checklist.md) | Where §12's human checks run |
| [`../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md`](../00_Content_Governance_and_Standards/CG-003_ERP_Product_Content_Style_Guide.md) | The English counterpart |
| [`../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md`](../00_Content_Governance_and_Standards/CG-010_Bilingual_Content_Policy.md) | §7 register question |
| [`../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md`](../01_Voice_Brand_and_Design_Content/VB-002_Persona_and_Portal_Tone_Matrix.md) | The tone this expresses in Bengali |
| [`../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md`](../03_UI_Copy_and_Microcopy/03B_Portals/UI-012_P02_Technician_App_UI_Copy_Pack.md) | §9 item 1, closed by §3 |

---

## 15. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-17 | Initial issue. Register question closed as চলিত with a formal Class A/B sub-register; address closed as আপনি/করুন with the তুই/কর prohibition and its adoption rationale; four-tier loanword policy bound to `BN-003`; ten sentence-construction rules with worked before-and-after examples; Bangla Academy orthography adopted; eight tone-under-failure rules; translator input requirements; twelve prohibitions; nine automated enforcement checks | Programme Content Lead (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] **The register question `CG-010` §12 item 1 and `CG-004` §10 item 1 leave open is answered, not restated**
- [x] **`UI-012` §9 item 1 (করুন vs কর) is answered with the reason it is not a close call**
- [x] Loanword policy expressed as a decidable tier bound to a register, not as guidance
- [x] Rules stated so they can be automated where automation is possible, and marked human where it is not
- [x] Worked before-and-after examples given for every major rule class
- [x] Tone-under-failure treated as a Bengali-specific risk, not a translation of `VB-001`
- [x] What a translator must be supplied with is specified, with the right to refuse
- [x] All internal links resolve
- [x] Bengali counterpart — n/a; internal standard, English-only by `CG-010` §3.2
- [ ] **Ratification of §2 and §3 recorded** — outstanding; §13 item 1. **Until ratified, every `BN` bundle is provisional**
- [ ] Named approver recorded — **pending Programme Content Lead**
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] Decision logged in `RF-006` — **outstanding; `RF-006` not yet written**

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
