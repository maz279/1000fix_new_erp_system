# M40 Partner, Channel, Alliance & Franchise — Sub-Module Capture Audit (2026-11-19)

**Trigger.** The user observed that not every M40 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/C_Commercial_Pricing_and_Revenue/M40_Partner_Channel_Alliance_and_Franchise.md`. Sections used: §5 FR-PCM-001…042, §6 T-01…15, §8 lifecycles, §9 BRU-PCM-01…20, §10.1 owned entities (25).
- Code:
  - `cd_p03_portal/static/src/a04/m40.js` (the page registry);
  - `cd_p03_portal/controllers/a04/m40.py` (surfaces and report packs);
  - `cd_partner/models/fix_partner.py` and `fix_partner_ops.py` (9 models before this audit).

## 1. What was there (HEAD 742e46bc)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows. Of the spec's 25 owned entities, 9 existed.

| # | Page | "+ New" | Form chips | Defect |
|---|---|---|---|---|
| 1 | Partner Master | Partner | Partner | No **programme / tier** (FR-PCM-003/004, P0; BRU-PCM-12 version binding). No **named contacts with roles** (FR-PCM-009, P0). |
| 2 | **Recruitment & Onboarding** | **Partner Authorisation** | none | The page listed and captured *brand authorisations*. No onboarding checklist (FR-PCM-007; BRU-PCM-01, H). No enablement/certification (FR-PCM-041). A partner was onboarded with nothing to show it had banking, tax registration, training or portal access. |
| 3 | Brand Relations | Partner Authorisation | **none** (`forms: []`) | No brand obligation (FR-PCM-017), brand audit calendar (FR-PCM-016) or engagement log / brand assessment (FR-PCM-020/021; BRU-PCM-20, H). |
| 4 | **Alliances** | **Partner** (alliance preset) | Partner | No alliance scheme (FR-PCM-030), no eligibility check at intake (FR-PCM-031; BRU-PCM-19, H), no volume commitment (FR-PCM-032). |
| 5 | Referrals | Partner Referral | none | `fix.referral` is the M53 commission record. No referral link/code (FR-PCM-022, P0; T-07), no partner-submitted lead with recorded consent (FR-PCM-023, P0; BRU-PCM-06, H), no attribution window (FR-PCM-024, P0; BRU-PCM-04/05). |
| 6 | Deal Registration | Deal Registration | Deal Registration | No declared channel precedence rule (FR-PCM-029; BRU-PCM-10, H). Conflicts were captured on page 10. |
| 7 | **Resellers** | **Partner** (reseller preset) | Partner | No reseller allocation (FR-PCM-033). |
| 8 | Franchise | Franchise Agreement | Franchise Agreement | No territory / exclusivity (FR-PCM-035; BRU-PCM-16, H). No royalty (FR-PCM-036; BRU-PCM-17: computed from ERP revenue, never declared). |
| 9 | Commercial Terms | Rebate Scheme | Rebate Scheme | No MDF fund ledger (FR-PCM-039, T-09) and no evidenced MDF claim decided by someone other than the allocator (BRU-PCM-11, H). |
| 10 | **Performance** | **Channel Conflict** | none | Captured a conflict docket. The Technical Audits list (the 85% rebate gate) sat on **no page**. |

In summary:
- Pages 2, 4, 7 and 10 captured the wrong record.
- Pages 1, 3, 5, 6, 8 and 9 captured one record and none of the others the spec puts there.
- The node guard fails **42 of 56** checks on HEAD; every page fails.

## 2. What was built

### Backend — `cd_partner` 19.0.0.3.0

**New file `models/fix_partner_capture.py`**, imported last (it extends `fix.partner`, `fix.partner.rebate` and `fix.partner.franchise`). States, stamps, codes, attributions and computed money are guarded (`fix.guarded.mixin`) and move only through actions that check role, evidence and segregation of duties. No new domain events: outcomes go to the chatter.

| Page | Record | What it enforces |
|---|---|---|
| 1 | `fix.partner.programme` + `fix.partner.tier` | Published by a Channel Manager who did not draft it, with entry criteria and at least one tier. Published terms and tiers never change; a change is **Draft New Version** (version + 1), and publishing it supersedes the old one. |
| 1 | `fix.partner` `programme_id` / `tier_id` | Programme must be published and of the partner's type. **BRU-PCM-12**: once the partner is submitted, its programme version is fixed. The tier moves only through **Move to Tier** (a manager, a tier of its programme; notice period recorded). |
| 1 | `fix.partner.contact.role` | Commercial / technical / finance / escalation contacts with a P12 portal scope; one primary per role; a person, not the partner's own party. |
| 2 | `fix.partner.onboarding` | **Generate Onboarding Checklist** creates the six standard steps (idempotent). A step is completed on evidence attached to it; the agreement step needs the M08 agreement linked. A required step is **never waived**; an optional one is waived by another manager with a reason. **BRU-PCM-01**: `action_onboard` refuses while any required step is pending. |
| 2 | `fix.partner.enablement` | Certified on completion date + certificate; a daily cron expires lapsed ones. **FR-PCM-041**: a rebate/MDF accrual is refused while a required certification is missing or expired. |
| 3 | `fix.brand.obligation` | Met only on evidence; a recurring one re-raises itself for the next period; a daily cron flags overdue ones on the authorisation. Frozen once met. |
| 3 | `fix.brand.audit` | Scheduled → findings recorded → 1000FiX response → closed by a manager other than the scheduler; findings freeze once recorded. |
| 3 | `fix.partner.engagement` | Append-only log. A brand's assessment of 1000FiX is inbound and can never be edited (**BRU-PCM-20**). |
| 4 | `fix.alliance.scheme` | Activated by another manager, for an onboarded alliance partner, only when it names the **M11 rule** that applies the benefit (**BRU-PCM-19**). Committed volume vs eligible members served (FR-PCM-032). |
| 4 | `fix.alliance.eligibility.check` | Only under an active scheme inside its validity; an immutable log entry with who checked and how. |
| 5 | `fix.referral.link` | Code generated on save (`secrets.token_urlsafe`, unique, never typed); onboarded partners only; revoked with a reason. |
| 5 | `fix.partner.lead` | **BRU-PCM-06**: refused *before the insert* without recorded consent and its method. **BRU-PCM-04**: partner, link and consent are written once. Converted inside the attribution window (90 days, `cd_partner.lead_attribution_days`) it raises the `fix.referral` that M53 pays; outside it, **no partner is credited** (BRU-PCM-05). Lost needs a reason the partner can see. |
| 6 | `fix.channel.conflict.rule` | Ordered channel precedence per territory. Activated by a Tier 3 officer (CCO) who did not draft it; activating supersedes the territory's previous rule (**BRU-PCM-10**). |
| 7 | `fix.reseller.allocation` | Confirmed by another manager for an onboarded reseller; draws recorded against it never exceed the allocation. |
| 8 | `fix.franchise.territory` | Activation refuses an **exclusive** territory sharing a district with another active territory in an overlapping period (**BRU-PCM-16**). |
| 8 | `fix.partner.franchise` `operating_unit_id`, `royalty_rate`, `marketing_levy_rate` | Agreement terms, frozen on activation. |
| 8 | `fix.franchise.royalty` | **BRU-PCM-17**: basis = verified settlements (`settlement_verified`) of the franchise branch's service orders in the period. Invoices on this estate carry no operating unit; the orders do. Refused without the branch OU or before the period ends. Finance records the M20 invoice. |
| 9 | `fix.mdf.fund` | Allocated by a manager; claimed / approved / paid / balance are **derived** from its claims (T-09). |
| 9 | `fix.mdf.claim` | Submitted on proof of execution within the fund's balance; decided by a manager who neither allocated the fund nor submitted the claim (**BRU-PCM-11**); refusal needs a reason; finance records payment. |

Data: 3 sequences (PLD / MDF / RAL), 2 daily crons, ACLs (plain users read; channel officers create and write; nobody deletes), 8 generated company rules.

### Workspace — `m40.js`, `controllers/a04/m40.py`, `writable.py` (regenerated)

| # | Page | "+ New" | Form chips |
|---|---|---|---|
| 1 | Partner Master | Partner | Partner · Partner Programme · Partner Contact |
| 2 | Recruitment & Onboarding | **Onboarding Step** | Onboarding Step · Partner Enablement · Partner |
| 3 | Brand Relations | Partner Authorisation | Partner Authorisation · Brand Obligation · Brand Audit · Partner Engagement |
| 4 | Alliances | **Alliance Scheme** | Alliance Scheme · Eligibility Check |
| 5 | Referrals | **Partner Lead** | Partner Lead · Referral Link · Referral |
| 6 | Deal Registration | Deal Registration | Deal Registration · Channel Conflict · Channel Precedence Rule |
| 7 | Resellers | **Reseller Allocation** | Reseller Allocation |
| 8 | Franchise | Franchise Agreement | Franchise Agreement · Franchise Territory · Franchise Royalty |
| 9 | Commercial Terms | Rebate Scheme | Rebate Scheme · MDF Fund · MDF Claim |
| 10 | Performance | **Technical Audit** | Technical Audit |

- 17 new lists (each with its lifecycle actions) and 15 new tabbed forms. The programme form edits its tiers in a `lines:` grid; franchise, scheme and MDF fund show their territories, checks and claims read-only.
- Partner list: **Generate Onboarding Checklist** and **Move to Tier**.
- Nav: Partner Master gains Programmes & Tiers and Partner Contacts; a new group "Onboarding & Brand Governance"; Programmes and Commercial gain the new registers. Every list sits on a page (Technical Audits included).
- 18 new served surfaces; the write whitelist was regenerated from the forms.

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m40_capture_buttons.py` (node runs the engine's `fregCreate`/`fregPanels`) | **56/56** now; **42/56 fail on HEAD** (`git archive` of 742e46bc) |
| Live `cd_partner/tests/test_m40_capture_live.py`, as non-admin users on `fix_test_m40` (clone of `fix_test_m36c2`, `-u cd_partner,cd_p03_portal`) | **44/44** |
| Regression after rebasing onto 15b41d7c (peers' M31-M39 work underneath): all cd_partner tests + A04 guards (registry coverage, forms-show-children, sub-module mapping, write whitelist) + estate pages, sub-module create button, picker, A12 whitelist | **862 tests, 0 failures** |
| Mutation check: 16 defects re-introduced one at a time (no consent check, attribution window ignored, onboarding with pending steps, required step waivable, allocator deciding MDF, MDF over balance, exclusive overlap, rebate without certification, published tiers editable, engagement editable, reseller over-draw, typed referral code, self-published programme, check on inactive scheme, typed royalty basis, page 2 back to authorisation) | **16/16 red**; sources restored byte-identical (sha256) |
| Headless Playwright walk, private server on `fix_test_m40` | 10/10 pages show the right "+ New"; **24/24 chips** open their forms; 36/36 new screens render; a precedence rule saved through the UI (draft, precedence computed); **0 console errors** |

Three defects were caught only by running things and fixed: ruff's isort re-ordered `models/__init__.py` (the guard caught it; the file now carries `# isort: skip_file`); the two append-only logs used a guard helper without inheriting the guard mixin (AttributeError on any edit), and a plain employee hit the consent rule before the access check.

## 4. Open — owner decisions (business defaults, not fabricated)

- **Attribution window** 90 days (`cd_partner.lead_attribution_days`) and **royalty/levy cap** 30%: defaults to confirm.
- **Royalty basis**: verified service-order settlements of the branch OU. If finance wants invoiced revenue instead, invoices first need an operating unit (`account_operating_unit` is not installed on fix_real or fix_dev).
- **fix_real has 0 partners, 0 franchises** today, so nothing is migrated; programmes, checklists and rules start empty.
- Not built (P1/P2, not capture gaps): lead→M07 opportunity hand-off (FR-PCM-025), P12 portal provisioning lifecycle (T-11), health-score factor decomposition (FR-PCM-018, BRU-PCM-18), partner hierarchy (FR-PCM-012), partner standing states probation/dormant/exiting (FR-PCM-010).

## 5. Deployment record (19 Nov 2026, owner-approved)

- Landed on `fix/a03-live-data-and-pending-work`: 9b5e1ba2 (fix), be296e7c (load-order pin), fb5647e6 (this report), by compare-and-swap `update-ref` + `read-tree -m -u`; pushed with `fix/m40-capture-buttons`.
- Backups: `_migration/backups/fix_real_pre_m40_capture_2026-11-19.dump` (52.6 MB), `fix_dev_pre_m40_capture_2026-11-19.dump` (48.7 MB).
- Upgrade: my `-u cd_partner,cd_p03_portal` on fix_real collided with the M37 session's concurrent `-u` (serialization error, mine rolled back). M37's run listed cd_partner and cd_p03_portal and finished clean on both DBs; I ran nothing further.
- Gap check right before the restart: no version gap on fix_real (155 modules) or fix_dev (151), no `-u` running.
- One restart at 13:24 for M33, M37 and M40: 8069 = PID 60036 (fix_real), 8090 = PID 83644 (fix_dev). Both answer 200; logs show the modules loaded and no registry errors.
- The old processes ran the two new crons between the `-u` and the restart (failure_count 1, the known benign case). Re-triggered on the new processes: both ran clean, failure_count 0.
- Read-only headless walk (admin, SAVE=0) on **8069 and 8090**: 10/10 pages show the right "+ New", 25/25 chips open their forms, 36/36 new screens render; console errors 0 on fix_dev, 1 transient `ERR_NETWORK_CHANGED` on fix_real.
