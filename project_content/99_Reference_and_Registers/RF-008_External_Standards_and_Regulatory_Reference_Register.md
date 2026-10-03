---
id: RF-008
title: External Standards and Regulatory Reference Register
project: 1000FiX ERP System v2.0
content_type: Generic
template: TPL_Content_File_Front_Matter.md
template_version: 1.0
version: 1.0
date: 2026-08-18
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Compliance with Legal & Compliance
author: Compliance with Programme Content Lead, Finance and Platform Engineering
reviewers: [Legal Counsel, CFO, CTO, Quality Manager, Data Protection Officer (unappointed — PD-15), Content Design Lead, Localisation Lead, Sustainability Lead, HSE Lead]
approver: Programme Content Lead
content_class: E
purpose: >
  The register of every external standard, statute, statutory instrument and industry
  specification the content set must conform to, with its version, its currency status and the
  date that currency was verified. Statutory and standards references go stale silently. Risk
  `RSK-035` records that this programme has already cited a statute repealed twice and a withdrawn
  NIST revision because no currency-review control existed, and audit `00-07` H2-13 records tax
  figures resting on press reporting rather than enacted law. This register is the content-side
  discharge of `DoD-17`. Verification on 2026-08-18 found **four instruments the content set cites
  in a superseded form**, one of which — ISO 9001:2015 — is replaced by a new edition **inside the
  programme window**, re-opening 38 content files.
traces_to: [DoD-17, RSK-035, 00-07, CG-012, CM-R8, CG-013, RF-001, RF-002, RF-006, RF-011, RF-012, LG-024, MD-037, 05-06]
priority: P2
wave: W1
bilingual: no
bn_counterpart: n/a
sources:
  - source: ISO — ISO/FDIS 9001 issued; publication of ISO 9001:2026 scheduled 16 September 2026, replacing ISO 9001:2015, with a three-year transition to September 2029. https://www.iso.org/standard/88464.html and certification-body transition guidance (BSI, DNV, SGS, Intertek, TÜV, DQS)
    verified: 2026-08-18
    class: P2
  - source: Bangladesh — Personal Data Protection Ordinance 2025 issued 6 Nov 2025; Personal Data Protection (Amendment) Ordinance 2026 (Ordinance 23 of 2026) promulgated 5 Feb 2026; Ordinance repealed and Personal Data Protection Act 2026 (Law 63 of 2026) passed by Parliament April 2026; 18-month compliance window from gazette publication
    verified: 2026-08-18
    class: P2
  - source: Bangladesh NBR — Mushak 9.1 monthly VAT return due by the 15th day of the month following the tax period, filed through the VAT Online System; online submission mandatory from July 2026; late-filing penalty and 2% monthly interest
    verified: 2026-08-18
    class: P2
  - source: Bangladesh Ministry of Commerce — Digital Commerce Operation Guidelines 2021 (issued 4 July 2021): marketplace must pay a third-party seller within 10 days after deducting charges unless otherwise agreed; complaints must be recorded and resolved within 72 hours
    verified: 2026-08-18
    class: P2
  - source: Bangladesh — Consumer Rights Protection Act 2009 §60: complaint to the Director General within 30 days of the cause of action. No replacing Act enacted as at August 2026
    verified: 2026-08-18
    class: P2
  - source: Bangladesh — Hazardous Waste (E-waste) Management Rules 2021: EPR framework, Department of Environment registration, WEEE collection targets 10% year one rising 10 points annually to 50% in year five (2026)
    verified: 2026-08-18
    class: P2
  - source: W3C — WCAG 2.2 is the current W3C Recommendation and the basis for compliance in 2026; WCAG 3.0 remains a Working Draft (updated March 2026, ~174 outcome-based requirements), Candidate Recommendation anticipated Q4 2027, Recommendation no earlier than 2028
    verified: 2026-08-18
    class: P2
  - source: Bangladesh — Cyber Security Act 2023 repealed 22 May 2025 and replaced by the Cyber Security Ordinance 2025 (Ordinance 25 of 2025); National Cyber Security Council established 26 August 2025
    verified: 2026-08-18
    class: P2
  - source: Enumeration of external source strings across project_content/, run 2026-08-18 — 229 distinct non-repository sources across 1,642 declarations
    verified: 2026-08-18
    class: P1
supersedes: none
review_due: 2026-11-18
---

# RF-008 — External Standards and Regulatory Reference Register

> **This register is authoritative for currency.** Under `RF-006` `CD-13`, no other content file
> re-states a currency date for an external instrument. A file cites `RF-008` `ST-nn`; this file
> carries the date. Currency asserted per file goes stale per file.

---

## 1. Purpose

`RSK-035` in `00-04` is unusually candid for a risk register:

> **Regulatory citations drift out of date.** The specification cited a statute repealed twice,
> and a withdrawn NIST revision, because no currency-review control existed.

The response was `DoD-17` — *"Regulatory citations verified current, with a verified-on date"* —
added to the module Definition of Done. `DoD-17` binds module specifications. **Nothing bound the
content set**, which now carries **229 distinct external source strings across 1,642 declarations**
in 443 files, including nine statutory instruments on which 41 Class A and B files depend.

This register is that control. It states, for every external instrument the content set relies on:
the exact citation, the version in force, whether the content set cites it correctly, and when
that was last verified.

**Verification on 2026-08-18 found four instruments cited in a superseded form.** One of them is
not a clerical matter: **ISO 9001 is being replaced on 16 September 2026**, four weeks after this
register was written, and 38 content files cite clauses of the 2015 edition. The company's ISO
9001:2015 certification is described throughout the programme as its principal market
differentiator.

---

## 2. Scope

**In scope** — every external instrument the content set conforms to or cites as authority:
Bangladesh statutes and statutory instruments; international standards; W3C, IETF, Unicode and
OMG specifications; regulator guidance; platform and vendor specifications with contractual force.

**Out of scope**

| Excluded | Owner |
|---|---|
| Where the programme's copy of a source lives, and who holds it | `RF-002` §4.3 |
| The evidence class of a citation | `RF-002` §4.1 |
| Compliance itself — whether the company *complies* | `LG-024`, `M60`, `M51` |
| Internal specifications | `RF-002` `SRC-01`…`SRC-08` |
| Contractual instruments with counterparties | `LG-001`, `M24` |

---

## 3. Audience

| Reader | Uses this register to |
|---|---|
| **Legal & Compliance** | See every external obligation the content set asserts, and its currency |
| **A gate G6 verifier** | Verify a Class A file against the instrument actually in force |
| **The Quality Manager** | Plan the ISO 9001:2026 transition against the 38 files that cite the 2015 edition |
| **A content author** | Cite the correct instrument the first time |
| **The CTO** | See which standards decisions are unmade — `WCAG 2.2`, `RFC 9457`, the ISO transition |
| **An external auditor** | See a maintained currency control rather than an assertion of currency |

---

## 4. Content

### 4.1 How to read

| Column | Meaning |
|---|---|
| **ID** | `ST-nn`, permanent, never reused. Files cite this, not a re-description |
| **Instrument** | Exact citation as it must be written |
| **Status** | `IN FORCE` · `IN FORCE — SUPERSESSION SCHEDULED` · `SUPERSEDED` · `DRAFT` |
| **Content set cites** | `CORRECT` · `STALE` · `AMBIGUOUS` · `UNVERIFIED` |
| **Consuming files** | Content files that depend on it. Impact set for `RF-002` §4.5 |
| **Verified** | Date the **status** was checked. Not the date a file was written |

**The `UNVERIFIED` status is used, not avoided.** A Class A statutory file whose instrument has not
been verified by an external verifier at gate G6 is marked `UNVERIFIED` here even where the
citation looks right. `WV-02` makes G6 unwaivable for six `LG` files and 26 `DT` files, and none
has been run.

---

### 4.2 Bangladesh statutes and statutory instruments

| ID | Instrument | Status | Cites | Consuming files | Verified |
|---|---|---|:--:|---|:--:|
| `ST-01` | **Value Added Tax and Supplementary Duty Act 2012**, with the **VAT and Supplementary Duty Rules 2016** | `IN FORCE` | ⚠ `AMBIGUOUS` — **eight different citation strings** for one Act (`RF-002` §4.8) | `MD-037`, `DT-010`–`DT-016`, `DT-019`, `DT-020`, `LG-009`, `RP-009`, `TS-009`, `SP-020`, `M51` — **17** | 2026-08-18 |
| `ST-02` | **Mushak forms 6.1, 6.2, 6.3, 6.6, 9.1** prescribed under the VAT and SD Rules 2016 | `IN FORCE` | `CORRECT` | `DT-010`–`DT-014`, `MD-037` | 2026-08-18 |
| `ST-03` | **Mushak 9.1 filing basis** — monthly, due by the **15th day of the month following** the tax period, through the NBR VAT Online System. Online submission **mandatory from July 2026**. Nil returns required. Late filing: penalty plus 2% monthly interest | `IN FORCE` | ❌ **CONTESTED — see §4.7 `SR-01`** | `DT-014`, `MD-037`, `RP-009`, `SP-020`, `05-06` `NFR-100` | 2026-08-18 |
| `ST-04` | **Income Tax Act 2023** and the Finance Act in force for the assessment year | `IN FORCE` | ⚠ `UNVERIFIED` — the applicable Finance Act is not named in any file | `MD-043`, `DT-041`, `SP-021`, `TS-010` | 2026-08-18 |
| `ST-05` | **Personal Data Protection Act 2026 (Act 63 of 2026)** | `IN FORCE` — compliance window to **~May 2027** | ❌ **STALE in 6 files — see §4.7 `SR-02`** | `LG-008`–`LG-012`, `UI-042`, `NT-002`, `HC-019`, `AP-012`, `TS-017`, `MD-012`, `MD-013` — **12** | 2026-08-18 |
| `ST-06` | **Consumer Rights Protection Act 2009**, §60 — complaint to the Director General within **30 days** of the cause of action | `IN FORCE` — **no replacing Act as at August 2026** | ⚠ `AMBIGUOUS` — cited under two names, *Consumer Rights Protection Act* (25×) and *Consumers' Right Protection Act* (7×) | `LG-013`, `LG-014`, `EO-013`, `SP-028`, `DT-039` | 2026-08-18 |
| `ST-07` | **Digital Commerce Operation Guidelines 2021** (Ministry of Commerce, 4 July 2021) — seller settlement **within 10 days**; complaint resolution **within 72 hours** | `IN FORCE` | `CORRECT` — but **the obligations are unmet**, `AUDIT-018` `EO-01` | `LG-004`, `EO-001`, `EO-002`, `EO-013`, `DT-039`, `SP-024` | 2026-08-18 |
| `ST-08` | **Bangladesh Labour Act 2006** (as amended) with the **Bangladesh Labour Rules 2015** | `IN FORCE` | ⚠ `AMBIGUOUS` — five citation variants | `MD-042`, `MD-043`, `DT-041`, `DT-042`, `SP-021`–`SP-023`, `TR-015`, `LG-020` | 2026-08-18 |
| `ST-09` | **Cyber Security Ordinance 2025 (Ordinance 25 of 2025)** — repealed and replaced the Cyber Security Act 2023 on 22 May 2025. National Cyber Security Council established 26 August 2025 | `IN FORCE` | `CORRECT` | `LG-020`, `LG-021` | 2026-08-18 |
| `ST-10` | **Hazardous Waste (E-waste) Management Rules 2021** — EPR framework; Department of Environment registration; WEEE collection targets 10% → **50% in year five (2026)** | `IN FORCE` | ⚠ `UNVERIFIED` — **the regulated-entity question is undecided** (`PD-16`) | `MD-047`, `LG-018`, `DT-035`, `SP-026`, `EO-014` | 2026-08-18 |
| `ST-11` | **Companies Act 1994** — RJSC Schedule X annual return within 21 days of the AGM (§36) | `IN FORCE` | `CORRECT` | `RP-009`, `MD-002` | 2026-08-18 |
| `ST-12` | **Evidence Act 1872**, as amended by the **Evidence (Amendment) Act 2022** — admissibility of electronic evidence | `IN FORCE` | `CORRECT` | `LG-019`, `M24`, `UI-038` | 2026-08-18 |
| `ST-13` | **Money Laundering Prevention Act 2012**; **Anti-Corruption Commission Act 2004**; **Public Interest Information Disclosure (Protection) Act 2011** | `IN FORCE` | `CORRECT` | `LG-023`, `M60` | 2026-08-18 |
| `ST-14` | **Copyright Act 2023**; **Information and Communication Technology Act 2006**; **Stamp Act 1899** | `IN FORCE` | `CORRECT` | `KB-003`, `LG-019`, `DT-030` | 2026-08-18 |
| `ST-15` | **Bangla Bhasha Prachalan Ain 1987** — Bengali language use in official documents | `IN FORCE` | `CORRECT` | `BN-001`, `BN-002`, `CG-010` | 2026-08-18 |
| `ST-16` | **BTRC** — Do Not Disturb register; **National Equipment Identity Register (NEIR)** | `IN FORCE` | ⚠ `UNVERIFIED` — DND time restrictions cited from practice, not from a published instrument | `NT-003`, `NT-004`, `MD-021` | 2026-08-18 |

---

### 4.3 International standards

| ID | Instrument | Status | Cites | Consuming files | Verified |
|---|---|---|:--:|---|:--:|
| `ST-20` | **ISO 9001:2015** Quality management systems — Requirements | ⚠ **`IN FORCE` — SUPERSESSION SCHEDULED 16 September 2026** | ❌ **STALE from Sept 2026 — see §4.7 `SR-03`** | **38 files** across `LG`, `DT`, `SP`, `TR`, `KB`, `MD` | 2026-08-18 |
| `ST-21` | **ISO 9001:2026** — replaces ISO 9001:2015; publication **16 September 2026**; transition ends **September 2029**; first certificates not expected before Q3 2027 | `IN FORCE` from Sept 2026 | **Not cited anywhere** | — | 2026-08-18 |
| `ST-22` | **ISO/IEC 27001:2022** Information security management systems | `IN FORCE` | `CORRECT` — the company is **not certified**; cited as an alignment target | `LG-021`, `05-06` | 2026-08-18 |
| `ST-23` | **ISO 22301** clause 8.5 — business continuity | `IN FORCE` | `CORRECT` | `OP-012` | 2026-08-18 |
| `ST-24` | **W3C WCAG 2.1** Level AA | ⚠ **Superseded as a Recommendation by WCAG 2.2 (October 2023)** | ⚠ **`STALE` as a standards choice — see §4.7 `SR-04`** | `CG-011`, `UI-010`, `TS-016`, `RP-007`, `MM-002`, `04-00` `PS-04`, `05-06` | 2026-08-18 |
| `ST-25` | **W3C WCAG 2.2** — the current W3C Recommendation and the 2026 compliance basis | `IN FORCE` | **Not cited anywhere** | — | 2026-08-18 |
| `ST-26` | **W3C WCAG 3.0** — Working Draft, updated March 2026, ~174 outcome-based requirements; Candidate Recommendation anticipated Q4 2027; Recommendation **no earlier than 2028** | `DRAFT` | Correctly **not** cited | — | 2026-08-18 |
| `ST-27` | **NIST SP 800-88 Rev.1** Guidelines for Media Sanitization | `IN FORCE` | `CORRECT` — note `RSK-035` records a **withdrawn NIST revision** previously cited elsewhere | `DT-034`, `SP-012`, `LG-017` | 2026-08-18 |
| `ST-28` | **IEC 61340-5-1** / **ANSI-ESD S20.20** — electrostatic discharge control | `IN FORCE` | `CORRECT` | `KB-013`, `MD-046` | 2026-08-18 |
| `ST-29` | **IEC 61010-1** measurement categories CAT II/III/IV | `IN FORCE` | `CORRECT` | `KB-012`, `MD-046` | 2026-08-18 |
| `ST-30` | **UN Manual of Tests and Criteria, section 38.3** — lithium battery transport | `IN FORCE` | `CORRECT` | `KB-013`, `SP-009` | 2026-08-18 |
| `ST-31` | **Basel Convention** on transboundary movements of hazardous wastes; **Montreal Protocol** HCFC phase-out | `IN FORCE` | `CORRECT` | `LG-018`, `KB-013`, `MD-047` | 2026-08-18 |
| `ST-32` | **ANSI Z535.6** safety-information signal words (DANGER / WARNING / CAUTION / NOTICE) | `IN FORCE` | `CORRECT` | `KB-002`, `KB-013`, `DT-002` | 2026-08-18 |
| `ST-33` | **OMG BPMN 2.0.2** | `IN FORCE` | `CORRECT` | `SP-003`, `MM-003` | 2026-08-18 |

---

### 4.4 Technical and platform specifications

| ID | Instrument | Status | Cites | Consuming files | Verified |
|---|---|---|:--:|---|:--:|
| `ST-40` | **RFC 9457** Problem Details for HTTP APIs (July 2023) | `IN FORCE` | ❌ **`API-04` diverges with no ruling** — `PD-20` | `AP-006`, `AP-002`, `UI-004` | 2026-08-18 |
| `ST-41` | **RFC 9745** The Deprecation HTTP Response Header Field (2025) | `IN FORCE` | `CORRECT` | `AP-011` | 2026-08-18 |
| `ST-42` | **IETF HTTPAPI `draft-ietf-httpapi-ratelimit-headers`** | ⚠ `DRAFT` | ⚠ Cited as though stable; a draft may change | `AP-005` | 2026-08-18 |
| `ST-43` | **Standard Webhooks specification** | `IN FORCE` (community) | ⚠ **No webhook signature scheme exists anywhere** — `PD-18` | `AP-004` | 2026-08-18 |
| `ST-44` | **AsyncAPI 3.0** (November 2023) | `IN FORCE` | `CORRECT` | `AP-003` | 2026-08-18 |
| `ST-45` | **OpenAPI 3.1** — mandated by `05-03` `IP-08` | `IN FORCE` | `CORRECT` | `AP-002`, `AP-001` | 2026-08-18 |
| `ST-46` | **Unicode CLDR** — `bn` numbers, dates, currencies, plurals, ordinals, `weekData` | `IN FORCE`, versioned | `CORRECT` — **the only external source cited with a file-level reference** | `BN-006`, `BN-007` | 2026-08-18 |
| `ST-47` | **XLIFF**, **TMX 1.4b**, **TBX**, **MQM** | `IN FORCE` | `CORRECT` | `BN-008`, `BN-018` | 2026-08-18 |
| `ST-48` | **GSM-7 / UCS-2 SMS segmentation** — Bengali segments at **70 characters**, not 160 | `IN FORCE` | `CORRECT` | `NT-004`–`NT-007`, `BN-014` | 2026-08-18 |
| `ST-49` | **WhatsApp Business Platform template categories** — Meta categorisation policy effective April 2025 | `IN FORCE` | ⚠ Vendor policy; changes without notice. **Pre-approval lead time is a schedule dependency** | `NT-008`, `NT-026` | 2026-08-18 |
| `ST-50` | **bKash PGW tokenised checkout**, **Nagad merchant API**, **SSLCOMMERZ v4 + IPN** | `IN FORCE` | ⚠ `UNVERIFIED` — **three payment availability commitments do not reconcile** (`AUDIT-016` `AP-06`) | `AP-009`, `MD-038`, `UI-039` | 2026-08-18 |
| `ST-51` | **Odoo 19.0 documentation**; **OCA** module sources | `IN FORCE` | `CORRECT` | `OP-007`, `02-05` `TD-01` | 2026-08-18 |
| `ST-52` | **Google Play Console** / **Apple App Store** release policy | `IN FORCE` | `CORRECT` | `OP-011` | 2026-08-18 |
| `ST-53` | **EU AI Act Article 50** transparency obligations | `IN FORCE` (EU) | ⚠ **Extraterritorial applicability to a Bangladesh operator is unassessed** | `HC-019` | 2026-08-18 |

---

### 4.5 Methodologies cited as authority

Not standards, and marked so they are not mistaken for them. Each is a `P2` or `P3` source under
`RF-002` `EV-03` and may not carry a statutory claim.

| ID | Source | Used for | Class |
|---|---|---|:--:|
| `ST-60` | New World Kirkpatrick Model | `TR-001` evaluation design | P3 |
| `ST-61` | Knowledge-Centered Service (KCS) | `KB-001`, `KB-015` | P3 |
| `ST-62` | Google SRE; incident-command practice; PagerDuty; Atlassian Statuspage | `OP-004`, `OP-005`, `OP-013` | P3 |
| `ST-63` | Microsoft Writing Style Guide; Nielsen Norman Group | `CG-003`, `UI-006` | P3 |
| `ST-64` | ITSM tiered support and escalation practice | `OP-001` | P3 |
| `ST-65` | Classical item analysis | `TR-005`, `TR-006` | P3 |

---

### 4.6 Currency review

| Instrument class | Review cadence | Trigger for immediate review | Owner |
|---|---|---|---|
| Bangladesh tax (`ST-01`–`ST-04`) | **Annual, at the Finance Act** | Any NBR circular, SRO or Paripatra | Tax Manager with CFO |
| Data protection (`ST-05`) | **Quarterly** until the ~May 2027 compliance deadline | Any NDMA rule, guidance or determination | Legal Counsel with DPO *(unappointed)* |
| Consumer / commerce (`ST-06`, `ST-07`) | Semi-annual | Any Ministry of Commerce guideline amendment | Legal Counsel |
| Labour (`ST-08`) | Annual | Any amendment to the Act or Rules | HR Director with Legal |
| Environmental (`ST-10`) | **Annual, at the EPR target step** | DoE notification; target change | Sustainability Lead |
| ISO standards (`ST-20`–`ST-23`) | Annual | **Any FDIS or publication announcement** | Quality Manager |
| W3C / IETF / Unicode (`ST-24`–`ST-26`, `ST-40`–`ST-47`) | Semi-annual | New Recommendation or RFC | Content Design Lead; Platform Engineering Lead |
| Vendor and platform (`ST-49`–`ST-52`) | **Quarterly** | Any vendor policy notice | Platform Engineering Lead |

**Rule `SC-01`.** A currency review that changes a status **fires `RF-002` §4.5** to identify the
consuming files, and each is re-opened at the gate stated there. Changing the status here and not
re-opening the files is the failure `RSK-035` describes.

**Rule `SC-02`.** No content file states a currency date for an external instrument. It cites
`RF-008` `ST-nn`. (`RF-006` `CD-13`.)

---

### 4.7 Findings — four instruments cited in a superseded or contested form

#### `SR-01` — the Mushak 9.1 filing basis is stated two ways inside the programme

| Source | Basis stated |
|---|---|
| `05-06` `NFR-100` | **Monthly**, filed by the **15th of the following month** through the NBR VAT Online portal |
| A secondary source cited in a `DT` file | **Quarterly**, within 15 days of quarter-end, for certain registered persons |

The `DT` file that carries the quarterly citation flags the conflict itself and defers it to G6 —
correct behaviour, and the reason this was findable.

**Verified position (2026-08-18).** The standard obligation is **monthly, by the 15th day of the
month following the tax period**, filed through the VAT Online System. Online submission became
**mandatory from July 2026**. Nil returns are required. `NFR-100` is correct for the standard
case.

**Remediation.** Adopt the monthly basis as the design assumption; retain the quarterly note as an
explicitly-flagged exception to be confirmed at G6 against the taxpayer's own registration class.
`M51` and `DT-014` must not implement two bases. **Still requires G6** — this file's source is
`P2`, and `RF-002` `EV-03` does not permit a `P2` source alone to settle a statutory obligation.

#### `SR-02` — six files cite a repealed instrument

| Name used | Occurrences |
|---|---:|
| Personal Data Protection **Act 2026** | 50 |
| Personal Data Protection **Ordinance 2025** | **6** |

**Verified sequence.**

| Date | Event |
|---|---|
| 6 Nov 2025 | Personal Data Protection **Ordinance** 2025 issued |
| 5 Feb 2026 | Personal Data Protection (Amendment) Ordinance 2026 (Ordinance 23 of 2026) — amends residency for critical information infrastructure and restricted data |
| April 2026 | Ordinance **repealed**; Personal Data Protection **Act 2026 (Law 63 of 2026)** passed |
| ~May 2027 | End of the 18-month compliance window from gazette publication |

The six citations were correct when written and are now stale. **This is precisely `RSK-035`
recurring**, at a smaller scale, four months after the mitigation was written.

**Remediation.** Standardise on *Personal Data Protection Act 2026 (Act 63 of 2026)*. Retain the
Ordinance lineage **only** where the February 2026 residency amendment is relied on — which is
where `NFR-086a/b/c` and `LG-012` rely on it. Logged as `RF-006` `CD-09`.

#### `SR-03` — ISO 9001:2015 is replaced inside the programme window

**This is the most consequential finding in this register.**

| Fact | Value |
|---|---|
| ISO 9001:2026 publication | **16 September 2026** — four weeks after this register |
| Replaces | ISO 9001:2015 |
| Transition ends | **September 2029** |
| First 2026-edition certificates expected | Not before **Q3 2027** |
| Content files citing ISO 9001:2015 clauses | **38** |
| Programme window | 36 months from 2026 — **the transition falls entirely inside it** |

The programme describes ISO 9001:2015 certification as the company's **principal market
differentiator**. `LG-022` is the quality policy set inspected at every surveillance audit;
`DT-043` carries the NCR/CAPA and internal audit forms the certification body inspects; `P11` is
the application auditors will use; `SP-029` is the audit-and-CAPA process; `TR-016` trains 20–60
auditors in clause-referenced classification.

**Nothing in the programme mentions the revision.** Every one of the 38 files cites a clause number
of an edition that will be superseded before Wave 2.

**Remediation.**

1. `PD-21` *(new, raised here)* — **ISO 9001:2026 transition plan**, owned by the Quality Manager
   with the CEO, needed at **W1**. It is a certification decision, not a content decision.
2. Do **not** retro-cite the 2026 edition before publication. Clause numbering is expected to move;
   citing an unpublished edition would repeat `RSK-035` in the opposite direction.
3. Add `ST-21` as a **watched** instrument, reviewed on publication, with `RF-002` §4.5 firing the
   38-file re-open at that point.
4. `LG-022`, `DT-043`, `SP-029`, `TR-016` and `MD-046` carry a transition note in their next
   revision.

#### `SR-04` — the contractual accessibility standard is one revision behind

`PS-04` and `05-06` make **WCAG 2.1 AA** contractual. **WCAG 2.2 has been the W3C Recommendation
since October 2023** and is the 2026 compliance basis; WCAG 3.0 remains a Working Draft with a
Recommendation no earlier than 2028.

WCAG 2.2 adds nine success criteria to 2.1. Three are material to this programme specifically:

| Criterion | Why it matters here |
|---|---|
| **2.5.8 Target Size (Minimum)** | `P02` and `P09` are used **one-handed, outdoors, gloved**, on low-end Android |
| **3.3.7 Redundant Entry** | `P01` booking-funnel conversion target is **> 72%**; re-entry is a known drop-off cause |
| **3.3.8 Accessible Authentication (Minimum)** | OTP-based login on every external portal |

**This is a decision, not a defect.** Holding at 2.1 AA is defensible if made deliberately and
recorded; it is not defensible by omission. Raised as `RF-006` `PD-22` — *adopt WCAG 2.2 or hold
at 2.1 AA, and record which*. `TS-016` currently tests to a superseded standard either way.

---

### 4.8 Verification statistics

| Measure | Value |
|---|---:|
| Instruments registered | **44** (`ST-01`–`ST-16`, `ST-20`–`ST-33`, `ST-40`–`ST-53`) |
| Methodologies registered | 6 |
| Status `IN FORCE` | 40 |
| Status `IN FORCE — SUPERSESSION SCHEDULED` | **1** (`ST-20`) |
| Status `DRAFT` | 2 (`ST-26`, `ST-42`) |
| Cites `CORRECT` | 24 |
| Cites `AMBIGUOUS` (multiple citation strings) | 4 |
| Cites `STALE` | **3** (`ST-05`, `ST-20` from Sept 2026, `ST-24`) |
| Cites `UNVERIFIED` | 5 |
| **Instruments with a controlled programme copy** | **1 of 44** — ISO 9001:2015 only (`RF-002` `O-04`) |
| Class A/B files awaiting **unwaivable** G6 verification | **32** |

**One controlled copy out of forty-four is the structural finding.** Every other status in this
register rests on published text read on the verification date, not on a version-stamped
instrument held by the company. That is adequate for `P2` currency tracking and **not adequate for
G6**, which is why 32 files remain `UNVERIFIED` regardless of how correct their citations look.

---

## 5. Dependencies

| Depends on | Why |
|---|---|
| `RF-002` | Registers where each source lives; §4.5 is the impact map `SC-01` fires |
| `CG-012`, `CM-R8` | The sourcing and verification rules |
| `CG-013` | Escalation when an instrument changes materially |
| `DoD-17` | The module-side control this file mirrors for content |
| `LG-024` | The regulator-facing obligation register |

| Depended on by | Why |
|---|---|
| Every Class A and B file at gate **G6** | Verification against the instrument in force |
| `RF-002` §4.5 | Trigger events |
| `RF-011` | Currency risk `CR-nn` |
| `RF-012` | Findings `SR-01`–`SR-04` |
| `MD-037`, `DT-010`–`DT-016`, `LG-008`–`LG-012`, `LG-022` | Their governing instruments |

---

## 6. Maintenance

| Item | Value |
|---|---|
| Review cadence | **Per instrument class**, §4.6. Whole-register review at every wave boundary |
| Update trigger | Any status change; any new external instrument cited by a new file |
| Currency rule | A `verified:` date is the date the **status was checked**, never the date a file was written, and **never a future date** (`RF-002` `EV-06`, `RF-006` `CD-02`) |
| Single-source rule | No other content file states a currency date (`SC-02`, `RF-006` `CD-13`) |
| Owner | Compliance with Legal & Compliance |
| Escalation | A status moving to `SUPERSEDED` escalates to Legal & Compliance and the affected domain owner **the same day**, and fires `SC-01` |

---

## Approval Record

| Gate | Required for Class E | Reviewer | Status |
|---|:--:|---|---|
| G1 Editorial | ● | Content Design | Not started |
| G2 Factual | ● | Compliance with Legal Counsel | Not started |
| G3 Technical | ○ | — | Not required |
| G4 Linguistic | ○ | — | Not required |
| G5 Legal | ○ | Requested — Legal Counsel, given §4.2 | Not started |
| G6 Statutory | ○ | **Not required for this file; required for the 32 files it tracks** | — |
| Final approver | — | **Programme Content Lead** | **Unappointed** |

> **Corrected at audit.** This file previously named **Legal Counsel** as final approver. `CG-007`
> §2.1 assigns the final approver by **content class**, and Class E — internal governance — is
> approved by the **Programme Content Lead**. Legal Counsel remains the `G5` reviewer and the owner
> of the statutory judgements in §4.2, which is where their authority belongs; the *approval* of an
> internal governance register is not theirs. Recorded as `AUDIT-020` finding `RF99-03`.

---

## Open Items

| # | Item | Owner | Blocks |
|---|---|---|---|
| `RF-008-OI-01` | **`SR-03` — ISO 9001:2026 publishes 16 Sept 2026.** 38 files cite 2015 clauses; no transition plan exists. Raised as `PD-21` | Quality Manager with CEO | ISO surveillance readiness; `P11`; `LG-022` |
| `RF-008-OI-02` | **`SR-02` — six files cite the repealed PDPO 2025** | Legal & Compliance | Statutory citation integrity |
| `RF-008-OI-03` | **`SR-01` — Mushak 9.1 basis stated two ways**; monthly verified from a `P2` source, **G6 still required** | Tax Manager with CFO | `DT-014`, `M51` implementation |
| `RF-008-OI-04` | **`SR-04` — WCAG 2.1 vs 2.2 undecided** (`RF-006` `PD-22`) | CTO with Content Design | `TS-016`; `PS-04` conformance claims |
| `RF-008-OI-05` | **1 of 44 instruments has a controlled copy.** 32 Class A/B files cannot pass G6 without one | Legal & Compliance with `M24` | Every Class A file's approval |
| `RF-008-OI-06` | **`ST-10` e-waste regulated-entity question undecided** (`PD-16`); EPR target reaches 50% in 2026 | Legal + Sustainability | `LG-018`, `MD-047`, `DT-035` |
| `RF-008-OI-07` | **`ST-53` EU AI Act extraterritorial applicability unassessed** | Legal Counsel | `HC-019` |
| `RF-008-OI-08` | **`ST-42` cited as stable and is an IETF draft** | Platform Engineering Lead | `AP-005` |
| `RF-008-OI-09` | **Four instruments carry multiple citation strings**, defeating search | Programme Content Lead | `RF-002` `EV-01` |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Content_File_Front_Matter.md`; register table and maintenance procedure added per `CG-009` §3
- [x] **44 instruments and 6 methodologies** registered with status, citation assessment, consuming files and verification date
- [x] Every status **verified externally on the stated date**, not inherited from a content file's own claim
- [x] Four currency findings `SR-01`–`SR-04` reported with remediation and owner
- [x] Currency review cadence stated per instrument class
- [x] Single-source rule `SC-02` established so currency is not restated per file
- [x] Sources of external verification declared in front matter with class `P2` where they are secondary
- [x] The structural limitation stated — **1 of 44 controlled copies**, so 32 files remain `UNVERIFIED` for G6
- [x] All internal links resolve
- [x] Bengali counterpart — n/a (`bilingual: no`, `CG-010` §3.2)
- [x] Registered in `1000FiX_ERP_Content_Master_Index.md` (rule `CM-R1`)
- [ ] **G5 legal review requested** — outstanding
- [ ] **Named approver recorded — Legal Counsel** — outstanding
- [ ] **`PD-21` ISO 9001:2026 transition plan raised and owned** — outstanding, `RF-008-OI-01`

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
