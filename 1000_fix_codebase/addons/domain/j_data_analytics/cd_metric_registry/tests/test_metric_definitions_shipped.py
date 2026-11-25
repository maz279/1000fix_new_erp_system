"""The five governed metric definitions ship as module data (A11 audit A3-F01/F04).

The metric registry is M62's headline promise - "one certified number" - and before
this audit it shipped NOTHING: the five definitions existed only as hand-made rows on
the live and reference estates, with no external ids, so a fresh database had an empty
registry and no migration could tell a hand row from a seed.

These tests pin the three properties that matter:
  * the definitions are product data (they carry cd_metric_registry external ids);
  * they are NOT born published - publication is a governance act, not a data file;
  * loading the file again changes nothing (one row per code, ever).

They deliberately do NOT assert a consumer: whether the BI metric bank (M25) is bound
to these definitions, and which formula wins where M25's own figure differs, is owner
decision D6 in audit_analysis/A11_ERP_AUDIT_DECISIONS_2026-11-23.md.
"""

import pytest

CODES = {
    "MET-WIP-AGE": "metric_def_met_wip_age",
    "MET-SLA-ATTAIN": "metric_def_met_sla_attain",
    "MET-AR-OVERDUE": "metric_def_met_ar_overdue",
    "MET-BENCH-UTIL": "metric_def_met_bench_util",
    "MET-NPS": "metric_def_met_nps",
}


def test_the_five_definitions_ship_as_module_data(odoo_env):
    """Each code exists once, carries its xmlid, and is a DRAFT with no version."""
    Definition = odoo_env["fix.metric.definition"]
    for code, xmlid in CODES.items():
        rows = Definition.search([("code", "=", code)])
        assert len(rows) == 1, "%s must exist exactly once, found %s" % (code, len(rows))
        data = odoo_env["ir.model.data"].search(
            [
                ("module", "=", "cd_metric_registry"),
                ("name", "=", xmlid),
                ("model", "=", "fix.metric.definition"),
            ]
        )
        assert data, "%s has no cd_metric_registry external id (was it adopted?)" % code
        assert data.res_id == rows.id, "%s points at %s, row is %s" % (xmlid, data.res_id, rows.id)
        assert rows.state == "draft", (
            "%s ships published - publication must go through the governed route" % code
        )
        assert not rows.current_version_id, "%s ships with a published version" % code


def test_each_definition_states_a_ratio_or_an_aggregate(odoo_env):
    """The module's own rule: a definition must say what it divides or averages."""
    for code in CODES:
        row = odoo_env["fix.metric.definition"].search([("code", "=", code)], limit=1)
        text = (row.definition or "").lower()
        assert text, "%s has no definition text" % code
        assert any(token in text for token in ("/", "mean", "sum", "promoters")), (
            "%s states neither a ratio nor an aggregate: %r" % (code, row.definition)
        )


def test_loading_the_definitions_twice_creates_no_duplicate(odoo_env):
    """Idempotent: the xmlid is the identity, so a second load updates in place."""
    Definition = odoo_env["fix.metric.definition"]
    before = Definition.search_count([("code", "in", list(CODES))])
    assert before == len(CODES)
    odoo_env["ir.model.data"]._update_xmlids(
        [
            {
                "xml_id": "cd_metric_registry.%s" % xmlid,
                "record": Definition.search([("code", "=", code)], limit=1),
                "noupdate": True,
            }
            for code, xmlid in CODES.items()
        ],
        update=True,
    )
    after = Definition.search_count([("code", "in", list(CODES))])
    assert after == before, "a second load duplicated definitions (%s -> %s)" % (before, after)


@pytest.mark.parametrize("code", sorted(CODES))
def test_each_definition_declares_an_owner_role_and_a_grain(odoo_env, code):
    """A certified number needs an accountable role and a stated grain."""
    row = odoo_env["fix.metric.definition"].search([("code", "=", code)], limit=1)
    assert row.owner_role, "%s has no accountable owner role" % code
    assert row.grain, "%s declares no grain" % code
    assert row.domain_area, "%s declares no domain area" % code
