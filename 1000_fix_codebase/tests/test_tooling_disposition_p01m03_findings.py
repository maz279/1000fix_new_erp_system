"""GV-009: disposition_p01m03_findings.py derives every status - undeclared
priorities FAIL, --dry-run never rewrites the register, an unrunnable FF-14
extractor is UNMEASURED, the Change Board ratification is never asserted, and
each RTM file is measured from its CR register, the RTM seed and the disk."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "disposition_p01m03_findings.py"


def _load():
    spec = importlib.util.spec_from_file_location("disposition_p01m03_findings_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

REGISTER = (
    '"﻿""requirement""",module,wave,multi_wave,layer,priority,disposition,note\n'
    "FR-X-001,M19,W1,False,L1,P0,fit,seed\n"
    "FR-X-002,M13,W3,False,L1,,fit,seed\n"
    "FR-X-003,M05,W4,False,L1,,fit,seed\n"
)

SEED = '﻿"requirement","module","wave"\n' '"FR-T-001","M99","W1"\n' '"FR-T-002","M99","W1"\n'


def _cr_doc(ref: str) -> str:
    return (
        "| Req ID | Name | Layer | Delivered Unit | Verification |\n"
        "|---|---|---|---|---|\n"
        "| `FR-T-001` | One | L4 | Unit A | `services/unit_a` |\n"
        f"| `FR-T-002` | Two | L4 | Unit A | `{ref}` |\n"
    )


SPEC = {
    "module_id": "M99",
    "task": "T-UT",
    "cr_id": "CR-UT",
    "title": "unit-test RTM",
    "prefix": "FR-T",
    "file": "rtm-ut.json",
    "delivery_units": [("services/unit_a", None, "unit a")],
}


def _tree(root: Path, ref: str) -> None:
    (root / "services" / "unit_a").mkdir(parents=True)
    (root / "docs" / "r10").mkdir(parents=True)
    (root / "docs" / "p01-m03" / "registers").mkdir(parents=True)
    (root / "docs" / "r10" / "CR-module-register-M99.md").write_text(_cr_doc(ref), encoding="utf-8")
    (root / "docs" / "p01-m03" / "registers" / "rtm-seed.csv").write_text(SEED, encoding="utf-8")


class TestPriorityDisposition(unittest.TestCase):
    def test_dry_run_counts_undeclared_and_never_rewrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "fit-gap.csv"
            reg.write_bytes(REGISTER.encode("utf-8"))
            before = reg.read_bytes()
            res = mod.measure_priorities(apply=False, register=reg)
            self.assertEqual(reg.read_bytes(), before)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(res["undeclared_before_run"], 2)
        self.assertEqual(res["undeclared_after_run"], 2)
        self.assertEqual(res["total_requirements"], 3)

    def test_apply_classifies_and_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "fit-gap.csv"
            reg.write_bytes(REGISTER.encode("utf-8"))
            res = mod.measure_priorities(apply=True, register=reg)
            again = mod.measure_priorities(apply=False, register=reg)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["classified_this_run"], 2)
        self.assertEqual(again["undeclared_before_run"], 0)
        self.assertEqual(again["rows_carrying_r10_m02_disposition_marker"], 2)
        self.assertEqual(again["priority_distribution"], {"P0": 1, "P1": 1, "P2": 1})


class TestReciprocityAndVerdict(unittest.TestCase):
    def test_no_powershell_is_unmeasured(self):
        orig = mod._powershell
        mod._powershell = lambda: None
        try:
            res = mod.measure_reciprocity()
        finally:
            mod._powershell = orig
        self.assertEqual(res["status"], "UNMEASURED")

    def test_ratification_keeps_verdict_from_pass(self):
        ev = mod.build_disposition(
            {"status": "PASS", "total_requirements": 3},
            {"status": "PASS", "reciprocity_measured": 53},
        )
        self.assertEqual(ev["checks"]["change_board_ratification"]["status"], "UNMEASURED")
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(ev["open_findings_remaining"], 0)

    def test_failed_check_reopens_finding_and_fails(self):
        ev = mod.build_disposition(
            {"status": "FAIL", "total_requirements": 3, "undeclared_after_run": 2},
            {"status": "UNMEASURED", "reason": "no powershell"},
        )
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(ev["open_findings_remaining"], 2)
        states = {f["id"]: f["state"] for f in ev["findings"]}
        self.assertEqual(states, {"F-P01M03-4": "OPEN", "F-P01M04-2": "UNVERIFIED"})
        md = mod.render_register(ev)
        self.assertNotIn("RATIFIED", md)
        self.assertIn("**FAIL**", md)


class TestRtmMeasurement(unittest.TestCase):
    def test_all_traced_is_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "services/unit_a")
            data = mod.measure_rtm(SPEC, root=root)
        self.assertEqual(data["verdict"], "PASS", data["failures"])
        self.assertEqual(data["requirements_count"], 2)

    def test_broken_path_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "infra/observability/missing")
            data = mod.measure_rtm(SPEC, root=root)
        self.assertEqual(data["verdict"], "FAIL")
        self.assertEqual(data["requirements_count"], 1)
        self.assertEqual(
            data["broken_path_references"], {"FR-T-002": ["infra/observability/missing"]}
        )

    def test_red_break_test_fails(self):
        spec = dict(SPEC, break_test="tests/test_break.py")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _tree(root, "services/unit_a")
            data = mod.measure_rtm(spec, root=root, pytest_fn=lambda _t: {"status": "FAIL"})
        self.assertFalse(data["pair_10_break_verified"])
        self.assertEqual(data["verdict"], "FAIL")

    def test_main_dry_run_exit_code_is_derived(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            saved = {
                k: getattr(mod, k)
                for k in (
                    "DISPOSITION_MD",
                    "DISPOSITION_EVIDENCE",
                    "measure_priorities",
                    "measure_reciprocity",
                    "generate_rtm_evidence_files",
                )
            }
            seen = {}

            def fake_priorities(apply):
                seen["apply"] = apply
                return {"status": "PASS", "total_requirements": 1}

            mod.DISPOSITION_MD = out / "register.md"
            mod.DISPOSITION_EVIDENCE = out / "evidence.json"
            mod.measure_priorities = fake_priorities
            mod.measure_reciprocity = lambda: {"status": "PASS", "reciprocity_measured": 53}
            mod.generate_rtm_evidence_files = lambda: [
                {"module_id": "M99", "verdict": "PASS", "requirements_count": 1}
                | {"requirements_in_cr_register": 1, "failures": []}
            ]
            try:
                code = mod.main(["--dry-run"])
            finally:
                for k, v in saved.items():
                    setattr(mod, k, v)
            data = json.loads((out / "evidence.json").read_text(encoding="utf-8"))
        self.assertFalse(seen["apply"])
        self.assertEqual(data["verdict"], "INCOMPLETE")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
