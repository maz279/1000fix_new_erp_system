# A02 ERP audit — findings ledger (19 Nov 2026)

Branch `fix/a02-erp-audit` (worktree `1000 fix/a02erp-wt`), base e6d7a9b1.
Test DB `fix_test_a02erp` = copy of fix_real (real 376-account chart, 73 branches, 58 OUs).

Status: OPEN / FIXED (test) / VERIFIED-LIVE / OWNER (business decision) / NOT-A-DEFECT.

## Runtime evidence already taken
- 3,152 screen field references (cols, forms, grids, domains) of M01-M06/M31 resolve on the ORM: 0 dropped columns.
- Order-to-cash probe on the fix_real copy (BDT 1,000 + 15% VAT counter job):
  - **X1** invoice posting CRASHED: `Branch ... does not belong to operating unit Main Operating Unit` (57/73 branches) -> fixed in cd_gl_ext `_attach_dimensions` (branch OU fallback). After fix: Dr AR 1,150 / Cr 400100 1,000 / Cr 200902 150.
  - **X2** counter cash BDT 1,150 in the drawer, 0 AR receipts, 0 GL lines; invoice residual 1,150 for a customer who paid.

## Money to ledger (owner: lead) — commit 9f232e3d + follow-ups
| id | sev | finding | status |
|---|---|---|---|
| X1 | P0 | AR postings with a branch fail on every branch outside the company's first OU (57/73 on fix_real) | FIXED cd_gl_ext `_attach_dimensions` (branch OU fallback); test + probe |
| X2 / M04-F1 / M01-F1 / X-01 / X-02 | P0 | counter settlement: drawer only, no receipt/GL; invoice never paid | FIXED: verified settlement raises a confirmed M20 receipt (Dr drawer / channel, Cr customer AR); invoice applies it. Probe on fix_real copy: cash Dr 100108, bKash Dr 100111, AR 0 after invoice |
| M04-F1b / M04-F7 | P0 | walk-in diagnostic fee: drawer only, no GL; charged again in the repair | FIXED: fee = advance receipt on the order; amount due nets advances |
| M04-F1c / M02 field cash | P0 | field cash: no GL | FIXED (receipt raised when a cashier verifies/accepts); two-step hand-over = B3 |
| M04-F8 / X-01b | P2 | counter settlement always booked as drawer cash (bKash/card too) | FIXED: settlement_tender; only cash enters the drawer |
| X-03 | P0 | tax invoice only at Close (nothing forces it) | FIXED: invoice raised at delivery (close drain stays as safety net) |
| X-05 / M01-F10 | P1 | over-settlement uncapped; unverified claims refunded on cancel | FIXED: amount due cap; unverified claim voided on cancel; paid order cancel = supervisor |
| X-07 / M01-F5 | P1 | price rise after payment deadlocks delivery | FIXED: top-up (counter / M20 receipt), drawer + receipt take the difference |
| X-08 / M01-F6 | P1 | credit_approved unreachable (B2B credit) | FIXED: action_release_on_credit (Finance Manager, M33 limit/hold, SoD) |
| X-06 | P1 | refund debits AR for money AR never held; refund tender | FIXED by receipts (AR now holds the money) + refund goes back by the receipt's tender |
| X-10 | P1 | OEM remittance never booked on AR | FIXED: bank receipt on the brand applied to the OEM invoice; invoice must be issued first |
| X-18 | P3 | counter sales on MISC journal (C11 says Sales journal) | FIXED |
| M04-F15 | P2 | counter account fallback to generic codes | NOT-A-DEFECT: a code not in the chart fails closed (resolve_account) |
| X-11 | P1 | damage_claim_expense = 645000, not in fix_real chart -> payouts clear to 100102 Bank Suspense | OWNER: name the expense account (candidates 201326 A/P provision for Damage Goods / a new "Transit damage claims" expense) |
| X3 | P3 | fix.ar.invoice numbers INV/2026/ and the GL move numbers INV/2026/ are two series; fix_real's invoice sequence is at 5 with 0 invoices (1-4 burnt by rehearsals) | OWNER: reset number_next to 1 before go-live (statutory gapless series) |
| M06-F1 / X-09 | P0 | M06 data recovery never billed | B1 |

## M02 field service
F3 P1 technician rewrites geofence/zone/order on an open field order; F4 P1 reassign keeps old van; F10 P2 reassign bypasses decision log; F11 P2 route sequence discarded, depot hard-coded; F14 P2 van variance reads bench parts, on-site recon ignores order collection; F18 P3 scheduled_start = SLA deadline; F21 P3 KPI limits.

## M04 front desk
F5 P2 cash-handler set narrow, shift branch/operator/date editable while open; F6 P2 discounted basket can never confirm; F7 P2 diagnostic fee default waived, paid fee charged again; F9 P2 operator-scope shift picks newest drawer; F12 P2 token priority/recall/no daily reset; F15 P2 counter account fallback to generic codes; F16 P2 BRU-FRD-03 variance approval before close, BRU-FRD-10 terms; F17 P3 KPIs; F19 P3 receipt VAT vs M51 rate.

## M03 logistics / COD / claims
F1 P1 hub seal bypass via typed hub_scan; F2 P1 dispatch evidence editable after confirm; F3 P1 device on two live legs; F4 P1 return closes without arrival; F5 P2 rider swap mid-transit; F6 P2 courier booking return/cancel unreachable; F7 P3 POD any attachment; F8 P0 rider COD shortage never cleared; F9 P2 rider settlement ignores pending COD receipt; F10 P0 no aggregate claim cap; F11 P2 settle with liability pending / courier payee+debtor.

## M31 workshop
F12 P1 job cost counts unfitted parts; F13 P1 unit_cost unguarded vs M15 cost; F14 P1 typed labour defeats cost gate, consumables excluded; F15 P1 QC passes with failed tests, results editable; F16 P2 test instruments not calibration-checked; F17 P2 transfer not tied to consignment; F18 P2 bench double-booked via qc_failed; F19 P3 burn_in->qc_failed edge errors; F20 P2 on-time ~0%, burn-in report, FPY; F21 P2 cross-company reports.

## M05 MSP
F2 P0 onboarding on a running contract zeroes SLA measurement; F3 P0 SLA terms unguarded, credits recompute after approval; F4 P1 device uplift never billed; F8 P1 open alerts at report time never judged; F14 P2 credit can point at another contract's report; F15 P2 periods in UTC; F18 P2 patch defer/fail no role/evidence; F19 P2 rollback plan only for high risk; F21 P3 KPI.

## M06 data services
F1 P0 never billed (above); F5 P1 re-quote approval bypass via fresh quote; F6 P1 BRU-DTS-10 bypass with request-less certificate; F7 P1 linked certificate serial changeable; F9 P1 purged case closes with media in lab, destroyed unreachable; F10 P2 media return any stage, no recipient check; F11 P2 witness not authenticated; F12 P2 hash verification copies visible hash; F13 P2 undertaking accepts any attachment; F16/F17/F20 KPI; F22 P3 mark_failed no role.

## Stream outcomes (20 Nov 2026)
| Stream | Findings | Result | New tests | Mutants red |
|---|---|---|---|---|
| Lead (money to ledger, X-*) | 16 | 13 FIXED, 1 NOT-A-DEFECT (M04-F15), 2 OWNER (X-11, X3) | 13 | 10/10 |
| B5 M01 | 20 | all FIXED (F13 cancel half NOT-A-DEFECT; OWNER notes F8/F14/F19/F21) | 23 | 22/23 |
| B3 M02 | 10 | all FIXED (OWNER: geofences, depots) | 15 | 18/18 |
| B2 M03 + M31 | 21 | all FIXED (OWNER: own-fleet SLA, payroll account, labour rates) | 41 | 32/32 |
| B4 M04 + X-04/13/14/15/17 | 12 | all FIXED (F6 completed by lead; OWNER: terms products) | 40 | 24/24 |
| B1 M05 + M06 | 22 | all FIXED (OWNER: M39 uplift billing, M06 pricing, credit role) | 40 | 35/37 |

Integration by the lead: field-cash verify by drawer cashier (M02 contract), basket price approvals
(M04-F6), variance-before-close test helper, call-next exposed, print buttons (M02/M03/M31/M06),
M36 estimate version read-only, whitelist regenerated, 3 events registered, storefront refuses a
returning leg, M50 payroll recovery prompt, settlement hand-back tests on the new rules.
Owner decisions: see `A02_ERP_AUDIT_REPORT_2026-11-20.md` (O1-O15).
