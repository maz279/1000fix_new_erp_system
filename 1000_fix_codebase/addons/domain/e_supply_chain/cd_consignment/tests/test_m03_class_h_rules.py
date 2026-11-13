"""M03 class-H business rules (13 Nov 2026, owner chose to build them).

BRU-LOG-03: a high-value consignment is insured and countersigned by a
second person before dispatch. BRU-LOG-05/10: a restricted item travels only
with a rider or courier certified for it on the day.

``odoo_env`` (addons/conftest.py): the test DB, rolled back after every test.
"""

from datetime import date, datetime, timedelta

import pytest
from odoo.addons.cd_consignment.models.fix_logistics_controls import HIGH_VALUE_PARAM
from odoo.exceptions import AccessError, UserError, ValidationError

HUB = "cd_consignment.group_fix_logistics_hub"


@pytest.fixture
def m3(odoo_env):
    env = odoo_env
    env["ir.config_parameter"].sudo().set_param(HIGH_VALUE_PARAM, "50000")
    ou = env["operating.unit"].search([], limit=1)
    entity = env["fix.entity"].create(
        {"code": "M3CH", "legal_name": "M03 Class-H Entity", "company_id": env.company.id}
    )
    a, b = env["fix.branch"].create(
        [
            {
                "name": "M03 CH A",
                "code": "M3HA",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
            {
                "name": "M03 CH B",
                "code": "M3HB",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            },
        ]
    )
    hub = env.ref(HUB)
    users = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            [
                {
                    "name": "M03 CH Hub %s" % n,
                    "login": "m03ch_hub_%s@example.test" % n,
                    "group_ids": [(4, hub.id), (4, env.ref("base.group_user").id)],
                    "operating_unit_ids": [(4, ou.id)],
                    "default_operating_unit_id": ou.id,
                }
                for n in (1, 2)
            ]
        )
    )
    rider = env["hr.employee"].create({"name": "M03 CH Rider"})

    def leg(**kw):
        vals = {
            "consignment_type": "branch_transfer",
            "scheduled_date": datetime.now(),
            "origin_branch_id": a.id,
            "dest_branch_id": b.id,
            "operating_unit_id": ou.id,
            "declared_value_bdt": 12000.0,
        }
        vals.update(kw)
        return env["fix.consignment"].create(vals)

    return env, users, rider, leg


# --- BRU-LOG-03 ------------------------------------------------------------


def test_a_low_value_leg_needs_no_countersignature(m3):
    env, (u1, _u2), _rider, leg = m3
    rec = leg()
    assert not rec.high_value
    rec.with_user(u1).action_confirm()
    assert rec.state == "confirmed"
    with pytest.raises(UserError, match="below the high-value threshold"):
        leg().with_user(u1).action_countersign_dispatch()


def test_a_high_value_leg_is_insured_and_countersigned_by_someone_else(m3):
    env, (u1, u2), _rider, leg = m3
    rec = leg(declared_value_bdt=80000.0)
    assert rec.high_value
    with pytest.raises(UserError, match="insurance"):
        rec.with_user(u1).action_confirm()
    rec.insurance_flag = True
    with pytest.raises(UserError, match="countersign"):
        rec.with_user(u1).action_confirm()
    rec.with_user(u2).action_countersign_dispatch()
    assert rec.dispatch_countersigned_by_id == u2
    assert rec.dispatch_countersigned_value == 80000.0
    with pytest.raises(UserError, match="different person"):
        rec.with_user(u2).action_confirm()
    rec.with_user(u1).action_confirm()
    assert rec.state == "confirmed"


def test_a_value_changed_after_countersigning_needs_a_new_signature(m3):
    env, (u1, u2), _rider, leg = m3
    rec = leg(declared_value_bdt=80000.0, insurance_flag=True)
    rec.with_user(u2).action_countersign_dispatch()
    rec.declared_value_bdt = 95000.0
    with pytest.raises(UserError, match="countersign"):
        rec.with_user(u1).action_confirm()


def test_the_countersignature_cannot_be_written_directly(m3):
    env, (u1, _u2), _rider, leg = m3
    rec = leg(declared_value_bdt=80000.0)
    assert "dispatch_countersigned_by_id" in rec._fix_guarded_fields()
    with pytest.raises((AccessError, UserError, ValidationError)):
        rec.with_user(u1).write({"dispatch_countersigned_by_id": u1.id})


# --- BRU-LOG-05 / 10 -------------------------------------------------------


def test_a_restricted_item_names_its_class(m3):
    env, _users, _rider, leg = m3
    with pytest.raises(ValidationError, match="name its class"):
        leg(restricted_item=True)


def test_an_uncertified_rider_cannot_take_a_restricted_item(m3):
    env, _users, rider, leg = m3
    with pytest.raises(ValidationError, match="not certified"):
        leg(restricted_item=True, restricted_item_class="lithium_battery", rider_id=rider.id)


def test_a_certified_rider_can_until_the_certification_lapses(m3):
    env, (u1, _u2), rider, leg = m3
    cert = env["fix.rider.certification"].create(
        {
            "employee_id": rider.id,
            "item_class": "lithium_battery",
            "certificate_ref": "DG-0001",
            "issued_on": date.today() - timedelta(days=30),
            "valid_until": date.today() + timedelta(days=30),
        }
    )
    rec = leg(restricted_item=True, restricted_item_class="lithium_battery", rider_id=rider.id)
    # another class is not covered
    with pytest.raises(ValidationError, match="not certified"):
        rec.restricted_item_class = "refrigerant"
    rec.restricted_item_class = "lithium_battery"
    # a lapsed certification stops the dispatch
    cert.valid_until = date.today() - timedelta(days=1)
    with pytest.raises(UserError, match="not certified"):
        rec.with_user(u1).action_confirm()


def test_a_courier_needs_a_valid_certification(m3):
    env, _users, _rider, leg = m3
    partner = env["fix.courier.partner"].create({"name": "M03 CH Courier", "code": "M3HC"})
    with pytest.raises(ValidationError, match="restricted-item certification"):
        leg(
            restricted_item=True,
            restricted_item_class="refrigerant",
            courier_partner_id=partner.id,
        )
    partner.write(
        {
            "restricted_item_certified": True,
            "restricted_cert_valid_until": date.today() + timedelta(days=90),
        }
    )
    rec = leg(
        restricted_item=True, restricted_item_class="refrigerant", courier_partner_id=partner.id
    )
    assert rec.courier_partner_id == partner


def test_a_certification_cannot_expire_before_it_is_issued(m3):
    env, _users, rider, _leg = m3
    with pytest.raises(ValidationError, match="expire before"):
        env["fix.rider.certification"].create(
            {
                "employee_id": rider.id,
                "item_class": "refrigerant",
                "certificate_ref": "DG-0002",
                "issued_on": date.today(),
                "valid_until": date.today() - timedelta(days=1),
            }
        )


def test_dispatch_evidence_is_fixed_once_the_leg_moves(m3):
    env, (u1, _u2), _rider, leg = m3
    rec = leg()
    rec.with_user(u1).action_confirm()
    rec.with_user(u1).action_start_transit()
    with pytest.raises(UserError, match="cannot be changed"):
        rec.with_user(u1).write({"insurance_flag": True})
