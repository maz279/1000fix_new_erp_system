from datetime import date

import pytest
from odoo.exceptions import UserError, ValidationError


def _get_or_create_op_unit(env):
    op_unit = env["operating.unit"].search([], limit=1)
    if not op_unit:
        op_unit = env["operating.unit"].create(
            {
                "name": "Main Operating Unit",
                "code": "MOU",
                "company_id": env.company.id,
            }
        )
    return op_unit


def _get_or_create_branch(env):
    branch = env["fix.branch"].search([], limit=1)
    if not branch:
        op_unit = _get_or_create_op_unit(env)
        entity = env["fix.entity"].search([], limit=1)
        if not entity:
            entity = env["fix.entity"].create(
                {
                    "legal_name": "1000FiX Group Ltd",
                    "code": "GRP",
                    "company_id": env.company.id,
                    "operating_unit_id": op_unit.id,
                }
            )
        branch = env["fix.branch"].create(
            {
                "name": "Dhaka Hub",
                "code": "DHK-HUB",
                "entity_id": entity.id,
                "operating_unit_id": op_unit.id,
            }
        )
    return branch


def test_flaw_01_1_settlement_delivery_gate(odoo_env):
    env = odoo_env
    customer = env["res.partner"].create({"name": "Test Cust M01"})
    branch = _get_or_create_branch(env)

    brand = env["fix.brand"].create({"name": "TestBrand M01", "code": "TBR01"})
    device_model = env["fix.device.model"].create({"name": "TestModel 10", "brand_id": brand.id})
    device = env["fix.device"].create(
        {
            "device_model_id": device_model.id,
            "owner_id": customer.id,
            "serial_number": "SN-M01-TEST",
        }
    )

    order = env["fix.service.order"].create(
        {
            "device_id": device.id,
            "customer_id": customer.id,
            "branch_id": branch.id,
            "service_type": "walk_in",
            "order_category": "standard",
            "fault_description": "Screen replacement",
        }
    )

    # Approved estimate with lines -> grand_total > 0
    estimate = env["fix.estimate"].create(
        {
            "order_id": order.id,
            "state": "approved",
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "description": "Screen replacement part",
                        "line_type": "part",
                        "quantity": 1.0,
                        "unit_price": 2000.0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "description": "Screen labour",
                        "line_type": "labour",
                        "quantity": 1.0,
                        "unit_price": 500.0,
                    },
                ),
            ],
        }
    )
    order.invalidate_recordset(["estimate_ids"])
    assert estimate.grand_total > 0

    # Direct gate check on order
    assert order.payment_settlement_state == "unpaid"
    with pytest.raises(UserError, match="FLAW-01.1 Financial Settlement Gate"):
        order._check_delivery_settlement_gate()

    # Set ready via DB update and test action_deliver
    env.cr.execute("UPDATE fix_service_order SET state = 'ready' WHERE id = %s", (order.id,))
    order.invalidate_recordset(["state"])
    assert order.state == "ready"

    with pytest.raises(UserError, match="FLAW-01.1 Financial Settlement Gate"):
        order.action_deliver()

    # Mark settled -> delivery succeeds
    order.action_mark_settled("INV-M01-001", estimate.grand_total)
    assert order.payment_settlement_state == "settled"
    order.action_deliver()
    assert order.state == "delivered"


def test_flaw_04_2_cash_shift_blind_count_and_variance(odoo_env):
    env = odoo_env
    branch = _get_or_create_branch(env)
    op_unit = _get_or_create_op_unit(env)
    operator = env["hr.employee"].create({"name": "Cashier M04"})

    shift = env["fix.cash.shift"].create(
        {
            "branch_id": branch.id,
            "operating_unit_id": op_unit.id,
            "company_id": env.company.id,
            "shift_date": date.today(),
            "shift_type": "morning",
            "operator_id": operator.id,
            "opening_float": 1000.0,
        }
    )

    # Simulate count with note denominations giving BDT 6300 (variance +5300 > 100 tolerance)
    shift.write(
        {
            "denom_1000_count": 5,  # 5000
            "denom_500_count": 2,  # 1000
            "denom_100_count": 3,  # 300 -> total 6300
        }
    )

    # A02 audit M04-11: the blind count no longer reveals the variance; the
    # gate is at reconcile, and the approval is stamped by Approve Variance.
    shift.action_submit_blind_count()
    assert shift.blind_count_submitted is True
    assert shift.closing_counted == 6300.0
    with pytest.raises(ValidationError, match="FLAW-04.2 Blind Cash Count Gate"):
        shift.action_reconcile()
    shift.action_approve_variance()
    assert shift.variance_approved_amount == 5300.0
    shift.action_reconcile()
    assert shift.state == "discrepancy"


def test_flaw_06_1_dual_custody_unsealing(odoo_env):
    env = odoo_env
    customer = env["res.partner"].create({"name": "Forensic Cust"})
    case = env["fix.data.recovery.case"].create(
        {
            "customer_id": customer.id,
            "media_type": "hdd",
            "residency_zone": "z4",
        }
    )

    unit = env["fix.data.media.unit"].create(
        {
            "case_id": case.id,
            "seal_number": f"BAG-SEAL-{case.id}-A02",
            "location": "z4_lab",
            "seal_state": "sealed",
        }
    )

    # Same user cannot be both technician and witness
    with pytest.raises(UserError, match="FLAW-06.1 Dual-Custody Gate"):
        unit.action_break_seal_with_witness(witness_user_id=env.uid)

    # Second witness user succeeds
    witness = env["res.users"].create(
        {"name": "Witness User", "login": f"witness_{case.id}@test.com"}
    )
    unit.action_break_seal_with_witness(witness_user_id=witness.id)
    assert unit.seal_state == "opened_in_lab"
    assert unit.witness_user_id.id == witness.id


def test_flaw_06_2_cleanroom_interlock_gate(odoo_env):
    env = odoo_env
    slot = env["fix.data.cleanroom.slot"].create(
        {
            "purpose": "head_swap",
            "iso_class": "iso_5",
            "start_at": "2026-10-31 04:00:00",
            "end_at": "2026-10-31 06:00:00",
            "particle_count_per_ft3": 250,  # Exceeds ISO Class 5 limit of 100
            "laminar_airflow_mps": 0.45,
        }
    )
    assert slot.interlock_passed is False
    with pytest.raises(UserError, match="FLAW-06.2 Cleanroom Interlock Gate"):
        slot.action_use()


def test_flaw_31_3_burn_in_duration_gate(odoo_env):
    env = odoo_env
    branch = _get_or_create_branch(env)
    workshop = env["fix.workshop"].search([], limit=1)
    if not workshop:
        workshop = env["fix.workshop"].create(
            {"name": "Central Workshop", "code": "CWS", "branch_id": branch.id}
        )
    tech = env["hr.employee"].create({"name": "Bench Tech M31"})
    bench = env["fix.workshop.bench"].create(
        {
            "workshop_id": workshop.id,
            "code": f"B-TEST-{tech.id}",
            "name": "ESD Bench",
            "name_bn": "ইএসডি বেঞ্চ",
            "repair_level": "l2",
            "is_esd_safe": True,
            "wrist_strap_mohm": 10.0,
            "worksurface_rtg_mohm": 100.0,
        }
    )

    job = env["fix.workshop.job"].create(
        {
            "workshop_id": workshop.id,
            "bench_id": bench.id,
            "technician_id": tech.id,
            "repair_level": "l2",
            "fault_description": "PMIC short circuit",
            "state": "burn_in",
            "burn_in_actual_minutes": 120.0,  # Less than 240 mins
        }
    )

    with pytest.raises(UserError, match="FLAW-31.3 Burn-In Gate"):
        job.action_pass_burn_in()

    # A02 audit M31-6: the minutes are measured from the burn-in start stamp
    from datetime import timedelta

    from odoo import fields

    job.burn_in_started_at = fields.Datetime.now() - timedelta(minutes=241)
    job.action_pass_burn_in()
    assert job.burn_in_passed is True
    assert job.state == "qc_pending"
