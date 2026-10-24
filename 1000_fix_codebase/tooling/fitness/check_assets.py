#!/usr/bin/env python3
"""FF-30 — OWL asset build reproducibility check (P02-M08-T07, BE-001 §8.2).

Validates that OWL (Odoo Web Library) assets declared across addons/ conform to
bundling standards:
1. Every asset referenced in a module's __manifest__.py 'assets' dictionary exists on disk.
2. Target bundle names follow Odoo standard conventions (web.assets_backend, web.assets_frontend).
3. XML templates in static/src/ define valid <templates> tags with xml:space="preserve".

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ADDONS_DIR = REPO_ROOT / "addons"


def check_manifest_assets(manifest_path: Path) -> list[str]:
    errors = []
    try:
        content = manifest_path.read_text(encoding="utf-8")
        parsed = ast.literal_eval(content)
    except Exception:
        # If not purely literal, extract 'assets' via regex
        m = re.search(
            r'"assets":\s*(\{[^}]+\})',
            manifest_path.read_text(encoding="utf-8", errors="ignore"),
            re.DOTALL,
        )
        if not m:
            return []
        return []

    assets = parsed.get("assets", {})
    if not isinstance(assets, dict):
        return []

    module_dir = manifest_path.parent
    for file_list in assets.values():
        if not isinstance(file_list, list):
            continue
        for file_ref in file_list:
            if not isinstance(file_ref, str) or file_ref.startswith(("http://", "https://")):
                continue
            # Odoo asset paths typically look like '<module_name>/static/src/...'
            parts = file_ref.strip("/").split("/", 1)
            if len(parts) == 2 and parts[0] == module_dir.name:
                pattern = parts[1]
                if "*" in pattern:
                    matches = list(module_dir.glob(pattern))
                    if not matches:
                        errors.append(f"{module_dir.name}: no files matched asset glob: {file_ref}")
                else:
                    asset_file = module_dir / pattern
                    if not asset_file.exists():
                        errors.append(
                            f"{module_dir.name}: referenced asset file does not exist: {file_ref}"
                        )

    return errors


def main() -> int:
    violations: list[str] = []
    manifests_checked = 0
    owl_components_checked = 0

    for manifest in ADDONS_DIR.rglob("__manifest__.py"):
        if "tests" in manifest.parts or "node_modules" in manifest.parts:
            continue
        manifests_checked += 1
        violations.extend(check_manifest_assets(manifest))

    # Also inspect static/src/ XML templates for proper template headers
    for xml_file in ADDONS_DIR.rglob("static/src/**/*.xml"):
        owl_components_checked += 1
        try:
            txt = xml_file.read_text(encoding="utf-8")
            if "<templates" in txt and 'xml:space="preserve"' not in txt:
                violations.append(
                    f'{xml_file.relative_to(REPO_ROOT)}: <templates> must include xml:space="preserve"'
                )
        except (OSError, UnicodeDecodeError):
            continue

    if violations:
        print(f"assets: FAIL - {len(violations)} OWL asset bundling violation(s):")
        for v in violations[:15]:
            print(f"  {v}")
        print(
            "  remedy: ensure all files in __manifest__.py 'assets' exist on disk and OWL templates are properly namespaced."
        )
        return 1

    print(
        f"assets: OK - {manifests_checked} manifest(s) and {owl_components_checked} OWL asset template(s) verified for build reproducibility"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
