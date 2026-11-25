"""document-generation runtime path, CLI smoke and BN-007 grouping edges (TR-07)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import document_generation
from document_generation import RenderJob, format_amount, render


def test_runtime_path_renders_when_odoo_is_up(monkeypatch):
    monkeypatch.setenv("FIX_DOCUMENT_RENDER_RUNTIME", "odoo")
    result = render(RenderJob("service_receipt", locale="en", payload={"amount": 2500.5}))
    assert result.status == "rendered"
    assert result.qweb_ref == "cd_service_order.report_jobcard"
    assert result.reference_image.endswith("bengali-conjunct-reference.png")
    assert result.detail == ""
    assert result.checks["numerals"] == "ascii"
    assert result.checks["amounts"] == "BDT 2,500.50"


def test_other_runtime_values_stay_dry_run(monkeypatch):
    monkeypatch.setenv("FIX_DOCUMENT_RENDER_RUNTIME", "wkhtmltopdf")
    result = render(RenderJob("mushak_6_6"))
    assert result.status == "dry-run"
    assert result.checks["numerals"] == "bn"
    assert result.checks["amounts"] == "৳ ০.০০"  # default amount 0.0


def test_unknown_template_detail_names_template():
    result = render(RenderJob("mushak_9_9"))
    assert result.detail == "template 'mushak_9_9' not in the W3 set"
    assert result.checks == {}


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (1234.56, "BDT 1,234.56"),
        (12345.67, "BDT 12,345.67"),
        (123456.0, "BDT 1,23,456.00"),
        (1234567.0, "BDT 12,34,567.00"),
        (12345678.9, "BDT 1,23,45,678.90"),
        (-150000.0, "-BDT 1,50,000.00"),
        (0.0, "BDT 0.00"),
    ],
)
def test_lakh_crore_grouping(amount, expected):
    assert format_amount(amount, "en") == expected


def test_bn_negative_amount_puts_sign_before_taka():
    assert format_amount(-1500.0, "bn") == "-৳ ১,৫০০.০০"


def test_main_prints_dry_run_decision(monkeypatch, capsys):
    monkeypatch.delenv("FIX_DOCUMENT_RENDER_RUNTIME", raising=False)
    document_generation.main()
    out = json.loads(capsys.readouterr().out)
    assert out["template"] == "mushak_6_3"
    assert out["status"] == "dry-run"
    assert out["qweb_ref"] == "cd_tax_engine_bd.report_mushak63"
    assert out["checks"]["amounts"] == "৳ ১,৫০,০০০.০০"
    assert out["checks"]["identifiers_ascii"] is True
