# Version-Currency Ritual — P01-M02-T10

The executable form of the alignment audit's `R-04` rule: **re-verify every
stack component against upstream, never against the last document that
verified it.** Established by roadmap task `P01-M02-T10`; every wave gate runs
it and the restricted-licence register (`D-030`) is reviewed on the same
cadence.

| File | Purpose |
|---|---|
| `components.json` | **The standing list** — all L4 systems (TSS §7 register incl. the `D-028`/`D-030` replacements), L1–L3 classes, app-platform runtimes, L6 commercial set; 43 checks + watch list + dated manual facts |
| `verify-version-currency.ps1` | The executable: `endoflife` checks (endoflife.date), `github` repo-liveness checks (archived = FAIL — the MinIO failure mode), `manual` staleness checks (`RG-08`); DE-18 remedies, non-zero exit on FAIL (DE-19) |
| `evidence/` | Dated verification records — first run: `verification-record-2026-10-01.md` (human record with sources) + the machine JSON |

## Usage

```powershell
powershell -ExecutionPolicy Bypass -File verify-version-currency.ps1 -Json record.json
# -Offline   manifest + manual facts only (no network)
# -Strict    warnings also fail the run
# -WarnDays / -ManualStaleDays   tune the horizons (default 365 / 90)
```

## Cadence & ownership

- **Every wave gate** (`G1`…`G10`): a fresh online run; the record is a gate
  artefact. **Annually:** the `D-030` licence register review.
- A FAIL (baseline cycle EOL, upstream repo archived) blocks the gate until a
  decision (`D-nnn`) re-baselines the component — the remedy line says exactly
  that.

## Operational notes

- **GitHub unauthenticated quota is 60 req/h** — a full online run uses ~44
  (the `releases/latest` probe is opt-in per component via `"latest": true`
  for exactly this reason). If a run reports HTTP 403 WARNs, wait for the
  hourly reset and re-run; the facts for rate-limited components live in
  `manualFacts` with dated sources meanwhile.
- `endoflife.date` encodes "no EOL announced yet" as `eol: false` for a
  current cycle (e.g. the Next.js 16 line) — handled as OK.
- No credentials are used anywhere; both APIs are public and keyless.
