# Component Contract — W1 set (UX-001 §3.2, §8)

> Realisations may differ in code and are **forbidden to differ in rendered
> result** beyond `PID-01…PID-07`. This contract is the single description of
> each component; every runtime realisation (R1 OWL 2, R2 React, R3 QWeb,
> R4 Flutter, R5 partial) implements it identically.

One token source (`libs/ts/ui/src/tokens/tokens.json`), one component
contract (this file), five realisations, one conformance suite
(`tooling/design-system/conformance.py`, CFM-01…CFM-05).

## Contract fields

Every component below declares: **Name · Props · Slots · States · Variants ·
Accessibility semantics · Copy contract · Token bindings**.

---

### status_badge

- **Props**: `status: success | warning | error | urgent | info | neutral | brand | accent` (the eight status tokens, UX-001 §5.4, mapped to MD-027 customer-facing states); `label: string (already localised)`
- **Slots**: none
- **States**: default; each status variant is a state, not a prop combination
- **Variants**: none beyond status
- **Accessibility**: text content carries the full meaning — never colour alone (WCAG 2.2 AA 1.4.1); `role="status"` when the badge announces a change
- **Copy contract**: label comes from MD-027 customer-facing column in the active language; the badge never truncates — Bengali status wording is longer (UX-007 expansion)
- **Tokens**: `$color-status-*`, `$dimension-space-xs/sm`, `$dimension-border-radius-sm`, `$typography-size-xs`

### button

- **Props**: `variant: primary | secondary | danger`; `disabled: boolean`; `loading: boolean`
- **Slots**: `default` (label)
- **States**: default · hover · focus-visible · active · disabled · loading
- **Variants**: primary (brand background) · secondary (surface) · danger (error)
- **Accessibility**: real `<button>`; visible focus ring (`:focus-visible`, WCAG 2.2 AA 2.4.11); minimum target 44×44px (2.5.8); loading is announced (`aria-busy`)
- **Copy contract**: verb-first label ≤ 24 chars English / ≤ 32 chars Bengali; never "OK" alone
- **Tokens**: `$color-status-brand/error`, `$color-text-inverse/disabled`, `$dimension-target-minimum`, `$dimension-space-sm/lg`, `$dimension-border-radius-sm`

### data_table

- **Props**: `columns: [{key, label, numeric?}]`; `rows: Array<Record>`; `zebra: boolean = true`
- **Slots**: per-cell override (`cell-<key>`)
- **States**: default · empty · row-breached (SLA) · loading (skeleton rows)
- **Variants**: zebra on/off; numeric columns render mono
- **Accessibility**: real `<table>` with `<thead>`; `scope="col"`; caption slot (1.3.1); no layout-by-div
- **Copy contract**: column labels localised; dates/amounts via BN-007 formatting (Bengali numerals in `bn`); empty state copy from the UI set, never "No data"
- **Tokens**: `$color-surface-*`, `$color-border-*`, `$typography-size-sm`, `$typography-lineheight-normal`, `$typography-font-mono-family` (numeric cells)

### form_control

- **Props**: `label: string`; `help?: string`; `error?: string`; `required: boolean`
- **Slots**: `control` (the input element)
- **States**: default · focus · disabled · error
- **Variants**: text · select · textarea (input-specific rendering, identical chrome)
- **Accessibility**: `<label for>`-bound; error text linked via `aria-describedby`; error announced (`role="alert"` on the error line); 44px minimum control height (2.5.8)
- **Copy contract**: label + help + error all localised; error copy names the fix, not the failure
- **Tokens**: `$color-border-default/focus`, `$color-text-secondary/disabled`, `$color-status-error`, `$dimension-target-minimum`, `$typography-size-xs/sm`

### panel

- **Props**: `title?: string`; `elevated: boolean = false`
- **Slots**: `default`; `actions`
- **States**: default · elevated (shadow)
- **Variants**: flat surface · secondary surface
- **Accessibility**: `title` renders as a heading with the correct outline level supplied by the host
- **Copy contract**: title localised; never ALL-CAPS in Bengali (Bengali has no case)
- **Tokens**: `$color-surface-secondary/primary`, `$shadow-sm/md`, `$dimension-space-md/lg`, `$dimension-border-radius-md`

---

## Conformance

`py tooling/design-system/conformance.py` — CFM-01 (no raw literals in
realisations), CFM-02 (token value parity across SCSS/CSS/TS + freshness),
CFM-03 (WCAG 2.2 AA contrast on the token pairs), CFM-04 (this inventory
matches realised partials), CFM-05 (Bengali stack first-class + expansion
room).

## R5 partial conformance (P04-M07-T09, declared — not discovered later)

Apache Superset/Grafana (P06 dashboards): colour tokens **full**, type tokens
**partial** (dashboard engines control their own scale), component contract
**not applicable**. Declared exception per UX-001 §3.5.

## Open item — UX-001-D-01 (P04-M07-T10)

The `NFR-080` restatement ("one component library") and UX-001 §3.2 ("one
component *contract*, many realisations") are both live until the Change
Board rules. **We build to the stricter reading** — this contract — until it
does. CR record: `docs/p04/CR-ux001-d01-nfr080-restatement.md`.
