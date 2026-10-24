#!/usr/bin/env python3
"""
generate-coverage-register.py — Generates docs/traceability/coverage-baseline-register.md
from the measured coverage telemetry in docs/traceability/evidence/coverage-baseline-report.json.
Implements R01-M04-T02.

Every number, target, story and count below is DERIVED from the report:
  - targets: 100% for modules in the report's `statutory_set` (exported from
    STATUTORY_SET in measure-coverage.py), 80% for every other module
  - stories: one per statutory path (gap to 100% under the financial/tax
    marker run) + one per non-statutory group directory (addons/domain/<cat>,
    addons/platform, services, libs/py) holding a gap to 80%
  - story coverage is weighted by statements+branches (covered / total)
  - "elements to target" = ceil(target * total) - covered
  - tool versions and the gate verdicts are read from the report
Refuses to render (exit 2) when the report marks the measurement invalid.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = REPO_ROOT / "docs" / "traceability" / "evidence" / "coverage-baseline-report.json"
OUTPUT_MD = REPO_ROOT / "docs" / "traceability" / "coverage-baseline-register.md"


def fmt_pct(v: float | None) -> str:
    return f"{v:.2f}%" if v is not None else "n/a"


def to_target(covered: int, total: int, target: float) -> int:
    return max(0, math.ceil(target / 100 * total) - covered) if total else 0


def weighted(mods: list[dict]) -> tuple[int, int, float | None]:
    covered = sum(m["covered_elements"] for m in mods)
    total = sum(m["total_elements"] for m in mods)
    return covered, total, (round(covered / total * 100, 2) if total else None)


def main() -> int:
    if not REPORT_JSON.is_file():
        print(f"Error: {REPORT_JSON} not found. Run measure-coverage.py first.")
        return 1
    raw = REPORT_JSON.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    if not data.get("measurement_valid"):
        print("Error: report marks the measurement INVALID; refusing to publish numbers:")
        for e in data.get("errors", []):
            print(f"  - {e}")
        return 2

    digest = hashlib.sha256(raw).hexdigest()[:16]
    modules = data["modules"]
    estate = data["estate_summary"]
    statutory = data["statutory_financial_tax_summary"]
    versions = data.get("tool_versions", {})
    estate_target = estate["target_gate_percent"]
    stat_target = statutory["target_gate_percent"]
    by_name = {m["name"]: m for m in modules}

    # ---------------------------------------------------------------- stories
    stories: list[dict] = []
    module_story: dict[str, str] = {}

    for entry in statutory["per_path"]:
        if to_target(entry["covered_elements"], entry["total_elements"], stat_target) == 0:
            continue  # already at 100% under the marker run: no gap, no story
        est_mod = by_name.get(entry["module"])
        stories.append(
            {
                "kind": "statutory",
                "label": f"`{entry['path']}`",
                "modules": [entry["module"]],
                "covered": entry["covered_elements"],
                "total": entry["total_elements"],
                "pct": entry["percent_covered"],
                "all_tests_pct": est_mod["percent_covered"] if est_mod else None,
                "target": stat_target,
                "why": entry["why"],
            }
        )

    groups: dict[str, list[dict]] = {}
    for m in modules:
        if m["statutory"] or m["percent_covered"] is None:
            continue
        groups.setdefault(m["group"], []).append(m)
    group_stories = []
    for grp, mods in groups.items():
        covered, total, cur = weighted(mods)
        gap_el = to_target(covered, total, estate_target)
        if gap_el == 0:
            continue
        group_stories.append(
            {
                "kind": "estate",
                "label": f"`{grp}` ({len(mods)} non-statutory modules)",
                "modules": [m["name"] for m in mods],
                "covered": covered,
                "total": total,
                "pct": cur,
                "target": estate_target,
                "mods": mods,
            }
        )
    group_stories.sort(key=lambda s: -to_target(s["covered"], s["total"], s["target"]))
    stories.extend(group_stories)

    for i, s in enumerate(stories, 1):
        s["id"] = f"BD-COV-{i:02d}"
        s["to_target"] = to_target(s["covered"], s["total"], s["target"])
        if s["kind"] == "statutory":
            s["prio"], s["wave"] = "P0 (Critical)", "W1"
        else:
            rank = group_stories.index(s) + 1
            s["prio"], s["wave"] = (
                ("P1 (High)", "W2")
                if rank <= 3
                else ("P2 (Medium)", "W3")
                if rank <= 7
                else ("P3 (Low)", "W4")
            )
        for name in s["modules"]:
            module_story[name] = s["id"]
    n_stories = len(stories)
    n_stat_stories = sum(1 for s in stories if s["kind"] == "statutory")

    # ---------------------------------------------------------------- header
    gates = data.get("gates_applied", {})

    def gate_line(key: str, summ: dict) -> str:
        g = gates.get(key)
        if g:
            return f"{g['verdict']} ({fmt_pct(g['measured_percent'])} vs gate {g['threshold_percent']:.0f}%)"
        return f"{summ['status']} vs policy target {summ['target_gate_percent']:.0f}% (no gate applied in this run)"

    md: list[str] = []
    a = md.append
    a("# Coverage Baseline Register — Milestone R01-M04")
    a(
        "## Empirical Baseline Measurement & Burn-Down Story Register (DoD-03 / P-3 Honesty Principle)"
    )
    a("")
    a(
        "> Generated by `tooling/scripts/generate-coverage-register.py` from the evidence JSON — do not hand-edit."
    )
    a("")
    a("| Metadata | Details |")
    a("|---|---|")
    a(
        "| **Roadmap Reference** | Revised Roadmap `RR-01` (`R01_Foundation_and_Governance_Closure.md`), Milestone `R01-M04`, Tasks `R01-M04-T01/T02` |"
    )
    a(f"| **Measurement Timestamp** | {data['timestamp']} |")
    a(
        f"| **Evidence Source** | `docs/traceability/evidence/coverage-baseline-report.json` (sha256 `{digest}…`) |"
    )
    a(
        f"| **Measurement Harness** | `tooling/scripts/measure-coverage.py`: Python {versions.get('python', '?')}, "
        f"pytest {versions.get('pytest', '?')}, pytest-cov {versions.get('pytest-cov', '?')}, "
        f"coverage {versions.get('coverage', '?')}; branch coverage |"
    )
    a(
        f"| **Estate Denominator** | {estate['files']} source files under `addons`, `services`, `libs` "
        f"({data['denominator']['method']}) |"
    )
    a(
        f"| **Estate Baseline Coverage** | **{fmt_pct(estate['percent_covered'])}** "
        f"({estate['covered_elements']:,} / {estate['total_elements']:,} statements & branches covered) |"
    )
    a(
        f"| **Estate Gate Target** | **{estate_target:.2f}%** (gap **{estate['gap_to_target_percent']:.2f} pp** = "
        f"**{estate['elements_to_target']:,}** more elements to cover: ceil({estate_target / 100:.2f} × "
        f"{estate['total_elements']:,}) − {estate['covered_elements']:,}) |"
    )
    a(
        f'| **Statutory Fin/Tax Baseline** | **{fmt_pct(statutory["percent_covered"])}** under `-m "{statutory["marker"]}"` '
        f"({statutory['covered_elements']:,} / {statutory['total_elements']:,}; "
        f"{statutory['elements_to_target']:,} elements to 100%) |"
    )
    a(
        f"| **Pure Calculation Logic (min)** | **{fmt_pct(statutory['pure_logic_coverage_percent'])}** "
        f"(`{statutory['pure_logic_min_file']}`; see §1) |"
    )
    a(f"| **Statutory Gate Target** | **{stat_target:.2f}%** (DoD-03) |")
    a(f"| **Estate Gate Verdict** | **{gate_line('estate', estate)}** |")
    a(f"| **Statutory Gate Verdict** | **{gate_line('statutory', statutory)}** |")
    a(
        f"| **Burn-Down Stories** | {n_stories} (BD-COV-01..{n_stories:02d}): {n_stat_stories} statutory + {n_stories - n_stat_stories} estate |"
    )
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------------- §1
    a("## 1. Statutory Set and Pure-Logic Coverage (financial/tax marker run)")
    a("")
    a(
        "The statutory set is defined once (`STATUTORY_SET` in `tooling/scripts/measure-coverage.py`)."
    )
    a("Coverage below is produced ONLY by tests marked `financial` or `tax`; `All-tests %` is the")
    a(
        "same module under the full estate run — a large difference means tests exist but are unmarked."
    )
    a("")
    a("| Statutory path | Why statutory | Files | Elements | Marker-run Cov % | All-tests Cov % |")
    a("|---|---|---:|---:|---:|---:|")
    for e in statutory["per_path"]:
        em = by_name.get(e["module"])
        a(
            f"| `{e['path']}` | {e['why']} | {e['files']} | {e['total_elements']} | "
            f"**{fmt_pct(e['percent_covered'])}** | {fmt_pct(em['percent_covered'] if em else None)} |"
        )
    a("")
    a(f"Pure calculation files ({statutory['pure_logic_basis']}):")
    a("")
    a("| Pure calculation file | Measured coverage |")
    a("|---|---:|")
    for fname, val in sorted(statutory["pure_logic_per_file"].items()):
        a(f"| `{fname}` | {fmt_pct(val)} |")
    a("")
    a(
        f"The aggregate is the **minimum per-file value: {fmt_pct(statutory['pure_logic_coverage_percent'])}** "
        f"(`{statutory['pure_logic_min_file']}`) — the gate is only as strong as its weakest engine."
    )
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------------- §2
    a("## 2. Complete Per-Module Coverage Baseline Register (full estate run)")
    a("")
    a(
        f"Target is {stat_target:.0f}% for statutory modules (§1) and {estate_target:.0f}% for every other "
        "module. `n/a` = no measurable statements (excluded from aggregates). "
        "`Unexec.` = files never executed by any test."
    )
    a("")
    a(
        "| # | Module / Component | Category | Group | Files (Unexec.) | Statements | Covered | Branches | Br Covered "
        "| Baseline Cov % | Target % | Gap pp | Elements to Target | Burn-Down Story |"
    )
    a("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for idx, m in enumerate(modules, 1):
        cov = m["percent_covered"]
        tgt = m["target_percent"]
        gap = fmt_pct(max(0.0, tgt - cov)).rstrip("%") if cov is not None else "n/a"
        el = (
            to_target(m["covered_elements"], m["total_elements"], tgt) if cov is not None else "n/a"
        )
        story = module_story.get(m["name"], "— (at target)" if cov is not None else "— (n/a)")
        a(
            f"| {idx} | `{m['name']}` | {m['category']} | `{m['group']}` | {m['files']} ({m['unexecuted_files']}) "
            f"| {m['num_statements']} | {m['covered_statements']} | {m['num_branches']} | {m['covered_branches']} "
            f"| **{fmt_pct(cov)}** | {tgt:.0f}% | {gap} | {el} | {story} |"
        )
    a("")
    a("---")
    a("")

    # ---------------------------------------------------------------- §3
    a("## 3. Burn-Down Stories Register (Statutory 100% & Gap-to-80%)")
    a("")
    a("Rules (derived, not hand-typed): one P0/W1 story per statutory path (gap to 100% under the")
    a("marker run); one story per non-statutory group directory with a gap to 80%, ranked by")
    a("elements to target (rank 1–3 P1/W2, 4–7 P2/W3, rest P3/W4). Current % is weighted by")
    a("statements+branches. Scope lists the largest per-module gaps in the story.")
    a("")
    a(
        "| Story ID | Priority | Target Domain / Component | Current Cov % | Target Cov % | Elements to Target | Wave | Scope |"
    )
    a("|---|:---:|---|---:|---:|---:|:---:|---|")
    for s in stories:
        if s["kind"] == "statutory":
            allp = s["all_tests_pct"]
            if allp is not None and s["pct"] is not None and allp > s["pct"] + 0.5:
                scope = (
                    f"{s['why']}. Unmarked tests already reach {fmt_pct(allp)} — mark them "
                    "`financial`/`tax`, then add marked tests for the remainder."
                )
            else:
                scope = f"{s['why']}. Add `financial`/`tax`-marked tests for every uncovered line/branch."
        else:
            worst = sorted(
                s["mods"],
                key=lambda m: -to_target(m["covered_elements"], m["total_elements"], s["target"]),
            )[:5]
            scope = "Largest gaps: " + ", ".join(
                f"`{m['name']}` {fmt_pct(m['percent_covered'])} "
                f"({to_target(m['covered_elements'], m['total_elements'], s['target'])} el)"
                for m in worst
                if to_target(m["covered_elements"], m["total_elements"], s["target"]) > 0
            )
        a(
            f"| **{s['id']}** | {s['prio']} | {s['label']} | {fmt_pct(s['pct'])} | {s['target']:.0f}% "
            f"| {s['to_target']:,} | {s['wave']} | {scope} |"
        )
    a("")
    est_story_el = sum(s["to_target"] for s in stories if s["kind"] == "estate")
    stat_story_el = sum(s["to_target"] for s in stories if s["kind"] == "statutory")
    a(
        f"Statutory stories sum to {stat_story_el:,} elements (to 100%, marker run); estate stories "
        f"sum to {est_story_el:,} elements (to 80%, per group). The estate gate itself needs "
        f"{estate['elements_to_target']:,} more covered elements across all {estate['files']} files; "
        "the sums differ because a group above 80% does not offset one below it and statutory "
        "modules are tracked against 100%."
    )
    a("")
    a("---")
    a("")
    a("## 4. Verification & Governance Traceability")
    a("")
    a(
        "- **Machine Telemetry:** [`docs/traceability/evidence/coverage-baseline-report.json`](evidence/coverage-baseline-report.json)"
    )
    a("- **Interactive Visual Report:** [`htmlcov/index.html`](../../htmlcov/index.html)")
    a("- **CI Cobertura Exchange:** [`coverage.xml`](../../coverage.xml)")
    a(
        "- **Reproduce:** `python tooling/scripts/measure-coverage.py --fail-under 80 "
        "--fail-under-financial 100 && python tooling/scripts/generate-coverage-register.py`"
    )
    a(
        f"- **Harness exit code (recorded):** {data.get('harness_exit_code', 'not recorded')} "
        "(0 pass, 1 gate failed, 2 invalid run)"
    )
    a("")

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(f"[ok] Successfully generated: {OUTPUT_MD} ({n_stories} stories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
