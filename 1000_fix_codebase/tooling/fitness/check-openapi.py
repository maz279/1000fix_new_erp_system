#!/usr/bin/env python3
"""check-openapi — FF-40 (PP1-M03): the contract surface is valid.

For every spec under contracts/openapi/: parses as JSON, declares openapi
3.x, carries info.title, info.version, servers, at least one path whose
item has responses, and every internal $ref (#/components/...) resolves to
a declared schema. PS-11 behavioural tests live beside the services that
implement each spec; this check guarantees the *documents* are sound so
api-client generation and the tests can trust them.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SPECS = REPO / "contracts" / "openapi"
REF = re.compile(r'"#\$ref"\s*:\s*"#/components/schemas/([^"]+)"')


def walk_refs(node, found: list[str]) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str) and v.startswith("#/components/schemas/"):
                found.append(v.split("/")[-1])
            else:
                walk_refs(v, found)
    elif isinstance(node, list):
        for item in node:
            walk_refs(item, found)


def main() -> int:
    if not SPECS.is_dir() or not any(SPECS.glob("*.json")):
        print("check-openapi: FAIL — contracts/openapi holds no specs")
        return 1
    v: list[str] = []
    for f in sorted(SPECS.glob("*.json")):
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            v.append(f"{f.name}: invalid JSON ({e})")
            continue
        if not str(spec.get("openapi", "")).startswith("3."):
            v.append(f"{f.name}: openapi field missing or not 3.x")
        for field in ("title", "version"):
            if field not in spec.get("info", {}):
                v.append(f"{f.name}: info.{field} missing")
        if not spec.get("servers"):
            v.append(f"{f.name}: servers missing (gateway routing is part of the contract)")
        paths = spec.get("paths", {})
        if not paths:
            v.append(f"{f.name}: no paths")
        for path, item in paths.items():
            for method, op in item.items():
                if method in {"get", "post", "put", "patch", "delete"}:
                    if "responses" not in op or not op["responses"]:
                        v.append(f"{f.name}: {method.upper()} {path} has no responses")
                    if "operationId" not in op:
                        v.append(f"{f.name}: {method.upper()} {path} has no operationId")
        refs: list[str] = []
        walk_refs(spec, refs)
        declared = set(spec.get("components", {}).get("schemas", {}))
        for r in refs:
            if r not in declared:
                v.append(f"{f.name}: $ref #{r} does not resolve")
    if v:
        print(f"check-openapi: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1
    print(
        f"check-openapi: OK - {len(list(SPECS.glob('*.json')))} specs valid "
        "(3.x, info, servers, operations, refs resolve)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
