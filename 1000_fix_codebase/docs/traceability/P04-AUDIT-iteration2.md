# P04 Audit — comprehensive post-iteration pass (2026-10-02)

Scope: everything committed through `4a1a75b` (Phase 4 M01–M10 incl. the M06
deepening). Method: four mechanical sweeps over the whole estate, each
negative-tested where a checker is involved, plus targeted research (npm
registry version verification).

## Sweep 1 — compile & parse

Every `.py` under `addons/` compiled; every `.xml` parsed as XML.

## Sweep 2 — view ↔ model field integrity (NEW: `audit-view-integrity.py`, wired into FF-27)

Recursive walk of every `ir.ui.view` arch: field names checked against the
owning model; inline one2many sub-views resolved through comodel relations;
`decoration-*` expressions tokenised (literals stripped); stray chatter tags
flagged. **Negative-tested**: an injected phantom-field view initially
PASSED — the checker was reading `arch.text` (empty) instead of the arch
children, i.e. it had zero coverage while reporting OK. Fixed, re-tested
(fails on the phantom, passes on the clean tree).

## Sweep 3 — formats & determinism (NEW: `audit-repo-formats.py`)

YAML (registry, cd-register, CI, compose, environments, pre-commit), every
repo JSON, every `bn_BD.po` (balanced msgid/msgstr, no empty translations),
and byte-identical regeneration of the design-token and UI-copy generators.

## Sweep 4 — dependency edges, a11y toolchain, security patterns

Every cross-module XML reference has a transitive manifest dependency;
the a11y suite installs and typechecks under `tsc --strict`; no credential
literals outside env access.

## Findings and fixes

| # | Severity | Finding | Fix |
|---|---|---|---|
| 1 | **Blocker** | `cd_rbac_ext/views/fix_rbac_views.xml` was **not well-formed XML** (unescaped `&` in "Security & Access") — module install would crash; never XML-validated since Phase 3 | Escaped `&amp;` |
| 2 | **Blocker** | **10 invalid `<chatter/>` elements** across 10 Phase-3/P04 view files — not Odoo markup; every form carrying it fails at view load | Replaced with the standard `oe_chatter` div (all target models verified to inherit `mail.thread`) |
| 3 | **Blocker** | Device-history sub-view referenced **three nonexistent fields** (`event_date`, `from_partner_id`, `to_partner_id`) — guessed names; the model has `date` and no partner fields | Sub-view corrected to real fields (`date`, `event_type`, `description`, optional `service_order_id`/`technician_id`) |
| 4 | **High** | CI stage 12 ran `npm ci` **without a package-lock.json** — the stage fails on every clean checkout | Lockfile generated from the verified pins and committed; `npm ci` verified locally |
| 5 | **High** | **Version skew in the a11y toolchain**: `@axe-core/playwright` 4.10.2 with `@playwright/test` 1.50.1 fails `tsc --strict` (unpinned `playwright-core` resolves 1.63.0 → `Page` type mismatch) | Aligned on `@playwright/test` 1.63.0 + `overrides.playwright-core` 1.63.0 + `@types/node` 26.6.4 + `typescript` 5.7.3 (all versions verified against the npm registry); `tsc --strict` exit 0 |
| 6 | **Process** | The first view-integrity checker reported **OK with zero actual coverage** (false negative) — caught only because the audit negative-tested the auditor itself | Checker rewritten as a proper recursive descent; negative test now fails as expected |

## Not findings (checked, clean)

- Cross-module menu/action/group references all have dependency edges
  (including the transitive `cd_front_desk → cd_rbac_ext` path).
- YAML/JSON/PO formats all valid; both generators byte-deterministic.
- No credential literals in any authored file (env-only access throughout).
- FF-25 po completeness, FF-23 tests-present, fitness suite, G1 gate, doctor
  check 10 — all re-run green after the fixes.

## Permanent enforcement added

- `audit-view-integrity.py` — now section 6 of **FF-27** (`check_portal_contract.py`):
  view-field integrity joins the portal contract, so the class of defects in
  findings 2–3 cannot recur silently.
- `audit-repo-formats.py` — standalone: run it in any audit or wire it to CI
  (YAML/JSON/PO validity + generator determinism).
