# M26 AI/ML services: the registry is honest, and every engine computes from
# the live records it names. (pytest + odoo_env fixture per addons/conftest.py.)
import json

import pytest
from odoo import exceptions


def _model(odoo_env, kind="fault_classifier"):
    return odoo_env["fix.ml.model"].search([("kind", "=", kind)], limit=1)


def test_catalog_seeded_honestly(odoo_env):
    models = odoo_env["fix.ml.model"].search([])
    kinds = models.mapped("kind")
    # seven engines in the catalog, demand forecast the only honest 'planned'.
    # lead_scoring was added by the A03 gap-closure build.
    assert len(models) == 7
    assert set(kinds) == {
        "dispatch_scoring",
        "fault_classifier",
        "predictive_maintenance",
        "tradein_valuation",
        "bi_aggregator",
        "demand_forecast",
        "lead_scoring",
    }
    planned = models.filtered(lambda m: m.status == "planned")
    assert planned.mapped("kind") == ["demand_forecast"]
    # every production entry names its owning module
    for rec in models.filtered(lambda m: m.status == "production"):
        assert rec.owning_module
    # 'Seeded honestly' is the point of this test, so the newest entry is held
    # to it explicitly: a deterministic weighted factor model must be
    # registered as rule_based, never as a live/trained engine. M07 reports
    # its score as basis='m26_model', and that is only truthful while this
    # entry says what it actually is.
    lead = models.filtered(lambda m: m.kind == "lead_scoring")
    assert len(lead) == 1
    assert lead.implementation == "rule_based"
    assert lead.status == "production"


def test_fault_classifier_matches_taxonomy(odoo_env):
    model = _model(odoo_env)
    run = odoo_env["fix.ml.inference.run"].create(
        {"model_id": model.id, "input_text": "phone will not power on, dead battery charging"}
    )
    run.action_execute()
    assert run.state == "computed"
    assert run.latency_ms >= 0
    out = json.loads(run.output_json)
    assert isinstance(out, list) and out, "expected matches against the fault taxonomy"
    assert all("fault_code" in item and "matched_terms" in item for item in out)


def test_fault_classifier_requires_text(odoo_env):
    model = _model(odoo_env)
    run = odoo_env["fix.ml.inference.run"].create({"model_id": model.id})
    with pytest.raises(exceptions.UserError):
        run._engine_fault_classifier()


def test_dispatch_scoring_runs_real_engine(odoo_env):
    model = _model(odoo_env, "dispatch_scoring")
    order = odoo_env["fix.field.order"].search([], limit=1)
    if not order:
        pytest.skip("no field order in this database")
    run = odoo_env["fix.ml.inference.run"].create(
        {"model_id": model.id, "field_order_id": order.id}
    )
    run.action_execute()
    assert run.state == "computed"
    out = json.loads(run.output_json)
    assert isinstance(out, list)
    assert all("score" in item and "reasons" in item for item in out)


def test_demand_forecast_fails_closed(odoo_env):
    model = _model(odoo_env, "demand_forecast")
    run = odoo_env["fix.ml.inference.run"].create({"model_id": model.id})
    run.action_execute()
    assert run.state == "failed"
    assert "consumption-history" in run.error_note or "not built" in run.error_note


def test_run_stats_follow_runs(odoo_env):
    model = _model(odoo_env)
    before = model.run_count
    odoo_env["fix.ml.inference.run"].create(
        {"model_id": model.id, "input_text": "screen cracked display broken"}
    ).action_execute()
    assert model.run_count == before + 1
