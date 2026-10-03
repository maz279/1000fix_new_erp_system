# UX-001-D-01 — the NFR-080 restatement (P04-M07-T10)

| Field | Value |
|---|---|
| CR id | UX-001-D-01 (named in UX-001 §3.2 — raised to the Change Board here) |
| Raised | 2026-10-02 (P04-M07 implementation) |
| Decides | Change Board (GV-003: both statements live until it rules) |
| Built-to | **The stricter reading** — per the roadmap task: "build to the stricter reading until it rules" |

## The two live statements

| Source | Statement |
|---|---|
| `NFR-080` | "a single component library" across the estate |
| `UX-001` §3.2 | "a single component **contract** with multiple runtime realisations" |

## Why this is a real decision and not wording

`UX-001` §3.1 records the constraint that forces the question:

- **Dart (Flutter) cannot consume a CSS custom property.**
- **QWeb cannot consume a React component.**
- **Grafana cannot consume either.**

A requirement that cannot be satisfied will be quietly breached in Wave 1
and then cited as satisfied for thirty-six months. The contract reading
makes the *rendered result* the governed thing (forbidden to differ beyond
`PID-01…PID-07`) and lets each runtime keep native code.

## What we build to (stricter, per the roadmap)

1. One authored token source: `libs/ts/ui/src/tokens/tokens.json` (DTCG
   Format Module 2025.10). No runtime authors a value.
2. One component contract: `docs/design-system/component-contract.md` —
   name, props, slots, states, variants, accessibility semantics, copy
   contract, token bindings.
3. Generated realisations only: SCSS/CSS (R1/R3) and TS (R2) are emitted by
   `tooling/generators/generate-design-tokens.py`; freshness is enforced
   (CFM-02 regenerates and demands byte-identity).
4. One conformance suite: `tooling/design-system/conformance.py`
   (CFM-01 no raw literals · CFM-02 value parity · CFM-03 WCAG 2.2 AA
   contrast · CFM-04 inventory parity · CFM-05 Bengali fit).
5. Declared partial conformance for R5 (P06 dashboards) per UX-001 §3.5 —
   colour full, type partial, component contract not applicable.

## Board outcome (to be completed by the Board)

| Outcome | Consequence |
|---|---|
| Uphold NFR-080 literally | Requires a shared-code library at least one runtime cannot consume — this CR then needs a derogation per runtime |
| Adopt the contract reading | This document closes; current build stands |
