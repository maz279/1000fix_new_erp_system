# M33 Customer & Party Master: sub-module capture audit

**Date:** 14 Nov 2026 · **Area:** A03 · **Workspace fragment:** `cd_p03_portal/static/src/a03/m33.js`
**Backend:** `cd_party_master` (models), `cd_p03_portal/controllers/a03/m33.py` (surfaces), `controllers/a03/writable.py` (write whitelist, generated)

The user reported that not every M33 sub-module page has a relevant data-capture button. They were right.
Of the 13 pages:
- two had no capture at all;
- two captured the wrong record;
- one had no way to raise a data-subject request, publish a notice, withdraw a consent or record processing.

Several forms that did exist let a person type values the system should measure or decide.

## What M33 is supposed to capture

The spec is `1000fix_ERP_Module/03_Modules/B_Customer_Engagement_and_Experience/M33_Customer_and_Party_Master_Management.md`:
- §5: FR-CPM-001..052
- §8: party, consent and duplicate lifecycles
- §9: BRU-CPM-01..16
- §10.1: owned entities
- §13: roles

| # | Sub-module | Spec basis | What a person records there |
|---|---|---|---|
| 1 | Party Record & Roles | FR-CPM-001/002/004 | **The party record**, and the roles it holds |
| 2 | Classification | FR-CPM-003 | **The party class**: Individual / Dealer / Corporate / Government. Seller, brand partner and vendor are roles. |
| 3 | Account Hierarchy | FR-CPM-008..013 | Hierarchy links |
| 4 | Addresses (BD + GPS) | FR-CPM-014..019 | **Tagged party addresses** with Division → District → Upazila → postcode, GPS, and a default per purpose |
| 5 | Identity & OTP | FR-CPM-020..025 | Identity documents. The OTP log is written by the channel that sends the code. |
| 6 | Registration Approval | FR-CPM-010, BRU-CPM-02 | A registration request. Each step is decided in the M63 inbox. |
| 7 | Deduplication & Merge | FR-CPM-026..031, T-03, BRU-CPM-03/04 | A suspected duplicate (scored by the rules), a merge request, dedup rules, detection jobs |
| 8 | Golden Record & Quality | FR-CPM-031/032/033 | **A quality score for the party in front of the steward**; survivorship rules (M64's golden rules, §12.1) |
| 9 | Consent & DSR | FR-CPM-035..044, BRU-CPM-07..11/15 | Consent; **withdrawal**; **data-subject requests**; **transparency notices**; the **record of processing** |
| 10 | Segments | FR-CPM-049/050 | Segments |
| 11 | Credit Profile | FR-CPM-047, BRU-CPM-12 | Credit profiles (the record is M20's) |
| 12 | Status Lifecycle | FR-CPM-005, BRU-CPM-13, §8.1 | **A status change with its reason**; a Tier 2 reactivation |
| 13 | Real-Customer Cut-over | readiness report §7 | Import batches |

## What the code did (proved on HEAD before the fix)

`cd_p03_portal/tests/test_m33_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node over the real registry fragments.
Against unmodified HEAD (`cc24bf5a`), **23 of its 43 checks fail**. All 43 pass after the fix.

| # | Page | "+ New" on HEAD | Chips on HEAD | Defect |
|---|---|---|---|---|
| 1 | Party Record & Roles | + Party Role | Party Master, Party (multi-role) | The page's first capture was a role, not the party it is named after |
| 2 | Classification | + Party Role | Party (multi-role) | **Wrong record**: the class is the party's own field. A role does not classify. |
| 3 | Account Hierarchy | + Account Hierarchy Link | — | — |
| 4 | Addresses | **+ Party** (Party Master) | Address with GPS, Party Master | **Wrong record**: the page listed and created *parties* (name / street / city). The address form was a chip only. fix_real holds **0** party addresses. |
| 5 | Identity & OTP | + Identity Document | Identity Document | — |
| 6 | Registration Approval | + Registration Approval | — | — |
| 7 | Deduplication & Merge | + Duplicate Candidate | Merge Request, Detection Job | The form let the person **type the match score and factors** (T-03: "explainable score"), and re-point an existing candidate to another pair. The Dedup Rule form was on no chip and lacked the block/flag choice. |
| 8 | Golden Record & Quality | **none** | **none** | No capture at all. A steward could not score the party in front of them. Survivorship rules were not reachable from here. |
| 9 | Consent & DSR | + Consent Record | **none** | No data-subject request, notice or withdrawal capture. **The record of processing (FR-CPM-044, P0) did not exist anywhere in the estate.** The consent form did not mark the notice version or proof as required (both are refused server-side), and the notice form offered a computed "active" and no purposes. |
| 10 | Segments | + Customer Segment | — | — |
| 11 | Credit Profile | + Credit Profile | Credit Profile | — |
| 12 | Status Lifecycle | **none** (`create: false`) | **none** | No capture. The status could only be typed on the party form, **with no reason**. |
| 13 | Cut-over | + Party Import Batch | — | — |

Backend defects found on the way:
- **Blacklisting is terminal (only the CEO reinstates, BRU-CPM-13), yet any clerk with Contact write could do it with one edit.**
- The party form also edited `res.partner.credit_limit`. That is a second credit limit beside the M20 credit profile, changed with no approval (BRU-CPM-12).
- A transparency notice's wording could be rewritten after customers had consented against it (BRU-CPM-08).

## What was built

**Workspace (`m33.js`), every page now captures what it names:**

| # | "+ New" now | Other captures on the page |
|---|---|---|
| 1 | + New Customer & Party Master | Party (multi-role) |
| 2 | **+ Classify a Party** (pick the party, set its class; Dealer / Corporate / Government open the two-step registration on save) | Party (multi-role) |
| 4 | **+ New Address with GPS** over a new **Party Addresses** list (party, tag, default, district, upazila, postcode, GPS) | Party Master |
| 7 | + New Duplicate Candidate: the **score and factors are now measured** | Merge Request, Detection Job, **Dedup Rule** |
| 8 | **+ Score a Party** | **Survivorship Rule** (M64's golden-rule form) |
| 9 | + New Consent Record | **Withdraw a Consent**, **Data-Subject Request**, **Transparency Notice**, **Processing Record** (new **Record of Processing** list) |
| 12 | **+ Change Party Status** (Dormant / Blocked / Credit Hold / Blacklisted, with a required reason) | **Reactivate a Party** (Tier 2, with a reason) |

**Form fixes:**
- Party form: status, status reason and credit limit are read-only, with a pointer to where each is changed.
- Address form: party and tag are required, and the form has a default flag.
- Consent form: notice version and proof are required.
- Notice form: purposes and both texts are required, and the computed fields are read-only.

**Server (`cd_party_master` 19.0.1.5.0):**
- `res.partner.action_set_party_status(status, reason)` takes restrictive states only, needs a reason, stamps the date and logs to the chatter.
  Blacklisting now needs DOFA Tier 2 by the form *or* by a plain edit.
  Restricting by plain edit stays open, as the A03 audit decided (its test is unchanged and green).
- `res.partner.action_score_quality()` upserts the party's quality row.
- `fix.party.duplicate`:
  - a pair a person raises is scored by every active dedup rule, and the typed score is ignored;
  - the rule verdicts and who raised it go in the factors;
  - an existing pair, its score and its factors can no longer be changed;
  - a second open candidate for the same pair is refused.
  The detection job and the import keep their measured scores (they write as the system).
- **New `fix.processing.record`** (FR-CPM-044, BRU-CPM-15):
  - **Fields:** party, purpose, lawful basis (consent / contract / legal obligation), data categories, recipients, retention, occurred at.
  - **Append-only:** nobody edits a row, and nobody deletes one inside five years (the system included).
  - **Who records:** the Data Protection Officer only. Every consent capture and withdrawal records itself (AUT-CPM-06).
  - **Consent basis:** must name a consent of the same party.
  - **Erasure:** if the party is erased, the party id is kept.
  - **Isolation:** a company rule was generated by `generate-isolation-rules.py`. The same run also rewrote cd_workshop, cd_competency and cd_rbac_ext; those drifts were reverted.
- `fix.transparency.notice`: the wording, version, purposes and publish date are fixed once any consent references the notice. Such a notice cannot be deleted.
- `fix.bd.address.is_default`: one default per party and tag.
- `controllers/a03/m33.py` serves the two new party actions and the processing register. `writable.py` was regenerated: the duplicate score, the party credit limit and the notice "active" are no longer writable.

## Evidence

- **Node guard:** `cd_p03_portal/tests/test_m33_capture_buttons.py` passes 43/43. On HEAD it fails 23/43.
- **Live tests:** `cd_party_master/tests/test_m33_capture_live.py` passes 13/13. They run as a Contact-manager clerk, a DOFA Tier 2 manager and a DPO, never as the superuser.
- **Mutation check, 3/3 red:**
  - duplicate scoring switched off;
  - the blacklist authority removed;
  - the consent processing record removed.
- **Regression on the private clone `fix_test_m33`:** all of `cd_party_master`, every `test_a03_*` portal test, the M33 guards and `test_a03_approval_bypass`. 542 tests, **0 failures, 0 errors**. The 172 skips are parametrised "carries no workflow-controlled fields" cases.
- **Estate page standard and A03 registry coverage:** green.
- **UI on the private server (8076):**
  - all 13 pages show the buttons above;
  - Change Party Status stored the status, reason, date and chatter line;
  - + New Address with GPS saved, and the address appears on Party Addresses.

## Deploy (14 Nov 2026, 15:31–15:33 machine time, 07:31–07:33 UTC)

- `-u cd_party_master,cd_p03_portal` on fix_real: 155 modules, no errors, no missing tables. The tree held only these changes.
- **8069 restarted at 15:33 (PID 50484)** with scratchpad `launch_8069.ps1`. It had no supervisor, so it was relaunched with Win32_Process Create. It answered 200 within 2 s and the registry loaded cleanly.
- Probed live on 8069:
  - all 13 page grids serve (10,115 roles, 3,659 duplicates, 23,603 quality rows, 23,643 parties);
  - the new actions are served (a made-up action is refused);
  - the processing register and form load;
  - Golden Record & Quality shows + Score a Party.
- **Not committed.**

## Owner gaps (not built)

- **Nobody can take the governed decisions on fix_real:**
  - Party Data Steward: 0 holders;
  - Data Protection Officer: 0 holders;
  - Registration Administrator: 0 holders;
  - client line manager approver: 42 holders.

  So duplicate review and merge, KYC verification, DSR work and processing records wait on role grants.
- **Credit limit changes are not approval-controlled** (BRU-CPM-12, SOD-04). The model of record is M20's `fix.credit.profile` (A08 area), so this is a finance decision.
- **OTP "Mark Verified"** can be pressed by any user without a code. That is a weak point for BRU-CPM-01 (activation needs a verified contact).
- **AUT-CPM-07 is not built:** publishing a new notice does not supersede existing consents.
- **Not modelled:**
  - contact points as their own record (`fix.contact.point`);
  - party-to-party relationships beyond the hierarchy's household / corporate / guarantor / care-of;
  - `fix.bd.geography` (addresses are validated text, not a cascading reference).
- **Live data:** fix_real holds 0 consents, 0 identity documents, 0 credit profiles and 0 party addresses. The pages are ready, but nothing has been captured yet.
- **Small display issue:** after a pick form saves, the "Current Status Since" value can show the old date until the page is refreshed. The stored value is correct.
- **Clean-up:** the private clone `fix_test_m33` is kept, so drop it on request.
