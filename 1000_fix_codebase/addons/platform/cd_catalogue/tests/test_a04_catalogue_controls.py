# A04 C2-C13 (2026-11-04): M37 catalogue controls, exercised as non-admin
# users on the live ORM (`odoo_env`, rolled back).
#
# Each test replays an attack from working/A04_evidence/probes/m11_m36_m37/
# probe_m37.py with the actor the control is about, and also shows the
# legitimate path works: a Catalogue Officer authors, a Catalogue Publisher
# who is not the author approves from the M63 inbox, an Active item sells.
import itertools
import uuid

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "A4C37-%s" % uuid.uuid4().hex[:6]
_SEQ = itertools.count(1)
OFFICER = "cd_catalogue.group_catalogue_officer"
PUBLISHER = "cd_catalogue.group_catalogue_publisher"
SALE_GATE = "cd_catalogue.sale_requires_active_item"


def _user(env, tag, groups=()):
    n = next(_SEQ)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "%s %s %d" % (TAG, tag, n),
                "login": "%s.%s.%d@a04.test" % (TAG.lower(), tag, n),
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
        officer2 = _user(odoo_env, "officer2", [OFFICER])
        publisher = _user(odoo_env, "pub", [PUBLISHER])
        publisher2 = _user(odoo_env, "pub2", [PUBLISHER])

    return P


def _category(env):
    return env["product.category"].search([], limit=1) or env["product.category"].create(
        {"name": "A04 Category"}
    )


def _service_definition(env, item_type):
    """M37 capture pass 3: what a service, inspection or labour item needs
    before it leaves Draft (FR-CAT-013/014/016, BRU-CAT-06)."""
    vals = {}
    if item_type in ("service", "inspection", "labour"):
        vals["scope_of_work"] = "Diagnose and repair as described."
        vals["mode_duration_ids"] = [(0, 0, {"delivery_mode": "walk_in", "standard_minutes": 45})]
    if item_type == "labour" and "required_competency_id" in env["fix.catalogue.item"]._fields:
        Competency = env["fix.competency"].sudo()
        vals["required_competency_id"] = (
            Competency.search([], limit=1)
            or Competency.create({"code": "M37-TST", "name": "M37 test competency"})
        ).id
    return vals


def _item(env, user, item_type="service", name_bn="পরীক্ষা সেবা", code=None, category=True):
    n = next(_SEQ)
    tmpl = env["product.template"].create(
        {
            "name": "%s item %d" % (TAG, n),
            "list_price": 800.0,
            "default_code": code or "%s-%d" % (TAG, n),
            "name_bn": name_bn or False,
        }
    )
    # BRU-CAT-02 (M37 capture audit 2026-11-14): an item is submitted only
    # with its VAT class and revenue-recognition class.
    vals = {
        "product_tmpl_id": tmpl.id,
        "item_type": item_type,
        "vat_class": "standard_15",
        "revenue_recognition": "on_completion",
    }
    if item_type == "labour":
        vals.update({"repair_level": "l1", "standard_labour_time": 1.0})
    vals.update(_service_definition(env, item_type))
    if category:
        vals["category_id"] = _category(env).id
    return env["fix.catalogue.item"].with_user(user).create(vals)


def _activate(env, item, publisher):
    item.with_user(item.create_uid).action_submit()
    approve_via_inbox(item, publisher, requester=item.create_uid)
    return item


# --- roles: plain users read, officers author ---------------------------------


def test_plain_user_cannot_create_or_delete_an_item(odoo_env, ppl):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        _item(odoo_env, ppl.clerk)
    item = _item(odoo_env, ppl.officer)
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        item.with_user(ppl.clerk).write({"description_bn": "x"})
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        item.with_user(ppl.clerk).unlink()


# --- ci_01 / ci_02 / ci_03: lifecycle fields are not typed ----------------------


@pytest.mark.parametrize(
    "vals",
    [{"state": "approved"}, {"state": "published", "is_published": True}, {"is_published": True}],
)
def test_officer_cannot_type_the_lifecycle(odoo_env, ppl, vals):
    item = _item(odoo_env, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).write(vals)


def test_author_cannot_stamp_approved_by(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).write({"approved_by": ppl.officer.id})


# --- ci_06: the lifecycle, approver != author, through M63 --------------------


def test_submit_routes_to_a_publisher_who_is_not_the_author(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    item.with_user(ppl.officer).action_submit()
    assert item.state == "in_review" and item.approval_state == "pending"
    assert item.submitted_by == ppl.officer
    assignees = item.approval_request_id.task_ids.mapped("assigned_user_id")
    assert ppl.officer not in assignees and ppl.publisher in assignees
    # the approve method does not run outside the inbox, even for a publisher
    with pytest.raises(UserError, match="approver's inbox"), odoo_env.cr.savepoint():
        item.with_user(ppl.publisher).action_approve()
    inbox_task(item, ppl.publisher).with_user(ppl.publisher).action_approve()
    assert item.state == "approved" and item.approved_by == ppl.publisher
    assert item.is_sellable
    events = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "catalogue.item_activated"), ("aggregate_id", "=", item.id)]
    )
    assert len(events) == 1


def test_publisher_who_authored_is_not_routed_the_item(odoo_env, ppl):
    item = _item(odoo_env, ppl.publisher)
    item.with_user(ppl.publisher).action_submit()
    assert ppl.publisher not in item.approval_request_id.task_ids.mapped("assigned_user_id")


def test_submission_needs_bengali_category_and_a_unique_code(odoo_env, ppl):
    bare = _item(odoo_env, ppl.officer, name_bn=False, category=False)
    with pytest.raises(UserError, match="Bengali name") as info, odoo_env.cr.savepoint():
        bare.with_user(ppl.officer).action_submit()
    assert "product category" in str(info.value)
    first = _item(odoo_env, ppl.officer, code="%s-DUP" % TAG)
    second = _item(odoo_env, ppl.officer2, code=first.product_tmpl_id.default_code.lower())
    with pytest.raises(UserError, match="BRU-CAT-13"), odoo_env.cr.savepoint():
        second.with_user(ppl.officer2).action_submit()


def test_rejection_returns_the_item_to_draft_with_its_reason(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    item.with_user(ppl.officer).action_submit()
    inbox_task(item, ppl.publisher).with_user(ppl.publisher).action_reject(comment="wrong type")
    assert item.state == "draft" and item.rejection_reason == "wrong type"


def test_recall_returns_the_item_to_draft(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    item.with_user(ppl.officer).action_submit()
    item.with_user(ppl.officer).action_recall_approval()
    assert item.state == "draft" and item.approval_state == "none"


def test_publish_restrict_discontinue_revise(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).action_publish()  # officer: no publisher role
    item.with_user(ppl.publisher2).action_publish()
    assert item.state == "published" and item.is_published
    item.with_user(ppl.publisher2).action_restrict(reason="recall of the batch")
    assert item.state == "restricted" and not item.is_published
    with pytest.raises(UserError, match="successor"), odoo_env.cr.savepoint():
        item.with_user(ppl.publisher2).action_discontinue()
    item.with_user(ppl.publisher2).action_discontinue(reason="brand exit, no successor")
    assert item.state == "deprecated" and item.discontinued_at
    assert not item.is_sellable
    item.with_user(ppl.officer).action_revise()
    assert item.state == "draft" and not item.approved_by


def test_classification_of_an_active_item_is_frozen(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    with pytest.raises(UserError, match="Revise the item"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).write({"item_type": "part"})
    # content that the approval does not cover stays editable
    item.with_user(ppl.officer).write({"description_bn": "নতুন বিবরণ"})


# --- ci_07 / ci_08: the item state gates sales ---------------------------------


def _branch(env):
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if branch:
        return branch
    ou = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "%s OU" % TAG, "code": "A4COU", "company_id": env.company.id}
    )
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "%s Entity" % TAG,
            "code": "A4CE",
            "company_id": env.company.id,
            "operating_unit_id": ou.id,
        }
    )
    return env["fix.branch"].create(
        {
            "name": "%s Branch" % TAG,
            "code": "A4C-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _estimate(env, user, product, price=800.0):
    branch = _branch(env)
    cust = env["res.partner"].create({"name": "%s cust" % TAG, "phone": "01700000937"})
    brand = env["fix.brand"].create({"name": "%s brand %d" % (TAG, next(_SEQ)), "code": "A4C"})
    model = env["fix.device.model"].create(
        {"name": "%s model %d" % (TAG, next(_SEQ)), "brand_id": brand.id}
    )
    dev = env["fix.device"].create(
        {
            "device_model_id": model.id,
            "owner_id": cust.id,
            "serial_number": "%s-SN-%d" % (TAG, next(_SEQ)),
        }
    )
    order = (
        env["fix.service.order"]
        .with_user(user)
        .create(
            {
                "device_id": dev.id,
                "customer_id": cust.id,
                "branch_id": branch.id,
                "service_type": "walk_in",
                "order_category": "standard",
                "fault_description": "a04 catalogue gate",
            }
        )
    )
    return (
        env["fix.estimate"]
        .with_user(user)
        .create(
            {
                "order_id": order.id,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "line_type": "part",
                            "description": "x",
                            "product_id": product.id,
                            "quantity": 1,
                            "unit_price": price,
                        },
                    )
                ],
            }
        )
    )


def test_a_discontinued_item_is_not_quoted(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    item.with_user(ppl.publisher2).action_discontinue(reason="end of life")
    product = item.product_tmpl_id.product_variant_id
    with pytest.raises(UserError, match="Discontinued"), odoo_env.cr.savepoint():
        _estimate(odoo_env, ppl.clerk, product)


def test_a_draft_item_is_quoted_only_while_the_gate_is_off(odoo_env, ppl):
    product = _item(odoo_env, ppl.officer).product_tmpl_id.product_variant_id
    Param = odoo_env["ir.config_parameter"].sudo()
    Param.set_param(SALE_GATE, "0")
    assert _estimate(odoo_env, ppl.clerk, product)
    Param.set_param(SALE_GATE, "1")
    with pytest.raises(UserError, match="only an Active item is sold"), odoo_env.cr.savepoint():
        _estimate(odoo_env, ppl.clerk, product)


def test_the_gate_defaults_off_for_deploy(odoo_env):
    Param = odoo_env["ir.config_parameter"].sudo()
    Param.search([("key", "=", SALE_GATE)]).unlink()
    item = odoo_env["fix.catalogue.item"].new({"state": "draft"})
    assert not item._sale_gate_on()


def test_restricted_item_is_not_sold_on_customer_facing_channels(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    item.with_user(ppl.publisher2).action_restrict(reason="existing customers only")
    product = item.product_tmpl_id.product_variant_id
    assert product._fix_check_sale(channel="estimate")
    with pytest.raises(UserError, match="restricted"):
        product._fix_check_sale(channel="storefront")


def test_an_item_needing_brand_authorisation_sells_only_while_it_is_held(odoo_env, ppl):
    brand = odoo_env["fix.brand"].create({"name": "%s auth brand" % TAG, "code": "A4AB"})
    item = _item(odoo_env, ppl.officer)
    item.with_user(ppl.officer).write({"brand_id": brand.id, "requires_brand_authorisation": True})
    product = item.product_tmpl_id.product_variant_id
    with pytest.raises(UserError, match="brand authorisation"):
        product._fix_check_sale(channel="estimate")


# --- ci_09 / M37-3: referenced items are never deleted -------------------------


def test_a_referenced_item_is_not_deleted(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    odoo_env["fix.rental.sku"].with_user(ppl.officer).create(
        {"catalogue_item_id": item.id, "daily_rate": 100.0}
    )
    with pytest.raises(UserError, match="BRU-CAT-03"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer2).unlink()
    with pytest.raises(UserError, match="BRU-CAT-03"), odoo_env.cr.savepoint():
        item.product_tmpl_id.with_user(ppl.publisher).unlink()
    assert item.exists()


def test_an_approved_item_is_never_deleted(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    with pytest.raises(UserError, match="never deleted"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).unlink()


def test_an_unreferenced_draft_can_be_deleted_by_its_officer(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer)
    item.with_user(ppl.officer).unlink()
    assert not item.exists()


# --- kit / rBOM / rental integrity (kit_02, kit_04, rbom_01, rbom_02, rs_01) ----


def _kit(env, item, user):
    return (
        env["fix.service.kit"]
        .with_user(user)
        .create(
            {
                "name": "%s kit" % TAG,
                "catalogue_item_id": item.id,
                "component_ids": [
                    (0, 0, {"component_type": "labour", "notes": "fit", "time_allocation": 1.0})
                ],
            }
        )
    )


def test_a_kit_keeps_at_least_one_component(odoo_env, ppl):
    kit = _kit(odoo_env, _item(odoo_env, ppl.officer), ppl.officer)
    with pytest.raises(ValidationError, match="at least one component"), odoo_env.cr.savepoint():
        kit.component_ids.with_user(ppl.officer).unlink()
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        kit.component_ids.with_user(ppl.clerk).unlink()
    assert kit.component_count == 1


def test_a_kit_does_not_sit_on_a_spare_part(odoo_env, ppl):
    part = _item(odoo_env, ppl.officer, item_type="part")
    with pytest.raises(ValidationError, match="service kit sits on"), odoo_env.cr.savepoint():
        _kit(odoo_env, part, ppl.officer)


def test_rbom_refuses_cycles_and_non_positive_quantities(odoo_env, ppl):
    a = _item(odoo_env, ppl.officer)
    b = _item(odoo_env, ppl.officer, item_type="part")
    c = _item(odoo_env, ppl.officer, item_type="part")
    Line = odoo_env["fix.rbom.line"].with_user(ppl.officer)
    Line.create({"item_id": a.id, "component_item_id": b.id, "quantity": 1})
    Line.create({"item_id": b.id, "component_item_id": c.id, "quantity": 2})
    with pytest.raises(ValidationError, match="rBOM cycle"), odoo_env.cr.savepoint():
        Line.create({"item_id": c.id, "component_item_id": a.id, "quantity": 1})
    for qty in (0, -3):
        with pytest.raises(ValidationError, match="positive quantity"), odoo_env.cr.savepoint():
            Line.create({"item_id": a.id, "component_item_id": c.id, "quantity": qty})
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        odoo_env["fix.rbom.line"].with_user(ppl.clerk).create(
            {"item_id": a.id, "component_item_id": c.id, "quantity": 1}
        )


@pytest.mark.parametrize(
    "vals", [{"daily_rate": -100.0}, {"security_deposit": -5000.0}, {"max_rental_days": -1}]
)
def test_rental_sku_refuses_negative_terms(odoo_env, ppl, vals):
    item = _item(odoo_env, ppl.officer, item_type="rental")
    with pytest.raises(ValidationError, match="cannot be negative"), odoo_env.cr.savepoint():
        odoo_env["fix.rental.sku"].with_user(ppl.officer).create(
            dict({"catalogue_item_id": item.id}, **vals)
        )


# --- br_01: brand authorisation is a decision ---------------------------------


def test_brand_authorisation_cannot_be_ticked(odoo_env, ppl):
    brand = (
        odoo_env["fix.brand"]
        .with_user(ppl.clerk)
        .create({"name": "%s brand tick" % TAG, "code": "A4BT"})
    )
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        brand.with_user(ppl.clerk).write({"authorised": True, "authorisation_expiry": "2020-01-01"})


def test_brand_authorisation_is_requested_and_decided_by_another_publisher(odoo_env, ppl):
    brand = (
        odoo_env["fix.brand"]
        .with_user(ppl.clerk)
        .create({"name": "%s brand ok" % TAG, "code": "A4BO"})
    )
    brand.with_user(ppl.clerk).write(
        {
            "proposed_authorisation_reference": "SAMS/AUTH/2026/17",
            "proposed_authorisation_expiry": "2027-12-31",
        }
    )
    brand.with_user(ppl.clerk).action_request_authorisation()
    assert brand.approval_state == "pending" and brand.authorisation_requested_by == ppl.clerk
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        brand.with_user(ppl.clerk).write({"proposed_authorisation_expiry": "2030-01-01"})
    approve_via_inbox(brand, ppl.publisher, requester=ppl.clerk)
    assert brand.authorised and str(brand.authorisation_expiry) == "2027-12-31"
    assert brand.authorised_by == ppl.publisher
    assert brand.authorisation_reference == "SAMS/AUTH/2026/17"
    # a requester who is also a publisher is never routed their own request
    other = (
        odoo_env["fix.brand"]
        .with_user(ppl.publisher)
        .create({"name": "%s brand self" % TAG, "code": "A4BS"})
    )
    other.with_user(ppl.publisher).write(
        {"proposed_authorisation_reference": "X/1", "proposed_authorisation_expiry": "2027-01-01"}
    )
    other.with_user(ppl.publisher).action_request_authorisation()
    assert ppl.publisher not in other.approval_request_id.task_ids.mapped("assigned_user_id")


def test_expired_authorisation_lapses_nightly(odoo_env):
    brand = odoo_env["fix.brand"].create(
        {
            "name": "%s brand lapse" % TAG,
            "code": "A4BL",
            "authorised": True,
            "authorisation_expiry": "2020-01-01",
        }
    )
    assert not brand._authorisation_in_force()
    assert odoo_env["fix.brand"].cron_authorisation_expiry() >= 1
    assert not brand.authorised
    assert odoo_env["fix.brand"].cron_authorisation_expiry() == 0  # idempotent


def test_discontinued_item_past_end_of_support_becomes_obsolete(odoo_env, ppl):
    item = _activate(odoo_env, _item(odoo_env, ppl.officer), ppl.publisher)
    item.with_user(ppl.publisher2).action_discontinue(reason="no successor")
    item._guarded().write({"end_of_support_date": "2020-01-01"})
    assert odoo_env["fix.catalogue.item"].cron_obsolete_discontinued() >= 1
    assert item.state == "obsolete"


# --- C10: the crons exist and name their methods --------------------------------


@pytest.mark.parametrize(
    "xmlid,method",
    [
        ("cd_catalogue.ir_cron_m37_brand_authorisation_expiry", "cron_authorisation_expiry"),
        ("cd_catalogue.ir_cron_m37_obsolete_discontinued", "cron_obsolete_discontinued"),
    ],
)
def test_catalogue_crons_are_scheduled(odoo_env, xmlid, method):
    cron = odoo_env.ref(xmlid)
    assert cron.active and method in cron.code


def test_roles_are_declared_with_the_admin_as_publisher(odoo_env):
    officer = odoo_env.ref(OFFICER)
    publisher = odoo_env.ref(PUBLISHER)
    assert officer in publisher.all_implied_ids
    assert odoo_env.ref("base.user_admin") in publisher.all_user_ids
    assert publisher.privilege_id == odoo_env.ref("cd_catalogue.privilege_catalogue")


def test_officer_sets_the_bengali_name_through_the_item(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, name_bn=False)
    item.with_user(ppl.officer).write({"name_bn": "নতুন নাম"})
    assert item.product_tmpl_id.name_bn == "নতুন নাম" and item.name_bn == "নতুন নাম"
