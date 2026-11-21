"""A02 pass 2 independent review (21 Nov 2026) - M31 Workshop.

B6  a job cancel never skips the supervisor and the reason by context;
P2  the bench never delivers by context; a supervisor never appoints
    himself to the receiving workshop (and its manager is matched as a
    user); a job in test with no protocol can be given one; a new bench is
    not ESD-verified.

Every control runs as a non-admin workshop user of the A02 P0 fixture
(``m31``). ``odoo_env`` rolls back.
"""

from odoo.exceptions import UserError

from . import test_a02_p0_m31 as a02
from ._m45_decided import calibrations_decided  # noqa: F401 - autouse fixture
from .test_a02r2_m31 import _in_repair, _ready

m31 = a02.m31
refused = a02.refused


# ============================================================ B6
def test_review_b6_a_context_key_does_not_skip_the_supervisor(m31):
    job = _in_repair(m31)
    with refused(m31.env, UserError, "role"):
        job.with_context(m31_ber_closing=True).action_cancel(reason="customer changed mind")
    with refused(m31.env, UserError, "why"):
        job.with_user(m31.supv).with_context(m31_ber_closing=True).action_cancel()
    assert job.sudo().state == "in_repair"
    # M01's cascade is trusted code (the superuser), with no context needed
    job.sudo().action_cancel()
    assert job.sudo().state == "cancelled"


# ============================================================ P2 deliver
def test_review_p2_a_context_key_does_not_let_the_bench_deliver(m31):
    so = m31.order()
    a02._approved_estimate(m31, so, 3000.0)
    job = _ready(m31, m31.job(so=so))
    job.action_release()
    with refused(m31.env, UserError, "front desk"):
        job.with_context(m31_order_delivered=True).action_deliver()
    assert job.sudo().state == "released"


# ============================================================ P2 receiving workshop
def test_review_p2_a_supervisor_does_not_appoint_himself_to_the_receiving_workshop(m31):
    env = m31.env
    job = m31.job()
    dst = env["fix.workshop"].create(
        {"code": "WS-RV-%d" % job.id, "name": "RV Depot", "name_bn": "ডিপো"}
    )
    supv_emp = env["hr.employee"].search([("user_id", "=", m31.supv.id)], limit=1)
    with refused(env, UserError, "himself"):
        dst.with_user(m31.supv).write({"supervisor_user_ids": [(4, m31.supv.id)]})
    with refused(env, UserError, "himself"):
        dst.with_user(m31.supv).write({"manager_id": supv_emp.id})
    assert not dst.supervisor_user_ids and not dst.manager_id
    t = (
        env["fix.workshop.transfer"]
        .with_user(m31.tech)
        .create({"job_id": job.id, "to_workshop_id": dst.id, "reason": "BGA"})
    )
    with refused(env, UserError, "receiving workshop"):
        t.with_user(m31.supv).action_confirm()
    # another manager appoints him; as the workshop's manager he accepts it
    other, _emp = a02._user(env, "supv2", [env.ref("cd_workshop.group_fix_workshop_manager")])
    dst.with_user(other).write({"manager_id": supv_emp.id})
    t.with_user(m31.supv).action_confirm()
    assert t.state == "in_transit"


# ============================================================ P2 protocol
def test_review_p2_a_job_in_test_with_no_protocol_gets_one(m31):
    job = _in_repair(m31)
    job.sudo()._guarded().write({"state": "qc_pending"})
    assert not job.protocol_id
    assert "protocol_id" not in job._fix_form_locked_fields()
    Proto = m31.env["fix.workshop.test.protocol"]
    first, second = (
        Proto.create(
            {
                "code": "RV-%d-%s" % (job.id, tag),
                "name": "RV check %s" % tag,
                "step_ids": [(0, 0, {"name": "Boots", "has_limits": False})],
            }
        )
        for tag in ("A", "B")
    )
    job.write({"protocol_id": first.id})
    assert job.protocol_id == first
    assert "protocol_id" in job._fix_form_locked_fields()
    with refused(m31.env, UserError, "protocol is fixed"):
        job.write({"protocol_id": second.id})


# ============================================================ P2 ESD
def test_review_p2_a_new_bench_is_not_esd_verified(m31):
    bench = m31.env["fix.workshop.bench"].create(
        {
            "workshop_id": m31.workshop.id,
            "code": "B-RV-%d" % m31.workshop.id,
            "name": "RV",
            "name_bn": "আরভি",
            "repair_level": "l2",
        }
    )
    assert not bench.esd_last_verified_date and not bench.esd_compliant_today
    bench.with_user(m31.tech).action_log_daily_esd(5.0, 50.0)
    assert bench.esd_compliant_today


# ============================================================ round 3: FR-WSR-034
def test_review_a_context_key_does_not_start_burn_in_off_the_station(m31):
    m31.env["fix.workshop.burnin.station"].create(
        {"workshop_id": m31.workshop.id, "code": "BI-RV", "name": "Rack RV", "capacity": 1}
    )
    job = a02._l2_in_repair(m31)
    with refused(m31.env, UserError, "stations"):
        job.with_user(m31.tech).with_context(m31_burnin_station=True).action_start_burn_in()
    assert job.sudo().state == "in_repair"
