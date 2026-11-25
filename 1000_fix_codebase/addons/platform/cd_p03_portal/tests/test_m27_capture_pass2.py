# M27 Contact Centre (16743), capture audit pass 2 (2026-11-19): each page now
# captures the record the spec names there that nothing could capture before.
#
# Before (HEAD a6ca660a), evaluated with the engine's own fregCreate/fregPanels:
#   * page 1 Voice & IVR: no callback (FR-CCE-003), no voicemail (FR-CCE-007,
#     AUT-CCE-11) and no on-call rota (FR-CCE-008) existed - the queue could
#     only SAY "offer a callback / voicemail";
#   * page 2 Digital Channels: inbound SMS (FR-CCE-012) and social messaging
#     (FR-CCE-013) could not be logged - no channel value;
#   * page 6 Workforce Management: no volume forecast (FR-CCE-050, spec 10.1
#     fix.contact.forecast) for the roster to be planned against;
#   * page 7 Quality Monitoring: no calibration session (FR-CCE-055) and no
#     coaching record (FR-CCE-056);
#   * page 8 ERP Notification Service: no per-party volume throttle
#     (FR-CCE-044, BRU-CCE-15, AUT-CCE-13);
#   * page 9 Consent Enforcement: no preference centre (FR-CCE-046,
#     BRU-CCE-13, spec 10.1 fix.channel.preference) and no way to challenge a
#     message's classification (FR-CCE-041, BRU-CCE-04).
#
# The registry half runs in node over the real fragments; the ORM half drives
# /p03/model/write and /p03/model/action as NON-ADMIN users (the superuser is
# trusted by the guards and would hide a gap).
from __future__ import annotations

import ast
import csv
import importlib.util
import itertools
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest import mock

import pytest

HERE = Path(__file__).resolve().parent
CC = HERE.parents[2] / "domain" / "b_customer_engagement" / "cd_contact_centre"
CONTROLLER = HERE.parent / "controllers" / "a03" / "m27.py"

_spec = importlib.util.spec_from_file_location("_m27_pass1", HERE / "test_m27_capture_buttons.py")
_pass1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pass1)
m27 = _pass1.m27  # the engine-evaluated pages (node), a module-scoped fixture

NEW = {
    "fix.cc.callback": ("M27-form-callback", "M27-callbacks"),
    "fix.cc.voicemail": ("M27-form-voicemail", "M27-voicemails"),
    "fix.cc.oncall.rota": ("M27-form-oncall", "M27-oncall"),
    "fix.cc.contact.forecast": ("M27-form-forecast", "M27-forecasts"),
    "fix.cc.qa.calibration": ("M27-form-calibration", "M27-calibrations"),
    "fix.cc.qa.coaching": ("M27-form-coaching", "M27-coaching"),
    "fix.cc.notif.throttle": ("M27-form-throttle", "M27-throttles"),
    "fix.cc.channel.preference": ("M27-form-channel-pref", "M27-channel-prefs"),
    "fix.cc.urgency.challenge": ("M27-form-challenge", "M27-challenges"),
}
# page -> {chip label: model} the page must now offer
EXPECTED = {
    "1": {
        "Callback Request": "fix.cc.callback",
        "Voicemail": "fix.cc.voicemail",
        "On-Call Slot": "fix.cc.oncall.rota",
    },
    "6": {"Volume Forecast": "fix.cc.contact.forecast"},
    "7": {"Calibration Session": "fix.cc.qa.calibration", "Coaching Session": "fix.cc.qa.coaching"},
    "8": {"Notification Throttle": "fix.cc.notif.throttle"},
    "9": {
        "Notification Preference": "fix.cc.channel.preference",
        "Classification Challenge": "fix.cc.urgency.challenge",
    },
}


def _model_fields():
    """{model: {field: {required, default}}} from the cd_contact_centre sources."""
    out = {}
    for path in (CC / "models").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            name = None
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and stmt.targets[0].id in ("_name", "_inherit")
                    and isinstance(stmt.value, ast.Constant)
                    and name is None
                ):
                    name = stmt.value.value
            if not name:
                continue
            for stmt in node.body:
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Name)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Attribute)
                    and isinstance(stmt.value.func.value, ast.Name)
                    and stmt.value.func.value.id == "fields"
                ):
                    kw = {k.arg: k.value for k in stmt.value.keywords}
                    req = kw.get("required")
                    out.setdefault(name, {})[stmt.targets[0].id] = {
                        "required": isinstance(req, ast.Constant) and req.value is True,
                        "default": "default" in kw or "related" in kw or "compute" in kw,
                    }
    return out


def _surfaces():
    tree = ast.parse(CONTROLLER.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "SURFACES":
            return ast.literal_eval(node.value)
    raise AssertionError("no SURFACES")


# ---------------------------------------------------------------- registry
def test_each_page_offers_the_capture_the_spec_names_there(m27):
    pages = {s["no"]: s for s in m27["subs"]}
    for no, chips in EXPECTED.items():
        offered = {f["f"]: f for f in pages[no]["forms"]}
        for label, model in chips.items():
            assert label in offered, "page %s has no %s chip" % (no, label)
            chip = offered[label]
            assert chip["model"] == model and chip["opens"], (no, chip)


def test_each_new_record_is_listed_on_its_page_and_in_the_nav(m27):
    pages = {s["no"]: s for s in m27["subs"]}
    for no, chips in EXPECTED.items():
        for model in chips.values():
            screen = NEW[model][1]
            assert screen in pages[no]["screens"], (no, screen)
            assert m27["screens"][screen]["kind"] == "model_list"
            assert m27["screens"][screen]["model"] == model
            assert m27["screens"][screen]["empty"], screen
            assert screen in m27["nav"], screen
            assert m27["by_screen"][screen] == NEW[model][0]


def test_digital_channels_log_sms_and_social(m27):
    pages = {s["no"]: s for s in m27["subs"]}
    assert ["channel", "in", ["whatsapp", "chat", "email", "in_app", "sms", "social"]] in pages[
        "2"
    ]["domain"]
    form = m27["screens"]["M27-form-digital"]
    choices = {c[0] for f in form["fields"] if f["name"] == "channel" for c in f["choices"]}
    assert {"sms", "social"} <= choices
    src = (CC / "models" / "fix_contact_centre.py").read_text(encoding="utf-8")
    assert '("sms", "SMS")' in src and '("social", "Social Messaging")' in src


def test_every_form_field_exists_on_its_model_and_no_required_field_is_missing(m27):
    fields_by_model = _model_fields()
    for model, (form_id, _list) in NEW.items():
        form = m27["screens"][form_id]
        assert form["kind"] == "model_form" and form["model"] == model
        on_form = {f["name"] for f in form["fields"]}
        known = fields_by_model[model]
        assert on_form <= set(known), "%s: unknown %s" % (form_id, sorted(on_form - set(known)))
        for name, spec in known.items():
            if spec["required"] and not spec["default"]:
                assert name in on_form, "%s cannot save: %s is not on it" % (form_id, name)
    lines = fields_by_model["fix.cc.qa.calibration.line"]
    assert {"evaluator_id", "score"} <= set(lines)


def test_each_new_model_is_served_with_its_list_actions_and_pickers(m27):
    surfaces = _surfaces()
    for model, (_form, screen) in NEW.items():
        assert model in surfaces, model
        acts = set(m27["screens"][screen]["actions"])
        assert acts <= surfaces[model]["actions"], (model, acts - surfaces[model]["actions"])
        assert "pickers" in surfaces[model], "%s offers unfiltered pickers" % model
    assert "fix.cc.qa.calibration.line" in surfaces
    assert surfaces["fix.cc.urgency.challenge"]["pickers"]["delivery_id"] == [
        ("state", "in", ("sent", "delivered", "dry_run"))
    ]
    writable = _pass1._writable()
    assert "state" not in writable["fix.cc.callback"]
    assert "agreed_score" not in writable["fix.cc.qa.calibration"]
    assert "line_ids" in writable["fix.cc.qa.calibration"]


def test_access_rows_and_isolation_rules_are_declared():
    rows = list(csv.DictReader((CC / "security" / "ir.model.access.csv").open(encoding="utf-8")))
    by_model = {}
    for row in rows:
        by_model.setdefault(row["model_id:id"], []).append(row)
    for model in [*NEW, "fix.cc.qa.calibration.line"]:
        assert by_model.get("model_" + model.replace(".", "_")), model
    # configuration is the supervisor's: agents read it only
    for model in ("fix_cc_oncall_rota", "fix_cc_notif_throttle"):
        user = [r for r in by_model["model_" + model] if r["group_id:id"] == "base.group_user"]
        assert user and user[0]["perm_write"] == "0" and user[0]["perm_create"] == "0", model
    rules = (CC / "security" / "fix_isolation_rules.xml").read_text(encoding="utf-8")
    for model in NEW:
        assert 'ref="model_%s"' % model.replace(".", "_") in rules, model
    manifest = (CC / "__manifest__.py").read_text(encoding="utf-8")
    assert "data/fix_cc_capture2_data.xml" in manifest


# ---------------------------------------------------------------- live ORM
_SEQ = itertools.count(1)
SUPERVISOR = "cd_contact_centre.group_cc_supervisor"


class FakeRequest:
    def __init__(self, env):
        self.env = env


@pytest.fixture
def call():
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    patchers = []

    def _call(env, route, **kw):
        p = mock.patch.object(api, "request", FakeRequest(env))
        p.start()
        patchers.append(p)
        return getattr(api.P03GenericApiController(), route)(**kw)

    yield _call
    for p in patchers:
        p.stop()


@pytest.fixture
def ou(odoo_env):
    return odoo_env["operating.unit"].search([], limit=1)


def _user(env, ou, *xmlids):
    n = next(_SEQ)
    groups = [env.ref("base.group_user").id] + [env.ref(x).id for x in xmlids]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "M27 Pass2 User %d" % n,
                "login": "m27.pass2.%d@a03.test" % n,
                "group_ids": [(6, 0, groups)],
                "operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )
    return env(user=user.id)


@pytest.fixture
def agent(odoo_env, ou):
    return _user(odoo_env, ou)


@pytest.fixture
def supervisor(odoo_env, ou):
    return _user(odoo_env, ou, SUPERVISOR)


@pytest.fixture
def supervisor2(odoo_env, ou):
    return _user(odoo_env, ou, SUPERVISOR)


@pytest.fixture
def queue(odoo_env):
    return odoo_env["fix.cc.queue"].create(
        {"name": "M27 Pass2 Queue %d" % next(_SEQ), "code": "M27P2Q%d" % next(_SEQ)}
    )


@pytest.fixture
def partner(odoo_env):
    return odoo_env["res.partner"].create(
        {"name": "M27 Pass2 Customer %d" % next(_SEQ), "phone": "0171%07d" % (7000000 + next(_SEQ))}
    )


def _ok(res):
    assert "id" in res or res.get("success"), res
    return res


def _refused(res):
    assert "error" in res and not res.get("success"), res
    return res["error"]


def _ts(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _local(env, dt):
    """A UTC moment as the workspace form sends it: in the user's timezone."""
    import pytz
    from odoo.addons.cd_p03_portal.controllers import p03_generic_api as api

    return _ts(pytz.utc.localize(dt).astimezone(api._user_tz(env)).replace(tzinfo=None))


# page 1 -------------------------------------------------------------------
def test_callback_is_captured_attempted_and_honoured_in_its_window(call, agent, partner):
    now = datetime.utcnow()
    res = _ok(
        call(
            agent,
            "model_write",
            model="fix.cc.callback",
            values={
                "phone": partner.phone,
                "partner_id": partner.id,
                "reason": "Wants the repair estimate explained",
                "promised_from": _local(agent, now - timedelta(minutes=30)),
                "promised_by": _local(agent, now + timedelta(hours=2)),
            },
        )
    )
    cb = agent["fix.cc.callback"].browse(res["id"])
    assert cb.state == "requested"
    no_note = call(
        agent,
        "model_action",
        model="fix.cc.callback",
        ids=[cb.id],
        method="action_log_failed_attempt",
        kwargs={"note": ""},
    )
    assert "what happened" in _refused(no_note).lower()
    _ok(
        call(
            agent,
            "model_action",
            model="fix.cc.callback",
            ids=[cb.id],
            method="action_log_failed_attempt",
            kwargs={"note": "No answer"},
        )
    )
    _ok(
        call(
            agent,
            "model_action",
            model="fix.cc.callback",
            ids=[cb.id],
            method="action_mark_reached",
        )
    )
    cb.invalidate_recordset()
    assert cb.state == "completed" and cb.attempt_count == 2 and cb.within_window
    typed = call(
        agent,
        "model_write",
        model="fix.cc.callback",
        record_id=cb.id,
        values={"state": "requested"},
    )
    cb.invalidate_recordset()
    assert cb.state == "completed", typed


def test_a_passed_callback_window_is_marked_missed(odoo_env, agent):
    now = datetime.utcnow()
    cb = agent["fix.cc.callback"].create(
        {
            "phone": "01711999001",
            "reason": "Status",
            "promised_from": now - timedelta(hours=3),
            "promised_by": now - timedelta(hours=1),
        }
    )
    assert odoo_env["fix.cc.callback"]._cron_mark_missed() >= 1
    cb.invalidate_recordset()
    assert cb.state == "missed"
    with pytest.raises(Exception, match="after"), odoo_env.cr.savepoint():
        agent["fix.cc.callback"].create(
            {"phone": "0171", "reason": "x", "promised_from": now, "promised_by": now}
        )


def test_voicemail_is_queued_as_a_conversation(call, agent, ou, queue):
    # a Thursday 23:00 BST message is due Sunday (Friday and Saturday are not business days)
    received = datetime(2026, 11, 19, 17, 0, 0)
    res = _ok(
        call(
            agent,
            "model_write",
            model="fix.cc.voicemail",
            values={
                "caller_number": "01811222333",
                "received_at": _ts(received),
                "operating_unit_id": ou.id,
                "queue_id": queue.id,
                "transcript": "My fridge is still not repaired, please call me.",
            },
        )
    )
    vm = agent["fix.cc.voicemail"].browse(res["id"])
    assert vm.respond_by == date(2026, 11, 22)
    _ok(
        call(
            agent,
            "model_action",
            model="fix.cc.voicemail",
            ids=[vm.id],
            method="action_queue_as_conversation",
        )
    )
    vm.invalidate_recordset()
    conv = vm.conversation_id
    assert vm.state == "queued" and conv.channel == "voice" and conv.state == "new"
    assert conv.queue_id == queue and conv.contact_identity == "01811222333"
    assert conv.turn_ids and conv.turn_ids[0].speaker == "customer"
    again = call(
        agent,
        "model_action",
        model="fix.cc.voicemail",
        ids=[vm.id],
        method="action_queue_as_conversation",
    )
    assert "already" in _refused(again)


def test_oncall_rota_is_the_supervisors_and_named_by_a_closed_queue(
    call, odoo_env, agent, supervisor, queue
):
    now = datetime.utcnow()
    vals = {
        "queue_id": queue.id,
        "user_id": supervisor.uid,
        "on_call_phone": "01700000016",
        "role": "primary",
        "start_at": _ts(now - timedelta(hours=1)),
        "end_at": _ts(now + timedelta(hours=8)),
    }
    _refused(call(agent, "model_write", model="fix.cc.oncall.rota", values=vals))
    _ok(call(supervisor, "model_write", model="fix.cc.oncall.rota", values=vals))
    clash = call(supervisor, "model_write", model="fix.cc.oncall.rota", values=dict(vals))
    assert "already has a primary" in _refused(clash)
    # shut the queue for the whole day: its diversion now names the person on call
    queue.write({"opens_hour": 0, "closes_hour": 0, "closed_action": "voicemail"})
    diversion = queue.current_diversion()
    assert diversion and diversion["oncall_phone"] == "01700000016"
    assert "On call:" in diversion["reason"]


# page 2 -------------------------------------------------------------------
def test_an_inbound_sms_contact_is_logged(call, agent, ou):
    res = _ok(
        call(
            agent,
            "model_write",
            model="fix.conversation",
            values={
                "channel": "sms",
                "contact_identity": "01911000111",
                "operating_unit_id": ou.id,
                "started_at": "2026-11-19 04:00:00",
            },
        )
    )
    assert agent["fix.conversation"].browse(res["id"]).channel == "sms"


# page 6 -------------------------------------------------------------------
def test_forecast_is_scored_against_the_contacts_that_arrived(call, odoo_env, agent, ou):
    day = date(2026, 11, 18)
    # 10:00-11:00 BST = 04:00-05:00 UTC
    for minute in (5, 40):
        odoo_env["fix.conversation"].create(
            {
                "channel": "social",
                "contact_identity": "fb:%d" % next(_SEQ),
                "operating_unit_id": ou.id,
                "started_at": datetime(2026, 11, 18, 4, minute),
            }
        )
    res = _ok(
        call(
            agent,
            "model_write",
            model="fix.cc.contact.forecast",
            values={
                "forecast_date": "2026-11-18",
                "interval_hour": 10,
                "channel": "social",
                "forecast_volume": 4,
                "basis": "judgement",
            },
        )
    )
    fc = agent["fix.cc.contact.forecast"].browse(res["id"])
    assert fc.actual_volume == 2 and fc.variance_pct == 100.0
    assert fc.forecast_date == day
    dup = call(
        agent,
        "model_write",
        model="fix.cc.contact.forecast",
        values={
            "forecast_date": "2026-11-18",
            "interval_hour": 10,
            "channel": "social",
            "forecast_volume": 5,
            "basis": "history",
        },
    )
    _refused(dup)


# page 7 -------------------------------------------------------------------
def _closed_conversation(env, ou, handler):
    return (
        env["fix.conversation"]
        .sudo()
        ._guarded()
        .create(
            {
                "channel": "voice",
                "contact_identity": "0171%07d" % next(_SEQ),
                "operating_unit_id": ou.id,
                "state": "resolved_agent",
                "agent_id": handler.uid,
            }
        )
    )


def test_calibration_compares_evaluators_and_a_supervisor_closes_it(
    call, odoo_env, agent, supervisor, ou
):
    handler = _user(odoo_env, ou)
    evaluator2 = _user(odoo_env, ou)
    conv = _closed_conversation(odoo_env, ou, handler)
    res = _ok(
        call(
            agent,
            "model_write",
            model="fix.cc.qa.calibration",
            values={
                "name": "Week 47 calibration",
                "conversation_id": conv.id,
                "facilitator_id": supervisor.uid,
                "session_date": "2026-11-19",
                "tolerance": 10,
            },
            lines={
                "field": "line_ids",
                "rows": [{"values": {"evaluator_id": agent.uid, "score": 80}}],
            },
        )
    )
    session = agent["fix.cc.qa.calibration"].browse(res["id"])
    # an evaluator cannot enter a score in someone else's name
    with pytest.raises(Exception, match="own calibration score"), odoo_env.cr.savepoint():
        agent["fix.cc.qa.calibration.line"].create(
            {"session_id": session.id, "evaluator_id": evaluator2.uid, "score": 60}
        )
    # the agent who handled it cannot calibrate it
    with pytest.raises(Exception, match="handled the interaction"), odoo_env.cr.savepoint():
        handler["fix.cc.qa.calibration.line"].create(
            {"session_id": session.id, "evaluator_id": handler.uid, "score": 90}
        )
    one = call(
        supervisor,
        "model_action",
        model="fix.cc.qa.calibration",
        ids=[session.id],
        method="action_close",
        kwargs={"agreed_score": ""},
    )
    assert "two evaluators" in _refused(one)
    evaluator2["fix.cc.qa.calibration.line"].create(
        {"session_id": session.id, "evaluator_id": evaluator2.uid, "score": 62}
    )
    session.invalidate_recordset()
    assert session.spread == 18 and not session.consistent and session.mean_score == 71.0
    by_agent = call(
        agent,
        "model_action",
        model="fix.cc.qa.calibration",
        ids=[session.id],
        method="action_close",
        kwargs={"agreed_score": "70"},
    )
    assert "Supervisor" in _refused(by_agent)
    _ok(
        call(
            supervisor,
            "model_action",
            model="fix.cc.qa.calibration",
            ids=[session.id],
            method="action_close",
            kwargs={"agreed_score": "70"},
        )
    )
    session.invalidate_recordset()
    assert session.state == "closed" and session.agreed_score == 70
    with pytest.raises(Exception, match="evidence"), odoo_env.cr.savepoint():
        session.line_ids[0].with_env(odoo_env).write({"score": 99})


def test_coaching_tracks_improvement_and_is_acknowledged_by_the_agent(
    call, odoo_env, agent, supervisor, ou
):
    conv = _closed_conversation(odoo_env, ou, agent)
    ev = odoo_env["fix.cc.qa.evaluation"].create(
        {
            "conversation_id": conv.id,
            "agent_id": agent.uid,
            "score": 60,
            "evaluated_at": datetime(2026, 11, 10, 6, 0),
        }
    )
    self_coach = call(
        agent,
        "model_write",
        model="fix.cc.qa.coaching",
        values={
            "agent_id": agent.uid,
            "coach_id": agent.uid,
            "focus_area": "Hold etiquette",
            "agreed_actions": "Ask before hold",
            "session_date": "2026-11-12",
        },
    )
    assert "coach themselves" in _refused(self_coach)
    res = _ok(
        call(
            supervisor,
            "model_write",
            model="fix.cc.qa.coaching",
            values={
                "agent_id": agent.uid,
                "coach_id": supervisor.uid,
                "evaluation_id": ev.id,
                "focus_area": "Hold etiquette",
                "agreed_actions": "Ask before every hold",
                "session_date": "2026-11-12",
            },
        )
    )
    odoo_env["fix.cc.qa.evaluation"].create(
        {
            "conversation_id": conv.id,
            "agent_id": agent.uid,
            "score": 84,
            "evaluated_at": datetime(2026, 11, 15, 6, 0),
        }
    )
    coaching = agent["fix.cc.qa.coaching"].browse(res["id"])
    assert coaching.baseline_score == 60 and coaching.later_count == 1
    assert coaching.improvement == 24.0
    by_coach = call(
        supervisor,
        "model_action",
        model="fix.cc.qa.coaching",
        ids=[coaching.id],
        method="action_acknowledge",
    )
    assert "coached agent" in _refused(by_coach)
    _ok(
        call(
            agent,
            "model_action",
            model="fix.cc.qa.coaching",
            ids=[coaching.id],
            method="action_acknowledge",
        )
    )


# page 8 -------------------------------------------------------------------
def test_a_throttle_defers_the_message_over_the_ceiling(call, odoo_env, agent, supervisor, partner):
    vals = {"purpose": "marketing", "max_messages": 1, "period_hours": 24}
    _refused(call(agent, "model_write", model="fix.cc.notif.throttle", values=vals))
    _ok(call(supervisor, "model_write", model="fix.cc.notif.throttle", values=vals))
    Delivery = odoo_env["fix.notif.delivery"]
    first = Delivery.queue(
        "sms", "marketing", partner=partner, body="Offer 1", lawful_basis="contract"
    )
    second = Delivery.queue(
        "sms", "marketing", partner=partner, body="Offer 2", lawful_basis="contract"
    )
    assert first.state == "queued" and not first.throttle_id
    assert second.state == "queued" and second.throttle_id
    assert second.next_attempt_at >= first.queued_at + timedelta(hours=24)
    # a repair milestone is never throttled
    update = Delivery.queue(
        "sms", "service_updates", partner=partner, body="Ready", lawful_basis="contract"
    )
    assert update.state == "queued" and not update.throttle_id


# page 9 -------------------------------------------------------------------
def test_preference_opt_out_is_enforced_at_send_but_not_for_mandatory(
    call, odoo_env, agent, partner
):
    mandatory = call(
        agent,
        "model_write",
        model="fix.cc.channel.preference",
        values={
            "partner_id": partner.id,
            "category": "service_updates",
            "opted_out": True,
            "source": "hotline",
        },
    )
    assert "mandatory" in _refused(mandatory)
    _ok(
        call(
            agent,
            "model_write",
            model="fix.cc.channel.preference",
            values={
                "partner_id": partner.id,
                "category": "marketing",
                "opted_out": True,
                "source": "hotline",
            },
        )
    )
    Delivery = odoo_env["fix.notif.delivery"]
    promo = Delivery.queue(
        "sms", "marketing", partner=partner, body="Offer", lawful_basis="contract"
    )
    assert promo.state == "suppressed" and promo.consent_decision == "preference_opt_out"
    assert promo.preference_id.category == "marketing"
    update = Delivery.queue(
        "sms", "service_updates", partner=partner, body="Ready", lawful_basis="contract"
    )
    assert update.state == "queued"


def test_a_classification_challenge_is_decided_by_another_supervisor(
    call, odoo_env, agent, supervisor, supervisor2, partner
):
    sent = odoo_env["fix.notif.delivery"].queue(
        "sms",
        "service_updates",
        partner=partner,
        body="Big sale this week!",
        lawful_basis="contract",
    )
    sent.sudo()._guarded().write({"state": "sent"})
    same = call(
        supervisor,
        "model_write",
        model="fix.cc.urgency.challenge",
        values={
            "delivery_id": sent.id,
            "proposed_class": "transactional_routine",
            "reason": "Looks fine",
        },
    )
    assert "different classification" in _refused(same)
    res = _ok(
        call(
            supervisor,
            "model_write",
            model="fix.cc.urgency.challenge",
            values={
                "delivery_id": sent.id,
                "proposed_class": "promotional",
                "reason": "A sale announcement sent as a service update",
            },
        )
    )
    ch = agent["fix.cc.urgency.challenge"].browse(res["id"])
    assert ch.claimed_class == "transactional_routine"
    by_agent = call(
        agent,
        "model_action",
        model="fix.cc.urgency.challenge",
        ids=[ch.id],
        method="action_uphold",
        kwargs={"note": "agree"},
    )
    assert "Supervisor" in _refused(by_agent)
    own = call(
        supervisor,
        "model_action",
        model="fix.cc.urgency.challenge",
        ids=[ch.id],
        method="action_uphold",
        kwargs={"note": "agree"},
    )
    assert "raised" in _refused(own)
    _ok(
        call(
            supervisor2,
            "model_action",
            model="fix.cc.urgency.challenge",
            ids=[ch.id],
            method="action_uphold",
            kwargs={"note": "Promotional copy; referred to the M01 owner"},
        )
    )
    ch.invalidate_recordset()
    assert ch.state == "upheld" and ch.decided_by_id.id == supervisor2.uid
