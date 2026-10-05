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

---

# Part 2 — The 13 Screen Archetypes (PP0-M04-T01)

Ported from the verified prototype (`Front_end/js/app.js`, 8,566-route crawl).
An archetype is a *screen-level* contract: it composes the Part-1 components
plus layout tokens into a pattern every realisation (R1 OWL, R2 Next.js,
R4 Flutter) must render identically beyond PID-01…PID-07. Field format
matches Part 1: **Props · Slots · States · Variants · Accessibility · Copy
contract · Token bindings**. The CFM-04 inventory rule applies to Part-1
components only; archetypes are realised as compositions, so their headings
deliberately do not match the inventory regex.

### A1 · Role Center (home)

- **Props**: `persona` (registry personas: super/ops/finance/branch);
  `kpis: KpiCard[]`; `worklist: RecordRef[]`; `approvals: RecordRef[]`;
  `favourites: RouteRef[]`; `news: Notice[]`
- **Slots**: KPI strip; worklist; approvals inbox; favourites; news flash
- **States**: empty (first run — UI-006 first-run copy); loaded
- **Variants**: per-persona emphasis ordering (ops persona → worklist first)
- **Accessibility**: landmark regions; KPI cards are links whose accessible
  name carries value + label + delta; worklist count announced
- **Copy contract**: `common.a11y.live.results`, `ws.firstrun.welcome`,
  UI-006 empty states
- **Tokens**: `dimension.layout.topbar-h`, `dimension.space.*`,
  `color.status.*` on KPI deltas

### A2 · Module Workspace

- **Props**: `module: RegistryModule`; `kpis: KpiCard[]` (labels from the
  registry; values from API only — never literals); `quickActions`;
  `lists: ListSpec[]`; `reports: string[]` (the module's report library)
- **Slots**: KPI strip; quick actions; per-group list previews; built-in
  reports panel
- **States**: loading; empty (UI-006); loaded
- **Accessibility**: section labelled by the module's localised name; quick
  actions keyboard-reachable in registry order
- **Copy contract**: `nav.module.*`, module `desc` (registry), UI-006
- **Tokens**: workspace rails (`sitemap-w`, `factbox-w`), status tints

### A3 · Function Explorer

- **Props**: `module`; `group`; `subModules` (registry `freg.sub` triples)
- **Slots**: sub-module ledger with counts; cross-module links (`cross[]`)
- **States**: loaded (registry data is static)
- **Accessibility**: definition-list semantics; counts `aria-hidden` when
  decorative beside text
- **Copy contract**: sub-module names are registry data, not UI copy
- **Tokens**: `dimension.density.*` list tokens

### A4 · Grid / List

- **Props**: `columns`; `rows`; `filters: FilterChip[]`; `sort`;
  `rowActions`; `selection: none|single|multi`
- **Slots**: filter chips; toolbar (views/columns/export/new/refresh/print);
  status pills; row-action overflow
- **States**: empty-search / empty-filter (UI-006); loading; loaded; stale
  (`p03.error.stale`); bulk-selected
- **Variants**: density compact/cozy/relaxed (`row-h`); mobile 390px —
  inner scroll, never document overflow (defect #9 lesson)
- **Accessibility**: real table semantics; sortable headers announce;
  selection announced; row actions keyboard-reachable
- **Copy contract**: `p03.list.*`, `common.empty.no_results.*`, `flow.bulk.*`
- **Tokens**: `dimension.density.row-*`, `color.status.*` pills

### A5 · Record Details — BPF + FactBox

- **Props**: `record`; `bpf {stages, current}`; `tabs`; `factbox: Fact[]`;
  `related`
- **Slots**: Business-Process-Flow stepper — labels UNDER circles (defect #2);
  tab panels; FactBox rail at `factbox-w`
- **States**: per-stage; audit tab; lines tab; workflow actions
- **Accessibility**: stepper an `ol` with `aria-current`; FactBox
  `complementary`; WAI-ARIA tabs
- **Copy contract**: `overview/related/audit/lines/factbox/workflow` shell keys
- **Tokens**: `factbox-w`; connectors via `color.border.*`

### A6 · Data-Entry Form (modal)

- **Props**: `fields`; `mode: create|edit`; `onValid(values)`
- **Slots**: chip pickers; required markers
- **States**: pristine; invalid (red-on-empty, field-level messages);
  submitting; closes on valid
- **Accessibility**: errors via `aria-describedby`; focus trap; Enter
  submits, Esc cancels
- **Copy contract**: UI-003 field library; `common.error.field.*`
- **Tokens**: `color.status.error*`; control radius `radius-sm`

### A7 · Process Console

- **Props**: `steps: ChecklistStep[]`; `gauges: GaugeSpec[]`; `livePills`;
  `actions`
- **Slots**: steppers × checklists × gauges; live status pills
- **States**: per-step pending/doing/done/blocked; live values via API
- **Accessibility**: real checklist; gauge values exposed as text
- **Copy contract**: console titles from registry screen names
- **Tokens**: chart palette; `color.status.*` pills

### A8 · Dashboard

- **Props**: `kpis`; `charts: ChartSpec[]`; `split: PanelSpec[]`
- **Slots**: KPI row; chart grid; split panel
- **States**: loading; loaded; error-per-tile (one dead tile never kills the
  board)
- **Accessibility**: every chart carries a data-table or text alternative;
  colour never the sole carrier
- **Copy contract**: tile titles from the registry; `common.a11y.live.status`
- **Tokens**: `color.chart.1..8`; dark set `color.dark.chart-*`

### A9 · 360° View (party)

- **Props**: `party`; `bands: BandSpec[]`; `relationshipMap: Edge[]`
- **Slots**: identity band; relationship map (SVG); domain bands
- **Accessibility**: map has a textual adjacency-list alternative
- **Copy contract**: `nav.module.m33` labels
- **Tokens**: rail colours encode relationship types

### A10 · Report Viewer

- **Props**: `report: RegistryReportRef`; `table`; `distribution`;
  `trend: number[]`
- **Slots**: table — financial reports carry BOLD totals footers (defect #4);
  distribution bar; 7-week trend
- **States**: generating; ready; error
- **Accessibility**: totals row labelled; scoped table headers
- **Copy contract**: report names are registry data; `print` shell key
- **Tokens**: `typography.weight.semibold` totals; chart tokens for trend

### A11 · Report Center

- **Props**: `library` (the 346-entry registry catalogue); `statutoryShelf`
- **Slots**: statutory shelf; full library grid; search
- **Accessibility**: navigable list; statutory items first
- **Copy contract**: `report_center`, `new_report` shell keys
- **Tokens**: list tokens

### A12 · Report Writer (no-code, 7-step)

- **Props**: `wizard: StepSpec[7]`; `preview`
- **Slots**: step rail; live preview
- **States**: per-step valid/invalid; preview renders from real schema
- **Copy contract**: `new_report`, `run` shell keys
- **Tokens**: reuses the A5 stepper

### A13 · Global Search Results

- **Props**: `query`; `scopes`; `hits` (modules, screens, sub-modules,
  reports, forms, records, actions)
- **Slots**: scoped groups; highlighted terms
- **Accessibility**: results a list; keyboard ↑/↓/Enter (defect #10 applies
  to the input dropdown too)
- **Copy contract**: `search_ph`, `tellme_title`, `common.empty.no_results.search`
- **Tokens**: `dimension.focus.*`

---

# Part 3 — Chart Primitive Contracts (PP0-M04-T02)

Ported from the prototype's dependency-free SVG charts (`js/charts.js`,
token-aware, dark-safe). No external chart library in R1/R2 realisations;
tokens are read at render time so theme flips restyle every chart; Bengali
axis labels use the BN font stack and never truncate (UX-007).

| # | Primitive | Contract |
|---|---|---|
| C1 | **spark** | Inline mini-line for KPI cards. `series ≤ 8`, `state`. Tokens `color.status.*`. Decorative when adjacent to the KPI value, else a text summary |
| C2 | **line** | Multi-series. Tokens `color.chart.1..8` / dark `color.dark.chart-*`; grid `color.border.default`. Data-table alternative |
| C3 | **bar** | Vertical/horizontal with direct value labels — never legend-only encoding. Chart palette; type-200 labels |
| C4 | **donut** | True annular ring, centre text on card surface (defect #6); segments ≥3% labelled directly; slice-list alternative |
| C5 | **gauge** | Semi-arc; caption BELOW the arc, ≤22 chars (defect #5); 150×96; status triplet tokens |
| C6 | **heatmap** | Grid (e.g. dispatch load); sequential brand ramp; colour + text dual encoding |
| C7 | **waterfall** | Financial bridge (Mushak/VAT); totals bars bold; connectors `color.border.strong` |
| C8 | **funnel** | Stage conversion; stage labels + absolute and % values |

Cross-cutting: charts respect `prefers-reduced-motion` (no animation),
render in dark mode via the dark token set, and never fabricate data — an
empty series renders the UI-006 empty state, not a zeroed chart.
