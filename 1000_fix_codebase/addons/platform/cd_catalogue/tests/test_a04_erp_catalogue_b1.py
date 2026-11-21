# A04 ERP audit (20 Nov 2026), stream B1: M37 catalogue fixes on the live ORM
# (`odoo_env`, rolled back). fix_real: 16,178 items, all Active, none with a
# VAT class; rBOMs and kits never exploded; no channel read publication.
import itertools
import uuid

import pytest
from odoo import Command
from odoo.exceptions import UserError, ValidationError

TAG = "B1CAT%s" % uuid.uuid4().hex[:5].upper()


def _item(env, name, item_type="part", **vals):
    tmpl = env["product.template"].create(
        {"name": "%s %s" % (TAG, name), "default_code": "%s-%s" % (TAG, name)}
    )
    item = env["fix.catalogue.item"].create(
        dict({"product_tmpl_id": tmpl.id, "item_type": item_type}, **vals)
    )
    item._guarded().write({"state": "approved"})
    return item


def _clerk(env):
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s clerk" % TAG,
                "login": "%s.clerk@b1.test" % TAG.lower(),
                "group_ids": [(6, 0, [env.ref("base.group_user").id])],
            }
        )
    )


def test_customer_channels_refuse_an_item_with_no_vat_class(odoo_env):
    item = _item(odoo_env, "NOVAT")
    clerk = _clerk(odoo_env)
    variant = item.product_tmpl_id.product_variant_id.with_user(clerk)
    for channel in ("storefront", "marketplace"):
        with pytest.raises(UserError, match="no VAT class"):
            item.with_user(clerk)._fix_assert_sellable(channel)
    # a branch estimate is not a customer channel (M01 keeps working)
    assert item.with_user(clerk)._fix_assert_sellable("estimate")
    assert variant._fix_check_sale(channel="estimate") is True


def test_storefront_sells_only_published_items(odoo_env):
    item = _item(odoo_env, "UNPUB", vat_class="standard_15")
    with pytest.raises(UserError, match="not published"):
        item._fix_assert_sellable("storefront")
    assert item._fix_assert_sellable("marketplace")
    item._guarded().write({"state": "published", "is_published": True, "name_bn": "পণ্য"})
    assert item._fix_assert_sellable("storefront")


def test_discontinued_item_still_serves_contract_covered_devices(odoo_env):
    """BRU-CAT-10: refused for new sale, kept for contract service; Obsolete ends both."""
    item = _item(odoo_env, "DISC", vat_class="standard_15")
    item._guarded().write({"state": "deprecated"})
    with pytest.raises(UserError, match="no longer sold"):
        item._fix_assert_sellable("service")
    assert item._fix_assert_sellable("service_contract")
    item._guarded().write({"state": "obsolete"})
    with pytest.raises(UserError, match="no longer sold"):
        item._fix_assert_sellable("service_contract")


def test_the_exported_item_sale_check_runs_the_product_check(odoo_env):
    item = _item(odoo_env, "EXP")
    with pytest.raises(UserError, match="no VAT class"):
        item._fix_check_sale(channel="marketplace")
    assert item._fix_check_sale(channel="estimate")


def test_supersession_resolves_to_the_live_successor(odoo_env):
    a, b, c = _item(odoo_env, "A"), _item(odoo_env, "B"), _item(odoo_env, "C")
    a._guarded().write({"state": "deprecated", "successor_id": b.id})
    b._guarded().write({"state": "obsolete", "successor_id": c.id})
    assert a._fix_live_successor() == c
    c._guarded().write({"state": "deprecated", "successor_id": a.id})  # a cycle
    assert not a._fix_live_successor()


def test_rbom_and_kit_explode_into_lines_and_part_demand(odoo_env):
    """FR-CAT-028/041: the rBOM and the kit never exploded."""
    env = odoo_env
    service = _item(env, "SVC", item_type="service")
    screen = _item(env, "SCREEN")
    glue = _item(env, "GLUE")
    alt1, alt2 = _item(env, "ALT1"), _item(env, "ALT2")
    sub = _item(env, "SUB", item_type="service")
    screw = _item(env, "SCREW")
    Line = env["fix.rbom.line"]
    Line.create({"item_id": service.id, "component_item_id": screen.id, "quantity": 1.0})
    Line.create(
        {
            "item_id": service.id,
            "component_item_id": alt1.id,
            "alternate_group": "BAT",
            "sequence": 20,
        }
    )
    Line.create(
        {
            "item_id": service.id,
            "component_item_id": alt2.id,
            "alternate_group": "BAT",
            "sequence": 30,
        }
    )
    Line.create(
        {"item_id": service.id, "component_item_id": sub.id, "quantity": 2.0, "sequence": 40}
    )
    Line.create({"item_id": sub.id, "component_item_id": screw.id, "quantity": 4.0})
    env["fix.service.kit"].create(
        {
            "name": "%s kit" % TAG,
            "catalogue_item_id": service.id,
            "component_ids": [
                Command.create(
                    {"product_id": glue.product_tmpl_id.product_variant_id.id, "quantity": 0.5}
                ),
                Command.create({"notes": "Optional cleaning", "is_optional": True}),
            ],
        }
    )
    rows = service._fix_explode(qty=2.0)
    got = {(r["item"].name, r["qty"]) for r in rows}
    assert got == {
        (screen.name, 2.0),
        (alt1.name, 2.0),  # one of the alternate group, not both
        (screw.name, 16.0),  # 2 services x 2 sub-operations x 4 screws
        (glue.name, 1.0),
    }
    demand = service._fix_part_demand(qty=1.0)
    assert demand[screw.product_tmpl_id.product_variant_id] == 8.0
    assert alt2.product_tmpl_id.product_variant_id not in demand


def test_rbom_and_charge_code_carry_a_company(odoo_env):
    env = odoo_env
    service = _item(env, "SVC2", item_type="service")
    part = _item(env, "P2")
    line = env["fix.rbom.line"].create({"item_id": service.id, "component_item_id": part.id})
    assert line.company_id == service.company_id
    assert env.ref("cd_catalogue.rule_fix_rbom_line_company")
    assert env.ref("cd_catalogue.rule_fix_charge_code_company")
    assert "company_id" in env["fix.charge.code"]._fields


def test_explosion_depth_is_bounded(odoo_env):
    env = odoo_env
    items = [_item(env, "D%d" % i, item_type="service") for i in range(11)]
    for parent, child in itertools.pairwise(items):
        env["fix.rbom.line"].create({"item_id": parent.id, "component_item_id": child.id})
    with pytest.raises(ValidationError, match="explodes deeper"):
        items[0]._fix_explode()


def test_explosion_refuses_a_part_that_does_not_fit_the_device(odoo_env):
    """M37-F11: compatibility was checked only when an rBOM line was saved."""
    env = odoo_env
    service = _item(env, "SVC3", item_type="service")
    part = _item(env, "P3")
    env["fix.rbom.line"].create({"item_id": service.id, "component_item_id": part.id})
    brand = env["fix.brand"].create({"name": "%s br" % TAG, "code": TAG[-5:]})
    model = env["fix.device.model"].create({"name": "%s phone" % TAG, "brand_id": brand.id})
    assert service._fix_explode(device_model=model)
    env["fix.model.compatibility"].create(
        {"item_id": part.id, "device_model_id": model.id, "compatible": False, "note": "wrong size"}
    )
    with pytest.raises(ValidationError, match="does not fit"):
        service._fix_explode(device_model=model)
