# M42 Supplier Relationship — workspace data-capture audit

**Scope.** The P03 Operations Workspace for M42 (`#/workspace/M42`): does every
sub-module have a relevant data-capture (data-entry) button, and does each
button capture what it says?
**Units.** CD-M42-01..04 (`cd_vendor_ext`, `cd_supplier_qualification`,
`cd_supplier_scorecard`, `cd_supplier_risk`) and CD-P03-01 (`cd_p03_portal`).

## 1. What is supposed to be there

| Source | What it defines for M42 |
|---|---|
| Module spec `1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/M42_Supplier_Relationship_and_Performance.md` | 6 functional areas / 34 FRs (§5), 19 owned entities (§10.1), roles and SoD (§13) |
| Navigation registry `contracts/nav/registry.json` (frozen from the prototype) | 9 Function Register sub-modules, 11 screens in 4 groups, 5 reports, **4 forms** (Supplier Profile, Qualification Questionnaire, CAR, Risk Assessment) |
| CD register `tooling/cd-register.yaml` | CD-M42-01 `cd_vendor_ext`, -02 `cd_supplier_qualification`, -03 `cd_supplier_scorecard`, -04 `cd_supplier_risk` (W4) |

The registry's four forms cover only four of the nine sub-modules. Mapping
each sub-module to the spec entity that people actually record:

| # | Sub-module | Spec (FR / entity) | Capture form(s) |
|---|---|---|---|
| 1 | Supplier Profiles | FR-001/002/005, `fix.supplier.profile` | Supplier Profile |
| 2 | Segmentation | FR-003/004 (segment, risk tier) | **Segment & Risk-Tier Review** (new) |
| 3 | Qualification | FR-008/009, `fix.supplier.qualification` | Qualification Questionnaire |
| 4 | Documents & Validity | FR-016/017/018, `fix.supplier.document`, `fix.supplier.bank.change` | **Supplier Document**, **Bank Detail Change Request** (new) |
| 5 | Contracts & Price Lists | FR-021/023, `fix.supplier.agreement`, `fix.supplier.price.change` | **Supplier Agreement**, **Price Change Request** (new) |
| 6 | Scorecards | FR-027 (computed, T-04/T-05) + FR-030 `fix.supplier.review` | **Performance Review** (new). The score itself is never typed in |
| 7 | Corrective Actions | FR-031, `fix.supplier.car` | CAR |
| 8 | Risk Assessment | FR-033, `fix.supplier.risk` | Risk Assessment |
| 9 | Compliance Screening | FR-019/020 | **Integrity Screening Declaration** (new) |

## 2. What the codebase had (before)

1. **Wrong module content.** `p03_modules_meta.js` M42 held warehouse content:
   2 sub-modules ("Wave Picking & Staging", "Barcode Inbound Receipt"), one
   screen ("Dock Receiving"), the KPI "Orders Picked Today" and the form
   "Inbound GRN Receiving Form". The same drift affected **all 67 modules**:
   the 2026-10 `sync-p03-meta-titles.py` fix corrected titles only.
2. **Every data-entry button opened the M01 Service Order intake modal**
   (`openNewForm`), in every module, including the header "+ New Service Order".
3. **No sub-module had its own capture button.** The sub-module view showed
   the module's first three forms, the same for every sub-module.
4. **No M42 backend** apart from `fix.supplier.scorecard` (in `cd_cx_feedback`).
   None of the four registered CD-M42 addons existed.
5. Seven hard-coded screen ids (journey chips, record fact box, Tell-ME)
   pointed to ids absent from the registry and silently opened the wrong page.

## 3. What changed

- **Backend (4 addons, 14 models).** All 11 capture forms are backed by real
  models, with the spec's rules enforced:
  - immutable, versioned qualifications (T-03);
  - the fail-closed activation gate `check_activation` (T-01/T-02);
  - de-activation when a qualification lapses (FR-011);
  - SoD — proposer/requester/raiser/assessor cannot approve or verify (§13);
  - bank-change hashing and immutability (T-06);
  - evidence hashing (T-11);
  - idempotent daily expiry (T-07);
  - price rows only through an approved change (FR-023);
  - the single-source rule (FR-033);
  - outbox events (T-09).

  Bengali `bn_BD.po` files are 100% translated.
- **Capture plumbing (`cd_p03_portal`).**
  - **Discovery.** A model opts in with `_p03_capture = {module, form, fields}`. `/p03/capture/{forms,schema,options,submit}` discovers it through the ORM registry, so the platform layer never imports a domain module (AR-007).
  - **Security.** Every call runs as the user (no sudo), and only the fields named in the spec are accepted.
  - **Workspace.** Each Function Register tile has its capture button(s). The forms card and the header open the named form. A registry form with no backing model says "backend not yet built" instead of opening an unrelated form.
- **Meta re-alignment.** `tooling/scripts/sync-p03-meta.py` regenerates
  `P03_MODULES` from the registry for all 67 modules (`--check` guards drift,
  covered by a test). The sub-module → form overlay lives in
  `p03_capture_map.js`, kept by hand as each module's backend lands.

## 4. Evidence

| Check | Result |
|---|---|
| `odoo-bin -i` of the 4 addons + `cd_p03_portal` on a fresh DB | clean |
| `tooling/scripts/livefire-m42.py` (Odoo shell, rolled back) | 57/57 |
| Addon pytest suite | 950 passed, 1 pre-existing failure (`cd_field_service` happy path) |
| Browser drive of `#/workspace/M42` (Playwright) | 9/9 sub-modules carry capture buttons; 11/11 forms load live schemas; save creates the record; duplicate returns the T-12 message; EN and বাংলা labels; no JS errors |
| Fitness checks | unchanged; the pre-existing `audit-view-integrity` failure in `cd_inventory` remains |

## 5. Follow-ups (not done here)

1. **Other modules.** They now show their correct registry sub-modules and
   forms, but their form buttons honestly say "not yet wired" until each
   module's models declare `_p03_capture` and `p03_capture_map.js` gains the
   module. This includes M16, whose `fix.purchase.order` already exists.
2. **Bengali at runtime.** Odoo 19 ships only `bn_IN`; it never loads the
   estate-wide `bn_BD.po` files. This is pre-existing, and a decision is needed
   (add a `bn_BD` `res.lang`, or ship `bn.po`).
3. **Role groups.** Spec §13 roles (Procurement Manager, R26 Finance, R03 CFO
   permanent block) have no Odoo groups yet. ACLs are `base.group_user`, and
   SoD is enforced in code. Bank-change approval relies on Odoo's own
   *Contact Creation* right.
4. **Not yet built.** From spec §10.1 / §12: the supplier-category standing
   table, consignment agreement (FR-024), development plan, concentration
   analysis, category strategy, the P05 supplier-facing flows, the T-08
   employee conflict-of-interest match, and the activation-gate HTTP API for M16.
