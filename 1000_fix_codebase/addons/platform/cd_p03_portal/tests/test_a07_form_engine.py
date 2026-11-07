# The form engine a person actually uses. The A07 build proved its controls by calling
# methods directly; no screen was driven, and these defects stood between a user and
# those controls. Each test drives the same endpoint the workspace calls.
from __future__ import annotations

import base64
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api
from odoo.exceptions import UserError


@pytest.fixture
def ui(odoo_env):
    ctl = api.P03GenericApiController()
    cls = api.P03GenericApiController
    old = getattr(api, "request", None)

    def call(name, **kw):
        api.request = types.SimpleNamespace(env=odoo_env)
        fn = getattr(cls, name)
        return getattr(fn, "original_endpoint", fn)(ctl, **kw)

    try:
        yield types.SimpleNamespace(
            records=lambda **kw: call("model_records", **kw),
            form=lambda **kw: call("model_form", **kw),
            write=lambda **kw: call("model_write", **kw),
            lookup=lambda **kw: call("model_lookup", **kw),
        )
    finally:
        api.request = old


# ------------------------------------------------------------ pickers
def test_a_long_comodel_is_searched_not_cut_at_300(odoo_env, ui):
    partners = odoo_env["res.partner"].create(
        [{"name": "A07 Far Away Partner %04d" % i} for i in range(310)]
    )
    out = ui.form(model="fix.device", fields=[{"name": "owner_id"}])
    owner = next(f for f in out["fields"] if f["name"] == "owner_id")
    assert owner["remote"] is True and owner["choices"] == []
    # the last one created, which a first-300 select could not offer
    found = ui.lookup(model="fix.device", field="owner_id", term="Far Away Partner 0309")
    assert found["rows"] == [{"id": partners[-1].id, "label": partners[-1].display_name}]


def test_a_short_comodel_stays_a_plain_select(odoo_env, ui):
    odoo_env["fix.site"].create({"name": "A07 Short"})
    out = ui.form(model="fix.facility.work.order", fields=[{"name": "site_id"}])
    entry = next(f for f in out["fields"] if f["name"] == "site_id")
    assert entry["remote"] is False and entry["choices"]


def test_a_picker_will_not_search_a_field_the_screen_does_not_offer(ui):
    out = ui.lookup(model="fix.device", field="create_uid", term="a")
    assert "cannot be searched" in out["error"]


def test_a_picker_is_fenced_to_the_callers_companies(odoo_env):
    domain = api._picker_domain(odoo_env, {}, "res.partner", "x")
    assert ("company_id", "in", odoo_env.companies.ids) in domain


def test_a_declared_picker_domain_narrows_the_choices(odoo_env):
    conf = {"pickers": {"insurer_id": [("is_company", "=", True)]}}
    assert ("is_company", "=", True) in api._picker_domain(
        odoo_env, conf, "res.partner", "insurer_id"
    )
    assert api._picker_domain(odoo_env, conf, "res.partner", "other_id")[0] == "|"


# ------------------------------------------------------------ list reach
def test_quick_find_reaches_rows_beyond_the_loaded_page(odoo_env, ui, monkeypatch):
    sites = odoo_env["fix.site"].create([{"name": "A07 Needle %d" % i} for i in range(2)])
    monkeypatch.setitem(api.SURFACES["fix.site"], "limit", 1)
    assert ui.records(model="fix.site", cols=["name"])["count"] == 1
    monkeypatch.setitem(api.SURFACES["fix.site"], "limit", 5)
    out = ui.records(model="fix.site", cols=["name"], search="a07 NEEDLE")
    assert {r["id"] for r in out["rows"]} == set(sites.ids)


def test_a_list_pages_past_its_limit(odoo_env, ui, monkeypatch):
    sites = odoo_env["fix.site"].create([{"name": "A07 Page %d" % i} for i in range(3)])
    monkeypatch.setitem(api.SURFACES["fix.site"], "limit", 2)
    first = ui.records(model="fix.site", cols=["name"], search="A07 Page")
    second = ui.records(model="fix.site", cols=["name"], search="A07 Page", offset=2)
    assert first["count"] == 2 and first["total"] == 3
    assert second["count"] == 1 and second["offset"] == 2
    assert {r["id"] for r in first["rows"] + second["rows"]} == set(sites.ids)


# ------------------------------------------------------------ what a form saves
def test_a_new_form_shows_a_tick_box_default(ui):
    out = ui.form(model="fix.equipment.verification", fields=[{"name": "found"}])
    assert out["defaults"].get("found") is True


def test_a_field_can_be_emptied(odoo_env, ui):
    site = odoo_env["fix.site"].create({"name": "A07 Clear", "address": "to be cleared"})
    assert "address" in api.SURFACES["fix.site"]["writable"]
    out = ui.write(model="fix.site", record_id=site.id, values={"address": False})
    assert "error" not in out
    site.invalidate_recordset()
    assert not site.address


# ------------------------------------------------------------ the wall clock
def test_datetimes_read_and_save_in_dhaka_time(odoo_env):
    env = odoo_env(su=True)
    env.user.tz = "Asia/Dhaka"
    assert api._datetime_to_local(env, "2026-11-07 04:00:00") == "2026-11-07 10:00:00"
    assert api._datetime_to_utc(env, "2026-11-07T10:00") == "2026-11-07 04:00:00"
    assert api._datetime_to_utc(env, "2026-11-07 10:00:00") == "2026-11-07 04:00:00"


def test_a_user_with_no_zone_reads_dhaka_not_utc(odoo_env):
    env = odoo_env(su=True)
    env.user.tz = False
    assert api._datetime_to_local(env, "2026-11-07 04:00:00") == "2026-11-07 10:00:00"


def test_a_form_echo_of_a_read_only_datetime_is_not_a_change(odoo_env):
    env = odoo_env(su=True)
    env.user.tz = "Asia/Dhaka"
    now = fields.Datetime.now()
    vals = {"create_date": api._datetime_to_local(env, now)}
    api.P03GenericApiController._datetimes_to_utc(env, "fix.site", vals)
    assert vals["create_date"][:16] == str(now)[:16]


# ------------------------------------------------------------ child grids
def test_an_unchanged_child_row_is_not_rewritten(odoo_env):
    child = odoo_env["res.partner"].create({"name": "A07 Child"})
    field = odoo_env["res.partner"]._fields["name"]
    assert api._child_value_changed(child, field, "A07 Child") is False
    assert api._child_value_changed(child, field, "A07 Child 2") is True


# ------------------------------------------------------------ evidence
def test_the_upload_form_really_uploads(odoo_env, ui):
    out = ui.write(
        model="fix.document",
        values={
            "name": "A07 Proof",
            "document_type": "evidence_pack",
            "upload_file": base64.b64encode(b"%PDF-1.4 proof").decode(),
            "upload_filename": "proof.pdf",
        },
    )
    assert "error" not in out, out
    doc = odoo_env["fix.document"].browse(out["id"])
    assert doc.attachment_id.name == "proof.pdf"
    assert base64.b64decode(doc.attachment_id.datas) == b"%PDF-1.4 proof"


def test_the_workspace_refuses_a_document_with_no_file(ui):
    out = ui.write(
        model="fix.document", values={"name": "A07 No", "document_type": "evidence_pack"}
    )
    assert "error" in out


# ------------------------------------------------------------ approval requests
def test_a_tier_2_request_with_no_justification_is_refused_when_asked(odoo_env):
    """It used to create the request; the approver's vote could then only refuse."""
    env = odoo_env
    site = env["fix.site"].create({"name": "A07 Tier"})
    order = env["fix.facility.work.order"].create(
        {
            "site_id": site.id,
            "work_type": "repair",
            "description": "A07",
            "estimated_cost": 500000.0,
        }
    )
    with pytest.raises(UserError, match="justification"), env.cr.savepoint():
        order.action_request_approval()
    assert order.approval_state != "pending"
