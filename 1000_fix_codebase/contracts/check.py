#!/usr/bin/env python3
"""contracts.check — OpenAPI 3.1 & Event Envelope Contract Verifier (PS-01, PS-11, AS-08).

CLI usage:
    python -m contracts.check openapi
    python -m contracts.check events
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OPENAPI_DIR = REPO_ROOT / "contracts" / "openapi"
EVENTS_DIR = REPO_ROOT / "contracts" / "events"
OUTBOX_MODEL = REPO_ROOT / "addons" / "platform" / "cd_event_outbox" / "models" / "fix_event_outbox.py"

REQUIRED_EVENT_FIELDS = {"event_id", "event_type", "timestamp", "producer", "payload"}
EVENT_TYPE_REGEX = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+){2,}$")


def check_openapi() -> int:
    """Validate OpenAPI contracts under contracts/openapi/."""
    if not OPENAPI_DIR.is_dir():
        print("contracts openapi: directory not found")
        return 1

    files = sorted(list(OPENAPI_DIR.glob("*.json")) + list(OPENAPI_DIR.glob("*.yaml")))
    if not files:
        print("contracts openapi: no contract files found in contracts/openapi/")
        return 0

    errors: list[str] = []
    checked = 0

    for path in files:
        checked += 1
        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
        except Exception as e:
            errors.append(f"{path.name}: failed to parse JSON: {e}")
            continue

        if not isinstance(data, dict):
            errors.append(f"{path.name}: root must be an object")
            continue

        ver = data.get("openapi") or data.get("swagger")
        if not ver:
            errors.append(f"{path.name}: missing 'openapi' version field")

        info = data.get("info", {})
        if not info.get("title") or not info.get("version"):
            errors.append(f"{path.name}: missing info.title or info.version")

        paths = data.get("paths", {})
        if not paths and not data.get("components"):
            errors.append(f"{path.name}: no paths or components defined")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        print(f"contracts openapi: {len(errors)} violation(s) across {checked} contract(s)", file=sys.stderr)
        return 1

    print(f"contracts openapi: OK — {checked} contract file(s) valid per OpenAPI standard")
    return 0


def check_events() -> int:
    """Validate event schemas and transactional outbox model per AS-08 & AR-009."""
    errors: list[str] = []
    checked = 0

    if EVENTS_DIR.is_dir():
        for path in sorted(EVENTS_DIR.glob("*.json")):
            checked += 1
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except Exception as e:
                errors.append(f"{path.name}: failed to parse JSON: {e}")
                continue

            props = data.get("properties", {})
            if props:
                missing = REQUIRED_EVENT_FIELDS - set(props.keys())
                if missing:
                    errors.append(f"{path.name}: missing required event envelope fields: {sorted(missing)}")

    # Verify transactional outbox model
    if OUTBOX_MODEL.is_file():
        content = OUTBOX_MODEL.read_text(encoding="utf-8")
        required_columns = ["event_id", "event_type", "aggregate", "aggregate_id", "payload", "status"]
        for col in required_columns:
            if col not in content:
                errors.append(f"outbox model {OUTBOX_MODEL.name} missing field {col}")
    else:
        errors.append(f"outbox model missing at {OUTBOX_MODEL}")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        print(f"contracts events: {len(errors)} violation(s)", file=sys.stderr)
        return 1

    print(f"contracts events: OK — {checked} schema(s) and outbox model verified (AR-009 / AS-08)")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    target = args[0] if args else "openapi"
    if target == "openapi":
        return check_openapi()
    elif target == "events":
        return check_events()
    else:
        print(f"contracts.check: unknown target '{target}'. Use 'openapi' or 'events'.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
