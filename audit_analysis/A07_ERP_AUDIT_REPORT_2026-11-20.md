# A07 ERP audit and fix — Assets, Equipment & Facilities (20–21 Nov 2026)

Scope: M17 Device & Customer Asset Registry, M45 Enterprise Asset & Test Equipment, M46 Fleet & Vehicle,
M47 Facility, Branch Infrastructure & Workplace, M48 IoT Telemetry & Predictive Maintenance, and the two A07
bridges (`cd_asset_workorder_spine`, `cd_asset_finance_hse_bridge`) with their links into M01/M02/M31 service,
M15 parts, M09 warranty, M19 GL, M49 fixed assets, M52 AP, M54 budget, M56 payroll, M59 HSE, M60 risk, M26 ML.

Owner decisions: `A07_ERP_AUDIT_DECISIONS_2026-11-20.md` (D1–D21, all approved as recommended).

## 1. How it was done
- Six read-only auditors (one per module + finance/cross-area) checked every spec rule, flow, approval,
  calculation, posting, form, report and cross-module link, with executable probes on a copy of production
  (`fix_real_a05`, rolled back). 176 findings: **P0 18 · P1 ~60 · P2 ~70 · P3 ~25**.
- Six builder streams fixed them in a shared worktree (`fix/a07-erp-audit`), each with its own test DB, strict
  file ownership, executable ORM tests and a mutation check; two finishing streams closed the cross-stream
  seams (money glue, printable documents, test glue).
- Lead integration: regenerated `writable.py`, static checks (ruff, import order, duplicate xml ids, cron
  records, consumer methods, guarded-vs-writable), full regression on an integration DB.

## 2. Worst defects found (all fixed)
Money / ledger
- No A07 asset could be capitalised, depreciated, disposed or leased: all 7 fixed-asset categories on fix_real
  had no journal or accounts, and the chart had no lease-liability, CWIP, gain or impairment account (FIN-25).
- Depreciation and IFRS 16 entries posted to the company's FIRST operating unit, not the asset's branch (FIN-01/02).
- Rent on an IFRS 16 lease was expensed twice (bill + lease schedule) and a modified lease rebuilt a rent month
  already sent to AP, so it was paid twice (FIN-03, M47-01/03).
- No fleet money reached the GL; service cost entries dropped the garage so AP could match any vendor's bill;
  cash fuel had no settlement path; vehicle cost had no branch (M46-01..04).
- Every facility cost went to 500200 Expense Clearing; lost-equipment losses were read as count events and dropped
  (M47-37, FIN-04); staff recharges, fines and insurance settlements were published to nobody (FIN-10/11).
Controls
- Anyone could re-point an open custody issue (exit clearance then passed), lower a write-off tier by editing the
  cost, certify an instrument with no certificate, or lift the calibration rule on a class (M45-01..04).
- Leases were recorded and terminated with no approval (M47-04); the IoT consent gate could be bypassed by clearing
  the device's customer (M48-01); a preventive WO skipped its approval (M48-03).
- The stolen flag was not checked at intake; a lost duplicate could launder its flag by merge; scrapped devices
  stayed "under warranty"; trade-in/e-waste/write-off never updated the device (M17-01..10).
Estate-wide
- All 264 crons run as `__system__` (Europe/Brussels): every cron's "today" was the previous Dhaka day from
  00:00 to 05:00 Dhaka (fixed in code for A07 + D4 time zone change on both DBs).

## 3. What was built (by module)
- **M17**: intake hold on lost/stolen/disputed devices; transfer release evidence; merge refuses flagged devices;
  device lifecycle follows trade-in, resale (warranty activated), e-waste certificate and M31 BER; provisional-device
  invoice gate; population changes approved by R05; warranty events published; purchase-date correction with proof;
  stewardship SoD; identifier quarantine; custody/dormancy projection; repeat-fault on the D13 30-day window;
  D12 warranty-on-resale + stolen needs GD ref + disputed flag; entitlement resolution; part genealogy from M15
  consumption (fix.stock.lot).
- **M45**: custody and cost guarded; D7(a) certificate + provider + hash on every pass, B9 role switches proven;
  class control-off is an M63 approval; standard traceability; Dhaka crons; branch OU computed; exit clearance
  covers register custodians; recall/lapse escalation; D7(c) QC gate scoped to measuring protocols + QM waiver;
  issue/return roles, blind count with review; compliance %/availability/MTBF/MTTR KPIs; certificate register,
  asset tags, hand-over slips, write-off memos; calibration cost to AP; out-of-tolerance → open warranty claims;
  M06 wipe before disposal of data-bearing items; D10 write-off basis = NBV.
- **M46**: dispatch gate on safety-critical defects; pre-use check enforced at accept/travel/work; off-road after
  dispatch stops the van; odometer reconciled across all sources; CFO-approved disposal with proceeds; fine DOFA
  (D11) and paid only through AP/petty cash; accident pins insurer/excess; class profile + fuel deterioration flag;
  HR↔fleet licence sync; logbook / gate pass / fine notice; commissioning lifecycle; Dhaka dates; cost facts
  (vendor, ref, payment method, branch OU) on every cost source.
- **M47**: rent rows never rebuilt once sent; D6 lease DOFA on total commitment + terminations approved; rent due
  cron; deposit/advance ledger with approved settlement; licence fees/penalties, fit-out cost lines, utility payee,
  mandatory cost centre; routed alerts and escalations; WO SLA clocks (D15); outage → affected M01/M02 orders;
  operating-hours loss; lease payment frequency/service charge/advance; facility job sheet, site hand-over,
  lease summary, licence and utility registers, outage report; IFRS 16 remeasurement screen.
- **M48**: consent binding lock; M26 accuracy-gated predictions; approved preventive WOs (date pinned, D17c);
  entitlement + proactive-service consent before customer work; M17 device / M46 vehicle / M05 endpoint binding;
  M46 + M05 telemetry adapters under the consent gate; M22 skill check; outcome after demand; "prevented" outcome;
  escalation/horizon/precision crons (D21); late readings re-aggregated; retention by criticality (D17b);
  timezone-safe file batches; health index; owner-module alert routing.
- **Money (bridges + M49)**: D1–D3/D19 account map and seed; cost-entry contract (payment method, D3 accounts,
  pinned vendor/ref/branch, direct posting for petty cash/employee/fuel card, internal jobs not to AP); IFRS 16
  per D5 (rent clearing, escalated + frequency-aware measurement, remeasurement and termination accounting, leased
  vehicles, exemptions, monthly cron); depreciation/IFRS 16/capitalisation on the branch OU; duplicate-capitalisation
  guard; disposal with proceeds (D10); recharge/fine recovery receivable (D9/D20); insurer receivable; D16 budget
  hold; fit-out → CWIP → capitalised; branch transfer moves GL balances; deposit/advance/break-penalty postings.
- **Platform**: events stamped with the record's own company (FIN-24).

## 4. Evidence
- New tests: M17 31, M45 27, M46 32, M47 32 + 9 documents, M48 34, money 21 + 15; every P0/P1 fix mutation-checked
  (S1 14, S2 15, S3 13, S4 18, S5 6, S6 19, R2a 11, R2b 7 mutants — all red).
- Integration (all streams together, DB `fix_test_a07` = clean template + `-u` of the 11 touched modules, exit 0,
  no ERROR in the log):
  - Shard A, the 9 A07 addons: 1,150 passed, 0 failed.
  - Shard B, neighbours (cd_fixed_asset_ext, cd_event_outbox, cd_workshop, cd_field_service, cd_service_order,
    cd_ap_ext, cd_billing_engine): 1,315 passed, 0 failed.
  - Shard C, all of cd_p03_portal: 6,299 passed, 0 failed, 375 skipped.
  - The first run showed 8 failures/errors, all stale expectations of owner-approved behaviour changes (vehicle form
    tab badge, the new hand-off screen, swap unit must be refurbishment stock, D7(c) measuring protocol, two new M47
    forms needing a `pick` instruction, M49 fixtures without a branch); each was fixed in the code or the test fixture
    and re-run green. No assertion was weakened.
- Wiring check on the integrated registry: 232 active consumers, 275 active crons, 108 A07 surfaces — every consumer
  and cron method exists, no guarded field is writable. Static: ruff + format clean, no duplicate xml ids, no new
  model-import-order problem.
- Not covered: a live browser walk on fix_real (done after deploy), real business data (fix_real holds no A07
  records yet).

## 5. Left for people / other areas (not code defects in A07)
- Business data on fix_real: 0 equipment, vehicles, drivers, sites, leases, IoT devices. Every A07 flow is ready
  but empty until the estate is loaded. Vehicles need a branch with an OU.
- Role holders (D8): Calibration Technician, Equipment Custodian, Fleet Officer/Driver, Population Approver (R05),
  DOFA tier 3/4/5 holders, `hr.group_hr_manager` for recharges. Today one group of 10 people holds every M45 role.
- HR: statutory wage-deduction cap before payroll recovery switches on (D20).
- M26: no prediction drives work until a reviewer records a passed accuracy gate on a deployed PdM model version.
- Peer areas (sent): A05 cd_rental_asset population check, cd_tradein `tradein.rejected` + resale-warranty proof,
  cd_ewaste/cd_tradein consume `device.end_of_life`; A02 intake warning on lost/disputed + loaner population check,
  P03 workshop surface for the QC waiver, vehicle_id on fix.consignment; A06 vehicle_id on fix.stock.location +
  `vehicle.off_road` stock recovery, M15 reservation from IoT parts; M56 payroll recovery API; M23 consume
  `device.identifier_conflict`; portal recipient acceptance and customer telemetry self-access.
- A04 (found here): live cron `fix.ar.aging.snapshot._cron_monthly_snapshot` pointed at a deleted method; fixed on
  the A04 branch.
- Deferred by D18: fleet trips/behaviour score/tyre & battery/pool, fuzzy identity matching, duplicate sweep,
  estate reconciliation, statistical IoT rules and correlation, AEMP adapter, impairment trigger, WO parts/labour
  lines, M45 goods-receipt registration, M47 extra lifecycle states, insurance/vendor scorecard/key custody/CCTV.

## 6. State (21 Nov 2026)
- **Landed and pushed:** `bc204bd6..e23fbe2e` on `fix/a03-live-data-and-pending-work` (8 commits, rebased onto the A04
  and A02-pass-2 landings; re-tested against both: 1,603 + 1,592 + 6,305 passed, the remaining failures reproduce on
  A02's code alone and were sent to A02). Branch `fix/a07-erp-audit` pushed.
- **Deployed 21 Nov ~09:05 UTC:** backups `1000 fix/backups/fix_{real,dev}_pre_a07_erp_2026-11-21.dump`; `-u` of the 11
  A07 modules on fix_real and fix_dev (exit 0, no errors); finance seed on fix_real (12 accounts, 5 made reconcilable,
  FA journal, 7 categories configured, 41 account roles, D7b/D14/D21 switches; health check OK); on fix_dev the
  switches/figures only (its chart is a different, generic chart); `__system__` and `admin` time zone = Asia/Dhaka on
  both; one restart of 8069 (fix_real) and 8090 (fix_dev): 155 / 153 modules loaded, no errors.
- **Live verification:** 57/57 A07 reports and 108/108 A07 list screens read on BOTH ports with 0 failures and 0
  dropped columns; wiring check on fix_real: 260 consumers, 290 crons, 108 surfaces, 0 problems.
- **Site register (owner, 21 Nov):** fix_real's live branch list was checked against the real branch file
  (Branch_details.xlsx, 79 branches): only 15 of the 73 live fix_real branches reconcile; the other 58 carry
  catalogue-style references and appear in no real source. On the owner's choice, 15 M47 sites were created
  (state Operational, real address, branch OU; lease, licences, utilities, floor area and accountable manager left
  for the Facility Manager, said in each site's readiness notes). Live probe after the load: 57/57 reports, 108/108
  screens. Data findings for the branch master (M30): 11 of those 15 branches point at "Main Operating Unit"
  instead of an OU of their own, 4 live branches have no company, and 58 live branches need reconciling.
- **Branch OUs (owner, 21 Nov):** the 11 confirmed branches on "Main Operating Unit" keep it until a Branch Manager
  (R-06) is named among their staff (12 Nov rule C12: branch approvals route to the branch OU's manager); then
  `_migration/scripts/sync_13_brand_branch_ou_fix_real.py apply` gives each its own OU (dry run 21 Nov: 0 of 15
  branches have a manager yet). The 58 unmatched branches wait for the owner's confirmed branch list.
- **Waiting on the owner (agreed 21 Nov):** equipment / vehicle / lease / IoT registers (owner will send; loaders are
  built through the normal create paths when they arrive), role holders' names (owner will send), HR's wage-deduction
  cap (HR will confirm; recoveries stay on 100049 meanwhile). A02 is fixing the A02 defects found here (field-cash
  shortage call, M05/M03/M08 screens); they ship in the A06 wave.
- **Open (people / data):** see §5. Plus: fix_dev's generic chart has no A07 account map (fix_real is the estate;
  map fix_dev only if it is still used for finance testing).
