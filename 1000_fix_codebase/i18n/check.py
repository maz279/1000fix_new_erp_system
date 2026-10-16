#!/usr/bin/env python3
"""i18n.check — Localisation completeness and parity verifier (DoD-08, DE-17, stage 10).

Usage:
    python -m i18n.check --completeness 100
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APPS_DIR = REPO_ROOT / "apps" / "web"


def load_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify translation completeness")
    parser.add_argument("--completeness", type=float, default=100.0,
                        help="Required completeness percentage (0-100)")
    parser.add_argument("--allow-baseline", action="store_true",
                        help="Record baseline measurement without failing")
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    total_keys = 0
    translated_keys = 0
    portal_count = 0
    missing_details: list[str] = []

    if APPS_DIR.is_dir():
        for app_dir in sorted(APPS_DIR.iterdir()):
            if not app_dir.is_dir():
                continue
            locales_dir = app_dir / "locales"
            messages_dir = app_dir / "messages"
            target_dir = locales_dir if locales_dir.is_dir() else (messages_dir if messages_dir.is_dir() else None)
            if not target_dir:
                continue

            en_file = target_dir / "en.json"
            bn_file = target_dir / "bn.json"
            if not en_file.is_file():
                continue

            portal_count += 1
            en_data = load_json(en_file)
            bn_data = load_json(bn_file) if bn_file.is_file() else {}

            app_keys = len(en_data)
            total_keys += app_keys
            app_translated = len(set(en_data.keys()) & set(bn_data.keys()))
            translated_keys += app_translated

            missing = set(en_data.keys()) - set(bn_data.keys())
            if missing:
                missing_details.append(f"{app_dir.name}: {len(missing)}/{app_keys} keys missing in bn.json")

    pct = (translated_keys / total_keys * 100.0) if total_keys > 0 else 100.0
    print(f"i18n.check: MEASURED completeness = {pct:.1f}% ({translated_keys}/{total_keys} keys across {portal_count} portal(s)) — Target: {args.completeness:.1f}%")

    if pct < args.completeness:
        print(f"i18n.check: FAIL — completeness {pct:.1f}% is below required threshold {args.completeness:.1f}%", file=sys.stderr)
        for detail in missing_details:
            print(f"  {detail}", file=sys.stderr)
        if args.allow_baseline:
            print("i18n.check: --allow-baseline specified, passing for measurement baseline")
            return 0
        return 1

    print("i18n.check: OK — localisation completeness meets threshold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
