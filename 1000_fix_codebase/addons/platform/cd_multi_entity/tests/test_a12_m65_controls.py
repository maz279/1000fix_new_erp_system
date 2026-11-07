"""A12 M65 controls on the live ORM (`odoo_env`, rolled back per test):
the payment-gateway lifecycle (P1-4), the VAT statutory-day clamp, the
nil-return guards (M65) and the release-to-ITSM-change gate (D8).

Working/A12_Workflow_and_Approval_Report.md §6, M65.md / M64.md:

- a gateway goes live only through a ROUTED M63 decision of the coded
  approver group; every transition writes a row in the security audit chain;
  checkout calls assert_live_for_checkout() and is refused on anything but
  an active gateway in live mode;
- the VAT statutory day clamps to the month's last day (NBR month-end rule);
- a nil return is generated only for a measured-empty period, and its
  evidence fields are never typed;
- a platform release ships an approved (or implemented) ITSM change.

The superuser only builds fixtures; decisions are taken by non-admin users
holding exactly the coded groups.
"""

import contextlib
import json
from datetime import date

import pytest
from odoo.addons.cd_workflow_engine.tests.approval_helpers import (
    approve_via_inbox,
    assigned,
)
from odoo.exceptions import AccessError, UserError, ValidationError

ADMIN = "cd_entity_config.group_platform_admin"
GATEWAY_APPROVER = "cd_entity_config.group_gateway_activation_approver"
ACCOUNT_USER = "account.group_account_user"
REFUSED = (UserError, ValidationError, AccessError)


@contextlib.contextmanager
def _rejects(env, exc, match):
    with pytest.raises(exc, match=match) as info, env.cr.savepoint():
        yield info


@pytest.fixture
def make_user(odoo_env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [odoo_env.ref("base.group_user").id] + [odoo_env.ref(x).id for x in xmlids]
        return (
            odoo_env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "A12 M65 Probe %d" % counter["n"],
                    "login": "a12.m65.probe.%d@test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


@pytest.fixture
def world(odoo_env, make_user):
    return {
        "admin": make_user(ADMIN),
        "approver": make_user(GATEWAY_APPROVER),
        "clerk": make_user(),
    }


def _gateway(odoo_env, user, tag, **vals):
    base = {
        "provider": "bkash-a12-%s" % tag,
        "country_code": "BD",
        "mode": "sandbox",
        "currencies": "BDT",
        "credential_ref": "vault://test/%s" % tag,
    }
    base.update(vals)
    return odoo_env["fix.payment.gateway"].with_user(user).create(base)


def _audit_rows(odoo_env, event, gateway):
    return (
        odoo_env["fix.security.audit"]
        .sudo()
        .search(
            [
                ("event", "=", event),
                ("object_ref", "=", "fix.payment.gateway,%d" % gateway.id),
            ]
        )
    )


# --- P1-4: the gateway lifecycle is routed, audited and checkout-gated --------


def test_activation_is_refused_as_a_button(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "btn")
    with _rejects(odoo_env, UserError, match="approver's inbox"):
        gw.with_user(world["admin"]).action_activate()
    with _rejects(odoo_env, UserError, match="approver's inbox"):
        gw.with_user(world["approver"]).action_activate()
    assert gw.state == "draft"


def test_checkout_refuses_a_draft_gateway(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "draft")
    with _rejects(odoo_env, UserError, match="storefront checkout refused"):
        gw.assert_live_for_checkout("storefront checkout")


def test_activation_routes_to_the_coded_approver_group(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "route")
    gw.with_user(world["admin"]).action_request_approval(justification="BD launch")
    assert world["admin"] not in assigned(gw)
    assert world["approver"] in assigned(gw)


def test_the_full_two_stage_go_live_is_audited_and_checkout_gated(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "golive")

    # Stage 1: draft -> active (still sandbox).
    approve_via_inbox(gw, world["approver"], requester=world["admin"])
    assert gw.state == "active" and gw.mode == "sandbox"
    assert _audit_rows(odoo_env, "payment.gateway_activated", gw)
    with _rejects(odoo_env, UserError, match="sandbox mode"):
        gw.assert_live_for_checkout("storefront checkout")

    # Stage 2: active/sandbox -> live, routed again.
    gw.with_user(world["admin"]).action_request_approval(justification="go-live after UAT")
    approve_via_inbox(gw, world["approver"], requester=world["admin"])
    assert gw.state == "active" and gw.mode == "live"
    assert _audit_rows(odoo_env, "payment.gateway_gone_live", gw)

    # Checkout passes on the live rail, and the country contract holds.
    assert gw.assert_live_for_checkout("storefront checkout") is True
    with _rejects(odoo_env, UserError, match="not IN"):
        gw.assert_live_for_checkout("storefront checkout", country_code="IN")


def test_suspension_needs_a_reason_and_the_authority(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "suspend")
    approve_via_inbox(gw, world["approver"], requester=world["admin"])
    # go live first so the rail is real
    gw.with_user(world["admin"]).action_request_approval()
    approve_via_inbox(gw, world["approver"], requester=world["admin"])

    with _rejects(odoo_env, UserError, match="Activation Approver' role"):
        gw.with_user(world["clerk"]).action_suspend(reason="probe")
    with _rejects(odoo_env, UserError, match="reason"):
        gw.with_user(world["admin"]).action_suspend()
    gw.with_user(world["admin"]).action_suspend(reason="issuer outage")
    assert gw.state == "suspended"
    assert _audit_rows(odoo_env, "payment.gateway_suspended", gw)
    with _rejects(odoo_env, UserError, match="suspended"):
        gw.assert_live_for_checkout("storefront checkout")


def test_reactivation_after_suspension_is_routed_again(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "react")
    approve_via_inbox(gw, world["approver"], requester=world["admin"])
    gw.with_user(world["admin"]).action_suspend(reason="planned maintenance")
    with _rejects(odoo_env, UserError, match="approver's inbox"):
        gw.with_user(world["admin"]).action_activate()
    approve_via_inbox(gw, world["approver"], requester=world["admin"])
    assert gw.state == "active"
    assert _audit_rows(odoo_env, "payment.gateway_reactivated", gw)


def test_credential_rotation_only_points_at_the_vault(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "rotate")
    with _rejects(odoo_env, UserError, match="Activation Approver' role"):
        gw.with_user(world["clerk"]).action_rotate_credential(
            new_ref="vault://test/rotate", reason="probe"
        )
    with _rejects(odoo_env, UserError, match="vault"):
        gw.with_user(world["admin"]).action_rotate_credential(
            new_ref="file:///etc/passwd", reason="probe"
        )
    with _rejects(odoo_env, UserError, match="reason"):
        gw.with_user(world["admin"]).action_rotate_credential(new_ref="vault://test/rotate")
    gw.with_user(world["admin"]).action_rotate_credential(
        new_ref="vault://test/rotate-2", reason="quarterly rotation"
    )
    assert gw.credential_ref == "vault://test/rotate-2"
    assert _audit_rows(odoo_env, "payment.gateway_credential_rotated", gw)


def test_gateway_state_and_credentials_are_never_typed(odoo_env, world):
    gw = _gateway(odoo_env, world["admin"], "guard")
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        gw.with_user(world["admin"]).write({"state": "active"})
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        gw.with_user(world["admin"]).write({"credential_ref": "vault://test/forged"})
    assert gw.state == "draft" and gw.credential_ref == "vault://test/guard"


# --- M65: the VAT statutory day clamps to the month's end ---------------------


def _entity(odoo_env, **vals):
    # fix.entity.company_id is required and UNIQUE per res.company, so each
    # probe entity gets its own throwaway company.
    seq = odoo_env["fix.entity"].search_count([])
    company = odoo_env["res.company"].create({"name": "A12 VAT Co %d" % seq})
    base = {
        "code": "A12-%d" % seq,
        "legal_name": "A12 VAT Probe",
        "statutory_calendar_rule": "strict_calendar_day",
        "company_id": company.id,
    }
    base.update(vals)
    return odoo_env["fix.entity"].sudo().create(base)


def test_a_31st_due_day_clamps_to_short_months(odoo_env):
    entity = _entity(odoo_env, vat_statutory_day=31)
    assert entity.get_vat_return_due_date(2026, 3) == date(2026, 4, 30)  # April has 30
    assert entity.get_vat_return_due_date(2026, 1) == date(2026, 2, 28)  # February
    assert entity.get_vat_return_due_date(2026, 4) == date(2026, 5, 31)  # May keeps the 31st


def test_an_unset_day_falls_back_to_the_statutory_15th(odoo_env):
    entity = _entity(odoo_env, vat_statutory_day=0)
    assert entity.get_vat_return_due_date(2026, 2) == date(2026, 3, 15)
    entity2 = _entity(odoo_env, vat_statutory_day=False)
    assert entity2.get_vat_return_due_date(2026, 2) == date(2026, 3, 15)


def test_the_mushak_rule_rolls_a_weekend_due_day(odoo_env):
    entity = _entity(
        odoo_env, vat_statutory_day=15, statutory_calendar_rule="mushak_next_working_day"
    )
    due = entity.get_vat_return_due_date(2026, 2)  # 2026-03-15 is a Sunday
    assert due == date(2026, 3, 15)
    # 2026-05-15 is a Friday: rolls to Sunday the 17th
    assert entity.get_vat_return_due_date(2026, 4) == date(2026, 5, 17)


def test_a_day_beyond_the_longest_month_is_refused(odoo_env):
    # Odoo 19 runs python constrains AFTER the INSERT, so the refusal is the
    # database CHECK (fix_entity_vat_day_range) — either layer refuses it.
    from psycopg2.errors import CheckViolation

    with _rejects(odoo_env, (*REFUSED, CheckViolation), match="vat_day_range|VAT statutory day"):
        _entity(odoo_env, vat_statutory_day=32)


# --- M65: nil returns are measured, guarded evidence --------------------------


def _nil_generator(odoo_env, user, entity, year=2020, month=1):
    return (
        odoo_env["fix.nil.return.generator"]
        .with_user(user)
        .create(
            {
                "entity_id": entity.id,
                "period_year": year,
                "period_month": month,
            }
        )
    )


@pytest.fixture
def nil_world(odoo_env, make_user):
    seq = odoo_env["fix.entity"].search_count([])
    company = odoo_env["res.company"].create({"name": "A12 Nil Co %d" % seq})
    entity = (
        odoo_env["fix.entity"]
        .sudo()
        .create(
            {
                "code": "A12-NIL-%d" % seq,
                "legal_name": "A12 Nil Return Co",
                "incorporation_date": date(2019, 1, 1),
                "bin_number": "1234567890123",
                "tin_number": "123456789012",
                "vat_statutory_day": 15,
                "company_id": company.id,
            }
        )
    )
    officer = make_user(ACCOUNT_USER)
    # AS-03 isolation: fix.entity rows are visible only inside the user's
    # allowed companies, so the compliance officer joins the probe company.
    officer.company_ids = [(4, company.id)]
    return {"entity": entity, "officer": officer}


def test_a_measured_empty_period_verifies_and_generates_the_packs(odoo_env, nil_world):
    gen = _nil_generator(odoo_env, nil_world["officer"], nil_world["entity"])
    gen.with_user(nil_world["officer"]).action_verify_eligibility()
    assert gen.state == "verified"
    assert gen.transaction_count == 0 and gen.transactions_counted_at
    assert gen.eligible_for_nil_return

    gen.with_user(nil_world["officer"]).action_generate_nil_packs()
    assert gen.state == "generated"
    mushak = json.loads(gen.mushak_9_1_nil_payload)
    assert (
        mushak["submission_type"] == "NIL" and mushak["part_3_supplies"]["total_sales_value"] == 0.0
    )
    assert json.loads(gen.tds_nil_payload)["is_nil_declaration"] is True


def test_generation_without_verification_is_refused(odoo_env, nil_world):
    gen = _nil_generator(odoo_env, nil_world["officer"], nil_world["entity"])
    with _rejects(odoo_env, REFUSED, match="verified"):
        gen.with_user(nil_world["officer"]).action_generate_nil_packs()
    assert gen.state == "draft"


def test_registration_numbers_are_required_before_packs(odoo_env, nil_world):
    nil_world["entity"].sudo().write({"bin_number": False})
    gen = _nil_generator(odoo_env, nil_world["officer"], nil_world["entity"])
    gen.with_user(nil_world["officer"]).action_verify_eligibility()
    with _rejects(odoo_env, REFUSED, match="BIN"):
        gen.with_user(nil_world["officer"]).action_generate_nil_packs()
    assert gen.state == "verified"


def test_submission_needs_the_real_nbr_acknowledgement(odoo_env, nil_world):
    gen = _nil_generator(odoo_env, nil_world["officer"], nil_world["entity"])
    gen.with_user(nil_world["officer"]).action_verify_eligibility()
    gen.with_user(nil_world["officer"]).action_generate_nil_packs()
    with _rejects(odoo_env, REFUSED, match="acknowledgement"):
        gen.with_user(nil_world["officer"]).action_submit_to_nbr()
    # the officer keys NBR's slip number: that field stays open by design
    gen.with_user(nil_world["officer"]).write({"filing_reference": "NBR-2020-0001"})
    # A08 M19-12: a nil return is recorded only for a closed and locked period
    gen.entity_id.company_id.sudo().fiscalyear_lock_date = "2020-12-31"
    gen.with_user(nil_world["officer"]).action_submit_to_nbr()
    assert gen.state == "acknowledged"


def test_nil_return_evidence_is_never_typed(odoo_env, nil_world):
    gen = _nil_generator(odoo_env, nil_world["officer"], nil_world["entity"])
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        gen.with_user(nil_world["officer"]).write({"state": "acknowledged"})
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        gen.with_user(nil_world["officer"]).write({"mushak_9_1_nil_payload": '{"forged": true}'})
    assert gen.state == "draft" and not gen.mushak_9_1_nil_payload


# --- D8: a release ships an approved ITSM change -------------------------------


def _release(odoo_env, tag, change=None):
    # A12 finish E7: a release names its target environment before it ships.
    target = (
        odoo_env["fix.platform.environment"]
        .sudo()
        .create(
            {
                "name": "A12 target %s" % tag,
                "kind": "production",
                "base_url": "https://a12.example",
            }
        )
    )
    vals = {
        "name": "A12 release %s" % tag,
        "version": "1.%d.0" % odoo_env["fix.platform.release"].search_count([]),
        "rollback_plan": "roll back to the previous tag",
        "environment_id": target.id,
    }
    if change is not None:
        vals["itsm_change_id"] = change.id
    return odoo_env["fix.platform.release"].sudo().create(vals)


def _itsm_change(odoo_env, tag, state=None):
    change = odoo_env["fix.itsm.change"].sudo().create({"title": "A12 change %s" % tag})
    if state:
        change.sudo().write({"state": state})
    return change


def test_a_release_without_a_change_is_refused(odoo_env):
    rel = _release(odoo_env, "nochange")
    with _rejects(odoo_env, REFUSED, match="ITSM change"):
        rel.sudo().action_release()
    assert rel.state == "planned"


def test_a_release_with_a_draft_change_is_refused(odoo_env):
    change = _itsm_change(odoo_env, "draft")
    rel = _release(odoo_env, "draftchange", change)
    with _rejects(odoo_env, REFUSED, match="approved or implemented"):
        rel.sudo().action_release()
    assert rel.state == "planned"


@pytest.mark.parametrize("state", ["approved", "implemented"])
def test_a_release_ships_an_approved_or_implemented_change(odoo_env, state):
    change = _itsm_change(odoo_env, state, state)
    rel = _release(odoo_env, state, change)
    rel.sudo().action_release()
    assert rel.state == "released" and rel.released_on


def test_the_release_state_is_never_typed(odoo_env, world):
    rel = _release(odoo_env, "guard")
    with _rejects(odoo_env, UserError, match="cannot be set directly"):
        rel.with_user(world["admin"]).write({"state": "released"})
    assert rel.state == "planned"
