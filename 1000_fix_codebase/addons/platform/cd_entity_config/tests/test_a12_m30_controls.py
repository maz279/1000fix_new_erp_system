"""test_a12_m30_controls.py — the A12 remediation of M30 (Platform
Administration) and X3 (the DOFA ruling), probed as NON-ADMIN users where the
attack was non-admin.

Source: working/A12_Workflow_and_Approval_Report.md §6 (X3, X4, R4) and
working/A12_evidence/module_findings/M30.md (M30-1..M30-14). Every control is
checked both ways: the bypass is refused, the legitimate role still works.
The superuser fixture only builds the world; the attacks run as plain
employees and as DOFA tier holders.

Note on the superuser exemption: action_put_in_force skips the two-person
check for env.su, exactly as every fix.guarded.mixin guard does. The
workspace never runs as superuser, and the lead's existing suites rule as su
(see test_a03_gap_closure.py) — a test here pins that contract too.

A12 finish E1: for a person action_put_in_force is now only the PROPOSAL; the
named Tier 5 holder's action_countersign rules. The refusal tests below still
call it (its checks are the proposal's), and `_rule` walks both acts.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from odoo import api
from odoo.exceptions import AccessError, UserError, ValidationError
from psycopg2 import IntegrityError

REFUSED = (UserError, ValidationError, AccessError)
TIER4 = "cd_entity_config.group_dofa_tier_4"
TIER5 = "cd_entity_config.group_dofa_tier_5"
PADMIN = "cd_entity_config.group_platform_admin"

# A model that really reads the ladder (cd_service_order), one that exists but
# never will (M29 access request), and the DOFA bands of fix.estimate's coded
# default, so a ruled test ladder governs something real (M30-5, d09).
DOFA_TARGET = "fix.estimate"
NON_DOFA_TARGET = "fix.access.request"

JS = (
    Path(__file__).resolve().parents[2]  # addons/platform/
    / "cd_p03_portal"
    / "static"
    / "src"
    / "a12"
    / "m30.js"
)


@pytest.fixture
def env(odoo_env):
    return odoo_env


@pytest.fixture
def make_user(env):
    counter = {"n": 0}

    def _make(*xmlids):
        counter["n"] += 1
        groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
        return (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "M30 A12 Probe %d" % counter["n"],
                    "login": "m30.a12.probe.%d@a12.test" % counter["n"],
                    "group_ids": [(6, 0, groups)],
                }
            )
        )

    return _make


def as_user(env, user):
    """The same transaction, a different pair of eyes."""
    return api.Environment(env.cr, user.id, {"lang": "en_US"})


def _rule(ladder, proposer, counter, reference):
    """The sanctioned ruling: two acts by two people."""
    ladder.with_user(proposer).action_propose_ruling(
        reference=reference, countersigned_by=counter.id
    )
    ladder.with_user(counter).action_countersign(reference=reference)


def _estimate_bands(env):
    """fix.estimate's coded default as ladder band values."""
    defaults = env[DOFA_TARGET]._dofa_thresholds()
    return [(b if b == float("inf") or b >= 1e9 else float(b), t) for b, t in defaults]


@pytest.fixture
def draft_ladder(env):
    """A ladder for a real DOFA target, not yet ruled."""

    def _draft(target=DOFA_TARGET, name="Estimate authority matrix", basis="dofa_matrix"):
        bands = [
            {"upper_bound": bound if bound < 1e9 else 1e9, "tier": tier, "note": "test band"}
            for bound, tier in _estimate_bands(env)
        ]
        return env["fix.dofa.ladder"].create(
            {
                "name": name,
                "target_model": target,
                "basis": basis,
                "threshold_ids": [(0, 0, band) for band in bands],
            }
        )

    return _draft


# ===================== X3 / M30-1: two-person ruling ========================


def test_m30_1_ruling_without_tier4_refused(env, make_user, draft_ladder):
    """A plain internal user cannot rule — even with a reference and a
    countersigner on file (d04's escalation started one tier too low)."""
    plain = make_user()
    counter = make_user(TIER4, TIER5)
    ladder = draft_ladder()
    ladder.write({"countersigned_by": counter.id})
    with pytest.raises(UserError, match="Tier 4 / Tier 5 authority"), env.cr.savepoint():
        ladder.with_user(plain).action_put_in_force(reference="minute 42")


def test_m30_1_single_person_ruling_refused(env, make_user, draft_ladder):
    """One Tier-4 user ruling ALONE is the finding: refused (d04)."""
    t4 = make_user(TIER4)
    ladder = draft_ladder()
    with pytest.raises(UserError, match="TWO authority holders"), env.cr.savepoint():
        ladder.with_user(t4).action_put_in_force(reference="x")


def test_m30_1_self_countersign_refused(env, make_user, draft_ladder):
    """Naming yourself as the countersigner is not two people."""
    t4 = make_user(TIER4)
    ladder = draft_ladder()
    ladder.write({"countersigned_by": t4.id})
    with pytest.raises(UserError, match="two DIFFERENT people"), env.cr.savepoint():
        ladder.with_user(t4).action_put_in_force(reference="minute 42")


def test_m30_1_pair_without_tier5_refused(env, make_user, draft_ladder):
    """Two Tier-4 holders are not enough: one of the pair must hold Tier 5."""
    t4a = make_user(TIER4)
    t4b = make_user(TIER4)
    ladder = draft_ladder()
    ladder.write({"countersigned_by": t4b.id})
    with pytest.raises(UserError, match="Tier 5"), env.cr.savepoint():
        ladder.with_user(t4a).action_put_in_force(reference="minute 42")


def test_m30_1_countersigner_without_tier4_refused(env, make_user, draft_ladder):
    """The countersigner must hold authority too — a random colleague's id
    does not legitimise the ruling."""
    t5 = make_user(TIER5)
    bystander = make_user()
    ladder = draft_ladder()
    ladder.write({"countersigned_by": bystander.id})
    with pytest.raises(UserError, match="cannot countersign"), env.cr.savepoint():
        ladder.with_user(t5).action_put_in_force(reference="minute 42")


def test_m30_1_ruling_without_reference_refused(env, make_user, draft_ladder):
    """Authority 'x' was the finding's string of choice; no reference, no
    ruling (d04)."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    ladder = draft_ladder()
    ladder.write({"countersigned_by": t5.id})
    with pytest.raises(UserError, match="ruling reference"), env.cr.savepoint():
        ladder.with_user(t4).action_put_in_force(reference="  ")


def test_m30_1_two_person_ruling_works(env, make_user, draft_ladder):
    """The proper path: a Tier 4 proposes, the named Tier 5 countersigns from
    their own session, and both are recorded on the ruling. Naming the Tier 5 is
    not their act: until they countersign, nothing is in force (A12 finish E1)."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    ladder = draft_ladder()
    ladder.write({"countersigned_by": t5.id})
    ladder.with_user(t4).action_put_in_force(reference="Board minute 2026-11-04")
    assert ladder.in_force is False and ladder.ruling_state == "proposed"
    assert env["fix.dofa.ladder"].thresholds_for(DOFA_TARGET) is None
    ladder.with_user(t5).action_countersign(reference="Board minute 2026-11-04")
    assert ladder.in_force is True
    assert ladder.ruled_by == t4
    assert ladder.countersigned_by == t5
    assert ladder.ruled_at
    assert ladder.ruling_reference == "Board minute 2026-11-04"
    # The ruling actually governs: the estimate model reads the ladder.
    tiers = env["fix.dofa.ladder"].thresholds_for(DOFA_TARGET)
    assert tiers and tiers[0][1] == ladder.threshold_ids.sorted("upper_bound")[0].tier


def test_m30_1_countersigner_must_hold_tier5_by_default(env, make_user, draft_ladder):
    """A12 finish decision E1: the countersigner is a Tier 5 holder, so a junior does
    not endorse a senior. The old test pinned either order, when the 'countersigner'
    did nothing. ir.config_parameter fix_dofa.countersign_min_tier=tier_4 reopens it."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    ladder = draft_ladder()
    with pytest.raises(UserError, match="Tier 5"), env.cr.savepoint():
        ladder.with_user(t5).action_put_in_force(reference="minute 7", countersigned_by=t4.id)
    env["ir.config_parameter"].sudo().set_param("fix_dofa.countersign_min_tier", "tier_4")
    _rule(ladder, t5, t4, "minute 7")
    assert ladder.in_force is True
    assert ladder.ruled_by == t5
    assert ladder.countersigned_by == t4


def test_m30_1_superuser_ruling_unchanged(env, draft_ladder):
    """The su path stays open (guarded-mixin convention; the lead's suites
    rule as superuser). It stamps ruled_by = superuser."""
    ladder = draft_ladder()
    ladder.action_put_in_force(reference="seed ruling")
    assert ladder.in_force is True
    assert ladder.ruled_by == env.user


# ===================== M30-2: the stamp cannot be forged ====================


def test_m30_2_in_force_plain_write_refused(env, make_user, draft_ladder):
    """`in_force = True` by plain write, no reference, no chatter — refused
    even for the Tier-4 holder who may legitimately rule (d05)."""
    t4 = make_user(TIER4, TIER5)
    ladder = draft_ladder()
    with pytest.raises(UserError, match="through its workflow action"), env.cr.savepoint():
        ladder.with_user(t4).write({"in_force": True})


def test_m30_2_ruled_by_retype_refused(env, make_user, draft_ladder):
    """`ruled_by` rewritten to name someone who never ruled (d08)."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    other = make_user(TIER4, TIER5)
    ladder = draft_ladder()
    _rule(ladder, t4, t5, "minute 1")
    with pytest.raises(UserError, match="workflow action"), env.cr.savepoint():
        ladder.with_user(other).write({"ruled_by": other.id})


def test_m30_2_one_in_force_enforced_by_the_database(env, draft_ladder):
    """d06's race: two ladders in force at once. The partial unique index
    refuses the second even when both writes go through the guarded token
    (i.e. even if a future action forgets to retire the sibling)."""
    ladder_a = draft_ladder(name="A", basis="req_text")
    ladder_b = draft_ladder(name="B", basis="dofa_matrix")
    ladder_a._guarded().write({"in_force": True})
    with pytest.raises(IntegrityError), env.cr.savepoint():
        ladder_b._guarded().write({"in_force": True})


def test_m30_2_bands_locked_once_in_force(env, make_user, draft_ladder):
    """d07: a second Tier-4 lowers the in-force band with no re-ruling.
    Write, create and delete of bands are all refused; the error says what
    to do instead (a new ladder)."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    ladder = draft_ladder()
    _rule(ladder, t4, t5, "minute 2")
    band = ladder.threshold_ids.sorted("upper_bound")[:1]
    for attack in (
        lambda: band.with_user(t4).write({"upper_bound": 1.0}),
        lambda: env["fix.dofa.threshold"]
        .with_user(t4)
        .create({"ladder_id": ladder.id, "upper_bound": 5.0, "tier": "tier_2"}),
        lambda: band.with_user(t4).unlink(),
    ):
        with pytest.raises(UserError, match="NEW ladder"), env.cr.savepoint():
            attack()


def test_m30_2_supersede_retires_the_old_ruling(env, make_user, draft_ladder):
    """Ruling a new ladder for the same target supersedes the old one — the
    retirement is part of the same two-person act, never a silent switch."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    t5b = make_user(TIER5)
    old = draft_ladder(name="Old", basis="req_text")
    _rule(old, t4, t5, "minute 3")
    new = draft_ladder(name="New", basis="ruling")
    _rule(new, t5, t5b, "minute 4")
    env.cr.flush()  # the index verdict is the database's, read it back
    assert old.in_force is False and new.in_force is True
    assert env["fix.dofa.ladder"].thresholds_for(DOFA_TARGET)


def test_m30_2_in_force_ladder_not_deletable(env, make_user, draft_ladder):
    """Erasing the ruling on record would return the model to its coded
    default with no trace; superseded, never erased."""
    t4, t5 = make_user(TIER4), make_user(TIER5)
    ladder = draft_ladder()
    _rule(ladder, t4, t5, "minute 5")
    with pytest.raises(UserError, match="supersede"), env.cr.savepoint():
        ladder.with_user(t4).unlink()


# ===================== M30-5: the target must be governed ===================


def test_m30_5_non_dofa_target_refused_on_create(env):
    """A ladder for fix.access.request governed nothing while reading 'in
    force' on the report — refused at create when the model exists (d09)."""
    with pytest.raises(ValidationError, match="does not carry fix.dofa.mixin"), env.cr.savepoint():
        env["fix.dofa.ladder"].create(
            {
                "name": "Bogus",
                "target_model": NON_DOFA_TARGET,
                "basis": "ruling",
                "threshold_ids": [(0, 0, {"upper_bound": 1e9, "tier": "tier_1"})],
            }
        )


def test_m30_5_unknown_target_refused_at_ruling(env):
    """A model that does not exist cannot be validated at create (the T0
    data load runs before the domain modules) — but nothing unreal can be
    RULED: the action refuses it absolutely (d09)."""
    ladder = env["fix.dofa.ladder"].create(
        {
            "name": "Phantom",
            "target_model": "no.such.model",
            "basis": "ruling",
            "threshold_ids": [(0, 0, {"upper_bound": 1e9, "tier": "tier_1"})],
        }
    )
    with pytest.raises(UserError, match="not a model governed by DOFA"), env.cr.savepoint():
        ladder.action_put_in_force(reference="minute 6")


# ============ M30-6 / M30-7 / M30-12: registers are master data =============


def test_m30_7_branch_create_refused_for_clerk(env, make_user):
    """b01: any user could create a branch. The ACL (group_user read-only)
    refuses the clerk outright."""
    clerk = make_user()
    entity = env["fix.entity"].search([], limit=1)
    ou = env["operating.unit"].search([], limit=1)
    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.branch"].with_user(clerk).create(
            {
                "name": "Ghost branch",
                "code": "GHOST",
                "entity_id": entity.id,
                "operating_unit_id": ou.id,
            }
        )


def test_m30_6_calendar_holiday_write_refused_for_clerk(env, make_user):
    """b07: a clerk's 60-day holiday moved an SLA deadline by 59 days."""
    clerk = make_user()
    calendar = env["fix.working.calendar"].search([], limit=1)
    if not calendar:
        calendar = env["fix.working.calendar"].create({"name": "Probe calendar"})
    with pytest.raises(AccessError), env.cr.savepoint():
        env["fix.working.calendar.holiday"].with_user(clerk).create(
            {
                "calendar_id": calendar.id,
                "name": "Clerk's very long weekend",
                "date_from": "2026-11-01",
                "date_to": "2027-01-01",
            }
        )


def test_m30_12_entity_write_refused_for_clerk(env, make_user):
    """b05: the entity master was writable by all."""
    clerk = make_user()
    entity = env["fix.entity"].search([], limit=1)
    if not entity:
        pytest.skip("no fix.entity row on this database")
    with pytest.raises(AccessError), env.cr.savepoint():
        entity.with_user(clerk).write({"legal_name": "Not the legal name"})


def test_m30_defense_in_depth_platform_admin_gate(env, make_user):
    """X4: the code-level gate holds even where an ACL does not (a future
    module granting CRUD to a wider group). require_platform_admin refuses
    anyone but a Platform Admin / Settings holder; the platform admin passes.
    """
    from odoo.addons.cd_entity_config.models.fix_entity import require_platform_admin

    clerk, t4 = make_user(), make_user(TIER4)
    admin = make_user(PADMIN)
    with pytest.raises(AccessError, match="Platform Admin"):
        require_platform_admin(as_user(env, clerk), "the probe")
    with pytest.raises(AccessError, match="Platform Admin"):
        require_platform_admin(as_user(env, t4), "the probe")
    assert require_platform_admin(as_user(env, admin), "the probe") is None


def test_m30_admin_path_still_works(env, make_user):
    """The legitimate role can still do the job: a Platform Admin edits the
    branch register through the ORM."""
    admin = make_user(PADMIN)
    branch = env["fix.branch"].search([], limit=1)
    if not branch:
        pytest.skip("no fix.branch row on this database")
    branch.with_user(admin).write({"phone": "+8801700000000"})
    assert branch.phone == "+8801700000000"


# ===================== M30-10: BD-02 / NT-003 cannot be bypassed ============


def _notif(**overrides):
    vals = {
        "consent_class": "marketing",
        "channel": "sms",
        "send_window": "10:00-20:00",
        "frequency_cap": 5,
        "sms_route": "non-masking",
    }
    vals.update(overrides)
    return vals


def test_m30_10_marketing_masking_route_refused(env):
    with pytest.raises(ValidationError, match="BD-02"), env.cr.savepoint():
        env["fix.notification.config"].create(_notif(sms_route="masking"))


def test_m30_10_sms_route_only_write_bypass_closed(env):
    """b09: the constraint used to depend on the cap fields only, so writing
    sms_route ALONE put marketing SMS on the masking route."""
    row = env["fix.notification.config"].create(_notif())
    with pytest.raises(ValidationError, match="BD-02"), env.cr.savepoint():
        row.write({"sms_route": "masking"})


def test_m30_10_marketing_uncapped_refused(env):
    """b10: cap 0 means uncapped; marketing may not be."""
    with pytest.raises(ValidationError, match="uncapped"), env.cr.savepoint():
        env["fix.notification.config"].create(_notif(frequency_cap=0))


def test_m30_10_transactional_still_uncappable(env):
    """The proper path: security/transactional stay uncapped by policy."""
    row = env["fix.notification.config"].create(
        _notif(consent_class="transactional", send_window="24/7", frequency_cap=0)
    )
    assert row.frequency_cap == 0


# ============ M30-13: sudo reports no longer hand out the platform ==========


@pytest.mark.parametrize("report", ["config_drift", "platform_health", "job_success_rate"])
def test_m30_13_config_reports_gated_for_clerk(env, make_user, report):
    """c04: any internal user could list 72 cron schedules and every config
    prefix. Now the report checks the model's read ACL first."""
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    clerk = make_user()
    with pytest.raises(UserError, match="platform administrators only"):
        getattr(m30, report)(as_user(env, clerk))


def test_m30_13_reports_read_for_settings_holder(env, make_user):
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    sysadmin = make_user("base.group_system")
    pack = m30.config_drift(as_user(env, sysadmin))
    assert pack.get("rows")
    jobs = m30.job_success_rate(as_user(env, sysadmin))
    # No invented success figure for jobs that have no counter (BRU-ADM-12).
    cron_rows = [r for r in jobs["rows"] if r["kind"] == "Scheduled job"]
    assert cron_rows and all(r["failures"] == "-" for r in cron_rows)


def test_m30_13_kpis_read_as_the_caller(env, make_user):
    """R4: KPIs dropped the sudo — a clerk's tiles answer for the caller's
    own company scoping, still working."""
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    clerk = make_user()
    tiles = m30.kpis(as_user(env, clerk))
    assert tiles["branches"] == len(env["fix.branch"].with_user(clerk).search([]))


# ===================== R4: the workspace surface whitelist ==================


def test_r4_every_m30_surface_declares_writable():
    """The write endpoint refuses everything the form was not meant to send:
    every M30 surface key is in WRITABLE, and the merge applied it."""
    from odoo.addons.cd_p03_portal.controllers import a12
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    assert set(m30.WRITABLE) == set(m30.SURFACES)
    for model, writable in m30.WRITABLE.items():
        assert a12.SURFACES[model]["writable"] == tuple(writable)
    # Deployment configuration is read-only in the workspace (c01-c03).
    assert m30.WRITABLE["ir.config_parameter"] == ()
    assert m30.WRITABLE["ir.cron"] == ()


def test_r4_dofa_stamp_not_writable():
    """The ruling stamp is never typeable through /p03/model/write."""
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    writable = set(m30.WRITABLE["fix.dofa.ladder"])
    assert writable & {"in_force", "ruled_by", "ruled_at", "ruling_reference"} == set()
    assert "countersigned_by" in writable  # chosen pre-ruling, frozen after


def test_r4_release_whitelist_links_the_approved_change():
    """D8 hand-off: an operator links the release to its approved M66 change;
    the go-live state stays action-only. A12 finish E7: version and name are in
    the list because + New could never save without them; the model freezes them
    all once released."""
    from odoo.addons.cd_p03_portal.controllers.a12 import m30

    writable = m30.WRITABLE["fix.platform.release"]
    assert {"version", "name", "environment_id", "itsm_change_id", "rollback_plan"} <= set(writable)
    assert not {"state", "released_on", "released_by_id", "rolled_back_reason"} & set(writable)


def test_r4_forms_offer_no_lifecycle_inputs():
    """The form must offer exactly what a user may legitimately type: no
    state / in_force inputs (badge only), the itsm_change link and the
    countersigner are there, and the ruling asks for its reference."""
    src = JS.read_text(encoding="utf-8")
    for banned in ("{ name: 'state'", '{ name: "state"', "{ name: 'in_force'"):
        assert banned not in src, "a form still types %r" % banned
    assert "itsm_change_id" in src
    assert "countersigned_by" in src
    assert re.search(r"ask:\s*'Ruling reference", src)
    assert "kwarg: 'reference'" in src


# ============ X3 companions: what the audit said must keep working ==========
def test_x3_thresholds_and_conflicts_survive(env, draft_ladder):
    """thresholds_for() answers None until ruled (coded default applies),
    the ruled ladder after; conflicts() keeps naming the open decision."""
    Ladder = env["fix.dofa.ladder"]
    draft = draft_ladder(name="Survival", basis="req_text")
    assert Ladder.thresholds_for(DOFA_TARGET) is None
    draft.action_put_in_force(reference="minute 8")
    ruled = Ladder.thresholds_for(DOFA_TARGET)
    assert ruled == [
        (band.upper_bound, band.tier) for band in draft.threshold_ids.sorted("upper_bound")
    ]
    other = draft_ladder(name="Survival alt", basis="dofa_matrix")
    assert any(
        c["target_model"] == DOFA_TARGET for c in Ladder.conflicts()
    ), "conflicts() must keep reporting the two bases on file"
    assert other.in_force is False
