#!/usr/bin/env python3
"""generate_event_schemas.py — the domain event registry, derived from the publishing code.

Realises Task R10-M03-T02, FF-19, AR-009 §5.5, and AS-08.

The registry (contracts/events/master-event-registry.json) lists EVERY event type the code
publishes through ``libs.py.fix_events.publish()`` - found statically by
``event_publishers.scan_publishers`` (direct calls, wrapper helpers, literal variables) -
with its owner module, Kafka topic (``map_topic_for_event``), schema version and a JSON
schema per event whose payload is derived from the publish() payload dict (field names
and types).

Code is the source of truth:
* a curated (hand-written) schema is kept while its payload keys equal what the code
  publishes; when it contradicts the code it is re-derived and its major version bumped;
* curated contracts no code publishes move to contracts/events/planned/ (and move back
  automatically once a publisher exists).

Usage:
    python tooling/generators/generate_event_schemas.py           # regenerate
    python tooling/generators/generate_event_schemas.py --check   # exit 1 on drift
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EVENTS_DIR = REPO_ROOT / "contracts" / "events"
PLANNED_DIR_NAME = "planned"
PLANNED_REGISTER = "planned-event-register.json"
ADDONS_DIR = REPO_ROOT / "addons"
REGISTRY_FILE = "master-event-registry.json"
# Files in contracts/events/ that are registers, not event schemas.
NON_SCHEMA_FILES = {REGISTRY_FILE, "portal-event-reconciliation-register.json"}

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from event_publishers import PublishSite, merge_payloads, producer_of, scan_publishers

from libs.py.fix_events.kafka_bus import map_topic_for_event

DERIVED_MARKER = "publish() call AST (tooling/generators/generate_event_schemas.py)"


def derived_schema(
    event_type: str,
    producer: str,
    sites: list[PublishSite],
    payload: dict[str, Any],
    curated_description: str | None = None,
) -> dict[str, Any]:
    paths = sorted({s.path for s in sites})
    via = "publish_dual()" if all(p.startswith("services/") for p in paths) else "publish()"
    description = (f"{curated_description} " if curated_description else "") + (
        f"Published by {producer} through libs.py.fix_events.{via} "
        f"({len(sites)} call site(s)); payload derived from the publishing code."
    )
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": event_type,
        "description": description,
        "type": "object",
        "required": ["event_id", "event_type", "timestamp", "producer", "payload"],
        "properties": {
            "event_id": {
                "type": "string",
                "format": "uuid",
                "description": "Unique event identifier for idempotency (UUIDv4)",
            },
            "event_type": {"type": "string", "const": event_type},
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "ISO-8601 UTC timestamp",
            },
            "producer": {"type": "string", "default": producer},
            "payload": payload,
        },
        "x-owner-module": producer,
        "x-publishers": paths,
        "x-derived-from": DERIVED_MARKER,
        **({"x-curated-description": curated_description} if curated_description else {}),
    }


def bump_version(version: str, old_payload: dict[str, Any], new_payload: dict[str, Any]) -> str:
    """Semver for a re-derived payload: additive change -> minor, anything else -> major."""
    if old_payload == new_payload:
        return version
    major, minor, _patch = (int(x) for x in version.split("."))
    old_props, new_props = old_payload.get("properties") or {}, new_payload.get("properties") or {}
    additive = (
        all(new_props.get(k) == v for k, v in old_props.items())
        and set(new_payload.get("required") or [])
        <= set(old_payload.get("required") or []) | (set(new_props) - set(old_props))
        and old_payload.get("additionalProperties") == new_payload.get("additionalProperties")
    )
    return f"{major}.{minor + 1}.0" if additive else f"{major + 1}.0.0"


def _payload_keys(schema: dict[str, Any]) -> set[str]:
    return set(((schema.get("properties") or {}).get("payload") or {}).get("properties") or {})


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def build_contracts(
    addons_dir: Path = ADDONS_DIR,
    events_dir: Path = EVENTS_DIR,
    services_dir: Path | None = None,
) -> tuple[dict[Path, dict[str, Any]], dict[str, Any]]:
    """(files to write -> contents, report) for every event type the code publishes.

    ``services_dir`` defaults to the ``services/`` next to ``addons_dir``.
    """
    scan = scan_publishers(addons_dir, services_dir or addons_dir.parent / "services")
    planned_dir = events_dir / PLANNED_DIR_NAME
    registry_path = events_dir / REGISTRY_FILE
    old_entries = {e["event_type"]: e for e in (_read_json(registry_path) or {}).get("events", [])}

    outputs: dict[Path, dict[str, Any]] = {}
    entries: list[dict[str, Any]] = []
    kept: list[str] = []
    derived: list[str] = []
    corrected: list[str] = []
    revived: list[str] = []
    for event_type in sorted(scan.sites):
        sites = scan.sites[event_type]
        producer = producer_of(sites)
        filename = event_type.replace(".", "_") + ".json"
        path = events_dir / filename
        payload = merge_payloads(sites)
        current = _read_json(path)
        if current is None and (planned := _read_json(planned_dir / filename)) is not None:
            current = planned  # a planned contract whose publisher now exists
            revived.append(event_type)
        version = old_entries.get(event_type, {}).get("schema_version", "1.0.0")
        curated = current is not None and "x-derived-from" not in current
        if curated and _payload_keys(current) == set(payload.get("properties") or {}):
            source = "curated"
            kept.append(event_type)
            if event_type in revived:
                outputs[path] = current
        else:
            source = "derived"
            if curated:  # the curated contract contradicts the code: breaking correction
                description = current.get("description")
                version = f"{int(version.split('.')[0]) + 1}.0.0"
                corrected.append(event_type)
            else:
                description = (current or {}).get("x-curated-description")
                if current is not None:
                    old_payload = (current.get("properties") or {}).get("payload") or {}
                    version = bump_version(version, old_payload, payload)
                derived.append(event_type)
            outputs[path] = derived_schema(event_type, producer, sites, payload, description)
        entries.append(
            {
                "event_type": event_type,
                "producer": producer,
                "filename": filename,
                "kafka_topic": map_topic_for_event(event_type),
                "schema_version": version,
                "schema_source": source,
            }
        )

    published = set(scan.sites)
    planned = sorted(
        p.name
        for p in events_dir.glob("*.json")
        if p.name not in NON_SCHEMA_FILES and (_read_json(p) or {}).get("title") not in published
    )
    outputs[registry_path] = {
        "title": "1000FiX ERP Domain Event Schema Master Registry",
        "description": (
            "Every event type the code publishes through libs.py.fix_events (publish() in the Odoo addons, publish_dual() in the L5 services), with "
            "its owner module, Kafka topic and payload schema (AS-08). Generated by "
            "tooling/generators/generate_event_schemas.py from the publish() calls - never "
            "hand-edited. Contracts no code publishes yet live in planned/."
        ),
        "total_registered_events": len(entries),
        "kafka_topics": sorted({e["kafka_topic"] for e in entries}),
        "events": entries,
    }
    report = {
        "registered": len(entries),
        "curated_kept": kept,
        "derived": derived,
        "curated_corrected": corrected,
        "revived_from_planned": revived,
        "planned": planned,
        "composed_event_types": scan.composed,
        "unresolved": scan.unresolved,
    }
    return outputs, report


def _serialise(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _update_planned(events_dir: Path, report: dict[str, Any]) -> None:
    """Move unpublished contracts to planned/ and drop revived ones from it."""
    planned_dir = events_dir / PLANNED_DIR_NAME
    if not report["planned"] and not report["revived_from_planned"]:
        return
    planned_dir.mkdir(exist_ok=True)
    register_path = planned_dir / PLANNED_REGISTER
    register = _read_json(register_path) or {
        "title": "Planned (not yet published) domain event contracts",
        "description": (
            "Curated contracts no code publishes yet. The generator moves one back to "
            "contracts/events/ as soon as a publish() call for it exists."
        ),
        "events": [],
    }
    events = {e["filename"]: e for e in register.get("events", [])}
    for name in report["planned"]:
        source = events_dir / name
        schema = _read_json(source) or {}
        (planned_dir / name).write_text(_serialise(schema), encoding="utf-8")
        source.unlink()
        events[name] = {"event_type": schema.get("title"), "filename": name, "status": "planned"}
    for event_type in report["revived_from_planned"]:
        name = event_type.replace(".", "_") + ".json"
        (planned_dir / name).unlink(missing_ok=True)
        events.pop(name, None)
    register["events"] = sorted(events.values(), key=lambda e: str(e["event_type"]))
    register_path.write_text(_serialise(register), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Regenerate the registry from the code; ``--check`` only reports drift (exit 1)."""
    args = sys.argv[1:] if argv is None else argv
    outputs, report = build_contracts()
    stale = [p for p, data in outputs.items() if _read_json(p) != data]
    print(
        f"event registry: {report['registered']} published event types "
        f"({len(report['curated_kept'])} curated kept, {len(report['derived'])} derived, "
        f"{len(report['curated_corrected'])} curated corrected to match the code); "
        f"{len(report['planned'])} unpublished contract(s) for planned/"
    )
    for item in report["composed_event_types"]:
        print(f"  [WARN] event type composed at run time, not registrable: {item}")
    for item in report["unresolved"]:
        print(f"  [WARN] {item}")
    if "--check" in args:
        drift = [p.name for p in stale] + [f"planned:{n}" for n in report["planned"]]
        for name in drift:
            print(f"  [DRIFT] {name}")
        return 1 if drift else 0
    for path in stale:
        path.write_text(_serialise(outputs[path]), encoding="utf-8")
    _update_planned(EVENTS_DIR, report)
    print(f"  wrote {len(stale)} file(s); moved {len(report['planned'])} to planned/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
