# Porting Playbook — phase-by-phase execution runbook (PP1 → PP7)

**Status**: EXECUTION-READY · **Issued**: 2026-10-05 · **Audience**: the engineer starting PP1
**Companions**: task tables in [`01-PORTING-PHASES.md`](01-PORTING-PHASES.md) (normative — *what &
why*); this file is *how & in what order*. Skill guidance per phase is drawn from the
workspace `.agents/skills/` set and is advisory — the roadmap, contracts and token
source remain the only normative sources (standing rule, AUDIT_REPORT §5.2).

---

## 0. Environment pre-flight (once, before any phase — ~10 min)

```powershell
cd 1000_fix_codebase
tasks.ps1 -Target doctor          # 14 checks; all must pass
tasks.ps1 -Target verify-repo     # fitness battery; 0 failures (FF-38 is blocking)
python tooling/design-system/conformance.py      # CFM 1–5 on 231 Service-Teal tokens
python tooling/fitness/check-nav-registry.py     # registry integrity (FF-38 standalone)
python tooling/generators/generate-nav-registry.py   # must print all-counts line (idempotent)
tasks.ps1 -Target test-smoke      # 14/14 against the live Odoo on :8069
```

Standing rules for every phase (from the audits): source only via Write/Edit tools
(Mimosa); no credential literals — env/secret store only; server-side fetches only
http/https with host validation (no localhost/loopback/private targets in shipped code);
commit format `<type>(<scope>): <subject>` ≤ 50 chars; the full battery must be green
before every commit — a red existing gate **blocks** the porting PR (P-13).

**Definition of a phase done**: its exit line in `01-PORTING-PHASES.md` holds, the
battery is green, and `ITERATIONS.md` gains a dated execution record.

---

## PP1 — Platform Scaffolding (start here)

**Entry**: PP0 complete (it is). **Exit**: 11 apps build; api-client + contracts in
place; anti-fixture gate live; CI wired. **Skills**: `erp-devops` (IaC/probes),
`erp-fullstack` (contract-first/TDD), `erp-frontend` (Next.js conventions).

1. **Version currency first (P0): re-verify Payload** — F4 in
   [`06-EXTERNAL-FACTS.md`](06-EXTERNAL-FACTS.md) is the one ⚠ claim. Check
   payloadcms.com/docs for the current 3.7x line against Next 16.3; append the finding
   to `tooling/version-currency/evidence/`. If unsupported → Payload is used ONLY where
   CMS is genuinely needed (customer/marketing), else dropped.
2. **Toolchain**: Node 22 LTS (nvm/windows), `fvm`-pinned Flutter 3.44 (read the 3.44
   migration notes at pin time — F6/F7), Turbopack default (F2), Next-16 checklist:
   `middleware.ts`→`proxy.ts`, Cache Components `'use cache'` (F3) — record in the
   portal template README.
3. **Scaffold `apps/web/`** — 7 Next.js 16.3 apps in dependency order:
   `corporate/` first (PP3's vehicle), then `customer/ analytics/ seller/ brand/
   agent-console/ partner/`. Per app: token-driven hello screen that imports
   `libs/ts/ui/src/tokens/tokens.generated.ts` and renders `#0E7A6E` — proves R2
   generation end-to-end. Bind `127.0.0.1:30xx` (EP-12).
4. **Scaffold `apps/mobile/`** — 4 Flutter apps (`technician/ rider/ auditor/
   customer/`) consuming `libs/dart/fix_ui/theme/tokens.dart`; `flutter analyze` clean.
5. **`libs/ts/api-client`** (PP1-M02): typed client generated from
   `contracts/openapi/*.json`; Keycloak OIDC (realm from compose, synthetic users);
   all calls route via **Kong 3.9** (`http://127.0.0.1:8000` local) — never
   direct-to-Odoo (P-11). Add `contracts/portal/` conventions doc (locale/tenant
   headers).
6. **Populate `contracts/openapi/`** (PP1-M03): move `openapi-w4-portals.json` in;
   author P01/P05/P07/P12 specs **from the existing Odoo controllers** (service-order
   tracking, vendor, marketplace, partner) — each with PS-11 contract tests like the
   W4 suite (`services/portal-contracts/tests`). Add the **PDPA consent endpoints**
   (status/grant/withdraw + DSR submission — backend `fix.consent` exists).
7. **Anti-fixture gate** (PP1-M04): `tooling/fitness/check-no-fixtures.py` — fail on
   fixture/demo/mock data under `apps/*/src`, `addons/**/static`, shipped bundles;
   allow only `**/tests/**`, `**/stories/**`, `db/seeds/**`. Register as **FF-39**
   (blocking) in `tooling/fitness/registry.yaml`.
8. **CI stages** per app: lint/type/test/build + the **P01 < 400 KB/3G** budget check
   from the skeleton onward. Wire `verify-repo` into the pipeline if not already.

**Gate**: `verify-repo` green incl. FF-38/FF-39; every app builds; commit as
`feat(CD-M62-01): PP1 platform scaffolding`.

## PP2 — Admin Operations Portal P03 (R1 OWL)

**Entry**: PP1 (menus read the registry). **Exit**: every registry back-office screen
key resolves in Odoo. **Skills**: `erp-architect` (menu/IA mapping),
`erp-frontend` (workspace patterns), `erp-qa` (E2E).

1. Menus per the binding mapping (`docs/navigation/registry-to-production-mapping.md`):
   module roots under `menu_fix_operations_root`; ≤7 primary sections (NVR-23), deeper
   groups nested; exceptions recorded in the PP2 register.
2. Workspace/grid/record screens per contract A2/A4/A5 — OWL partials under
   `cd_design_tokens` tokens only (CFM-01 will catch literals).
3. Consoles (A7), Report Center linking the 346 registry reports (A10/A11), Tell-ME
   search EN+বাংলা (A13), 4 persona role centers (A1).
4. Extend `check_portal_contract.py` to resolve **registry screen keys → actions**;
   record unbacked keys in the coverage ledger (Gate GP D1 denominator).

## PP3 — First vertical slice: P04 Corporate (R2)

**Entry**: PP1 apps + contracts. **Exit**: P04 fully usable on seed data; the R2
component set extracted to `libs/ts/ui`. **Skills**: `erp-frontend`,
`enterprise_frontend_ux_designer` (guidance lenses only — its omni-nav/cockpit
patterns are options, not requirements).

Shell+OIDC → `/estate` → `/invoices` (display-only money — backend totals) →
`/service-requests` → dark/density/i18n toggles → **template extraction** (the PP5
proof is reusing it unchanged).

## PP4 — Flutter apps (R4)

**Entry**: PP1 skeletons. **Exit**: 4 apps build; offline engine shared (FL-03).
**Skills**: `erp-fullstack`, `erp-qa` (L-suite). Build `libs/dart/fix_offline` per
AR-010 (§4 journal, SP-07 upload-first, §6 disclosure; ARCHITECTURE_STATE §7 semantics
need AR-010 authority-matrix sign-off first — K-12 watch items).

## PP5 — Next.js portal batch (P01, P05, P06-embed, P07, P08, P10, P12)

**Entry**: PP3 template. **Exit**: 12 portals live on seed data. Per-portal table in
`01` §PP5; **P01 carries the contracted < 400 KB/3G budget** and the PDPA consent
dashboard; landing ports from `FX_DEMO.PORTALS` + `LAND_I18N` via the registry.

## PP6 — Data strategy execution

**Entry**: portal surfaces exist. **Exit**: fixture-free, API-only, seed-as-test-data,
migration wired (MIG-02 control totals, MG-005 rehearsal). Run
`check-no-fixtures.py` + the per-portal parity suites (03 §9 real models).

## PP7 — Hardening & Gate GP

**Entry**: all portals. **Exit**: DoD D1–D19 green; **Gate GP verifier**
(`tooling/gate/verify-gate-gp.ps1`) authored and 0 FAIL — registry coverage 100%,
fixture-free, i18n 0-pending, CFM green, budgets met (contracted ones), E2E journeys
green — added beside G0b–G8. **Ratify-or-drop the watch items** (K-10/11/12) with
benchmarks here.

---

## The one-page loop (every phase, every day)

```
read the phase table (01) → pick the next task → implement via Write/Edit
→ its Verify column becomes a command you run → battery green → commit
→ ITERATIONS.md one-line record
```

When in doubt: the registry (`contracts/nav/registry.json`), the token source
(`libs/ts/ui/src/tokens/tokens.json`) and the roadmap are the truth; everything marked
*(non-normative)* is optional; everything marked **[TARGET]** needs ratification at the
phase that builds it.
