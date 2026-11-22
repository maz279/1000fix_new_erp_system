# A08 ERP audit — owner decisions (D1–D12), 2026-11-22

Context: IAB visual drive-through (all 8 modules) + six read-only deep auditors with
executable probes on a copy of production (`fix_real_a08`). Evidence:
`1000_fix_codebase/scratch/a08_drive/REGISTER.md` + per-auditor FINDINGS.md in
`C:\Users\DELL\AppData\Local\Temp\a08erp\A1..A6\`. Totals: **P0 3 · P1 15 · P2 ~70 · P3 ~45**;
2 visual defects already fixed live (CoA statutory load; Payables KPI `4ad0c295`), 3 audit code
fixes implemented and under test (M51-F1/F2, M50-F1 P0 unlink guards).

Each decision carries a recommendation. Approve as recommended or state the alternative.

## Money in the books of record (P0/P1)

**D1 — Prime Bank control mis-stated by ৳31.58M (A1 M19-F3, P0).** Take-on move
`MIG/2026/11/0001` credits the migration contra ৳31,584,219 to bank GL 100009 (and ৳374,738 Dr
to equity 300101). The bank reconciliation for Prime Bank can never tie.
*Recommendation:* post one correcting journal entry (Dr 100009 ৳31,584,219 / Cr the migration
contra; reverse the ৳374,738 equity leg) dated 2026-11-30 with reference "MIG/0001 correction —
A08 audit D1", after a fresh backup; I prepare it, your accountant approves through M19's
maker-checker. *Alternative:* leave until the Prime Bank row-level take-on is loaded on fix_real
(currently provenance-only) and correct against the real statement.

**D2 — Activate the ITA Third Schedule tax-depreciation rates (A6 M49-F1, P0).** All 6 rates sit
`verify_with_adviser`, so the dual-book tax run refuses — FR-FXA-020 inoperative.
*Recommendation:* tax adviser confirms the 6 rates in M51 sign-off; then the tax book runs and
M49 feeds M51 the book-difference.

**D3 — Load the 45-service VDS schedule (A5 M51-F3, P1; cross-noted by A3).** Only S074.00
(rent) exists; SRO 182-Ain/2025 services (incl. S031.00 repair — your own sub-contracted repair
bills) cannot be determined.
*Recommendation:* I load the schedule through the propose→adviser→CFO master flow as
effective-dated rows; adviser signs off in the 34-row queue.

**D4 — Marketplace commission model + seller scheme (A6 M53-F1, P1).** `fix.marketplace.tax_model`
empty (D-03 undeclared) and no commission scheme → every W7 settlement dead-letters.
*Recommendation:* declare the D-03 model (agency, commission as principal revenue) and seed one
starter seller commission scheme; defers live marketplace settlement otherwise.

**D5 — Credit-limit and ECL coverage of the legacy take-on estate (A2 M20-F1/F2, P1).**
Exposure never recomputes on invoice events and ignores the ৳15.39 Cr migrated receivables;
IFRS 9 ECL omits take-on open items entirely (probe: provisioned ৳432.50 against ৳153.86M).
*Recommendation:* builder fix — exposure recompute wired to invoice/receipt events including
take-on open items; ECL basis = the same ageing snapshot incl. take-on (conservative: assign
the migration vintage to the 90+ band until real payment behaviour emerges).

## Controls & organization (P1)

**D6 — Finance duty separation (A6 SOD-F1/F2).** Four people hold the accounting-manager group
(create+approve+pay capability in the same hands; two of them also release payroll and approve
procurement); the SoD exception workflow has **zero** approvers registered. Code-level
maker≠checker is real and refused every probe.
*Recommendation:* (a) appoint at least 2 SoD exception approvers who are NOT in the 4-manager
set; (b) split release duty (payments) from approval duty among named people; (c) I add a
dashboard warning when any finance SoD group has <2 active holders. People names needed from you.

**D7 — Filing approver bench (A5 M51-F5).** Exactly one CFO-group holder (ashish.kumar) is also
the only filer and master activator. *Recommendation:* appoint a second filing approver; then
enable `enforce_rate_signoff`.

**D8 — Statutory filings (D-Q1, repeated with more evidence).** Mushak 9.1 for 2026-06/07/08
(and Jul–Oct per A1/A5 measurements) + 2025-Q4 withholding overdue, all "no return prepared".
*Recommendation:* I prepare the nil 9.1s + Q4 withholding nil return in M51 for adviser review
(VAT activity was zero; balances are legacy take-on).

## Chart & statements

**D9 — Statutory↔real chart mapping (D-Q3 + A1's new evidence).** Only 2 links exist and they
are semantically WRONG (statutory "Operating bank account" ↔ POS bKash 101401); 21 accounts /
৳50.36 Cr unmapped; 1,733/1,837 MIG lines carry no branch/OU dimension.
*Recommendation:* I draft the full mapping (bank GLs→bank family, 100201→Trade Debtors,
200101→Trade Creditors, POS/MFS→their floats, 2.99.99.901/902→controls), extend
ODOO_CHART_MAPPING + tests, re-run link+reconcile, and show you the accounting-equation result
before anything posts.

**D10 — Sectioned, branded statements (D-Q2).** *Recommendation unchanged:* fold into the
Phase-2 document suite rather than patching now.

## Builder-phase code fixes (no decision needed — listed for transparency)

Already implemented, under test: M51-F1 zero-rated 9.1 misclassification; M51-F2 filing gate
live re-read; M50-F1 P0 treasury-evidence unlink guards. Queued next: M19-F1 close-gate
hardening + M19-F2 su lock bypass; M19-F4 branch/OU P&L slice; M20-F1/F2 (D5); M52-F1 GRNI GL
posting; M50-F2 statement dedup/re-import; M50-F3 MT940 balance validation; M50-F4 loan-pay
four-eyes; M51 6.7/6.8 note GL leg; M51 events→M23/M60 consumers.

**D11 — fix_test event-outbox test contention (environment).** Concurrent odoo test sessions
deadlock on the conftest seed-backlog UPDATE. *Recommendation:* serialise heavy suites on
dedicated DB copies (proven this session) and fix the relay UPDATE's isolation in a platform PR.

**D12 — Register the P2 backlog.** ~70 P2s (year-end close, subledger close gate coverage,
audit-trail hash chain, FX demo rates purge, retention, statement pack gaps…) are enumerated in
the FINDINGS files. *Recommendation:* I sequence them into the next builder waves by money risk.

## D13 — GL config pack for the new controls (added 2026-11-22, one decision, five parameters)
The wave-2/3 controls are fail-closed until these seats are pointed at real-chart accounts
(all additive `ir.config_parameter` rows — I apply them on your yes, no code change):
1. `cd_ap_ext.account_code.grni_accrual` — GRNI accrual liability (recommend a dedicated
   2-xxxxx accrual account your accountant names; NOT 100503/211000 which it reconciles against).
2. `cd_tax_engine_bd.note_counter_account_code` — counter seat of a Mushak 6.7/6.8 note's VAT
   leg (recommend the AR control 100201 — a credit note reduces AR).
3. M53 settlement seats (A6 M53-F9/F10): `partner_payable` currently 32656556 "BP Payable"
   (wrong) and `seller_payable` 200102 — recommend payable-side accounts your accountant names.
4. TDS deposit due-day master: seeded 14th, ITA says the 7th — I correct the seed file and the
   live row through the adviser→CFO master flow on your yes (D3's sign-off queue covers it).
5. FX conversion seats (A4): no exchange gain/loss accounts and no FX journal exist — needed
   before the first multi-currency conversion; recommend your accountant names the two accounts.

## Appendix — builder-phase fixes landed (no decision needed; for the record)
11 commits on `fix/a03-live-data-and-pending-work`, all deployed to fix_real and fix_dev:
`4ad0c295` M52 payables KPI · `9e5ce1a0` M51 zero-rated 9.1 + filing gate · `a14feffb` **P0** treasury
evidence unlink guards · `5aa54ac2` M19 close gate + superuser lock + GRNI seam · `6f0d6a54` M52 GRNI
GL + reversal · `71321c25` M20 credit limits + ECL over the take-on · `9d21a026` M51 note VAT legs +
4 event consumers · `60e076a6` M50 import dedup/MT940 quarantine/instalment evidence · `5e99f30f`
M50 P03 surfaces · `3ec832c5` M51 buyer-BIN normalization + M20 credit-profile ACL + SOD-08 ·
`71c2f3ec` M52 point-in-time ageing + employee own-advance read rule.
