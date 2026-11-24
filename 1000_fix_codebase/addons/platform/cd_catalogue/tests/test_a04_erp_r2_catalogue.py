# A04 ERP audit round 2 (21 Nov 2026), stream R2-3: M37-F5/F7/F11 on the
# live ORM (`odoo_env`, rolled back), as non-superusers where a role decides.
import itertools
import uuid

import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "R23C%s" % uuid.uuid4().hex[:5].upper()
_SEQ = itertools.count(1)


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@r23c.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


def _item(env, item_type="part", code=True, state="approved", **vals):
    n = next(_SEQ)
    tvals = {"name": "%s item %d" % (TAG, n)}
    if code:
        tvals["default_code"] = "%s-%d" % (TAG, n)
    tmpl = env["product.template"].create(tvals)
    item = env["fix.catalogue.item"].create(
        dict({"product_tmpl_id": tmpl.id, "item_type": item_type}, **vals)
    )
    item._guarded().write({"state": state})
    return item


# ---- FR-CAT-007: numbering ---------------------------------------------------------


def test_items_take_the_next_code_of_their_type_mask_and_never_reuse_one(odoo_env):
    officer = _user(odoo_env, "off", ["cd_catalogue.group_catalogue_officer"])
    publisher = _user(odoo_env, "pub", ["cd_catalogue.group_catalogue_publisher"])
    Numbering = odoo_env["fix.catalogue.numbering"]
    with pytest.raises(AccessError):
        Numbering.with_user(officer).create({"item_type": "accessory", "prefix": TAG + "A-"})
    rule = Numbering.with_user(publisher).create(
        {"item_type": "accessory", "prefix": TAG + "A-", "padding": 4}
    )
    assert rule.sequence_id.implementation == "no_gap"
    assert rule.next_code == TAG + "A-0001"
    first = _item(odoo_env, "accessory", code=False, state="draft")
    second = _item(odoo_env, "accessory", code=False, state="draft")
    assert first.product_tmpl_id.default_code == TAG + "A-0001"
    assert second.product_tmpl_id.default_code == TAG + "A-0002"
    # a typed code is kept; renumbering a draft keeps the old code as an alias
    legacy = _item(odoo_env, "accessory", state="draft")
    old = legacy.product_tmpl_id.default_code
    legacy.with_user(officer).action_assign_code()
    assert legacy.product_tmpl_id.default_code == TAG + "A-0003"
    assert legacy.legacy_codes == old
    assert odoo_env["fix.catalogue.item"].search([("legacy_codes", "ilike", old)]) == legacy
    assert legacy.id in [r[0] for r in odoo_env["fix.catalogue.item"].name_search(old)]
    # the alias is never issued again: the sequence skips a taken code
    odoo_env["product.template"].create({"name": "squatter", "default_code": TAG + "A-0004"})
    fourth = _item(odoo_env, "accessory", code=False, state="draft")
    assert fourth.product_tmpl_id.default_code == TAG + "A-0005"
    clash = _item(odoo_env, "part", state="draft")
    clash.product_tmpl_id.write({"default_code": old})
    assert any("legacy code" in p for p in clash._completeness_problems())
    with pytest.raises(UserError, match="is not renumbered"):
        _item(odoo_env, "accessory").with_user(officer).action_assign_code()
    with pytest.raises(UserError, match="never deleted"):
        rule.unlink()


# ---- FR-CAT-015: who may perform it -----------------------------------------------


def test_technician_requirements_and_the_skill_band_check(odoo_env):
    brand = odoo_env["fix.brand"].create({"name": "%s brand" % TAG, "code": "C%s" % TAG[-5:]})
    item = _item(
        odoo_env,
        "labour",
        repair_level="l2",
        required_skill_band="senior",
        requires_brand_certification=True,
        brand_id=brand.id,
    )
    req = item._fix_technician_requirements()
    assert (req["repair_level"], req["skill_band"], req["brand_id"]) == ("l2", "senior", brand.id)
    assert req["brand_certification"] is True
    employee = odoo_env["hr.employee"].create({"name": "%s tech" % TAG})
    ok, why = item._fix_technician_qualified(employee, skill_band="standard")
    assert not ok and any("skill band" in w for w in why)
    if "fix.certification" in odoo_env:
        assert any("certification of" in w for w in why)
    plain = _item(odoo_env, "labour", repair_level="l1")
    assert plain._fix_technician_qualified(employee) == (True, [])


# ---- FR-CAT-018 / FR-CAT-031 ----------------------------------------------------------


def test_repair_warranty_helper_and_live_successor_offer(odoo_env):
    service = _item(odoo_env, "service", repair_warranty_days=180)
    assert service._fix_repair_warranty_days(90) == 180
    assert _item(odoo_env, "service", repair_warranty_days=30)._fix_repair_warranty_days(90) == 90
    a, b, c = _item(odoo_env), _item(odoo_env), _item(odoo_env)
    a._guarded().write({"state": "deprecated", "successor_id": b.id})
    b._guarded().write({"state": "deprecated", "successor_id": c.id})
    assert a._fix_sale_substitute("service") == c
    with pytest.raises(UserError, match="offer its successor %s instead" % c.name):
        a._fix_assert_sellable("service")
    assert not c._fix_sale_substitute("service")  # c still sells


# ---- AUT-PRC-09 producer: the re-baseline event ----------------------------------------


def test_an_applied_rebaseline_publishes_its_event_and_holds_its_price_effect(odoo_env):
    op = _item(odoo_env, "labour", repair_level="l1", standard_labour_time=1.0)
    base = odoo_env["fix.srt.baseline"].create(
        {"item_id": op.id, "repair_level": "l1", "minutes": 45.0, "reason": "study"}
    )
    base.action_propose()
    base.action_approve()
    assert base.price_effect == "held"
    row = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "catalogue.srt_rebaselined"), ("aggregate_id", "=", base.id)]
    )
    payload = row._relay_event_dict()["payload"]
    assert (payload["old_minutes"], payload["new_minutes"]) == (60.0, 45.0)
    fresh = _item(odoo_env, "labour", repair_level="l1")
    first = odoo_env["fix.srt.baseline"].create(
        {"item_id": fresh.id, "repair_level": "l1", "minutes": 30.0, "reason": "first"}
    )
    first.action_propose()
    first.action_approve()
    assert first.price_effect == "none"  # a first baseline replaces no priced time
    clerk = _user(odoo_env, "clerk")
    with pytest.raises(REFUSED):
        base.with_user(clerk).write({"price_effect": "released"})
