"""GV-009: tooling/gate/verify-gate-g5/g6/g7/g8.ps1 derive every DR (PE-007)
criterion from the drill evidence JSON - PASS only when the evidence verdict
is PASS with RPO and RTO measured, RPO/RTO printed from the evidence (or
UNMEASURED when null) - and no RPO/RTO number, "verified"/"certified" claim or
unconditional PASS is hard-coded in the scripts.

The behavioural tests extract the scripts' own helper functions with the
PowerShell parser and run them against temporary evidence files; they need
powershell.exe and are skipped where it is absent. Nothing here touches the
network, a database or the real evidence files."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_DIR = REPO_ROOT / "tooling" / "gate"

# gate script -> (its PE-007 drill evidence file, the drill's verdict key,
# the drill's metrics block, the RPO key, the RTO key)
GATES = {
    "verify-gate-g5.ps1": (
        "g5-pe007-dr-drill-evidence.json",
        "status",
        "sla_metrics",
        "rpo_achieved_seconds",
        "rto_achieved_seconds",
    ),
    "verify-gate-g6.ps1": (
        "g6-pe007-dr-drill-evidence.json",
        "overall_status",
        "metrics",
        "rpo_achieved_seconds",
        "rto_achieved_seconds",
    ),
    "verify-gate-g7.ps1": (
        "g7-pe007-dr-drill-evidence.json",
        "verdict",
        "metrics",
        "rpo_measured_seconds",
        "rto_measured_seconds",
    ),
    "verify-gate-g8.ps1": (
        "g8-pe007-full-estate-dr-drill-evidence.json",
        "verdict",
        "measured_metrics",
        "rpo_measured_seconds",
        "rto_measured_seconds",
    ),
}

# "RPO 0s", "RPO=0s", "RTO: 42.4s", "RTO 36.5" ... anywhere in the script.
HARD_CODED_RPO_RTO = re.compile(r"\bR[PT]O\s*[=:]?\s*\d")
HELPERS = (
    "Read-EvidenceJson",
    "Get-EvidenceVerdict",
    "Get-OutcomeFromVerdicts",
    "Format-Measured",
    "Get-DrMetric",
    "Get-DrDrill",
)

HARNESS = r"""
param([string]$GateScript, [string]$EvidenceDir)
$ErrorActionPreference = 'Stop'
$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($GateScript, [ref]$tokens, [ref]$errors)
if ($errors.Count -gt 0) { throw "parse errors in $GateScript" }
$wanted = @(%(helpers)s)
$defs = $ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)
foreach ($d in $defs) { if ($wanted -contains $d.Name) { . ([scriptblock]::Create($d.Extent.Text)) } }
$out = [ordered]@{}
$out.defined = @($wanted | Where-Object { Get-Command $_ -CommandType Function -ErrorAction SilentlyContinue })
foreach ($case in @('fail', 'pass', 'pass_unmeasured', 'incomplete', 'missing')) {
    $dr = Get-DrDrill (Join-Path $EvidenceDir "$case.json")
    $out[$case] = [ordered]@{
        verdict = $dr.Verdict
        text = $dr.Text
        outcome = (Get-OutcomeFromVerdicts @('PASS', $dr.Verdict) 'CONDITION')
        outcome_missing_fail = (Get-OutcomeFromVerdicts @('PASS', $dr.Verdict) 'FAIL')
    }
}
$out.mapping = [ordered]@{
    all_pass = (Get-OutcomeFromVerdicts @('PASS', 'PASS') 'CONDITION')
    fail_wins = (Get-OutcomeFromVerdicts @('FAIL', 'MISSING', 'PASS') 'CONDITION')
    incomplete = (Get-OutcomeFromVerdicts @('PASS', 'INCOMPLETE') 'FAIL')
    unknown = (Get-OutcomeFromVerdicts @('PASS', 'UNKNOWN') 'FAIL')
    empty = (Get-OutcomeFromVerdicts @() 'FAIL')
}
$out | ConvertTo-Json -Depth 4
""".replace("%(helpers)s", ", ".join(f"'{h}'" for h in HELPERS))


def _source(script: str) -> str:
    return (GATE_DIR / script).read_bytes().decode("utf-8-sig")


@pytest.mark.parametrize("script", sorted(GATES))
def test_no_hard_coded_rpo_rto_or_claims(script):
    text = _source(script)
    assert HARD_CODED_RPO_RTO.findall(text) == []
    assert re.findall(r"(?i)certified|\bverified\b(?! CAPA)", text) == []
    # an unconditional top-level PASS is a hard-coded verdict
    assert re.findall(r"(?m)^Result 'PASS'", text) == []
    # 'passed' next to failures is not a pass: pytest outcomes use the exit code
    assert "-match 'passed'" not in text


@pytest.mark.parametrize("script", sorted(GATES))
def test_reads_its_drill_evidence(script):
    evidence_file = GATES[script][0]
    text = _source(script)
    assert evidence_file in text
    assert "ConvertFrom-Json" in text
    assert "Get-DrDrill" in text
    for helper in HELPERS:
        assert f"function {helper}(" in text or f"function {helper} " in text


@pytest.mark.parametrize("script", sorted(GATES))
def test_script_is_ascii(script):
    raw = (GATE_DIR / script).read_bytes()
    # Windows PowerShell 5.1 reads a BOM-less script as ANSI: keep it ASCII.
    assert raw.startswith(b"\xef\xbb\xbf") or raw.isascii()


def _powershell() -> str | None:
    return shutil.which("powershell") or shutil.which("pwsh")


def _write_cases(directory: Path, script: str) -> None:
    _, verdict_key, block, rpo_key, rto_key = GATES[script]
    cases = {
        "fail": ("FAIL", None, None),
        "pass": ("PASS", 3, 42),
        "pass_unmeasured": ("PASS", None, 42),
        "incomplete": ("INCOMPLETE", None, None),
    }
    for name, (verdict, rpo, rto) in cases.items():
        evidence = {
            verdict_key: verdict,
            block: {rpo_key: rpo, rto_key: rto, "data_loss_records": None},
            "summary": {
                "checks_total": 4,
                "checks_passed": 2,
                "checks_failed": 1,
                "checks_unmeasured": 1,
            },
        }
        (directory / f"{name}.json").write_bytes(json.dumps(evidence).encode("utf-8"))


@pytest.fixture(params=sorted(GATES))
def helper_run(request, tmp_path):
    exe = _powershell()
    if exe is None:
        pytest.skip("powershell is not available on this host")
    script = request.param
    _write_cases(tmp_path, script)
    harness = tmp_path / "harness.ps1"
    harness.write_bytes(HARNESS.encode("ascii"))
    proc = subprocess.run(
        [
            exe,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(harness),
            str(GATE_DIR / script),
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        pytest.fail(f"harness failed for {script}: {proc.stderr}")
    return script, json.loads(proc.stdout)


def test_helpers_are_defined(helper_run):
    _, out = helper_run
    assert sorted(out["defined"]) == sorted(HELPERS)


def test_fail_evidence_is_fail_with_unmeasured_rpo_rto(helper_run):
    _, out = helper_run
    case = out["fail"]
    assert case["verdict"] == "FAIL"
    assert case["outcome"] == "FAIL"
    assert "RPO=UNMEASURED" in case["text"]
    assert "RTO=UNMEASURED" in case["text"]
    assert "verdict=FAIL" in case["text"]


def test_pass_evidence_prints_measured_rpo_rto(helper_run):
    script, out = helper_run
    case = out["pass"]
    assert case["verdict"] == "PASS"
    assert case["outcome"] == "PASS"
    assert "RPO=3s" in case["text"]
    assert "RTO=42s" in case["text"]
    assert GATES[script][0] not in case["text"]  # temp file, not the real evidence
    assert "2 PASS / 1 FAIL / 1 UNMEASURED of 4 checks" in case["text"]


def test_pass_verdict_without_measured_rpo_is_not_pass(helper_run):
    _, out = helper_run
    case = out["pass_unmeasured"]
    assert case["verdict"] == "INCOMPLETE"
    assert case["outcome"] == "CONDITION"
    assert "RPO=UNMEASURED" in case["text"]
    assert "RTO=42s" in case["text"]


def test_incomplete_evidence_is_condition(helper_run):
    _, out = helper_run
    assert out["incomplete"]["verdict"] == "INCOMPLETE"
    assert out["incomplete"]["outcome"] == "CONDITION"


def test_missing_evidence_uses_the_gates_missing_outcome(helper_run):
    _, out = helper_run
    case = out["missing"]
    assert case["verdict"] == "MISSING"
    assert case["outcome"] == "CONDITION"
    assert case["outcome_missing_fail"] == "FAIL"
    assert "RPO=UNMEASURED" in case["text"]


def test_outcome_mapping(helper_run):
    _, out = helper_run
    assert out["mapping"] == {
        "all_pass": "PASS",
        "fail_wins": "FAIL",
        "incomplete": "CONDITION",
        "unknown": "CONDITION",
        "empty": "CONDITION",
    }
