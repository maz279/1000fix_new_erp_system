# A07 ERP audit — owner decisions (20 Nov 2026)

**OWNER ANSWER (20 Nov 2026): apply ALL D1–D18 as recommended; D4 = set `__system__` and `admin` to Asia/Dhaka on
fix_real AND fix_dev (plus the code fix); D7(c) = scope the QC-instrument gate to instrument-bearing QC + QM waiver.**

Area A07 = M17 Device Registry, M45 Equipment, M46 Fleet, M47 Facilities, M48 IoT, plus the two A07 bridges.
Six read-only auditors found ~170 findings (P0 18 · P1 ~60 · P2 ~70 · P3 ~20). Most are defects and
will be fixed without asking. The items below need the owner's decision, because they set a business
figure, an account, a policy, or a switch that changes production behaviour. Each has a recommendation (R).

Live facts (fix_real, read-only, 20 Nov): 0 equipment, 0 calibrations, 0 vehicles, 0 drivers, 0 sites,
0 leases, 0 IoT devices, 0 open workshop jobs. All 7 fixed-asset categories have no journal and no accounts.
All 264 active crons run as `__system__`, whose time zone is Europe/Brussels.

**OWNER ROUND 2 (20 Nov 2026, all as recommended):**
- D19 accounts: NEW 200128 Fixed Asset Sale Clearing (liability_current; `account.disposal_proceeds`), NEW 200129 Fuel Card
  Clearing (liability_current; `account.fuel_card_clearing`), petty-cash fallback for a branch with no M50 imprest fund =
  existing 100034 Advance for LP, Petty Cash & Others (`account.petty_cash`).
- D20 payroll recovery: HR-approved recharges stay on 100049 Employee Recovery Receivable and are collected manually;
  the payroll deduction switches on only once HR enters the statutory cap (`cd_payroll_bd.recharge_deduction_limit_percent`).
- D21 IoT figures: alert acknowledgement SLA critical 15 / major 60 / minor 240 minutes; predictive-model precision floor
  70 % (else suspended, spec Q-08); rule review below 50 % acknowledged alerts; gateway keys rotated every 90 days; late
  readings accepted up to 7 days.

## D1 — Fixed-asset category accounts (FIN-25, P0)
No A07 asset can be capitalised, depreciated, disposed or leased today: every category is unconfigured.
R: a new "FA — Fixed Assets" journal (general) and, per category (cost / accumulated depreciation / depreciation expense):

| Category | Cost | Acc. depreciation | Expense |
|---|---|---|---|
| VEH Vans & motorbikes | 100044 Vehicle | 100601 Acc. Depreciation of Motor Vehicles | 500803 Depreciation Of Motor Vehicles |
| FIT Fit-out | 100603 Leasehold Improvement | 100602 Amortisation on Leasehold Improvement | 500801 Amortisation on Leasehold Improvement |
| ROU Right of use | 100801 Right of use Asset (IFRS 16) | 100802 Accumulated Depreciation right use asset | 500851 Depreciation on right of use asset |
| IT | 100041 Computer & Computer Equipment | 100607 Acc. Deprn. Computer Hardware & Software | 500805 Depreciation Of Computer Hard & Soft |
| FURN | 100039 Furniture | 100606 Acc. Deprn. of Furniture & Office Equipment | 500804 Depreciation Of Furniture & Office Equipment |
| OFF | 100043 Office Equipment | 100606 | 500804 |
| TOOL (test equipment) | 100803 Tools | NEW 100609 Acc. Depreciation – Tools | 500865 Depreciation |

Loss on disposal 500901 (exists). CWIP for every category = NEW 100608.

## D2 — New accounts to create (FIN-25, M47-37, FIN-10/11)
R: create these on fix_real and fix_dev (codes are free in the real chart):
- 100608 Capital Work in Progress (asset_fixed)
- 100609 Acc. Depreciation – Tools (asset_fixed)
- 200126 Lease Liability (IFRS 16) – Current (liability_current)
- 200505 Lease Liability (IFRS 16) – Non-current (liability_non_current)
- 200127 Rent Payable Clearing (IFRS 16) (liability_current)
- 500604 Interest on Lease Liability (IFRS 16) (expense)
- 400116 Gain on Disposal of Fixed Assets (income_other)
- 500910 Impairment Loss on Fixed Assets (expense)
- 100048 Insurance Claim Receivable (asset_current)
- 100049 Employee Recovery Receivable (asset_current)

## D3 — Running-cost account map (M47-37, M46-01, M45-19)
Today every A07 cost goes to 500200 Expense Clearing. R (existing accounts):
fuel 600259 Fuel Expense · vehicle repair/service 500005 Auto Maintenance · vehicle insurance 500505 Insurance ·
vehicle document renewal fees (fitness, tax token, route permit) 5000110 Certifications & Registrations ·
traffic fine absorbed 500121 Penalty Expense · office rent (short-term/exempt leases) 500401 Office Rent ·
electricity & water 500403 Water & Electricity · gas 500031 Gas Charge · other utilities 500012 Utilities Expense ·
facility repairs and calibration service 510003 Repair & Maintenance Expense · trade licence 500503 Trade License Fees ·
other licences 500209 Legal & License fee · security deposit 100031 Security Deposit · advance rent 100032 Advance House Rent ·
equipment below the capitalisation floor 500093 Tools Expense.

## D4 — Cron time zone (estate-wide; M45-08, M47, M48-16)
`__system__` (runs all 264 crons) is Europe/Brussels. From 18:00 to 23:00 UTC (midnight to 05:00 Dhaka), every cron's
"today" is the previous Dhaka day: calibration lapses, document/licence expiry, consent expiry and PM due dates fire a day late.
R: set the time zone of `__system__` and `admin` to Asia/Dhaka on fix_real and fix_dev. ALSO, in code, A07 crons compute the
Dhaka day explicitly, so they no longer depend on the user's time zone. This touches every area's crons (for the better);
the peer sessions will be told.

## D5 — IFRS 16 policy (M47-01..09, FIN-02/03/07/08/09)
R:
(a) the landlord's rent bill on a commenced lease debits 200127 Rent Payable Clearing, not expense;
(b) measure the lease on the escalated payment schedule, not a flat rent;
(c) build remeasurement (modification) and termination accounting;
(d) leased vans/motorbikes also go on the IFRS 16 book;
(e) exemptions: lease term ≤ 12 months, or underlying asset new value ≤ BDT 500,000 → expensed (500401 / 500005).
   Finance confirms the BDT figure;
(f) the incremental borrowing rate is entered per lease by finance (activation refuses 0, as today);
(g) a monthly cron posts due IFRS 16 entries (Dhaka month-end).

## D6 — Lease approval (M47-04)
Any internal user can record a lease, and a Branch Ops Lead can terminate one alone.
R: recording a lease and terminating it both go through M63 DOFA on the total commitment
(sum of all payments): ≤ 1,000,000 Operations Director; above that CFO; above 10,000,000 CEO.
Only the Facility Manager/Branch Ops Lead role may create.

## D7 — Calibration control (B9) and the workshop QC switch (M45-03, M45-13)
(a) Evidence: a calibration PASS always needs a certificate file and the provider (and accreditation ref when "accredited"
    is ticked). R: enforce now, always (no switch).
(b) The B9 switches (only Calibration Technicians certify; a second, different QM accepts) are OFF. The QM, Custodian and
    Calibration Technician groups have the SAME 10 members, so segregation would barely hold. R: turn both switches ON now
    (fix_real has 0 instruments, so nothing is blocked), and appoint different people per role (see D8).
(c) `cd_workshop.qc_requires_instrument` is ON on fix_real with 0 instruments: the first real workshop job will be unable
    to pass QC. R: keep it ON, but make the gate apply only to service categories whose QC procedure names a measuring
    instrument. Until instruments are registered, QC for those jobs needs a QM waiver with a reason, recorded on the job.

## D8 — Role holders (B1 carried over)
The A07 roles are held either by nobody or by the same 10 people for every role. R: you name the holders. Until then
nothing changes, but the SoD checks stay on. (No action from me without names.)

## D9 — Staff recharge for lost/damaged equipment and recovered traffic fines (M45-05, FIN-10, M46-14)
R: allowed only with an HR-approved recovery decision. It books Dr 100049 Employee Recovery Receivable / Cr the loss or
expense account, and is recovered through M56 payroll deduction within the statutory wage-deduction limit, which HR
records as a setting. The deduction never runs until HR enters that limit (fail-closed).

## D10 — Write-off and disposal basis (M45-30, FIN-12)
R: the DOFA amount is the M49 net book value when the item is capitalised, and acquisition cost otherwise.
Sale proceeds are captured on disposal: Dr receivable/cash, Cr 400116 gain or Dr 500901 loss vs NBV, and output VAT per M51.
Disposal of a vehicle needs CFO approval (BRU-FLT-20). Archiving a vehicle never raises a disposal.

## D11 — Traffic-fine and accident authority (M46-14)
R: a fine's recover-or-absorb decision uses the existing estate DOFA ladder: ≤ 10,000 Logistics Manager, ≤ 50,000
Operations Director, above CFO. Payment goes through AP or petty cash, never a typed "paid" date.

## D12 — Device warranty on resale and the stolen flag (M17 OWNER-1..3)
R: (a) a manufacturer warranty transfers with the device. A 1000FiX extended warranty or protection plan transfers only
through the M09 four-eyes warranty transfer; otherwise it lapses at the ownership change. (b) Anyone may raise "lost", but
"stolen" needs a GD/police reference. Add a "disputed ownership" flag that blocks hand-over the same way.

## D13 — Rework window (M17 OWNER-4, spec Q-04)
R: 30 days, the same for all device families (a parameter, so it can change later).

## D14 — Fleet switches (M46-21)
fix_real has 0 vehicles, so turning on `dispatch_requires_vehicle` would block every field dispatch.
R: now: require_fuel_receipt ON, pm_overdue_takes_offroad ON, legacy_documents_count_valid OFF (rules that only bite once
vehicles exist). Later, after vehicles, documents and drivers are loaded: dispatch_requires_vehicle and
require_licence_class (you tell me when).

## D15 — Facility SLA, anomaly and test intervals (M47 O-4)
R: facility work-order SLA (response / restore): emergency 2 h / 8 h · high 8 h / 48 h · normal 24 h / 5 days ·
low 72 h / 15 days. Utility anomaly factor 2.0× the 3-month average. Generator/UPS test every 30 days. All parameters.

## D16 — Budget control on A07 spend (M47 O-5, FIN-15)
R: check against the M54 budget line for branch + cost type. Above the remaining budget, hold for the Branch Ops Lead
(facility) or Logistics Manager (fleet), plus the CFO above BDT 100,000 over budget. No hard stop.

## D17 — IoT data (M48 Q-01, B5)
R: (a) M48 becomes the single time-series store. The M46 telematics and M05 endpoint readings feed it through adapters,
with the M17 consent gate applied. (b) Retention: raw readings 30 / 90 / 365 days by signal criticality
(low / medium / high), hourly aggregates 3 years, daily forever; raw purge ON. (c) The approval of a preventive work
order pins its scheduled date.

## D18 — Scope of this pass
R: fix every P0, P1 and P2 DEFECT, plus the P1/P2 GAPs that complete a money path, a control or a cross-module link.
Build the printable documents (asset tag, calibration certificate register, custody hand-over slip, vehicle logbook,
facility work order, gate pass).
Defer to a follow-up wave the new subsystems the spec names but nobody uses yet: fleet trips/driver behaviour
score/tyre & battery tracking, fuzzy device identity matching, estate reconciliation, IoT rule-engine statistics
(non-absolute thresholds, correlation), and the AEMP telematics adapter.
