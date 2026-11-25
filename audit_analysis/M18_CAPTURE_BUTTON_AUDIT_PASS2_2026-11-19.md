# M18 E-Waste & Recycling: second capture audit (19 Nov 2026)

**Reported:** not all the M18 sub-modules have a relevant data-capture button.

**Scope:** the 10 sub-module pages of the M18 workspace (`cd_p03_portal/static/src/a05/m18.js`), measured against:
- the M18 specification (`1000fix_ERP_Module/03_Modules/D_Circular_and_Asset_Based_Business/M18_EWaste_Recycling_and_Circular_Economy.md`): FR-ESG-001…026, T-01…13, BRU-ESG-01…20, the 15 owned entities of §10.1;
- the code: `cd_ewaste` and `controllers/a05/m18.py`.

The first pass ([M18_CAPTURE_BUTTON_AUDIT_2026-11-13.md](M18_CAPTURE_BUTTON_AUDIT_2026-11-13.md)) gave every page a button. It fixed the dead certificate button and made the six evidence links uploadable. Its "Still open" table listed spec records that had no model at all. Those records, read page by page, are why pages still lacked a relevant capture.

## 1. What was there (shared tip 422b005b)

Measured with the engine's own `fregCreate`, run in node over the real registry, then read against the FRs:

| Page | What it offered | What the spec records there | Verdict |
|---|---|---|---|
| 1 Intake & Channels | + Collection Intake; incentive chip | FR-ESG-001/003: channel and source, condition, **hazardous flags**, **photographic evidence**. FR-ESG-005 / **BRU-ESG-14 (H)** / AC-15: corporate disposal reconciled to the client's declared asset list (entity `fix.corporate.disposal`) | **Missing**: the collection held customer, device, category and weight only; no corporate disposal anywhere |
| 2 Triage & Disposition | + Triage Record (4 decisions) | FR-ESG-006 "against **published criteria**"; FR-ESG-007 / **BRU-ESG-09 (H)** "assessor, **criteria** and **evidence**"; FR-ESG-008 **parts harvesting**; FR-ESG-023 / **BRU-ESG-15 (H)** **donation** | **Missing**: no criteria, no evidence, no harvest or donation route |
| 3 Data Destruction | Start Secure Destruction; bind; release | FR-ESG-009 | OK |
| 4 Outbound Recycler | + Batch; recycler, PIC, money chips | FR-ESG-024 / **BRU-ESG-18 (H)**: the recycler's **declared onward destinations**, verified at least annually (entity `fix.partner.downstream`) | **Missing** |
| 5 Green Certificates | Record a certificate from its batch | FR-ESG-013 (P0) / T-03 / **BRU-ESG-04 (H)** / AC-07: "**flag any item not covered**", an open exception until closed. FR-ESG-014 / **BRU-ESG-19 (H)**: material recovery by class and weight, at an agreed rate, as the batch's income (entity `fix.material.recovery`) | **Missing**: a certificate certified the whole batch or nothing; recovery was one money line |
| 6 Public Drives & Bins | + Drive Event | FR-ESG-022: designated **collection points** (bins) with capacity, storage constraints, hazmat limits and responsible person (entity `fix.collection.point`) | **Missing** |
| 7 Hazardous Fraction | + Battery Dossier | FR-ESG-015: batteries **and CRTs, mercury lamps, refrigerant, toner**. **T-06 / BRU-ESG-07 (H)**: a ceiling **per location and class** | **Partly missing**: batteries only; one company-wide ceiling per typed location name |
| 8 EPR Reporting | + Statutory Return | FR-ESG-017 | OK |
| 9 ESG & Carbon | nothing | FR-ESG-019 / T-08 / Q-09: a documented, **versioned factor set**, approved, stamped on every figure. The figures stay computed (BRU-ESG-11) | **Missing**: the factor was a config parameter anyone with settings access could change |
| 10 Compliance Pack | + DoE Registration | FR-ESG-016: the **regulatory register** (instrument, obligation, owner, evidence source, review date); **BRU-ESG-16** quarterly review; AUT-ESG-19 (entity `fix.regulatory.obligation`) | **Missing** |

## 2. What was built

`cd_ewaste` 19.0.0.2.0. Most of it is in the new file `models/fix_m18_capture.py`, imported last. Every decision is a method that checks its role. Where the spec separates duties, the person who recorded a thing does not approve it.

| Page | Record | Rules it enforces |
|---|---|---|
| 1 | Collection receipt fields | Channel (9 channels of FR-ESG-001, set automatically for M14/M15 hand-overs), condition, five hazard flags, receipt photo **upload**, collection point, declared corporate asset. All frozen once triaged. Received only at an **active** point; over capacity notifies HSE |
| 1 | **Corporate Disposal** `fix.ewaste.corporate.disposal` + declared-asset lines | The asset list is entered as a grid and **frozen when receiving starts**. An item is booked against one declared asset, only from the contract's client, once. A line is *reconciled* when its item is certified, disposed, donated, or routed under a verified M06 certificate. **Close is refused** while any asset is unreconciled (BRU-ESG-14). An asset that will not arrive is closed only as an exception, with a documented reason accepted by a compliance officer |
| 2 | **Triage Criteria** `fix.ewaste.triage.criteria` | Versioned. Written by one compliance officer and **published by another**. Publishing retires the previous version. Frozen once published. The version in force is **stamped on every decision**, and a typed version is refused. Under criteria in force a decision needs the functional result and photo evidence. Reuse and donation need a fully functional device. Donation needs a market value at or below the criteria's ceiling |
| 2 | Triage decision | Functional, cosmetic and value results; evidence **upload**. All write-once, evidence and notes included (T-04) |
| 2 | **Harvest route** | Decision "Parts Harvest", then **Route for Parts Harvest** (assessor). It is refused until a verified M06 certificate is bound (spec §8.2). The unit then goes to M14 by the existing `ewaste.reuse_routed`, and M14 grades and harvests it into M15 stock |
| 2 | **Donation** `fix.ewaste.donation` | Only for an item triaged "Donation"; one live donation per item. **Approved by a compliance officer who did not raise it**, with the recipient's registration number. **Hand-over** (dispatcher) needs the signed acknowledgement upload and passes the **M06 gate** on the item. The item ends **Donated** (new terminal state) |
| 4 | **Downstream Vendor** `fix.ewaste.partner.downstream` | A recycler is **not approved without a declared destination**. Verified from uploaded evidence by a recycler approver **who did not declare it**; re-verified at least yearly (`cd_ewaste.downstream_verification_days`, 365). **Dispatch is refused** unless the recycler has a current verified destination for the batch's material |
| 5 | **Uncovered items** on the recycler certificate, and **Certificate Exception** `fix.ewaste.certificate.exception` | The draft certificate lists the batch items the recycler's certificate leaves out. Issue certifies only the covered items, checking the stated weight against those items. Each uncovered item opens an exception that is **never typed and never closed silently**. A **supplementary certificate** can then be recorded for the batch; when it covers the item, the exception resolves. Otherwise a compliance officer **other than the certificate's issuer** closes it on a recorded finding. Revoking a supplementary certificate re-opens exceptions for its items |
| 5 | **Material Recovery** `fix.ewaste.material.recovery` | Per processed batch and material class (9 classes of FR-ESG-014). Total weight is capped at the batch's processed weight. **Raise Batch Income** creates the batch's recovery-income settlement (BRU-ESG-19). The **finance approver who recorded the weights cannot approve it** (spec §13 SoD). Readable only by the dispatcher, compliance, finance and procurement roles (spec §13 field restriction) |
| 6, 7 | **Collection Point** `fix.ewaste.collection.point` + hazardous ceilings | Kind, branch, responsible person, capacity, storage constraints, one ceiling per class (grid). **Activated by an HSE officer who did not register it**, and frozen while active. A battery or hazardous record at a point is held **only for a class the point has a ceiling for**, and refused beyond it (T-06, BRU-ESG-07). Damaged/swollen lithium is its own class (BRU-ESG-08). Closing is refused while the point holds anything |
| 7 | Hazardous fractions | CRT glass, mercury lamp, refrigerant and toner join the cell chemistries. A hazardous item opens **one hazmat record per hazard flagged at receipt** |
| 9 | **Emission Factor Set** `fix.esg.factor.set` | Proposed with its source and source document; **activated by another compliance officer**; the previous set retires. CO2 avoided is now computed with the company's active set and stamped with its version. The parameter is only the fallback. The ESG figures still have no entry path |
| 10 | **Regulatory Obligation** `fix.ewaste.obligation` | Instrument, clause, duty, owner, evidence source, frequency. Activated with an owner and an evidence source. **Review an Obligation** records the finding and note, and sets the next review **at most 92 days** ahead (BRU-ESG-16) whatever the duty's frequency. A daily job flags overdue reviews (AUT-ESG-19). Status changes only through a review |

**Workspace:**
- 10 new lists and 12 new forms (3 of them step forms that pass their inputs to the method).
- Chips on pages 1, 2, 4, 5, 6, 7, 9 and 10.
- 10 new surfaces; `writable.py` regenerated (M18 lines only).
- The diversion KPI and report count harvest and donation as diverted from disposal (GRI 306-4).

**Page "+ New" after the fix:**

| Page | Opens |
|---|---|
| 1 | Collection Intake (chips: Corporate Disposal Contract, Accept a Corporate Asset Exception, Incentive) |
| 2 | Triage & Sanitization Record (chips: Triage Criteria, Route for Parts Harvest, Donation Hand-over) |
| 3 | Start Secure Destruction |
| 4 | Recycler Dispatch Batch (chip: Downstream Vendor Declaration, …) |
| 5 | Record a Recycler Certificate (chips: Close a Certificate Exception, Material Recovery, …) |
| 6 | Collection Drive Event (chip: Collection Point) |
| 7 | Battery & Hazardous Dossier (chip: Collection Point) |
| 8 | Statutory Environmental Return |
| 9 | **+ New Emission Factor Set** (the figures stay computed) |
| 10 | **Regulatory Obligation** (chips: Review an Obligation, DoE Registration, …) |

## 3. Evidence

All runs used a private clone of the test database (`fix_test_m18c2`, `cd_ewaste` upgraded to 19.0.0.2.0 with 0 errors). fix_real and fix_dev were not touched while testing.

| Check | Result |
|---|---|
| Guard test `cd_p03_portal/tests/test_m18_capture_pass2.py` | **33 passed** |
| What the guard covers | <ul><li>the page rule over the real registry (node), page by page</li><li>no creatable form omits a required field without a default</li><li>every grid field exists; step-form inputs are the methods' own parameters</li><li>evidence is uploaded, never picked</li><li>every new record exercised through the endpoint its form uses, as non-admin users holding only their M18 role</li></ul> |
| Mutation check: each of 23 controls disabled in turn | **23/23 red**. The first run left one survivor: "the declarer cannot verify a downstream". The test had tried it with a user lacking the role. The guard now uses an approver who declared the destination |
| Regression on the same clone | **970 passed, 6 skipped, 0 failed**. Covers <ul><li>all of `cd_ewaste`</li><li>both M18 capture tests</li><li>journey 10</li><li>the A05 control suite</li><li>all of `cd_tradein` (M14)</li><li>the A05 settlement consumer</li><li>the 67-module page standard</li><li>the picker standard</li></ul> The 6 skips are the A05 suite's known "no workflow fields" cases |
| Defect found by the regression and fixed | The new recycler-approval rule ran before the routed-approval check (A05 E11). The routed check now runs first |
| Defects found by the guard and fixed | <ul><li>Receipt fields froze only after destruction rather than at triage.</li><li>A duplicate corporate asset or duplicate recovery class reached the database as a raw unique-key error instead of a stated refusal.</li><li>The recovery form's company had no default.</li></ul> |
| ruff 0.8.4 and all pre-commit hooks | clean |
| FF-25 Bengali labels | 89 labels translated in `bn_BD.po`. `cd_ewaste` drops from 78 to 76 untranslated labels, below the shared tip; the estate-wide check was already failing before this pass |
| `writable.py` | regenerated (`form_fields.py --a05`); the diff touches M18 models only |
| After landing (code at f70e0ec8, the clone upgraded to every peer module landed by then) | **1013 passed, 6 skipped, 0 failed**: the same suites plus the new guard |
| Headless walk, private server on the clone (8118, admin) | <ul><li>All 10 pages show their button and chips</li><li>All 24 new or changed lists and forms open</li><li>0 console errors</li></ul> |
| Defects found by the walk and fixed (5dfb8c6f) | <ul><li>Page 9 read "+ + New Emission Factor Set".</li><li>Material Recovery was closed even to the administrator while no M18 role has a holder. Administrators may now read it; only the dispatcher writes it.</li></ul> |

## 4. State: landed, pushed, live

- **Landed** on `fix/a03-live-data-and-pending-work` and **pushed**:
  - 50a7df8e: code and tests;
  - a62539f3: this report;
  - f70e0ec8: the walk fixes.
  The feature branch `fix/m18-capture-pass2` is pushed as well.
- **Deployed 19 Nov 2026** after the owner chose "Land, deploy, restart":
  - `cd_ewaste` was upgraded on fix_real and fix_dev inside the M21 session's combined deploy wave (one `-u` per DB, with backups taken by that wave);
  - that wave ran the single restart at 08:06:51: 8069 = PID 81988 (fix_real), 8090 = PID 21792 (fix_dev).
- **Checked read-only on both DBs:**
  - `cd_ewaste` 19.0.0.2.0;
  - 11 new models, the new ACL rows (including the administrator read from f70e0ec8), the 6 new collection columns and the review cron.
- **Live walk after the restart** (headless, its own session, dev login), on 8069/fix_real and on 8090/fix_dev:
  - all 10 pages show the buttons in §2;
  - all 24 new or changed lists and forms open;
  - 0 console errors.
- **Live data:**
  - fix_real holds no M18 transaction (0 collections, 0 recyclers);
  - fix_dev has 1 recycler and 1 batch; that batch now needs a verified downstream destination before it can be dispatched.
  - Every M18 role still has 0 holders on fix_real. The role-gated steps (publish, approve, verify, activate, issue) are refused for everyone, administrators included, until the owner appoints holders. Capturing drafts works now.

## 5. Still open (owner decisions)

| Item | Why it is not built |
|---|---|
| FR-ESG-002 / BRU-ESG-13: portal booking that triggers the incentive on receipt | P01 portal work; the incentive stays a manual, approved settlement, paid only after triage |
| FR-ESG-004 / T-09 / AUT-ESG-09: an M03 consignment for every movement | needs an M03 contract for e-waste consignments |
| FR-ESG-018 / T-11: one-click evidence pack | the Statutory Compliance Pack report covers part of it |
| AUT-ESG-11: certificate-not-received window | no agreed window has been set (spec Q-04 / Q-06) |
| Who holds the roles on fix_real | every M18 role has 0 holders on fix_real: a business appointment |
