"""test_catalogue_engine_paths.py - classification cadence, residency-scan findings, CLI.

Evidence JSON lands in the per-test directory from ``conftest.isolated_warehouse``;
residency-scan scenarios run against a synthetic repository tree under ``tmp_path``.
"""

from __future__ import annotations

import json
from pathlib import Path

import catalogue_engine
import pytest
from catalogue_engine import DataGovernanceEngine


@pytest.fixture
def engine():
    return DataGovernanceEngine()


def _by_classification(engine: DataGovernanceEngine, cls: str) -> list[dict]:
    return [e for e in engine.entities if e["classification"] == cls]


def test_regression_no_entities_are_synthesised_to_pad_the_catalogue(engine, isolated_warehouse):
    """Regression: the catalogue padded itself with generated filler rows
    (fix_cd_partner_481 & co.) until it reached exactly 1,335 entities and then
    certified 100% DA-002 coverage. The audit now reports the 31 real entities
    (2.32% coverage) and FAILs while the estate is not fully catalogued.
    """
    report = engine.build_full_catalogue()

    assert report["total_entities_catalogued"] == 31
    assert report["target_entity_count"] == 1335
    assert report["completeness_pct"] == 2.32
    assert report["status"] == "FAIL"
    # Only real, individually-declared entities - no generated names.
    assert not [
        e
        for e in engine.entities
        if e["name"].startswith(("fix_cd_", "api_", "event_", "report_", "doc_"))
    ]
    residency = {e["name"] for e in _by_classification(engine, "residency_classified")}
    assert residency == {"fix_identity_document", "fix_biometric_log"}
    assert report["classification_breakdown"] == {
        "internal": 19,
        "confidential": 7,
        "residency_classified": 2,
        "public": 3,
    }
    evidence = isolated_warehouse.evidence_dir / "r09-m02-data-catalogue-audit.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == report


def test_catalogue_never_accepts_target_as_input(engine):
    """The DA-002 target is a constant, not an argument: no caller can ask the
    engine to 'reach' a count anymore."""
    import inspect

    assert "target_count" not in inspect.signature(engine.build_full_catalogue).parameters


def _fake_repo(root: Path, models: dict[str, str] | None, sync_source: str | None) -> Path:
    bi = root / "services" / "bi-warehouse"
    if models is not None:
        core = bi / "dbt" / "models" / "core"
        core.mkdir(parents=True)
        for name, sql in models.items():
            (core / name).write_text(sql, encoding="utf-8")
    if sync_source is not None:
        (bi / "src").mkdir(parents=True)
        (bi / "src" / "warehouse_sync.py").write_text(sync_source, encoding="utf-8")
    return root


def test_residency_scan_flags_classified_columns_and_missing_pseudonymisation(
    monkeypatch, engine, tmp_path, isolated_warehouse
):
    repo = _fake_repo(
        tmp_path / "repo",
        {
            "dim_customer.sql": "select NID, passport_no, md5(email) as h from x",
            "fact_nps.sql": "select score from x",
            "notes.txt": "passport",  # not a model: never scanned
        },
        sync_source="customers = [{'email': raw_email}]",
    )
    monkeypatch.setattr(catalogue_engine, "REPO_ROOT", repo)

    report = engine.audit_warehouse_residency_scan()

    assert report["status"] == "FAIL"
    assert sorted(report["scanned_files"]) == [
        "dim_customer.sql",
        "fact_nps.sql",
        "warehouse_sync.py",
    ]
    assert sorted((v["file"], v.get("forbidden_token")) for v in report["violations"]) == [
        ("dim_customer.sql", "nid"),
        ("dim_customer.sql", "passport_no"),
        ("warehouse_sync.py", None),
    ]
    assert report["violations_count"] == 3
    sync_violation = next(v for v in report["violations"] if v["file"] == "warehouse_sync.py")
    assert sync_violation["violation"] == "dim_customer does not enforce pseudonym_hash"
    assert report["audit_finding"] == (
        "3 residency-classified (S3) hit(s). Warehouse violates NFR-086c."
    )
    evidence = isolated_warehouse.evidence_dir / "r09-m02-nfr086c-residency-scan.json"
    assert json.loads(evidence.read_text(encoding="utf-8")) == report


def test_residency_scan_passes_clean_models_with_pseudonymised_sync(monkeypatch, engine, tmp_path):
    repo = _fake_repo(
        tmp_path / "repo",
        {"dim_customer.sql": "select md5(email) as pseudonym_hash from x"},
        sync_source="row = {'pseudonym_hash': h}",
    )
    monkeypatch.setattr(catalogue_engine, "REPO_ROOT", repo)

    report = engine.audit_warehouse_residency_scan()

    assert report["status"] == "PASS"
    assert report["scanned_files"] == ["dim_customer.sql", "warehouse_sync.py"]
    assert report["violations"] == []
    assert report["unscanned_targets"] == []
    assert report["audit_finding"].startswith("0 residency-classified (S3) hits.")


@pytest.mark.parametrize(
    ("models", "sync_source", "unscanned"),
    [
        (None, None, ["dbt core models (*.sql)", "warehouse_sync.py"]),
        ({"README.md": "no models here"}, "pseudonym_hash", ["dbt core models (*.sql)"]),
        ({"dim_customer.sql": "select pseudonym_hash from x"}, None, ["warehouse_sync.py"]),
    ],
)
def test_regression_residency_scan_with_missing_targets_does_not_pass(
    monkeypatch, engine, tmp_path, models, sync_source, unscanned
):
    """Regression: with no model / sync file found the scan checked nothing, yet
    reported PASS ("Warehouse satisfies NFR-086c completely")."""
    repo = _fake_repo(tmp_path / "repo", models, sync_source)
    monkeypatch.setattr(catalogue_engine, "REPO_ROOT", repo)

    report = engine.audit_warehouse_residency_scan()

    assert report["violations_count"] == 0
    assert report["unscanned_targets"] == unscanned
    assert report["status"] == "FAIL"
    assert report["audit_finding"] == (
        f"Scan incomplete, not found: {', '.join(unscanned)}. NFR-086c compliance not demonstrated."
    )


def test_governance_suite_fails_when_any_task_fails(monkeypatch, engine):
    monkeypatch.setattr(engine, "audit_warehouse_residency_scan", lambda: {"status": "FAIL"})

    res = engine.run_full_governance_suite()

    assert res["status"] == "FAIL"
    assert res["tasks"] == {
        "R09-M02-T01": "FAIL",  # real: 31/1335 entities catalogued
        "R09-M02-T02": "PASS",
        "R09-M02-T03": "PASS",
        "R09-M02-T04": "FAIL",
    }


def test_main_exit_code_follows_governance_suite(monkeypatch, isolated_warehouse):
    # The catalogue task honestly FAILs (31/1335), so the suite exits 1.
    assert catalogue_engine.main() == 1
    written = sorted(p.name for p in isolated_warehouse.evidence_dir.iterdir())
    assert written == [
        "r09-m02-data-catalogue-audit.json",
        "r09-m02-dq-monitoring-evidence.json",
        "r09-m02-lineage-audit.json",
        "r09-m02-nfr086c-residency-scan.json",
    ]

    monkeypatch.setattr(
        DataGovernanceEngine,
        "build_full_catalogue",
        lambda self: {"status": "PASS"},
    )
    assert catalogue_engine.main() == 0
