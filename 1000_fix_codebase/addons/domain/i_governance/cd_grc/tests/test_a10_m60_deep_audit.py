# A10 deep audit (2026-11-22) — M60 fixes landed from the five-auditor sweep:
#
# A3-F02  a HIGH residual is RECORDABLE (pending acceptance) — the acceptance
#         constraint now bites on the accepted state, not on the assessment;
#         reopening clears the acceptance stamps so a stale acceptor can never
#         stand next to a re-assessed residual.
# A3-F01  the SoD governance register derives from the controls M29 enforces
#         (fix.sod.control), DoA-register style: upsert by source control,
#         waivers survive rebuilds, group-pair controls are counted not dropped.
# A3-F04  legitimate_interest is not offered as a lawful basis (PDPA 2026),
#         and the DSR 30-day clock notifies the Compliance Officers once.
#
# Every control is exercised as NON-ADMIN users holding only the role groups
# each step needs; the odoo_env fixture rolls everything back.
import itertools

import pytest
from odoo import fields
from odoo.exceptions import UserError, ValidationError

RISK_OWNER = "cd_grc.group_grc_risk_owner"
OFFICER = "cd_grc.group_grc_officer"

_SEQ = itertools.count(1)


def _user(env, name, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 DA %s %d" % (name, n),
                "login": "a10da.%s.%d@a10.test" % (name.replace(" ", "").lower(), n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


@pytest.fixture
def m(odoo_env):
    env = odoo_env
    x = lambda: None  # noqa: E731  (tiny namespace)
    x.env = env
    x.clerk = _user(env, "clerk")
    x.officer = _user(env, "officer", [OFFICER])
    x.owner = _user(env, "owner", [RISK_OWNER])
    x.owner_emp = env["hr.employee"].create({"name": "A10 DA Risk Owner", "user_id": x.owner.id})
    return x


# ------------------------------------------------- A3-F02: the residual deadlock
def test_a_high_residual_is_recordable_pending_acceptance(m):
    """5×4 = 20 lands in the HIGH band. The old constraint fired at assessment
    time (high band + no acceptor), which made the assessment itself
    unrecordable — the acceptance action presupposes it. Now the assessment
    records, the register shows it pending, and only the ACCEPTED state needs
    the named acceptor."""
    env = m.env
    env["fix.risk.appetite"].create({"category": "operational", "max_residual_score": 25})
    rec = env["fix.risk.register"].create(
        {
            "name": "DA high residual",
            "category": "operational",
            "likelihood": "5",
            "impact": "5",
            # the residual (20) sits below the inherent (25): the reduction
            # claim needs its grounding control
            "control_ids": [
                (0, 0, {"name": "DA mitigating control", "control_type": "preventive"})
            ],
        }
    )
    # the assessment itself is the act that used to be impossible
    rec.write({"residual_likelihood": "5", "residual_impact": "4"})
    rec.invalidate_recordset()
    assert rec.residual_score == 20 and rec.residual_band == "high"
    assert rec.state == "open" and not rec.residual_accepted_by_id
    # within the stated appetite (25): the owner's own signature completes it
    rec.with_user(m.owner).action_accept_residual()
    rec.invalidate_recordset()
    assert rec.state == "accepted"
    assert rec.residual_accepted_by_id == m.owner_emp
    # the accepted state without an acceptor is still refused — typing the
    # state is guarded, and the constraint is the belt behind the braces
    with pytest.raises(UserError), env.cr.savepoint():
        rec._guarded().write({"residual_accepted_by_id": False})


def test_reopening_ends_the_old_acceptance(m):
    """A closed risk reopens without the old acceptor: a stale acceptance
    stamp must never survive into a new assessment cycle."""
    env = m.env
    env["fix.risk.appetite"].create({"category": "operational", "max_residual_score": 25})
    rec = env["fix.risk.register"].create(
        {
            "name": "DA reopen clears acceptance",
            "category": "operational",
            "likelihood": "4",
            "impact": "4",
            "residual_likelihood": "2",
            "residual_impact": "3",
            "control_ids": [(0, 0, {"name": "DA grounding control", "control_type": "preventive"})],
        }
    )
    rec.with_user(m.owner).action_accept_residual()
    rec.invalidate_recordset()
    assert rec.residual_accepted_by_id == m.owner_emp
    rec.with_user(m.owner).action_close()
    rec.with_user(m.owner).action_reopen()
    rec.invalidate_recordset()
    assert rec.state == "open"
    assert not rec.residual_accepted_by_id and not rec.residual_accepted_on


# ------------------------------------- A3-F01: the derived SoD governance register
def _role(env, name):
    n = next(_SEQ)
    # the role register enforces its own R-nn code format
    return env["fix.role"].sudo().create({"name": name, "code": "R-%02d" % (900 + n)})


def test_sod_register_derives_from_the_enforced_controls(m):
    env = m.env
    role_a, role_b = _role(env, "DA Purchaser"), _role(env, "DA Paymaster")
    Control = env["fix.sod.control"].sudo()
    Control.create(
        {
            "code": "DA-SOD-1",
            "name": "Purchasing and payment are separate hands",
            "role_a_id": role_a.id,
            "role_b_id": role_b.id,
            "conflict_action": "block",
            "rationale": "One hand buying and paying is the classic fraud pair.",
        }
    )
    # a group-pair control (no role ends) must be counted, never mirrored
    Control.create(
        {
            "code": "DA-SOD-2",
            "name": "Group-pair control with no role ends",
            "control_type": "group",
            "group_a_id": env.ref("base.group_user").id,
            "group_b_id": env.ref("base.group_system").id,
            "conflict_action": "warn",
        }
    )
    Register = env["fix.grc.sod.rule"]
    # the estate's own controls derive too — the first pass creates one row
    # per ACTIVE role-pair control (61 seeded on the test DB + this one)
    active_role_pairs = Control.search_count([("active", "=", True), ("control_type", "=", "role")])
    assert active_role_pairs >= 2
    res = Register.with_user(m.officer).action_rebuild_from_controls()
    assert res["created"] == active_role_pairs and res["updated"] == 0
    assert res["skipped_group_pair"] >= 1
    derived = Register.sudo().search([("source_control_id.code", "=", "DA-SOD-1")])
    assert len(derived) == 1
    assert derived.severity == "high"  # block -> high
    assert derived.role_a == role_a and derived.role_b == role_b
    assert derived.state == "active"
    # idempotent: the second rebuild updates, it never duplicates
    res2 = Register.with_user(m.officer).action_rebuild_from_controls()
    assert res2["created"] == 0 and res2["updated"] == active_role_pairs
    assert len(Register.sudo().search([("source_control_id.code", "=", "DA-SOD-1")])) == 1
    # a waiver is an officer's decision — it survives the rebuild
    derived.with_user(m.officer).action_waive(reason="Compensating review in place.")
    Register.with_user(m.officer).action_rebuild_from_controls()
    derived.invalidate_recordset()
    assert derived.state == "waived" and derived.waived_by_id == m.officer
    # a manual rule (no source control) is never touched by a rebuild
    manual = Register.sudo().create(
        {"name": "DA manual rule", "role_a": role_a.id, "role_b": role_b.id}
    )
    Register.cron_rebuild_sod()
    manual.invalidate_recordset()
    assert manual.state == "active" and not manual.source_control_id


# ------------------------------------------------ A3-F04: the PDPA fixes
def test_legitimate_interest_is_not_a_lawful_basis(m):
    """PDPA 2026 does not offer legitimate interest; the register must refuse
    to record processing on it."""
    env = m.env
    assert "legitimate_interest" not in {
        key for key, _label in env["fix.grc.processing.activity"]._fields["lawful_basis"].selection
    }
    with pytest.raises((ValidationError, ValueError)), env.cr.savepoint():
        env["fix.grc.processing.activity"].create(
            {
                "name": "DA unlawful basis",
                "purpose": "Marketing profiling",
                "lawful_basis": "legitimate_interest",
                "data_categories": "Contact details",
                "subject_categories": "Customers",
            }
        )


def test_the_dsr_clock_notifies_the_officers_once(m):
    env = m.env
    Pdpa = env["fix.grc.pdpa"]
    today = fields.Date.context_today(Pdpa)
    stale = Pdpa.create(
        {
            "name": "DA stale DSR",
            "request_type": "access",
            "subject_name": "DA Subject",
            "received_on": fields.Date.subtract(today, days=45),
        }
    )
    fresh = Pdpa.create(
        {
            "name": "DA fresh DSR",
            "request_type": "correction",
            "subject_name": "DA Subject Two",
            "received_on": today,
        }
    )
    stale.invalidate_recordset()
    assert stale.due_on == fields.Date.subtract(today, days=15)  # received + 30
    Pdpa.cron_dsr_overdue()
    stale.invalidate_recordset()
    assert stale.overdue_notified_on == today
    told = len(stale.message_ids.filtered(lambda msg: "OVERDUE" in (msg.body or "")))
    assert told == 1
    # the second pass is silent — one notification, not daily noise
    Pdpa.cron_dsr_overdue()
    stale.invalidate_recordset()
    told_again = len(stale.message_ids.filtered(lambda msg: "OVERDUE" in (msg.body or "")))
    assert told_again == 1
    # a request inside its window is never stamped
    fresh.invalidate_recordset()
    assert not fresh.overdue_notified_on
    # the stamp is the system's, not a typed value (the superuser is trusted
    # by the field guard — the refusal is only honest from a real officer)
    with pytest.raises(UserError), env.cr.savepoint():
        stale.with_user(m.officer).write(
            {"overdue_notified_on": fields.Date.subtract(today, days=99)}
        )
