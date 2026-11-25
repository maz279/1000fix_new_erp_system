"""Brand template registry lookups and default config resolution (R05-M01-T03)."""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.workflow import BrandSubmissionWorkflow as PackageExportedWorkflow
from services.workflow.brand_submission_engine import (
    BrandSubmissionWorkflow,
    BrandTemplateRegistry,
    CompletenessViolationError,
)

_BUNDLED = Path(__file__).resolve().parents[1] / "brand_templates.json"


def _write_config(tmp_path, templates):
    path = tmp_path / "brand_templates.json"
    path.write_text(json.dumps({"templates": templates}), encoding="utf-8")
    return path


def test_default_config_is_the_bundled_template_file():
    registry = BrandTemplateRegistry()
    assert registry.config_path == _BUNDLED
    assert len(registry.list_all_templates()) == 18


def test_lookup_by_code_name_and_case_insensitive_name(tmp_path):
    tmpl = {"brand_code": "BRD-900", "brand_name": "Walton", "channel": "api", "endpoint": "x"}
    registry = BrandTemplateRegistry(_write_config(tmp_path, [tmpl]))
    assert registry.get_template("BRD-900") == tmpl
    assert registry.get_template("walton") == tmpl
    assert registry.get_template("WALTON") == tmpl
    assert registry.get_template("Unknown Brand") is None


def test_config_without_templates_key_is_empty(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("{}", encoding="utf-8")
    registry = BrandTemplateRegistry(path)
    assert registry.list_all_templates() == []
    assert registry.get_template("BRD-001") is None


def test_list_is_unique_and_sorted_by_code(tmp_path):
    templates = [
        {"brand_code": "BRD-2", "brand_name": "Beta"},
        {"brand_code": "BRD-1", "brand_name": "Alpha"},
    ]
    registry = BrandTemplateRegistry(_write_config(tmp_path, templates))
    assert [t["brand_code"] for t in registry.list_all_templates()] == ["BRD-1", "BRD-2"]


def test_violation_error_carries_context():
    err = CompletenessViolationError("CLM-1", "Dell", ["invoice", "photo"])
    assert (err.claim_no, err.brand_name, err.missing_items) == (
        "CLM-1",
        "Dell",
        ["invoice", "photo"],
    )
    assert "missing mandatory evidence: invoice, photo" in str(err)


def test_minimal_template_defaults_and_unknown_claim_number():
    wf = BrandSubmissionWorkflow(
        {"brand_code": "BRD-X", "brand_name": "X", "channel": "email", "endpoint": "x@brand.test"}
    )
    assert wf.mandatory_evidence == set()
    assert wf.transform_payload({"claim_no": "C1"})["data"] == {}
    assert wf.execute_submission({})["acknowledgement_ref"] == "ACK/BRD-X/None"

    strict = BrandSubmissionWorkflow(
        {
            "brand_code": "BRD-Y",
            "brand_name": "Y",
            "channel": "api",
            "endpoint": "https://brand.test",
            "mandatory_evidence": ["invoice"],
        }
    )
    with pytest.raises(CompletenessViolationError) as excinfo:
        strict.check_completeness({})
    assert excinfo.value.claim_no == "UNKNOWN"


def test_package_reexports_engine_classes():
    assert PackageExportedWorkflow is BrandSubmissionWorkflow
