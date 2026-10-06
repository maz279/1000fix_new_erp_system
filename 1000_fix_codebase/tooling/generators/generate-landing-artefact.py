#!/usr/bin/env python3
"""generate-landing-artefact — PP5 landing/marketing shell data.

Extracts the 12 portal cards + 10 journey strips from the frozen
navigation registry (contracts/nav/registry.json) into a small landing
artefact (libs/ts/i18n/src/landing.generated.json) the shared
LandingShell consumes. Navigation-only extraction — no screens, no
functions, no data (keeps the customer bundle under its 400KB budget:
the full registry is ~1MB, this artefact is a few KB).

Regenerate after registry changes:
    python tooling/generators/generate-landing-artefact.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "contracts" / "nav" / "registry.json"
OUT = REPO / "libs" / "ts" / "i18n" / "src" / "landing.generated.json"


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    landing = {
        "$description": "Landing/marketing shell data — PP5. Generated from "
                        "contracts/nav/registry.json (portals + journeys only; "
                        "navigation, not data). Do not hand-edit.",
        "portals": [
            {
                "id": p["id"],
                "en": p["name"],
                "users": p.get("users", ""),
                "volume": p.get("volume", ""),
                "capabilities": p.get("capabilities", [])[:4],
            }
            for p in registry.get("portals", [])
        ],
        "journeys": [
            {
                "id": j["id"],
                "en": j["en"],
                "bn": j.get("bn", ""),
                "steps": [
                    {"actor": s.get("actor", ""), "desc": s.get("desc", "")}
                    for s in j.get("steps", [])[:6]
                ],
            }
            for j in registry.get("journeys", [])
        ],
    }
    landing["counts"] = {
        "portals": len(landing["portals"]),
        "journeys": len(landing["journeys"]),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(landing, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"landing artefact: {landing['counts']['portals']} portals, "
          f"{landing['counts']['journeys']} journeys -> {OUT.relative_to(REPO)} "
          f"({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
