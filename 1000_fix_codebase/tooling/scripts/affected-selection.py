#!/usr/bin/env python3
"""affected-selection (BG-01..BG-05, P02-M09-T08) - the 20-minute budget holder.

Computes the affected component set for a change from the REGENERATED
dependency graph (tooling/architecture-baseline/evidence/*.json - MR-01: the
graph is regenerated, never edited). Inverts DEP edges so a change to a
prerequisite marks every dependent; PE-004-F-01 is honoured by design: with
18 cycles, a change inside a cycle marks every member - the broken pairs are
the slow sets, measured per gate and burned down by the 11 interface breaks.

Output: module names, one per line, consumed by pytest path selection.
Exit 0 always (an empty result prints 'addons services libs' - full run).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_GLOB = "tooling/architecture-baseline/evidence/dependency-graph-*.json"


def changed_files(base: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", base], capture_output=True, text=True,
        shell=False, cwd=REPO_ROOT, check=True,
    )
    return [l.strip() for l in proc.stdout.splitlines() if l.strip()]


def load_graph() -> dict[str, list[str]]:
    graphs = sorted(REPO_ROOT.glob(GRAPH_GLOB))
    if not graphs:
        print("addons services libs", end="")
        return {}
    # The canonical edge list is graph.txt (DEP A B lines) next to the
    # registers; the evidence JSON carries the analysis, graph.txt the edges.
    dependents: dict[str, list[str]] = {}
    gt = REPO_ROOT / "docs" / "p01-m04" / "registers" / "graph.txt"
    for line in gt.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEP "):
            _, a, b = line.split()
            dependents.setdefault(b, []).append(a)
    return dependents


def module_of(path: str) -> str | None:
    parts = Path(path).parts
    if parts and parts[0] == "addons" and len(parts) >= 3:
        # addons/<layer>/<category>/<module> OR addons/<layer>/<module>
        seg = parts[-2] if parts[-2].startswith("cd_") else parts[-1].split(".")[0]
        return seg if seg.startswith("cd_") else None
    return None


def main(argv: list[str]) -> int:
    base = "origin/develop"
    if "--base" in argv:
        base = argv[argv.index("--base") + 1]
    dependents = load_graph()
    touched: set[str] = set()
    for f in changed_files(base):
        m = module_of(f)
        if m:
            touched.add(m)
    affected: set[str] = set(touched)
    frontier = list(touched)
    while frontier:  # transitive dependents (inverted DEP edges)
        nxt: list[str] = []
        for m in frontier:
            for d in dependents.get(m, []):
                if d not in affected:
                    affected.add(d)
                    nxt.append(d)
        frontier = nxt
    if affected:
        print("\n".join(sorted(affected)))
    else:
        print("addons services libs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
