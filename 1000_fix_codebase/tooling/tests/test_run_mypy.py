"""run-mypy (ci.yml stage 2): verdict derivation - a mypy that never ran is never a pass."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RUNNER = Path(__file__).resolve().parents[1] / "ci" / "run-mypy.py"


@pytest.fixture(scope="module")
def rm():
    spec = importlib.util.spec_from_file_location("run_mypy", RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fake_mypy(monkeypatch, rm, returncode: int, output: str) -> list[list[str]]:
    calls: list[list[str]] = []

    def run(cmd, **kwargs):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, returncode, stdout=output, stderr="")

    monkeypatch.setattr(rm.subprocess, "run", run)
    return calls


def test_clean_run_passes(monkeypatch, rm):
    fake_mypy(monkeypatch, rm, 0, "Success: no issues found in 3 source files")
    assert rm.main(["--only", "libs"]) == 0


def test_type_errors_fail(monkeypatch, rm):
    fake_mypy(monkeypatch, rm, 1, "x.py:1: error: boom  [misc]\nFound 1 error in 1 file")
    assert rm.main(["--only", "libs"]) == 1


def test_config_error_is_not_a_result(monkeypatch, rm, capsys):
    # mypy exits 1 on a config error too - there is no summary line then.
    fake_mypy(monkeypatch, rm, 1, "pyproject.toml: [module = 'x']: Patterns must be ...")
    assert rm.main(["--only", "libs"]) == 2
    assert "FAILED TO RUN" in capsys.readouterr().out


def test_startup_crash_is_not_a_result(monkeypatch, rm):
    fake_mypy(monkeypatch, rm, 2, "corporate-sso is not a valid Python package name")
    assert rm.main(["--only", "addons"]) == 2


def test_each_service_runs_from_its_own_root(monkeypatch, rm):
    calls = fake_mypy(monkeypatch, rm, 0, "Success: no issues found in 1 source file")
    assert rm.main(["--only", "services"]) == 0
    services = [p for p in (rm.ROOT / "services").iterdir() if p.is_dir() and rm.service_sources(p)]
    assert len(calls) == len(services)
    assert all("libs" not in c and "addons" not in c for c in calls)


def test_nothing_selected_is_not_a_pass(monkeypatch, rm):
    fake_mypy(monkeypatch, rm, 0, "Success: no issues found")
    assert rm.main(["--only", "no-such-tree"]) == 2
