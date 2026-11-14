# M37 capture audit, second pass (2026-11-14): the records and rules behind
# the sub-module pages that had nothing relevant to capture, exercised as
# non-admin users on the live ORM (`odoo_env`, rolled back).
#
# - Tax & Rev-Rec (FR-CAT-043, BRU-CAT-02): an item is not submitted without
#   its VAT class and revenue class; a blank on a decided (migrated) item may
#   be completed, a set value changes only by Revise.
# - Repair operations (BRU-CAT-06) need a level and an SRT; an Active item's
#   SRT moves only by an approved baseline (BRU-CAT-11).
# - fix.srt.baseline, fix.part.crossref, fix.catalogue.publication.
import itertools
import uuid

import psycopg2
import pytest
from odoo import fields
from odoo.exceptions import AccessError, UserError, ValidationError

REFUSED = (UserError, ValidationError, AccessError)
TAG = "M37L-%s" % uuid.uuid4().hex[:6]
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
                "login": "%s.%s.%d@m37.test" % (TAG.lower(), tag, n),
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
        publisher2 = _user(odoo_env, "pub2", [PUBLISHER])

    return P


def _category(env):
    return env["product.category"].search([], limit=1)


def _item(env, user, item_type="service", classified=True, **extra):
    n = next(_SEQ)
    tmpl = env["product.template"].create(
        {
            "name": "%s item %d" % (TAG, n),
            "default_code": "%s-%d" % (TAG, n),
            "name_bn": "পরীক্ষা %d" % n,
        }
    )
    vals = {"product_tmpl_id": tmpl.id, "item_type": item_type, "category_id": _category(env).id}
    if classified:
        vals.update({"vat_class": "standard_15", "revenue_recognition": "on_completion"})
    vals.update(extra)
    return env["fix.catalogue.item"].with_user(user).create(vals)


def _decided(item, state="approved"):
    """As the 16,178 migrated items on fix_real: decided, with no review."""
    item.sudo()._guarded().write({"state": state})
    return item


# --- BRU-CAT-02 / 06 / 15: what an item needs before it leaves Draft -----------


def test_submit_needs_vat_and_revenue_class(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, classified=False)
    with pytest.raises(UserError, match="VAT class.*revenue-recognition"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).action_submit()
    item.with_user(ppl.officer).write({"vat_class": "exempt", "revenue_recognition": "on_delivery"})
    item.with_user(ppl.officer).action_submit()
    assert item.state == "in_review"


def test_repair_operation_needs_level_and_srt(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, item_type="labour")
    with (
        pytest.raises(UserError, match="repair level.*standard repair time"),
        odoo_env.cr.savepoint(),
    ):
        item.with_user(ppl.officer).action_submit()
    item.with_user(ppl.officer).write({"repair_level": "l2", "standard_labour_time": 0.75})
    item.with_user(ppl.officer).action_submit()
    assert item.state == "in_review"


def test_hazardous_item_needs_its_handling_constraints(odoo_env, ppl):
    with pytest.raises(ValidationError, match="BRU-CAT-15"), odoo_env.cr.savepoint():
        _item(odoo_env, ppl.officer, item_type="part", hazard_class="lithium_battery")
    item = _item(
        odoo_env,
        ppl.officer,
        item_type="part",
        hazard_class="lithium_battery",
        hazard_handling="UN3481; store below 30C; e-waste vendor only.",
    )
    assert item.hazard_class == "lithium_battery"


@pytest.mark.parametrize(
    "code,ok", [("8517.13.00", True), ("85171300", True), ("85x7", False), ("851", False)]
)
def test_hs_code_is_a_tariff_code(odoo_env, ppl, code, ok):
    item = _item(odoo_env, ppl.officer, item_type="part")
    if ok:
        item.with_user(ppl.officer).write({"hs_code": code})
        assert item.hs_code == code
    else:
        with pytest.raises(ValidationError, match="tariff code"), odoo_env.cr.savepoint():
            item.with_user(ppl.officer).write({"hs_code": code})


def test_decided_item_blank_classification_is_completed_not_changed(odoo_env, ppl):
    item = _decided(_item(odoo_env, ppl.officer, item_type="part", classified=False))
    officer = item.with_user(ppl.officer)
    # the page-12 capture: completing a migrated item's blanks
    officer.write(
        {"vat_class": "standard_15", "revenue_recognition": "on_delivery", "hs_code": "8473.30.00"}
    )
    assert (item.vat_class, item.revenue_recognition) == ("standard_15", "on_delivery")
    # the workspace form re-sends every field: the same values pass
    officer.write({"vat_class": "standard_15", "hs_code": "8473.30.00"})
    for vals in ({"vat_class": "exempt"}, {"hs_code": "8517.13.00"}, {"sd_applicable": True}):
        with pytest.raises(UserError, match="Revise the item"), odoo_env.cr.savepoint():
            officer.write(vals)
    locked = item._fix_form_locked_fields()
    assert {"vat_class", "hs_code", "revenue_recognition", "sd_applicable"} <= locked
    assert "provenance_grade" not in locked  # still blank: open to complete


def test_active_item_srt_is_not_edited_in_place(odoo_env, ppl):
    item = _decided(
        _item(
            odoo_env, ppl.officer, item_type="labour", repair_level="l1", standard_labour_time=1.0
        )
    )
    with pytest.raises(UserError, match="Revise the item"), odoo_env.cr.savepoint():
        item.with_user(ppl.officer).write({"standard_labour_time": 2.0})
    assert "standard_labour_time" in item._fix_form_locked_fields()


# --- fix.srt.baseline (FR-CAT-023/024, BRU-CAT-11) ---------------------------


def _baseline(env, user, item, minutes=90.0, **extra):
    vals = {
        "item_id": item.id,
        "repair_level": "l1",
        "minutes": minutes,
        "source": "time_study",
        "reason": "Bench time study, 12 jobs",
    }
    vals.update(extra)
    return env["fix.srt.baseline"].with_user(user).create(vals)


def test_srt_baseline_moves_the_item_only_when_another_publisher_approves(odoo_env, ppl):
    item = _decided(
        _item(
            odoo_env, ppl.officer, item_type="labour", repair_level="l1", standard_labour_time=1.0
        )
    )
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        _baseline(odoo_env, ppl.clerk, item)
    base = _baseline(odoo_env, ppl.officer, item, minutes=90.0)
    base.with_user(ppl.officer).action_propose()
    assert base.state == "proposed" and base.previous_minutes == pytest.approx(60.0)
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        base.with_user(ppl.officer).action_approve()
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        base.with_user(ppl.officer).write({"state": "approved"})
    with pytest.raises(UserError, match="fixed"), odoo_env.cr.savepoint():
        base.with_user(ppl.officer).write({"minutes": 30.0})
    base.with_user(ppl.publisher).action_approve()
    assert base.state == "approved" and base.approved_by == ppl.publisher and base.applied_at
    assert item.standard_labour_time == pytest.approx(1.5)
    # the next approved baseline supersedes it
    nxt = _baseline(
        odoo_env,
        ppl.officer,
        item,
        minutes=75.0,
        source="calibration",
        sample_size=20,
        observed_avg_minutes=74.0,
    )
    nxt.with_user(ppl.officer).action_propose()
    nxt.with_user(ppl.publisher2).action_approve()
    assert base.state == "superseded" and item.standard_labour_time == pytest.approx(1.25)
    with pytest.raises(UserError, match="never deleted"), odoo_env.cr.savepoint():
        base.with_user(ppl.officer).unlink()


def test_publisher_cannot_approve_a_baseline_they_proposed(odoo_env, ppl):
    item = _item(
        odoo_env, ppl.officer, item_type="labour", repair_level="l1", standard_labour_time=1.0
    )
    base = _baseline(odoo_env, ppl.publisher, item)
    base.with_user(ppl.publisher).action_propose()
    with pytest.raises(UserError, match="Segregation of duties"), odoo_env.cr.savepoint():
        base.with_user(ppl.publisher).action_approve()
    with pytest.raises(UserError, match="why"), odoo_env.cr.savepoint():
        base.with_user(ppl.publisher2).action_reject("")
    base.with_user(ppl.publisher2).action_reject("Sample too small")
    assert base.state == "rejected" and item.standard_labour_time == pytest.approx(1.0)


def test_future_baseline_waits_for_its_date(odoo_env, ppl):
    item = _decided(
        _item(
            odoo_env, ppl.officer, item_type="labour", repair_level="l1", standard_labour_time=1.0
        )
    )
    tomorrow = fields.Date.add(fields.Date.context_today(item), days=1)
    base = _baseline(odoo_env, ppl.officer, item, minutes=45.0, effective_from=tomorrow)
    base.with_user(ppl.officer).action_propose()
    base.with_user(ppl.publisher).action_approve()
    assert base.state == "approved" and not base.applied_at
    assert item.standard_labour_time == pytest.approx(1.0)
    base.sudo()._guarded().write({"effective_from": fields.Date.context_today(item)})
    base.env["fix.srt.baseline"].sudo().cron_apply_due_baselines()
    assert base.applied_at and item.standard_labour_time == pytest.approx(0.75)


def test_calibration_baseline_needs_measured_evidence(odoo_env, ppl):
    item = _item(
        odoo_env, ppl.officer, item_type="labour", repair_level="l1", standard_labour_time=1.0
    )
    with pytest.raises(ValidationError, match="measured"), odoo_env.cr.savepoint():
        _baseline(odoo_env, ppl.officer, item, source="calibration")


def test_baseline_belongs_to_an_operation_not_a_part(odoo_env, ppl):
    part = _item(odoo_env, ppl.officer, item_type="part")
    with pytest.raises(ValidationError, match="not to a part"), odoo_env.cr.savepoint():
        _baseline(odoo_env, ppl.officer, part)


# --- fix.part.crossref (FR-CAT-030) -------------------------------------------


def test_part_crossref_rules(odoo_env, ppl):
    a = _item(odoo_env, ppl.officer, item_type="part")
    b = _item(odoo_env, ppl.officer, item_type="part")
    svc = _item(odoo_env, ppl.officer, item_type="service")
    X = odoo_env["fix.part.crossref"]
    with pytest.raises(AccessError), odoo_env.cr.savepoint():
        X.with_user(ppl.clerk).create(
            {"part_item_id": a.id, "alt_item_id": b.id, "relation_type": "oem_equivalent"}
        )
    with pytest.raises(ValidationError, match="quality note"), odoo_env.cr.savepoint():
        X.with_user(ppl.officer).create(
            {"part_item_id": a.id, "alt_item_id": b.id, "relation_type": "aftermarket"}
        )
    with pytest.raises(ValidationError, match="service item"), odoo_env.cr.savepoint():
        X.with_user(ppl.officer).create(
            {"part_item_id": a.id, "alt_item_id": svc.id, "relation_type": "oem_equivalent"}
        )
    with pytest.raises((ValidationError, psycopg2.IntegrityError)), odoo_env.cr.savepoint():
        X.with_user(ppl.officer).create(
            {"part_item_id": a.id, "alt_item_id": a.id, "relation_type": "oem_equivalent"}
        )
    xref = X.with_user(ppl.officer).create(
        {
            "part_item_id": a.id,
            "alt_item_id": b.id,
            "relation_type": "aftermarket",
            "direction": "two_way",
            "quality_note": "Aftermarket panel: 6-month warranty, lower brightness.",
        }
    )
    assert X.search([("part_item_id", "=", a.id)]) == xref and "<->" in xref.display_name


# --- fix.catalogue.publication (FR-CAT-044) -----------------------------------


def test_channel_publication_is_a_versioned_snapshot(odoo_env, ppl):
    _decided(_item(odoo_env, ppl.officer, item_type="part"))
    P = odoo_env["fix.catalogue.publication"]
    for user in (ppl.clerk, ppl.officer):
        with pytest.raises(AccessError), odoo_env.cr.savepoint():
            P.with_user(user).create({"channel": "pos"})
    first = P.with_user(ppl.publisher).create({"channel": "pos", "note": "Counter list"})
    second = P.with_user(ppl.publisher).create({"channel": "pos"})
    sellable = odoo_env["fix.catalogue.item"].search_count(
        [("state", "in", ["approved", "published", "restricted"])]
    )
    assert second.version == first.version + 1
    assert first.item_count == sellable and len(first.content_hash) == 64
    assert 0.0 <= first.completeness_pct <= 100.0
    pub = first.with_user(ppl.publisher)
    pub.write({"note": "Counter list, Nov", "channel": "pos"})  # full-form resend passes
    with pytest.raises(UserError, match="snapshot"), odoo_env.cr.savepoint():
        pub.write({"channel": "portal"})
    with pytest.raises(UserError, match="cannot be set directly"), odoo_env.cr.savepoint():
        pub.write({"item_count": first.item_count + 1000})
    with pytest.raises(UserError, match="never deleted"), odoo_env.cr.savepoint():
        pub.unlink()


def test_incomplete_customer_facing_publication_is_refused(odoo_env, ppl):
    item = _item(odoo_env, ppl.officer, item_type="part")
    item.sudo()._guarded().write({"state": "published", "is_published": True, "category_id": False})
    with pytest.raises(UserError, match="FR-CAT-044"), odoo_env.cr.savepoint():
        odoo_env["fix.catalogue.publication"].with_user(ppl.publisher).create({"channel": "portal"})
