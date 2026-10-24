"""GV-009: audit_programme_controls.py reads and validates the gate evidence
(missing / non-PASS evidence is FAIL, never "PASS_READY"), derives open and
expired stubs from the register, measures the bypass controls, and derives
the opinion - which is never UNQUALIFIED while the sign-off is unobservable."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "audit_programme_controls.py"


def _load():
    spec = importlib.util.spec_from_file_location("audit_programme_controls_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()

HEADER = (
    "| Stub ID | From | Target | Wave | Mechanism | Suspense | Opened | Expiry | Target Date "
    "| Owner | Closure | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n"
)


def _stub(stub_id: str, target_date: str, status: str) -> str:
    return f"| `{stub_id}` | M1 | M2 | W1 | m | N/A | R01 | R02 | {target_date} | o | c | **{status}** |\n"


def _gate_tree(root: Path, verdicts: dict[str, object]) -> tuple[Path, list[Path]]:
    gate_dir, ev_dir = root / "gate", root / "evidence"
    gate_dir.mkdir()
    ev_dir.mkdir()
    for gate, script, _phase, _name in mod.REQUIRED_GATES:
        (gate_dir / script).write_text("# verifier\n", encoding="utf-8")
        if gate in verdicts and verdicts[gate] is not None:
            body = verdicts[gate]
            (ev_dir / f"gate-{gate.lower()}-latest.json").write_text(
                json.dumps(body), encoding="utf-8"
            )
    return gate_dir, [ev_dir]


GREEN = {"verdict": "PASS", "criteria": [{"Id": "x", "Status": "PASS"}]}


class TestGateChain(unittest.TestCase):
    def test_all_green_evidence_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            gate_dir, dirs = _gate_tree(Path(tmp), {g[0]: GREEN for g in mod.REQUIRED_GATES})
            res = mod.audit_gate_evidence_chain(gate_dir, dirs)
        self.assertEqual(res["status"], "PASS")
        self.assertEqual(res["gates_passed"], 12)

    def test_missing_or_red_evidence_fails(self):
        verdicts = {g[0]: GREEN for g in mod.REQUIRED_GATES}
        verdicts["G3"] = None  # no evidence at all
        verdicts["G2"] = {"verdict": "RED", "criteria": [{"Status": "CONDITION"}]}
        verdicts["G1"] = [{"Id": "G1-01", "Status": "PASS"}, {"Id": "G1-02", "Status": "CONDITION"}]
        with tempfile.TemporaryDirectory() as tmp:
            gate_dir, dirs = _gate_tree(Path(tmp), verdicts)
            res = mod.audit_gate_evidence_chain(gate_dir, dirs)
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual(sorted(res["gates_not_passed"]), ["G1", "G2", "G3"])
        self.assertNotIn("PASS_READY", json.dumps(res))

    def test_g1_evidence_never_matches_g1a(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "gate-g1a-latest.json").write_text("{}", encoding="utf-8")
            self.assertEqual(mod.find_gate_evidence("G1", [d]), [])
            self.assertEqual(len(mod.find_gate_evidence("G1a", [d])), 1)


class TestStubLedger(unittest.TestCase):
    def test_open_stub_past_target_date_is_expired_and_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "register.md"
            reg.write_text(
                HEADER
                + _stub("STUB-A-001", "2026-01-01", "CLOSED")
                + _stub("STUB-B-001", "2026-02-01", "OPEN"),
                encoding="utf-8",
            )
            res = mod.audit_gv005_stub_ledger(reg, today=date(2026, 10, 22))
        self.assertEqual(res["status"], "FAIL")
        self.assertEqual((res["open_stubs"], res["expired_stubs"]), (1, 1))

    def test_empty_register_is_unmeasured(self):
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "register.md"
            reg.write_text(HEADER, encoding="utf-8")
            res = mod.audit_gv005_stub_ledger(reg, today=date(2026, 10, 22))
        self.assertEqual(res["status"], "UNMEASURED")


class TestBypassAndOpinion(unittest.TestCase):
    def test_failing_ff09_run_fails_bypass_audit(self):
        def runner(cmd):
            if "check_ff09_residency.py" in cmd[-1]:
                return 1, "FF-09: FAIL - 2 residency bypass path(s) found:"
            return 0, "check-vendor-clean: OK"

        res = mod.audit_bypass_log(runner=runner)
        self.assertEqual(res["checks"]["ff09_residency"]["status"], "FAIL")
        self.assertEqual(res["checks"]["ff09_residency"]["residency_bypass_paths"], 2)
        self.assertEqual(res["checks"]["bypass_log_register"]["status"], "UNMEASURED")
        self.assertEqual(res["status"], "FAIL")

    def test_unrunnable_check_is_unmeasured(self):
        res = mod.audit_bypass_log(runner=lambda cmd: (None, "not runnable"))
        self.assertEqual(res["checks"]["ff09_residency"]["status"], "UNMEASURED")

    def test_bypass_markers_found_outside_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            wf = Path(tmp) / "ci.yml"
            wf.write_text(
                "jobs:\n  a:\n    # continue-on-error: true is banned\n"
                "    continue-on-error: true\n    steps:\n      - run: make lint || true\n",
                encoding="utf-8",
            )
            scanned, hits = mod.scan_bypass_markers([Path(tmp)])
        self.assertEqual(scanned, 1)
        self.assertEqual(len(hits), 2)

    def test_opinion_is_derived(self):
        clean = {"gate_chain": "PASS", "stub_ledger": "PASS"}
        self.assertEqual(
            mod.issue_internal_audit_opinion(clean)["audit_opinion"], "UNQUALIFIED_CLEAN_OPINION"
        )
        unsigned = dict(clean, audit_sign_off="UNMEASURED")
        self.assertEqual(
            mod.issue_internal_audit_opinion(unsigned)["audit_opinion"],
            "DISCLAIMER_INSUFFICIENT_EVIDENCE",
        )
        failed = dict(unsigned, gate_chain="FAIL")
        self.assertEqual(
            mod.issue_internal_audit_opinion(failed)["audit_opinion"],
            "QUALIFIED_OPINION_EXCEPTIONS_FOUND",
        )

    def test_evidence_verdict_never_pass_without_sign_off(self):
        gate = {"status": "PASS", "gates_passed": 12, "total_gates_audited": 12}
        gate.update(gates_not_passed=[], gates=[])
        stub = {"status": "PASS", "stubs": []}
        byp = {"checks": {"x": {"status": "PASS"}}, "status": "PASS"}
        ev = mod.build_evidence(gate, stub, byp)
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)
        self.assertNotIn("UNQUALIFIED", mod.render_markdown(ev))


if __name__ == "__main__":
    unittest.main()
