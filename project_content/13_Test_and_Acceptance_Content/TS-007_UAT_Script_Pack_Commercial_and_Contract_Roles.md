---
id: TS-007
title: UAT Script Pack — Commercial and Contract Roles
project: 1000FiX ERP System v2.0
content_type: Test script
template: TPL_Test_Script.md
template_version: 1.0
version: 1.0
date: 2026-08-19
status: Draft
classification: CONFIDENTIAL — Internal Use Only
owner: Business Owners Forum with QA Lead
author: QA Lead with CCO delegate, account managers and warranty operations
reviewers: [CCO delegate, Sales Manager, Account Manager representatives, Warranty Claims Officer, Marketplace Operations Officer, Retail Operations Head, Finance Manager]
approver: QA Lead with CCO delegate
content_class: E
purpose: >
  The acceptance scripts executed by the roles that set price, sign commitments and recover money
  from third parties — account managers, sales, warranty claims, marketplace operations, retail and
  refurbishment, and marketing. Commercial configuration errors do not announce themselves: a rate
  card with the wrong labour rate, an entitlement that silently absorbs out-of-scope work, or a
  claim window that lapses unnoticed all produce a system that runs correctly and loses money, and
  none of them is visible in a module test. They are found by the person whose number they are.
traces_to: [M07, M08, M09, M10, M11, M12, M36, M37, M38, M39, M40, M14, M20, 05-04, 05-04 §7, 05-05, 06-02 §4, MD-029, MD-030, MD-031, MD-032, MD-033, MD-034, SP-013, SP-014, SP-015, SP-024, SP-025, TR-018, TR-019, DT-030, DT-031, DT-032, DT-033, DT-036, DT-038, DT-039, DT-040, UI-014, UI-017, UI-018, UI-032, UI-033, UI-034, UI-042, TS-001, TS-002, TS-003, TS-006, TS-011, TS-012, TS-018]
priority: P1
wave: W2
bilingual: no
bn_counterpart: n/a
sources:
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-04_Role_Permission_and_Access_Matrix.md §1.4 Commercial (R21 3–6, R22 8–20, R23 2–4, R24 4–10, R25 5–15), §1.5 (R28 4–10); §3.2 Pillar B permission matrix; §7 Approval Authority Matrix discount and contract bands
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-05_Business_Rules_and_Automation_Catalogue.md §5 BRU-CTR-01…08 and BRU-WTY-01…08, §8 BRU-ECM-01…10, §9 BRU-TRF-01…05, §12.2 AUT-015…AUT-030
    verified: 2026-08-19
    class: P1
  - source: 1000fix_ERP_Module/06_Delivery_and_Implementation/06-02_KPI_Benefits_and_Acceptance_Criteria.md §4 Gate 4 G4-01…G4-03, G4-08; Gate 7 G7-01…G7-06; §2.4 KPI-028…036, §2.5 KPI-037…041
    verified: 2026-08-19
    class: P1
supersedes: none
review_due: 2027-02-19
---

# UAT Script Pack — Commercial and Contract Roles

| Item | Value |
|---|---|
| Test level | **UAT** — method in [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 |
| Roles executing | `R21` `R22` `R23` `R24` `R25` `R28` — **6 roles, 26–65 people** |
| Modules covered | `M07` `M08` `M09` `M10` `M11` `M12` `M14` `M36`–`M40`, with `M20` as touchpoint |
| Portals covered | `P03` (Contract, Warranty, Marketplace consoles), `P04`, `P07`, `P08` as counterparty surfaces |
| Environment | `UAT` — frozen for the cycle |
| Test data set | `TS-002` — personas 4, 6, 7, 11; sets `M-01`, `M-02`, `M-07`, `D-04`, `D-06`, `D-09` |
| Wave | W2, extending to W7 for the marketplace block |

> **Template conformance.** As `TS-006`: `TPL_Test_Script.md` at pack level, all six sections
> retained in order with pack-level interpretation.

> **Method by reference.** `UA-01`…`UA-18` and the seven-phase script pattern are in
> [`TS-006`](TS-006_UAT_Script_Pack_Service_Operations_Roles.md) §2.1 and §3.2 (`CP-01`). This pack
> adds `UA-19`…`UA-22` (§2.1), which exist because commercial defects are arithmetic, not workflow.

---

## 1. Traceability

### 1.1 Why commercial roles must execute their own scripts

`M-01` in `TS-002` supplies 99 amounts on 33 approval boundaries. **A tester can confirm that a
discount above 35% requires the CCO. Only the CCO can confirm that 35% is the right number**, that
the band applies to the right basis, and that the resulting margin is one the business will accept.

The same distinction runs through the whole pack:

| A tester can verify | Only the role can verify |
|---|---|
| The rate card was applied | The rate card is the rate card that was agreed with the brand |
| Entitlement decremented by one visit | One visit is what this contract type should consume |
| The claim was submitted in the brand's format | The brand will accept that format |
| Commission calculated at the configured rate | The configured rate matches the seller agreement |
| A refurbished grade was assigned | The grade means what the disclosure says it means |

**Every script in this pack therefore states the expected *number*, not the expected *behaviour*.**
That is `UA-19`, and it is the pack's central discipline.

### 1.2 Traceability obligation

Per `TS-006` §1.2, with the `MD` commercial masters added as a required column: `MD-029` price lists
and rate cards, `MD-030` discounts and vouchers, `MD-031` warranty types and coverage terms,
`MD-032` contract and AMC templates, `MD-033` subscription plans, `MD-034` loyalty tiers. **A
commercial script that does not name the `MD` row it depends on cannot be re-executed after a rate
change**, and rate changes are the most frequent change this category sees.

### 1.3 Role coverage

| Role | Headcount | Scripts | `P0` | Language | Portal | SOP | Course pack |
|---|---:|---:|---:|---|---|---|---|
| `R28` Warranty Claims Officer | 4–10 | **14** | 8 | English | `P03` Warranty Console, `P08` | `SP-014` | **none — `O-05`** |
| `R22` Account Manager (Corporate) | 8–20 | 12 | 5 | English | `P03` Contract Console, `P04` | `SP-015` | `TR-018` |
| `R24` Marketplace Operations Officer | 4–10 | 12 | 6 | English | `P03` Marketplace Console, `P07` | `SP-024` | `TR-019` |
| `R21` Sales Manager | 3–6 | 8 | 3 | English | `P03`, `P06` | `SP-013` | `TR-018` |
| `R25` Retail / Refurbishment Officer | 5–15 | 8 | 4 | English | `P03` | `SP-025` | **none — `O-05`** |
| `R23` Marketing Manager | 2–4 | 6 | 1 | English | `P03`, `P06`, `P12` | **none** | **none — `O-05`** |
| **Total** | **26–65** | **60** | **27** | | | | |

---

## 2. Preconditions

### 2.1 Additional rules for commercial scripts

| # | Rule |
|---|---|
| **UA-19** | **Every script states the expected number** — price, rate, discount, entitlement count, commission, margin, claim value — computed independently before execution, and the executor confirms the number, not the flow (`SL-26` applied to UAT) |
| **UA-20** | Every script names the **`MD` master row** it depends on, so the script can be re-executed after a rate, tier or template change |
| **UA-21** | **Third-party-facing output is verified in the counterparty's format**, not in ours: a claim as the brand receives it, a payout statement as the seller receives it, a consolidated invoice as the corporate client receives it |
| **UA-22** | Every script that creates a **commitment** — a contract, a warranty product, a seller agreement, a rate card — verifies that the commitment cannot be created outside its approved template (`BRU-CTR-01`, `BRU-ECM-01`, `MD-032`) |

### 2.2 Additional preconditions

| # | Precondition | How to establish |
|---|---|---|
| 1 | `TS-006` preconditions 1–4, 7, 9, 11 met | As recorded there |
| 2 | `MD-029`…`MD-034` loaded, **with one rate-card version change scheduled inside the cycle** | `MD-048`; exercises `UA-20` |
| 3 | Contract templates from `MD-032` configured, including one non-standard-terms template | `BRU-CTR-01`; `05-04` §7 |
| 4 | Warranty types from `MD-031` including one with an exclusion the executor must find | `BRU-WTY-07` |
| 5 | A brand partner sandbox or stub in the partner's own claim format | `TS-003` `O-03` |
| 6 | Seller agreement, commission scheme and payout schedule configured | `BRU-BIL-03`, `BRU-BIL-04` |
| 7 | Loyalty tiers and point rules from `MD-034` | `BRU-SRM-10`, `BRU-WTY-06` |
| 8 | A corporate account hierarchy from `MD-015` with sites and departments | `BRU-BIL-07` |
| 9 | Role accounts for all 6 roles with field-level access to `margin`, `commission_rate`, `vendor_price` per `05-04` §5 | **Does not exist** — `TS-002` `O-04` |

---

## 3. Scripts

### 3.1 Block A — `R28` Warranty Claims Officer · 14 scripts

`SP-014` · **the highest-value block in the pack**: `KPI-038` targets warranty revenue leakage
falling from 15–20% to under 2%.

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R28-001` | Work the claim pipeline created automatically from yesterday's closed warranty jobs | `BRU-WTY-02`(C) `AUT-018`; **within 24 h**, `G4-01` | **P0** |
| `UAT-R28-002` | **Try to submit a claim missing a before-photo, and be refused with the missing item named** | `BRU-WTY-01`(H) `BRU-SRM-17`(H) | **P0** |
| `UAT-R28-003` | Submit a complete claim in the brand's required format and confirm it as the brand receives it | `AUT-019`; `UA-21` | **P0** |
| `UAT-R28-004` | **Try to submit a duplicate claim for the same serial and fault within 90 days, and be refused** | `BRU-WTY-03`(H) | **P0** |
| `UAT-R28-005` | Confirm the claim value equals the agreed labour rate plus parts at the completion-date FX rate | `BRU-WTY-05`(C); `MD-029`; `UA-19` | **P0** |
| `UAT-R28-006` | Handle a brand rejection: open a dispute task, gather evidence, resubmit | `AUT-020` | **P0** |
| `UAT-R28-007` | **See a claim approaching the brand's submission window and act before it lapses** | `BRU-WTY-08`(C); `KPI-038` | **P0** |
| `UAT-R28-008` | Reconcile a brand remittance to claims; identify the unmatched difference and its cause | `AUT-021` | **P0** |
| `UAT-R28-009` | **Try to consume a brand consignment part on a non-warranty job, and be refused** | `BRU-WTY-04`(H) | P1 |
| `UAT-R28-010` | Confirm a technician's certification was current at the service date on a claim about to be submitted | `BRU-HRM-01`(H); `KPI-063` zero | P1 |
| `UAT-R28-011` | Sell a warranty extension, and **be refused on a device that fails eligibility** | `BRU-WTY-07`(H); `MD-031` | P1 |
| `UAT-R28-012` | Confirm a Privilege discount applied to labour only, never to parts, consumables or transport | `BRU-WTY-06`(C); `UA-19` | P1 |
| `UAT-R28-013` | **Try to approve the write-off of your own claim, and be refused** | `SOD-11`; `BRU-SEC-07`(H) | P1 |
| `UAT-R28-014` | Report first-submission approval rate and days-to-reimbursement for the period | `KPI-039`, `KPI-040`; `G4-02` ≥ 90% | P2 |

### 3.2 Block B — `R22` Account Manager (Corporate) · 12 scripts

`SP-015` · `TR-018`

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R22-001` | **Try to activate a contract with no covered asset, no entitlements or no billing frequency, and be refused each time** | `BRU-CTR-01`(H) | **P0** |
| `UAT-R22-002` | Activate an AMC and confirm the full preventive schedule generated for the term, on the right dates | `AUT-016` `AUT-017`; `UA-19` | **P0** |
| `UAT-R22-003` | Confirm the RAMC package price derives from the registered appliances, **not a flat fee** | `BRU-CTR-06`(C); `MD-032`; `UA-19` | **P0** |
| `UAT-R22-004` | **Deliver work outside contract scope and confirm it is billed separately, never silently absorbed** | `BRU-CTR-02`(H) | **P0** |
| `UAT-R22-005` | Consume entitlement to its limit, then confirm over-consumption is blocked or billed per configuration — **never invisible** | `BRU-CTR-04`(H) | **P0** |
| `UAT-R22-006` | See a contract's true margin including parts, labour and logistics, and identify a negative-margin contract | `KPI-031`; `UA-19` | P1 |
| `UAT-R22-007` | Take a renewal from the automatic 60-day quotation to a signed extension | `AUT-015` | P1 |
| `UAT-R22-008` | Confirm expiry cancels future scheduled work orders and notifies the customer | `BRU-CTR-03`(C) | P1 |
| `UAT-R22-009` | **Try to issue a contract on non-standard terms without CCO and CFO approval, and be refused** | `05-04` §7; `UA-22` | P1 |
| `UAT-R22-010` | Confirm a service credit calculated automatically from measured SLA breach, and that a manual credit needs CFO approval | `BRU-CTR-08`(C/A); `UA-19` | P1 |
| `UAT-R22-011` | Confirm a healthcare-equipment contract cannot omit calibration scheduling | `BRU-CTR-07`(H) | P2 |
| `UAT-R22-012` | See only your assigned accounts — **and confirm you cannot see another manager's** | `05-04` §1.4 scope `(o)` | P1 |

### 3.3 Block C — `R24` Marketplace Operations Officer · 12 scripts

`SP-024` · `TR-019` · **W7 block**, executed at `G7`

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R24-001` | **Try to let a seller transact before documents are verified, the agreement is signed and you have approved — refused at each stage** | `BRU-ECM-01`(H); `UA-22` | **P0** |
| `UAT-R24-002` | Approve a seller and confirm they can only list in categories they hold a verified qualification for | `BRU-ECM-07`(H) | **P0** |
| `UAT-R24-003` | Confirm a marketplace job is held to the same evidence, QC and warranty standards as an owned job | `BRU-ECM-03`(H); `G7-03` | **P0** |
| `UAT-R24-004` | Confirm commission accrues at the agreed rate after the hold period, to the paisa | `AUT-026`; `MD-030`; `UA-19` | **P0** |
| `UAT-R24-005` | **Open a dispute and confirm the payout is blocked entirely while it is open** | `BRU-BIL-03`(H) | **P0** |
| `UAT-R24-006` | Decide a dispute, record the decision and its evidence, and confirm commission reverses where decided against the seller | `BRU-ECM-09`(H) `BRU-BIL-04`(C) | **P0** |
| `UAT-R24-007` | Confirm a seller below the performance threshold loses visibility automatically, and is suspended below the suspension threshold | `BRU-ECM-04`(C); `UA-19` | P1 |
| `UAT-R24-008` | Confirm registration expiry suspends the seller until renewed | `BRU-ECM-08`(C) | P1 |
| `UAT-R24-009` | Confirm only a customer with a completed transaction can leave a review | `BRU-ECM-02`(H) | P1 |
| `UAT-R24-010` | Confirm a promoted listing is always disclosed as promoted, whatever the boost spend | `BRU-ECM-06`(H) | P1 |
| `UAT-R24-011` | **Try to approve a seller and then approve their payout, and be refused** | `SOD-06`; `BRU-SEC-07`(H) | P1 |
| `UAT-R24-012` | Verify a payout statement as the seller receives it, and confirm 100% payout accuracy on the run | `UA-21`; `KPI-082`; `G7-02` | P1 |

### 3.4 Block D — `R21` Sales Manager · 8 scripts

`SP-013` · `TR-018`

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R21-001` | Approve a discount up to 35%, and **be refused at 40%** | `05-04` §7; `UA-10` | **P0** |
| `UAT-R21-002` | Confirm a rate card change takes effect for new orders and not for in-flight ones | `MD-029`; `CG-006` §5; `UA-20` | **P0** |
| `UAT-R21-003` | Take a quotation to an order at the quoted price, and confirm an expired estimate requires re-issue | `BRU-SRM-13`(H) | **P0** |
| `UAT-R21-004` | Confirm quotation-to-order conversion and gross margin on paid repair for the period | `KPI-032`, `KPI-033`; `UA-19` | P1 |
| `UAT-R21-005` | Approve a standard-terms contract at any value | `05-04` §7 | P1 |
| `UAT-R21-006` | Confirm a dynamic price stayed inside its guard rails, with the decision auditable | `BRU-AIM-02`(H); `G7-06` | P1 |
| `UAT-R21-007` | See the pipeline for your assigned segment only | `05-04` §1.4 scope | P2 |
| `UAT-R21-008` | Confirm a voucher applies once, to the right basis, and cannot be reused | `MD-030`; `UA-19` | P2 |

### 3.5 Block E — `R25` Retail / Refurbishment Officer · 8 scripts

`SP-025`

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R25-001` | **Try to move a trade-in device to refurbishment without a certified destruction record, and be refused** | `BRU-TRF-01`(H) | **P0** |
| `UAT-R25-002` | **Try to pay a trade-in offer before provenance and stolen-device screening pass, and be refused** | `BRU-TRF-02`(H) | **P0** |
| `UAT-R25-003` | **Try to list a refurbished unit without a completed QA protocol and an assigned grade, and be refused** | `BRU-TRF-03`(H) | **P0** |
| `UAT-R25-004` | Confirm battery health and known defects are disclosed on the listing, and that the grade matches the disclosure | `BRU-TRF-04`(H); `UA-19` | **P0** |
| `UAT-R25-005` | Make a trade-in offer up to `BDT 30,000`, and **be refused above it** | `05-04` §7; `UA-10` | P1 |
| `UAT-R25-006` | Override a grade with a recorded justification | `BRU-TRF-05`(A) | P1 |
| `UAT-R25-007` | **Try to value, purchase and then resell the same unit, and be refused** | `SOD-10` | P1 |
| `UAT-R25-008` | Confirm refurbishment yield and margin for the period | `KPI-077`, `KPI-078`; `UA-19` | P2 |

### 3.6 Block F — `R23` Marketing Manager · 6 scripts

**No SOP and no course pack** — see `O-05`.

| Script | The job | Rules and expected number | Pri |
|---|---|---|:--:|
| `UAT-R23-001` | Run a campaign and confirm attribution survives into reporting, with the referral-attributed figure matching source records | `KPI-035`; `UA-19` `SL-26` | **P0** |
| `UAT-R23-002` | Confirm loyalty tier benefits apply automatically and correctly at every tier | `MD-034`; `BRU-SRM-10`(C); `G2-10` | P1 |
| `UAT-R23-003` | Confirm a referral credits both parties once and accrues partner commission | `AUT-030` | P1 |
| `UAT-R23-004` | Confirm consent and preference settings are respected on every campaign send | `NFR-090`, `NFR-092`, `NFR-093` | P1 |
| `UAT-R23-005` | Confirm you can see all customer segments but not individual `nid_number` or `bank_account` | `05-04` §1.4, §5 | P1 |
| `UAT-R23-006` | Publish a partner benefit schedule to `P12` and confirm what the partner sees | `UA-21` | P2 |

**Pack total: 60 scripts · 27 at `P0` · 25 at `P1` · 8 at `P2`.**

### 3.7 Negative and edge cases

| # | Condition | Expected system behaviour |
|---|---|---|
| N-01 | Rate card version changes between quotation and order | Quoted price honoured; the version applied is recorded (`UA-20`) |
| N-02 | Contract amended mid-term with entitlements already partly consumed | Consumption carried, not reset; the amendment is versioned |
| N-03 | Claim submitted, then the underlying job reopened as rework | Claim flagged, not silently invalid (`BRU-SRM-19`) |
| N-04 | Two claims for the same serial, different faults, inside 90 days | Both permitted — `BRU-WTY-03` blocks same serial **and** same fault |
| N-05 | Seller suspended while holding an open job | Job completes under supervision; new work blocked; customer not stranded |
| N-06 | Commission scheme changed after accrual but before payout | Accrued at the scheme in force at accrual (`CG-006` §5) |
| N-07 | Refund issued after commission paid out | Commission recovered against the next run, with the seller informed (`BRU-BIL-04`) |
| N-08 | `R22` attempts to see `margin` on an account not assigned to them | Refused by record rule and by field rule together (`05-04` §5) |
| N-09 | Loyalty points redeemed against an invoice later cancelled | Points restored exactly; no rounding gain (`SL-21`) |

### 3.8 Bilingual check

**English-only pack (`CG-010` §3.2).** All six roles are head-office functions working in English.
It nevertheless asserts bilingual output at three points, because the counterparty or customer reads
the result:

| Element | EN | BN | Truncation |
|---|:--:|:--:|:--:|
| Contract and AMC document as the customer receives it (`DT-030`, `MD-032`, `BN-015`) | ● | ● | ● |
| Warranty terms and exclusions shown to a customer at point of sale (`MD-031`) | ● | ● | ● |
| Loyalty tier and benefit names (`MD-034`, `VB-010`) | ● | ● | ● |

> **Why the pack itself is not bilingual.** `CG-010` §3.3 sets the test: bilingual if someone
> outside the English-working core reads it to do their job. These 26–65 people are inside it. The
> *artefacts they configure* are read by Bengali speakers, which is why the three assertions above
> are in the pack rather than deferred.

---

## 4. Exit Criteria

`TS-006` §4 applies. Additional:

| Criterion | Threshold |
|---|---|
| `P0` scripts passed | **100%** |
| `P1` scripts passed | ≥ 98% |
| Scripts stating an independently computed expected number | **100%** (`UA-19`) |
| Scripts naming their `MD` master row | 100% (`UA-20`) |
| Counterparty-format verifications | 100% of third-party output (`UA-21`) |
| Claim scripts `UAT-R28-001`…`008` | **100%, no tolerance** — `G4-01`, `G4-02`, and `KPI-038` is a revenue-leakage target |
| Marketplace payout accuracy | **100% with zero unexplained variance** — `G7-02` |
| SoD refusals (`SOD-06`, `SOD-10`, `SOD-11`) | 3 of 3 blocked |
| Roles with a signature | 6 of 6 (`UA-17`) |
| Open Critical defects | Zero |

---

## 5. Defects Raised

| Defect ID | Script | Severity (`TS-018`) | Status |
|---|---|---|---|
| *(populated at execution)* | | | |

**Automatic escalation:** any defect where a **configured commercial number is wrong** — rate,
commission, entitlement count, tier benefit, claim value — is **High minimum**, to the CCO and CFO,
even where the workflow is correct. `TS-018` §4 records the reason: a wrong number produces
correct-looking transactions at scale and the loss is discovered in a reconciliation months later.

---

## 6. Sign-off

| Role | Super-user name | Release | Pack version | Date | Signature |
|---|---|---|---|---|---|
| `R28` Warranty Claims Officer | | | | | |
| `R22` Account Manager | | | | | |
| `R24` Marketplace Operations Officer | | | | | |
| `R21` Sales Manager | | | | | |
| `R25` Retail / Refurbishment Officer | | | | | |
| `R23` Marketing Manager | | | | | |
| **Pack acceptance** — CCO delegate | | | | | |
| **Counter-signature** — Finance Manager (claim and commission values) | | | | | |

---

## Open Items

| # | Item | Owner | Needed by |
|---|---|---|---|
| **O-01** | **The marketplace block is W7 and the pack is registered at W2.** `UAT-R24-*` evidences `G7-01`…`G7-06` at Month 30; the rest of the pack evidences `G4` at Month 18. **One pack spanning five waves cannot be signed once**, and `UA-16` requires a signature per role per release. Either the block is split out or the register records a staged sign-off | Programme Content Lead with QA Lead | **W2 — register decision** |
| **O-02** | **`UA-21` cannot be discharged for warranty claims without the brands.** 17+ partners submit in different formats; `TS-003` `O-03` records that a stub tests our assumption of the format, not the format. `G4-02` requires a first-submission approval rate of 90% and that is a claim about the *brands'* systems | Warranty Claims Officer with Commercial | **W4 — before `G4`** |
| **O-03** | **`MD-030` discount, promotion and voucher rules are the only source for commission and voucher arithmetic in this pack, and `UA-19` requires an independent computation.** Independent of what? There is no second source; the executor is confirming that the configured number matches the configured number | CCO with Finance Manager | **W2 — the agreed commercial schedule must exist outside the system** |
| **O-04** | **No pack verifies that a brand rate card matches the signed brand agreement.** `MD-017` registers brand partners and `MD-029` holds the rates; the *agreement* is a `LG` document and Category 10 is 2 of 24 written. `UAT-R28-005` verifies the arithmetic against `MD-029`, which is the same assumption twice | Legal Counsel with Commercial | **W4** |
| **O-05** | **Three of six roles have no course pack and one has no SOP** — `R28` (4–10 people handling the whole claim pipeline), `R25`, `R23`. `UA-03` requires training before execution and `UA-15` requires an `SP` for diagnosis. `TS-006` `O-05`/`O-07` record the same gap for service operations; **it is now visible in two packs and is a Category 06/08 register gap, not a Category 13 one** | L&D Lead with Business Process Analysts | **W2** |
| **O-06** | **`DT-031` SLA schedule and `LG-015` are named by `AUDIT_Checklist_Recurring.md` check `F3` as carrying financial liability and requiring identical SLA definitions across `MD-028`, `DT-031` and `LG-015`.** `UAT-R22-010` verifies a service credit computed from a measured breach; **`LG-015` does not exist**, so the credit is computed against an SLA definition with no contractual counterpart | Legal Counsel with Account Management | **W4** |

---

## Definition of Done

- [x] Front matter complete, including `purpose:` and `traces_to:`
- [x] Conforms to `TPL_Test_Script.md` at pack level; interpretation declared
- [x] **Method taken by reference from `TS-006` §2.1 and §3.2 rather than restated (`CP-01`)**
- [x] Four additional rules stated, all addressing the arithmetic nature of commercial defects
- [x] **The tester-can-verify versus role-must-verify distinction stated as the pack's central discipline**
- [x] 60 scripts enumerated across 6 roles with rules, expected-number obligation and priority
- [x] Role coverage reconciles to `05-04` §1.4 and §1.5 headcounts; missing SOPs and course packs named
- [x] Counterparty-format verification required for every third-party-facing output
- [x] Nine commercial edge cases stated, including version-change and post-payout-refund paths
- [x] English-only status justified against `CG-010` §3.3 rather than assumed, with three bilingual assertions retained
- [x] Automatic High escalation for wrong configured numbers, with the reason recorded
- [x] All internal links resolve
- [x] Six open items recorded, including the circular-verification problem in `O-03`
- [x] Registered in the Content Master Index (rule `CM-R1`)
- [ ] **The 60 per-step grids with their computed expected numbers — outstanding**
- [ ] **`O-01` five-wave span with one sign-off — outstanding; register decision**
- [ ] **`O-02` brand claim formats unverified — outstanding; blocking `G4-02`**
- [ ] **`O-03`/`O-04` commercial schedule and brand agreements outside the system — outstanding**
- [ ] Named approvers recorded — **pending QA Lead and CCO delegate**
- [ ] Bengali counterpart — n/a; English-only per `CG-010` §3.2

---

*1000FiX Services Limited · ERP Programme · CONFIDENTIAL — Internal Use Only*
