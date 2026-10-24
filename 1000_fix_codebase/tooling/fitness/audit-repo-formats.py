#!/usr/bin/env python3
"""audit-repo-formats — comprehensive P04 audit pass 3.

Validates every config/data format the estate ships:

  - YAML: fitness registry, cd-register, CI workflow, compose, environments,
    pre-commit
  - JSON: every repo JSON (tokens, ui-copy registry, realm, kong, otel…)
  - PO: every bn_BD.po is balanced (msgid count == msgstr count) and has no
    empty translation for a non-empty msgid (wrapped entries read whole)
  - Determinism: regenerating design tokens and UI copy over a clean tree
    changes nothing (generated artefacts are never hand-edited or stale)

Exit: 0 clean / 1 violations.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]

YAML_FILES = [
    "tooling/fitness/registry.yaml",
    "tooling/cd-register.yaml",
    # The workflow lives at the git root (parent of this codebase): GitHub
    # reads workflows only from <git-root>/.github/workflows.
    "../.github/workflows/ci.yml",
    "infra/compose/docker-compose.yml",
    "infra/environments.yaml",
    ".pre-commit-config.yaml",
]
SKIP_DIRS = {"node_modules", "__pycache__", ".git", "vendor", ".venv"}
FITNESS_DIR = Path(__file__).resolve().parent


def po_issues(addons: Path, rel_to: Path = REPO) -> list[str]:
    """Every .po under `addons` is balanced (one msgstr per msgid; a plural
    entry's msgstr[0] counts) and translates every non-empty msgid.

    Entries are read with check_translations.parse_po_entries - the FF-24/25
    reader - so a gettext-wrapped msgid/msgstr (continuation lines, the form
    Odoo's own export writes) is one entry, not a false "empty msgstr".
    """
    if str(FITNESS_DIR) not in sys.path:
        sys.path.insert(0, str(FITNESS_DIR))
    from check_translations import parse_po_entries  # sibling fitness script (FF-24/25 reader)

    issues: list[str] = []
    for po in sorted(addons.rglob("*.po")):
        text = po.read_text(encoding="utf-8")
        rel = po.relative_to(rel_to).as_posix()
        msgids = len(re.findall(r"^msgid ", text, re.M))
        msgstrs = len(re.findall(r"^msgstr(?:\[0\])? ", text, re.M))
        if msgids != msgstrs:
            issues.append(f"PO unbalanced: {rel}: {msgids} msgid vs {msgstrs} msgstr")
        for msgid, msgstr, _fuzzy in parse_po_entries(text):
            if msgid.strip() and not msgstr.strip():
                issues.append(f"PO empty msgstr: {rel}: {msgid[:40]!r}")
    return issues


def main() -> int:
    issues: list[str] = []

    for rel in YAML_FILES:
        path = REPO / rel
        if not path.exists():
            issues.append(f"YAML missing: {rel}")
            continue
        try:
            yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            issues.append(f"YAML invalid: {rel}: {str(exc)[:100]}")

    for path in REPO.rglob("*.json"):
        if SKIP_DIRS & {p.lower() for p in path.parts}:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            issues.append(f"JSON invalid: {path.relative_to(REPO).as_posix()}: {str(exc)[:80]}")

    issues.extend(po_issues(REPO / "addons"))

    # Determinism of the generators over the current tree: snapshot the
    # generated-artefact directories, run the generators, compare. (R01
    # re-audit 2026-10-22: the previous `git status` test compared against
    # HEAD, so ANY uncommitted edit there - even to a non-generated file such
    # as a manifest - was reported as "not deterministic".)
    gen_dirs = ("addons/platform/cd_design_tokens", "libs/ts/ui", "libs/ts/i18n")

    def _snapshot() -> dict[str, str]:
        snap: dict[str, str] = {}
        for d in gen_dirs:
            for f in sorted((REPO / d).rglob("*")):
                if f.is_file() and "node_modules" not in f.parts:
                    snap[f.relative_to(REPO).as_posix()] = hashlib.sha256(
                        f.read_bytes()
                    ).hexdigest()
        return snap

    before = _snapshot()
    for generator in (
        "tooling/generators/generate-design-tokens.py",
        "tooling/scripts/extract-ui-copy.py",
        "tooling/generators/generate-landing-artefact.py",
    ):
        result = subprocess.run(
            [sys.executable, str(REPO / generator)], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            issues.append(f"generator failed: {generator}: {result.stdout.strip()[-120:]}")
    after = _snapshot()
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    if changed:
        issues.append(
            f"generated artefacts not deterministic/stale: {changed[0]} (+{len(changed) - 1} more)"
        )

    if issues:
        print(f"repo-formats: FAIL - {len(issues)} issue(s):")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print("repo-formats: OK - YAML/JSON/PO valid; generators deterministic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
