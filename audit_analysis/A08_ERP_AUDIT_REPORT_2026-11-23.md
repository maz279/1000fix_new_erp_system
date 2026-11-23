# A08 ERP audit and fix — Finance & Treasury (21–23 Nov 2026)

Scope: M19 Financial Accounting & GL, M20 AR/Invoicing/Collections, M52 AP & Employee Expense,
M50 Treasury & Banking, M51 Tax & Regulatory (BD), M53 Revenue Recognition & Settlement,
M49 Fixed Assets & Capex, M54 Cost Accounting & FP&A — with their cross-relations into A02
service orders, A03 party master/credit, A04 contracts/warranty, A05 rental/trade-in, A06
procurement, A07 assets/fleet costs, A09 payroll, A10 GRC/QMS, A11 BI/ML and A12 platform
(events, approvals, SoD, P03 workspace).

Owner: 1000 FiX Services Ltd (after-sales service; BDT; VAT 15%; VDS/TDS; Asia/Dhaka).
Owner decisions: `A08_ERP_AUDIT_DECISIONS_2026-11-22.md` (D1–D13, recommendations attached).

## 1. How it was done
- **Live drive-through in the in-app browser** on production (`fix_real` @ 8069): all 8 module
  homes (KPIs), ~60 screens, the AR-invoice / vendor-bill / journal-entry forms, every
  reconciliation, with each number cross-checked screen ↔ screen ↔ SQL (AR ৳15,38,59,759.09 /
  AP −৳13,00,43,343.04 identical on the sub-ledger screen, the ageing, and raw
  account_move_line).
- **Six read-only deep auditors**, one per module group + finance SoD, each running executable
  probes on a copy of production (`fix_real_a08`, every probe rolled back): spec coverage
  (FR/BRU/AUT/entities/KPIs/reports/integrations), data capture vs the form whitelist, state
  machines, approvals & four-eyes, calculations with real numbers, GL postings on the real
  chart, cross-module contracts, security.
- **Findings totals (rows in the six FINDINGS.md): 135** — P0 3 · P1 20 · P2 61 · P3 51.
  2 auditor false positives were caught and corrected on lead re-verification; 1 claim
  (M50 KPI tiles) was disproved live.
- **Fixes** were built by module-scoped builders on dedicated test databases, verified by the
  lead (lint, targeted suites, integration runs), committed individually, and deployed to both
  databases. Every commit below is in `fix/a03-live-data-and-pending-work` and live.

## 2. Worst defects found — and fixed
Money & ledger
- **P0 — treasury evidence was deletable**: `fix.guarded.mixin` guarded create/write only, so one
  Accounting Administrator could unlink imported bank statement lines, executed payment
  instructions (with their releaser stamps), gateway report lines, cleared cheques and settled
  COD settlements (probe deleted all five) → T-14 immutable-audit breach. **Fixed** (`a14feffb`):
  unlink guards on all five families, superuser/transition-token only for service flows.
- **P0 — GRNI accrual never reached the GL** (`M52-F1`): the received-not-invoiced period-end
  liability computed and was second-person-confirmed but posted nothing. **Fixed** (`6f0d6a54`):
  escalation through `post_ap_move` with per-line expense accounts, a fail-closed accrual seat, an
  exact next-period mirror reversal, and a close-block seam wired into M19 (`5aa54ac2`).
- **P1 — credit limits ignored the migrated estate** (`M20-F1/F2`): exposure never recomputed and
  excluded the ৳15.39 Cr take-on receivables; IFRS-9 ECL provisioned ৳432.50 against a
  ৳153.86M book. **Fixed** (`71321c25`): event-driven exposure + take-on + commercial-partner
  children, live gate on both issue paths, ECL on the ageing snapshot's own basis.
- **P1 — the Mushak 9.1 could mis-declare** (`M51-F1/F2`): zero-rated/exempt lines were dropped
  from the treatment summary (so a ৳5,000 export was filed on the 15% line), and the filing gate
  trusted the preparation snapshot — a probe FILED a return with an unclassified row in the live
  register. **Fixed** (`9e5ce1a0`): 0% lines flagged, named treatments corroborated against the
  amounts, filing re-reads the live register.
- **P1 — treasury import integrity** (`M50-F2/F3/F4`): identical transactions were silently
  deduped, re-downloaded statements re-imported everything, MT940 balances were never validated,
  and a loan instalment moved bank money on one click. **Fixed** (`60e076a6`): every reported line
  imports with cross-import dedup, balance/sequence validation with a quarantine state, instalments
  marked → second-person confirmed against an imported bank debit.
- **P1/P2 — statutory issuance blocked by real data** (`M51-F12`): 0 of 1,624 partners carry a
  machine-clean 13-digit VAT; a BIN in NBR print format either dropped off the Mushak 6.3 or
  refused the whole issuance. **Fixed** (`3ec832c5`): normalised in both paths, document keeps the
  print form, register/event carry digits, replays normalised.
- **P2 — AP ageing dropped history** (`M52-F5`): a bill paid after the as-of vanished from that
  as-of (77,500 → 0.00). **Fixed** (`71c2f3ec`): point-in-time ageing reconstructed from payment
  runs, request settlements, LC remittances, reversals and notes, take-on included.

Controls & governance
- **P1 — close gate let drafts through** (`M19-F1`): a period with an unposted draft CLOSED and
  set its lock. **Fixed** (`5aa54ac2`): unposted drafts and pending manual drafts are blockers at
  ready and re-checked at close.
- **P1 — the lock stopped at the superuser** (`M19-F2`): with a hard lock, `post_with_dimensions`
  as su posted a back-dated entry (Odoo silently re-dates). **Fixed** (`5aa54ac2`): the funnel
  enforces the lock on every source, su included; the only door is an approved
  `fix.period.reopen` that posts as its named beneficiary, dated, with the trail naming them.
- **P2 — payroll/tax note GL legs missing** (`M51-F4`): Mushak 6.7/6.8 notes wrote register rows
  with no move, blocking the next filing. **Fixed** (`9d21a026`) inside the same second-person
  approval; the M20 credit-note path keeps its own documented reversal (no double VAT).
- **P2 — dead tax event feed** (`M51-F10`): 11 published events, zero consumers. **Fixed**
  (`9d21a026`): variance + overdue notices raise risk-register entries; filed returns discharge the
  period's compliance obligation with the NBR acknowledgement as evidence.
- **P2 — over-broad reads and missing SoD**: credit profiles readable by every internal user, and
  the customer-record creator could approve its own limit. **Fixed** (`3ec832c5`); employees can
  now read their own advances (`71c2f3ec`).

Data & configuration on production (fixed)
- Statutory chart register showed **0 accounts** while the books carried 433 → governed MD-035
  load: **79 statutory accounts live** (60 postable, 28 control).
- No fiscal year existed → **FY 2026-27 (July–June) seeded** through the constrained model.
- fix_test was **72 + 7 modules behind** → caught up twice; M52's Payables KPI read 0 while the
  books carried ৳13.00 Cr → now **৳ 13,00,43,343.04, tying to the control** (`4ad0c295`).

## 3. What the probes proved *works* (so it is not re-litigated)
Invoice → gapless `INV/2026/0000n` + Mushak 6.3 (supplier BIN on the document) → GL
Dr 100201 / Cr 400100 / Cr 200902 on the real chart with OU dims; VAT 15% inclusive/exclusive
exact; bKash receipt two-stage Dr 100111 / Cr 100201; allocation caps and cross-customer
refusals; credit-note ladder with pro-rata VAT and 6.7; VDS Dr 200903; dunning triggered by
state with disputed-only suspension; ageing immutability; ECL rate approval with second person;
write-off allowance-first. Vendor bill → 3-way match (tolerances qty +8%/+12%, price +4%/+6%)
→ approval matrix → GL Dr 100503/200901/600001, Cr 200905 TDS / 200904 VDS / 200101 AP → payment
Dr 200101 / Cr 100009, with one-live-payment DB lock, payee-bank dual control, duplicate refusals.
Payment instruction → DOFA routing to four real holders → M63 approve → different-manager release
→ CSV bank file → statement auto-match → executed with GL Dr 100102 / Cr 100001; cheque bounce
after clearing reverses exactly; gateway settlement splits fee + VAT through 100111; imprest
count variance is a formula, not a slip count; covenants compute real GL ratios. Revenue
schedule recognition 12,000 over Jun–Nov → 11,406.59 by days, Dr 200401 / Cr 400100; commission
TDS 10% ×1.5 non-filer = 150 with 7-day escrow; full payout e2e through M63/M50/statement.
Capex → CWIP → capitalisation 300,000 → monthly 8,333.33 with branch OU and register-vs-GL
variance 0.00. Budget variance favourable-positive, day-prorated, rolling forecast on the
documented basis; board-pack revenue equals the M53 recognition line. Trial balance balances to
the paisa (Nov: Dr = Cr = ৳353,918,376.91). SoD refusals hold across JE, invoices, credit notes,
write-offs, payments, notes, filings, bulk imports.

## 4. What is left — by owner decision (D1–D13)
- **D1 (P0, money in the books):** take-on move `MIG/2026/11/0001` credits ৳31,584,219 to bank GL
  100009 (Prime Bank) and ৳374,738 to equity; the bank control is mis-stated until a correcting
  entry is approved. Ready to prepare; needs the owner's word and the accountant's approval.
- **D2 (P0, config):** all six ITA Third-Schedule tax-depreciation rates sit
  `verify_with_adviser`, so the dual-book tax run refuses. Needs the adviser's confirmation.
- **D3** 45-service VDS schedule (only S074.00 loaded) · **D4** marketplace D-03 model + seller
  commission scheme · **D5** credit/ECL policy confirmation · **D6/D7** finance SoD appointments
  (exception approvers, second filing approver) · **D8** nil returns for the overdue 9.1 periods ·
  **D9** real-chart ↔ statutory mapping (21 accounts / ৳50.36 Cr unmapped; the two existing links
  are semantically wrong) · **D10** Phase-2 statements suite · **D11** fix_test test-contention
  isolation · **D12** P2 backlog sequencing · **D13** the five GL config seats (GRNI accrual, note
  counter, M53 settlement seats, TDS due-day 14th→7th, FX accounts).

## 5. Engineering backlog — status as of 2026-11-23
**Closed since the audit** (waves 5–6 and the P03 wiring): dunning reminder dispatch with delivery
evidence (M20-F5); consignment settlement (M52-F3, spec P0); retention money (M52-F4); branch/OU
P&L slice (M19-F4); subledger reconciliation as a hard close gate; posting-log hash chain with
tamper detection; VAT input-credit carry-forward (M51-F8 core — no negative net can strand
credit); P03 workspace surfaces for every new register (`f3bd13c3`).

**Still open — no owner decision needed:**
- M20: billable-event coverage beyond service orders, TDS/AIT settle seat, bilingual invoice
  content, multiple documents (PO / statement of account).
- M52: approved-bill cancellation path, near-duplicate detection at entry, invoice-line coding
  dimensions.
- M50: field-technician cash reconciliation (FR-TRE-017, spec P0 — in build), account-purpose
  segregation per treasury role, manual instruction debit seat.
- M19: year-end close console, purge of 163 stale demo FX rates, widening subledger
  reconciliation from 4 to 7 subledgers.
- M51: tax determination record, Mushak 6.5 register, income-tax pack, import-tax record,
  truncated-base computation (refund applications deliberately out of scope).
- M49/M54: M49 book-vs-tax feed to M51 (needs D2), M54 job costing coverage from A02 orders.
- Settlement GL seats (M53) are configuration — item D13.
**Owner-gated:** D1, D2, D3, D4, D6, D7, D8, D9, D10, D13 (see the decisions document).

## 6. Evidence index
- `1000_fix_codebase/scratch/a08_drive/REGISTER.md` — every defect, its status, the commit.
- `C:\Users\DELL\AppData\Local\Temp\a08erp\A1..A6\FINDINGS.md` — full auditor tables + probe logs.
- `A08_ERP_AUDITOR_BRIEF.md` — the method, the hard rules, the probe recipe.
- Commits: 4ad0c295 · 9e5ce1a0 · a14feffb · 5aa54ac2 · 6f0d6a54 · 71321c25 · 9d21a026 · 60e076a6 ·
  5e99f30f · 3ec832c5 · 71c2f3ec — each with the rule id and the verified suites in its message.
- Backups: `fix_real_pre_coaload_2026-11-22.dump`, `fix_real_pre_wave23_2026-11-22.dump`,
  `fix_test_pre_a08_2026-11-22.dump`.

## 7. Wave 5–6 (added 2026-11-23, merged to the mainline and deployed)
Merged `fix/a08-wave5` into the working branch (fast-forward after absorbing the mainline; the one
`cd_gl_ext/models/__init__.py` conflict resolved as a union of late-loading imports). Commits:
- `9fadcab1` **M20-F5** dunning reminders are SENT with immutable per-step evidence (M27 delivery
  queue, `purpose=collections`, `lawful_basis=contract`, recipient masked, `sent` never claimed as
  delivered without the provider callback; idempotent 2h retry capped at 3; disputes/promises/plans
  re-checked at send; call steps create the M27 follow-up row; `action_run_dunning` returns only
  transitioned runs so a daily re-scan cannot spam).
- `9006d2dd` **M52-F3** consignment settlement (spec P0 — gather M15 consumptions, agreement/price-list
  rate, VAT per the partner tax profile, AP-matrix approval, Dr expense / Cr 200101 with OU+branch+brand)
  and **M52-F4** retention money (exact % withheld at posting, retention register, release only by a
  different manager after certified completion, ageing at the net; seats fail closed).
- `380cdc6d` **M19-F4** branch/OU P&L engine slice (`pnl_by_branch`, ties exactly to the company P&L,
  unallocated bucket never dropped) + **subledger reconciliation as a hard close gate** (AR/AP/VAT
  out+in, fail-closed on missing config) + **posting-log hash chain** (`verify_chain` detects changed
  content, sequence gaps, predecessor mismatch and tail truncation; advisory+row locks; genesis at
  deployment, no rewrite of history).
- `7d192ef4` **M51 input-credit carry-forward** (opening/used/closing credit on the 9.1; `credit_used =
  min(opening, max(0, output−input))`; negative net now impossible; filing refuses when opening ≠
  previous closing, naming both; challan settles the post-credit net; refund application deliberately
  out of scope per FR-TAX-018's core).
Deploy: fix_real backed up (`fix_real_pre_wave56_2026-11-23.dump`), `-u` of the four modules clean
(0 non-RST errors), versions live (cd_gl_ext 19.0.2.8.0, cd_ap_ext 19.0.1.5.0, cd_billing_engine
19.0.2.10.0, cd_tax_engine_bd 19.0.1.4.0), all five new tables and the three credit columns created;
fix_dev upgraded to match. Test evidence: 7 new carry-forward tests, 6 consignment/retention,
6 M19 P&L/close/chain, 5 dunning — plus ~490 module regressions, all green; lead re-ran each new
suite directly (zero failures).
