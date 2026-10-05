# Learnings & Engineering Conventions — Prototype Porting

**Status**: ACTIVE MEMORY — defects L-01…L-05 are historical FACTS; conventions C-01… are forward-looking STANDARDS · **Audited**: 2026-10-05 forensic pass

This document maintains persistent organizational memory. **L-01…L-05 document real, verified defects** from the PP0 implementation. **L-06/L-07 are design cautions reclassified by that audit** — they were originally written as past-tense incident reports, but no such incidents have occurred (no Flutter code and no ported screens exist; `libs/dart/fix_offline` is unbuilt). Conventions C-01… are target standards for PP1+, not descriptions of shipped code.

---

## 1. Defect Catalog & Root Cause Analyses (RCAs)

### L-01: Sass `:root` Custom Property Literal Leak
*   **Symptom**: Served CSS `web.assets_web.min.css` carried `--fix-color-status-brand: $color-status-brand` instead of evaluated hex values. The design tokens were completely unreachable as CSS variables in Odoo.
*   **Root Cause**: The Sass specification treats CSS custom property values (`--var: ...`) as raw text, meaning Sass variables `$var` inside custom property declarations are NOT automatically evaluated unless interpolated with `#{}`.
*   **Resolution**: Generator `generate-design-tokens.py` was refactored to emit literal values directly into the `:root` CSS block instead of referencing `$refs`.
*   **Rule**: Never write `--custom-prop: $sass-var` without explicit interpolation `#{}` or direct literal values. Always verify the served, compiled minified bundle in the browser.

### L-02: Line-Anchored Regex vs AST Parsing for Payload Extraction
*   **Symptom**: Initial regex attempts undercounted `FX_I18N` (reported 44 keys instead of 74) and `LAND_I18N` (reported 17 keys instead of 40).
*   **Root Cause**: Multi-line string concatenation and varied indentation broke simplistic line-anchored regular expressions.
*   **Resolution**: Block-level parsing with strict shape asserts — the generator FAILS on any count drift, and `check-nav-registry.py` independently recomputes every headline. The lesson is not regex-vs-AST but: every parsed count must be asserted against an expected constant so drift is a build failure, not a silent short read.
*   **Rule**: Never use single-line regular expressions to extract structured JSON/JS object trees. Always compute counts programmatically with balanced bracket counters.

### L-03: Menu Governance Drift vs NVR-23 Constraints
*   **Symptom**: `cd_party_master` had drifted to 10 top-level menu sections, violating the NVR-23 maximum constraint of 7 primary sections per workspace.
*   **Root Cause**: Incremental module feature additions during Phases 5–11 added root menu items without checking workspace hierarchy budgets.
*   **Resolution**: Grouped the four governance surfaces under a single "Data Governance" submenu, reducing primary sections to 7.
*   **Rule**: Every module menu must be guarded by `check_portal_contract.py` in CI to prevent hierarchy explosion.

### L-04: Omission of Dark-Mode Ambient Shadow Tokens
*   **Symptom**: In dark mode, card elevations appeared completely flat and lacked ambient separation.
*   **Root Cause**: Token migration initially extracted only color and spacing tokens, omitting `shadow.dark.{sm,md,lg}`.
*   **Resolution**: Added 3 dark shadow tokens to DTCG `tokens.json` (bringing the token count to 231) and regenerated SCSS/CSS/TS/Dart outputs.
*   **Rule**: Conformance suites (CFM-01..05) must audit dark theme elevation pairs alongside contrast triplets.

### L-05: Vendored Source Supremacy Over Online Blog Claims
*   **Symptom**: Web searches reported "Odoo 19 uses OWL 3", leading to potential architecture drift towards alpha APIs.
*   **Root Cause**: Third-party tech blogs conflated upstream development repository `odoo/owl` (which had a 3.0.0 Alpha) with the actual code vendored inside Odoo 19.
*   **Resolution**: Inspected `vendor/odoo/addons/web/static/lib/owl/owl.js`, which conclusively defines OWL version `2.8.4`.
*   **Rule**: The vendored codebase is the final source of truth. When web claims conflict with `vendor/`, the vendored source always wins.

### L-06: Phantom Overwrites in Distributed Field Operations — **DESIGN CAUTION (not an incident; reclassified 2026-10-05)**
*   **The risk**: a technician syncing after hours offline under last-write-wins would silently overwrite dispatcher changes made server-side.
*   **Source**: AR-010 §5 already mandates server-authoritative resolution and §6 conflict disclosure — this caution restates it for implementers.
*   **Status**: `libs/dart/fix_offline` is UNBUILT (libs/dart holds only the generated tokens today). Field-level merge semantics are the PP4 design and must be ratified against AR-010's authority matrix before coding.
*   **Rule**: never last-write-wins on distributed entities; store the base sync snapshot and diff three ways.

### L-07: Silent A11y Degradation during Rapid Screen Porting
*   **Symptom**: Hand-ported prototype form screens lost keyboard focus indicators and shrank mobile touch targets below 40px under tight layout constraints.
*   **Root Cause**: Lack of automated accessibility gatekeepers in the pre-commit battery allowed developers to omit `<label for>` attributes and bypass minimum padding.
*   **Resolution**: Integrated `@axe-core/playwright` CI gatekeeper running across all 823 screen routes, enforcing 0 critical/serious violations, minimum $48\times 48$px mobile touch targets, and modal focus traps.
*   **Rule**: Every screen and component must undergo automated axe-core scanning in CI before merging. Accessibility is a blocking gate, not a post-launch audit.

---

## 2. Engineering Conventions & Defensive Standards

### C-01: The client never does money math (AS-09/AS-10)
*   **Standard**: monetary computation (tax, totals, balancing) is BACKEND-only (Odoo Decimal; AS-10 currency-carrying fields). Portal UIs **render** backend-computed amounts via BN-007 formatters — they never compute `subtotal + vat` in any numeric type.
*   **Display formatting**: locale grouping via `libs/ts/i18n` BN-007 formatters; if a pure display aggregation is ever unavoidable it must use decimal-safe libraries — but the default answer is "the API returns the rounded value".

### C-02: Zero Direct Backend Database Access from Portals
*   **Standard**: Web portals (`apps/web/*`) and mobile apps (`apps/mobile/*`) must NEVER directly import Odoo ORM models, connect directly to PostgreSQL, or write raw SQL.
*   **Convention**: All portal traffic routes through Kong 3.9 API gateway to typed OpenAPI endpoints (`contracts/openapi/*.json`). State mutations flow through `cd_event_outbox` (AS-08).

### C-03: Tab-rail memory management — NON-NORMATIVE design option
*   **Standard**: the prototype's accumulating tab rail is the normative behaviour. IF PP3/PP2 measurably need eviction (dozens of open tabs on low-end hardware): cap active DOM instances (~8) and snapshot to sessionStorage — **the 50 ms rehydration figure is an aspiration to benchmark, not a criterion**.

### C-04: South Asian Currency & Form Masking Formats
*   **Standard**: Format currency using South Asian grouping (`1,23,45,678.00` Lakhs/Crores) and support keyboard multipliers (`100k` = 100,000; `5m` = 5,000,000; `2c` = 20,000,000).
*   **Convention**: Auto-mask statutory identifiers:
    *   13-Digit BIN: `XXXXXXXXXXXXX`
    *   10/17-Digit NID: `XXXXXXXXXX` or `YYYYXXXXXXXXXXXXX`
    *   12-Digit e-TIN: `XXXX-XXXX-XXXX`
    *   (CDBL BO account removed 2026-10-05 — wrong business domain for a repair-services ERP)
    *   Keyboard multipliers (`100k`/`5m`/`2c`) are a UX OPTION for PP3, not a standard.

### C-05: Gateway Ingress Isolation & Identity Propagation
*   **Standard**: All inbound HTTP requests to domain services must carry cryptographically verified JWT identity headers injected by Kong 3.9.
*   **Convention**: Downstream services (Odoo controllers, Superset BI) extract user claims from `X-User-Id`, `X-Tenant-OU`, and `X-Correlation-ID`. Services reject any request missing gateway signature headers.

### C-06: Non-Blocking Background Media Isolate for Mobile Sync
*   **Standard**: High-resolution photo attachments (diagnostic evidence, Mushak challan photos) must NEVER block operational metadata synchronization.
*   **Convention (PP4 target — engine unbuilt)**: `libs/dart/fix_offline` SHALL dispatch binary uploads to a background isolate queue (chunked, integrity-checked) so metadata commands are never blocked by media — restating AR-010 §8 SP-09; the 2-second figure is a design aim to verify in the L-suite.

---

## 3. Statutory Financial & Regulatory Checklist (Bangladesh)

*   [ ] **Income Tax Act 2023 TDS**: 10% (verified 12-digit e-TIN individual), 15% (non-e-TIN individual), 20% (corporate/institutional).
*   (CDBL / BFIU / BSEC items removed 2026-10-05 — securities/banking domain, not this ERP; PDPA SC-003/SC-008 governs identity and consent here.)
