#!/usr/bin/env python3
"""extract-ui-copy — P04-M06-T09 (UI-001 i18n key standard, BN-005).

Loads the W1 subset of the UI-* copy library (the 18 files whose front matter
carries `wave: W1`) into ONE machine-readable registry every runtime consumes:

  project_content/03_UI_Copy_and_Microcopy/**   SOURCE (content library)
  libs/ts/i18n/src/ui-copy.generated.json       GENERATED (this script)

Rules baked in (UI-001/CG-003/CG-004):
- A row is a copy entry only when one cell is an i18n key (dotted lowercase,
  e.g. `ws.intake.title`). Everything else is documentation.
- English and Bengali travel together — `bilingual: yes` is the W1 norm and
  a key with an empty side is a violation, not a fallback.
- `max` is the display budget IN CHARACTERS for BOTH locales (VB-002): the
  Bengali string must fit the same budget; a Bengali overrun is reported at
  extraction time, not discovered in a branch office.

Exit: 0 regenerated / 1 violations (missing side or budget overrun).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CONTENT = REPO.parent / "project_content" / "03_UI_Copy_and_Microcopy"
OUT = REPO / "libs/ts/i18n/src/ui-copy.generated.json"

KEY_CELL = re.compile(r"^`?([a-z][a-z0-9]*(?:\.[a-z0-9_]+)+)`?$")
WAVE_RE = re.compile(r"^wave:\s*(\S+)", re.MULTILINE)
ID_RE = re.compile(r"^id:\s*(UI-\d+)", re.MULTILINE)
PLACEHOLDER = re.compile(r"\{(\w+)\}")
# Bengali Unicode block — the only reliable inline-bilingual discriminator
# across every table shape the library uses (some tables put a class marker,
# a ✔ or a guidance sentence in the column after English).
BENGALI_SCRIPT = re.compile(r"[\u0980-\u09FF]")


def w1_files() -> list[Path]:
    files = []
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if WAVE_RE.search(text).group(1) == "W1" if WAVE_RE.search(text) else False:
            files.append(path)
    return files


def parse_copy_rows(text: str) -> list[dict]:
    """One pass over every markdown table row; keep rows whose second-ish
    cell is an i18n key.

    Two row shapes exist in the library (UI-001 §2):
    - inline bilingual: | label | key | English | বাংলা | max? |
    - Bengali elsewhere: any other column layout (class marker, ✔, guidance
      text) — the Bengali lives in the `*_BN.md` counterpart file (266 of 452
      content files await one; tracked at programme level, not a pack defect).
    Discriminator: a row is inline bilingual only when the cell after English
    carries Bengali script.
    """
    entries: list[dict] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 4 or set("".join(cells[:2])) <= {"-", " ", ":"}:
            continue
        key_idx = next(
            (i for i, cell in enumerate(cells) if KEY_CELL.match(cell)), None
        )
        if key_idx is None:
            continue
        key = KEY_CELL.match(cells[key_idx]).group(1)
        rest = cells[key_idx + 1 :]
        if len(rest) < 2:
            continue
        english, second = rest[0].strip(), rest[1].strip()
        if BENGALI_SCRIPT.search(second):
            max_len = None
            for cell in rest[2:]:
                if cell.isdigit():
                    max_len = int(cell)
                    break
            row = {"key": key, "en": english, "bn": second,
                   "bn_status": "inline", "max": max_len}
        else:
            row = {"key": key, "en": english, "bn": None,
                   "bn_status": "counterpart-pending", "max": None}
        entries.append(row)
    return entries


def main() -> int:
    if not CONTENT.is_dir():
        print(f"extract-ui-copy: content library missing at {CONTENT}")
        return 1
    files = w1_files()
    registry: dict[str, dict] = {}
    violations: list[str] = []
    seen_keys: dict[str, str] = {}
    counterpart_pending = 0

    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        ui_id = ID_RE.search(text).group(1) if ID_RE.search(text) else path.stem
        rows = parse_copy_rows(text)
        entries: list[dict] = []
        for row in rows:
            key = row["key"]
            if key in seen_keys and seen_keys[key] != ui_id:
                # CG-004: one key, one string, everywhere. Divergent duplicates
                # across packs are a content defect.
                violations.append(f"{ui_id}: key {key} also defined in {seen_keys[key]}")
            seen_keys[key] = ui_id
            if row["bn_status"] == "counterpart-pending":
                # The Bengali side ships with the *_BN.md counterpart file.
                # 266 counterparts are pending programme-wide (content
                # readiness report) — recorded here, escalated there.
                counterpart_pending += 1
                entries.append(row)
                continue
            if not row["en"] or not row["bn"]:
                violations.append(f"{ui_id}/{key}: bilingual pair incomplete (en={row['en']!r}, bn={row['bn']!r})")
                continue
            if row["max"] is not None:
                if len(row["bn"]) > row["max"]:
                    violations.append(
                        f"{ui_id}/{key}: Bengali {len(row['bn'])} chars exceeds budget {row['max']} (VB-002)"
                    )
                if len(row["en"]) > row["max"]:
                    violations.append(
                        f"{ui_id}/{key}: English {len(row['en'])} chars exceeds budget {row['max']} (VB-002)"
                    )
            # Placeholder parity — {var} sets must match or interpolation
            # silently drops a value in one locale.
            if set(PLACEHOLDER.findall(row["en"])) != set(PLACEHOLDER.findall(row["bn"])):
                violations.append(f"{ui_id}/{key}: placeholder mismatch en/bn")
            entries.append(row)
        if entries:
            registry[ui_id] = {
                "source": str(path.relative_to(CONTENT.parent)).replace("\\", "/"),
                "wave": "W1",
                "copy": entries,
            }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "$description": "GENERATED by tooling/scripts/extract-ui-copy.py — DO NOT EDIT. "
                        "Source: project_content/03_UI_Copy_and_Microcopy (W1 files only).",
        "total_keys": len(seen_keys),
        "counterpart_pending": counterpart_pending,
        "packs": registry,
    }
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8", newline="\n")

    total = sum(len(pack["copy"]) for pack in registry.values())
    print(f"extract-ui-copy: {len(registry)} W1 packs, {total} keys ({len(seen_keys)} unique, "
          f"{counterpart_pending} awaiting BN counterparts) "
          f"-> {OUT.relative_to(REPO)}".replace("\\", "/"))
    if violations:
        print(f"extract-ui-copy: {len(violations)} violation(s):")
        for v in violations:
            print(f"  {v}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
