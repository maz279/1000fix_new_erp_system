---
id: BE-002
title: Coding Standards & Style Guide
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Engineering Lead
approver: Chief Architect
standards_basis: >
  PEP 8 · PEP 257 · PEP 484 · Odoo 19.0 coding guidelines · OCA contributing conventions ·
  TypeScript 5 strict · ESLint flat config · Effective Dart · package:flutter_lints ·
  ISO/IEC 25010:2023 maintainability characteristic
traces_to: >
  PGD-000 BE-002 · old-primary-doc Missing-Documents checklist Document 4 · 02-05 §9 ·
  Technology Stack Specification §18.2 · AR-007 §4 (naming), §7 (logic placement) ·
  AR-012 FF-02, FF-10, FF-18…FF-25, FF-32 · AS-04, AS-09, AS-10, AS-11, AS-12
depends_on: BE-004 (where configuration lives) · BE-005 (commit and branch scopes) · AR-007
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P0
needed_by: Now
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-002 — Coding Standards & Style Guide

### Category 07 · Code `BE` · PEP 8 / 257 / 484 · OCA conventions · TypeScript 5 strict · Effective Dart

---

## 1. Purpose

Search the 621-file source estate for the phrase *"coding standard"* and it returns **seven
occurrences across four files**, none of them normative: four in a March 2026 checklist saying the
document is missing, one in each of two technology specifications saying it is inherited, and one in
a Bengali transliteration register. *(Counted 2026-08-18 21:45 (+06). The figure of "four
occurrences" carried by `PGD-000` and `_CATEGORY_OVERVIEW.md` is an undercount — finding `BEA-19`.)* Code review therefore has no objective standard to review against, which
means review becomes a contest of preferences between the reviewer and the author — the least
valuable and most corrosive form it can take.

This document is that standard. It covers the four language stacks the programme actually builds in,
it states rules that a machine can check wherever a machine can check them, and it ships the linter
and formatter configuration that enforces them. Where a rule cannot be machine-checked it says so and
gives the reviewer a specific thing to look for, rather than an adjective.

> **Read `AR-007` first if you write Odoo code.** `AR-007` owns module **structure** — directory
> anatomy, model and table naming, inheritance mechanism, state machines, security artefacts,
> migrations. This document owns **style** — formatting, imports, typing, docstrings, error handling,
> logging, string handling and the tool configuration. Where the two touch, `AR-007` wins and this
> document cites it rather than restating it.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | **Cross-stack rules** (`XS-nn`) that apply in every language — money, time, identifiers, secrets, logging, translation |
| 2 | **Python / Odoo and Python services** (`PYS-nn`) — formatting, imports, typing, docstrings, exceptions, ORM idioms not covered by `AR-007` |
| 3 | **TypeScript / React 19 / Next.js** (`JS-nn`) — inherited from `AGENTS.md` and extended |
| 4 | **Dart / Flutter** (`FL-nn`) — the stack `AGENTS.md` does not cover at all |
| 5 | **SQL and migrations** (`SQL-nn`) |
| 6 | The **committed tool configuration** — Ruff, pylint-odoo, ESLint, Prettier, `analysis_options.yaml`, pre-commit |
| 7 | The mapping from each rule to the mechanism that enforces it |
| 8 | The **review checklist** for the rules no tool can check |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Odoo module anatomy, model/table naming, inheritance | `AR-007` §3–§7 | Structure, not style |
| Repository layout and where config files sit | `BE-004` | This document states the file's content; `BE-004` states its path |
| Branch names, commit format, review process | `BE-003` | Style vs process |
| Test **strategy**, coverage targets, test types | `QA-001`, `AR-007` §9 | This document covers how test *code* is written |
| CI pipeline construction | `PE-004` | §10 lists the gates; `PE-004` builds them |
| UI copy, microcopy and Bengali wording | `project_content/03_UI_Copy…`, `BN-002` | This document governs how a string is *handled*, never what it says |
| i18n key naming | `BN-005` | Cited, not restated |
| Security control design | `SC-005` | This document carries the coding rules that implement it |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer, day one** | The rules their editor and pre-commit hook will enforce before they push |
| Code reviewers | §11 — the checklist of what a machine cannot check, so review spends its time there |
| Implementation vendor | The acceptance standard for delivered source (RFP §5.10) |
| Platform Engineering | §10 — the gates to wire into `PE-004` |
| Solution Architect | The boundary with `AR-007`, and the rules that implement `AS-04`, `AS-09`…`AS-12` |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **PEP 8** | Adopted as the Python baseline, applied by the Ruff formatter (Black-compatible, 88 columns) | **Departure:** line length 88, not PEP 8's 79. Rationale: OCA formats with Black defaults, and code contributed upstream must not be reformatted at the boundary |
| **PEP 257** | Docstring conventions | `PYS-12` narrows *where* docstrings are mandatory rather than requiring them everywhere |
| **PEP 484 / 585 / 604** | Type hints | **Departure:** hints are mandatory in `services/` and `libs/py/`, and **optional on Odoo model methods**. Rationale: `PYS-09` |
| **Odoo 19.0 coding guidelines** | Directory, manifest, model and view conventions | Deferred to `AR-007`, which is the programme's expression of them |
| **OCA contributing conventions** | Black formatting, isort five-block import order, pylint-odoo checks, `[FIX]`/`[IMP]`/`[MIG]` commit tags | Adopted for formatting and linting. Commit tags are `BE-003` `GW-06`'s dual-convention rule |
| **TypeScript 5 strict** | `strict`, `noImplicitAny`, `strictNullChecks`, `noUnusedLocals`, `noUnusedParameters`, `noImplicitReturns` | Adopted verbatim from `AGENTS.md`; extended by `JS-04`, `JS-11` |
| **Effective Dart** | Style, documentation, usage and design guidance | Applied through `package:flutter_lints` plus the additions in §6 |
| **ISO/IEC 25010:2023** | Maintainability — modularity, reusability, analysability, modifiability, testability | This document is the *analysability* and *modifiability* control; `RQ-006` carries the measurable targets |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Document 4 | The original requirement: PEP 8 + Odoo additions, model naming, field naming, import order, pylint-odoo, pre-commit, XML/OWL standards |
| **`../../../AGENTS.md`** §"Code Style Guidelines" | The in-house TypeScript, React/Next.js, file-naming and Tailwind standards, adopted in §5 |
| `02-05` §9 | Pre-commit scope: *"formatting, linting, Odoo-specific checks, secret scanning"* |
| TSS §18.2 | The CI stage list this document's gates must satisfy |
| `AR-007` §4 `N-01`…`N-18` | Naming and model conventions; cited, never restated |
| `AR-012` §4.2 | `FF-02`, `FF-06`, `FF-10`, `FF-18`…`FF-25`, `FF-32` — the checks this document's rules feed |
| `project_content/11_Localisation_Bengali/BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md` | i18n key form and pluralisation, cited by `XS-08` |
| `project_content/11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md` | Numeral and typography handling, cited by `XS-05` |
| `05-06` NFR-062, NFR-090 | Secrets and financial-precision requirements behind `XS-06` and `XS-03` |

### 2.3 What the inherited standard covers, measured

`02-05` §9 states the ERP *"inherits the conventions already established in the repository
(`AGENTS.md`)"*. Measured at 2026-08-18 13:06 (+06):

| Test | Result |
|---|---:|
| Mentions of **Odoo** in `AGENTS.md` | **0** |
| Mentions of **Flutter** / **Dart** | **0** / **0** |
| Mentions of **Python** | **1** |
| `BE-005` items in stacks it does not cover | **270 of 331 — 82%** |
| Technologies named in its stack table that the ERP rejected by name | **2** — Rasa 3.6 (`TD-06`), Timefold (`TD-05`) |
| Internal inconsistency | Stack table names **Drizzle ORM**; build commands and security section name **Prisma** |

**Position.** §5 adopts `AGENTS.md`'s TypeScript, React and file-naming rules substantially
unchanged, because they are sound and already agreed in-house. Nothing else is inherited. The
technology table is not inherited. Recorded as `BEA-09` in `BE-005` §12 and repeated here so a
reader of either document sees it.

---

## 3. Cross-Stack Rules

These bind in **every** language. They exist because each one has a failure mode that is silent, is
expensive, and crosses a language boundary — which is exactly where a per-stack standard loses them.

| # | Rule | Why | Enforced by |
|---|---|---|---|
| **`XS-01`** | **Every file is UTF-8 without BOM, LF line endings.** `.gitattributes` normalises on checkin | Bengali source strings and `.po` files are corrupted silently by a re-encode; a BOM breaks Odoo's XML parser | `.editorconfig`, `.gitattributes`, CI |
| **`XS-02`** | **Identifiers, comments and commit messages are in English.** User-facing strings are never in source (`XS-08`) | The team is bilingual; the codebase has one language so that a reviewer is never blocked by one | Review |
| **`XS-03`** | **Money is a fixed-precision decimal type, never a float, in every language.** Python `Decimal` / Odoo `fields.Monetary`; TypeScript a minor-unit integer or `decimal.js`; Dart `Decimal` | `AS-10`, `DI-01`. A float rounding error in commission settlement across 5,000 sellers is a reconciliation failure that surfaces months later | `FF-22`; Ruff custom rule; ESLint `no-restricted-syntax`; Dart lint |
| **`XS-04`** | **Time is stored and transported as UTC**, ISO 8601 with an explicit offset on the wire. Presentation converts to `Asia/Dhaka`. **No naive local datetime crosses a boundary** | `AS-11`, `DM-08`. Bangladesh is UTC+06 with no DST, which makes the defect invisible in testing and visible only in cross-border data | `FF-23`; review |
| **`XS-05`** | **Numerals are Western Arabic in storage and computation.** Bengali numeral rendering is a presentation concern, applied at the view layer per `BN-006` | A Bengali numeral in a stored amount or an identifier is unparseable by every downstream consumer | Review; `FF-24` adjacency |
| **`XS-06`** | **No secret, credential, key, token or connection password in source, configuration, test fixture, comment or log** | NFR-062, `REPO-26`. A secret in history is a secret forever | `gitleaks` pre-commit **and** full-history CI scan |
| **`XS-07`** | **No personal data and no residency-classified value in a log, a trace, an exception message, an analytics event or an LLM prompt** | `FF-32`, `FF-09`, `TR-16`, NFR-086a. `FF-09` is the one check `AR-012` gives **no exemption route** | `FF-09`, `FF-32`; review |
| **`XS-08`** | **No user-facing string literal in code.** Python `_("…")`; TypeScript through the i18n layer; Dart through ARB. Keys follow `BN-005` | `AS-12`, `DoD-08`, `FF-24`. A hard-coded string cannot reach 100% `bn_BD` and will ship in English to a Bengali-first user | `FF-24`; linter string-literal rules |
| **`XS-09`** | **Every error carries a stable machine-readable code** from the `AP-006` catalogue, plus a translatable human message. Never a bare string | An error a portal cannot branch on is an error a customer cannot be helped with | Review; contract tests |
| **`XS-10`** | **Structured logging only** — key/value or JSON, never string interpolation into a message. Every log line carries the correlation identifier | `OPS-04`. Interpolated logs cannot be queried, and are where `XS-07` breaches hide | Linter; review |
| **`XS-11`** | **No `TODO` without an issue reference.** `# TODO(CD-M15-03, #1421): …` | An unreferenced TODO is technical debt that no register knows about (`BE-009` `DBT-03`) | Linter; CI warning, blocking at wave gate |
| **`XS-12`** | **No commented-out code.** Delete it; the history has it | Commented code is ambiguous to every future reader and is never re-enabled | Review |
| **`XS-13`** | **Every source file that implements a CD item is under a directory carrying that item's issued identifier** (`BE-005`, `REPO-02`) | Traceability from requirement to test terminates on a component that can be located | `REPO-CHK-01` |
| **`XS-14`** | **Public functions and endpoints validate their inputs at the boundary** and never trust a caller, including an internal one | `PS-11` requires an invalid payload posted directly to an API to be rejected; a validation that lives only in a UI form does not satisfy it | `FF-12`; contract tests |
| **`XS-15`** | **No business rule in a view, template, controller or portal component** | `AS-09`, `FF-10`. A rule enforced in a controller binds API callers and not UI users, or the reverse — `DoD-04` exists to catch exactly this | `FF-10`; review |

> **`XS-03` and `XS-04` are the two that will be broken by competent people.** Both look like
> pedantry in a code review and both are unrecoverable in production data. A `Float` money column
> that has been in production for six months cannot be corrected by changing the type; the lost
> precision is not stored anywhere.

---

## 4. Python — Odoo Modules and Services

Applies to `addons/**`, `services/**/*.py` and `libs/py/**`. Read alongside `AR-007` §4, which owns
model, field and method **naming**; this section does not repeat `N-01`…`N-18`.

### 4.1 Formatting and imports

| # | Rule |
|---|---|
| **`PYS-01`** | **Ruff is the single formatter and linter.** It replaces Black, isort, Flake8, pyupgrade and autoflake. Formatting is Black-compatible, so code contributed upstream to OCA arrives already conforming |
| **`PYS-02`** | Line length **88**. Not a target — a limit the formatter applies |
| **`PYS-03`** | Imports are sorted into the **five OCA blocks**, in this order: standard library · third-party · `odoo` · `odoo.addons` · local. Enforced by Ruff's isort rules with an `odoo` known-first-party section |
| **`PYS-04`** | **No wildcard imports.** `from odoo import fields, models` — never `import *` |
| **`PYS-05`** | **No relative import beyond one level.** `from . import models` is correct; `from ...libs import x` is not — that is a dependency, and it is declared, not reached for |
| **`PYS-06`** | Module-level code does work only at import time that is safe at import time. No I/O, no database access, no network |

### 4.2 Typing

| # | Rule |
|---|---|
| **`PYS-07`** | **`services/**` and `libs/py/**` are fully type-hinted** and pass `mypy --strict`. These are ordinary Python and there is no reason to give up type safety in them |
| **`PYS-08`** | **Odoo model methods are hinted where the type is unambiguous** — scalars, `bool`, `dict`, `list` — and are not required to hint recordsets |
| **`PYS-09`** | Rationale for `PYS-08`, stated so it is not read as laziness: an Odoo recordset's type is `self`-dependent and varies by `_inherit` chain; annotating it either lies or requires generics the ecosystem does not use. **Requiring hints here would produce decorative annotations**, which are worse than none because reviewers stop reading them |
| **`PYS-10`** | `Any` requires a comment giving the reason. `# type: ignore` requires the specific error code and a reason |
| **`PYS-11`** | Public function signatures in `libs/py/**` are **stable contracts**. A signature change is a `BE-007` `LX-08` semantic-version event for the library |

### 4.3 Docstrings and comments

| # | Rule |
|---|---|
| **`PYS-12`** | Docstrings are **mandatory** on: every public method of a `services/` or `libs/py/` module; every Odoo model method that implements a business rule; every `_do_transition` guard; every migration script. They are **not** required on trivial getters, `compute_` methods whose `depends` are self-explanatory, or test methods with descriptive names |
| **`PYS-13`** | A docstring states **what and why**, never how. The code states how, and the docstring goes stale the moment it duplicates it |
| **`PYS-14`** | A method implementing a business rule cites the rule identifier: `"""Enforce BRU-SRM-04: an unverified seller may not transact."""` | 
| **`PYS-15`** | A comment explaining a workaround names what it works around and the condition for removing it — the same discipline as `vendor/FORKS.yaml` |

### 4.4 Errors and exceptions

| # | Rule |
|---|---|
| **`PYS-16`** | Odoo business errors raise `UserError` or `ValidationError` with a **translated** message and an `AP-006` code. Never a bare `Exception` |
| **`PYS-17`** | **Never `except: pass`, and never a bare `except:`.** Catch the specific exception; if it is genuinely ignorable, log it at `debug` with the reason |
| **`PYS-18`** | An exception is never used for control flow across a module boundary. Across a boundary, a result type or an explicit status is returned |
| **`PYS-19`** | Service code raises **domain exceptions** defined in the service, translated to HTTP at the edge. A `fastapi.HTTPException` deep in a service couples the domain to a transport |
| **`PYS-20`** | Every external call — HTTP, gateway, bus, ML model — has an explicit **timeout**, an explicit **retry policy** and a declared **fallback**. `IP-05` / NFR-050 require that no service failure blocks a P0 business path, and a call with no timeout blocks it by default |

### 4.5 Odoo-specific style not covered by `AR-007`

| # | Rule |
|---|---|
| **`PYS-21`** | **No raw SQL** except where a documented performance case exists, and then only through `self.env.cr.execute` with **parameters**, never string interpolation. Every instance carries a comment stating the measured reason |
| **`PYS-22`** | **`sudo()` is exceptional and is always commented** with why the privilege escalation is safe. An uncommented `sudo()` fails review. This is the single most common Odoo security defect |
| **`PYS-23`** | No query inside a loop. Read the recordset once and operate on it — the N+1 defect is the dominant Odoo performance failure and it is invisible at demo data volumes |
| **`PYS-24`** | `search()` in a loop, `browse()` on a list built in a loop, and `write()` per record are all `PYS-23` violations. Batch |
| **`PYS-25`** | Business computation that does not need the ORM lives in `services/` inside the module (`AR-007` §3.1) and is unit-tested without a database |
| **`PYS-26`** | Test methods are named `test_<condition>_<expected>` — `test_unverified_seller_cannot_transact`. A test named `test_1` communicates nothing when it fails at 02:00 |
| **`PYS-27`** | Tests use `demo/` data or explicit factories. **No test depends on another test's residue or on execution order** (`AR-007` `T-02`) |

### 4.6 Committed configuration

```toml
# pyproject.toml  (repository root — BE-004 §4)
[tool.ruff]
line-length = 88
target-version = "py312"
extend-exclude = ["vendor/", "**/migrations/**/pre-migrate.py"]

[tool.ruff.lint]
select = [
  "E", "W",      # pycodestyle
  "F",           # pyflakes
  "I",           # isort            → PYS-03
  "UP",          # pyupgrade
  "B",           # bugbear
  "S",           # bandit           → XS-06 support
  "T20",         # no print()
  "SIM", "C4", "RET", "PTH",
  "ERA",         # commented-out code → XS-12
  "TRY",         # exception antipatterns → PYS-17, PYS-18
  "LOG", "G",    # logging correctness → XS-10
]
ignore = [
  "E501",        # line length is the formatter's job, not the linter's
  "S101",        # assert is permitted in tests only; see per-file-ignores
]

[tool.ruff.lint.per-file-ignores]
"**/tests/**" = ["S101", "PLR2004"]
"**/__manifest__.py" = ["B018"]

[tool.ruff.lint.isort]
known-first-party = ["odoo"]
section-order = ["future", "standard-library", "third-party", "odoo", "odoo-addons", "first-party", "local-folder"]

[tool.ruff.lint.isort.sections]
"odoo" = ["odoo"]
"odoo-addons" = ["odoo.addons"]

[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "parents"   # PYS-05

[tool.mypy]
python_version = "3.12"
strict = true
files = ["services", "libs/py"]     # PYS-07 — Odoo addons excluded by PYS-08
```

```ini
# .pylintrc-odoo — Odoo-specific checks Ruff does not implement
[MASTER]
load-plugins = pylint_odoo
[ODOOLINT]
manifest_required_authors = 1000FiX Services Limited
manifest_required_keys = license,summary,version,depends,author
manifest_version_format = ^19\.0\.\d+\.\d+\.\d+$
valid_odoo_versions = 19.0
[MESSAGES CONTROL]
disable = all
enable =
  manifest-required-key, manifest-required-author, manifest-version-format,
  missing-readme, invalid-commit, resource-not-exist, xml-syntax-error,
  sql-injection, translation-required, translation-field,
  no-write-in-compute, method-compute, method-search, method-inverse,
  attribute-string-redundant, external-dependency-not-in-manifest,
  license-allowed, development-status-allowed
```

> **`manifest_version_format` encodes an `AR-007` defect this document does not have the authority to
> fix, and names.** `AR-007` §3.2's manifest example comments `"19.0.1.0.0"` as
> `<odoo>.<major>.<minor>.<patch>.<build>` — five components. OCA's convention is
> `{odoo_version}.{major}.{minor}.{patch}`, where `odoo_version` is the two-part series `19.0`. There
> is no build component. The regex above implements the OCA reading. Raised as finding `BEA-10`,
> referred to `AR-007` v1.1.

---

## 5. TypeScript, React 19 and Next.js

Applies to `apps/web/**` and `libs/ts/**`. **Adopted from `AGENTS.md` §"Code Style Guidelines"**,
which is retained substantially unchanged and extended where the ERP context adds a constraint.

### 5.1 Inherited unchanged from `AGENTS.md`

| # | Rule |
|---|---|
| **`JS-01`** | `tsconfig` strict set: `strict`, `noImplicitAny`, `strictNullChecks`, `noUnusedLocals`, `noUnusedParameters`, `noImplicitReturns` |
| **`JS-02`** | Interfaces `PascalCase`; types `PascalCase`; props `ComponentNameProps`; **`const` objects with `as const` instead of `enum`** |
| **`JS-03`** | Never `any` without justification; always declare function return types; prefer `interface` for object shapes and `type` for unions |
| **`JS-04`** | Import grouping: React · Next.js · third-party · internal UI · types |
| **`JS-05`** | Server Components by default; `'use client'` only for interactivity, browser APIs or hooks; client components kept as small as possible |
| **`JS-06`** | File naming: components `PascalCase.tsx`; hooks `useThing.ts`; utilities `camelCase.ts`; types `thing.types.ts`; routes `kebab-case/page.tsx` |
| **`JS-07`** | Tailwind utilities only; `cn()` for conditional classes; mobile-first; design tokens from `tailwind.config.ts`; **no inline `style`** |

### 5.2 Added for the ERP context

| # | Rule | Why |
|---|---|---|
| **`JS-08`** | **All ERP data access goes through the generated client in `libs/ts/api-client`**, which is generated from `contracts/openapi`. No hand-written `fetch` to an ERP endpoint | The contract is the interface (`REPO-06`); a hand-written call silently survives a contract change |
| **`JS-09`** | **No money arithmetic in TypeScript.** Amounts arrive computed, as minor-unit integers with an explicit currency, and are formatted for display only | `XS-03`. JavaScript's `Number` is a float; `0.1 + 0.2` is the canonical demonstration |
| **`JS-10`** | **Every user-facing string is an i18n key** per `BN-005`. Bengali is a first-class locale, not a translation pass | `XS-08`, `AS-12` |
| **`JS-11`** | **No business rule in a component**, including validation that decides an outcome. Components render state and call actions | `XS-15`, `AS-09`, `FF-10` |
| **`JS-12`** | Critical customer paths respect the **< 400 KB first-load** budget; a route that exceeds it fails the build | `FF-11`, NFR-081, `PS-07` |
| **`JS-13`** | Every interactive element is **keyboard operable**, and every drag interaction has a keyboard and single-pointer alternative | WCAG 2.2 SC 2.5.7; TSS §25.3.8 requires it for the P03 dispatch board specifically; `FF-35` blocks on axe-core violations |
| **`JS-14`** | Server components never receive a secret through props, and never serialise one into the client payload | `XS-06` |
| **`JS-15`** | Errors surfaced to a user render the `AP-006` code alongside the translated message, so support can act on it | `XS-09` |

### 5.3 Committed configuration

```js
// eslint.config.mjs — flat config
import js from '@eslint/js';
import ts from 'typescript-eslint';
import next from '@next/eslint-plugin-next';
import a11y from 'eslint-plugin-jsx-a11y';

export default ts.config(
  js.configs.recommended,
  ...ts.configs.strictTypeChecked,
  { plugins: { '@next/next': next, 'jsx-a11y': a11y },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',            // JS-03
      '@typescript-eslint/explicit-function-return-type': 'error',
      '@typescript-eslint/no-floating-promises': 'error',
      'jsx-a11y/no-noninteractive-element-interactions': 'error', // JS-13
      'no-restricted-syntax': ['error',
        { selector: "BinaryExpression[operator=/[*/]/][left.name=/(amount|price|total|Amount)$/]",
          message: 'XS-03/JS-09: no money arithmetic in TypeScript.' }],
      'no-restricted-imports': ['error',
        { patterns: [{ group: ['**/vendor/**'], message: 'BE-004 REPO-03.' }] }],
      'no-restricted-globals': ['error',
        { name: 'fetch', message: 'JS-08: use libs/ts/api-client.' }],
    } },
);
```

Prettier is configured with defaults plus `singleQuote: true` and `semi: true`, matching `AGENTS.md`.
Prettier formats; ESLint does not — the two do not overlap.

---

## 6. Dart and Flutter

Applies to `apps/mobile/**` and `libs/dart/**`. **`AGENTS.md` carries nothing for this stack**, and
the three field applications are, per TSS §25.5 item 2, the hardest deliverable in the programme.

### 6.1 Rules

| # | Rule | Why |
|---|---|---|
| **`FL-01`** | `package:flutter_lints` is the **baseline**; `very_good_analysis` is layered over it for `libs/dart/**` and the three offline applications | The offline engine is where a lint-level defect becomes lost field data |
| **`FL-02`** | The Flutter SDK is **pinned via `fvm`** and committed in `.fvmrc`. No developer builds on an unpinned SDK | `REPO-17`. Three applications built on three SDK patch levels produce three different offline behaviours |
| **`FL-03`** | **All offline persistence goes through `libs/dart/fix_offline`.** No application opens its own database, defines its own queue, or writes its own conflict resolution | `ADR-024` mandates one offline engine across three applications. Three copies is the single most likely structural defect in the programme |
| **`FL-04`** | The sync journal is **append-only**; no code path mutates or deletes a journal entry | TSS §25.5 item 2; `AR-010`. A mutable journal cannot prove what the device knew |
| **`FL-05`** | Every mutating operation carries a **client-generated idempotency key**, persisted with the operation before any network attempt | A retry after a lost response must not double-apply. `AR-010` requires zero double-application |
| **`FL-06`** | **No money arithmetic on device.** Amounts are computed server-side; the device displays and captures | `XS-03` |
| **`FL-07`** | All strings via ARB; **`bn_BD` is the primary locale in development**, not an afterthought. A developer runs the app in Bengali | `AS-12`. An interface designed in English and translated late has layout defects that only appear in Bengali |
| **`FL-08`** | Widget files contain layout; logic lives in the state layer; data access lives in a repository. **No network or database call in a `build()` method** | Testability, and rebuild storms on a 3 GB Android device |
| **`FL-09`** | Every asynchronous operation is **cancellable and lifecycle-aware**. A response arriving after disposal never touches state | The dominant crash class in offline-first mobile |
| **`FL-10`** | **Battery and data budgets are respected in code**, not only in design: no unbounded background polling; sync is batched, backoff is exponential with jitter | The device is a technician's working tool for a ten-hour shift in the field |
| **`FL-11`** | No residency-classified value is persisted on a device, cached in an image, or written to a crash report | `FF-09`, NFR-086a. A phone is not a controlled environment |
| **`FL-12`** | `const` constructors wherever possible; `dispose()` on every controller, stream subscription and animation | `flutter_lints` enforces; listed because leaks on long-running field sessions surface as "the app gets slow after lunch" |

### 6.2 Committed configuration

```yaml
# analysis_options.yaml — apps/mobile/** and libs/dart/**
include: package:very_good_analysis/analysis_options.yaml

analyzer:
  language:
    strict-casts: true
    strict-raw-types: true
  errors:
    missing_required_param: error
    missing_return: error
    invalid_use_of_protected_member: error
    avoid_dynamic_calls: error
  exclude: [ "**/*.g.dart", "**/*.freezed.dart" ]

linter:
  rules:
    prefer_const_constructors: true          # FL-12
    cancel_subscriptions: true               # FL-09
    close_sinks: true                        # FL-09
    avoid_print: true                        # XS-10
    always_declare_return_types: true
    prefer_final_locals: true
    use_build_context_synchronously: true    # FL-09
```

> **Open dependency.** `D-027` — Flutter or React Native — is undecided (TSS §25.2.5, `AR-013`,
> `BE-005` `BEA-07`). Five `BE-005` items are declared React Native or unqualified "mobile
> application" against three declared Flutter. **This section covers Flutter only.** If `D-027`
> settles on two frameworks, this document requires a `JS`-family section for React Native and
> `BE-001` requires a second mobile toolchain. That cost is a reason to settle `D-027`, not a reason to
> pre-write the section.

---

## 7. SQL and Migrations

Applies to `db/migrations/**` and any raw SQL permitted under `PYS-21`. Odoo schema is managed by the
ORM; this section governs everything the ORM does not own — TimescaleDB, ClickHouse and Odoo
migration scripts.

| # | Rule | Why |
|---|---|---|
| **`SQL-01`** | Keywords upper-case, identifiers `snake_case` lower-case, one column per line in DDL | Diff readability; a migration is reviewed as text |
| **`SQL-02`** | **Every statement is parameterised.** String interpolation into SQL fails review and fails `pylint-odoo`'s `sql-injection` check | The one defect class that is both trivial to avoid and catastrophic |
| **`SQL-03`** | Migrations are **forward-only**; a rollback is a documented procedure, not a `down` script | `MG-01`, `OPS-07`. Cited from `AR-007` §10 rather than restated |
| **`SQL-04`** | Migrations are **idempotent and restartable** — `IF NOT EXISTS`, guarded backfills | `MG-04`. A migration killed halfway must be safely re-runnable |
| **`SQL-05`** | **Add a column before code uses it; drop a column only after no code references it — two releases, never one** | `MG-02`, NFR-008 zero downtime. Old and new pods run simultaneously during a rolling deploy |
| **`SQL-06`** | Every index is created `CONCURRENTLY` in production migrations | A plain `CREATE INDEX` takes an `ACCESS EXCLUSIVE` lock and stops the branch estate |
| **`SQL-07`** | A backfill touching more than 100,000 rows runs **batched, outside the deployment window**, as a background job with progress reporting | `MG-05` |
| **`SQL-08`** | No migration reads or writes a residency-classified value directly; it goes through the residency service | `MG-07`, `FF-09` |
| **`SQL-09`** | Every migration is dry-run against a **production-sized clone** before promotion, and the run time is recorded | `MG-03`; `DoD-16` rollback rehearsal |
| **`SQL-10`** | Monetary columns are `NUMERIC`, never `float8`/`double precision`. Money columns carry an explicit currency column | `XS-03`, `DI-01` |

---

## 8. Test Code

Test code is production code and this document applies to it, with three additions.

| # | Rule |
|---|---|
| **`XS-16`** | **A flaky test is a defect.** It is fixed or deleted, never re-run until green (`AR-007` `T-03`) |
| **`XS-17`** | Every **H**-class business rule has a **negative** test, exercised through **both** the UI path and the API path (`DoD-04`) |
| **`XS-18`** | Concurrency behaviour declared in the SDD has a test that exercises the contention (`AR-007` `T-04`) — a reservation race, a duplicate webhook, two dispatchers assigning one technician |

> **`XS-18` is the rule most often skipped and the one with the highest return.** All three examples
> are reproducible in a test and invisible in single-user manual testing, and all three are how a
> field service system loses money quietly.

---

## 9. Pre-Commit

One configuration, committed at the repository root, running the same tools CI runs (`REPO-20`).

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks: [ { id: ruff, args: [--fix] }, { id: ruff-format } ]      # PYS-01
  - repo: https://github.com/OCA/pylint-odoo
    hooks: [ { id: pylint-odoo, files: ^addons/ } ]                  # §4.6
  - repo: https://github.com/gitleaks/gitleaks
    hooks: [ { id: gitleaks } ]                                      # XS-06
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - { id: end-of-file-fixer }
      - { id: mixed-line-ending, args: [--fix=lf] }                  # XS-01
      - { id: check-merge-conflict }
      - { id: check-added-large-files, args: [--maxkb=512] }         # REPO-30
  - repo: local
    hooks:
      - { id: eslint,  entry: pnpm -w exec eslint --max-warnings=0, types: [ts] }
      - { id: prettier, entry: pnpm -w exec prettier --write, types_or: [ts, tsx, json, css] }
      - { id: dart-analyze, entry: fvm dart analyze --fatal-infos, types: [dart] }
      - { id: no-vendor-edit, entry: tooling/scripts/check-vendor-clean.sh }   # FF-03
      - { id: cd-id-check, entry: tooling/scripts/check-cd-id.py }             # FF-16
```

| # | Rule |
|---|---|
| **`XS-19`** | Pre-commit is installed by `make bootstrap` and is **not optional**. CI re-runs every hook, so bypassing locally only moves the failure later |
| **`XS-20`** | `--no-verify` is permitted only for a `hotfix/*` branch under `BE-003` `GW-11`, and the next commit on that branch must pass |

---

## 10. Enforcement Map

Every rule resolves to a mechanism. Rules with no mechanism are listed as such rather than presented
as enforced.

| Mechanism | Rules |
|---|---|
| **Formatter** (Ruff, Prettier, `dart format`) | `PYS-01`, `PYS-02`, `SQL-01`, `JS-07` |
| **Linter** (Ruff, ESLint, `dart analyze`) | `PYS-03`…`PYS-06`, `PYS-17`, `PYS-18`, `JS-01`…`JS-04`, `JS-08`, `JS-09`, `FL-01`, `FL-08`, `FL-09`, `FL-12`, `XS-10`…`XS-12` |
| **pylint-odoo** | Manifest completeness, `sql-injection` (`SQL-02`), `translation-required` (`XS-08`), compute-method correctness |
| **Type checker** (`mypy --strict`, `tsc`) | `PYS-07`, `PYS-10`, `PYS-11`, `JS-01`, `JS-03` |
| **Secret scan** (`gitleaks`, full history) | `XS-06` |
| **Fitness function** (`AR-012`) | `XS-03`→`FF-22`, `XS-04`→`FF-23`, `XS-07`→`FF-09`/`FF-32`, `XS-08`→`FF-24`, `XS-13`→`FF-16`, `XS-14`→`FF-12`, `XS-15`→`FF-10`, `JS-12`→`FF-11`, `JS-13`→`FF-35` |
| **Contract test** | `XS-09`, `XS-14`, `JS-08` |
| **Coverage gate** | `XS-17` — ≥ 80%, 100% on financial and tax paths (`DoD-03`) |
| **Review only — no tool exists** | `XS-02`, `XS-05`, `PYS-13`…`PYS-15`, `PYS-19`, `PYS-20`, `PYS-22`…`PYS-25`, `FL-03`…`FL-07`, `FL-10`, `FL-11`, `XS-18`, `SQL-05`, `SQL-07` |

> **Twenty-two rules are review-only, and four of them are the most consequential in the document** —
> `PYS-22` (`sudo()` justification), `PYS-20` (timeout, retry, fallback), `FL-03` (one offline engine)
> and `SQL-05` (two-release column lifecycle). §11 exists so that review spends its attention on
> these rather than on formatting a tool has already fixed.

---

## 11. The Review Checklist

`BE-003` owns the review **process**. This is the content: what a reviewer looks for once the
machine-checkable rules are already green.

| # | Question | Rule |
|---|---|---|
| 1 | Is every `sudo()` commented with why the escalation is safe? | `PYS-22` |
| 2 | Does every external call declare a timeout, a retry policy and a fallback? | `PYS-20` |
| 3 | Is there a query inside a loop? | `PYS-23`, `PYS-24` |
| 4 | Is any business rule sitting in a view, controller, template or component? | `XS-15`, `FF-10` |
| 5 | Does an H-class rule change carry a **negative** test through both UI and API? | `XS-17` |
| 6 | Could this change put a personal or residency-classified value in a log, trace, prompt or crash report? | `XS-07` |
| 7 | Does a schema change add before use and drop after disuse — two releases? | `SQL-05` |
| 8 | Does any mobile change introduce a second offline store, queue or conflict resolver? | `FL-03` |
| 9 | Is money handled as a decimal end to end, including in transport? | `XS-03` |
| 10 | Does every new user-facing string have a `BN-005` key, and is `bn_BD` populated? | `XS-08` |
| 11 | Does the change touch a contract in `contracts/` without a version decision? | `REPO-06`, `LX-08` |
| 12 | Is there a `TODO` without an issue, or commented-out code? | `XS-11`, `XS-12` |

> **A review that finds nothing on this list and comments on formatting has been wasted.** Formatting
> was decided by `PYS-01` and applied before the code was pushed.

---

## 12. Adoption

The estate has no code yet, which makes adoption unusually cheap and unusually easy to get wrong by
turning everything on before anything is written.

| Step | Action | When |
|:--:|---|---|
| 1 | Commit all configuration in this document at repository initialisation (`BE-004` §13 step 7) | **W0** |
| 2 | Enable every hook and gate as **Blocking from the first commit** | **W0** |
| 3 | Run `BE-001` §7's verification: a scaffolded module passes every gate with no edits | W0 |
| 4 | Review the review-only list (§11) at the W1 gate against actual review comments — a rule nobody has ever commented on is either universally obeyed or universally ignored | W1 gate |
| 5 | Re-verify external tool versions and rule sets | Every wave gate (`PG-M4`) |

> **Step 2 is only affordable because there is no legacy code.** `AR-012` §5.2's promotion rule
> exists for checks with a non-zero existing violation count — `FF-13` at 953, `FF-14` at 55,
> `FF-27` at 34. **Style rules have a violation count of zero today and will never again be as cheap
> to enforce.**

---

## 13. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-002-D-01` | Python toolchain | (a) Black + isort + Flake8 + pylint (OCA's set); (b) **Ruff** + pylint-odoo | **(b)** | Ruff is Black-compatible, so upstream contributions are unaffected; one tool, one config, materially faster feedback | pylint-odoo is retained separately for Odoo-specific checks Ruff does not implement |
| `BE-002-D-02` | Line length | (a) PEP 8's 79; (b) **88** | **(b)** | OCA formats with Black defaults; 79 would reformat every upstream contribution at the boundary | A documented departure from PEP 8 |
| `BE-002-D-03` | Typing in Odoo models | (a) `mypy --strict` everywhere; (b) **strict in services and libs, pragmatic in addons** | **(b)** | Recordset types are `self`-dependent; strictness there yields decorative annotations | `PYS-08`, `PYS-09` state the boundary explicitly so it is not read as inconsistency |
| `BE-002-D-04` | TypeScript standard | (a) Write fresh; (b) **adopt `AGENTS.md`** | **(b)** | Already agreed in-house, sound, and reduces divergence with the `CON-03` platform | Only the code-style section is inherited; the technology table is not |
| `BE-002-D-05` | Dart lint set | (a) `flutter_lints` alone; (b) **`flutter_lints` + `very_good_analysis` on offline code** | **(b)** | The offline engine is where a lint-level defect becomes lost field data | Stricter rules on the code that is hardest to change later |
| `BE-002-D-06` | Enforcement timing | (a) Warning then promote; (b) **Blocking from commit one** | **(b)** | Zero existing violations; the promotion rule exists for retrofit, and this is not a retrofit | No grace period; step 3 of §12 proves the gates pass on scaffolded code first |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | `D-027` — one mobile framework or two? A second framework doubles §6 | CTO | **W0** | §6 completeness; `BE-001` toolchain |
| `Q-02` | Does `AR-007` §3.2's five-component manifest version comment stand, or does OCA's four-component form (`BEA-10`)? | Solution Architect | **W0** | `manifest_version_format` regex; every manifest |
| `Q-03` | Is `AGENTS.md` re-issued for the ERP repository, or does the ERP carry its own? | Engineering Lead | W0 | `BE-004` §4 root file; contributor onboarding |
| `Q-04` | Does the `CON-03` portal platform adopt these rules, or does the boundary carry two standards? | Chief Architect / portal owner | W1 | `libs/ts/` sharing; `Q-05` in `BE-004` |
| `Q-05` | Who owns the `AP-006` error-code catalogue's technical form, given it is currently content? | Integration Lead | W1 | `XS-09`, `JS-15` |

---

## 15. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every stack in `BE-005` §9.1 has a rule set | Python, TypeScript, Dart, SQL — covering 331 of 331 items, subject to `Q-01` |
| `AC-02` | Every rule names its enforcement mechanism, or is explicitly listed as review-only | §10 |
| `AC-03` | Configuration is committed and runnable, not described | §4.6, §5.3, §6.2, §9 |
| `AC-04` | The boundary with `AR-007` is stated and no rule is duplicated across the two | §1 preamble; `AR-007` `N-01`…`N-18` cited, never restated |
| `AC-05` | Review-only rules are collected into a usable checklist | §11 |
| `AC-06` | Every external tool and standard carries a verification date | §17 |
| `AC-07` | Rules trace to the architecture standards they implement | `AS-04`, `AS-09`…`AS-12`; `FF-*` map in §10 |

**Definition of done.** Complete when every criterion is met, §12 step 3 has passed on a scaffolded
module in CI, `PGD-000`'s `BE-002` row moves to ✅ with a fresh timestamped enumeration, and the
approver has signed.

---

## 16. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `AR-007` §4, §7, §9, §10 | Structure and naming this document defers to |
| Upstream | `AR-012` §4.2 | The fitness functions these rules feed |
| Upstream | `../../../AGENTS.md` | The TypeScript standard adopted in §5.1 |
| Upstream | `BN-005`, `BN-006` | i18n keys and numeral handling cited by `XS-05`, `XS-08` |
| Upstream | `BE-004` | Where every configuration file lives |
| Downstream | `BE-003` §7 | The review checklist §11 feeds the PR template |
| Downstream | `BE-006` | Component scaffolds ship conforming code |
| Downstream | `PE-004` | Implements the gates in §10 |
| Downstream | `QA-005` | The automation framework assumes §8's test conventions |
| Lateral | `../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-06_*` | NFR-062, NFR-090 |
| Lateral | `../../project_content/15_Integration_and_Developer_Content/AP-006_*` | The error-code catalogue `XS-09` requires |

---

## 17. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-001`](BE-001_Development_Environment_Setup_Guide.md) ·
[`BE-003`](BE-003_Git_Workflow_Branching_and_Code_Review_Standard.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-005`](BE-005_Custom_Development_CD_Master_Register.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
`../02_Architecture_and_Design/AR-007_Odoo_Module_Architecture_and_Code_Structure_Standard.md` ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md`

**Workspace**
`../../../AGENTS.md` §"Code Style Guidelines" ·
`../../old-primary-doc/1000FiX_ERP_Missing_Implementation_Documents.md` §3 Document 4 ·
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §9 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §18.2, §18.6 ·
`../../project_content/11_Localisation_Bengali/BN-005_i18n_Key_Placeholder_and_Pluralisation_Rules.md` ·
`../../project_content/11_Localisation_Bengali/BN-006_Bengali_Typography_Font_and_Numeral_Standard.md`

**External standards and sources** *(all verified 2026-08-18)*
PEP 8, PEP 257, PEP 484 — Python Software Foundation ·
Ruff — linter and formatter, Black-compatible, superseding Flake8/isort/Black/pyupgrade ·
`OCA/pylint-odoo` — Odoo plugin for Pylint ·
OCA contributing conventions, `OCA/odoo-community.org` `CONTRIBUTING.rst` — module naming, manifest
keys, `{odoo_version}.{major}.{minor}.{patch}` version scheme, five-block import order, Black + isort
+ pre-commit ·
TypeScript 5 compiler options · ESLint flat configuration · `typescript-eslint` strict-type-checked ·
Effective Dart · `package:flutter_lints` · `very_good_analysis` ·
WCAG 2.2 SC 2.5.7 (dragging movements) ·
ISO/IEC 25010:2023 — product quality model

---

## 18. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. 20 cross-stack, 27 Python, 15 TypeScript, 12 Dart and 10 SQL rules; committed tool configuration; enforcement map; review checklist. Raises `BEA-09`, `BEA-10` | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-002` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
