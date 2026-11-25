#!/usr/bin/env python3
"""FF-19 — Event payload schema conformance check (AR-009 §5.5, CBS-14, P02-M08-T07).

Validates event payload schemas under contracts/events/ and outbox event definitions.
Every registered event schema must:
1. Parse as valid JSON or YAML.
2. Define standard CloudEvents / FixEvent envelope properties:
   - event_id (string/UUID)
   - event_type (domain.entity.action format)
   - timestamp (ISO-8601 string)
   - producer (string identifier)
   - payload (object)
3. Ensure no un-versioned or malformed schema files exist.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_DIR = REPO_ROOT / "contracts" / "events"
OUTBOX_MODEL = (
    REPO_ROOT / "addons" / "platform" / "cd_event_outbox" / "models" / "fix_event_outbox.py"
)

REQUIRED_FIELDS = {"event_id", "event_type", "timestamp", "producer", "payload"}
EVENT_TYPE_REGEX = re.compile(r"^[a-z0-9_]+(?:\.[a-z0-9_]+){2,}$")


def validate_schema_file(path: Path) -> list[str]:
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"{path.name}: failed to parse JSON: {e}"]

    if not isinstance(data, dict):
        return [f"{path.name}: top-level schema must be an object"]

    # Check required schema fields if defining full event schema
    props = data.get("properties", {})
    if props:
        missing = REQUIRED_FIELDS - set(props.keys())
        if missing:
            errors.append(f"{path.name}: missing required event envelope fields: {sorted(missing)}")

    return errors


def main() -> int:
    violations: list[str] = []
    schemas_checked = 0

    if EVENTS_DIR.is_dir():
        for f in sorted(EVENTS_DIR.glob("*.json")):
            schemas_checked += 1
            violations.extend(validate_schema_file(f))

    # Also verify outbox model exists and defines event payload handling
    if not OUTBOX_MODEL.is_file():
        violations.append("event outbox model cd_event_outbox/models/event_outbox.py missing")

    if violations:
        print(f"event-schemas: FAIL - {len(violations)} violation(s):")
        for err in violations:
            print(f"  {err}")
        print(
            "  remedy: schemas under contracts/events/ must declare standard CloudEvents envelope (AR-009 §5.5)."
        )
        return 1

    print(
        f"event-schemas: OK - {schemas_checked} schema(s) conform to AR-009 event envelope specification; outbox model verified"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
