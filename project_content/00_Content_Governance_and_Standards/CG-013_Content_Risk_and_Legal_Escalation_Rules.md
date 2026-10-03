---
id: CG-013
title: Content Risk and Legal Escalation Rules
project: 1000FiX ERP System v2.0
content_type: Standard
version: 1.0
date: 2026-08-15
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance
author: Legal & Compliance with Programme Content Lead
reviewers: [Programme Content Lead, CFO delegate, DPO, Quality Manager, CTO delegate]
approver: ERP Steering Committee
purpose: >
  Lists the triggers that force a content file out of its normal review path into legal, tax or
  regulator escalation. Prevents an author from shipping a warranty exclusion, a tax narrative,
  a data-protection statement or a capability promise on their own authority — not because
  authors are untrustworthy, but because they cannot be expected to recognise which sentence
  carries the liability.
traces_to: [00-04 §4 risks, 00-04 §5.2 decision rights, CG-002 §7, CG-007, RF-011, LG-001]
priority: P2
wave: W0
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-04 §4 risk register (RSK-022, RSK-033, RSK-036) and §5.2 decision rights
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6 regulatory obligations NFR-086, NFR-092, NFR-093, NFR-094, NFR-100
    verified: 2026-08-15
  - source: 1000fix_ERP_Module/00_Governance_and_Charter/00-07 findings H2-12, H2-13
    verified: 2026-08-15
supersedes: none
review_due: 2027-02-15
---

# CG-013 — Content Risk and Legal Escalation Rules

> **The problem is recognition, not diligence.** A content author writing a help article about
> device collection will, at some point, write a sentence about what happens if the customer
> does not collect. That sentence is a liability position. The author will not know that.
>
> **This file makes recognition mechanical.** It lists the words, topics and situations that
> trigger escalation regardless of who is writing, what file they are writing, or how confident
> they feel.

---

## 1. How escalation works

```
   Author writing content
            │
            ▼
   ┌────────────────────────┐   no    ┌─────────────────────────┐
   │  Does a §2 trigger     │────────►│  Normal review path      │
   │  fire?                 │         │  per CG-007 §2.1         │
   └───────────┬────────────┘         └─────────────────────────┘
               │ yes
               ▼
   ┌────────────────────────────────────────────────────────┐
   │  STOP. Do not complete the sentence on your own        │
   │  authority. Raise per §4.                              │
   └───────────┬────────────────────────────────────────────┘
               │
               ▼
   ┌────────────────────────┐
   │  Content Lead triages  │──► Reclassify the file (CG-002 §4)
   │  within 2 working days │──► Add the required gate (CG-007)
   └───────────┬────────────┘──► Escalate to the §3 authority
               │
               ▼
   ┌────────────────────────────────────────────────────────┐
   │  Decision recorded in RF-006; risk recorded in RF-011   │
   └────────────────────────────────────────────────────────┘
```

**Escalation is not failure.** An author who escalates correctly has done their job. An author
who resolves a §2 trigger alone has created an unreviewed liability, whether or not they got the
answer right.

---

## 2. Triggers

### 2.1 Absolute triggers — stop and escalate, always

If content does any of these, it escalates. There is no threshold and no judgement call.

| # | Trigger | Escalates to |
|---|---|---|
| **T-A01** | States, limits, disclaims or excludes **liability** | Legal |
| **T-A02** | Describes what the company will do if it **loses, damages or cannot return** a customer's device or data | Legal |
| **T-A03** | States a **warranty** term, period, exclusion or claim condition | Legal |
| **T-A04** | States a **refund, cancellation or compensation** entitlement or its limits | Legal |
| **T-A05** | States a **tax** treatment, rate, threshold, form or filing obligation | Tax + Legal |
| **T-A06** | Describes **personal data** collection, use, sharing, retention, location or deletion | DPO + Legal |
| **T-A07** | States or implies a **consent** basis, or wording that will be used to capture consent | DPO + Legal |
| **T-A08** | Describes **cross-border transfer** or data residency | DPO + Legal |
| **T-A09** | Creates, varies or interprets a **contractual obligation** — ours or a counterparty's | Legal |
| **T-A10** | States an **SLA commitment, measurement method or service credit** | Legal + Service Ops |
| **T-A11** | States **pricing**, a charge, a fee, a commission rate or a payout term | Finance + Commercial |
| **T-A12** | Makes a **capability promise** to an external party beyond what the specification commits | Product owner + Legal |
| **T-A13** | Makes a **comparative or superlative claim** — "only", "largest", "first", "best", "fastest" | Legal + Brand |
| **T-A14** | Describes an **employment** term, disciplinary consequence, or termination | HR + Legal |
| **T-A15** | Describes **health, safety** or hazardous-material handling | HSE + Legal |
| **T-A16** | States an **environmental or recycling** claim | Sustainability + Legal |
| **T-A17** | Describes conduct toward a **regulator** — filings, notifications, inspections, disclosures | Legal + the accountable function |
| **T-A18** | Describes **suspension, removal, penalty or sanction** of a seller, vendor or partner | Legal + Commercial |
| **T-A19** | Uses another organisation's **name, logo, brand or trade mark** | Brand + Legal |
| **T-A20** | Describes what an **AI system** will do, decide, or be relied on for | Legal + Data (`HC-019`) |

### 2.2 Threshold triggers — escalate above a limit

| # | Trigger | Threshold | Escalates to |
|---|---|---|---|
| **T-B01** | Content that changes an approval limit or delegation | Any change | Finance + `SP-004` owner |
| **T-B02** | Content describing a financial control | Any | Finance |
| **T-B03** | Content that would change a business rule in `05-05` | Any | The rule owner + Enterprise Architecture |
| **T-B04** | Content that contradicts an approved specification | Any | Enterprise Architecture |
| **T-B05** | Content asserting a figure that underpins a system control | Any unverified figure | Content Lead → the control's owner |
| **T-B06** | Content that would require a system change to be true | Any | Product owner + PMO |

### 2.3 Situation triggers — escalate on circumstance

| # | Situation | Escalates to |
|---|---|---|
| **T-C01** | A counterparty, regulator, brand partner or customer **challenges** existing content | Legal, within 2 working days |
| **T-C02** | An **incident** traces to content — wrong instruction, wrong figure, missing warning | Content Lead + the incident owner |
| **T-C03** | A **statutory instrument changes** and its effect on content is unclear | Tax or Legal, immediately |
| **T-C04** | An author cannot source a claim that matters (`CG-012` §6) | Content Lead; the accountable owner |
| **T-C05** | Two approved files **contradict each other** on a legal or statutory point | Legal, immediately |
| **T-C06** | A translation cannot convey an English legal obligation faithfully (`BP-07`) | Legal + Localisation |
| **T-C07** | Content is requested that would breach a policy the programme has already approved | Content Lead → Steering |
| **T-C08** | An external adviser's opinion **conflicts** with an approved content position | Legal → CFO |
| **T-C09** | A content decision is needed faster than the gate service levels allow | Content Lead, per §6 |

### 2.4 Word triggers

Some words carry legal weight regardless of intent. Their presence in a draft prompts a check —
not automatic escalation, but a question the author must answer.

| Word or phrase | Question it raises |
|---|---|
| guarantee, guaranteed, warrant, warranty | Is this a legal warranty? → `T-A03` |
| insure, insured, insurance | **Never use.** Regulated term. Use "protection plan" (`CG-004`) |
| liable, liability, responsible for | → `T-A01` |
| always, never, all, every, 100%, zero | Can we honour an absolute? → `T-A12` |
| only, first, largest, best, fastest, leading | → `T-A13` |
| free, no charge, at no cost | Is it free unconditionally? → `T-A11` |
| unlimited | → `T-A12` |
| immediately, instantly, real-time | Does the system do this? → `T-A12` |
| certified, accredited, authorised, approved | By whom, and can we evidence it? → `T-A13` |
| secure, safe, protected, encrypted | Is this a security claim we can substantiate? → `T-A06` |
| permanent, permanently deleted, destroyed | Data-deletion claim → `T-A06` |
| we will, we must, you must, you agree | Obligation language → `T-A09` |
| terms and conditions apply | Which terms, and are they accessible? → `T-A09` |
| penalty, fine, forfeit, sanction | → `T-A18` |
| tax, VAT, Mushak, BIN, TIN, VDS | → `T-A05` |

> **This list is a prompt, not a filter.** Absence of these words does not mean absence of a
> trigger. The §2.1 triggers are about **substance**, not vocabulary.

---

## 3. Escalation authorities

| Escalation | Authority | Service level | Fallback |
|---|---|---|---|
| Legal | Legal Counsel | 10 working days (`CG-007` G5) | CFO |
| Tax | Tax Manager, with external adviser | 15 working days (`CG-007` G6) | CFO |
| Data protection | DPO, with Legal | 10 working days | CTO / Legal |
| Financial control | Finance Manager, then CFO | 5 working days | CFO |
| Pricing | Commercial, then CCO | 5 working days | CCO |
| Specification conflict | Architecture Review Board | Next fortnightly meeting | CTO |
| Business rule change | The rule owner in `05-05`, then Business Owners Forum | Next fortnightly meeting | PMO |
| HSE | HSE lead, with Legal | 5 working days | Ops Director |
| Brand and trade mark | Brand lead, with Legal | 5 working days | CCO |
| AI behaviour and disclosure | Legal, with Data | 10 working days | CTO |
| Anything unresolved above | Programme Content Lead → PMO → **Steering Committee** | Per `00-04` §5.2 | Board |

**Decision rights are unchanged.** This file routes content questions into the decision rights
already set in `00-04` §5.2; it does not create new authorities.

---

## 4. What the author does

| Step | Action |
|---|---|
| 1 | **Stop writing the triggering content.** Leave the rest of the file progressing |
| 2 | Mark the passage in the draft: `<!-- ESCALATED: T-A03 warranty exclusion — awaiting Legal -->` |
| 3 | Raise it to the Content Lead with: the file, the passage, the trigger ID, and what you were trying to say |
| 4 | Continue with the rest of the file. **The file may reach `Review` with an escalation open; it may not reach `Approved`** |
| 5 | Record the escalation in `RF-011` |

### 4.1 What the author does **not** do

| Do not | Why |
|---|---|
| Guess and mark it "to be confirmed" | An unmarked guess reads as fact to the next reader |
| Copy wording from the corporate website | Different content set, different approval authority, possibly different legal position (`AF-11`, Master Index §11) |
| Copy wording from a competitor | Their legal position is not ours, and it may be their intellectual property |
| Soften it until it seems safe | Vague liability wording is unenforceable **and** unclear — the worst of both |
| Remove the topic entirely | The customer still needs the answer. Escalate; do not delete the question |
| Ask an adviser directly | Advice must be commissioned through the accountable function so it is recorded and retained (`CG-012` §8) |

---

## 5. Triage

The Content Lead triages every escalation within **2 working days** to one of four outcomes.

| Outcome | Meaning | Action |
|---|---|---|
| **Reclassify** | The file's content class was wrong | Move it to Class A or B; the `CG-007` gates follow automatically |
| **Add a gate** | The class is right; this passage needs a specific review | Add G5 or G6 to this file only |
| **Refer** | The question is not a content question | Route to the accountable function; the content waits on their answer |
| **Release** | The trigger fired but no legal or statutory question exists | Record why, in `RF-006`. **The reasoning is recorded even when the answer is "no issue"** |

> **Recording "no issue" matters.** A trigger that fires and is released without a record will
> fire again on the next file, be released again, and eventually be released when it should not
> have been. The record is what makes the second and third judgements consistent with the first.

---

## 6. Urgency

Some content genuinely cannot wait for a 10 or 15 working-day gate — an incident notice, a
regulatory response, a correction to published content that is actively wrong.

| # | Rule |
|---|---|
| **UR-01** | Urgency never removes a gate. It compresses it |
| **UR-02** | Class A and B content under urgency requires the **same** approver, reached directly, with the compression recorded |
| **UR-03** | A correction to content that is **actively causing harm** may be published immediately by the Content Lead, provided it only **removes or narrows** a claim. It may never add one |
| **UR-04** | Any urgent publication is reviewed within 5 working days and either confirmed or replaced |
| **UR-05** | Urgent publications are reported to the Steering Committee at its next meeting |
| **UR-06** | Repeated urgency in one area is a planning defect, and is raised as such |

---

## 7. Content risks already known

Recorded here at issue so the first entries in `RF-011` are not blank. Each traces to an existing
programme risk or audit finding.

| # | Risk | Consequence | Likelihood | Owner | Traces to |
|---|---|---|---|---|---|
| **CR-01** | Legal review capacity is the binding constraint on 75 Class A and B files | Wave gates slip, or content ships unreviewed | High | Legal Counsel | `CG-007` §10 |
| **CR-02** | Content effort of 520–775 PW is unfunded | Content quality is sacrificed at wave boundaries | **High** | Programme Director | `AF-09` |
| **CR-03** | No Programme Content Lead is appointed | Every escalation in this file has no destination | **High** | Programme Director | `AF-09`, R-07 |
| **CR-04** | Translation capacity cannot meet 266 bilingual files across nine waves | Bengali-first commitments (`PS-03`, `P02` #3) are missed | High | Localisation Lead | `CG-010` §9 |
| **CR-05** | The "17+ brands" figure underpins an `M22` control and is unverified | A certification control operates on an unverified population | Medium | Commercial | `00-07` H2-12 |
| **CR-06** | Statutory content may rest on non-primary sources | Non-compliant invoices or filings | Medium | Tax Manager | `00-07` H2-13, `CG-012` |
| **CR-07** | Marketplace VAT and liability model is undecided | `P07` content cannot state commission, payout or liability terms correctly | Medium | CFO | `00-04` RSK-022 |
| **CR-08** | Data residency legal opinion is outstanding | `LG-008`, `LG-012` and every consent string may be wrong | Medium | CTO / Legal | `00-04` RSK-033, `05-06` NFR-086 |
| **CR-09** | Master data is not ready when a wave needs it | Configuration, testing and training all stall | High | Master Data Owner | Master Index §6 |
| **CR-10** | The Bengali register decision is open | No `BN` bundle can start; every day of delay compounds | Medium | Localisation Lead | `CG-010` §12 |
| **CR-11** | `00-05` decision log does not exist; content decisions may repeat the gap | Decisions become unretrievable, as `D-14` already is | Medium | Programme Office | `AF-04` |
| **CR-12** | Content authored by vendors may not follow this operating model | Inconsistent, unreviewable content at scale | Medium | Programme Content Lead | `CO-09` |
| **CR-13** | **The primary brand colour `#39B1DF` fails WCAG AA text contrast at 2.46:1 on white, and fails the 3:1 non-text threshold** | `PS-04` and `NFR-073` make WCAG 2.1 AA contractual on all web portals. Applying the marketing palette to text unchanged fails the mandated pre-release scan on every portal | **High** | Brand Lead with CTO | `VB-003` §3, `04-00` PS-04, `05-06` NFR-073 |

**All thirteen transfer to `RF-011` at its creation**, with scoring against the `00-04` scale and
review at the Steering Committee cadence.

> **CR-13 was raised on 2026-08-15** by direct computation of the `CB-001` palette against the
> WCAG 2.1 relative-luminance formula, during authoring of `VB-003`. It requires a Brand ruling
> on one of three options set out in `VB-003` §3.2 and **blocks design-system token approval**.

---

## 8. Verification

| Check | Method | When |
|---|---|---|
| Escalation markers resolved before approval | Automated — scan for `ESCALATED:` comments in files at `Approved` | Every commit |
| Word-trigger scan | Automated — §2.4 list produces a review prompt, not a build failure | Every commit |
| Class A and B files carry the required gates | Automated against `CG-007` §2.1 | Every commit |
| Escalations triaged within 2 working days | Weekly report to PMO | Weekly |
| Released triggers carry a recorded reason | Wave audit | Every wave |
| Urgent publications reviewed within 5 working days | Weekly report | Weekly |
| Content risks reviewed and current | Wave audit; Steering monthly | Every wave |

---

## 9. Related documents

| Document | Relationship |
|---|---|
| [`CG-002_Content_Operating_Model_and_RACI.md`](CG-002_Content_Operating_Model_and_RACI.md) | Content classes, escalation path, decision rights |
| [`CG-007_Review_Approval_and_Signoff_Workflow.md`](CG-007_Review_Approval_and_Signoff_Workflow.md) | The gates escalation adds |
| [`CG-012_Content_Sourcing_and_Evidence_Rules.md`](CG-012_Content_Sourcing_and_Evidence_Rules.md) | `T-C04` unsourceable claims |
| [`CG-003_ERP_Product_Content_Style_Guide.md`](CG-003_ERP_Product_Content_Style_Guide.md) | §8.1 banned words overlaps §2.4 word triggers |
| `RF-011` Content Risk Register | Where §7 lives and is maintained |
| `RF-006` Content Decision Log | Where triage outcomes are recorded |
| `LG-001` Legal Content Register | Where legal approvals are evidenced |
| `LG-013` Service Terms, Warranty Terms and Exclusions | The canonical source for `T-A03` |
| `LG-008` Privacy Notice and Consent Copy | The canonical source for `T-A06`, `T-A07` |
| `HC-019` AI Guardrail, Disclosure and Handover Copy | `T-A20` |
| `00-04` §4, §5.2 | The programme risk register and decision rights |

---

## 10. Revision history

| Version | Date | Change | Approver |
|---|---|---|---|
| 1.0 | 2026-08-15 | Initial issue. Twenty absolute triggers, six threshold triggers, nine situation triggers, a word-trigger prompt list, escalation authorities routed to existing decision rights, author instructions including what not to do, four triage outcomes, urgency rules, and twelve known content risks | Steering Committee (pending) |

---

## Definition of Done

- [x] Front matter complete
- [x] Triggers are stated as recognisable conditions, not as judgement calls
- [x] Word triggers included as a prompt, with the limitation stated
- [x] Escalation routes to existing `00-04` §5.2 decision rights rather than inventing authorities
- [x] Author instructions include an explicit "do not" list covering the realistic shortcuts
- [x] Triage requires a recorded reason even for "no issue"
- [x] Urgency compresses gates rather than removing them
- [x] Twelve known content risks recorded with owners and traceability
- [x] All internal links resolve
- [x] Bengali counterpart — n/a
- [ ] Named approver recorded — **pending Steering Committee**
- [x] Registered in the Content Master Index

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
