#!/usr/bin/env python3
"""affected-selection (BG-01..BG-05, P02-M09-T08) - the 20-minute budget holder.

Computes the affected component set for a change from the REGENERATED
dependency graph (docs/p01-m04/registers/graph.txt, regenerated with
tooling/architecture-baseline/evidence/dependency-graph-*.json - MR-01: the
graph is regenerated, never edited). Inverts DEP edges so a change to a
prerequisite marks every dependent; PE-004-F-01 is honoured by design: with
18 cycles, a change inside a cycle marks every member - the broken pairs are
the slow sets, measured per gate and burned down by the 11 interface breaks.

Graph nodes are registry IDs (M01..M67); docs/navigation/
registry-to-production-mapping.md maps each ID to its cd_* addon(s).

Output: pytest PATHS (directories/files relative to the codebase root), one
per line, e.g. addons/domain/g_finance/cd_tax_engine_bd. Whenever the change
cannot be narrowed safely (shared libs, conftest, pyproject/lock, vendor,
git failure, nothing selectable) the full test roots are printed:
  addons services libs tests
Exit 0 always.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GRAPH_GLOB = "tooling/architecture-baseline/evidence/dependency-graph-*.json"
GRAPH_TXT = REPO_ROOT / "docs" / "p01-m04" / "registers" / "graph.txt"
ID_MAP_MD = REPO_ROOT / "docs" / "navigation" / "registry-to-production-mapping.md"
FULL_RUN = ("addons", "services", "libs", "tests")

# A change under any of these can affect any test: run everything.
FULL_RUN_TRIGGERS = (
    "libs/",
    "vendor/",
    "addons/conftest.py",
    "pyproject.toml",
    "uv.lock",
    "conftest.py",
)


class FullRun(Exception):
    """The change cannot be narrowed - run the full test roots."""


def changed_files(base: str) -> list[str]:
    # --relative: paths relative to the codebase dir (the git toplevel is its
    # parent, so plain --name-only would prefix every path with 1000_fix_codebase/).
    try:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "--relative", base],
            capture_output=True,
            text=True,
            shell=False,
            cwd=REPO_ROOT,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"affected-selection: git diff failed ({e}); full run", file=sys.stderr)
        raise FullRun from e
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def load_graph(graph_json: str | None) -> dict[str, list[str]]:
    """Inverted DEP edges: prerequisite -> [dependents] (registry IDs)."""
    if graph_json:
        if not (REPO_ROOT / graph_json).is_file():
            raise FullRun
    elif not sorted(REPO_ROOT.glob(GRAPH_GLOB)):
        raise FullRun
    if not GRAPH_TXT.is_file():
        raise FullRun
    dependents: dict[str, list[str]] = {}
    for line in GRAPH_TXT.read_text(encoding="utf-8").splitlines():
        if line.startswith("DEP "):
            _, a, b = line.split()
            dependents.setdefault(b, []).append(a)
    return dependents


def load_id_map() -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """(registry ID -> addons, addon -> registry IDs) from the mapping table."""
    id_to_mod: dict[str, set[str]] = {}
    mod_to_id: dict[str, set[str]] = {}
    if not ID_MAP_MD.is_file():
        return id_to_mod, mod_to_id
    row = re.compile(r"^\|\s*(M\d{2})\s*\|[^|]*\|[^|]*\|([^|]*)\|")
    for line in ID_MAP_MD.read_text(encoding="utf-8").splitlines():
        m = row.match(line)
        if not m:
            continue
        for mod in re.findall(r"\bcd_[a-z0-9_]+\b", m.group(2)):
            id_to_mod.setdefault(m.group(1), set()).add(mod)
            mod_to_id.setdefault(mod, set()).add(m.group(1))
    return id_to_mod, mod_to_id


def addon_dirs() -> dict[str, str]:
    """cd_* module name -> its directory (relative posix path)."""
    out: dict[str, str] = {}
    for mf in (REPO_ROOT / "addons").glob("**/__manifest__.py"):
        out[mf.parent.name] = mf.parent.relative_to(REPO_ROOT).as_posix()
    return out


def module_of(path: str) -> str | None:
    """cd_* addon owning a changed file: addons/platform/<cd_x>/... or
    addons/domain/<category>/<cd_x>/... (any depth below the module)."""
    parts = Path(path).as_posix().split("/")
    if not parts or parts[0] != "addons":
        return None
    for seg in parts[1:4]:
        if seg.startswith("cd_"):
            return seg
    return None


def select(changed: list[str], dependents: dict[str, list[str]]) -> list[str]:
    id_to_mod, mod_to_id = load_id_map()
    dirs = addon_dirs()
    touched_mods: set[str] = set()
    paths: set[str] = set()
    for f in changed:
        posix = Path(f).as_posix()
        if posix.startswith(FULL_RUN_TRIGGERS) or posix.endswith("/conftest.py"):
            raise FullRun
        mod = module_of(posix)
        if mod:
            touched_mods.add(mod)
            continue
        parts = posix.split("/")
        if parts[0] == "services" and len(parts) >= 3:
            svc = "/".join(parts[:2])
            if (REPO_ROOT / svc).is_dir():
                paths.add(svc)
        elif parts[0] == "tests" and posix.endswith(".py"):
            if (REPO_ROOT / posix).is_file():
                paths.add(posix)
        elif parts[0] == "addons" and posix.endswith(".py"):
            raise FullRun  # addon-level file outside any module

    # Transitive dependents over the registry-ID graph.
    affected_ids: set[str] = set()
    for mod in touched_mods:
        affected_ids |= mod_to_id.get(mod, set())
    frontier = list(affected_ids)
    while frontier:
        nxt: list[str] = []
        for mid in frontier:
            for d in dependents.get(mid, []):
                if d not in affected_ids:
                    affected_ids.add(d)
                    nxt.append(d)
        frontier = nxt
    affected_mods = set(touched_mods)
    for mid in affected_ids:
        affected_mods |= id_to_mod.get(mid, set())
    for mod in affected_mods:
        if mod in dirs:
            paths.add(dirs[mod])
    return sorted(paths)


def main(argv: list[str]) -> int:
    base = "origin/develop"
    graph_json: str | None = None
    if "--base" in argv:
        base = argv[argv.index("--base") + 1]
    if "--graph" in argv:
        graph_json = argv[argv.index("--graph") + 1]
    try:
        dependents = load_graph(graph_json)
        selected = select(changed_files(base), dependents)
        if not selected:
            raise FullRun
    except FullRun:
        selected = list(FULL_RUN)
    print("\n".join(selected))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
