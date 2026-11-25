# Presentation defects the headless UI walk of 8069 found (fix_real, 11 Nov 2026).
#
# - M30 "Open DOFA Rulings" passed its column headers as a positional list;
#   the workspace reads a {col: header} map, so five headers showed raw keys.
# - M29 audit trail showed the technical "model,id" reference; a computed,
#   never-stored label resolves it without touching the hash chain.
# - M19 Chart of Accounts was empty on an estate whose statutory register has
#   no rows (the real legacy chart lives only in the posting chart).
from __future__ import annotations

import pytest
from odoo.addons.cd_p03_portal.controllers.a12 import m30
from odoo.addons.cd_p03_portal.controllers.p03_gl_api import P03GlApiController


def test_pack_maps_positional_labels_onto_columns():
    pack = m30._pack("T", ["a", "b"], ["Alpha", "Beta"], [], [])
    assert pack["labels"] == {"a": "Alpha", "b": "Beta"}


def test_pack_refuses_a_label_list_of_the_wrong_length():
    with pytest.raises(ValueError):
        m30._pack("T", ["a", "b"], ["Alpha"], [], [])


def test_open_dofa_rulings_labels_every_column(odoo_env):
    pack = m30.open_dofa_rulings(odoo_env)
    assert isinstance(pack["labels"], dict)
    assert set(pack["cols"]) <= set(pack["labels"])
    assert pack["labels"]["is_today"] == "What The Code Does Today"


def test_audit_object_label_resolves_a_record_reference(odoo_env):
    Audit = odoo_env["fix.security.audit"]
    user = odoo_env.user
    entry = Audit.log_event("ui.walk.label", "res.users,%d" % user.id)
    assert entry.object_ref == "res.users,%d" % user.id  # stored value unchanged
    assert entry.object_label.endswith(": %s" % user.display_name)
    assert Audit.search([("object_label", "ilike", "res.users,%d" % user.id)]) >= entry


def test_audit_object_label_keeps_a_bare_model_and_unknown_text(odoo_env):
    Audit = odoo_env["fix.security.audit"]
    bare = Audit.log_event("ui.walk.label", "res.users")
    odd = Audit.log_event("ui.walk.label", "not a model ref")
    gone = Audit.log_event("ui.walk.label", "res.users,999999999")
    assert bare.object_label == odoo_env["ir.model"]._get("res.users").name
    assert odd.object_label == "not a model ref"
    assert gone.object_label.endswith("#999999999")


def test_coa_falls_back_to_the_posting_chart(odoo_env):
    company = odoo_env.company
    data = P03GlApiController._coa_from_posting_chart(odoo_env, company)
    accounts = (
        odoo_env["account.account"]
        .with_context(active_test=False)
        .search_count([("company_ids", "in", company.id)])
    )
    assert data["source"] == "posting_chart"
    assert data["count"] == accounts > 0
    assert {r["type"] for r in data["rows"]} <= {
        "asset",
        "liability",
        "equity",
        "income",
        "expense",
        "off",
    }
    receivable = [r for r in data["rows"] if r["subtype"] == "asset_receivable"]
    assert receivable and all(
        r["control"] and r["control_subledger"] == "receivable" for r in receivable
    )
    assert all(r["manual_balance"] is None for r in data["rows"])


def test_identity_read_log_shows_and_filters_by_the_readers_clock(odoo_env):
    # M21 printed the stored UTC value ("2026-11-11 13:08:22") and filtered a
    # local calendar day with UTC bounds, losing 00:00-05:59 Dhaka time.
    from odoo.addons.cd_p03_portal.controllers.a09 import m21

    env = odoo_env(context=dict(odoo_env.context, tz="Asia/Dhaka"))
    env.user.tz = "Asia/Dhaka"
    log = (
        env["fix.hr.identity.access.log"]
        .sudo()
        .create(
            {
                "field_name": env["fix.hr.identity.access.log"]
                ._fields["field_name"]
                .selection[0][0],
                "employee_name": "UI walk clock check",
                "user_id": env.uid,
                "purpose": "ui-walk-clock",
                "read_at": "2026-03-01 19:30:00",  # 2 Mar 01:30 in Dhaka
            }
        )
    )
    pack = m21.identity_access_log(env, date_from="2026-03-02", date_to="2026-03-02")
    mine = [r for r in pack["rows"] if r["purpose"] == "ui-walk-clock"]
    assert log and mine, "a 01:30 Dhaka read belongs to 2 March"
    assert mine[0]["read_at"] == "2026-03-02 01:30"
    assert not [
        r
        for r in m21.identity_access_log(env, date_from="2026-03-01", date_to="2026-03-01")["rows"]
        if r["purpose"] == "ui-walk-clock"
    ]
