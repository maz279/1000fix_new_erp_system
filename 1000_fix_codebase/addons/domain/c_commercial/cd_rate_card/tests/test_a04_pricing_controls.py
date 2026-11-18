# A04 C2-C13 (2026-11-04): M11 pricing controls, exercised as non-admin users
# on the live ORM (`odoo_env`, rolled back).
#
# Each test replays an attack from working/A04_evidence/probes/m11_m36_m37/
# probe_m11.py with the actor the control is about, and shows the legitimate
# path: a Pricing Officer authors, a Price-Book Releaser who is not the author
# releases from the M63 inbox, a DOFA holder approves a below-floor override.
import importlib.util
import itertools
import json
import uuid
from datetime import timedelta
from pathlib import Path

import pytest
from odoo import fields
from odoo.addons.cd_rate_card.tests import contract_helpers
from odoo.addons.cd_workflow_engine.tests.approval_helpers import approve_via_inbox, inbox_task
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "A4C11-%s" % uuid.uuid4().hex[:6]
_SEQ = itertools.count(1)
OFFICER = "cd_rate_card.group_pricing_officer"
RELEASER = "cd_rate_card.group_price_releaser"


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
        releaser = _user(odoo_env, "rel", [RELEASER])
        t2 = _user(odoo_env, "t2", ["cd_entity_config.group_dofa_tier_2"])
        t4 = _user(odoo_env, "t4", ["cd_entity_config.group_dofa_tier_4"])

    return P


def _today(env):
    return fields.Date.context_today(env["res.users"])


def _book(env, user):
    n = next(_SEQ)
    return (
        env["fix.price.book"]
        .with_user(user)
        .create({"name": "%s book %d" % (TAG, n), "code": "%s-B%d" % (TAG, n)})
    )


def _version(env, book, user, effective=None, version="1"):
    return (
        env["fix.price.version"]
        .with_user(user)
        .create(
            {
                "name": "%s v%s" % (TAG, version),
                "book_id": book.id,
                "version": version,
                "effective_from": effective or _today(env),
            }
        )
    )


# --- roles -------------------------------------------------------------------


@pytest.mark.parametrize(
    "model,vals",
    [
        ("fix.price.book", {"name": "x", "code": "X"}),
        ("fix.price.floor", {"name": "x", "product_code": "X", "floor_price": 10.0}),
        ("fix.promotion", {"name": "x", "code": "X", "value": 5.0}),
        ("fix.rate.card", {"product_code": "X", "unit_price": 10.0}),
        ("fix.discount.policy", {"name": "x", "min_pct": 0, "max_pct": 50}),
    ],
)
def test_plain_user_reads_but_does_not_author_prices(odoo_env, ppl, model, vals):
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        odoo_env[model].with_user(ppl.clerk).create(vals)


# --- pv_01..pv_07, pb_01: the price-book version lifecycle ----------------------


@pytest.mark.parametrize(
    "vals", [{"state": "active"}, {"approved_by": None}, {"state": "approved"}]
)
def test_version_state_and_approver_are_not_typed(odoo_env, ppl, vals):
    version = _version(odoo_env, _book(odoo_env, ppl.officer), ppl.officer)
    vals = {k: (v if v is not None else ppl.officer.id) for k, v in vals.items()}
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        version.with_user(ppl.officer).write(vals)


def test_book_state_is_not_typed(odoo_env, ppl):
    book = _book(odoo_env, ppl.officer)
    _version(odoo_env, book, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        book.with_user(ppl.officer).write({"state": "active"})


def test_version_is_released_by_someone_else_and_activates_its_book(odoo_env, ppl):
    book = _book(odoo_env, ppl.officer)
    v1 = _version(odoo_env, book, ppl.officer)
    v1.with_user(ppl.officer).action_submit()
    assert v1.state == "in_review" and v1.approval_state == "pending"
    assert ppl.officer not in v1.approval_request_id.task_ids.mapped("assigned_user_id")
    with pytest.raises(UserError, match="approver's inbox"), odoo_env.cr.savepoint():
        v1.with_user(ppl.releaser).action_approve()
    inbox_task(v1, ppl.releaser).with_user(ppl.releaser).action_approve()
    assert v1.state == "active" and v1.approved_by == ppl.releaser
    assert book.state == "active" and book.active_version_id == v1
    # a second version supersedes the first: one active version per book
    v2 = _version(odoo_env, book, ppl.officer2, version="2")
    v2.with_user(ppl.officer2).action_submit()
    approve_via_inbox(v2, ppl.releaser, requester=ppl.officer2)
    assert v2.state == "active" and v1.state == "superseded" and v1.superseded_by_id == v2
    assert (
        odoo_env["fix.price.version"].search_count(
            [("book_id", "=", book.id), ("state", "=", "active")]
        )
        == 1
    )
    # a released version is frozen
    with pytest.raises(UserError, match="cannot change any more"), odoo_env.cr.savepoint():
        v2.with_user(ppl.officer2).write({"effective_from": _today(odoo_env) + timedelta(days=9)})


def test_future_version_waits_for_its_date(odoo_env, ppl):
    book = _book(odoo_env, ppl.officer)
    future = _version(odoo_env, book, ppl.officer, effective=_today(odoo_env) + timedelta(days=30))
    future.with_user(ppl.officer).action_submit()
    approve_via_inbox(future, ppl.releaser, requester=ppl.officer)
    assert future.state == "approved" and book.state == "draft"
    assert odoo_env["fix.price.version"].cron_activate_due_versions() == 0
    with pytest.raises(ValidationError, match="never active before"), odoo_env.cr.savepoint():
        future._guarded().write({"state": "active"})
    future._guarded().write({"effective_from": _today(odoo_env)})
    assert odoo_env["fix.price.version"].cron_activate_due_versions() == 1
    assert future.state == "active"
    assert odoo_env["fix.price.version"].cron_activate_due_versions() == 0  # idempotent


def test_rejected_version_returns_to_draft(odoo_env, ppl):
    version = _version(odoo_env, _book(odoo_env, ppl.officer), ppl.officer)
    version.with_user(ppl.officer).action_submit()
    inbox_task(version, ppl.releaser).with_user(ppl.releaser).action_reject(comment="margin")
    assert version.state == "draft" and version.rejection_reason == "margin"


# --- pf_01..pf_09: the below-floor override is a routed, pinned DOFA approval ---


def _changes(env, field, target):
    return env["fix.price.change"].search([(field, "=", target.id)])


def _floor(env, user, price=1000.0, **kw):
    vals = {"name": "%s floor" % TAG, "product_code": "%s-SKU" % TAG, "floor_price": price}
    vals.update(kw)
    return env["fix.price.floor"].with_user(user).create(vals)


def test_override_flag_cannot_be_forged(odoo_env, ppl):
    floor = _floor(odoo_env, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        floor.with_user(ppl.officer).write({"dofa_override_approved": True})
    with pytest.raises(UserError, match="below statutory price floor"):
        floor.validate_price_against_floor(100.0)


def test_override_covers_only_the_depth_approved(odoo_env, ppl):
    """pf_07: approve 10% below the floor (Tier 2), then deepen to 90%."""
    floor = _floor(odoo_env, ppl.officer)
    floor.with_user(ppl.clerk).write(
        {"proposed_override_price": 900.0, "dofa_justification": "price match"}
    )
    approve_via_inbox(floor, ppl.t2, requester=ppl.clerk)
    assert floor.dofa_approved and floor.dofa_override_approved
    assert floor.dofa_override_user_id == ppl.t2
    assert floor.validate_price_against_floor(900.0)
    floor.with_user(ppl.clerk).write({"proposed_override_price": 100.0})
    assert not floor.dofa_approved and not floor.dofa_override_approved
    with pytest.raises(UserError):
        floor.validate_price_against_floor(100.0)


def test_override_is_decided_from_the_inbox_by_the_right_tier(odoo_env, ppl):
    floor = _floor(odoo_env, ppl.officer, proposed_override_price=400.0)  # 60% below: Tier 4
    floor.with_user(ppl.officer).write({"dofa_justification": "clearance"})
    with pytest.raises(UserError, match="authority insufficient"), odoo_env.cr.savepoint():
        floor.with_user(ppl.t2).action_approve_dofa_override()
    with pytest.raises(UserError, match="approver's inbox"), odoo_env.cr.savepoint():
        floor.with_user(ppl.t4).action_approve_dofa_override()
    floor.with_user(ppl.clerk).action_request_approval()
    assert ppl.t4 in floor.approval_request_id.task_ids.mapped("assigned_user_id")
    assert floor.dofa_tier == "tier4" and floor.dofa_tier_required == "tier_4"


def test_floor_price_moves_only_through_an_approved_change(odoo_env, ppl):
    """pf_08: lowering the floor 1000 -> 1."""
    floor = _floor(odoo_env, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        floor.with_user(ppl.officer2).write({"floor_price": 1.0})
    floor.with_user(ppl.officer).write(
        {"proposed_floor_price": 800.0, "floor_change_reason": "cost fell"}
    )
    floor.with_user(ppl.officer).action_request_floor_change()
    change = _changes(odoo_env, "floor_id", floor)
    assert change.state == "pending" and change.current_value == 1000.0
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        change.with_user(ppl.officer).write({"proposed_value": 1.0})
    approve_via_inbox(change, ppl.releaser, requester=ppl.officer)
    assert change.state == "applied" and floor.floor_price == 800.0
    assert change.applied_by == ppl.releaser


def test_change_is_refused_when_the_target_moved_meanwhile(odoo_env, ppl):
    floor = _floor(odoo_env, ppl.officer)
    change = (
        odoo_env["fix.price.change"]
        .with_user(ppl.officer)
        .create(
            {
                "target_type": "floor",
                "change_type": "change",
                "floor_id": floor.id,
                "proposed_value": 700.0,
                "reason": "test",
            }
        )
    )
    change.with_user(ppl.officer).action_submit()
    floor._guarded().write({"floor_price": 1200.0})
    with pytest.raises(UserError, match="raise it again"), odoo_env.cr.savepoint():
        approve_via_inbox(change, ppl.releaser, requester=ppl.officer)


# --- rc_01: a released rate changes only through a release --------------------


def test_rate_card_release_and_change(odoo_env, ppl):
    card = (
        odoo_env["fix.rate.card"]
        .with_user(ppl.officer)
        .create({"product_code": "%s-RC" % TAG, "unit_price": 1000.0})
    )
    assert card.state == "draft"
    Card = odoo_env["fix.rate.card"]
    assert not Card._resolve(card.product_code)  # a draft prices nothing
    card.with_user(ppl.officer).action_request_release()
    approve_via_inbox(_changes(odoo_env, "rate_card_id", card), ppl.releaser, requester=ppl.officer)
    assert card.state == "released" and card.released_by == ppl.releaser
    assert Card._resolve(card.product_code) == card
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        card.with_user(ppl.officer).write({"unit_price": 1.0})
    with pytest.raises(REFUSED), odoo_env.cr.savepoint():
        card.with_user(ppl.clerk).write({"unit_price": 1.0})
    card.with_user(ppl.officer2).write({"proposed_unit_price": 950.0, "change_reason": "survey"})
    card.with_user(ppl.officer2).action_request_change()
    change = _changes(odoo_env, "rate_card_id", card).filtered(lambda c: c.state == "pending")
    # the officer who raised it cannot release it, even holding the role
    assert ppl.officer2 not in change.approval_request_id.task_ids.mapped("assigned_user_id")
    approve_via_inbox(change, ppl.releaser, requester=ppl.officer2)
    assert card.unit_price == 950.0
    event = odoo_env["fix.event.outbox"].search(
        [("event_type", "=", "pricing.price_changed"), ("aggregate_id", "=", change.id)]
    )
    assert json.loads(event.payload)["new_value"] == 950.0


def test_contract_lane_wins_in_resolution(odoo_env):
    code = "%s-RES" % TAG
    Card = odoo_env["fix.rate.card"]
    tier = Card.create({"product_code": code, "unit_price": 500.0, "min_tier": 0})
    k = contract_helpers.contract(odoo_env)
    contract = Card.create(
        {"product_code": code, "unit_price": 400.0, "min_tier": 99, "contract_no": k.code}
    )
    (tier | contract)._guarded().write({"state": "released"})
    assert Card._resolve(code) == tier
    assert Card._resolve(code, contract_no=k.code) == contract


# --- pf_10: the estimate reads the floor ---------------------------------------


def _branch(env):
    branch = env["fix.branch"].search([("operating_unit_id", "!=", False)], limit=1)
    if branch:
        return branch
    ou = env["operating.unit"].search([], limit=1) or env["operating.unit"].create(
        {"name": "%s OU" % TAG, "code": "A4POU", "company_id": env.company.id}
    )
    entity = env["fix.entity"].search([], limit=1) or env["fix.entity"].create(
        {
            "legal_name": "%s Entity" % TAG,
            "code": "A4PE",
            "company_id": env.company.id,
            "operating_unit_id": ou.id,
        }
    )
    return env["fix.branch"].create(
        {
            "name": "%s Branch" % TAG,
            "code": "A4P-BR",
            "entity_id": entity.id,
            "operating_unit_id": ou.id,
        }
    )


def _estimate(env, user, product, price):
    n = next(_SEQ)
    cust = env["res.partner"].create({"name": "%s cust" % TAG, "phone": "01700000111"})
    brand = env["fix.brand"].create({"name": "%s brand %d" % (TAG, n), "code": "A4PB"})
    model = env["fix.device.model"].create({"name": "%s m %d" % (TAG, n), "brand_id": brand.id})
    dev = env["fix.device"].create(
        {"device_model_id": model.id, "owner_id": cust.id, "serial_number": "%s-%d" % (TAG, n)}
    )
    order = (
        env["fix.service.order"]
        .with_user(user)
        .create(
            {
                "device_id": dev.id,
                "customer_id": cust.id,
                "branch_id": _branch(env).id,
                "service_type": "walk_in",
                "order_category": "standard",
                "fault_description": "a04 floor gate",
            }
        )
    )
    line = {
        "line_type": "part",
        "description": "p",
        "product_id": product.id,
        "quantity": 1,
        "unit_price": price,
    }
    return (
        env["fix.estimate"]
        .with_user(user)
        .create({"order_id": order.id, "line_ids": [(0, 0, line)]})
    )


def test_estimate_below_the_floor_is_refused(odoo_env, ppl):
    code = "%s-FLOORSKU" % TAG
    product = odoo_env["product.product"].create(
        {"name": "%s floor product" % TAG, "default_code": code, "list_price": 500.0}
    )
    floor = _floor(odoo_env, ppl.officer, price=900.0, product_code=code)
    with pytest.raises(UserError, match="below statutory price floor"), odoo_env.cr.savepoint():
        _estimate(odoo_env, ppl.clerk, product, 600.0)
    assert _estimate(odoo_env, ppl.clerk, product, 950.0)
    # with an override approved for 850, 850 is accepted and 800 is not
    floor.with_user(ppl.clerk).write(
        {"proposed_override_price": 850.0, "dofa_justification": "competitor match"}
    )
    approve_via_inbox(floor, ppl.t2, requester=ppl.clerk)
    assert _estimate(odoo_env, ppl.clerk, product, 850.0)
    with pytest.raises(UserError, match="Re-approval is required"), odoo_env.cr.savepoint():
        _estimate(odoo_env, ppl.clerk, product, 800.0)


# --- pr_01..pr_05: promotions --------------------------------------------------


def _promo(env, user, **kw):
    n = next(_SEQ)
    vals = {
        "name": "%s promo %d" % (TAG, n),
        "code": "%s-P%d" % (TAG, n),
        "value": 10.0,
        "valid_from": _today(env),
        "valid_until": _today(env) + timedelta(days=30),
    }
    vals.update(kw)
    return env["fix.promotion"].with_user(user).create(vals)


@pytest.mark.parametrize(
    "vals,match",
    [
        ({"value": 150.0}, "at most 100"),
        ({"value": 0.0}, "positive discount"),
        ({"value": -5.0}, "positive discount"),
        ({"budget_amount": -1.0}, "cannot be negative"),
    ],
)
def test_promotion_bounds(odoo_env, ppl, vals, match):
    with pytest.raises(ValidationError, match=match), odoo_env.cr.savepoint():
        _promo(odoo_env, ppl.officer, **vals)


def test_promotion_window_cannot_be_inverted(odoo_env, ppl):
    with pytest.raises(ValidationError, match="ends"), odoo_env.cr.savepoint():
        _promo(
            odoo_env,
            ppl.officer,
            valid_from=_today(odoo_env) + timedelta(days=10),
            valid_until=_today(odoo_env),
        )


def test_promotion_is_released_not_typed(odoo_env, ppl):
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        _promo(odoo_env, ppl.officer, state="active")
    promo = _promo(odoo_env, ppl.officer)
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        promo.with_user(ppl.officer).write({"state": "active"})
    promo.with_user(ppl.officer).action_submit()
    approve_via_inbox(promo, ppl.releaser, requester=ppl.officer)
    assert promo.state == "active" and promo.approved_by == ppl.releaser
    with pytest.raises(UserError, match="cannot change any more"), odoo_env.cr.savepoint():
        promo.with_user(ppl.officer).write({"value": 95.0})


def test_promotion_budget_and_stacking(odoo_env, ppl):
    excl_a = _promo(odoo_env, ppl.officer, value=10.0)
    excl_b = _promo(odoo_env, ppl.officer, value=15.0)
    stack_a = _promo(odoo_env, ppl.officer, value=5.0, stackable=True)
    stack_b = _promo(odoo_env, ppl.officer, value=8.0, stackable=True, budget_amount=100.0)
    promos = excl_a | excl_b | stack_a | stack_b
    promos._guarded().write({"state": "active"})
    Promo = odoo_env["fix.promotion"]
    best, discount = Promo.best_combination(promos, 1000.0)
    # exclusive promotions never combine: the best one (15% = 150) beats the
    # stackable pair (5% + 8% = 130); 10% and 15% are never added up
    assert best == excl_b and discount == 150.0
    stack_c = _promo(odoo_env, ppl.officer, value=12.0, stackable=True)
    stack_c._guarded().write({"state": "active"})
    promos |= stack_c
    best, discount = Promo.best_combination(promos, 1000.0)
    assert best == (stack_a | stack_b | stack_c) and discount == 250.0
    promos -= stack_c
    stack_b.consume(100.0)
    assert stack_b.state == "ended"  # budget spent
    best, discount = Promo.best_combination(promos, 1000.0)
    assert best == excl_b and discount == 150.0
    with pytest.raises(UserError, match="not usable"):
        stack_b.consume(1.0)


def test_promotion_window_cron(odoo_env, ppl):
    promo = _promo(odoo_env, ppl.officer, valid_from=_today(odoo_env) + timedelta(days=5))
    promo.with_user(ppl.officer).action_submit()
    approve_via_inbox(promo, ppl.releaser, requester=ppl.officer)
    assert promo.state == "approved"
    promo._guarded().write(
        {
            "valid_from": _today(odoo_env) - timedelta(days=40),
            "valid_until": _today(odoo_env) - timedelta(days=1),
        }
    )
    odoo_env["fix.promotion"].cron_promotion_window()
    assert promo.state == "ended"


# --- dp_01: the one discount ladder --------------------------------------------


def test_discount_ladder_defaults_to_the_spec_and_follows_released_bands(odoo_env, ppl):
    Policy = odoo_env["fix.discount.policy"]
    Policy.sudo().search([("state", "=", "active")])._guarded().write({"state": "retired"})
    assert Policy.tier_for_discount(10.0) == "tier_0"
    assert Policy.tier_for_discount(20.0) == "tier_2"
    assert Policy.tier_for_discount(35.0) == "tier_3"
    assert Policy.tier_for_discount(36.0) == "tier_4"
    band = Policy.with_user(ppl.officer).create(
        {"name": "agent", "min_pct": 0.0, "max_pct": 5.0, "requires_approval": False}
    )
    # a draft band is not in force
    assert Policy.tier_for_discount(8.0) == "tier_0"
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        band.with_user(ppl.officer).write({"state": "active"})
    band.with_user(ppl.officer).action_submit()
    approve_via_inbox(band, ppl.releaser, requester=ppl.officer)
    assert band.state == "active"
    assert Policy.tier_for_discount(5.0) == "tier_0"
    assert Policy.tier_for_discount(8.0) == "tier_4"  # above every released band: CCO
    with pytest.raises(UserError, match="cannot change any more"), odoo_env.cr.savepoint():
        band.with_user(ppl.officer).write({"max_pct": 50.0})


# --- ps_01: the simulation is computed, not typed --------------------------------


def test_simulation_is_computed(odoo_env, ppl):
    code = "%s-SIM" % TAG
    card = odoo_env["fix.rate.card"].create({"product_code": code, "unit_price": 1200.0})
    card._guarded().write({"state": "released"})
    _floor(odoo_env, ppl.officer, price=1000.0, product_code=code)
    sim = (
        odoo_env["fix.price.simulation"]
        .with_user(ppl.clerk)
        .create(
            {
                "name": "%s sim" % TAG,
                "rate_card_id": card.id,
                "input_json": '{"quantity": 2, "price": 900}',
            }
        )
    )
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        sim.with_user(ppl.clerk).write({"state": "computed", "result_json": '{"price": 1}'})
    sim.with_user(ppl.clerk).action_compute()
    result = json.loads(sim.result_json)
    assert sim.state == "computed" and sim.computed_at
    assert result["gross"] == 2400.0 and result["proposed_below_floor"] is True


# --- C10 / roles / migration --------------------------------------------------


@pytest.mark.parametrize(
    "xmlid,method",
    [
        ("cd_rate_card.ir_cron_m11_activate_versions", "cron_activate_due_versions"),
        ("cd_rate_card.ir_cron_m11_promotion_window", "cron_promotion_window"),
    ],
)
def test_pricing_crons_are_scheduled(odoo_env, xmlid, method):
    cron = odoo_env.ref(xmlid)
    assert cron.active and method in cron.code


def test_roles_are_declared_with_the_admin_as_releaser(odoo_env):
    releaser = odoo_env.ref(RELEASER)
    assert odoo_env.ref(OFFICER) in releaser.all_implied_ids
    assert odoo_env.ref("base.user_admin") in releaser.all_user_ids


def test_migration_releases_the_pre_control_cards(odoo_env):
    path = Path(__file__).resolve().parents[1] / "migrations" / "19.0.1.1.0" / "post-migrate.py"
    spec = importlib.util.spec_from_file_location("a04_rate_card_post_migrate", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    Card = odoo_env["fix.rate.card"].with_context(active_test=False)
    live = Card.create({"product_code": "%s-MIG1" % TAG, "unit_price": 10.0})
    gone = Card.create({"product_code": "%s-MIG2" % TAG, "unit_price": 10.0, "active": False})
    odoo_env.flush_all()
    mod.migrate(odoo_env.cr, "19.0.1.0.0")
    (live | gone).invalidate_recordset()
    assert (live.state, gone.state) == ("released", "retired")
