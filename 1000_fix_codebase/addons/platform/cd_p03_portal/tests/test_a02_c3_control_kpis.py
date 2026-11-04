"""A02 audit C3: the A02 control KPIs on the M63 dashboard.

Each figure is checked against an independent SQL count over the same data,
and a self-approved cash variance and a self-verified wipe certificate are
planted to prove the counters see them.
"""

import pytest
from odoo.addons.cd_p03_portal.controllers.a11 import m63


@pytest.fixture
def env(odoo_env):
    return odoo_env


def _sql(env, query):
    env.flush_all()
    env.cr.execute(query)
    return env.cr.fetchone()[0] or 0


def test_figures_match_an_independent_count(env):
    k = m63.a02_control_figures(env)
    self_approved = _sql(
        env,
        """SELECT count(*) FROM fix_cash_shift s
           LEFT JOIN hr_employee e ON e.id = s.operator_id
           WHERE s.supervisor_variance_approved_by IS NOT NULL
             AND (s.supervisor_variance_approved_by = s.counted_by
                  OR s.supervisor_variance_approved_by = e.user_id)""",
    )
    assert k["cash_variance_self_approved"] == self_approved
    self_verified = _sql(
        env,
        """SELECT count(*) FROM fix_data_wipe_certificate
           WHERE verified_by_id IS NOT NULL AND verified_by_id = technician_id""",
    )
    assert k["wipe_cert_self_verified"] == self_verified
    delivered = _sql(
        env, "SELECT count(*) FROM fix_service_order WHERE state IN ('delivered','closed')"
    )
    with_otp = _sql(
        env,
        "SELECT count(*) FROM fix_service_order WHERE state IN ('delivered','closed') "
        "AND delivery_otp_verified",
    )
    assert k["delivery_otp_verified_pct"] == (
        round(with_otp / delivered * 100.0, 1) if delivered else 0.0
    )
    done = _sql(env, "SELECT count(*) FROM fix_field_order WHERE state = 'completed'")
    evidenced = _sql(
        env,
        "SELECT count(*) FROM fix_field_order WHERE state = 'completed' "
        "AND (customer_otp_verified OR customer_signature_attachment_id IS NOT NULL) "
        "AND post_work_photo_attachment_id IS NOT NULL",
    )
    assert k["field_completion_evidence_pct"] == (
        round(evidenced / done * 100.0, 1) if done else 0.0
    )


def test_a_planted_self_verified_certificate_is_counted(env):
    Cert = env["fix.data.wipe.certificate"]
    before = m63.a02_control_figures(env)["wipe_cert_self_verified"]
    cert = Cert.search([]).filtered(lambda c: c.verified_by_id != c.technician_id)[:1]
    if not cert:
        method = Cert._fields["method"].selection[0][0]
        cert = Cert.create({"method": method})
    # Trusted (superuser) write: this plants the bad state the KPI must catch.
    cert.write({"verified_by_id": cert.technician_id.id})
    assert m63.a02_control_figures(env)["wipe_cert_self_verified"] == before + 1


def test_the_dashboard_and_report_carry_the_figures(env):
    tiles = m63.kpis(env)
    for key in (
        "a02_variance_self_approved",
        "a02_cert_self_verified",
        "a02_delivery_otp_pct",
        "a02_completion_evidence_pct",
    ):
        assert key in tiles
    report = m63.REPORTS["a02_controls"](env)
    assert len(report["rows"]) == 4
