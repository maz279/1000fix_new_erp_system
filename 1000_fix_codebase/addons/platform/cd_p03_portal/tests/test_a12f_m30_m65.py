"""A12 finish build, M30 + M65: every engineering item E1-E25 in
working/A12_evidence/finish/m30_m65/FINDINGS.md, proven through the real methods
and the same controllers the screens call, as real role-holding non-admin users.

Everything runs in the rolled-back odoo_env except the E2 test, which needs real
commits: a single transaction hides that bug (the ORM batches both ladders).
"""

import importlib.util
import re
import types
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from odoo import SUPERUSER_ID, api, fields
from odoo.addons.cd_storefront.tests.test_a04_c2_c13_storefront import released_card
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
T4 = "cd_entity_config.group_dofa_tier_4"
T5 = "cd_entity_config.group_dofa_tier_5"
PA = "cd_entity_config.group_platform_admin"
APPROVER = "cd_entity_config.group_gateway_activation_approver"
FINANCE = "account.group_account_manager"

SRC = Path(__file__).resolve().parents[1] / "static" / "src"
M30_JS = (SRC / "a12" / "m30.js").read_text(encoding="utf-8")
M65_JS = (SRC / "a12" / "m65.js").read_text(encoding="utf-8")
WORKSPACE_JS = (SRC / "p03_workspace.js").read_text(encoding="utf-8")
BOARD = "BOARD-MIN-1"


class Ctx:
    pass


def _user(env, login, groups=()):
    gids = [env.ref("base.group_user").id] + [env.ref(x).id for x in groups]
    ou = env["operating.unit"].search([], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [(6, 0, gids)],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


def attempt(env, fn):
    try:
        with env.cr.savepoint():
            return ("ok", fn())
    except REFUSED as exc:
        return ("refused", str(exc)[:300])


def refused(env, fn):
    return attempt(env, fn)[0] == "refused"


def perr(res):
    if res.get("error"):
        return res["error"]
    return res.get("error") or ("failed" if res.get("success") is False else None)


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = Ctx()
    x.env = env
    x.ou = env["operating.unit"].search([], limit=1)
    x.clerk = _user(env, "a12f_clerk")
    x.pa = _user(env, "a12f_pa", [PA])
    x.pa2 = _user(env, "a12f_pa2", [PA])
    x.approver = _user(env, "a12f_gwapp", [APPROVER])
    x.t4 = _user(env, "a12f_t4", [T4])
    x.t4b = _user(env, "a12f_t4b", [T4])
    x.t5 = _user(env, "a12f_t5", [T5])
    x.t5b = _user(env, "a12f_t5b", [T5])
    x.entity = env["fix.entity"].search([("company_id", "=", env.company.id)], limit=1) or env[
        "fix.entity"
    ].create({"code": "A12F", "legal_name": "A12F Entity", "company_id": env.company.id})
    x.branch = env["fix.branch"].create(
        {
            "code": "A12FB1",
            "name": "A12F Branch",
            "entity_id": x.entity.id,
            "operating_unit_id": x.ou.id,
        }
    )
    return x


@pytest.fixture
def p03(c):
    import odoo.addons.cd_p03_portal.controllers.p03_generic_api as g
    import odoo.addons.cd_p03_portal.controllers.p03_service_order_api as s

    ctl = g.P03GenericApiController()

    def ep(name):
        fn = getattr(g.P03GenericApiController, name)
        return getattr(fn, "original_endpoint", fn)

    old_g, old_s = getattr(g, "request", None), getattr(s, "request", None)

    def as_user(user):
        req = types.SimpleNamespace(env=c.env(user=user.id))
        g.request = req
        s.request = req
        return types.SimpleNamespace(
            write=lambda **kw: ep("model_write")(ctl, **kw),
            action=lambda **kw: ep("model_action")(ctl, **kw),
            records=lambda **kw: ep("model_records")(ctl, **kw),
            form=lambda **kw: ep("model_form")(ctl, **kw),
            report=lambda **kw: ep("model_report")(ctl, **kw),
        )

    try:
        yield as_user
    finally:
        g.request, s.request = old_g, old_s


def _flush(c):
    c.env.flush_all()
    c.env.invalidate_all()


def _ladder(
    c, user=None, target="fix.rental.asset", bands=((1e9, "tier_3"),), basis="ruling", **kw
):
    vals = {
        "name": "A12F ladder %s" % uuid.uuid4().hex[:6],
        "target_model": target,
        "basis": basis,
        "threshold_ids": [(0, 0, {"upper_bound": b, "tier": t}) for b, t in bands],
    }
    vals.update(kw)
    return c.env["fix.dofa.ladder"].with_user(user or c.t4).create(vals)


def _rule(c, lad, proposer=None, counter=None, reference=BOARD):
    """The sanctioned path: two acts by two people."""
    _flush(c)
    lad.with_user(proposer or c.t4).action_propose_ruling(
        reference=reference, countersigned_by=(counter or c.t5).id
    )
    _flush(c)
    lad.with_user(counter or c.t5).action_countersign(reference=reference)
    _flush(c)


def _rental_asset(c):
    env = c.env
    tmpl = env["product.template"].create({"name": "A12F Camera"})
    item = env["fix.catalogue.item"].create({"product_tmpl_id": tmpl.id})
    sku = env["fix.rental.sku"].create(
        {"catalogue_item_id": item.id, "daily_rate": 1000, "security_deposit": 5000}
    )
    return env["fix.rental.asset"].create(
        {
            "name": "A12F-CAM-1",
            "rental_sku_id": sku.id,
            "serial_no": "A12F-SN-1",
            "category": "camera",
            "purchase_cost": 100000,
            "acquisition_date": date.today() - timedelta(days=100),
            "operating_unit_id": c.ou.id,
        }
    )


def _gateway(c, user=None, tag="x", **kw):
    vals = {
        "provider": "a12f-%s" % tag,
        "country_code": "BD",
        "currencies": "BDT",
        "credential_ref": "vault://fix/payments/%s" % tag,
    }
    vals.update(kw)
    return c.env["fix.payment.gateway"].with_user(user or c.pa).create(vals)


def _inbox_approve(record, approver, requester):
    if record.approval_state != "pending":
        record.with_user(requester).action_request_approval(justification="a12f")
    task = record.approval_request_id.task_ids.filtered(
        lambda t: t.state == "pending" and t.assigned_user_id == approver
    )
    assert task, "approver got no inbox task"
    task.with_user(approver).action_approve(comment="ok")


def _live_gateway(c, tag="live", **kw):
    gw = _gateway(c, tag=tag, **kw)
    _inbox_approve(gw, c.approver, c.pa)
    _inbox_approve(gw, c.approver, c.pa)
    gw.invalidate_recordset()
    assert gw.state == "active" and gw.mode == "live"
    return gw


@pytest.fixture
def shop(c):
    env = c.env
    product = env["product.template"].create({"name": "A12F Router", "list_price": 1200.0})
    # A04 ERP M38-F1: the storefront sells only at a released M11 price
    # (BDT 1,043.48 excl. VAT = BDT 1,200.00 with 15% VAT), never list_price
    released_card(env, product, 1043.48)
    partner = env["res.partner"].create({"name": "A12F Customer"})

    def cart():
        crt = env["fix.storefront.cart"].create({"customer_id": partner.id})
        env["fix.storefront.cart.line"].create(
            {"cart_id": crt.id, "product_id": product.id, "quantity": 1, "unit_price": 1200.0}
        )
        return crt

    return cart


def _place(c, cart, rail="bkash"):
    return attempt(
        c.env, lambda: cart.action_place_order(shipping_address="House 3, Dhaka", payment_rail=rail)
    )


def _pack(c, user=None, kind="holidays", code="NP-HOL-A12F", lines=None):
    env = c.env
    pack = (
        env["fix.country.pack"]
        .with_user(user or c.pa)
        .create({"name": "P %s" % code, "code": code, "kind": kind, "version": "1"})
    )
    for i, ln in enumerate(lines or [{"date_value": "2027-02-15"}]):
        vals = {"pack_id": pack.id, "code": "L%d" % i, "name": "L%d" % i, "name_bn": "এল"}
        vals.update(ln)
        env["fix.country.pack.line"].with_user(user or c.pa).create(vals)
    return pack


def _walk_pack(c, pack, author=None, certifier=None):
    author, certifier = author or c.pa, certifier or c.pa2
    pack.with_user(author).action_validate()
    pack.with_user(certifier).action_certify(note="Gazette of 2 Jan 2027")
    pack.with_user(certifier).action_activate()
    return pack


def _change(c, state="approved", title="A12F change"):
    chg = c.env["fix.itsm.change"].sudo().create({"title": title})
    if state:
        chg.sudo().write({"state": state})
    return chg


def _environment(c, name="A12F Target", kind="production"):
    return (
        c.env["fix.platform.environment"]
        .sudo()
        .create({"name": name, "kind": kind, "base_url": "https://%s.example" % kind})
    )


def _release(c, user=None, **kw):
    vals = {
        "name": "A12F release",
        "version": "9.%s" % uuid.uuid4().hex[:6],
        "rollback_plan": "roll back to previous tag",
        "environment_id": _environment(c, name="Env %s" % uuid.uuid4().hex[:6]).id,
    }
    vals.update(kw)
    return c.env["fix.platform.release"].with_user(user or c.pa).create(vals)


def _js_lists(js):
    """{screen id: (model, cols)} for every model_list in a fragment."""
    out = {}
    pattern = (
        r"'(M\d+-[\w-]+)':\s*\{\s*kind:\s*'model_list',\s*model:\s*'([\w.]+)'[^\[]*?"
        r"cols:\s*\[([^\]]*)\]"
    )
    for sid, model, cols in re.findall(pattern, js, flags=re.S):
        out[sid] = (model, re.findall(r"'(\w+)'", cols))
    return out


def _js_form_fields(js, form_id):
    """Field names declared by one model_form, up to the next top-level screen."""
    start = js.index("'%s': {" % form_id)
    following = re.search(r"\n  '(M\d+-[\w-]+)':", js[start + 5 :])
    block = js[start : start + 5 + following.start()] if following else js[start:]
    return set(re.findall(r"\{ name: '(\w+)'", block))


# ===================================================================== E1


def test_a12f_e1_replay_one_t4_session_cannot_rule(c, p03):
    """The original attack, exactly: only the T4 session acts, through the screen's
    API. T5 is merely named. Then a clerk tries to retire the BDT 90,868 asset."""
    env = c.env
    asset = _rental_asset(c)
    assert refused(env, lambda: asset.with_user(c.clerk).action_retire())
    w = p03(c.t4).write(
        model="fix.dofa.ladder",
        values={
            "name": "zero",
            "target_model": "fix.rental.asset",
            "basis": "ruling",
            "countersigned_by": c.t5.id,
        },
        lines={
            "field": "threshold_ids",
            "rows": [{"values": {"upper_bound": 1e9, "tier": "tier_0"}}],
        },
    )
    assert not perr(w), w
    lad = env["fix.dofa.ladder"].browse(w["id"])
    # the old button is gone from the surface...
    r = p03(c.t4).action(
        model="fix.dofa.ladder",
        ids=[lad.id],
        method="action_put_in_force",
        kwargs={"reference": BOARD},
    )
    assert perr(r)
    # ...and the ORM path is only ever a proposal
    lad.with_user(c.t4).action_put_in_force(reference=BOARD)
    _flush(c)
    assert not lad.in_force and lad.ruling_state == "proposed" and not lad.countersigned_at
    assert env["fix.dofa.ladder"].thresholds_for("fix.rental.asset") is None
    assert refused(env, lambda: asset.with_user(c.clerk).action_retire())


def test_a12f_e1_screen_walk_propose_then_countersign(c, p03):
    env = c.env
    form = p03(c.t4).form(model="fix.dofa.ladder", fields=[{"name": "countersigner_choice"}])
    choices = form["fields"][0]["choices"]
    assert str(c.t5.id) in {x["key"] for x in choices}
    w = p03(c.t4).write(
        model="fix.dofa.ladder",
        values={
            "name": "Walk",
            "target_model": "fix.rental.asset",
            "basis": "ruling",
            "countersigner_choice": str(c.t5.id),
        },
        lines={
            "field": "threshold_ids",
            "rows": [{"values": {"upper_bound": 1e9, "tier": "tier_4"}}],
        },
    )
    assert not perr(w), w
    lad = env["fix.dofa.ladder"].browse(w["id"])
    assert lad.countersigned_by == c.t5
    _flush(c)
    r = p03(c.t4).action(
        model="fix.dofa.ladder",
        ids=lad.ids,
        method="action_propose_ruling",
        kwargs={"reference": BOARD},
    )
    assert not perr(r), r
    _flush(c)
    assert not lad.in_force and lad.ruling_state == "proposed" and lad.proposed_by == c.t4
    r = p03(c.t5).action(
        model="fix.dofa.ladder",
        ids=lad.ids,
        method="action_countersign",
        kwargs={"reference": BOARD},
    )
    assert not perr(r), r
    _flush(c)
    assert lad.in_force and lad.ruling_state == "in_force"
    assert (lad.ruled_by, lad.countersigned_by) == (c.t4, c.t5) and lad.countersigned_at
    assert lad.ruling_reference == BOARD


def test_a12f_e1_only_the_named_active_tier5_countersigns(c):
    env = c.env
    lad = _ladder(c)
    assert refused(env, lambda: lad.with_user(c.t4).action_propose_ruling(reference=BOARD))
    for counter in (c.t4, c.clerk, c.t4b):  # self / no tier / Tier 4 only
        assert refused(
            env,
            lambda u=counter: lad.with_user(c.t4).action_propose_ruling(
                reference=BOARD, countersigned_by=u.id
            ),
        ), counter.login
    c.t5b.sudo().write({"active": False})
    res = attempt(
        env,
        lambda: lad.with_user(c.t4).action_propose_ruling(
            reference=BOARD, countersigned_by=c.t5b.id
        ),
    )
    assert res[0] == "refused" and "archived" in res[1]
    assert refused(
        env,
        lambda: lad.with_user(c.t4).action_propose_ruling(reference="x", countersigned_by=c.t5.id),
    )
    lad.with_user(c.t4).action_propose_ruling(reference=BOARD, countersigned_by=c.t5.id)
    other_t5 = _user(env, "a12f_t5c", [T5])
    for actor in (c.t4, c.t4b, c.clerk, other_t5):
        assert refused(env, lambda u=actor: lad.with_user(u).action_countersign(reference=BOARD))
    assert refused(env, lambda: lad.with_user(c.t5).action_countersign(reference="OTHER-1"))
    assert refused(env, lambda: lad.with_user(c.t5).write({"in_force": True}))
    assert not lad.in_force


def test_a12f_e1_proposal_freezes_what_is_being_ruled(c):
    env = c.env
    lad = _ladder(c, bands=((1e9, "tier_5"),))
    lad.with_user(c.t4).action_propose_ruling(reference=BOARD, countersigned_by=c.t5.id)
    band = lad.threshold_ids[:1]
    assert refused(env, lambda: band.with_user(c.t4).write({"tier": "tier_0"}))
    assert refused(env, lambda: lad.with_user(c.t4).write({"countersigned_by": c.t5b.id}))
    assert refused(env, lambda: lad.with_user(c.t4).write({"target_model": "fix.complaint"}))
    assert refused(env, lambda: lad.with_user(c.t4b).action_withdraw_ruling(reason="no"))
    lad.with_user(c.t5).action_withdraw_ruling(reason="the minute was not passed")
    assert lad.ruling_state == "draft" and not lad.proposed_by and not lad.countersigned_by


def test_a12f_e1_countersign_runs_the_doa_register_resync(c):
    """cd_grc overrides action_put_in_force; the countersignature must reach it."""
    env = c.env
    lad = _ladder(c, bands=((1e9, "tier_5"),))
    _rule(c, lad)
    rows = (
        env["fix.grc.authority"].sudo().search([("source_ref", "=", "fix.dofa.ladder:%d" % lad.id)])
    )
    if "source_ref" in env["fix.grc.authority"]._fields and not rows:
        rows = env["fix.grc.authority"].sudo().search([("source_ref", "like", "ladder")])
    assert rows, "the DoA register did not resync on the countersignature"


# ===================================================================== E2


def _req(registry, uid, fn):
    with registry.cursor() as cr:
        env = api.Environment(cr, uid, {"lang": "en_US", "tz": "Asia/Dhaka"})
        return fn(env)


def _mk_user(registry, login, xmlid):
    def go(env):
        gids = [env.ref("base.group_user").id, env.ref(xmlid).id]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create({"name": login, "login": login, "group_ids": [(6, 0, gids)]})
            .id
        )

    return _req(registry, SUPERUSER_ID, go)


def _create_ladder(registry, uid, basis):
    return _req(
        registry,
        uid,
        lambda env: env["fix.dofa.ladder"]
        .create(
            {
                "name": "commit %s %s" % (basis, uid),
                "target_model": "fix.rental.asset",
                "basis": basis,
                "threshold_ids": [(0, 0, {"upper_bound": 1e9, "tier": "tier_3"})],
            }
        )
        .id,
    )


def _propose_and_countersign(registry, proposer, counter, lad_id, ref):
    _req(
        registry,
        proposer,
        lambda env: env["fix.dofa.ladder"]
        .browse(lad_id)
        .action_propose_ruling(reference=ref, countersigned_by=counter),
    )
    _req(
        registry,
        counter,
        lambda env: env["fix.dofa.ladder"].browse(lad_id).action_countersign(reference=ref),
    )


@pytest.mark.parametrize("second", ["same", "other"])
def test_a12f_e2_supersede_real_commits(odoo_registry, second):
    """Each step is its own committed transaction, like separate HTTP requests. A
    different T4 last wrote the new ladder: that was the UniqueViolation."""
    tag = uuid.uuid4().hex[:6]
    x = _mk_user(odoo_registry, "cx_%s_x" % tag, T4)
    y = _mk_user(odoo_registry, "cx_%s_y" % tag, T4)
    t5 = _mk_user(odoo_registry, "cx_%s_t5" % tag, T5)
    ids = []

    def state(env):
        env.cr.execute(
            "SELECT id, in_force FROM fix_dofa_ladder WHERE id IN %s ORDER BY id", [tuple(ids)]
        )
        return env.cr.fetchall()

    try:
        ids.append(_create_ladder(odoo_registry, x, "ruling"))
        _propose_and_countersign(odoo_registry, x, t5, ids[0], "BM-1")
        actor = {"same": x, "other": y}[second]
        ids.append(_create_ladder(odoo_registry, actor, "req_text"))
        _propose_and_countersign(odoo_registry, actor, t5, ids[1], "BM-2")
        assert _req(odoo_registry, SUPERUSER_ID, state) == [(ids[0], False), (ids[1], True)]
    finally:

        def cleanup(env):
            env.cr.execute("DELETE FROM fix_dofa_ladder WHERE id IN %s", [tuple(ids) or (0,)])
            env["fix.grc.authority"].sudo()._doa_rebuild()
            env["res.users"].browse([x, y, t5]).sudo().write({"active": False})

        _req(odoo_registry, SUPERUSER_ID, cleanup)


# ===================================================================== E3, E4


def test_a12f_e3_in_force_ruling_cannot_be_moved_by_orm(c):
    env = c.env
    other = env["res.company"].create({"name": "A12F Other Co"})
    c.t4b.sudo().write({"company_ids": [(4, other.id)]})
    lad = _ladder(c, target="fix.complaint", bands=((1e9, "tier_0"),))
    _rule(c, lad)
    assert refused(env, lambda: lad.with_user(c.t4b).write({"target_model": "fix.rental.asset"}))
    assert refused(env, lambda: lad.with_user(c.t4b).write({"company_id": other.id}))
    assert refused(env, lambda: lad.with_user(c.t4b).write({"basis": "dofa_matrix"}))
    assert lad.target_model == "fix.complaint" and lad.in_force


def test_a12f_e4_superseded_ladder_cannot_be_reruled_on_its_stale_stamp(c):
    env = c.env
    a = _ladder(c, bands=((1e9, "tier_1"),), basis="ruling")
    b = _ladder(c, bands=((1e9, "tier_5"),), basis="req_text")
    _rule(c, a, reference="BOARD-MIN-1")
    _rule(c, b, reference="BOARD-MIN-2")
    a.invalidate_recordset()
    assert a.ruling_state == "superseded" and a.superseded_by_id == b and a.superseded_at
    assert not a.ruling_reference and not a.countersigned_by, "the stale stamp must go"
    assert "BOARD-MIN-1" in " ".join(str(x) for x in a.message_ids.mapped("body"))
    assert refused(env, lambda: a.with_user(c.t4b).action_put_in_force(reference=""))
    assert refused(env, lambda: a.with_user(c.t4b).action_propose_ruling(reference=""))
    # a fresh reference and a fresh countersignature do re-rule it
    _rule(c, a, proposer=c.t4b, counter=c.t5b, reference="BOARD-MIN-3")
    a.invalidate_recordset()
    assert a.in_force and a.ruled_by == c.t4b and not a.superseded_at


def _migration():
    path = (
        Path(__file__).resolve().parents[2]
        / "cd_entity_config"
        / "migrations"
        / "19.0.1.0.2"
        / "post-a12_finish_m30.py"
    )
    spec = importlib.util.spec_from_file_location("a12f_m30_migration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a12f_e4_migration_clears_the_live_stale_stamps(c):
    env = c.env
    winner = _ladder(c, basis="req_text")
    loser = _ladder(c, basis="dofa_matrix")
    winner._guarded().write({"in_force": True, "ruled_by": c.t4.id, "ruling_reference": "OLD-1"})
    loser._guarded().write(
        {
            "ruled_by": c.t4.id,
            "ruled_at": fields.Datetime.now(),
            "ruling_reference": "OLD-1",
            "countersigned_by": c.t5.id,
        }
    )
    _migration()._supersede_stale_ladders(env)
    assert loser.ruling_state == "superseded" and loser.superseded_by_id == winner
    assert not loser.ruling_reference and not loser.countersigned_by
    assert "OLD-1" in " ".join(str(x) for x in loser.message_ids.mapped("body"))
    assert "predates the countersign step" in " ".join(
        str(x) for x in winner.message_ids.mapped("body")
    )


# ===================================================================== E5, E12


def test_a12f_e5_live_gateway_is_not_deleted(c):
    gw = _live_gateway(c, tag="d11")
    assert refused(c.env, lambda: gw.with_user(c.pa).unlink())
    draft = _gateway(c, tag="dd")
    draft.with_user(c.pa).unlink()
    assert not draft.exists()


def test_a12f_e5_suspended_gateway_archive_or_rename_does_not_reopen_checkout(c, p03, shop):
    env = c.env
    gw = _live_gateway(c, tag="d12", provider="bkash")
    gw.with_user(c.approver).action_suspend(reason="fraud")
    assert _place(c, shop())[0] == "refused"
    assert perr(
        p03(c.pa).write(model="fix.payment.gateway", record_id=gw.id, values={"active": False})
    )
    assert perr(
        p03(c.pa).write(model="fix.payment.gateway", record_id=gw.id, values={"provider": "x"})
    )
    assert refused(env, lambda: gw.with_user(c.pa).write({"active": False}))
    assert refused(env, lambda: gw.with_user(c.pa).write({"provider": "bkash-old"}))
    assert refused(env, lambda: gw.with_user(c.approver).write({"country_code": "NP"}))
    # even an archive by superuser code keeps the rail shut
    gw.sudo().write({"active": False})
    assert _place(c, shop())[0] == "refused"


def test_a12f_e12_checkout_reads_the_row_for_this_country(c, shop):
    # A04 ERP M38-F13: a web checkout is paid by the signed callback, so the
    # rail needs its callback secret (configuration, set here) as well
    c.env["ir.config_parameter"].sudo().set_param("cd_storefront.gateway_secret.bkash", "a12f-test")
    np_live = _live_gateway(c, tag="d14", provider="bkash", country_code="NP")
    assert _place(c, shop())[0] == "refused", "an NP row must not serve a BD sale"
    bd = _live_gateway(c, tag="d15", provider="bkash", country_code="BD")
    assert _place(c, shop())[0] == "ok"
    bd.with_user(c.approver).action_suspend(reason="fraud")
    assert _place(c, shop())[0] == "refused"
    assert np_live.state == "active"


def test_a12f_e12_rail_with_no_row_is_refused(c, shop):
    """A04 ERP M38-F13: a prepaid rail with no gateway master used to take
    orders nobody could ever pay; it is now refused until M65 has it live."""
    assert not c.env["fix.payment.gateway"].sudo().search_count([("provider", "=ilike", "nagad")])
    outcome, message = _place(c, shop(), rail="nagad")
    assert outcome == "refused" and "not configured" in message


# ===================================================================== E6


def test_a12f_e6_only_an_active_loaded_pack_moves_the_vat_date(c):
    env = c.env
    e = c.entity
    e.sudo().write({"statutory_calendar_rule": "mushak_next_working_day", "vat_statutory_day": 15})
    before = e.get_vat_return_due_date(2027, 1)
    pack = _pack(c, lines=[{"date_value": str(before)}])
    _flush(c)
    assert e.get_vat_return_due_date(2027, 1) == before, "a draft pack moved the date"
    _walk_pack(c, pack)
    _flush(c)
    assert e.get_vat_return_due_date(2027, 1) == before, "active but not loaded moved the date"
    pack.with_user(c.pa).action_load()
    _flush(c)
    assert e.get_vat_return_due_date(2027, 1) > before, "an active, loaded holiday must count"
    pack.with_user(c.pa).action_retire()
    _flush(c)
    assert e.get_vat_return_due_date(2027, 1) == before, "a retired pack moved the date"
    assert env["fix.country.pack"].browse(pack.id).state == "retired"


# ===================================================================== E7


def test_a12f_e7_release_is_created_on_screen(c, p03):
    target = _environment(c)
    w = p03(c.pa).write(
        model="fix.platform.release",
        values={
            "version": "9.9.9",
            "name": "New",
            "planned_on": "2026-12-01",
            "rollback_plan": "p",
            "environment_id": target.id,
            "owner_id": c.pa.id,
        },
    )
    assert not perr(w), w
    rel = c.env["fix.platform.release"].browse(w["id"])
    assert (rel.version, rel.name, rel.environment_id) == ("9.9.9", "New", target)
    assert not perr(
        p03(c.pa).write(model="fix.platform.release", record_id=rel.id, values={"name": "Renamed"})
    )


def test_a12f_e7_second_person_environment_and_one_release_per_change(c, p03):
    env = c.env
    chg = _change(c)
    rel = _release(c, itsm_change_id=chg.id, owner_id=c.pa.id)
    r = p03(c.pa).action(model="fix.platform.release", ids=rel.ids, method="action_release")
    assert perr(r) and "second person" in perr(r)
    no_env = _release(c, itsm_change_id=_change(c).id, environment_id=False)
    assert refused(env, lambda: no_env.with_user(c.pa2).action_release())
    a = _release(c, itsm_change_id=chg.id)
    b = _release(c, itsm_change_id=chg.id)
    a.with_user(c.pa2).action_release()
    assert a.released_by_id == c.pa2
    assert refused(env, lambda: b.with_user(c.pa2).action_release())


def test_a12f_n_m66_6_reviewed_ships_and_retro_rejected_does_not(c, p03):
    assert "retro_approval_state" in c.env["fix.itsm.change"]._fields
    reviewed = _release(c, itsm_change_id=_change(c, "reviewed", "reviewed").id)
    r = p03(c.pa2).action(model="fix.platform.release", ids=reviewed.ids, method="action_release")
    assert not perr(r), r
    assert reviewed.state == "released"

    rejected = _change(c, "implemented", "emergency, rejected afterwards")
    rejected.sudo().write({"retro_approval_state": "rejected"})
    rel = _release(c, itsm_change_id=rejected.id)
    r = p03(c.pa2).action(model="fix.platform.release", ids=rel.ids, method="action_release")
    assert perr(r) and "retrospective" in perr(r)
    assert rel.state == "planned"


def test_a12f_e7_released_release_is_frozen_and_rolls_back(c, p03):
    env = c.env
    rel = _release(c, itsm_change_id=_change(c).id)
    r = p03(c.pa2).action(model="fix.platform.release", ids=rel.ids, method="action_start_test")
    assert not perr(r), r
    assert rel.state == "in_test"
    r = p03(c.pa2).action(model="fix.platform.release", ids=rel.ids, method="action_release")
    assert not perr(r), r
    other = _change(c, "implemented", "other")
    assert perr(
        p03(c.pa).write(
            model="fix.platform.release", record_id=rel.id, values={"itsm_change_id": other.id}
        )
    )
    assert perr(
        p03(c.pa).write(
            model="fix.platform.release",
            record_id=rel.id,
            values={"rollback_plan": "rewritten", "planned_on": "2020-01-01"},
        )
    )
    assert refused(env, lambda: rel.with_user(c.pa).write({"version": "0.0.0"}))
    assert refused(env, lambda: rel.with_user(c.pa).write({"environment_id": False}))
    assert perr(
        p03(c.pa).action(model="fix.platform.release", ids=rel.ids, method="action_rollback")
    )
    r = p03(c.pa).action(
        model="fix.platform.release",
        ids=rel.ids,
        method="action_rollback",
        kwargs={"reason": "bad build"},
    )
    assert not perr(r), r
    assert rel.state == "rolled_back" and rel.rolled_back_reason == "bad build"


# ===================================================================== E8


def test_a12f_e8_gateway_is_created_on_screen_with_its_vault_reference(c, p03):
    form = p03(c.pa).form(
        model="fix.payment.gateway",
        fields=[{"name": "credential_ref", "required": True}, {"name": "mode", "required": True}],
    )
    meta = {f["name"]: f["readonly"] for f in form["fields"]}
    assert meta["credential_ref"] is False and meta["mode"] is True
    w = p03(c.pa).write(
        model="fix.payment.gateway",
        values={
            "provider": "NewPay",
            "country_code": "BD",
            "currencies": "BDT",
            "credential_ref": "vault://fix/payments/newpay",
            "settlement_cycle_days": 2,
        },
    )
    assert not perr(w), w
    gw = c.env["fix.payment.gateway"].browse(w["id"])
    assert gw.sudo().credential_ref == "vault://fix/payments/newpay" and gw.state == "draft"
    # afterwards the reference changes only through rotation
    assert perr(
        p03(c.pa).write(
            model="fix.payment.gateway", record_id=gw.id, values={"credential_ref": "vault://x/y"}
        )
    )


def test_a12f_e8_live_rotation_is_routed_and_namespaced(c, p03):
    env = c.env
    gw = _live_gateway(c, tag="d9")
    old = gw.sudo().credential_ref
    res = attempt(
        env,
        lambda: gw.with_user(c.pa).action_rotate_credential(
            new_ref="vault://attacker-namespace/stolen", reason="r"
        ),
    )
    assert res[0] == "refused" and "namespace" in res[1]
    r = p03(c.pa).action(
        model="fix.payment.gateway",
        ids=gw.ids,
        method="action_rotate_credential",
        kwargs={"new_ref": "vault://fix/payments/d9-2", "reason": "scheduled"},
    )
    assert not perr(r), r
    _flush(c)
    assert gw.sudo().credential_ref == old, "one person must not rotate a live rail"
    assert gw.approval_state == "pending" and gw.state == "active" and gw.mode == "live"
    task = gw.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == c.approver)
    assert task and c.pa not in gw.approval_request_id.task_ids.mapped("assigned_user_id")
    task.with_user(c.approver).action_approve(comment="ok")
    _flush(c)
    assert gw.sudo().credential_ref == "vault://fix/payments/d9-2"
    assert not gw.sudo().pending_credential_ref and gw.approval_state == "approved"
    assert (
        env["fix.security.audit"]
        .sudo()
        .search_count(
            [
                ("event", "=", "payment.gateway_credential_rotated"),
                ("object_ref", "=", "fix.payment.gateway,%d" % gw.id),
            ]
        )
    )


def test_a12f_e8_recalled_rotation_leaves_nothing_waiting(c):
    gw = _live_gateway(c, tag="d9b")
    gw.with_user(c.pa).action_rotate_credential(new_ref="vault://fix/payments/z", reason="r")
    gw.with_user(c.pa).action_recall_approval()
    _flush(c)
    assert not gw.sudo().pending_credential_ref and gw.approval_state == "none"


def test_a12f_e8_rotation_button_supplies_both_kwargs():
    assert "m: 'action_rotate_credential'" in M65_JS
    assert "kwarg: 'new_ref'" in M65_JS and "Why is it being rotated?" in M65_JS


# ===================================================================== E9


def test_a12f_e9_entity_is_created_on_screen_and_statutory_fields_recorded(c, p03):
    env = c.env
    co = env["res.company"].create({"name": "A12F New Co"})
    c.pa.sudo().write({"company_ids": [(4, co.id)]})
    w = p03(c.pa).write(
        model="fix.entity",
        values={"code": "A12FNEW", "legal_name": "New Co Ltd", "company_id": co.id},
    )
    assert not perr(w), w
    r = p03(c.pa).write(
        model="fix.entity",
        record_id=w["id"],
        values={
            "bin_number": "1000000000017",
            "tin_number": "100000000017",
            "incorporation_date": "2020-01-01",
        },
    )
    assert not perr(r), r
    other = env["res.company"].create({"name": "A12F Other"})
    c.pa.sudo().write({"company_ids": [(4, other.id)]})
    assert perr(
        p03(c.pa).write(model="fix.entity", record_id=w["id"], values={"company_id": other.id})
    )
    for form in ("M30-form-entity",):
        assert {"company_id", "bin_number", "tin_number", "vat_statutory_day"} <= _js_form_fields(
            M30_JS, form
        )
    assert {"company_id", "bin_number", "tin_number"} <= _js_form_fields(M65_JS, "M65-form-entity")


def test_a12f_e9_vat_date_needs_finance_and_is_audited(c):
    env = c.env
    e = c.entity
    assert refused(env, lambda: e.with_user(c.pa).write({"vat_statutory_day": 28}))
    assert refused(
        env, lambda: e.with_user(c.pa).write({"statutory_calendar_rule": "strict_calendar_day"})
    )
    finance = _user(env, "a12f_fin", [PA, FINANCE])
    before = (
        env["fix.security.audit"].sudo().search_count([("event", "=", "entity.statutory_changed")])
    )
    e.with_user(finance).write({"vat_statutory_day": 20})
    assert (
        env["fix.security.audit"].sudo().search_count([("event", "=", "entity.statutory_changed")])
        > before
    )
    # the same value echoed by the form moves nothing and needs nothing
    e.with_user(c.pa).write({"vat_statutory_day": 20})


def test_a12f_e9_bin_tin_format(c):
    env = c.env
    assert refused(env, lambda: c.entity.with_user(c.pa).write({"bin_number": "not-a-bin"}))
    assert refused(env, lambda: c.entity.with_user(c.pa).write({"tin_number": "1"}))
    c.entity.with_user(c.pa).write({"bin_number": "1000000000017", "tin_number": "100000000017"})


# ===================================================================== E10


def test_a12f_e10_author_cannot_certify_and_a_vague_basis_is_refused(c):
    env = c.env
    pack = _pack(c)
    pack.with_user(c.pa).action_validate()
    assert refused(env, lambda: pack.with_user(c.pa).action_certify(note="Gazette of 2 Jan 2027"))
    assert refused(env, lambda: pack.with_user(c.pa2).action_certify(note="x"))
    pack.with_user(c.pa2).action_certify(note="Gazette of 2 Jan 2027")
    assert pack.certified_by_id == c.pa2


def test_a12f_e10_pack_is_frozen_after_validation(c, p03):
    env = c.env
    pack = _pack(c, code="NP-HOL-F")
    line = pack.line_ids[:1]
    pack.with_user(c.pa).action_validate()
    assert refused(env, lambda: line.with_user(c.pa).write({"date_value": "2027-03-01"}))
    assert perr(
        p03(c.pa).write(model="fix.country.pack.line", record_id=line.id, values={"name": "edited"})
    )
    assert refused(
        env,
        lambda: env["fix.country.pack.line"]
        .with_user(c.pa)
        .create({"pack_id": pack.id, "code": "NEW", "name": "n", "name_bn": "ন"}),
    )
    assert refused(env, lambda: line.with_user(c.pa).unlink())
    assert perr(
        p03(c.pa).write(model="fix.country.pack", record_id=pack.id, values={"version": "2"})
    )
    # a validated pack can go back for correction; a certified one cannot
    pack.with_user(c.pa).action_back_to_draft()
    line.with_user(c.pa).write({"date_value": "2027-03-01"})
    _walk_pack(c, pack)
    assert refused(env, lambda: pack.with_user(c.pa).action_back_to_draft())
    assert refused(env, lambda: line.with_user(c.pa).write({"date_value": "2027-03-02"}))


def test_a12f_e10_load_copies_per_kind_and_says_what_it_did(c):
    env = c.env
    Address = env["fix.bd.address"]
    pack = _pack(
        c,
        kind="divisions",
        code="NP-DIV-L",
        lines=[
            {"code": "DIVA", "name": "A12F Division", "name_bn": "বিভাগ"},
            {"code": "DISA", "parent_code": "DIVA", "name": "A12F District", "name_bn": "জেলা"},
        ],
    )
    _walk_pack(c, pack)
    assert not Address.search_count([("district", "=", "A12F District")])
    out = pack.with_user(c.pa).action_load()
    assert (
        Address.search_count(
            [("district", "=", "A12F District"), ("division", "=", "A12F Division")]
        )
        == 1
    )
    assert "1 address rows added" in out["note"] and pack.load_summary == out["note"]
    assert "already present" in pack.with_user(c.pa).action_load()["note"]

    cal = env["fix.working.calendar"].create({"name": "A12F National"})
    hol = _walk_pack(c, _pack(c, code="NP-HOL-L", lines=[{"date_value": "2027-02-15"}]))
    out = hol.with_user(c.pa).action_load()
    assert "national calendar" in out["note"]
    rows = cal.holiday_ids.filtered(lambda h: h.pack_line_id in hol.line_ids)
    assert rows and rows[0].date_from == date(2027, 2, 15)
    hol.with_user(c.pa).action_retire()
    assert not cal.holiday_ids.filtered(
        lambda h: h.pack_line_id in hol.line_ids
    ), "retire removes them"

    post = _walk_pack(c, _pack(c, kind="postcodes", code="NP-PC", lines=[{"code": "1205"}]))
    assert "nothing was copied" in post.with_user(c.pa).action_load()["note"]


def test_a12f_e10_bangladesh_loads_as_draft_from_the_screen_and_is_not_certified(c, p03):
    env = c.env
    env["fix.country.pack"].sudo().search(
        [("code", "in", ("BD-DIV-DIST-2026", "BD-HOL-2026"))]
    ).unlink()
    any_pack = _pack(c, code="NP-ANY")
    r = p03(c.pa).action(
        model="fix.country.pack", ids=any_pack.ids, method="action_load_bangladesh_drafts"
    )
    assert not perr(r), r
    assert "must verify" in r["result"]["note"]
    packs = env["fix.country.pack"].search([("code", "in", ("BD-DIV-DIST-2026", "BD-HOL-2026"))])
    assert len(packs) == 2
    for pack in packs:
        assert pack.state == "draft" and not pack.certified_by_id and not pack.certification_note
        assert not pack.loaded_at and pack.create_uid == c.pa
        assert "must verify" in " ".join(str(x) for x in pack.message_ids.mapped("body"))
    # the second person walks it; the loader never does
    hol = packs.filtered(lambda p: p.code == "BD-HOL-2026")
    hol.with_user(c.pa).action_validate()
    assert refused(env, lambda: hol.with_user(c.pa).action_certify(note="Gazette of 2 Jan 2027"))
    # idempotent
    assert (
        p03(c.pa).action(
            model="fix.country.pack", ids=any_pack.ids, method="action_load_bangladesh_drafts"
        )["result"]["created"]
        == []
    )
    assert perr(
        p03(c.clerk).action(
            model="fix.country.pack", ids=any_pack.ids, method="action_load_bangladesh_drafts"
        )
    )


# ===================================================================== E11, E22 static screen shape


def test_a12f_e11_ladder_and_band_grids_have_a_form_route():
    assert "'fix.dofa.ladder': 'M30-form-dofa-ladder'" in M30_JS
    assert "'M30-dofa-ladders': 'M30-form-dofa-ladder'" in M30_JS
    assert "'fix.dofa.threshold': 'M30-form-dofa-band'" in M30_JS
    assert "'M30-dofa-bands': 'M30-form-dofa-band'" in M30_JS


def test_a12f_e11_band_is_created_from_the_grid_payload(c, p03):
    lad = _ladder(c, basis="req_text")
    w = p03(c.t4).write(
        model="fix.dofa.threshold",
        values={"ladder_id": lad.id, "upper_bound": 500, "tier": "tier_1"},
    )
    assert not perr(w), w


def test_a12f_e22_no_phantom_columns_on_any_list(c):
    bad = []
    for js in (M30_JS, M65_JS):
        for sid, (model, cols) in _js_lists(js).items():
            for col in cols:
                if col not in c.env[model]._fields:
                    bad.append("%s %s.%s" % (sid, model, col))
    assert not bad, bad
    assert _js_lists(M30_JS)["M30-backup"][1] and _js_lists(M65_JS)["M65-intercompany"][1]


def test_a12f_e22_branch_and_flag_and_packline_forms(c):
    assert {
        "calendar_id",
        "manager_id",
        "phone",
        "email",
        "address_id",
        "name_bn",
    } <= _js_form_fields(M30_JS, "M30-form-branch")
    assert "branch_ids" in _js_form_fields(M30_JS, "M30-form-flag")
    packline = _js_form_fields(M65_JS, "M65-form-packline")
    assert "date_value" in packline and "active" not in packline


def test_a12f_e22_every_form_field_is_on_the_model(c):
    forms = re.findall(
        r"'(M\d+-form[\w-]*)':\s*\{[^{]*?model:\s*'([\w.]+)'", M30_JS + M65_JS, flags=re.S
    )
    assert len(forms) > 10
    for form, model in forms:
        js = M30_JS if form.startswith("M30") else M65_JS
        for name in _js_form_fields(js, form):
            comodels = [model] + [
                f.comodel_name for f in c.env[model]._fields.values() if f.type == "one2many"
            ]
            assert any(name in c.env[m]._fields for m in comodels if m in c.env), (form, name)


def test_a12f_e22_status_badge_field_is_requested():
    assert "gl.formCfg.status && gl.formCfg.status.field" in WORKSPACE_JS
    assert "formFields.push({ name: statusField, readonly: true })" in WORKSPACE_JS


def test_a12f_e22_status_field_loads_through_the_form_endpoint(c, p03):
    ann = c.env["fix.platform.announcement"].with_user(c.pa).create({"name": "n"})
    out = p03(c.pa).form(
        model="fix.platform.announcement",
        fields=[{"name": "name"}, {"name": "state", "readonly": True}],
        record_id=ann.id,
    )
    assert out["record"]["state"] == "draft"
    w = p03(c.pa).write(
        model="fix.platform.announcement", record_id=ann.id, values={"name": "m", "state": "draft"}
    )
    assert not perr(w), w


def test_a12f_e22_calendar_lines_and_holidays_on_screen(c, p03):
    cal = c.env["fix.working.calendar"].with_user(c.pa).create({"name": "A12F Cal"})
    r = p03(c.pa).write(
        model="fix.working.calendar",
        record_id=cal.id,
        values={},
        lines={
            "field": "line_ids",
            "rows": [{"values": {"weekday": "sun", "hour_from": 3, "hour_to": 11}}],
        },
    )
    assert not perr(r), r
    assert cal.line_ids.weekday == "sun"
    w = p03(c.pa).write(
        model="fix.working.calendar.holiday",
        values={
            "calendar_id": cal.id,
            "name": "Short",
            "date_from": "2026-12-16",
            "date_to": "2026-12-16",
        },
    )
    assert not perr(w), w
    assert "'fix.working.calendar.holiday': 'M30-form-holiday'" in M30_JS


def test_a12f_e22_countersigner_picker_lists_only_holders(c, p03):
    form = p03(c.t4).form(model="fix.dofa.ladder", fields=[{"name": "countersigner_choice"}])
    labels = {x["label"] for x in form["fields"][0]["choices"]}
    assert c.t5.name in labels and c.clerk.name not in labels and c.t4.name not in labels


def test_a12f_e22_form_save_on_a_superseded_ladder_names_a_new_countersigner(c, p03):
    """The form posts every field and every band row: the echo must pass, the picker
    must win over the echoed countersigned_by, and a changed band must still refuse."""
    a = _ladder(c, basis="ruling")
    b = _ladder(c, basis="req_text")
    _rule(c, a, reference="BOARD-MIN-1")
    _rule(c, b, reference="BOARD-MIN-2")
    a.invalidate_recordset()
    band = a.threshold_ids[:1]
    echo = {"upper_bound": band.upper_bound, "tier": band.tier}
    w = p03(c.t4).write(
        model="fix.dofa.ladder",
        record_id=a.id,
        values={"name": a.name, "countersigner_choice": str(c.t5b.id), "countersigned_by": False},
        lines={"field": "threshold_ids", "rows": [{"id": band.id, "values": echo}]},
    )
    assert not perr(w), w
    assert a.countersigned_by == c.t5b
    assert perr(
        p03(c.t4).write(
            model="fix.dofa.ladder",
            record_id=a.id,
            values={},
            lines={
                "field": "threshold_ids",
                "rows": [{"id": band.id, "values": {"tier": "tier_0"}}],
            },
        )
    )


def test_a12f_op_platform_admin_reads_inventories_values_stay_masked(c, p03):
    for rep in ("job_success_rate", "platform_health", "config_drift"):
        assert not p03(c.pa).report(module="M30", report=rep).get("error"), rep
        assert p03(c.clerk).report(module="M30", report=rep).get("error"), rep
    for model, cols in (
        ("ir.cron", ["name"]),
        ("ir.config_parameter", ["key"]),
        ("fix.intercompany.rule", ["name"]),
    ):
        assert not p03(c.pa).records(model=model, cols=cols).get("error"), model
    env = c.env
    env["ir.config_parameter"].sudo().set_param("a12f.secret", "s3cret-value")
    rows = p03(c.pa).records(
        model="ir.config_parameter", cols=["key", "value"], domain=[("key", "=", "a12f.secret")]
    )
    assert rows["rows"] and "value" not in rows["rows"][0]
    param = env["ir.config_parameter"].sudo().search([("key", "=", "a12f.secret")])
    assert refused(env, lambda: param.with_user(c.pa).sudo(False).read(["value"]))
    assert refused(env, lambda: param.with_user(c.pa).sudo(False).write({"value": "x"}))
    assert refused(
        env, lambda: env["ir.cron"].with_user(c.pa).search([], limit=1).write({"active": False})
    )
    assert env["ir.config_parameter"].with_user(c.pa).get_param("a12f.secret") == "s3cret-value"


# ===================================================================== E13


def test_a12f_e13_vault_path_not_readable_by_plain_user(c, p03):
    gw = _gateway(c, tag="d17", credential_ref="vault://fix/payments/secret-path")
    rows = p03(c.clerk).records(model="fix.payment.gateway", cols=["provider", "credential_ref"])
    row = next(r for r in rows["rows"] if r["id"] == gw.id)
    assert "credential_ref" not in row
    assert refused(c.env, lambda: gw.with_user(c.clerk).read(["credential_ref"]))
    out = p03(c.clerk).report(module="M65", report="gateway_readiness")
    assert not out.get("error"), out
    assert any("ONLY reader" in n for n in out["notes"])
    assert any("does not change a live secret" in n for n in out["notes"])


# ===================================================================== E14


def test_a12f_e14_environment_controls(c, p03):
    env = c.env
    w = p03(c.pa).write(
        model="fix.platform.environment",
        values={
            "name": "A12F New",
            "kind": "production",
            "base_url": "https://n.example",
            "release_channel": "stable",
        },
    )
    assert not perr(w), w
    rec = env["fix.platform.environment"].browse(w["id"])
    assert rec.state == "provisioning"
    assert perr(
        p03(c.pa).write(
            model="fix.platform.environment",
            record_id=rec.id,
            values={"base_url": "http://attacker.example:1/x"},
        )
    )
    assert refused(env, lambda: rec.with_user(c.pa).write({"state": "live"}))
    r = p03(c.pa).action(model="fix.platform.environment", ids=rec.ids, method="action_go_live")
    assert not perr(r), r
    assert rec.state == "live"
    assert perr(
        p03(c.clerk).action(
            model="fix.platform.environment",
            ids=rec.ids,
            method="action_mark_degraded",
            kwargs={"reason": "r"},
        )
    )
    r = p03(c.pa).action(
        model="fix.platform.environment",
        ids=rec.ids,
        method="action_mark_degraded",
        kwargs={"reason": "slow"},
    )
    assert not perr(r), r
    r = p03(c.pa).action(
        model="fix.platform.environment",
        ids=rec.ids,
        method="action_take_offline",
        kwargs={"reason": "maintenance"},
    )
    assert not perr(r), r
    assert rec.state == "offline"
    assert (
        env["fix.security.audit"]
        .sudo()
        .search_count([("object_ref", "=", "fix.platform.environment,%d" % rec.id)])
        >= 3
    )


def test_a12f_e14_non_production_needs_second_person_masking_evidence(c, p03):
    env = c.env
    rec = (
        env["fix.platform.environment"]
        .with_user(c.pa)
        .create({"name": "A12F Staging", "kind": "staging", "base_url": "https://s.example"})
    )
    assert refused(env, lambda: rec.with_user(c.pa).action_go_live())
    assert refused(env, lambda: rec.with_user(c.pa).action_record_masking(evidence="run 7"))
    assert refused(env, lambda: rec.with_user(c.pa2).action_record_masking(evidence=" "))
    r = p03(c.pa2).action(
        model="fix.platform.environment",
        ids=rec.ids,
        method="action_record_masking",
        kwargs={"evidence": "masking run 7"},
    )
    assert not perr(r), r
    rec.with_user(c.pa).action_go_live()
    assert rec.state == "live" and rec.masking_recorded_by_id == c.pa2
    assert refused(env, lambda: rec.with_user(c.pa).write({"masking_state": "pending"}))


def test_a12f_e14_local_dev_may_use_http_but_nothing_else(c):
    env = c.env
    Env = env["fix.platform.environment"].with_user(c.pa)
    assert Env.create({"name": "A12F dev", "kind": "dev", "base_url": "http://127.0.0.1:8069"})
    assert refused(
        env,
        lambda: Env.create({"name": "A12F dev2", "kind": "dev", "base_url": "http://dev.example"}),
    )
    assert refused(
        env,
        lambda: Env.create(
            {"name": "A12F prod", "kind": "production", "base_url": "http://127.0.0.1"}
        ),
    )


# ===================================================================== E15


def test_a12f_e15_second_person_publishes_and_dates_make_sense(c, p03):
    env = c.env
    w = p03(c.pa).write(
        model="fix.platform.announcement",
        values={
            "name": "critical",
            "severity": "critical",
            "audience": "all",
            "publish_on": "2026-11-20",
            "body": "b",
        },
    )
    assert not perr(w), w
    assert perr(
        p03(c.pa).action(model="fix.platform.announcement", ids=[w["id"]], method="action_publish")
    )
    r = p03(c.pa2).action(model="fix.platform.announcement", ids=[w["id"]], method="action_publish")
    assert not perr(r), r
    assert env["fix.platform.announcement"].browse(w["id"]).published_by_id == c.pa2
    assert refused(
        env,
        lambda: env["fix.platform.announcement"]
        .with_user(c.pa)
        .create({"name": "x", "publish_on": "2026-12-01", "expires_on": "2026-01-01"}),
    )


def test_a12f_e15_maintenance_needs_72_hours(c):
    env = c.env
    Ann = env["fix.platform.announcement"].with_user(c.pa)
    soon = Ann.create(
        {
            "name": "m",
            "kind": "maintenance",
            "maintenance_start": datetime.now() + timedelta(hours=5),
        }
    )
    assert refused(env, lambda: soon.with_user(c.pa2).action_publish())
    missing = Ann.create({"name": "m2", "kind": "maintenance"})
    assert refused(env, lambda: missing.with_user(c.pa2).action_publish())
    ok = Ann.create(
        {
            "name": "m3",
            "kind": "maintenance",
            "maintenance_start": datetime.now() + timedelta(hours=80),
        }
    )
    ok.with_user(c.pa2).action_publish()
    assert ok.state == "published"


def test_a12f_e15_any_user_acknowledges_from_the_screen(c, p03):
    ann = c.env["fix.platform.announcement"].with_user(c.pa).create({"name": "n"})
    assert perr(
        p03(c.clerk).action(
            model="fix.platform.announcement", ids=ann.ids, method="action_acknowledge"
        )
    )
    ann.with_user(c.pa2).action_publish()
    for _ in range(2):
        r = p03(c.clerk).action(
            model="fix.platform.announcement", ids=ann.ids, method="action_acknowledge"
        )
        assert not perr(r), r
    rows = p03(c.clerk).records(
        model="fix.platform.announcement", cols=["name", "acknowledged_count", "acknowledged_by_me"]
    )
    row = next(r for r in rows["rows"] if r["id"] == ann.id)
    assert row["acknowledged_count"] == 1
    assert ann.with_user(c.clerk).acknowledged_by_me and not ann.with_user(c.pa).acknowledged_by_me


# ===================================================================== E16


def test_a12f_e16_coverage_is_measured_not_typed(c, p03):
    env = c.env
    field = env["fix.locale.pack"]._fields["coverage_pct"]
    assert field.compute and not field.store
    lo = env["fix.locale.pack"].with_user(c.pa).create({"code": "ne_NP", "name": "Nepali"})
    assert perr(
        p03(c.pa).write(model="fix.locale.pack", record_id=lo.id, values={"coverage_pct": 100})
    )
    assert lo.coverage_pct < 100
    assert perr(p03(c.pa).action(model="fix.locale.pack", ids=lo.ids, method="action_activate"))
    assert lo.state == "draft"
    en = env["fix.locale.pack"].sudo().search([("code", "=", "en_US")], limit=1) or env[
        "fix.locale.pack"
    ].sudo().create({"code": "en_US", "name": "English"})
    assert en.coverage_pct == 100, "source language is fully covered"


def test_a12f_e16_activation_drives_res_lang(c):
    env = c.env
    env["ir.config_parameter"].sudo().set_param("fix_locale.min_activation_coverage_pct", "0")
    lang = env["res.lang"].with_context(active_test=False).search([("code", "=", "fr_FR")], limit=1)
    lang.sudo().write({"active": False})
    lo = env["fix.locale.pack"].with_user(c.pa).create({"code": "fr_FR", "name": "French"})
    lo.with_user(c.pa).action_activate()
    assert lang.active and lo.state == "active"
    lo.with_user(c.pa).action_retire()
    assert not lang.active and lo.state == "retired"
    unknown = env["fix.locale.pack"].with_user(c.pa).create({"code": "xx_XX", "name": "Nope"})
    assert refused(env, lambda: unknown.with_user(c.pa).action_activate())


# ===================================================================== E17, E18


def test_a12f_e17_jurisdiction_is_tracked_and_labelled_documentation(c, p03):
    env = c.env
    rule = env["fix.jurisdiction.rule"].create(
        {
            "jurisdiction": "BD-NBR",
            "rule_area": "tax",
            "requirement": "Mushak 9.1",
            "frequency": "monthly",
        }
    )
    n0 = len(rule.message_ids)
    w = p03(c.pa).write(
        model="fix.jurisdiction.rule", record_id=rule.id, values={"frequency": "annual"}
    )
    assert not perr(w), w
    _flush(c)
    assert len(rule.message_ids) > n0
    assert "DOCUMENTATION ONLY" in M65_JS and "No calculation reads it" in M65_JS


def test_a12f_e18_expansion_ready_needs_real_pack_and_live_gateway(c, p03):
    env = c.env
    env["fix.country.pack"].with_user(c.pa).create(
        {"name": "NP empty", "code": "NP-EMPTY", "kind": "holidays"}
    )
    env["fix.jurisdiction.rule"].with_user(c.pa).create(
        {"jurisdiction": "NP-TAX", "requirement": "x"}
    )
    gw = _gateway(c, tag="d20", country_code="NP")
    _inbox_approve(gw, c.approver, c.pa)  # active but sandbox
    out = p03(c.clerk).report(module="M65", report="expansion_assessment")
    row = next(r for r in out["rows"] if r["country"] == "NP")
    assert row["readiness"] != "Ready" and row["packs"] == 0 and row["gateways"] == 0


# ===================================================================== E19


def test_a12f_e19_branch_lifecycle_and_second_person_closure(c, p03):
    env = c.env
    assert c.branch.state == "provisioning"
    assert perr(
        p03(c.pa).write(model="fix.branch", record_id=c.branch.id, values={"active": False})
    )
    assert refused(env, lambda: c.branch.with_user(c.pa).write({"state": "closed"}))
    assert refused(env, lambda: c.branch.with_user(c.pa).write({"active": False}))
    assert perr(
        p03(c.pa).write(model="fix.branch", record_id=c.branch.id, values={"manager_id": c.pa.id})
    )
    assert not perr(
        p03(c.pa).write(model="fix.branch", record_id=c.branch.id, values={"manager_id": c.pa2.id})
    )
    r = p03(c.pa).action(model="fix.branch", ids=c.branch.ids, method="action_go_live")
    assert not perr(r), r
    assert c.branch.state == "live"
    assert perr(p03(c.clerk).action(model="fix.branch", ids=c.branch.ids, method="action_go_live"))
    assert perr(
        p03(c.pa).action(model="fix.branch", ids=c.branch.ids, method="action_request_closure")
    )
    r = p03(c.pa).action(
        model="fix.branch",
        ids=c.branch.ids,
        method="action_request_closure",
        kwargs={"reason": "lease ended"},
    )
    assert not perr(r), r
    assert c.branch.state == "live" and c.branch.active
    assert perr(
        p03(c.pa).action(model="fix.branch", ids=c.branch.ids, method="action_confirm_closure")
    )
    r = p03(c.pa2).action(model="fix.branch", ids=c.branch.ids, method="action_confirm_closure")
    assert not perr(r), r
    c.branch.invalidate_recordset()
    assert c.branch.state == "closed" and not c.branch.active
    audits = (
        env["fix.security.audit"]
        .sudo()
        .search([("object_ref", "=", "fix.branch,%d" % c.branch.id)])
    )
    assert {"branch.closure_requested", "branch.state_closed", "branch.manager_changed"} <= set(
        audits.mapped("event")
    )


def test_a12f_e19_long_holiday_needs_a_second_person_and_all_changes_audit(c):
    env = c.env
    cal = env["fix.working.calendar"].with_user(c.pa).create({"name": "A12F Cal"})
    Sla = env["fix.sla.kpi.instance"]
    cal.sudo().write(
        {
            "line_ids": [
                (0, 0, {"weekday": d, "hour_from": 3.0, "hour_to": 11.0})
                for d in ("sun", "mon", "tue", "wed", "thu")
            ]
        }
    )
    start = datetime(2026, 11, 8, 4, 0)
    before = Sla.add_business_hours(start, 8.0, cal)
    Holiday = env["fix.working.calendar.holiday"].with_user(c.pa)
    res = attempt(
        env,
        lambda: Holiday.create(
            {"calendar_id": cal.id, "name": "x", "date_from": "2026-11-08", "date_to": "2027-01-06"}
        ),
    )
    assert res[0] == "refused" and "second Platform Admin" in res[1]
    cal.invalidate_recordset()
    assert Sla.add_business_hours(start, 8.0, cal) == before
    # widening a short holiday past the limit is the same attack
    short = Holiday.create(
        {"calendar_id": cal.id, "name": "short", "date_from": "2026-12-16", "date_to": "2026-12-16"}
    )
    assert refused(env, lambda: short.with_user(c.pa).write({"date_to": "2027-02-01"}))
    assert (
        env["fix.security.audit"]
        .sudo()
        .search_count(
            [
                ("event", "=", "calendar.holiday_added"),
                ("object_ref", "=", "fix.working.calendar,%d" % cal.id),
            ]
        )
    )
    assert "Holiday" in " ".join(str(x) for x in cal.message_ids.mapped("body"))
    # the screen path: proposed by one, confirmed by another
    cal.with_user(c.pa).action_propose_closure(
        name="Flood", date_from="2026-11-08", date_to="2026-11-30"
    )
    assert refused(env, lambda: cal.with_user(c.pa).action_confirm_closure())
    assert not cal.holiday_ids.filtered(lambda h: h.name == "Flood")
    cal.with_user(c.pa2).action_confirm_closure()
    assert cal.holiday_ids.filtered(lambda h: h.name == "Flood") and not cal.pending_closure_name


# ===================================================================== E20


def test_a12f_e20_null_company_branch_is_visible_and_repaired_by_an_edit(c, p03):
    env = c.env
    env.flush_all()
    env.cr.execute("UPDATE fix_branch SET company_id = NULL WHERE id = %s", [c.branch.id])
    env.invalidate_all()
    rows = p03(c.pa).records(model="fix.branch", cols=["code", "name"])
    assert not rows.get("error"), rows
    assert c.branch.id in [r["id"] for r in rows["rows"]]
    c.branch.with_user(c.pa).write({"name": "touch"})
    _flush(c)
    assert c.branch.company_id


def test_a12f_e20_migration_moves_null_rows_only_with_one_real_entity(c):
    env = c.env
    env["fix.entity"].sudo().search([("id", "!=", c.entity.id)]).write({"active": False})
    other_co = env["res.company"].create({"name": "A12F Smoke Co"})
    smoke = (
        env["fix.entity"]
        .sudo()
        .create(
            {"code": "SMOKEA12F", "legal_name": "Smoke", "company_id": other_co.id, "active": False}
        )
    )
    lost = env["fix.branch"].create(
        {"code": "A12FLOST", "name": "Lost", "entity_id": smoke.id, "operating_unit_id": c.ou.id}
    )
    env.flush_all()
    env.cr.execute("UPDATE fix_branch SET company_id = NULL WHERE id = %s", [lost.id])
    env.invalidate_all()
    _migration()._null_company_branches(env)
    _flush(c)
    assert lost.entity_id == c.entity and lost.company_id == c.entity.company_id
    # two real entities: nothing is guessed
    co2 = env["res.company"].create({"name": "A12F Real Two"})
    env["fix.entity"].sudo().create(
        {"code": "REALTWO", "legal_name": "Real Two", "company_id": co2.id}
    )
    lost2 = env["fix.branch"].create(
        {"code": "A12FLOST2", "name": "Lost 2", "entity_id": smoke.id, "operating_unit_id": c.ou.id}
    )
    env.flush_all()
    env.cr.execute("UPDATE fix_branch SET company_id = NULL WHERE id = %s", [lost2.id])
    env.invalidate_all()
    _migration()._null_company_branches(env)
    _flush(c)
    assert lost2.entity_id == smoke and not lost2.company_id


def test_a12f_e20_legacy_flag_does_not_toggle(c, p03):
    flag = (
        c.env["fix.feature.flag"]
        .sudo()
        .create({"key": "fix.new_checkout_a12f", "name": "legacy", "enabled": True})
    )
    assert perr(
        p03(c.pa).write(model="fix.feature.flag", record_id=flag.id, values={"enabled": False})
    )
    flag.with_user(c.pa).unlink()
    assert not flag.exists()


def test_a12f_e20_decorative_flags_are_truly_unwired():
    root = Path(__file__).resolve().parents[3]
    names = _migration().DECORATIVE_FLAGS
    this = Path(__file__).name
    for path in root.rglob("*.py"):
        if path.name == this or "migrations" in path.parts or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not any(name in text for name in names), path


def test_a12f_e20_send_window_follows_the_class(c):
    env = c.env
    Config = env["fix.notification.config"].with_user(c.pa)
    env["fix.notification.config"].sudo().search([("channel", "=", "email")]).unlink()
    assert refused(
        env,
        lambda: Config.create(
            {
                "consent_class": "marketing",
                "channel": "email",
                "send_window": "08:00-21:00",
                "sms_route": "non-masking",
                "frequency_cap": 2,
            }
        ),
    )
    row = Config.create(
        {
            "consent_class": "marketing",
            "channel": "email",
            "sms_route": "non-masking",
            "frequency_cap": 2,
        }
    )
    assert row.send_window == "10:00-20:00"
    assert refused(env, lambda: row.with_user(c.pa).write({"send_window": "24/7"}))
    assert Config.create({"consent_class": "security", "channel": "email"}).send_window == "24/7"


# ===================================================================== E21


def test_a12f_e21_coverage_has_the_honest_columns_and_denominator(c, p03):
    env = c.env
    rep = p03(c.t4).report(module="M30", report="dofa_coverage")
    assert not rep.get("error"), rep
    assert {"in_force", "coded_group", "source"} <= set(rep["cols"])
    by = {r["model"]: r for r in rep["rows"]}
    approve_only = [r for r in rep["rows"] if r["source"] == "approve action only"]
    assert approve_only, "models outside the mixin must be in the denominator"
    gw = by["fix.payment.gateway"]
    assert gw["coded_group"] == "cd_entity_config.group_gateway_activation_approver"
    assert gw["authority"] == "coded_group", "a coded group is not 'none'"
    assert by["fix.rental.asset"]["in_force"] == "-"
    _rule(c, _ladder(c))
    rep = p03(c.t4).report(module="M30", report="dofa_coverage")
    assert {r["model"]: r for r in rep["rows"]}["fix.rental.asset"]["in_force"] == "yes"
    assert "working list" in " ".join(rep["notes"])
    assert env["fix.dofa.ladder"].search_count([("in_force", "=", True)]) >= 1


# ===================================================================== E23


def test_a12f_e23_ruled_ladder_is_not_deleted_or_rerun(c):
    env = c.env
    a = _ladder(c, bands=((1e9, "tier_5"),), basis="ruling")
    _rule(c, a)
    first = (a.ruled_by, a.countersigned_by, a.ruling_reference)
    assert refused(
        env,
        lambda: a.with_user(c.t4b).action_put_in_force(
            reference="OTHER-1", countersigned_by=c.t5b.id
        ),
    )
    assert refused(
        env,
        lambda: a.with_user(c.t4b).action_propose_ruling(
            reference="OTHER-1", countersigned_by=c.t5b.id
        ),
    )
    assert refused(env, lambda: a.action_put_in_force(reference="OTHER-1"))
    assert first == (a.ruled_by, a.countersigned_by, a.ruling_reference)
    b = _ladder(c, bands=((1e9, "tier_4"),), basis="req_text")
    _rule(c, b, reference="BOARD-MIN-2")
    a.invalidate_recordset()
    assert refused(
        env, lambda: a.with_user(c.t4b).unlink()
    ), "a superseded ruling keeps its history"
    draft = _ladder(c, basis="dofa_matrix")
    draft.with_user(c.t4).unlink()


def test_a12f_e23_amendment_is_a_new_version(c):
    env = c.env
    a = _ladder(c, bands=((1e9, "tier_5"),), basis="ruling")
    _rule(c, a)
    b = _ladder(c, bands=((1e9, "tier_4"),), basis="ruling", version=77)
    _flush(c)
    assert (a.version, b.version) == (1, 2), "the number is the server's, never typed"
    assert refused(env, lambda: b.with_user(c.t4).write({"version": 9}))
    _rule(c, b, reference="BOARD-MIN-2")
    a.invalidate_recordset()
    assert b.in_force and not a.in_force


def test_a12f_e23_ghost_target_is_refused_for_a_person(c):
    assert refused(c.env, lambda: _ladder(c, target="no.such.model"))


# ===================================================================== E24, E25


def test_a12f_e24_kill_switch_honours_scope(c):
    env = c.env
    Flags = env["fix.feature.flag"]
    flag = Flags.with_user(c.pa).create(
        {
            "key": "itsm.sla_auto_escalate",
            "name": "k",
            "scope": "branch",
            "branch_ids": [(4, c.branch.id)],
            "enabled": True,
        }
    )
    flag.with_user(c.pa).write({"enabled": False})
    assert Flags.is_disabled("itsm.sla_auto_escalate") is False
    assert Flags.is_disabled("itsm.sla_auto_escalate", branch=c.branch) is True
    flag.with_user(c.pa).write({"scope": "global"})
    assert Flags.is_disabled("itsm.sla_auto_escalate") is True


def test_a12f_e25_geofence_is_platform_admin_master_data(c):
    env = c.env
    zone = env["fix.zone"].create({"code": "A12FZ", "name": "Z"})
    vals = {
        "name": "f",
        "zone_id": zone.id,
        "geometry_json": '{"lat": 23.7, "lng": 90.4, "radius_m": 100}',
    }
    assert refused(env, lambda: env["fix.geofence"].with_user(c.clerk).create(vals))
    fence = env["fix.geofence"].with_user(c.pa).create(vals)
    assert refused(env, lambda: fence.with_user(c.clerk).write({"name": "g"}))
    assert fence.with_user(c.clerk).name == "f"


def test_a12f_e25_screens_state_what_is_not_built(c, p03):
    drift = p03(c.pa).report(module="M30", report="config_drift")
    assert any("not built" in n for n in drift["notes"])
    jobs = p03(c.pa).report(module="M30", report="job_success_rate")
    assert any("not built" in n for n in jobs["notes"])
    assessment = p03(c.clerk).report(module="M65", report="expansion_assessment")
    assert any("not built" in n for n in assessment["notes"])


# ===================================================================== operability walks


def test_a12f_walk_gateway_on_screen_payloads_all_roles(c, p03):
    env = c.env
    w = p03(c.pa).write(
        model="fix.payment.gateway",
        values={
            "provider": "WalkPay",
            "country_code": "BD",
            "currencies": "BDT",
            "credential_ref": "vault://fix/payments/walk",
        },
    )
    assert not perr(w), w
    gw = env["fix.payment.gateway"].browse(w["id"])
    action = lambda user, method, **kw: p03(user).action(  # noqa: E731
        model="fix.payment.gateway", ids=gw.ids, method=method, kwargs=kw or None
    )
    decide = lambda: p03(c.approver).action(  # noqa: E731
        model="fix.workflow.task",
        ids=gw.approval_request_id.task_ids.filtered(
            lambda t: t.state == "pending" and t.assigned_user_id == c.approver
        ).ids,
        method="action_approve",
        kwargs={"comment": "ok"},
    )
    assert not perr(action(c.pa, "action_request_approval", justification="launch"))
    _flush(c)
    assert not perr(decide())
    _flush(c)
    assert (gw.state, gw.mode) == ("active", "sandbox")
    assert not perr(action(c.pa, "action_request_approval", justification="go live"))
    _flush(c)
    assert not perr(decide())
    _flush(c)
    assert (gw.state, gw.mode) == ("active", "live")
    assert not perr(action(c.approver, "action_suspend", reason="outage"))
    _flush(c)
    assert gw.state == "suspended"
    assert not perr(action(c.pa, "action_request_approval", justification="back"))
    _flush(c)
    assert not perr(decide())
    _flush(c)
    assert (gw.state, gw.mode) == ("active", "live")


def test_a12f_walk_country_pack_on_screen_payloads_two_admins(c, p03):
    env = c.env
    w = p03(c.pa).write(
        model="fix.country.pack",
        values={"name": "BD Holidays", "code": "BD-HOL-A", "kind": "holidays", "version": "1"},
    )
    assert not perr(w), w
    pid = w["id"]
    line = p03(c.pa).write(
        model="fix.country.pack.line",
        values={
            "pack_id": pid,
            "code": "V",
            "name": "Victory Day",
            "name_bn": "বিজয় দিবস",
            "date_value": "2027-12-16",
        },
    )
    assert not perr(line), line
    pack = env["fix.country.pack"].browse(pid)
    for user, method, kw in (
        (c.pa, "action_validate", None),
        (c.pa2, "action_certify", {"note": "Gazette of 2 Jan 2027"}),
        (c.pa2, "action_activate", None),
        (c.pa2, "action_load", None),
        (c.pa2, "action_retire", None),
    ):
        r = p03(user).action(model="fix.country.pack", ids=[pid], method=method, kwargs=kw)
        assert not perr(r), (method, r)
        _flush(c)
    assert (
        pack.state == "retired"
        and pack.loaded_at
        and pack.line_ids.date_value == date(2027, 12, 16)
    )


def test_a12f_walk_all_reports_and_kpis_run(c, p03):
    from odoo.addons.cd_p03_portal.controllers.a12 import m30, m65

    for module, mod in (("M30", m30), ("M65", m65)):
        for rep in mod.REPORTS:
            out = p03(c.pa).report(module=module, report=rep)
            assert not out.get("error"), (module, rep, out)
    assert "dofa_awaiting_countersign" in m30.kpis(c.env(user=c.t5.id))
    assert m65.kpis(c.env(user=c.clerk.id))["entities"] >= 0


# ===================================================================== seed script


def _seed_module():
    path = Path(__file__).resolve().parents[4] / "db" / "seeds" / "a12_finish_m30_m65.py"
    spec = importlib.util.spec_from_file_location("a12f_m30_seed", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_a12f_seed_walks_the_sanctioned_path_and_flags_the_rest(c):
    """fix_dev's shape: bKash live with no approval on record, a planned release with
    no change, placeholder BIN/TIN, an uncapped marketing row."""
    env = c.env
    seed = _seed_module()
    for login, group in (
        (seed.GATEWAY_APPROVER_LOGIN, APPROVER),
        (seed.T4_LOGIN, T4),
        (seed.T5_LOGIN, T5),
    ):
        if not seed._user(env, login):
            _user(env, login, [group])
    approver = seed._user(env, seed.GATEWAY_APPROVER_LOGIN)
    approver.write({"group_ids": [(4, env.ref(APPROVER).id)], "active": True})
    rail = (
        env["fix.payment.gateway"]
        .sudo()
        .create(
            {
                "provider": "bKashA12F",
                "country_code": "BD",
                "credential_ref": "vault://fix/payments/b",
            }
        )
    )
    rail._guarded().write({"state": "active", "mode": "live"})
    release = _release(c, version="19.0.4-a12f")
    # the seed's rows may be absent on this database, so build the fix_dev shape
    entity = c.entity.sudo()
    entity.write({"bin_number": seed.PLACEHOLDER_BIN, "tin_number": seed.PLACEHOLDER_TIN})
    env["fix.notification.config"].sudo().search([("consent_class", "=", "marketing")]).unlink()
    env.cr.execute(
        """
        INSERT INTO fix_notification_config
            (consent_class, channel, send_window, frequency_cap,
             combined_cap_non_transactional, sms_route, stale_discard_hours, company_id, name)
        VALUES ('marketing', 'sms', '10:00-20:00', 0, 4, 'non-masking', 24, %s, 'marketing / sms')
        """,
        [env.company.id],
    )
    env["fix.feature.flag"].sudo().search([("key", "=", seed.FLAG_KEY)]).unlink()
    env["fix.dofa.ladder"].sudo().search(
        [("target_model", "=", "fix.loyalty.ledger"), ("ruling_state", "=", "proposed")]
    ).unlink()
    loyalty = (
        env["fix.dofa.ladder"]
        .sudo()
        .search([("target_model", "=", "fix.loyalty.ledger"), ("basis", "=", "req_text")], limit=1)
    )
    if not loyalty.in_force:
        loyalty.action_put_in_force(reference="SEED-TEST-1")

    out = seed.run(env)
    _flush(c)

    # the rail really went through the routed decision, as the seed users
    assert rail.state == "active" and rail.mode == "live" and rail.approval_state == "approved"
    assert any("bKashA12F" in line for line in out["gateways_reapproved"])
    events = (
        env["fix.security.audit"]
        .sudo()
        .search([("object_ref", "=", "fix.payment.gateway,%d" % rail.id)])
        .mapped("event")
    )
    assert {"payment.gateway_suspended", "payment.gateway_reactivated"} <= set(events)
    tasks = rail.approval_request_id.task_ids
    assert approver in tasks.mapped("assigned_user_id")
    assert "pending" not in tasks.mapped("state")
    # the packs are drafts, uncertified, created by the seed's second admin
    packs = env["fix.country.pack"].search([("code", "in", ("BD-DIV-DIST-2026", "BD-HOL-2026"))])
    assert (
        packs and not packs.filtered("certified_by_id") and set(packs.mapped("state")) == {"draft"}
    )
    # nothing invented: the release stays planned, the BIN and TIN stay, both are listed
    assert release.state == "planned" and not release.itsm_change_id
    assert entity.bin_number == seed.PLACEHOLDER_BIN and entity.tin_number == seed.PLACEHOLDER_TIN
    listed = " ".join(out["for_a_person"])
    assert "19.0.4-a12f" in listed and "placeholders" in listed
    assert "look like placeholders" in " ".join(str(b) for b in entity.message_ids.mapped("body"))
    # the marketing row is capped, and a real proposal is waiting on the Tier 5 seed user
    assert (
        env["fix.notification.config"].search([("consent_class", "=", "marketing")]).frequency_cap
        == 4
    )
    proposal = env["fix.dofa.ladder"].search(
        [("target_model", "=", "fix.loyalty.ledger"), ("ruling_state", "=", "proposed")]
    )
    assert proposal and proposal.countersigned_by.login == seed.T5_LOGIN and not proposal.in_force
    assert env["fix.feature.flag"].is_disabled(seed.FLAG_KEY) is False

    # idempotent: a second run walks nothing again and does not duplicate a note
    again = seed.run(env)
    assert not again["gateways_reapproved"] and not again["bd_packs_created_as_draft"]
    assert not again["notification_caps_set"] and not again["rulings_proposed"]
