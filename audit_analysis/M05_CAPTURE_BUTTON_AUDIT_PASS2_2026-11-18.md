# M05 Remote Support & MSP: sub-module capture audit, pass 2 (18 Nov 2026)

**Reported:** not every M05 sub-module page has a relevant data-capture button.
**Spec:** `1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M05_Remote_Support_and_Managed_Services.md` (§5 features, §8.3 client onboarding lifecycle, §9 rules, §10 entities).
**Code:** `cd_p03_portal/static/src/a02/m05.js`, `controllers/a02/m05.py`, `cd_msp_contract`.
**Branch:** `fix/m05-capture-pass2`, based on `576c8804`.
**Previous pass:** `M05_CAPTURE_BUTTON_AUDIT_2026-11-13.md` (pages 3, 4, 8 and 9 fixed then).

## 1. Method

1. **Spec.** The Function Register names 10 sub-modules but lists no individual functions, so each sub-module
   was mapped to its spec section by subject: 1 → §5.1, 2 → §5.2, 3 → FR-011/014, 4 → §5.3, 5 → FR-017/038,
   6 → FR-018/054/055, 7 → §5.4, 8 → §5.5, 9 → §5.6 reporting and credits, 10 → FR-047/048 and §8.3.
2. **Code, as the browser runs it.** Node ran the workspace engine's own `fregCreate` and `fregPanels` over
   the real registry. That gave each page's "+ New", its form chips and its lists.
3. **Data.** fix_real and fix_dev hold 0 MSP contracts, assets, alerts and credits, so no live record is
   affected by the new rules.

## 2. What the pages offered at HEAD

| # | Page | "+ New" | Chips | Finding |
|---|---|---|---|---|
| 1 | Remote Sessions | Remote Session | Remote Session | correct |
| 2 | Monitored Estate | Managed Estate Device | Estate Device, Cloud Subscription | correct |
| 3 | Metrics & Health Scoring | Record a Health Reading | Reading, Backup Job, DR Plan, DR Test | correct |
| 4 | Alerting Engine | Define an Alert Rule | Alert Rule, MSP Ticket | **Maintenance windows were missing.** FR-RMS-019 places them under §5.3 Alerting, because a window suppresses alerting, but they sat only on page 7 |
| 5 | On-Call & Escalation | On-Call Shift | On-Call Shift | correct |
| 6 | Runbooks & Remediation | Runbook | Runbook, Runbook Execution | correct |
| 7 | Patch Management | Patch Update | Patch Update, Maintenance Window | **Lists Patch Policies but had no Patch Policy chip.** The policy form existed, but no chip opened it |
| 8 | MSP Service Desk | Log a Client Ticket | Ticket, Change, Contact, Major Incident | correct |
| 9 | Client Reporting | Generate a Monthly Service Report | Report, Review Meeting, Roadmap Item | **SLA Credits were on no page.** The list and its manual-credit form (FR-RMS-037, BRU-RMS-06: a manual credit needs CFO approval) were reachable only from the menu, and no "SLA Credit" chip existed |
| 10 | Onboarding Projects | **+ MSP Contract** (the module's button) | MSP Contract | **Wrong record, missing feature.** FR-RMS-047 (P1) and §8.3 call for a structured onboarding project: discovery, agents, baseline, contacts, portal, runbooks, alert tuning, SLA set-up, then service live once coverage reaches the agreed share. SLA clocks bind only from go-live. No model held any of this; the button created a contract. FR-RMS-048 offboarding also never recorded the **data return** |

## 3. What was built

### Backend (`cd_msp_contract` 19.0.3.5.0, new `models/fix_msp_services_onboarding.py`)

- **`fix.msp.onboarding`** (FR-RMS-047, §8.3):
  - one project per contract, started by an MSP Engineer, only on an in-service contract that is not yet live;
  - its company and operating unit come from the contract;
  - it arrives with the eight §8.3 checklist steps;
  - stages: Onboarding Initiated → Estate Onboarding (first step done) → Service Live.
- **`fix.msp.onboarding.step`**: done once, by an engineer, with written evidence. Steps cannot be added,
  deleted or ticked by a direct write. The system verifies these steps when they are marked:
  - *Agent deployment*: an asset is enrolled.
  - *Baseline capture*: every enrolled asset has a reading.
  - *Contact registration*: a client contact may raise tickets.
  - *Runbook authoring*: an active runbook covers the contract (or all contracts).
  - *Alert threshold tuning*: an active alert rule watches the contract (or all contracts).
  - *SLA configuration*: the SLA target is set.
- **Go Live** needs every step done, an entitled contract, and coverage at or above the agreed percentage.
  Coverage counts agents that reported in the last 24 h (the BRU-RMS-04 measure) against the covered devices.
  Go-live stamps `service_live_at` on the contract and closes the project.
- **SLA clocks bind from go-live** (§8.3):
  - a contract being onboarded has no binding alerts yet;
  - a live contract measures only alerts raised since go-live;
  - a contract with no onboarding project keeps its whole history binding, as before.
- **FR-RMS-048:** `action_record_data_returned(evidence)` during offboarding. Offboarding completes only when
  agents are removed, access is revoked and the data is returned, each evidenced.

### Workspace (`m05.js`, `controllers/a02/m05.py`, regenerated `a02/writable.py`)

| # | Page | "+ New" | Chips now |
|---|---|---|---|
| 4 | Alerting Engine | Define an Alert Rule | Alert Rule, MSP Ticket, **Maintenance Window** (+ Maintenance Windows list) |
| 7 | Patch Management | Patch Update | Patch Update, **Patch Policy**, Maintenance Window |
| 9 | Client Reporting | Generate a Monthly Service Report | Report, **SLA Credit**, Review Meeting, Roadmap Item (+ SLA Credits list) |
| 10 | Onboarding Projects | **Start a Client Onboarding** | **Client Onboarding**, MSP Contract (+ Onboarding Projects and Onboarding Checklist lists) |

- There is a new nav group, **Client Onboarding**, with two lists: *Onboarding Projects* (Go Live) and
  *Onboarding Checklist* (Mark Step Done, with evidence).
- The onboarding form has two tabs and shows the checklist as a read-only grid.
- The MSP Contracts list has a new action, **Record Data Returned**. The contract form shows the go-live
  and the data return.

## 4. Evidence

- **Workspace rule run in node over the real registry.**
  - At HEAD: SLA Credits was the one list on no page; the credit and patch-policy forms had no chip.
  - After the change: every list sits on a page, every form has a chip, and every chip sits on a page.
- **Tests on a private clone** (`fix_test_m05c2`, made from an idle copy and brought level with the code
  for 40 lagging modules):
  - **822 passed, 0 skipped** across the cd_msp_contract suite, `test_m05_msp_contract_form`, and the
    estate guards `test_submodule_create_button`, `test_estate_module_pages`, `test_screens_wiring` and
    `test_a02_write_whitelist`.
  - New `test_m05_onboarding.py` (15 tests). It covers:
    - start from the page form (non-engineer refused);
    - one project per contract, and none for a departing client;
    - the checklist and go-live cannot be typed;
    - evidence and the system checks on each step;
    - go-live blocked by an open step or by low coverage;
    - a live project is closed;
    - SLA binding before, during and after onboarding.
  - Updated `test_m05_submodule_capture.py` (page 10 button; required chips on pages 4/7/9/10; every list
    on a page) and the offboarding test (data return).
- **Two failures not caused by this change.** They fail identically on the shared tip `6deb4dca` without it:
  - `test_no_submodule_page_offers_another_records_button` (M30/1 Branch Master);
  - `test_a_row_opens_a_form_of_its_own_model` (M60 legal holds open the M24 form).
- **Mutation check: 6 of 6 caught.** Each mutation broke one rule:
  - the coverage gate;
  - no binding SLA during onboarding;
  - binding only since go-live;
  - the data-return gate;
  - the step system checks;
  - the open-step gate.

## 5. State (18 Nov 2026)

- **Landed** on `fix/a03-live-data-and-pending-work` as `4f09c1db`. **Pushed** (origin `4f09c1db`).
- **Backup:** `_migration/backups/fix_real_pre_m05_capture2_2026-11-18.dump` (51 MB).
- **Upgraded** `cd_msp_contract` 19.0.3.5.0 and `cd_p03_portal` on **fix_real** and **fix_dev**: no errors, no
  missing tables, no other module left behind.
- **Probe of the landed controller code against both databases** (read-only, rolled back): **50 of 50**
  M05 screens load (26 lists, 24 forms). That includes the onboarding list, checklist and form, and the
  credit and policy forms.
- **Restart of 8069 and 8090: not done by this session.** The safety check refused stopping the
  production server processes. Both servers started at 22:11, before the landing (22:32). They load
  Python only at start, so until they restart:
  - the new onboarding surfaces are not served;
  - "Record Data Returned" is not whitelisted.

  The next restart (the operator's or a peer's) brings it all live. No database change is needed.

## 6. Not built

- **The M67 project link.** §8.3 says the onboarding project is "created in M67". cd_msp_contract does
  not depend on cd_ppm (accounting, HR and the workflow engine), so the onboarding is an M05 record. A link
  to an M67 project is an integration decision for the owner.
- **Final reporting at offboarding** (FR-RMS-048).
- Spec features with no capture of their own:
  - FR-RMS-012 software inventory;
  - FR-RMS-013 configuration baseline drift;
  - FR-RMS-053 client warranty tracking;
  - FR-RMS-058 client satisfaction;
  - FR-RMS-033/034 entitlement consumption beyond the device count.
