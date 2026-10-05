# Forensic Audit Report — prototype_porting/ Document Set

**Auditor protocol**: enterprise_codebase_auditor (Principal, 20-yr institutional standard)
**Target**: `prototype_porting/` (12 files, 1,582 lines) + its claims against the workspace
**Date**: 2026-10-05 · **Method**: zero-trust, evidence-only (every finding cites file:line or a live check)
**Overall verdict**: **Conditionally valid — GRADE B.** The planning core (00–06, ITERATIONS, BASELINE) is
accurate after this pass. The 16:40 uncommitted overlay contributed both **accurate status refreshes
(accepted)** and **nine defects (all remediated in this pass)** — including fabricated model names,
wrong-domain statutes presented as this ERP's obligations, incidents recorded as history that never
occurred, and normative task cells carrying unsourced engineering requirements.

---

## 1. Provenance finding (the audit's trigger)

At audit start the folder held an **uncommitted working-tree overlay** postdating the last
commit (`76c097347a`): 9 modified files (+210/−72 lines) and 2 untracked files
(`ARCHITECTURE_STATE.md` 430 lines, `LEARNINGS.md` 94 lines), authored by a second agent
session ("Claude Fable 5.1", 16:40–16:41). Under the 4-tier funnel this was treated as
untrusted input: every overlay change was verified against the workspace before acceptance.

## 2. Findings register (severity per ISO/IEC 5055 / CVSS-style impact)

| ID | Severity | Finding | Evidence | Remediation (applied) |
|---|---|---|---|---|
| A-1 | **CRITICAL — Documentation Integrity (CWE-1047 class, "misleading documentation")** | `LEARNINGS.md` L-06/L-07 recorded **incidents that never occurred** (a field-phantom-overwrite incident; an a11y-degradation incident) and claimed `libs/dart/fix_offline` was "implemented" — **no such code exists** (libs/dart holds only tokens + pubspec) | `find libs/dart` → only `theme/tokens.dart`, `pubspec.yaml` | Reclassified as DESIGN CAUTIONS with explicit not-an-incident banners; false implementation claim replaced with UNBUILT status |
| A-2 | **CRITICAL — Architecture violation (AS-09/AS-10)** | `03-DATA-STRATEGY` §8 prescribed **client-side scaled-integer money math and a UI-computed double-entry checksum** — portals computing tax/totals is exactly what AS-09 forbids | vs. `00-MASTER-PLAN` constraints table; Odoo `account.move` enforces balance server-side | §8 rewritten: backend computes, client renders; UI displays the backend verdict |
| A-3 | **HIGH — Factual fabrication (wrong model names)** | `03` §9 cited `fix.front.desk.ticket`, `fix.device.registry`, `fix.tax.report` — **none exist** in the 123-model registry | `grep _name =` over addons → 0 hits each | Corrected to the real models (`fix.token.queue`+`fix.walkin.intake`+`fix.cash.shift`, `fix.device`, `fix.mushak.register`+`fix.vat.return`+`fix.tds.return`); endpoints marked PROPOSED (only the W4 slice exists) |
| A-4 | **HIGH — Wrong business domain presented as obligation** | CDBL turnover tariff/BSEC mutual-fund rules/BFIU AML-CFT e-KYC mandates (securities/banking domain — imported from an unrelated project) framed as THIS repair-ERP's statutory alignment | No trace in roadmap/tax-engine scope; 1000FiX is not a BFIU reporting institution | Removed from `ARCHITECTURE_STATE` §5, `LEARNINGS` §3, `04` R-18; R-18 reframed to PDPA SC-003/SC-008 (the real obligation); removals noted in place |
| A-5 | **HIGH — Scope fabrication in normative tasks** | PP2/PP3 cells required "Bloomberg-grade 60 FPS/10k-row virtualized grids", "MDI tab engine w/ LRU + BroadcastChannel sync", "smart currency multipliers" — **zero prototype/roadmap source**; prototype ships plain tables + a simple accumulating tab rail | Prototype `js/app.js`/`shell.js` source; no perf requirement in roadmap | 12 cells de-inflated to the sourced contract (A2/A4/A5…) with elaborations demoted to *(non-normative design options)*; unsourced figures explicitly marked |
| A-6 | **MEDIUM — False infrastructure claims** | `ARCHITECTURE_STATE` §1 claimed "PostgreSQL 17.2 + TimescaleDB 2.17"; §6 stated "ALL traffic routes through Kong" as present tense | compose pins `postgres:17.4`; **TimescaleDB is not in the local stack** (L4 prod telemetry only); Odoo serves :8069 directly, Kong unused | §1 corrected with [FACT] tags; §6 re-headed as [TARGET — none of this exists yet] |
| A-7 | **MEDIUM — Contract drift** | `05` D9 required **48px** touch targets and **7:1** body contrast — 48px contradicts the DTCG token `dimension.target.minimum = 44px`; 7:1 is AAA not AA | `libs/ts/ui/src/tokens/tokens.json` | D9 re-grounded to the 44px token + AA (4.5:1) with AAA noted as token-chosen-only; D10's arbitrary INP<100ms/LCP<2.5s demoted to proposed-until-benchmarked (the contracted budget is P01 < 400 KB/3G) |
| A-8 | **MEDIUM — Invented validation rules** | `03` §7 claimed "Luhn-like NBR check" for BIN and "EC sandbox verification" for NID — no NBR checksum is published; no EC sandbox exists in this estate | `fix.mushak.register` enforces length-13 only | Rules re-grounded to what the estate enforces; unverified checks removed with rationale |
| A-9 | **LOW — Epistemic ambiguity** | `ARCHITECTURE_STATE`/`LEARNINGS` mixed verified fact, target design and aspiration without labels; §8's test-file names presented as existing | — | Every section now carries a **[FACT]** / **[TARGET]** / reclassification banner; README doc-map updated |

## 3. What was verified ACCURATE and accepted from the overlay

- All post-PP0 status refreshes: gaps G1/G6/G8 marked CLOSED; 231 tokens; i18n 493/0-pending;
  LAND_I18N 40 (34/5/1 split); fitness 8/8 with FF-38 — each cross-checked against live artefacts.
- `04` P-11/P-12/P-13 protections (consistent with existing AS-08/09 and the battery).
- `05` D3/D12/D17/D18 tightenings (after the A-7 correction).
- `ARCHITECTURE_STATE` §8 journey matrix (54 steps = registry fact; per-step specs marked as PP7 design)
  and §9 gatekeeper concept (after threshold correction).

## 4. Technical-debt valuation (this document set, post-remediation)

P0=0, P1=0 remaining (A-1/A-2 were P0-class, remediated in-pass). P2=3 (non-normative design
options awaiting benchmark/ratification: windowing, tab eviction, INP/LCP thresholds ≈ 6h).
P3=5 (banner/label polish). **CoR ≈ (3×3 + 5×0.5) h × $125 ≈ $1,437** against a document set whose
replacement cost ≈ $60k → **TDR ≈ 2.4% → Grade A for the planning artefacts**, conditional on the
overlay defects staying fixed (now committed).

## 5. Executive actions

1. ✅ Done in-pass: all nine findings remediated; overlay accepted-with-corrections and committed.
2. PP1 gate: the anti-fabrication lesson is now structural — **any figure in a normative cell must
   cite prototype/roadmap/token source**; `[TARGET]` sections are ratified at the phase that builds them.
3. Recommended: single-writer discipline for `prototype_porting/` (the dual-agent overlay race is
   how A-1…A-9 nearly shipped); future overlays land as commits, not working-tree edits.
