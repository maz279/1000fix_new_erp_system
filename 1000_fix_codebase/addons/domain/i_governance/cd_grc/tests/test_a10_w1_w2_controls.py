# A10 remediation (2026-11-04), M60: W1 whistle-blower confidentiality +
# W2 legal-matter closure authority.
#
# Every control is exercised as NON-ADMIN users holding only the role groups
# each step needs (the superuser is trusted by the field guard and would
# hide a gap). Each control is attacked three ways where it applies: the
# wrong role, a plain write() (the JSON-RPC path) and the real P03
# endpoints (/p03/model/records, /p03/model/form, /p03/model/write,
# /p03/model/action). The legitimate path runs end to end through the real
# actions. The odoo_env fixture rolls everything back.
import itertools
import json
import types

import pytest
from odoo import fields
from odoo.addons.cd_p03_portal.controllers import p03_generic_api as g
from odoo.exceptions import AccessError, UserError

REFUSED = (UserError, AccessError)
GUARD = "changes only through its workflow"
INTAKE = "cd_grc.group_grc_whistle_intake"
INVESTIGATOR = "cd_grc.group_grc_whistle_investigator"
LEGAL = "cd_grc.group_grc_legal"

_MW = getattr(g.P03GenericApiController.model_write, "original_endpoint", None) or (
    g.P03GenericApiController.model_write
)
_MA = getattr(g.P03GenericApiController.model_action, "original_endpoint", None) or (
    g.P03GenericApiController.model_action
)
_MR = getattr(g.P03GenericApiController.model_records, "original_endpoint", None) or (
    g.P03GenericApiController.model_records
)
_MF = getattr(g.P03GenericApiController.model_form, "original_endpoint", None) or (
    g.P03GenericApiController.model_form
)

_SEQ = itertools.count(1)


def _user(env, login, groups=()):
    n = next(_SEQ)
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "A10 M60 %s %d" % (login, n),
                "login": "a10m60.%s.%d@a10.test" % (login, n),
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(x).id for x in groups])
                ],
            }
        )
    )
    assert not user.has_group("base.group_system")
    return user


def _events(env, event_type, aggregate_id=None):
    domain = [("event_type", "=", event_type)]
    if aggregate_id is not None:
        domain.append(("aggregate_id", "=", aggregate_id))
    return [json.loads(e.payload) for e in env["fix.event.outbox"].search(domain, order="id")]


def _access_log(env, res_id, field_name=None):
    domain = [("res_model", "=", "fix.grc.whistle"), ("res_id", "=", res_id)]
    if field_name:
        domain.append(("field_name", "=", field_name))
    return env["fix.pii.access.log"].sudo().search(domain, order="id desc")


@pytest.fixture
def w(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env)
    x.clerk = _user(env, "clerk")
    x.intake1 = _user(env, "intake1", [INTAKE])
    x.intake2 = _user(env, "intake2", [INTAKE])
    x.inv = _user(env, "inv", [INVESTIGATOR])
    x.inv2 = _user(env, "inv2", [INVESTIGATOR])
    x.legal = _user(env, "legal", [LEGAL])
    x.inv_emp = env["hr.employee"].create({"name": "A10 M60 Investigator", "user_id": x.inv.id})
    x.inv2_emp = env["hr.employee"].create({"name": "A10 M60 Investigator Two", "user_id": x.inv2.id})
    saved = getattr(g, "request", None)
    yield x
    g.request = saved


def _file(x, vals=None, user=None):
    vals = dict(
        {
            "channel": "web",
            "category": "fraud",
            "anonymous": False,
            "summary": "Warehouse parts invoiced twice",
        },
        **(vals or {}),
    )
    return x.env["fix.grc.whistle"].with_user(user or x.intake1).create(vals)


def p03(x, endpoint, user=None, **kw):
    g.request = types.SimpleNamespace(env=x.env(user=(user or x.clerk).id))
    return endpoint(g.P03GenericApiController(), **kw)


def _journey(x, rec):
    """received -> investigating, worked by the assigned investigator."""
    rec.with_user(x.intake1).action_assign_investigator(x.inv_emp.id)
    rec.with_user(x.inv).action_investigate()
    return rec


# --------------------------------------------------------------------------- W1
def test_w1_filing_gate_and_reporter_stamp(w):
    Whistle = w.env["fix.grc.whistle"]
    with pytest.raises(UserError, match="Whistleblowing Intake"):
        Whistle.with_user(w.clerk).create({"channel": "web", "summary": "clerk files directly"})
    # a caller-typed reporter id is never trusted: the system stamps the
    # session user, through sudo (the field is system-only)
    rec = _file(w, {"reporter_user_id": w.intake2.id})
    assert rec.sudo().reporter_user_id == w.intake1
    assert rec.state == "received"
    # the filing itself is an access-log entry
    assert _access_log(w.env, rec.id, "summary").filtered(
        lambda row: "filed" in (row.reason or "")
    )


def test_w1_reporter_field_is_system_only(w):
    rec = _file(w)
    # neither intake nor the assigned investigator reads the identity by
    # field — only the logged reveal action may
    with pytest.raises(AccessError):
        rec.with_user(w.intake1).read(["reporter_user_id"])
    with pytest.raises(AccessError):
        rec.with_user(w.inv).read(["reporter_user_id"])


def test_w1_investigator_sees_only_assigned_reports(w):
    rec_a = _file(w, {"summary": "A: billing fraud"})
    rec_b = _file(w, {"summary": "B: safety cut corners"})
    rec_a.with_user(w.intake1).action_assign_investigator(w.inv_emp.id)
    Whistle = w.env["fix.grc.whistle"]
    assert Whistle.with_user(w.inv).search([]).mapped("id") == [rec_a.id]
    assert not Whistle.with_user(w.inv2).search([])
    assert set(Whistle.with_user(w.intake1).search([]).ids) == {rec_a.id, rec_b.id}
    # a plain internal user cannot read a report at all (ACL)
    with pytest.raises(AccessError):
        Whistle.with_user(w.clerk).search([])


def test_w1_assignment_controls(w):
    rec = _file(w)
    # intake cannot investigate its own filing
    self_emp = w.env["hr.employee"].create(
        {"name": "A10 M60 self", "user_id": w.intake1.id}
    )
    with pytest.raises(UserError, match="may not investigate"):
        rec.with_user(w.intake1).action_assign_investigator(self_emp.id)
    # an employee without a login cannot be assigned
    with pytest.raises(UserError, match="with a login"):
        rec.with_user(w.intake1).action_assign_investigator(
            w.env["hr.employee"].create({"name": "A10 M60 no login"}).id
        )
    # only intake assigns
    with pytest.raises(UserError, match="Whistleblowing Intake"):
        rec.with_user(w.clerk).action_assign_investigator(w.inv_emp.id)
    rec.with_user(w.intake1).action_assign_investigator(w.inv_emp.id)
    # a received-and-assigned report cannot be reassigned
    with pytest.raises(UserError, match="already has an investigator"):
        rec.with_user(w.intake1).action_assign_investigator(w.inv2_emp.id)


def test_w1_intake_facts_are_guarded(w):
    rec = _file(w)
    for vals in ({"state": "closed"}, {"summary": "rewritten"}, {"channel": "letter"}):
        with pytest.raises(UserError, match=GUARD):
            rec.with_user(w.intake1).write(vals)
    with pytest.raises(UserError, match=GUARD):
        w.env["fix.grc.whistle"].with_user(w.intake1).create(
            {"channel": "web", "summary": "born closed", "state": "closed"}
        )


def test_w1_reveal_is_logged_and_gated(w):
    rec = _journey(w, _file(w))  # non-anonymous, filed by intake1
    with pytest.raises(UserError, match="State why"):
        rec.with_user(w.inv).action_reveal_reporter()
    out = rec.with_user(w.inv).action_reveal_reporter("Needed for the disciplinary file")
    assert out == {"revealed": True, "reporter": w.intake1.name}
    assert rec.revealed_count == 1
    log = _access_log(w.env, rec.id, "reporter_user_id")
    assert log and log[0].user_id == w.inv
    assert "disciplinary" in log[0].reason
    # only the assigned investigator reveals
    with pytest.raises(UserError, match="assigned"):
        rec.with_user(w.inv2).action_reveal_reporter("trying anyway")
    # an anonymous report has nothing to reveal
    anon = _journey(w, _file(w, {"anonymous": True}))
    assert anon.with_user(w.inv).action_reveal_reporter("check")["revealed"] is False


def test_w1_close_journey_event_and_consumer(w):
    rec = _journey(w, _file(w, {"category": "harassment"}))
    # closing before investigating is refused
    fresh = _file(w)
    fresh.with_user(w.intake1).action_assign_investigator(w.inv_emp.id)
    with pytest.raises(UserError, match="Investigate"):
        fresh.with_user(w.inv).action_close(finding="substantiated")
    # a finding is required
    with pytest.raises(UserError, match="finding"):
        rec.with_user(w.inv).action_close()
    # wrong investigator
    with pytest.raises(UserError, match="assigned"):
        rec.with_user(w.inv2).action_close(finding="substantiated")
    rec.with_user(w.inv).action_close(finding="substantiated", follow_up="Disciplinary process")
    assert (rec.state, rec.finding, rec.follow_up) == ("closed", "substantiated", "Disciplinary process")
    # the second reviewer is an intake member, never the investigator, and
    # is stamped by the system
    intake_members = w.env.ref(INTAKE).all_user_ids
    assert rec.reviewer_id and rec.reviewer_id in intake_members
    assert rec.reviewer_id != rec.investigator_id.user_id
    # the event carries the finding, never the identity
    (payload,) = _events(w.env, "grc.whistle.closed", rec.id)
    assert payload == {
        "report": rec.name,
        "category": "harassment",
        "finding": "substantiated",
        "follow_up": "Disciplinary process",
    }
    assert w.intake1.name not in json.dumps(payload)
    # relay-only, idempotent consumer
    env_from_relay = {"aggregate_id": rec.id, "payload": {"finding": "substantiated"}}
    with pytest.raises(UserError):
        w.env["fix.grc.whistle"].with_user(w.intake1).consume_grc_whistle_closed(env_from_relay)
    w.env["fix.grc.whistle"].sudo().consume_grc_whistle_closed(env_from_relay)
    bodies = [m.body or "" for m in rec.message_ids]
    assert any("Closed — finding: substantiated." in b for b in bodies)
    w.env["fix.grc.whistle"].sudo().consume_grc_whistle_closed(env_from_relay)  # redelivery
    assert len([b for b in bodies if "Closed — finding" in b]) == 1


def test_w1_p03_list_is_rule_filtered(w):
    rec_a = _file(w, {"summary": "A"})
    rec_b = _file(w, {"summary": "B"})
    rec_a.with_user(w.intake1).action_assign_investigator(w.inv_emp.id)
    cols = ["name", "channel", "state"]
    out = p03(w, _MR, user=w.inv, model="fix.grc.whistle", cols=cols)
    assert "error" not in out and [r["name"] for r in out["rows"]] == [rec_a.name]
    out = p03(w, _MR, user=w.intake2, model="fix.grc.whistle", cols=cols)
    assert {r["name"] for r in out["rows"]} == {rec_a.name, rec_b.name}
    out = p03(w, _MR, user=w.clerk, model="fix.grc.whistle", cols=cols)
    assert "error" in out


def test_w1_p03_form_read_is_rule_checked(w):
    rec = _file(w, {"summary": "secret account"})
    fieldspec = [{"name": "summary"}, {"name": "investigation_notes"}]
    out = p03(w, _MF, user=w.inv2, model="fix.grc.whistle", fields=fieldspec, record_id=rec.id)
    assert "error" in out  # an unassigned investigator cannot open it by id
    out = p03(w, _MF, user=w.intake2, model="fix.grc.whistle", fields=fieldspec, record_id=rec.id)
    assert out.get("record", {}).get("summary") == "secret account"


def test_w1_p03_write_and_action(w):
    rec = _journey(w, _file(w))
    # intake facts are refused on the write endpoint too
    out = p03(w, _MW, user=w.inv, model="fix.grc.whistle", record_id=rec.id, values={"summary": "x"})
    assert "error" in out and GUARD in out["error"]
    # the working notes stay editable until closure
    out = p03(
        w, _MW, user=w.inv, model="fix.grc.whistle", record_id=rec.id,
        values={"investigation_notes": "Interviewed two witnesses"},
    )
    assert "error" not in out
    assert rec.investigation_notes == "Interviewed two witnesses"
    # the close action runs through the endpoint with its prompt kwarg
    out = p03(
        w, _MA, user=w.inv, model="fix.grc.whistle", ids=rec.ids, method="action_close",
        kwargs={"finding": "policy_gap"},
    )
    assert out.get("success") is True
    assert (rec.state, rec.finding) == ("closed", "policy_gap")
    # a clerk cannot run any whistle action
    out = p03(
        w, _MA, user=w.clerk, model="fix.grc.whistle", ids=rec.ids, method="action_investigate"
    )
    assert out.get("success") is False and "assigned" in out.get("error", "")


# --------------------------------------------------------------------------- W2
def test_w2_legal_closure_needs_outcome_and_note(w):
    Legal = w.env["fix.grc.legal"]
    with pytest.raises(AccessError):
        Legal.with_user(w.clerk).create({"matter_type": "litigation"})
    rec = Legal.with_user(w.legal).create(
        {"matter_type": "litigation", "counterparty": "Ex Vendor Ltd"}
    )
    # a plain write cannot close a matter (W2)
    with pytest.raises(UserError, match=GUARD):
        rec.with_user(w.legal).write({"state": "closed"})
    with pytest.raises(UserError, match="outcome"):
        rec.with_user(w.legal).action_close()
    with pytest.raises(UserError, match="closing note"):
        rec.with_user(w.legal).action_close(outcome="settled")
    rec.with_user(w.legal).action_close(outcome="settled", close_note="Deed of release signed")
    assert rec.state == "closed"
    assert (rec.outcome, rec.close_note, rec.closed_on) == (
        "settled", "Deed of release signed", fields.Date.context_today(rec)
    )
    with pytest.raises(UserError, match="already closed"):
        rec.with_user(w.legal).action_close(outcome="won", close_note="again")


def test_w2_legal_closure_freezes_the_record(w):
    rec = w.env["fix.grc.legal"].with_user(w.legal).create({"matter_type": "contract"})
    rec.with_user(w.legal).action_close(outcome="dismissed", close_note="Court dismissed")
    out = p03(
        w, _MW, user=w.legal, model="fix.grc.legal", record_id=rec.id,
        values={"close_note": "rewritten"},
    )
    assert "error" in out
    # and the P03 close action carries both prompts as kwargs
    rec2 = w.env["fix.grc.legal"].with_user(w.legal).create({"matter_type": "ip"})
    out = p03(
        w, _MA, user=w.legal, model="fix.grc.legal", ids=rec2.ids, method="action_close",
        kwargs={"outcome": "won", "close_note": "Injunction granted"},
    )
    assert out.get("success") is True
    assert rec2.state == "closed" and rec2.outcome == "won"
    # only Legal Counsel (ACL) reaches the surface at all
    out = p03(w, _MR, user=w.clerk, model="fix.grc.legal", cols=["name", "state"])
    assert "error" in out
