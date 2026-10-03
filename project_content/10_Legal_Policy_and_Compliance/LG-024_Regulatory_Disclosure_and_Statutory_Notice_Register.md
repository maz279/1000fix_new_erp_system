---
id: LG-024
title: Regulatory Disclosure and Statutory Notice Register
project: 1000FiX ERP System v2.0
content_type: Legal / policy
template: TPL_Legal_Document.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Legal & Compliance with the CFO
author: Legal & Compliance with the CFO, Quality, HR, the Chief Data Officer and the CTO
reviewers: [Legal Counsel, CFO, Quality Manager, HR Director, Chief Data Officer, CTO, external tax adviser, external legal adviser]
approver: CFO with Legal Counsel
content_class: A
purpose: >
  The register of every regulator-facing obligation the company carries, and the notices, filings,
  disclosures, registrations and licences each requires — with an owner, a recurrence, a deadline, an
  evidence requirement and the consequence of breach. Obligations to the NBR and to the sectoral,
  environmental, labour and data-protection regulators are otherwise tracked in individuals' memory,
  and an obligation nobody has written down is an obligation that will be missed by whoever leaves.
traces_to: [M60, M51, M23, M29, M18, M21, M56, LG-001, LG-008, LG-009, LG-012, LG-018, LG-021, LG-022, LG-023, DT-010, DT-011, DT-012, DT-013, DT-014, DT-041, MD-002, MD-037, MD-041, SP-020, SP-021, CG-012, CG-013, BRU-GRC-12, BRU-GRC-13, BRU-GRC-22, BRU-ESG-16, BRU-ESG-17, BRU-TAX-09, BRU-TAX-10, BRU-TAX-13, BRU-TAX-14, BRU-TAX-15, BRU-TAX-24, BRU-QMS-13, FR-GRC-023, FR-GRC-024, FR-GRC-025, FR-GRC-026, FR-GRC-027, FR-GRC-032, NFR-088, NFR-094, NFR-100]
priority: P2
wave: W3
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §5.3 FR-GRC-023 obligation register with source, requirement text, owner, recurrence and consequence of breach; FR-GRC-024 discharge with evidence, and obligations discharged without evidence reported as a control failure; FR-GRC-025 obligation calendar with advance notice, escalation before due date and breach recording after; FR-GRC-026 regulatory change monitoring; FR-GRC-027 licence and registration register covering trade licence, VAT/BIN, TIN, environmental, import and sector registrations with validity, renewal lead time and evidence; FR-GRC-032 retention schedule defined from obligations and published to M24
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M60 §9 BRU-GRC-12 an obligation discharged without evidence is a control failure; BRU-GRC-13 a breached obligation is recorded, assessed and escalated and never quietly closed; BRU-GRC-22 a licence, registration or insurance policy approaching expiry escalates on the declared lead time and a lapse generates a mandatory incident record
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/G_Finance_and_Treasury/M51 §9 BRU-TAX-09 a deduction is deposited by its statutory deadline with escalation to the CFO; BRU-TAX-10 a withholding certificate is issued within the statutory window; BRU-TAX-13 a return cannot be filed without CFO approval; BRU-TAX-14 the VAT return is filed and the net VAT paid by the 15th of the following month; BRU-TAX-15 a filed return is never altered and a correction is a separately evidenced amendment; BRU-TAX-24 tax records retained seven years and queryable
    verified: 2026-08-18
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06 §6.1 statutory currency table verified 2026-08-12; §6.2 NFR-088 records retention per the statutory schedule enforced by the system, NFR-100 Mushak 9.1 filed by the 15th of the following month through the NBR VAT Online portal, NFR-101 input VAT credit only against a valid Mushak 6.3; §6.3 NFR-094 breach notification to the National Data Management Authority
    verified: 2026-08-12
    class: P1
  - source: 1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M18 §9 BRU-ESG-16 the regulatory register is reviewed at least quarterly and after any published amendment; BRU-ESG-17 statutory returns are filed within the deadline in the instrument and a late filing is a reportable compliance event
    verified: 2026-08-18
    class: P1
  - source: The instruments listed in §4.3 — VAT and Supplementary Duty Act 2012 and its rules, Income Tax Act 2023 and the applicable Finance Act, Bangladesh Labour Act 2006 and Labour Rules 2015, Environment Conservation Act 1995 and the Hazardous Waste (E-waste) Management Rules 2021, Personal Data Protection Act 2026, Cyber Security Ordinance 2025, ICT Act 2006, Companies Act 1994, Consumer Rights Protection Act 2009, and the Digital Commerce Operation Guidelines 2021. **Instrument-level citations. Every deadline, form reference, threshold and filing route marked ‡ is unverified at section level and is pending G6 by an external tax adviser and an external legal adviser**
    verified: 2026-08-18
    class: P2
supersedes: none
review_due: 2027-02-18
---

# LG-024 — Regulatory Disclosure and Statutory Notice Register

| Item | Value |
|---|---|
| Document class | **Register** — obligations, filings, notices, registrations and licences |
| Counterparty | **The regulators** — and the register is internal |
| Governing law | **Bangladesh** |
| Effective date | On publication of version 1.0 — *pending G6* |
| Acceptance capture method | **`AC-6` publication.** The register is operated, not agreed |
| Version accepted by users | n/a. **Every version retained**, because a discharge is evidenced against the register in force |
| External counsel review | **Required — G6**, by an external **tax** adviser and an external **legal** adviser. Neither alone covers §4.3 |
| Bengali version | **Not required** (`CG-010` §3.2 — internal register; filings are made in the form the regulator prescribes) |

> ⚠ **Class A — statutory, and the register that several other files have been waiting for.**
>
> `LG-018` `O-03` needs the environmental obligations here. `LG-021` §4.13.7 needs the security ones.
> `LG-022` `O-02` needs the ISO certificate and its expiry recorded. `LG-009` needs the obligations
> that generate its retention periods (`FR-GRC-032`).
>
> **`M60` provides the machinery** — `FR-GRC-023` register, `FR-GRC-024` evidenced discharge,
> `FR-GRC-025` calendar with escalation, `FR-GRC-026` change monitoring, `FR-GRC-027` licence
> register. **This file is the content that populates it.**
>
> **And it is the file most exposed to the honest-gap problem.** A register listing 40 obligations
> with unverified deadlines is more dangerous than one listing 20 verified ones, because it looks
> complete. **§4.3 therefore marks every unverified element and §4.7 states what is not known.**
>
> **Conformance note.** All ten template sections retained in order. The obligation register is §4.3,
> the licence register §4.4, notice types §4.5, within §4 Terms. Gate questions and open items are
> §1.2 and §1.3 (`CP-09`).

---

## 1. Approval Record

| Role | Name | Date | Evidence |
|---|---|---|---|
| Drafted by | Legal & Compliance with the CFO | 2026-08-18 | Draft issue v1.0 |
| G1 Editorial — Content Design | *pending* | | |
| G2 Factual — CFO, Quality Manager, HR Director, CDO, CTO | *pending* | | |
| **G5 Legal — Legal Counsel** | *pending* | | **Required** |
| **G6 Statutory — external tax adviser** | *pending* | | **Required for every tax row** |
| **G6 Statutory — external legal adviser** | *pending* | | **Required for every non-tax row** |
| Approved by — CFO with Legal Counsel | *pending* | | |

### 1.2 Questions for the external advisers (G6)

| # | Question | Adviser |
|---|---|---|
| **RG1** ‡ | **Confirm the company's registration set** — trade licence, VAT registration and BIN, TIN, import registration, environmental clearance, and any sector-specific registration | Legal + Tax |
| **RG2** ‡ | **Confirm every tax filing, its form, its deadline, its route and its approver** — VAT return, withholding returns and statements, income tax return, and any periodic statement | Tax |
| **RG3** ‡ | **Confirm the withholding deposit deadline and the certificate window** (`BRU-TAX-09`, `BRU-TAX-10`) | Tax |
| **RG4** ‡ | **Confirm the labour filings and registers** the Labour Act 2006 and Labour Rules 2015 require, including any statutory fund contribution and its return | Legal + HR |
| **RG5** ‡ | **Confirm the environmental registrations, returns and their deadlines** — this is `LG-018` `EW1`, `EW4` and `EW5`, and it cannot be answered here without them | Environmental |
| **RG6** ‡ | **Confirm the data-protection obligations** that are register-tracked rather than continuous — breach notification (`NFR-094`), cross-border transfer notification (`NFR-086b`), any registration with the National Data Management Authority, and any Chief Data Officer notification (`NFR-096`) | Data protection |
| **RG7** ‡ | **Confirm whether the company must register or report under the Cyber Security Ordinance 2025**, and whether it is critical information infrastructure — **`LG-021` `CS1` and `LG-012` `RD3` are the same question** | Legal |
| **RG8** ‡ | **Confirm the Companies Act 1994 filings** — annual return, financial statements, changes in directors or capital | Legal |
| **RG9** ‡ | **Confirm the consumer-protection and digital-commerce obligations** that are register-tracked, including any registration or complaint-response duty | Legal |
| **RG10** | **Where a regulator's requirement changes, who monitors it and how is the change detected?** `FR-GRC-026` provides the capability; **`BRU-ESG-16` requires quarterly review of the register** | Legal + Tax |

### 1.3 Open items

| # | Open item | Blocking? | Owner |
|---|---|:--:|---|
| **O-01** | **`RG1`–`RG10` unanswered. Every `‡` element is provisional and `CG-012` `PR-04` blocks approval of a Class A file containing one** | **Yes — blocks `Approved` absolutely** | CFO with Legal Counsel |
| **O-02** | **The register is incomplete by construction and says so (§4.7).** `CG-012` `EX-01`: a claim that an artefact exists is verified by checking. **The company's actual registration certificates have not been produced to the content function** | **Yes** | CFO |
| **O-03** | **`LG-022` `O-02`: the ISO 9001 certificate is not recorded anywhere.** §4.4 is where it belongs, and it is **empty** | **Yes — a claim the company makes publicly rests on it** | Quality Manager |
| **O-04** | **`LG-018` `EW1` is unresolved, so the environmental rows cannot be completed.** `LG-018` is `W5` and this file is `W3`: **this file needs an answer from a file written two waves later** | **Yes — mutual dependency** | Quality Manager with Legal |
| **O-05** | **`M60` is undelivered**, so the register, the calendar, the escalation and the change monitoring are all manual at `W3`. **A manual obligation calendar across tax, labour, environment, data protection and company law will miss something** | **Yes** | CTO with CFO |
| **O-06** | **`RT8` from `LG-009` is unanswered — the limitation period.** More than twenty retention rows depend on it, and this register is where the obligation that sets it should be recorded | **Yes** | Legal Counsel |
| **O-07** | **No insurance register exists.** `FR-GRC-040` provides one and `BRU-GRC-22` treats an insurance lapse the same as a licence lapse. **§4.4 covers licences and not insurance**, and `LG-016` `RA7` raises insurance from the managed-services side | Yes | CFO |
| **O-08** | **The Chief Data Officer is not appointed** (`LG-008` `O-05`), and `NFR-096` may make the appointment itself a registrable obligation (`RG6`) | **Yes** | CEO |
| **O-09** | **`LG-021` `CS1`, `LG-012` `RD3` and `RG7` are one question asked in three files.** It needs one answer, recorded once, here | **Yes** | CTO with Legal Counsel |

---

## 2. Scope and Parties

**In scope:** every obligation the company owes to a regulator or public authority; the registrations
and licences it must hold; the filings, returns, notices and disclosures each requires; the owner,
recurrence, deadline, evidence and consequence for each; the change-monitoring duty; and what is not
yet known.

**Out of scope:**

| Subject | Owned by |
|---|---|
| **How long records are kept** | [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) — **this register supplies the obligations it derives from** (`FR-GRC-032`) |
| The statutory output documents themselves | `DT-010`…`DT-014`, `DT-041` |
| Tax determination and computation | `M51`; `MD-037` |
| The environmental position and its claims | [`LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md`](LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md) |
| Data-protection substance | `LG-008`, `LG-010`, `LG-012` |
| Security controls | [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) |
| Quality management system | [`LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md`](LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md) |
| Ethics and external reporting of an offence | [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) §4.8.5 |
| The filing procedures | `SP-020` month-end and year-end close; `SP-021` payroll and statutory filing |
| The enterprise risk register | `M60` `FR-GRC-001`; `RF-011` for content risks |

---

## 3. Definitions

| Term | Meaning |
|---|---|
| **Obligation** | A requirement imposed by an instrument, a licence, a certification or a contract, owed to a regulator or authority (`FR-GRC-023`) |
| **Occurrence** | A single instance of a recurring obligation — one month's VAT return |
| **Discharge** | Meeting an occurrence. **An obligation discharged without evidence is a control failure** (`FR-GRC-024`, `BRU-GRC-12`) |
| **Registration** | A registration, licence or permit the company must hold to operate (`FR-GRC-027`) |
| **Notice** | A communication the company must make to a regulator or an affected person |
| **Disclosure** | Information the company must publish or make available |
| **Lead time** | The advance period at which a renewal or deadline escalates (`BRU-GRC-22`, `FR-GRC-025`) |
| **Consequence of breach** | The stated result of missing an occurrence — penalty, interest, suspension, prosecution, or loss of a licence |
| **‡** | An element resting on a secondary source, unverified, **pending G6** |

---

## 4. Terms

### 4.1 The rules the register operates under

| # | Rule |
|---|---|
| **RG-R1** | **Every obligation has a named owner, a recurrence, a deadline, an evidence requirement and a stated consequence of breach** (`FR-GRC-023`). **A row missing any of the five is not a register entry** |
| **RG-R2** | **An obligation discharged without evidence is recorded as a control failure, not as discharged** (`FR-GRC-024`, `BRU-GRC-12`) |
| **RG-R3** | **The calendar escalates before the due date and records a breach after it** (`FR-GRC-025`) |
| **RG-R4** | **A breached obligation is recorded, assessed for consequence and escalated. It is never quietly closed** (`BRU-GRC-13`) |
| **RG-R5** | **A registration or licence approaching expiry escalates on its declared lead time; a lapse generates a mandatory incident record** (`BRU-GRC-22`) |
| **RG-R6** | **The register is reviewed at least quarterly and after any published amendment** (`BRU-ESG-16`, applied to the whole register rather than only its environmental rows) |
| **RG-R7** | **A regulatory change is recorded, its impact on obligations, controls and processes assessed, and the resulting actions driven** (`FR-GRC-026`) |
| **RG-R8** | **A return cannot be filed without the CFO's approval of the compiled version** (`BRU-TAX-13`), and **a filed return is never altered — a correction is a separately evidenced amendment** (`BRU-TAX-15`) |
| **RG-R9** | **A filing deadline is taken from the instrument, not from custom.** `BRU-ESG-17` says the same for environmental returns |
| **RG-R10** | **Every deadline in §4.3 that carries `‡` is unverified and is pending G6.** A `‡` deadline is **not** relied on operationally until verified |
| **RG-R11** | **This register is the source of the `LG-009` retention obligations** (`FR-GRC-032`) |
| **RG-R12** | **A regulator communication is recorded**, both directions, with the date, the officer and the content |

### 4.2 The regulators and authorities

| Authority | Domain | Company owner |
|---|---|---|
| **National Board of Revenue (NBR)** | VAT, income tax, withholding, customs | **CFO** |
| **National Data Management Authority** | Personal data protection | **Chief Data Officer** — **`O-08`: unappointed** |
| **Department of Environment** | E-waste, hazardous waste, environmental clearance | **Quality Manager** |
| **Labour authorities and inspectorate** | Employment, wages, hours, safety, statutory funds | **HR Director** |
| **Registrar of Joint Stock Companies and Firms** | Company filings | **CFO** |
| **Directorate of National Consumer Rights Protection** | Consumer complaints and practices | **Legal Counsel** |
| **National cyber security structure** | Cyber incidents, critical information infrastructure | **CTO** — **`RG7`, `O-09`** |
| **City corporation or municipality** | Trade licence, premises | CFO |
| **Certification body (ISO 9001)** | Not a regulator, but an external audit obligation | **Quality Manager** — **`O-03`** |

### 4.3 The obligation register — **`‡` throughout; see §4.7**

> **`CL-01`. Every deadline, form reference and threshold below carries `‡` unless it is drawn from an
> approved specification in the repository.** Three rows are **not** `‡` because `05-06` §6.2 and `M51`
> §9 state them and were verified on 2026-08-12: the **VAT return by the 15th through the NBR VAT
> Online portal** (`NFR-100`, `BRU-TAX-14`), **input VAT credit only against a valid Mushak 6.3**
> (`NFR-101`, `BRU-TAX-06`), and **tax records retained seven years** (`BRU-TAX-24`).

**Tax — owner: CFO**

| # | Obligation | Recurrence | Deadline | Evidence | Consequence of breach |
|---|---|---|---|---|---|
| **OB-01** | **File the VAT return (Mushak 9.1) and pay the net VAT** | **Monthly** | **By the 15th of the following month, through the NBR VAT Online portal** | Filed return acknowledgement; payment challan; `DT-014` pack | Penalty and interest; **`BRU-TAX-14` is a hard rule** |
| **OB-02** | Issue a **Mushak 6.3** tax invoice for every taxable supply at the time of supply, displaying the BIN | **Per transaction** | At the time of supply | `DT-010`; gapless sequence per entity and premises (`BRU-TAX-05`) | Invalid invoice; **customer cannot claim input credit**; penalty |
| **OB-03** | Maintain the **sales register (Mushak 6.2)** and **purchase register (Mushak 6.1)** | **Continuous, locked at period close** | Per period | `DT-011`, `DT-012`; register reconciled to the GL control account (`BRU-TAX-12`) | Return cannot be compiled |
| **OB-04** | **Deduct VDS / TDS** at the determined rate on every applicable payment | **Per payment** | Before payment proceeds (`BRU-TAX-07`) | Determination record; payment record | **Payment cannot proceed**; company liability for the un-deducted amount |
| **OB-05** | **Deposit each deduction by its statutory deadline** | **Per deduction cycle** | **‡ Statutory deadline; escalates to the CFO on approach** (`BRU-TAX-09`) | Deposit challan | Penalty and interest |
| **OB-06** | **Issue a withholding certificate to the payee** | **Per deduction** | **‡ Within the statutory window of the triggering event** (`BRU-TAX-10`) | `DT-013`; issued certificate | Payee cannot claim credit; penalty |
| **OB-07** | **File the income tax return** | **Annual** | **‡** | Filed return; CFO approval (`BRU-TAX-13`) | Penalty; assessment |
| **OB-08** | Apply an **exemption or reduced rate only where its SRO basis and evidence are recorded and valid at the tax point** | Per transaction | At the tax point | SRO reference; evidence | Under-declaration; penalty (`BRU-TAX-25`) |
| **OB-09** | **Retain tax documents, registers, returns, challans, certificates and determination records** | **Continuous** | **7 years, queryable** (`BRU-TAX-24`) | The records themselves; `LG-009` `RC-03`, `DC-01` | Inability to defend an assessment |
| **OB-10** | Maintain the **country-pack version** with fixtures passed, external consultant sign-off and CFO approval before activation | Per change | Before activation (`BRU-TAX-22`) | Fixture results; sign-off | Wrong determination applied |

**Data protection — owner: Chief Data Officer (`O-08`)**

| # | Obligation | Recurrence | Deadline | Evidence | Consequence of breach |
|---|---|---|---|---|---|
| **OB-11** | **Notify the Authority of a breach likely to cause significant damage** | **Per breach** | **‡ Within the prescribed timeframe** (`NFR-094`) — **`LG-008` `PN3`** | Breach register entry; notification record (`FR-GRC-036`) | **Penalty up to BDT 25 lakh, or 50 lakh for a significant data fiduciary** |
| **OB-12** | **Notify the Authority of a cross-border transfer of sensitive personal data and disclose the safeguards** | **Per transfer basis** | **‡ Before the transfer executes** (`NFR-086b`, `BRU-SEC-14`) | `LG-012` §4.5 transfer register; notification reference | **Transfer blocked; penalty** |
| **OB-13** | **Maintain the record of processing activities** | **Continuous** | Retained **at least 5 years** (`NFR-095`, `BRU-GRC-17`) | `FR-GRC-033` register | Control failure; penalty |
| **OB-14** | **Appoint a Chief Data Officer if classified a significant data fiduciary** | One-off, then maintained | **‡** (`NFR-096`) — **`RG6`, `O-08`** | Appointment record; authority and reporting line | Non-compliance; penalty |
| **OB-15** | **Fulfil and evidence a data-subject request within the statutory period** | **Per request** | **‡ `LG-010` `DR1`** | `LG-010` §4.7 register | Penalty; regulatory complaint |

**Environment — owner: Quality Manager (`LG-018` `EW1`–`EW5`, `O-04`)**

| # | Obligation | Recurrence | Deadline | Evidence | Consequence of breach |
|---|---|---|---|---|---|
| **OB-16** | **‡ Registration with the Department of Environment** where required | One-off, then renewed | **‡** | Registration certificate | **‡ Licensing exposure** |
| **OB-17** | **‡ Submit and maintain a waste-management plan** where required | **‡** | **‡** | Submitted plan | **‡** |
| **OB-18** | **‡ Meet the applicable collection target** | **‡ Annual** | **‡** | Posted transactions (`BRU-ESG-11`); baseline — **`LG-018` `O-07`: none exists** | **‡** |
| **OB-19** | **‡ File environmental statutory returns** | **‡** | **In the deadline in the instrument** (`BRU-ESG-17`) | Filed return | **A late filing is a reportable compliance event** |
| **OB-20** | **‡ Hold environmental clearance for premises storing or handling e-waste and batteries** | Per site, renewed | **‡** | Clearance certificate per site | **‡ Operating exposure** |
| **OB-21** | **Obtain a Basel prior-informed-consent reference before any transfer outside Bangladesh** | Per transfer | **Before execution** (`BRU-ESG-06`) | Recorded reference | **Transfer blocked; serious exposure** |

**Labour and payroll — owner: HR Director (`RG4`)**

| # | Obligation | Recurrence | Deadline | Evidence | Consequence of breach |
|---|---|---|---|---|---|
| **OB-22** | **‡ Maintain the statutory employment registers and records** | Continuous | **‡** | The registers; `LG-009` `RC-10`…`RC-12` | Inspection finding; penalty |
| **OB-23** | **‡ Statutory fund contributions and their returns** | **‡** | **‡** | Contribution and filing records | Penalty; employee claim |
| **OB-24** | **Deduct and remit employee tax** | Per payroll | Per `OB-04`, `OB-05` | Payroll records; `DT-041` | Penalty; employee tax position misstated |
| **OB-25** | **‡ Report a serious workplace accident** | Per incident | **‡** | Incident record; `SP-030` | Penalty; prosecution |
| **OB-26** | **‡ Comply with wage, hours, leave and safety requirements** | Continuous | Continuous | Attendance, payroll and HSE records | Inspection finding; penalty |

**Company, consumer and cyber — owners as stated**

| # | Obligation | Owner | Recurrence | Deadline | Evidence | Consequence |
|---|---|---|---|---|---|---|
| **OB-27** | **‡ Companies Act 1994 annual return and financial statements** | CFO | Annual | **‡** | Filed documents | Penalty; officer liability |
| **OB-28** | **‡ Notify changes in directors, capital or registered office** | CFO | Per change | **‡** | Filed notice | Penalty |
| **OB-29** | **Hold and renew the trade licence** | CFO | Annual | **‡** | Licence | **Operating exposure** (`BRU-GRC-22`) |
| **OB-30** | **‡ Respond to a DNCRP complaint** | Legal Counsel | Per complaint | **‡** | Response record | Penalty; adverse order |
| **OB-31** | **‡ Digital-commerce delivery and refund obligations** on applicable paths | Legal with CCO | Continuous | **`LG-014` `RF1`** | `LG-014` records | Penalty; consumer order |
| **OB-32** | **‡ Cyber Security Ordinance 2025 registration or incident reporting** | CTO | **‡** | **‡** | **`RG7`, `O-09`** | **‡** |
| **OB-33** | **‡ Import registration and trade-compliance filings** where the company imports parts | CFO with Supply Chain | Per consignment and annual | **‡** | Import documents | Clearance delay; penalty |

**Certification — owner: Quality Manager**

| # | Obligation | Recurrence | Deadline | Evidence | Consequence |
|---|---|---|---|---|---|
| **OB-34** | **Maintain ISO 9001:2015 certification** — surveillance audits, recertification, findings closed | Per the certificate's cycle | **`LG-022` `QP1`: the cycle and expiry are not recorded** | The certificate; audit reports; CAPA closure | **Loss of the company's stated differentiator; a mandatory incident record on lapse** (`BRU-GRC-22`) |
| **OB-35** | **Notify the certification body of a change requiring it** | Per change | Per the body's rules | Notification record | Finding; scope invalidity — **`LG-022` `QP4`** |
| **OB-36** | **Retain ISO records for three certification cycles and not dispose while a certificate is live** | Continuous | `BRU-QMS-13`; `LG-009` `DC-19` | The records | Audit finding — **cycle definition is `LG-022` `QP5`** |

### 4.4 The licence and registration register — **empty (`O-02`, `O-03`)**

`FR-GRC-027` provides the register. **This is its content specification, and every row is unpopulated
because the certificates have not been produced to the content function.**

| Field | Notes |
|---|---|
| `registration_type` | Trade licence, VAT/BIN, TIN, environmental clearance, import registration, sector registration, ISO certificate |
| `issuing_authority` | Named |
| `number` | The registration or certificate number |
| `scope` | Activities and sites covered — **`LG-022` `QP2` for the ISO certificate** |
| `valid_from` / `valid_to` | Dates |
| `renewal_lead_time` | The advance period at which escalation fires (`BRU-GRC-22`) |
| `owner` | Named person |
| `evidence_ref` | The `M24` document reference for the certificate itself |
| `dependency` | What stops if it lapses |

| # | Rule |
|---|---|
| **4.4.1** | **A registration with no recorded evidence reference is treated as not held**, until the certificate is filed |
| **4.4.2** | **`O-07`: insurance policies belong in a parallel register** (`FR-GRC-040`), and `BRU-GRC-22` treats an insurance lapse identically. **§4.4 does not currently cover insurance** |
| **4.4.3** | **The ISO 9001 certificate is the most-cited and least-documented artefact in the repository** (`LG-022` `O-02`, `O-03`) |

### 4.5 Notice and disclosure types

| Type | Trigger | To whom | Owner | Where the content lives |
|---|---|---|---|---|
| **Statutory filing** | A recurring deadline | The regulator | Per §4.3 | `DT-010`…`DT-014`, `DT-041` |
| **Breach notification** | A personal-data breach above the threshold | The Authority, and affected persons | CDO | `LG-008` §4.8; `LG-010` `T-11`; `OP-004` |
| **Transfer notification** | A cross-border transfer of sensitive data | The Authority | CDO | `LG-012` §4.5 |
| **Cyber incident report** | An incident, where the regime applies | The national structure | CTO | `LG-021` `IS-10` — **`RG7`** |
| **Workplace accident report** | A serious accident | Labour authority | HR Director | `SP-030` |
| **Environmental return or declaration** | Per instrument or per transfer | Department of Environment; the receiving partner | Quality Manager | `LG-018` §4.5 |
| **Consumer authority response** | A complaint | DNCRP | Legal Counsel | `LG-014` §8; `SP-028` |
| **Certification notification** | A qualifying change | Certification body | Quality Manager | `LG-022` §9.2 |
| **Public disclosure** | A published statement of position | The public | The stating function | `LG-008`, `LG-012`, `LG-018` §4.6 |
| **Regulator information request** | An inspection or enquiry | The regulator | Legal Counsel | §4.6 |

### 4.6 Handling a regulator

| # | Clause |
|---|---|
| **4.6.1** | **Every regulator contact is routed to Legal Counsel and the domain owner**, and is recorded both directions (`RG-R12`) |
| **4.6.2** | **No employee responds to a regulator's substantive enquiry on their own authority.** `CG-013` `T-A17` makes conduct toward a regulator an absolute escalation trigger |
| **4.6.3** | An information request is answered accurately and completely, within the period allowed, with the response recorded |
| **4.6.4** | **An evidence pack is assemblable in under five minutes with a manifest and completeness check** (`FR-DMS-041`), and **a legal hold is placed where a matter may arise** (`FR-GRC-039`) |
| **4.6.5** | **Nothing is destroyed once a request or an inspection is known about** (`BRU-DMS-02`, `LG-009` `OV-04`) |
| **4.6.6** | An inspection finding is recorded as a matter (`FR-GRC-038`), remediated, and reported |
| **4.6.7** | **A breached obligation is disclosed rather than concealed** — `RG-R4`, and `LG-023` `EB-13` makes concealment a disciplinary offence |

### 4.7 What is not known — stated (`O-02`)

> **`CL-02`. A register that looks complete and is not is more dangerous than one that admits its
> gaps**, because the calendar will be built from it and the gaps will be invisible. This section is
> republished with every version until it is empty.

| Gap | Effect |
|---|---|
| **36 obligations listed; only 3 elements verified against an approved specification** | Every `‡` deadline is provisional and must not drive an operational calendar (`RG-R10`) |
| **No registration certificates produced** | §4.4 is empty; the company cannot evidence what it holds |
| **The ISO 9001 certificate is not recorded** | `LG-022` §4.3 cannot be completed and a public claim rests on it |
| **Environmental obligations depend on `LG-018` `EW1`**, which is `W5` | This `W3` file cannot complete rows `OB-16`…`OB-21` |
| **The cyber-regime question is asked in three files** | `RG7` = `LG-021` `CS1` = `LG-012` `RD3`. One answer, three consequences (`O-09`) |
| **The limitation period is unstated** | `LG-009` `RT8`; more than twenty retention rows wait on it |
| **No insurance register** | `BRU-GRC-22` treats insurance like a licence; §4.4 does not cover it (`O-07`) |
| **`M60` undelivered** | Register, calendar, escalation and change monitoring are manual (`O-05`) |
| **No Chief Data Officer** | Five obligations have an unappointed owner (`O-08`) |

---

## 5. Liability, Exclusions and Limits

| # | Clause |
|---|---|
| **5.1** | This register creates no contractual limitation |
| **5.2** | **A missed filing carries penalty and interest, and in some cases prosecution.** The exposure is the company's and, for some obligations, its officers' |
| **5.3** | **A lapsed registration or licence is an operating exposure**, not an administrative one: it can stop the activity it authorises (`BRU-GRC-22`) |
| **5.4** | **An obligation discharged without evidence is treated as not discharged** (`BRU-GRC-12`). In a dispute with a regulator, the evidence is the discharge |
| **5.5** | **A register that omits an obligation does not reduce the obligation.** §4.7 exists so an omission is a known gap rather than an assumed completeness |
| **5.6** | Nothing limits liability that cannot lawfully be limited |

---

## 6. Data Protection

> Must reconcile with `LG-008`, `LG-009`, `LG-012`. Check **F6**.

| # | Clause |
|---|---|
| **6.1** | Filings and disclosures contain personal data — employee tax and payroll data, customer TIN on invoices, identity data in some filings. `LG-008` `P-16` covers it on legal obligation |
| **6.2** | **A statutory filing is a lawful disclosure, and `LG-008` `P-03` and `P-16` state it to the data subject.** `LG-008` §4.7.1's correction to the `UI-042` TIN wording exists because of this row |
| **6.3** | **TIN is residency-restricted and yet appears on statutory outputs and in filings** (`LG-012` §4.3). The disclosure is lawful and the storage restriction still applies |
| **6.4** | Records supporting a filing are retained per `LG-009` — **7 years for tax** (`OB-09`, `RC-03`) |
| **6.5** | **An erasure request cannot defeat a statutory retention obligation**, and the override and its basis are stated to the data subject (`BRU-CPM-11`, `LG-009` §4.5) |
| **6.6** | **Breach and transfer notifications are themselves processing records**, retained at least 5 years (`OB-13`) |
| **6.7** | Regulator correspondence may contain personal data and is retained per `LG-009` `RC-19` |

---

## 7. Termination and Consequences

| Event | Consequence |
|---|---|
| **An occurrence approaches its deadline** | Advance notice, then escalation before the due date (`FR-GRC-025`) |
| **An occurrence is missed** | **Recorded as a breach, assessed for consequence, escalated — never quietly closed** (`BRU-GRC-13`); an environmental late filing is a **reportable compliance event** (`BRU-ESG-17`) |
| **An occurrence is discharged with no evidence** | **A control failure** (`BRU-GRC-12`) |
| **A registration approaches expiry** | Escalates on the declared lead time (`BRU-GRC-22`) |
| **A registration lapses** | **A mandatory incident record**, and the dependent activity stops |
| **A regulation changes** | Recorded; impact assessed on obligations, controls and processes; actions driven (`FR-GRC-026`); **`LG-009`, `LG-008` and the affected `LG` files re-open at G2, G5 and G6** |
| **A regulator opens an inspection** | A legal hold is placed (`FR-GRC-039`); **nothing is destroyed** (§4.6.5) |
| **This register is superseded** | Prior versions retained permanently (`LG-009` `RC-19`, `DC-23`), because a discharge is evidenced against the register in force |

---

## 8. Dispute Resolution

| Step | Route |
|---|---|
| **1 — An internal question about an obligation** | The domain owner in §4.2, then Legal Counsel |
| **2 — A disagreement with a regulator's position** | **Legal Counsel with the external adviser who verified the row at G6.** Never the domain owner alone |
| **3 — A penalty or assessment** | CFO with Legal Counsel and the external adviser; recorded as a matter (`FR-GRC-038`) |
| **4 — Appeal** | As the instrument provides |
| **5 — Courts** | The courts of Dhaka, Bangladesh, or the tribunal the instrument specifies |

---

## 9. Change Control

| Version | Date | Change | Notice given to users | Re-acceptance required |
|---|---|---|---|:--:|
| 1.0 | 2026-08-18 | Initial issue — draft, blocked on G6 by two advisers. 36 obligations registered; §4.4 empty; §4.7 states nine gaps | n/a | n/a |

| # | Rule |
|---|---|
| **9.1** | Adding, changing or removing an obligation is **MAJOR** |
| **9.2** | **A verified `‡` element removes the marker and is recorded with its verification date and adviser** (`CG-012` §4) |
| **9.3** | **A regulatory change re-opens G2, G5 and G6 here and in every file citing the instrument** (`LG-001` §4.8) |
| **9.4** | **Reviewed at least quarterly and after any published amendment** (`RG-R6`, `BRU-ESG-16`) |
| **9.5** | Every version retained permanently |
| **9.6** | **§4.7 is republished with every version until it is empty**, and is never removed for presentation |

---

## 10. Cross-References

| Document | Relationship | Must not contradict |
|---|---|---|
| [`LG-009_Data_Retention_and_Deletion_Schedule.md`](LG-009_Data_Retention_and_Deletion_Schedule.md) | **`RG-R11` — this register supplies the obligations `LG-009` derives from** (`FR-GRC-032`) | `OB-09` 7 years; `OB-13` 5 years; `RT8` limitation period |
| [`LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md`](LG-018_EWaste_EPR_and_Environmental_Compliance_Statements.md) | **`OB-16`…`OB-21` depend on its `EW1`–`EW5`; its `O-03` depends on this file** | **Mutual dependency across waves (`O-04`)** |
| [`LG-021_ISMS_Policy_Set.md`](LG-021_ISMS_Policy_Set.md) | **`OB-32`; `RG7` = its `CS1`**; §4.13.7 there points here | The cyber regime |
| [`LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md`](LG-012_Cross_Border_Data_Transfer_and_Residency_Statement.md) | **`OB-12`; `RG7` = its `RD3`** | Transfer notification |
| [`LG-008_Privacy_Notice_and_Consent_Copy.md`](LG-008_Privacy_Notice_and_Consent_Copy.md) · [`LG-010_Data_Subject_Request_Handling_Content.md`](LG-010_Data_Subject_Request_Handling_Content.md) | `OB-11`, `OB-13`, `OB-15`; §6.2 | Check **F6**; breach and rights timeframes |
| [`LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md`](LG-022_Quality_Policy_and_ISO_9001_Statement_Set.md) | **`OB-34`…`OB-36`; §4.4 should hold the certificate** (`O-03`) | Certificate scope and cycle |
| [`LG-014_Refund_Cancellation_and_Compensation_Policy.md`](LG-014_Refund_Cancellation_and_Compensation_Policy.md) | **`OB-30`, `OB-31`; `RF1`** | Consumer and digital-commerce duties |
| [`LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md`](LG-023_Anti_Bribery_Ethics_and_Whistleblowing_Content.md) | §4.6.7 disclosure over concealment; its §4.8.5 external reporting | Reporting duties |
| [`../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-014_VAT_Return_Pack_Mushak_9_1.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-014_VAT_Return_Pack_Mushak_9_1.md) · [`../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md`](../05_Document_and_Print_Templates/05B_Finance_and_Statutory/DT-010_Tax_Invoice_Mushak_6_3.md) | `OB-01`, `OB-02` | Form content and deadlines |
| [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-037_Tax_Code_VAT_Rate_and_Mushak_Mapping_Register.md) · [`../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md`](../02_Master_Data_and_Configuration/02E_Finance_and_Statutory/MD-041_Fiscal_and_Bangladesh_Holiday_Calendar.md) | Rates and the calendar deadlines are computed against | Tax configuration |
| [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-020_SOP_Month_End_and_Year_End_Close.md) · [`../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md`](../06_Process_SOP_and_Workflow/06B_Standard_Operating_Procedures/SP-021_SOP_Payroll_Run_and_Statutory_Filing.md) | **Where `OB-01`…`OB-09` and `OB-22`…`OB-26` are actually operated** | Filing steps and approvals |
| `OP-*` runbooks · `RF-011` risk register | Escalation and risk recording | The calendar and its escalations |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Legal_Document.md` — ten sections in order; additions declared
- [x] **36 obligations registered with owner, recurrence, deadline, evidence and consequence** per `FR-GRC-023`, satisfying `RG-R1`
- [x] **Every unverified element marked `‡`, and the three verified against an approved specification distinguished** (`CL-01`)
- [x] Twelve operating rules, tying the register to `M60`'s discharge, calendar, escalation and change-monitoring machinery
- [x] Licence-register content specified, with its emptiness stated
- [x] Ten notice and disclosure types mapped to their content owner
- [x] Regulator-handling rules stated, including the absolute escalation under `T-A17` and the no-destruction rule
- [x] **§4.7 states nine known gaps and §9.6 keeps it published until empty** (`CL-02`)
- [x] **The one question asked in three files identified and consolidated** (`RG7` = `CS1` = `RD3`, `O-09`)
- [x] All internal links resolve
- [x] Bengali counterpart — n/a per `CG-010` §3.2
- [ ] **G6 by an external tax adviser and an external legal adviser** — outstanding. **`WV-02`: cannot be waived**
- [ ] **`RG1`–`RG10` answered; every `‡` element verified** — outstanding; `PR-04` blocks approval
- [ ] **Registration certificates produced and §4.4 populated** — outstanding, `O-02`
- [ ] **The ISO 9001 certificate recorded** — outstanding, `O-03`; a public claim depends on it
- [ ] **Environmental rows completed once `LG-018` `EW1` is answered** — outstanding, `O-04`; **a `W3` file waiting on a `W5` file**
- [ ] **The limitation period stated** — outstanding, `O-06`; `LG-009` `RT8`
- [ ] **Insurance register created** — outstanding, `O-07`
- [ ] Named approver recorded — pending
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
