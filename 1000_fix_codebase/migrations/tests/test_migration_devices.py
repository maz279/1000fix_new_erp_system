"""ETL-2 device loader rules that need no database (migrations/load_devices.py).

- warranty state is derived from the evidenced end date relative to the LOAD date
- the Wave-1 device extract carries a real duplicate serial, so the MDM
  quarantine path is exercised by every rehearsal (DB side: test_migration_wave1)
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from migrations.extracts_generator import compute_sha256
from migrations.load_devices import derive_warranty_status

EXTRACTS_DIR = Path(__file__).resolve().parents[1] / "extracts"


@pytest.mark.parametrize(
    ("end", "load_date", "expected"),
    [
        ("2026-06-15", date(2026, 10, 22), "out_of_warranty"),  # the Wave-1 extract case
        ("2026-06-15", date(2026, 6, 15), "in_warranty"),  # last day still covered
        ("2026-06-15", date(2026, 6, 16), "out_of_warranty"),
        ("2027-01-31", date(2026, 10, 22), "in_warranty"),
        (date(2026, 12, 31), date(2026, 10, 22), "in_warranty"),
        (None, date(2026, 10, 22), "unknown"),
        ("", date(2026, 10, 22), "unknown"),
    ],
)
def test_derive_warranty_status(end, load_date, expected):
    assert derive_warranty_status(end, load_date) == expected


def test_device_extract_has_a_real_duplicate_serial():
    devices = json.loads((EXTRACTS_DIR / "devices_extract.json").read_text(encoding="utf-8"))
    serials = Counter(d["serial_number"] for d in devices)
    duplicates = {s: n for s, n in serials.items() if n > 1}
    assert duplicates == {"SN-OPP-2026001": 2}
    first, dup = (d for d in devices if d["serial_number"] == "SN-OPP-2026001")
    assert (first["source_id"], dup["source_id"]) == ("DEV-AST-2001", "DEV-AST-2050")
    assert first["imei_1"] != dup["imei_1"]  # a mis-keyed serial, not the same asset


def test_device_control_total_matches_extract():
    """MIG-02: the manifest counts every extracted device, the duplicate included."""
    manifest = json.loads((EXTRACTS_DIR / "control-totals.json").read_text(encoding="utf-8"))
    path = EXTRACTS_DIR / "devices_extract.json"
    assert manifest["control_totals"]["devices"] == len(json.loads(path.read_text("utf-8"))) == 50
    assert manifest["checksums"]["devices"] == compute_sha256(path)
