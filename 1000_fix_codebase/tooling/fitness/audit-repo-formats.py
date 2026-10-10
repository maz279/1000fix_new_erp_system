#!/usr/bin/env python3
"""audit-repo-formats — comprehensive P04 audit pass 3.

Validates every config/data format the estate ships:

  - YAML: fitness registry, cd-register, CI workflow, compose, environments,
    pre-commit
  - JSON: every repo JSON (tokens, ui-copy registry, realm, kong, otel…)
  - PO: every bn_BD.po is balanced (msgid count == msgstr count) and has no
    empty translation for a non-empty msgid
  - Determinism: regenerating design tokens and UI copy over a clean tree
    changes nothing (generated artefacts are never hand-edited or stale)

Exit: 0 clean / 1 violations.
"""
from __future__ import annotations

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
    ".github/workflows/ci.yml",
    "infra/compose/docker-compose.yml",
    "infra/environments.yaml",
    ".pre-commit-config.yaml",
]
PO_BLOCK = re.compile(r'msgid "((?:[^"\\]|\\.)*)"\nmsgstr "((?:[^"\\]|\\.)*)"')
SKIP_DIRS = {"node_modules", "__pycache__", ".git", "vendor", ".venv"}


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
        if SKIP_DIRS & set(p.lower() for p in path.parts):
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            issues.append(f"JSON invalid: {path.relative_to(REPO).as_posix()}: {str(exc)[:80]}")

    for po in (REPO / "addons").rglob("*.po"):
        text = po.read_text(encoding="utf-8")
        msgids = re.findall(r"^msgid ", text, re.M)
        msgstrs = re.findall(r"^msgstr ", text, re.M)
        if len(msgids) != len(msgstrs):
            issues.append(
                f"PO unbalanced: {po.relative_to(REPO).as_posix()}: "
                f"{len(msgids)} msgid vs {len(msgstrs)} msgstr"
            )
        for mid, mstr in PO_BLOCK.findall(text):
            if mid.strip() and not mstr.strip():
                issues.append(f"PO empty msgstr: {po.relative_to(REPO).as_posix()}: {mid[:40]!r}")

    # Determinism of the two generators over the current tree.
    for generator in (
        "tooling/generators/generate-design-tokens.py",
        "tooling/scripts/extract-ui-copy.py",
        "tooling/generators/generate-landing-artefact.py",
    ):
        result = subprocess.run(  # noqa: S603 - fixed argv inside the repo
            [sys.executable, str(REPO / generator)], capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            issues.append(f"generator failed: {generator}: {result.stdout.strip()[-120:]}")
    dirty = subprocess.run(  # noqa: S603 - fixed argv
        ["git", "status", "--porcelain", "--", "addons/platform/cd_design_tokens",
         "libs/ts/ui", "libs/ts/i18n"],
        capture_output=True, text=True, check=False, cwd=REPO,
    ).stdout.strip()
    if dirty:
        issues.append(f"generated artefacts not deterministic/stale: {dirty.splitlines()[0]} ...")

    if issues:
        print(f"repo-formats: FAIL - {len(issues)} issue(s):")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print("repo-formats: OK - YAML/JSON/PO valid; generators deterministic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
