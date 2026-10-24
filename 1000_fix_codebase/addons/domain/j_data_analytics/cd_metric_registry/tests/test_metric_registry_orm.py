# cd_metric_registry live-ORM tests — P11-M02 (CD-M62-01): catalogue
# warehouse-safety (NFR-086c), lineage, DA-008 data-quality thresholds.
import json

import pytest
from odoo.exceptions import UserError


def _events(env, event_type, aggregate_id):
    rows = env["fix.event.outbox"].search(
        [("event_type", "=", event_type), ("aggregate_id", "=", aggregate_id)], order="id"
    )
    return [json.loads(r.payload) for r in rows]


def _entity(env, name, **vals):
    return env["fix.data.entity"].create({"name": name, **vals})


def test_residency_classified_tables_never_enter_the_warehouse(odoo_env):
    with pytest.raises(UserError, match="NFR-086c"), odoo_env.cr.savepoint():
        _entity(odoo_env, "Warehouse.dim_customer_nid", classification="residency_classified")
    # allowed: S3 outside the warehouse, a warehouse table that is not S3,
    # and a non-table S3 artefact
    assert _entity(odoo_env, "fix_identity_document", classification="residency_classified")
    assert _entity(odoo_env, "warehouse.fact_orders", classification="confidential")
    assert _entity(
        odoo_env, "warehouse nid feed", classification="residency_classified", entity_type="event"
    )
    # reclassifying an existing warehouse table is caught as well
    table = _entity(odoo_env, "warehouse.dim_party")
    with (
        pytest.raises(UserError, match="must not appear in the analytical warehouse"),
        odoo_env.cr.savepoint(),
    ):
        table.write({"classification": "residency_classified"})


def test_lineage_links_source_to_target(odoo_env):
    source = _entity(odoo_env, "fix_service_order")
    target = _entity(odoo_env, "warehouse.fact_service_orders")
    hop = odoo_env["fix.data.lineage"].create(
        {
            "name": "orders -> fact",
            "source_entity_id": source.id,
            "target_entity_id": target.id,
            "transformation": "dbt: stg_orders -> fact_service_orders",
            "lineage_order": 1,
        }
    )
    assert (hop.source_entity_id, hop.target_entity_id) == (source, target)
    source.unlink()  # cascade: lineage cannot dangle
    assert not hop.exists()


def test_quality_rule_threshold(odoo_env):
    entity = _entity(odoo_env, "warehouse.fact_invoices")
    rule = odoo_env["fix.data.quality.rule"].create(
        {"name": "invoice completeness", "entity_id": entity.id, "threshold": 95.0}
    )
    rule.action_check(97.5)
    assert (rule.state, rule.last_result) == ("passing", 97.5)
    assert rule.last_checked
    rule.action_check(95.0)  # at the threshold is not below it
    assert rule.state == "passing"
    assert _events(odoo_env, "data_quality.failing", rule.id) == []
    rule.action_check(91.2)
    assert (rule.state, rule.last_result) == ("failing", 91.2)
    assert _events(odoo_env, "data_quality.failing", rule.id) == [
        {"entity": "warehouse.fact_invoices", "result": 91.2, "threshold": 95.0}
    ]
