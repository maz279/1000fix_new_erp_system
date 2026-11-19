# M37 capture audit, third pass (2026-11-19): the records and rules behind the
# pages whose "+ New" opened a form that could not hold the page's record,
# exercised as non-admin users on the live ORM (`odoo_env`, rolled back).
#
# - Service Definition (FR-CAT-013..019): scope, delivery modes and their
#   standard durations, warranty, consent; BRU-CAT-12 on an Active scope.
# - Repair Operations (BRU-CAT-06): the required skill profile.
# - rBOM per operation per model (FR-CAT-022) and the compatibility matrix
#   (FR-CAT-033, BRU-CAT-07).
# - Attribute sets per item class (FR-CAT-005) and the commercial tree
#   (FR-CAT-004, BRU-CAT-02).
# - Fault taxonomy (FR-CAT-042) and fault -> operation (FR-CAT-025).
# - Subscription plans (FR-CAT-038), refurb grades (FR-CAT-040), rental SKU
#   terms (FR-CAT-039), kit lines (FR-CAT-041), part MPN (FR-CAT-029).
import itertools
import uuid

import psycopg2
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "M37P3-%s" % uuid.uuid4().hex[:6]
_SEQ = itertools.count(1)
OFFICER = "cd_catalogue.group_catalogue_officer"
PUBLISHER = "cd_catalogue.group_catalogue_publisher"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@m37p3.test" % (TAG.lower(), tag, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
            }
        )
    )


@pytest.fixture
def ppl(odoo_env):
    class P:
        clerk = _user(odoo_env, "clerk")
        officer = _user(odoo_env, "officer", [OFFICER])
        publisher = _user(odoo_env, "pub", [PUBLISHER])

    return P


def _category(env, tree="commercial"):
    cat = env["product.category"].search([("tree_type", "=", tree)], limit=1)
    return cat or env["product.category"].create({"name": "%s %s" % (TAG, tree), "tree_type": tree})


def _competency(env):
    Competency = env["fix.competency"].sudo()
    return Competency.search([], limit=1) or Competency.create(
        {"code": "M37P3", "name": "M37 pass-3 competency"}
    )


def _item(env, user, item_type="service", **extra):
    n = next(_SEQ)
    tmpl = env["product.template"].create(
        {
            "name": "%s item %d" % (TAG, n),
            "default_code": "%s-%d" % (TAG, n),
            "name_bn": "পরীক্ষা %d" % n,
        }
    )
    vals = {
        "product_tmpl_id": tmpl.id,
        "item_type": item_type,
        "category_id": _category(env).id,
        "vat_class": "standard_15",
        "revenue_recognition": "on_completion",
    }
    if item_type == "labour":
        vals.update(
            {
                "repair_level": "l1",
                "standard_labour_time": 1.0,
                "required_competency_id": _competency(env).id,
            }
        )
    if item_type in ("service", "inspection", "labour"):
        vals.update(
            {
                "scope_of_work": "Replace the part and test.",
                "mode_duration_ids": [(0, 0, {"delivery_mode": "walk_in", "standard_minutes": 40})],
            }
        )
    vals.update(extra)
    return env["fix.catalogue.item"].with_user(user).create(vals)


def _model(env, name="M"):
    brand = env["fix.brand"].search([], limit=1)
    return env["fix.device.model"].create(
        {"name": "%s %s %d" % (TAG, name, next(_SEQ)), "brand_id": brand.id}
    )


# --- FR-CAT-013/014/016: the service definition ---------------------------------


def test_service_needs_scope_and_a_delivery_mode_before_review(odoo_env, ppl):
    bare = _item(odoo_env, ppl.officer, scope_of_work=False, mode_duration_ids=[])
    with pytest.raises(UserError, match="scope of work") as err, odoo_env.cr.savepoint():
        bare.with_user(ppl.officer).action_submit()
    assert "delivery mode" in str(err.value)
    full = _item(odoo_env, ppl.officer)
    full.with_user(ppl.officer).action_submit()
    assert full.state == "in_review"
    # a part carries neither
    part = _item(odoo_env, ppl.officer, item_type="part")
    part.with_user(ppl.officer).action_submit()
    assert part.state == "in_review"


def test_delivery_mode_lines_are_positive_unique_and_officer_only(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    Mode = odoo_env["fix.service.mode.duration"]
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        Mode.with_user(ppl.officer).create(
            {"item_id": item.id, "delivery_mode": "on_site", "standard_minutes": 0}
        )
    with pytest.raises((ValidationError, psycopg2.IntegrityError)), odoo_env.cr.savepoint():
        Mode.with_user(ppl.officer).create(
            {"item_id": item.id, "delivery_mode": "walk_in", "standard_minutes": 30}
        )
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        Mode.with_user(ppl.clerk).create(
            {"item_id": item.id, "delivery_mode": "remote", "standard_minutes": 30}
        )
    Mode.with_user(ppl.officer).create(
        {"item_id": item.id, "delivery_mode": "on_site", "standard_minutes": 90}
    )
    assert set(item.mode_duration_ids.mapped("delivery_mode")) == {"walk_in", "on_site"}


def test_active_scope_changes_only_by_revise(odoo_env, ppl):
    """BRU-CAT-12: a set scope on an Active service is what was approved; a
    blank one (a migrated item) may be completed."""
    item = _item(odoo_env, ppl.officer, inclusions=False)
    item.sudo()._guarded().write({"state": "approved"})
    officer = item.with_user(ppl.officer)
    officer.write({"inclusions": "Screen protector fitted."})  # blank -> completed
    officer.write({"scope_of_work": item.scope_of_work})  # unchanged resend passes
    with pytest.raises(UserError, match="BRU-CAT-12"), odoo_env.cr.savepoint():
        officer.write({"scope_of_work": "Something else"})
    assert {"scope_of_work", "inclusions"} <= item._fix_form_locked_fields()


def test_service_definition_fields_are_captured(odoo_env, ppl):
    sla = odoo_env["fix.sla.policy"].search([], limit=1)
    item = _item(
        odoo_env,
        ppl.officer,
        exclusions="Liquid damage",
        prerequisites="Customer brings the charger",
        deliverables="Test report",
        repair_warranty_days=90,
        requires_customer_consent=True,
        requires_data_declaration=True,
        tooling_required="Hot-air station",
        workstation_class="esd_bench",
        default_sla_policy_id=sla.id or False,
    )
    assert item.repair_warranty_days == 90 and item.requires_customer_consent
    assert item.workstation_class == "esd_bench"


# --- BRU-CAT-06: a repair operation needs its skill profile -------------------------


def test_repair_operation_needs_a_skill_profile(odoo_env, ppl):
    op = _item(odoo_env, ppl.officer, item_type="labour", required_competency_id=False)
    with pytest.raises(UserError, match="skill profile"), odoo_env.cr.savepoint():
        op.with_user(ppl.officer).action_submit()
    op.with_user(ppl.officer).write({"required_competency_id": _competency(odoo_env).id})
    op.with_user(ppl.officer).action_submit()
    assert op.state == "in_review"


# --- FR-CAT-022 / 033, BRU-CAT-07: rBOM per model and the compatibility matrix ------


def test_rbom_is_per_model_with_criticality_and_alternates(odoo_env, ppl):
    op = _item(odoo_env, ppl.officer, item_type="labour")
    part = _item(odoo_env, ppl.officer, item_type="part")
    m1, m2 = _model(odoo_env, "A"), _model(odoo_env, "B")
    Line = odoo_env["fix.rbom.line"].with_user(ppl.officer)
    base = {"item_id": op.id, "component_item_id": part.id, "quantity": 1}
    Line.create(dict(base, device_model_id=m1.id, criticality="critical", alternate_group="SCR"))
    Line.create(dict(base, device_model_id=m2.id))
    Line.create(dict(base))  # the general line
    with pytest.raises(ValidationError, match="every model"), odoo_env.cr.savepoint():
        Line.create(dict(base))  # a second general line: the NULL twin
    assert len(odoo_env["fix.rbom.line"].search([("item_id", "=", op.id)])) == 3


def test_incompatible_part_is_refused_on_that_models_rbom(odoo_env, ppl):
    op = _item(odoo_env, ppl.officer, item_type="labour")
    part = _item(odoo_env, ppl.officer, item_type="part")
    model = _model(odoo_env)
    Compat = odoo_env["fix.model.compatibility"]
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        Compat.with_user(ppl.clerk).create({"device_model_id": model.id, "item_id": part.id})
    with pytest.raises(ValidationError, match="FR-CAT-033"), odoo_env.cr.savepoint():
        Compat.with_user(ppl.officer).create(
            {"device_model_id": model.id, "item_id": part.id, "compatible": False}
        )
    row = Compat.with_user(ppl.officer).create(
        {
            "device_model_id": model.id,
            "item_id": part.id,
            "compatible": False,
            "note": "Different connector revision",
        }
    )
    assert "does NOT fit" in row.display_label
    with pytest.raises(ValidationError, match="BRU-CAT-07"), odoo_env.cr.savepoint():
        odoo_env["fix.rbom.line"].with_user(ppl.officer).create(
            {"item_id": op.id, "component_item_id": part.id, "device_model_id": model.id}
        )
    with pytest.raises(ValidationError, match="already has"), odoo_env.cr.savepoint():
        Compat.with_user(ppl.officer).create({"device_model_id": model.id, "item_id": part.id})


def test_part_on_an_rbom_cannot_then_be_declared_incompatible(odoo_env, ppl):
    op = _item(odoo_env, ppl.officer, item_type="labour")
    part = _item(odoo_env, ppl.officer, item_type="part")
    model = _model(odoo_env)
    odoo_env["fix.rbom.line"].with_user(ppl.officer).create(
        {"item_id": op.id, "component_item_id": part.id, "device_model_id": model.id}
    )
    with pytest.raises(ValidationError, match="take it off"), odoo_env.cr.savepoint():
        odoo_env["fix.model.compatibility"].with_user(ppl.officer).create(
            {"device_model_id": model.id, "item_id": part.id, "compatible": False, "note": "x"}
        )


def test_rbom_line_model_must_be_one_the_operation_covers(odoo_env, ppl):
    covered, other = _model(odoo_env, "C"), _model(odoo_env, "D")
    op = _item(odoo_env, ppl.officer, item_type="labour", device_model_ids=[(6, 0, covered.ids)])
    part = _item(odoo_env, ppl.officer, item_type="part")
    Line = odoo_env["fix.rbom.line"].with_user(ppl.officer)
    with pytest.raises(ValidationError, match="BRU-CAT-07"), odoo_env.cr.savepoint():
        Line.create({"item_id": op.id, "component_item_id": part.id, "device_model_id": other.id})
    Line.create({"item_id": op.id, "component_item_id": part.id, "device_model_id": covered.id})


# --- FR-CAT-004/005: commercial tree and attribute sets ----------------------------


def test_presentation_category_is_not_a_commercial_position(odoo_env, ppl):
    root = odoo_env["product.category"].create(
        {"name": "%s web" % TAG, "tree_type": "presentation", "code": "%s-WEB" % TAG}
    )
    with pytest.raises(ValidationError, match="parent's tree"), odoo_env.cr.savepoint():
        odoo_env["product.category"].create(
            {"name": "%s child" % TAG, "parent_id": root.id, "tree_type": "commercial"}
        )
    item = _item(odoo_env, ppl.officer, item_type="part", category_id=root.id)
    with pytest.raises(UserError, match="commercial tree"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).action_submit()


def test_attribute_set_blocks_review_and_flags_channel_publication(odoo_env, ppl):
    Attr = odoo_env["product.attribute"]
    colour = Attr.create({"name": "%s colour" % TAG, "create_variant": "no_variant"})
    storage = Attr.create({"name": "%s storage" % TAG, "create_variant": "no_variant"})
    Sets = odoo_env["fix.catalogue.attribute.set"]
    Sets.with_user(ppl.officer).search([("item_type", "=", "accessory")]).sudo().write(
        {"active": False}
    )
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        Sets.with_user(ppl.clerk).create({"name": "x", "item_type": "accessory"})
    Sets.with_user(ppl.officer).create(
        {
            "name": "%s accessories" % TAG,
            "item_type": "accessory",
            "line_ids": [
                (0, 0, {"attribute_id": colour.id, "channel": "all"}),
                (0, 0, {"attribute_id": storage.id, "channel": "portal"}),
            ],
        }
    )
    with pytest.raises(ValidationError, match="already has"), odoo_env.cr.savepoint():
        Sets.with_user(ppl.officer).create({"name": "dup", "item_type": "accessory"})
    item = _item(odoo_env, ppl.officer, item_type="accessory")
    with pytest.raises(UserError, match="FR-CAT-005"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).action_submit()
    value = odoo_env["product.attribute.value"].create({"name": "Black", "attribute_id": colour.id})
    item.product_tmpl_id.sudo().write(
        {
            "attribute_line_ids": [
                (0, 0, {"attribute_id": colour.id, "value_ids": [(6, 0, value.ids)]})
            ]
        }
    )
    item.with_user(ppl.officer).action_submit()
    Pub = odoo_env["fix.catalogue.publication"]
    assert item in Pub._incomplete_for(item, "portal")  # storage is required on the portal
    assert item not in Pub._incomplete_for(item, "pos")


# --- FR-CAT-042 / 025: the fault taxonomy -------------------------------------------


def test_fault_taxonomy_symptom_root_cause_and_operations(odoo_env, ppl):
    fault = odoo_env["fix.fault.code"].create(
        {"code": "%s-F" % TAG, "name": "No display", "name_bn": "ডিসপ্লে নেই", "category": "display"}
    )
    symptom = odoo_env["fix.fault.symptom"].create(
        {
            "code": "%s-S" % TAG,
            "name": "Screen stays black",
            "name_bn": "স্ক্রিন কালো",
            "fault_code_ids": [(6, 0, fault.ids)],
        }
    )
    assert symptom in fault.symptom_ids  # one relation, both directions
    fault.write(
        {
            "root_cause_ids": [
                (0, 0, {"code": "LIQ", "name": "Liquid ingress", "is_customer_induced": True})
            ]
        }
    )
    op = _item(odoo_env, ppl.officer, item_type="labour")
    fault.write({"operation_ids": [(4, op.id)]})
    assert fault in op.fault_code_ids
    part = _item(odoo_env, ppl.officer, item_type="part")
    with pytest.raises(ValidationError, match="not a repair operation"), odoo_env.cr.savepoint():
        fault.write({"operation_ids": [(4, part.id)]})


# --- FR-CAT-038 / 039 / 040 / 041 / 029 ----------------------------------------------


def test_subscription_plan_definition(odoo_env, ppl):
    plan_item = _item(odoo_env, ppl.officer, item_type="subscription")
    Plan = odoo_env["fix.subscription.plan.def"]
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        Plan.with_user(ppl.clerk).create({"item_id": plan_item.id, "billing_frequency": "monthly"})
    with pytest.raises(ValidationError, match="at least one month"), odoo_env.cr.savepoint():
        Plan.with_user(ppl.officer).create(
            {"item_id": plan_item.id, "billing_frequency": "monthly", "commitment_months": 0}
        )
    plan = Plan.with_user(ppl.officer).create(
        {
            "item_id": plan_item.id,
            "billing_frequency": "monthly",
            "commitment_months": 12,
            "included_quantity": 4,
        }
    )
    assert plan.name == plan_item.name
    with pytest.raises(ValidationError, match="already has"), odoo_env.cr.savepoint():
        Plan.with_user(ppl.officer).create({"item_id": plan_item.id, "billing_frequency": "yearly"})
    with pytest.raises(UserError, match="never deleted"), odoo_env.cr.savepoint():
        plan.with_user(ppl.officer).unlink()


def test_refurb_grade_criteria_are_defined_but_its_code_and_multiplier_stay_fixed(odoo_env, ppl):
    grade = odoo_env["fix.refurb.grade"].search([], limit=1)
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        grade.with_user(ppl.clerk).write({"cosmetic_criteria": "x"})
    grade.with_user(ppl.officer).write(
        {
            "cosmetic_criteria": "No scratch visible at 30 cm",
            "functional_criteria": "Battery health >= 85%",
            "sell_marketplace": False,
            "code": grade.code,  # a full-form resend
            "currency_id": grade.currency_id.id,
        }
    )
    assert grade.cosmetic_criteria and not grade.sell_marketplace
    with pytest.raises(UserError, match="fixed"), odoo_env.cr.savepoint():
        grade.with_user(ppl.officer).write({"price_multiplier": 5.0})


def test_rental_sku_hire_period(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, item_type="rental")
    Sku = odoo_env["fix.rental.sku"].with_user(ppl.officer)
    with pytest.raises(ValidationError, match="minimum hire"), odoo_env.cr.savepoint():
        Sku.create({"catalogue_item_id": item.id, "min_hire_days": 10, "max_rental_days": 5})
    sku = Sku.create(
        {
            "catalogue_item_id": item.id,
            "min_hire_days": 3,
            "deposit_basis": "pct_value",
            "return_criteria": "No cracks; all accessories returned",
        }
    )
    assert sku.deposit_basis == "pct_value"


def test_kit_lines_are_required_or_optional_with_substitution(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, item_type="bundle")
    kit = (
        odoo_env["fix.service.kit"]
        .with_user(ppl.officer)
        .create(
            {
                "name": "%s kit" % TAG,
                "catalogue_item_id": item.id,
                "explode_at": "quotation",
                "component_ids": [
                    (
                        0,
                        0,
                        {
                            "component_type": "part",
                            "quantity": 1,
                            "notes": "Screen guard",
                            "is_optional": True,
                            "substitution": "crossref",
                        },
                    )
                ],
            }
        )
    )
    assert kit.explode_at == "quotation" and kit.component_ids.is_optional


def test_officer_records_the_part_number_on_the_product(odoo_env, ppl):
    part = _item(odoo_env, ppl.officer, item_type="part", manufacturer_part_number="GH82-1")
    assert part.product_tmpl_id.manufacturer_part_number == "GH82-1"
    part.with_user(ppl.officer).write(
        {"manufacturer_part_number": "GH82-2", "oem_reference": "SVC-9"}
    )
    assert (
        part.product_tmpl_id.manufacturer_part_number == "GH82-2" and part.oem_reference == "SVC-9"
    )
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        part.with_user(ppl.clerk).write({"manufacturer_part_number": "X"})


def test_protection_product_carries_its_cover(odoo_env):
    fields_ = odoo_env["fix.warranty.product"]._fields
    assert {"coverage_scope", "exclusions", "duration_months", "claim_limit"} <= set(fields_)
