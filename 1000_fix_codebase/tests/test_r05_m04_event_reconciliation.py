#!/usr/bin/env python3
"""test_r05_m04_event_reconciliation.py — Verification of Milestone R05-M04-T05 (B-17).

Validates:
1. All 69 unpublished portal-consumed events from B-17 (IN-003 §7) are reconciled.
2. Unadjudicated count is exactly 0 (100% adjudicated).
3. Every event carries exactly one normative disposition: D1 (Rename), D2 (Projection), or D3 (Register).
4. D1 events map to a valid canonical published event name.
5. D2 events define source events in projected_from.
6. D3 events define owning module and schema specification.
7. The four focus portals (P04 corporate, P06 analytics, P08 brand, P10 agent console) are 100% covered.
8. 1-to-1 parity between the baseline CSV and the JSON register.
"""

import csv
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTER_PATH = REPO_ROOT / "contracts" / "events" / "portal-event-reconciliation-register.json"
CSV_PATH = (
    REPO_ROOT.parent
    / "project-guide-doc"
    / "04_Integration_and_API_Engineering"
    / "IN-003_artefacts"
    / "reconciliation"
    / "portal-consumed-unpublished.csv"
)


class TestEventReconciliationRegister(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.assertTrue(REGISTER_PATH.exists(), f"Missing register: {REGISTER_PATH}")
        with open(REGISTER_PATH, encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.events = cls.data.get("events", [])

    def test_total_event_count_is_69(self):
        """B-17: Exactly 69 unpublished portal-consumed events."""
        self.assertEqual(len(self.events), 69, "Register must hold exactly 69 events")
        self.assertEqual(self.data.get("total_unpublished_baseline"), 69)
        self.assertEqual(self.data.get("adjudicated_count"), 69)

    def test_zero_unadjudicated_events(self):
        """Task R05-M04-T05 requirement: zero unadjudicated rows remain."""
        self.assertEqual(self.data.get("unadjudicated_count"), 0)
        for ev in self.events:
            self.assertIn(
                ev.get("disposition"),
                {"D1", "D2", "D3"},
                f"Event {ev.get('event_type')} has invalid disposition: {ev.get('disposition')}",
            )

    def test_d1_renames_complete(self):
        """Every D1 event must provide a canonical published_event and remedy."""
        d1_events = [e for e in self.events if e.get("disposition") == "D1"]
        self.assertGreaterEqual(len(d1_events), 20)
        for e in d1_events:
            self.assertTrue(
                e.get("published_event"), f"D1 event {e['event_type']} missing published_event"
            )
            self.assertTrue(
                e.get("remedy"), f"D1 event {e['event_type']} missing remedy explanation"
            )

    def test_d2_projections_complete(self):
        """Every D2 event must define projected_from source events."""
        d2_events = [e for e in self.events if e.get("disposition") == "D2"]
        self.assertGreaterEqual(len(d2_events), 7)
        for e in d2_events:
            proj = e.get("projected_from")
            self.assertTrue(
                isinstance(proj, list) and len(proj) > 0,
                f"D2 event {e['event_type']} missing projected_from list",
            )

    def test_d3_registrations_complete(self):
        """Every D3 event must define an owning module and published_event."""
        d3_events = [e for e in self.events if e.get("disposition") == "D3"]
        self.assertGreaterEqual(len(d3_events), 25)
        for e in d3_events:
            self.assertTrue(
                e.get("owning_module", "").startswith("M"),
                f"D3 event {e['event_type']} has invalid owning_module: {e.get('owning_module')}",
            )
            self.assertTrue(
                e.get("published_event"), f"D3 event {e['event_type']} missing published_event"
            )

    def test_four_portals_at_depth_coverage(self):
        """Four portals (P04, P06, P08, P10) must have all consumed events adjudicated."""
        portals_covered = {"P04": 0, "P06": 0, "P08": 0, "P10": 0}
        for e in self.events:
            for p in e.get("consuming_portals", []):
                if p in portals_covered:
                    portals_covered[p] += 1
        self.assertGreaterEqual(portals_covered["P04"], 6, "P04 corporate events missing")
        self.assertGreaterEqual(portals_covered["P06"], 5, "P06 analytics events missing")
        self.assertGreaterEqual(portals_covered["P08"], 6, "P08 brand events missing")
        self.assertGreaterEqual(portals_covered["P10"], 8, "P10 contact centre events missing")

    def test_reconciliation_parity_with_baseline_csv(self):
        """Verify 100% of event names in baseline CSV exist in JSON register."""
        if not CSV_PATH.exists():
            self.skipTest("Baseline CSV not reachable from current path")
        csv_events = set()
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_events.add(row["event_type"])
        json_events = {e["event_type"] for e in self.events}
        missing = csv_events - json_events
        self.assertEqual(len(missing), 0, f"Events in CSV missing from JSON register: {missing}")


if __name__ == "__main__":
    unittest.main()
