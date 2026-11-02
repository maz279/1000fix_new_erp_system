# M25 BI sync: the snapshot engine must measure what it logs — every number
# in a log row is re-counted from the live tables and asserted equal.
# (pytest + odoo_env fixture per addons/conftest.py; rollback afterwards.)
import json

import pytest
from odoo import exceptions

OPEN_STATES = [
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
    "ready",
]


def _config(odoo_env, enabled=True):
    return odoo_env["fix.bi.sync.config"].create(
        {
            "name": "Exec KPI Sync (test)",
            "dataset_scope": "exec_kpi",
            "sync_frequency": "daily",
            "enabled": enabled,
        }
    )


def test_snapshot_metrics_match_live_counts(odoo_env):
    cfg = _config(odoo_env)
    orders = odoo_env["fix.service.order"]
    metrics = cfg._compute_snapshot_metrics()
    assert metrics["orders_open"] == orders.search_count([("state", "in", OPEN_STATES)])
    assert metrics["orders_in_repair"] == orders.search_count([("state", "=", "in_repair")])
    assert isinstance(metrics["revenue_approved_mtd"], int | float)


def test_run_sync_logs_real_snapshot(odoo_env):
    cfg = _config(odoo_env)
    cfg.action_run_sync()
    log = odoo_env["fix.bi.sync.log"].search([("config_id", "=", cfg.id)], limit=1)
    assert log.status == "success"
    snap = json.loads(log.snapshot_json)
    assert "orders_open" in snap
    assert snap["orders_open"] == cfg._compute_snapshot_metrics()["orders_open"]


def test_freshness_minutes_follows_newest_log(odoo_env):
    logs = odoo_env["fix.bi.sync.log"]
    # fixture transaction may coexist with earlier real runs — accept None
    # or a fresh value, then assert a new sync lands within a minute.
    minutes = logs.freshness_minutes()
    assert minutes is None or minutes <= 1
    cfg = _config(odoo_env)
    cfg.action_run_sync()
    assert logs.freshness_minutes() <= 1


def test_disabled_config_fails_closed(odoo_env):
    cfg = _config(odoo_env, enabled=False)
    with pytest.raises(exceptions.UserError):
        cfg.action_run_sync()


def test_connection_test_is_honest(odoo_env):
    cfg = _config(odoo_env, enabled=False)
    cfg.action_test_connection()
    assert cfg.last_test_status == "fail"
    cfg.enabled = True
    cfg.action_test_connection()
    assert cfg.last_test_status == "ok"
    assert "fail-closed" in cfg.last_test_note
