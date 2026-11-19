# A02 ERP audit — findings ledger (19 Nov 2026)

Branch `fix/a02-erp-audit` (worktree `1000 fix/a02erp-wt`), base e6d7a9b1.
Test DB `fix_test_a02erp` = copy of fix_real (real 376-account chart, 73 branches, 58 OUs).

Status: OPEN / FIXED (test) / VERIFIED-LIVE / OWNER (business decision) / NOT-A-DEFECT.

## Runtime evidence already taken
- 3,152 screen field references (cols, forms, grids, domains) of M01-M06/M31 resolve on the ORM: 0 dropped columns.
- Order-to-cash probe on the fix_real copy (BDT 1,000 + 15% VAT counter job):
  - **X1** invoice posting CRASHED: `Branch ... does not belong to operating unit Main Operating Unit` (57/73 branches) -> fixed in cd_gl_ext `_attach_dimensions` (branch OU fallback). After fix: Dr AR 1,150 / Cr 400100 1,000 / Cr 200902 150.
  - **X2** counter cash BDT 1,150 in the drawer, 0 AR receipts, 0 GL lines; invoice residual 1,150 for a customer who paid.

## Money to ledger (owner: lead)
| id | sev | finding | status |
|---|---|---|---|
| X1 | P0 | AR postings with a branch fail on every branch outside the company's first OU | FIXED |
| X2 / M04-F1 | P0 | M01 counter settlement: drawer only, no receipt/GL; invoice never paid | in progress |
| M04-F1b | P0 | walk-in diagnostic fee cash: drawer only, no GL | in progress |
| M04-F1c / M02-F2,F13,F20 | P0 | M02 field cash: no GL; hand-over into ANY branch's newest shift; recon loses carried cash; no source ref | in progress |
| M04-F8 | P2 | counter settlement always booked as drawer cash (bKash/card too) | in progress |
| X3 | P2 | invoice numbering INV/2026/ shared by fix.ar.invoice and the account journal; fix.ar.invoice sequence already at 5 with 0 invoices on fix_real | OPEN |
| M06-F1 | P0 | M06 data recovery never billed; hand-over has no payment gate | OPEN |

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
