"""Tests for the R05-M03-T03 CPU vs GPU latency sizing report generator.

The script makes no network calls (the figures are calibrated constants), so
nothing needs mocking except where the evidence file is written: main() is
re-rooted under tmp_path so services/conversational-ai/evidence/ is never
touched.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPT = Path(__file__).resolve().parents[1] / "benchmark_ollama_latency.py"
_MODULE_NAME = "conversational_ai_benchmark_ollama_latency"


def _load():
    if _MODULE_NAME in sys.modules:
        return sys.modules[_MODULE_NAME]
    spec = importlib.util.spec_from_file_location(_MODULE_NAME, _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[_MODULE_NAME] = module  # dataclasses resolve annotations via sys.modules
    spec.loader.exec_module(module)
    return module


bench = _load()


@pytest.fixture
def report():
    return bench.run_benchmark_simulation()


def test_report_header(report):
    assert report["milestone"] == "R05-M03-T03"
    assert report["benchmark_date"] == "2026-10-17"
    assert "NVIDIA T4" in report["executive_summary"]
    assert len(report["results"]) == 3


def test_every_result_is_a_serialisable_benchmark_row(report):
    fields = set(bench.LatencyBenchmarkResult.__dataclass_fields__)
    hw_fields = set(bench.HardwareProfile.__dataclass_fields__)
    for row in report["results"]:
        assert set(row) == fields
        assert set(row["hardware"]) == hw_fields
        assert row["quantization"] == "Q4_K_M"
        assert row["test_utterances"] == 100
        assert "sha256:926d40fd" in row["model_name"]
    json.dumps(report)  # asdict() output is plain JSON


def test_sla_flags_match_the_latency_thresholds(report):
    for row in report["results"]:
        assert row["voice_ivr_sla_compliant"] == (row["p95_turn_latency_ms"] <= 400.0)
        assert row["text_chat_sla_compliant"] == (row["p95_turn_latency_ms"] <= 2000.0)


def test_cpu_profile_is_text_only_and_gpu_profiles_cover_voice(report):
    by_type = {}
    for row in report["results"]:
        by_type.setdefault(row["hardware"]["hardware_type"], []).append(row)
    (cpu,) = by_type["CPU"]
    assert cpu["voice_ivr_sla_compliant"] is False
    assert cpu["text_chat_sla_compliant"] is True
    assert all(r["voice_ivr_sla_compliant"] for r in by_type["GPU"])
    # the cheapest voice-capable profile is the recommended T4
    cheapest_voice = min(by_type["GPU"], key=lambda r: r["hardware"]["cost_per_hour_usd"])
    assert "T4" in cheapest_voice["hardware"]["name"]
    assert cheapest_voice["verdict"].startswith("OPTIMAL")


def test_main_writes_evidence_under_module_dir_and_prints_summary(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(bench, "__file__", str(tmp_path / "benchmark_ollama_latency.py"))

    assert bench.main() == 0

    out_file = tmp_path / "evidence" / "gpu-vs-cpu-latency-report.json"
    written = json.loads(out_file.read_text(encoding="utf-8"))
    assert written == bench.run_benchmark_simulation()

    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "=== OLLAMA GPU VS CPU LATENCY BENCHMARK COMPLETED ==="
    assert lines[1] == f"Evidence written to: {out_file}"
    assert lines[2:] == [
        "-> Cloud VM Standard (CPU Only): 1360.0 ms/turn | 18.5 tps | "
        "SUFFICIENT FOR TEXT CHAT; VOICE IVR REQUIRES GPU",
        "-> Cloud GPU Optimized (NVIDIA T4): 305.0 ms/turn | 76.0 tps | "
        "OPTIMAL FOR HOTLINE 16743 VOICE + CONCURRENT CHAT",
        "-> High-Performance GPU (NVIDIA A10G): 202.0 ms/turn | 115.0 tps | "
        "OVER-PROVISIONED FOR TRANSACTIONAL INTENTS",
    ]


def test_main_reuses_existing_evidence_dir(monkeypatch, tmp_path, capsys):
    (tmp_path / "evidence").mkdir()
    stale = tmp_path / "evidence" / "gpu-vs-cpu-latency-report.json"
    stale.write_text("stale", encoding="utf-8")
    monkeypatch.setattr(bench, "__file__", str(tmp_path / "benchmark_ollama_latency.py"))

    assert bench.main() == 0
    capsys.readouterr()
    assert json.loads(stale.read_text(encoding="utf-8"))["milestone"] == "R05-M03-T03"
