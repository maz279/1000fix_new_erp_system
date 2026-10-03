# Gate checklist item — version-currency re-verification (all gates)

**Task `P01-M02-T10` produces this item** · Established 2026-10-01 · Applies
from `G0a` onward.

| | |
|---|---|
| **Item ID** | `GATE-VC` — "Version currency re-verified against upstream" |
| **Applies at** | **Every** gate: `G0a`, `G0b`, `G1`…`G10` (and the annual `D-030` licence-register review on the same cadence) |
| **Tool** | `tooling/version-currency/verify-version-currency.ps1` (exit 0 required; `-Strict` where the gate chair demands) |
| **Standing list** | `tooling/version-currency/components.json` — all L4 systems (incl. the `D-028`/`D-030` replacements), L1–L3 classes, app-platform runtimes, L6 commercial set |
| **Evidence** | A dated record per gate: JSON (`-Json`) filed under `tooling/version-currency/evidence/`, next to the first record of 2026-10-01 |

## Gate acceptance rule

1. **Fresh online run at the gate** — a record older than 14 days is not
   evidence at a gate; the ritual's own rule ("never against the last
   document that verified it") applies to its own output.
2. **Exit 0.** Any FAIL (baseline cycle EOL'd upstream; upstream repo
   archived — the MinIO failure mode) blocks the gate until a `D-nnn`
   decision re-baselines the component and updates `versions.lock` +
   `components.json` together.
3. **WARN dispositions recorded.** EOL within 365 days, stale manual facts
   (>90 days) and network-unreachable probes each need a named owner and a
   next-gate action in the gate minutes — a WARN with no disposition at two
   consecutive gates escalates to FAIL by rule.
4. **New components enter the standing list at adoption**, not at the next
   gate: a component missing from `components.json` is itself a finding
   (the register is the list — `R-04`'s original lesson).

## Why this item exists (the one-paragraph history for gate chairs)

The estate's Technology Stack Specification verified its stack on 13 August
2026 and did not notice its object store had been archived four months
earlier; the cross-repository alignment audit re-verified four famous
components six days later and re-verified the same four. Nine of eleven
external findings sat in components nobody checked. This checklist item, with
its named 43-check standing list (42 components plus the archived-repo watch
guard), is what fixes that (IR-002 Appendix I §I.8).
