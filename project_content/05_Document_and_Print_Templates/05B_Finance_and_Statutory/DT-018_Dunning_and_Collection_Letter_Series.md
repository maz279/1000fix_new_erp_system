---
id: DT-018
title: Dunning and Collection Letter Series
project: 1000FiX ERP System v2.0
content_type: Document / print
template: TPL_Document_Print_Template.md
template_version: 1.0
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Finance with Legal & Compliance
author: Finance with Legal & Compliance and Content Design
reviewers: [Legal Counsel, Account Management, Collections, Contact Centre, Localisation Lead]
approver: Legal Counsel with Chief Financial Officer
content_class: B
purpose: >
  The escalating reminder series and the final-demand format, with legally reviewed tone at every
  step. Collections language carries legal constraint: a letter that threatens what cannot lawfully
  be done, or that harasses, converts a debt-recovery matter into a liability. The ladder is
  pre-approved so that it is never improvised per case.
traces_to: [M20, M08, P04, P10, DT-001, DT-017, DT-030, DT-031, LG-013, MD-026, MD-038, MD-041, BRU-CTR-05, NT-003, NT-006]
priority: P1
wave: W3
bilingual: yes
bn_counterpart: DT-018_Dunning_and_Collection_Letter_Series_BN.md
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05 BRU-CTR-05 — contract suspension for non-payment follows the defined notice sequence; it cannot be applied without it
    verified: 2026-08-15
    class: P1
  - source: project_content/04_Notification_and_Messaging/NT-006 — collections messaging carries legal tone constraints; ad-hoc wording creates harassment exposure
    verified: 2026-08-15
    class: P1
  - source: project_content/00_Content_Governance_and_Standards/CG-013 — triggers that force content into legal escalation
    verified: 2026-08-15
    class: P1
supersedes: none
review_due: 2027-02-15
---

# DT-018 — Dunning and Collection Letter Series

> ⚠ **Class B — legal.** Every letter in this series is signed off by Legal Counsel **as a set**,
> not individually. The ladder only works if each rung is proportionate to the one before it.
>
> **A collections letter can only threaten what the company will actually and lawfully do.** A
> final demand that mentions a consequence the company has no intention of pursuing is not a
> stronger letter; it is an unenforceable one, and it teaches the debtor that our letters are
> theatre.

---

## 1. Document Summary

| Item | Value |
|---|---|
| Document type | Escalating collections correspondence series |
| Owning module | `M20` Accounts Receivable, with `M08` for contract customers |
| Statutory | No — **legally constrained**. Tone, threats and process are Legal's, not Collections' |
| Recipient(s) | Debtor customer, account manager, collections file, Legal on escalation |
| Languages | **Bilingual — parallel columns.** A demand a recipient cannot read is not a demand |
| Output formats | A4 portrait letter · PDF for email · SMS and WhatsApp counterparts (`NT-006`) · registered post for the final steps |
| Numbering mask | `MD-040` — `DUN-{entity}-{yy}-{seq:06d}` per letter issued |
| Retention period | `LG-009`; **retained for the limitation period** — the letter trail is the evidence in any recovery action |

### 1.1 The ladder

| Step | Name | Trigger | Channel | Tone | Signed by |
|:--:|---|---|---|---|---|
| **0** | Courtesy reminder | 3 days **before** due date | SMS + email | Neutral, service-oriented | System |
| **1** | First reminder | Due date + 1 | SMS + email | Neutral, assumes oversight | System |
| **2** | Second reminder | Due + 15 | Email + letter | Firm, states the account is overdue | Credit Controller |
| **3** | Formal notice | Due + 30 | Letter + email + call (`P10`) | Formal, states consequences that will follow | Finance Manager |
| **4** | Pre-suspension notice | Due + 45 | Letter (registered) + email + call | Formal, names the suspension date | Finance Manager |
| **5** | Suspension notice | Per `BRU-CTR-05` sequence | Letter (registered) + email | Factual, states what has happened | Finance Manager |
| **6** | **Final demand** | Due + 60, or per contract | **Letter, registered post** | Formal legal notice | **Legal Counsel** |
| **7** | Referral notice | After final demand expires | Letter (registered) | Factual, states referral | Legal Counsel |

| # | Rule |
|---|---|
| **LD-01** | **Steps are never skipped.** `BRU-CTR-05` requires the defined sequence; a suspension applied without steps 4 and 5 is invalid and reversible |
| **LD-02** | Steps are never repeated to buy time. A step is issued once; the ladder moves forward or it stops |
| **LD-03** | Any step may be **paused** by an open dispute, an agreed payment plan, or a Legal hold — and the pause is recorded with its reason |
| **LD-04** | The intervals above are defaults. **Contract terms override them** where the contract specifies a different sequence (`DT-030`, `DT-031`) |
| **LD-05** | Steps 6 and 7 are issued **only** by Legal Counsel. Collections cannot issue a final demand |

---

## 2. Statutory Requirements

No prescribed form. Five constraints, all Legal's:

| Constraint | Source | Effect |
|---|---|---|
| No harassment | Consumer protection and general law — **pending G6** | Frequency, timing and language are bounded; `NT-003` quiet hours apply to collections contact |
| No misrepresentation of consequence | Contract and consumer law — **pending G6** | A letter may state only consequences the company will lawfully pursue |
| No disclosure to third parties | `LG-008`, data protection at `05-06` NFR-086 | A debt is not disclosed to an employer, a relative or a colleague of the debtor |
| Accuracy of the amount demanded | `DT-017` | Demanding a disputed or incorrect amount undermines the whole series |
| Contractual notice compliance | `DT-030`, `DT-031`, `BRU-CTR-05` | Where the contract specifies notice content or period, the contract governs |

### 2.1 G6 questions for Legal Counsel

| # | Question |
|---|---|
| **L1** | What language is permissible and impermissible in consumer debt collection in Bangladesh? |
| **L2** | What contact frequency and timing constraints apply? |
| **L3** | What must a valid final demand contain, and what notice period must it give? |
| **L4** | What are the limitation periods for recovery, and how do our letters affect them? |
| **L5** | What is the position on interest or late-payment charges — permitted, and at what rate, and must it be in the contract? |
| **L6** | What may be disclosed to a corporate customer's parent or group entity? |
| **L7** | At what point must a matter be referred, and to whom? |

---

## 3. Layout

**Primary format: A4 portrait letter**, `VB-004` §4 geometry with letterhead.

| Zone | Content | Bilingual |
|---|---|---|
| Header | Letterhead, letter reference, date, step designation (internal code, not printed) | Title stacked |
| Party block | Addressee and account reference left; account manager and contact right | Labels stacked |
| Body | Subject → statement of the debt → what we ask → **what happens next** → how to resolve | **Parallel columns** |
| Totals | The amount demanded, and its composition | Arabic numerals |
| Statutory block | Not used. The **consequence statement** occupies this zone | Parallel columns |
| Signature | Named signatory per §1.1, with designation | Labels stacked |
| Footer | Letter reference, `page n of m`, hotline, dispute route | English |
| Enclosure | **`DT-017` statement of account, always** | — |

| # | Rule |
|---|---|
| **L-18-a** | Every letter encloses the current `DT-017` statement. A demand without a statement is a demand the recipient cannot check |
| **L-18-b** | The **amount demanded** is stated once, prominently, and excludes disputed items (`DT-017` FM-17-b) |
| **L-18-c** | "What happens next" is a distinct, headed block on every step. Ambiguity about consequence is what makes a ladder ineffective |
| **L-18-d** | The resolution route — how to pay, how to dispute, who to call — appears on **every** step, including the final demand |
| **L-18-e** | Bengali and English are equally prominent. Neither is a "translation" of the other in appearance (`VB-004` BL-02) |

---

## 4. Field Mapping

| Label EN | Label BN | Source field | Format | Required |
|---|---|---|---|:--:|
| Letter reference | পত্র সূত্র | `MD-040` sequence | Monospace | ✔ |
| Letter date | তারিখ | `dunning.issued_at` | `DD/MM/YYYY` | ✔ |
| Step | ধাপ | `dunning.step` | Internal code | ✔ (not printed) |
| Addressee | প্রাপক | `party.legal_name` + address | Text | ✔ |
| Attention | দৃষ্টি আকর্ষণ | `party.ap_contact_name` | Text | ✔ corporate |
| Account code | হিসাব কোড | `MD-013` / `MD-015` | Monospace | ✔ |
| Contract reference | চুক্তি সূত্র | `M08.contract_ref` | Monospace | Where contracted |
| **Amount demanded** | **দাবিকৃত পরিমাণ** | Computed, excluding disputes | BDT, 2 dp | ✔ |
| Oldest item date | প্রাচীনতম বকেয়া | Computed | `DD/MM/YYYY` | ✔ |
| Days overdue | বিলম্বিত দিন | Computed | Integer | ✔ |
| Invoices covered | অন্তর্ভুক্ত চালান | `DT-010` references | List | ✔ |
| Disputed amount excluded | বাদ দেওয়া বিরোধপূর্ণ পরিমাণ | Computed | BDT, 2 dp | ✔ where any |
| Late-payment charge | বিলম্ব চার্জ | `MD-038` / contract term | BDT, 2 dp | **Only where the contract provides — G6 L5** |
| Payment deadline | পরিশোধের সময়সীমা | Computed from step | `DD/MM/YYYY` | ✔ |
| **Consequence if unpaid** | **অপরিশোধিত থাকলে পরিণতি** | Step-specific approved text | Text | ✔ |
| Payment instructions | পরিশোধের নির্দেশনা | `MD-038` bank details | Text | ✔ |
| Dispute route | বিরোধ জানানোর পথ | `M34` case route + deadline | Text | ✔ |
| Signatory | স্বাক্ষরকারী | `employee.display_name` + designation | Text | ✔ |
| Enclosure | সংযুক্তি | `DT-017` reference | Monospace | ✔ |

| # | Rule |
|---|---|
| **FM-18-a** | Consequence text is **selected from the approved set per step**, never written per case. This is the single control that keeps the series lawful |
| **FM-18-b** | Late-payment charges appear only where the contract provides for them and **G6 L5** confirms the position |
| **FM-18-c** | The amount demanded is recomputed at issue. A letter demanding an amount already paid destroys the ladder's credibility permanently |
| **FM-18-d** | Delivery evidence — email receipt, registered-post reference, call log — is recorded against the letter. **The trail is the asset** |
| **FM-18-e** | The dispute route on a final demand is not weaker than on step 1. Removing it does not increase pressure; it removes our defence |

---

## 5. Business Rules Affecting Output

| Rule ID | Effect on this document |
|---|---|
| `BRU-CTR-05` | Suspension requires the full notice sequence; steps 4 and 5 exist to satisfy it |
| `BRU-CTR-03` | On contract expiry, future scheduled work is cancelled and the customer notified — a separate event, not a collections step |
| `BRU-FIN-03` | No payment against a cancelled invoice; a cancelled invoice leaves the ladder |
| [`NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](../../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Quiet hours, frequency caps and religious/public-holiday sensitivity apply to every collections contact |
| [`NT-006_SMS_Template_Library_Finance_and_Collections.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-006_SMS_Template_Library_Finance_and_Collections.md) | The SMS counterparts of steps 0–3 are drawn from the collections SMS library, under the same Legal sign-off |
| `BRU-QMS-04` | Where a complaint is linked, closure requires confirmation with the customer — a complaint pauses the ladder (`LD-03`) |

### 5.1 Stop conditions

The ladder halts immediately, at any step, on any of these:

| # | Condition | Action |
|---|---|---|
| **ST-01** | Payment received in full | Ladder closed; confirmation issued |
| **ST-02** | Payment plan agreed and documented | Ladder paused; plan monitored; breach restarts at the paused step |
| **ST-03** | Dispute raised on the demanded amount | Ladder paused for the disputed portion; undisputed portion may continue |
| **ST-04** | Legal hold or litigation | Ladder stops; Legal takes conduct |
| **ST-05** | Customer insolvency notified | Ladder stops; Legal and Finance take conduct |
| **ST-06** | Data error found in the demand | Ladder stops, is corrected, and **restarts from step 1** — not from where it stopped |
| **ST-07** | Bereavement or documented hardship | Ladder pauses; handled by a named account manager, not by the automated sequence |

> **ST-06 and ST-07 are the two that get argued about.** Restarting after our own error is the
> cost of the error. And an automated ladder that continues through a bereavement is the single
> fastest way to turn a debt into a public complaint.

---

## 6. Variants

| Variant | When used | Difference |
|---|---|---|
| **Consumer series** | Retail customers | Plainer language; `NT-003` frequency limits tightest; hardship route prominent |
| **Corporate series** | `P04` contract accounts | Addressed to a named AP contact and copied to the account manager; references the contract's notice clause |
| **Brand partner** | `M09` claim receivables | Reconciliation-led rather than demand-led; relationship escalation before formal notice |
| **Marketplace seller** | Negative balance on `DT-039` | Set-off against future payouts is the primary remedy (`BRU-BIL-03`); letters are secondary |
| **Government / public sector** | Where payment cycles are institutional | Extended intervals; escalation is procedural, not punitive |
| **SMS / WhatsApp counterpart** | Steps 0–3 | Short form from `NT-006`; **never carries a consequence statement not in the letter** |
| **Final demand** | Step 6 | Legal letterhead, Legal signature, registered post, notice period per **G6 L3** |

---

## 7. Worked Example

| Specimen | Scenario | Proves |
|---|---|---|
| `DT-018-S1` | Consumer, step 2, BDT 8,400 overdue 18 days | Base bilingual rendition, enclosure |
| `DT-018-S2` | Corporate, step 4 pre-suspension | `BRU-CTR-05` sequence compliance |
| `DT-018-S3` | Account with a disputed line | `L-18-b` exclusion, `ST-03` partial pause |
| `DT-018-S4` | Step 6 final demand | Legal signature, notice period, dispute route retained |
| `DT-018-S5` | Ladder restarted after a data error | `ST-06` |

Held in `RF-009`, watermarked **SPECIMEN**.

---

## 8. Approval

| Role | Name | Date | Signature evidence |
|---|---|---|---|
| Author | Finance with Legal & Compliance | 2026-08-15 | Draft issue |
| Reviewer — Collections | *pending* | | |
| Reviewer — Account Management | *pending* | | |
| Reviewer — Contact Centre | *pending* | | |
| **Legal Counsel — the series approved as a set** | *pending* | | **Required; individual-step approval is not sufficient** |
| Approver — Legal Counsel with CFO | *pending* | | |

---

## 9. Numbering, Retention and Archive

| Item | Value |
|---|---|
| Sequence | `MD-040` — `DUN-{entity}-{yy}-{seq:06d}`, one number per issued letter |
| Gap policy | `gaps_recorded` |
| Archive format | PDF/A-3 at issue for steps 3–7; standard PDF for steps 0–2 |
| Retention | `LG-009`; **for the limitation period** confirmed at **G6 L4** — the trail is the evidence in recovery |
| Delivery evidence | Email delivery receipt, registered-post reference or call log, archived with the letter (`FM-18-d`) |
| Re-render | Prohibited — the amount demanded was correct at issue and must remain visible as issued |
| Reprint | Watermarked **COPY**, logged |
| Ladder record | The complete sequence for an account is retrievable as one file, in order, with dates and delivery evidence. **This is what a court, or the customer's lawyer, will ask for** |

---

## 10. Related Documents

| Document | Relationship |
|---|---|
| [`../DT-001_Document_Template_Standard_and_Branding_Rules.md`](../DT-001_Document_Template_Standard_and_Branding_Rules.md) | The category standard |
| [`DT-017_Customer_Statement_of_Account.md`](DT-017_Customer_Statement_of_Account.md) | Enclosed with every step |
| [`DT-010_Tax_Invoice_Mushak_6_3.md`](DT-010_Tax_Invoice_Mushak_6_3.md) | The invoices demanded |
| [`../05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md`](../05D_Commercial_and_Contract/DT-030_Contract_and_AMC_Agreement_Template_Set.md) | Contractual notice clauses that override the default ladder |
| [`../05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md`](../05D_Commercial_and_Contract/DT-031_SLA_Schedule_and_Service_Credit_Annex.md) | Where a service credit offsets a demanded amount |
| [`../05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md`](../05D_Commercial_and_Contract/DT-039_Marketplace_Seller_Payout_Statement.md) | Seller set-off route |
| [`NT-006_SMS_Template_Library_Finance_and_Collections.md`](../../04_Notification_and_Messaging/04A_SMS_and_OTP/NT-006_SMS_Template_Library_Finance_and_Collections.md) | The SMS counterparts |
| [`NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md`](../../04_Notification_and_Messaging/NT-003_Quiet_Hours_Throttling_and_Frequency_Policy.md) | Contact timing constraints |
| `LG-013` Service Terms, Warranty Terms and Exclusions | Payment terms and consequences |
| [`SP-019_SOP_Cash_Collection_and_Banking.md`](../../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-019_SOP_Cash_Collection_and_Banking.md) | How the ladder is operated — **note: no collections SOP exists in the `SP` register; see `AUDIT-007` finding DT-02** |
| `RP-004` Dashboard Specification Pack — Operational Consoles | Ladder effectiveness and stop-condition reporting |

---

## 11. Revision History

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Eight-step ladder with signatory per step, five ladder rules, seven-question Legal G6 list, seven stop conditions including error-restart and hardship, approved-consequence-text control | Legal Counsel with CFO (pending) |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to the `DT-001` §12 section spine
- [x] Ladder defined with trigger, channel, tone and signatory per step
- [x] Consequence text controlled to an approved set (`FM-18-a`)
- [x] Stop conditions defined, including restart-after-our-error and hardship
- [x] `BRU-CTR-05` notice-sequence dependency stated
- [x] All internal links resolve
- [ ] **Legal Counsel approval of the series as a set** — **outstanding; blocks `Approved`**
- [ ] G6 L1–L7 answered, particularly L3 final-demand content and L5 late-payment charges — **outstanding**
- [ ] Bengali counterpart authored and signed off in context (`BN-018`) — **outstanding**
- [ ] Approved consequence-text set authored per step and legally reviewed — **outstanding**
- [ ] Named approver recorded — **pending**
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
