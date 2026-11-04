#!/usr/bin/env python3
"""FF-49 - KPI and report reads stay inside the user's companies (A05 audit E14).

A KPI, report or summary that reads with ``sudo().search([])`` (or
``search_count`` / ``search_read`` / ``read_group`` with an empty domain)
counts every company's records: the A05 audit found M18's ESG and DoE figures
crossing company boundaries this way (M18-11). This check finds every such
read inside a function whose name says it is a figure (kpi, report,
dashboard, summary, metric, figure, scorecard).

Ratchet: the reads that already exist outside A05 are recorded per
file and function in evidence/kpi_company_scope_baseline.json and may only go
down; any new one fails. A05 (controllers/a05 and the d_circular modules) has
no baseline: it must have none.

  python tooling/fitness/check_kpi_company_scope.py             # check
  python tooling/fitness/check_kpi_company_scope.py --baseline  # rewrite baseline

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS = REPO_ROOT / "addons"
BASELINE = Path(__file__).resolve().parent / "evidence" / "kpi_company_scope_baseline.json"
FIGURE = re.compile(r"kpi|report|dashboard|summary|metric|figure|scorecard", re.I)
READS = {"search", "search_count", "search_read", "read_group", "_read_group"}
# held to zero: no baseline is ever recorded for these paths
STRICT = (
    "addons/platform/cd_p03_portal/controllers/a05/",
    "addons/domain/d_circular/cd_rental_asset/",
    "addons/domain/d_circular/cd_tradein/",
    "addons/domain/d_circular/cd_ewaste/",
)


def _empty_domain(call: ast.Call) -> bool:
    domain = call.args[0] if call.args else None
    for kw in call.keywords:
        if kw.arg == "domain":
            domain = kw.value
    return isinstance(domain, ast.List) and not domain.elts


def _is_sudo_read(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in READS
        and isinstance(node.func.value, ast.Call)
        and isinstance(node.func.value.func, ast.Attribute)
        and node.func.value.func.attr == "sudo"
        and _empty_domain(node)
    )


def scan() -> tuple[Counter, list[str]]:
    """(count per 'path::function', the 'path:line function' of each read)."""
    counts: Counter = Counter()
    sites: list[str] = []
    for path in sorted(ADDONS.rglob("*.py")):
        if "tests" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef | ast.AsyncFunctionDef) or not FIGURE.search(
                fn.name
            ):
                continue
            for node in ast.walk(fn):
                if _is_sudo_read(node):
                    counts["%s::%s" % (rel, fn.name)] += 1
                    sites.append("%s:%d %s()" % (rel, node.lineno, fn.name))
    return counts, sites


def main(argv: list[str]) -> int:
    counts, sites = scan()
    if "--baseline" in argv:
        kept = {k: v for k, v in sorted(counts.items()) if not k.startswith(STRICT)}
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(json.dumps(kept, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(
            "kpi-company-scope: baseline written, %d function(s), %d read(s)"
            % (len(kept), sum(kept.values()))
        )
        return 0
    baseline = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.is_file() else {}
    over = {
        key: (n, baseline.get(key, 0))
        for key, n in counts.items()
        if n > (0 if key.startswith(STRICT) else baseline.get(key, 0))
    }
    if over:
        print("kpi-company-scope: FAIL - %d function(s) read every company's records:" % len(over))
        for key, (n, allowed) in sorted(over.items()):
            path, fn = key.split("::")
            print("  %s %s(): %d sudo().search([]) read(s), %d allowed" % (path, fn, n, allowed))
            for site in sites:
                if site.startswith(path + ":") and site.endswith(" %s()" % fn):
                    print("    " + site)
        print(
            "  remedy: scope the read to the user's companies, e.g. [('company_id', 'in', env.companies.ids)]."
        )
        return 1
    print(
        "kpi-company-scope: OK - %d legacy read(s) in %d function(s) at or under the baseline; A05 has none"
        % (sum(counts.values()), len(counts))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
