# M65 Multi-Entity & Localisation: sub-module capture audit

**Date:** 18 Nov 2026 · **Area:** A12 · **Workspace fragment:** `cd_p03_portal/static/src/a12/m65.js`
**Backend:** `cd_multi_entity` (new `models/fix_m65_capture.py`), `cd_entity_config` (existing registers),
`cd_p03_portal/controllers/a12/m65.py` (surfaces, write whitelist, reports, KPIs)

The request named "M65b". No module, screen or document in the repository is called M65b; the only
M65 workspace is **M65 · Multi-Entity & Localisation** (`/odoo/operations` → Platform & Technology → M65),
so that is what was audited.

The user reported that not every M65 sub-module page has a relevant data-capture button. That was
right: **five of the six pages failed**. One page had no capture at all, one offered a different
page's record, and five records the specification makes M65 own did not exist anywhere in the code.

## What M65 is supposed to capture

Source: `1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M65_Multi_Entity_Multi_Country_and_Localisation.md`,
§5 (FR-GLO-001..036), §8 (lifecycles), §9 (BRU-GLO-01..20) and §10.1 (24 owned entities).

| # | Sub-module (page) | Spec basis | What a person records there |
|---|---|---|---|
| 1 | Entity Structure | FR-GLO-001, 004, 010; BRU-GLO-14 | Legal entities, and **which country pack (and version) each entity uses**, with its default locale and reporting currency (`fix.entity.jurisdiction`) |
| 2 | Country Packs | FR-GLO-008..012, 016, 017, 019 | Packs, their lines (divisions, holidays, postcodes) and the payment rails per country |
| 3 | Locale Packs | FR-GLO-020, 021, 027 | Locale packs |
| 4 | Jurisdiction | FR-GLO-013, 015, 035, 036; BRU-GLO-02, 05, 13, 19 | The obligation register, **data residency rules** (`fix.jurisdiction.residency.rule`) and the **country onboarding** process (`fix.country.onboarding`) |
| 5 | Translation | FR-GLO-022..025; BRU-GLO-06..08 | **Translations under review** (`fix.translation.entry`) and **Bengali rendering evidence** (`fix.rendering.verification`) |
| 6 | Intercompany ("Audit") | FR-GLO-034; BRU-GLO-17, 18 | Intercompany arrangements with their arm's-length basis, the charges between entities, the approved transfer-pricing rates |


## What the code did (proved on HEAD before the fix)

`cd_p03_portal/tests/test_m65_capture_buttons.py` runs the engine's own `fregCreate` / `fregPanels` in node
over the real registry fragments. Run against the HEAD versions of `m65.js` and `controllers/a12/m65.py`,
**10 of its 26 checks fail, on pages 1, 2, 4, 5 and 6.**

| # | Page | "+ New" on HEAD | Form chips on HEAD | Defect |
|---|---|---|---|---|
| 1 | Entity Structure | + Legal Entity | **none** | No way to say which country pack an entity uses: no assignment record existed (FR-GLO-001/010) |
| 2 | Country Packs | + Country Pack | Country Pack | Lists Pack Lines and Payment Gateways, but offered no capture for either |
| 3 | Locale Packs | + Locale Pack | Locale Pack | Correct |
| 4 | Jurisdiction | + Jurisdiction Rule | Jurisdiction Rule | Only the documentation register. **No data residency rule** (FR-GLO-015, BRU-GLO-13) and **no country onboarding record** (FR-GLO-035, the 12-week governed process with the zero-core-change gate BRU-GLO-02) existed |
| 5 | Translation | **+ Locale Pack** | Locale Pack | Offered page 3's record. Nothing to translate or review: **no translation review record** (FR-GLO-022/024, BRU-GLO-07 "machine translation is not acceptable") and **no rendering verification** (FR-GLO-025) existed |
| 6 | "Audit" | **none** | **none** | Listed intercompany rules with `create: false`. The charges between entities and the approved transfer-pricing rates it governs were not shown at all |

fix_real today (read-only count, 18 Nov): 3 entities, 0 country packs, 2 locale packs (bn_BD, en_US, both
active), 4 jurisdiction rules, 2 payment gateways, 0 intercompany rules/charges/rates.

## What was changed

**Workspace (`m65.js`)**: every page names its captures explicitly.

| # | Page | "+ New" now | Chips now |
|---|---|---|---|
| 1 | Entity Structure | + New Legal Entity | Legal Entity, **Entity Pack Assignment** |
| 2 | Country Packs | + New Country Pack | Country Pack, **Pack Line**, **Payment Gateway** |
| 3 | Locale Packs | + Locale Pack | Locale Pack (unchanged) |
| 4 | Jurisdiction & Expansion | + New Jurisdiction Rule | Jurisdiction Rule, **Residency Rule**, **Country Onboarding** |
| 5 | Translation | **+ New Translation Review** | **Translation Review**, **Rendering Verification** |
| 6 | Intercompany & Transfer Pricing (was "Audit") | **+ New Intercompany Rule** | **Intercompany Rule**, **Intercompany Charge**, **Transfer-Pricing Rate** (M19's own forms: M19 owns the accounting) |

- New lists: Entity Pack Assignments, Data Residency Rules, Country Onboarding, Translation Review,
  Rendering Verification, Intercompany Charges, Transfer-Pricing Rates. Every list and report is on a page
  and in the navigation (regrouped: Structure, Country, Localisation, Jurisdiction & Expansion,
  Translation, Intercompany).
- Row actions: Verify / Retire (residency), Advance / Abandon (onboarding), Approve / Reject
  (translation), and M19's Post & Mirror / Match / Settle and rate Approve / Retire on the intercompany lists.
- The Onboarding (18 fields) and Translation (14) forms are tabbed.
- Two KPI tiles: Translations In Review, Onboardings Open.

**Backend (`cd_multi_entity` 19.0.1.3.0, new `models/fix_m65_capture.py`, spec §10.1):**
- `fix.entity.jurisdiction`: entity ↔ **active** country pack, version recorded at assignment, default
  locale (active), reporting currency. A new assignment of the same pack kind supersedes the current one,
  which stays readable (BRU-GLO-14). Never edited or deleted. Platform Admin only.
- `fix.jurisdiction.residency.rule`: country, data class, must-stay / cross-border / notify, safeguard,
  authority, statute. A contradictory rule is refused. **A second Platform Admin verifies it** with a note
  naming the statute; verifying retires the verified rule it replaces; verified = frozen.
  **Nothing enforces it yet** (M29 does not read it); the screens say so.
- `fix.country.onboarding`: discovery → pack authoring → translation → integration → validation → pilot
  → active, each step refused until its registers hold what it needs (obligations recorded as
  jurisdiction rules for the country, packs named, an active locale, gateways selected). **The pilot is
  refused while "Needs A Core Code Change" is ticked (BRU-GLO-02)**, or while a pack is uncertified
  (BRU-GLO-05) or no residency rule is verified. Activation needs every pack active, a gateway active and
  **a second person** (not the creator or lead). Elapsed weeks are measured against the 12-week target.
- `fix.translation.entry`: a translation of one record field (record type, ID, translatable field: the
  English is read from the record) or one interface string. **A second person approves it**; **machine
  translation is refused** (BRU-GLO-07); a translation whose English changed since is refused as stale.
  Approving a record translation writes it into that record in the locale's language **as the reviewer**,
  so a reviewer who may not edit the record cannot approve it. An approved interface string changes no
  screen by itself (it is the reviewed text for the language file): the report says so.
- `fix.rendering.verification`: locale, target (Android, iOS, Windows, thermal, label, PDF), device,
  test set, result, issues (required on a fail), evidence upload. Never edited or deleted.
- Access: Platform Admin creates (MDM Domain Stewards also submit and review translations and record
  rendering evidence); every internal user reads, none of them writes. Company isolation rules generated by
  `generate-isolation-rules.py` (its rewrites of 7 unrelated modules were reverted).

**Controller (`controllers/a12/m65.py`):** 5 new surfaces and write whitelists (workflow stamps are never
writable). Reports now read the new records: Entity Structure shows each entity's packs in use and default
locale; Translation Completeness shows awaiting review / approved / rejected / stale per locale; Bengali
Support shows per target what renders, fails or is not yet verified; Expansion Assessment adds verified
residency rules, the onboarding step and elapsed weeks, and treats a missing residency rule as a gap.

## Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m65_capture_buttons.py` (engine `fregCreate`/`fregPanels` in node) | **26/26** on the branch; **10/26 fail on HEAD** (pages 1, 2, 4, 5, 6) |
| Static suites: guard + estate page standard (all 67 modules) + A12 write whitelist + M30 guard + i18n separation + M51/M65 dependency isolation | **666 passed, 0 failed** |
| Live ORM suite `cd_multi_entity/tests/test_m65_capture_live.py` on private `fix_test_m65` (`-u all`, clean), as non-admin users through the real `/p03/model/*` endpoints | **30/30** |
| Mutation check: 14 controls broken one at a time | **14/14 caught** (the first sweep found that self-approval was masked by access rights; a direct test was added and kills it) |
| Regression on `fix_test_m65`: all of cd_multi_entity and cd_entity_config, A12 + M19 portal suites, estate page standard | **1,144 passed, 0 failed, 2 skipped** (final run on the finished code: 1,146 collected). The 2 skips are existing M30 tests that need an entity/branch row `fix_test` does not have. Two earlier runs failed only because my own UI-walk rows (a draft `bn_BD` locale pack, a thermal-printer failure) were in the same database; the test helpers now reuse existing data instead of assuming an empty one. |
| UI on private server 8165 (`?debug=assets`) | All 6 pages show the right "+ New" and all 14 chips. Created a Locale Pack (page 3) and a Rendering Verification (page 5) through the forms: the fail-without-issues save was refused with the model's message, the corrected save stored row 33 (`bn_BD`, thermal, fail, verified by the signed-in user) and the Bengali Support report showed "Fails On: Thermal Printer". |

## Not built, and why (spec §10.1 entities with no record)

- **Identifier formats** (FR-GLO-018), **holiday sets with provisional moon-dependent dates** (BRU-GLO-16),
  **address structure/nodes**, **payment method availability**: no screen or validation reads such a
  register yet; Bangladesh address and holiday data travel as country pack lines. Building them is a design
  change to the pack model (nine components, §8.1), not a capture button.
- **Tax / payroll / statutory-report rule registers**: M51 and M56 compute from their own rules; BRU-GLO-12
  says M65 supplies, but moving them is a cross-module change.
- **Fiscal calendars and exchange rates**: M19 owns fiscal periods; Odoo's currency rates and M50's FX
  conversion hold rates.
- **Consolidation structure (ownership %)**: the M19/M54 consolidation book has members but no ownership
  percentage; adding one changes consolidation arithmetic and is M19's decision.
- **Entity lifecycle and one-action provisioning** (FR-GLO-002/005): a provisioning engine, not a capture.
- **Enforcement**: residency rules are not yet read by M29; the jurisdiction rule register remains
  documentation only.

## Deployment

18 Nov 2026, on the user's "Commit and deploy" (not pushed):

- Committed on `fix/m65-capture-buttons` with the pre-commit hooks green (one ruff UP038 fix in the guard).
  Rebased three times as M63, M59, M60 and M61 landed (no shared files), with the static guards re-run on
  the rebased tree: 761/0, then 703/0. Fast-forwarded onto `fix/a03-live-data-and-pending-work` with a
  compare-and-swap `update-ref`: **5c6e3422** (code) and **0f071e5e** (this report).
- Backups: `1000 fix/backups/fix_real_pre_m65_capture_2026-11-18.dump` and `fix_dev_pre_m65_capture_2026-11-18.dump`.
- `-u cd_multi_entity,cd_p03_portal` on fix_real (00:18 UTC) and fix_dev (00:19 UTC; the first try collided
  with a concurrent upgrade by another session and was re-run clean). Both are at cd_multi_entity 19.0.1.3.0
  with the five new tables; the module version gap against the shared checkout is 0 on both.
- 8069 and 8090 were restarted once at 00:20 UTC by the M61 session, covering M59, M60, M61, M63, M64 and
  M65 (8069 = fix_real PID 7840, 8090 = fix_dev PID 71092, both 200 on `/web/login`, no registry failure).
- Checked after the restart, on both databases: all five models are registered and queryable, the
  onboarding sequence exists, all eight page models (including M19's intercompany rule, charge and
  transfer-pricing rate) are in the served surfaces, and the `web.assets_web` bundle carries the M65
  forms and lists (fix_real `d91fc14`, fix_dev `2ecffda`).
