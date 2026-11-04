"""Behavioural security tests for the P01 public routes (R01 re-audit 2026-10-22).

Runs against the live ORM (``odoo_env``: database fix_test, rolled back per test)
with ``odoo.http.request`` replaced by a minimal stand-in exposing ``env`` /
``session`` / ``update_env`` — the controller code itself runs unmodified. The
session is a real ``odoo.http.Session`` so OTP sign-in finalises it exactly as
the framework does. The SMS hand-off to the notification dispatcher is replaced
by a recorder (``dispatcher`` fixture): no packet leaves the test.
"""

import logging
from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from odoo import Command, http
from odoo.addons.cd_customer_portal.controllers import customer_api, otp_delivery
from odoo.addons.cd_customer_portal.controllers.customer_api import CustomerApiController
from odoo.exceptions import ValidationError

PHONE = "01712345678"


@pytest.fixture(autouse=True)
def dispatcher(monkeypatch):
    """Record every event POSTed to the dispatcher; answer 'delivered' (dry-run)."""
    monkeypatch.delenv(otp_delivery.DISPATCHER_URL_ENV, raising=False)
    sent = []

    def fake_post(url, payload):
        sent.append((url, payload))
        return {"decisions": [{"event": payload["event_type"], "state": "delivered"}]}

    monkeypatch.setattr(otp_delivery, "_post_json", fake_post)
    return sent


class _Browser:
    """One client: a user plus its own server-side session."""

    def __init__(self, env, user):
        self.env = env(user=user.id)
        self.session = http.Session(http.get_default_session(), f"sid-{id(self)}", new=True)

    def update_env(self, user=None, context=None, su=None):
        self.env = self.env(user=user, context=context, su=su)


@contextmanager
def _in(browser):
    with patch.object(customer_api, "request", browser):
        yield CustomerApiController()


@pytest.fixture
def world(odoo_env):
    env = odoo_env
    ou = env["operating.unit"].search([], limit=1)
    # fix.entity is UNIQUE per company: a dedicated company keeps this fixture
    # from queueing behind other suites' entity on the shared test database
    company = env["res.company"].create({"name": "Portal Security Test Co"})
    entity = env["fix.entity"].create(
        {"code": "SECENT", "legal_name": "Security Test Entity", "company_id": company.id}
    )
    branch = env["fix.branch"].create(
        {"name": "Sec Branch", "code": "SECB", "entity_id": entity.id, "operating_unit_id": ou.id}
    )
    brand = env["fix.brand"].create({"name": "SecBrand", "code": "SECBR"})
    device_model = env["fix.device.model"].create({"name": "SecPhone", "brand_id": brand.id})
    portal = env.ref("base.group_portal")
    users = env["res.users"].with_context(no_reset_password=True)
    alice = users.create(
        {"name": "Alice", "login": "alice@sec.test", "group_ids": [Command.set([portal.id])]}
    )
    bob = users.create(
        {"name": "Bob", "login": "bob@sec.test", "group_ids": [Command.set([portal.id])]}
    )
    staff = users.create({"name": "Staff", "login": "staff@sec.test"})

    def order_for(user, serial):
        device = env["fix.device"].create(
            {
                "device_model_id": device_model.id,
                "owner_id": user.partner_id.id,
                "serial_number": serial,
            }
        )
        return env["fix.service.order"].create(
            {
                "device_id": device.id,
                "customer_id": user.partner_id.id,
                "branch_id": branch.id,
                "fault_description": "Battery swelling",
            }
        )

    return SimpleNamespace(
        env=env,
        alice=alice,
        bob=bob,
        staff=staff,
        public=env.ref("base.public_user"),
        alice_order=order_for(alice, "SN-SEC-A"),
        bob_order=order_for(bob, "SN-SEC-B"),
    )


def _pending(browser):
    return browser.session.get(customer_api.OTP_SESSION_PREFIX + PHONE)


# --- OTP send ----------------------------------------------------------------------


def test_otp_send_issues_a_random_expiring_code_and_hides_it(world, monkeypatch):
    browser = _Browser(world.env, world.public)
    monkeypatch.delenv("FIX_ENV", raising=False)
    with _in(browser) as ctrl:
        sent = ctrl.otp_send(phone="+880 1712-345678")
        bare = ctrl.otp_send(phone="1812345678")  # 10 digits: the leading 0 is restored
        invalid = ctrl.otp_send(phone="12345")
    assert sent["sent"] is True
    assert sent["masked_phone"] == "017*****678"
    assert "dev_code" not in sent
    assert bare["phone"] == "01812345678"
    assert invalid["error"]["code"] == "invalid_phone"
    pending = _pending(browser)
    assert pending["attempts"] == 0
    assert len(pending["code"]) == 6
    assert pending["code"].isdigit()
    assert pending["expires_at"] == pending["issued_at"] + customer_api.OTP_TTL_SECONDS
    monkeypatch.setenv("FIX_ENV", "prod")
    with _in(_Browser(world.env, world.public)) as ctrl:
        prod = ctrl.otp_send(phone=PHONE)
    assert prod["sent"] is True
    assert "dev_code" not in prod


def test_otp_dev_code_is_echoed_only_in_the_local_environment(world, monkeypatch):
    browser = _Browser(world.env, world.public)
    monkeypatch.setenv("FIX_ENV", "local")
    with _in(browser) as ctrl:
        sent = ctrl.otp_send(phone=PHONE)
    assert sent["dev_code"] == _pending(browser)["code"]


# --- OTP delivery (notification dispatcher, NT-007) ----------------------------------


def test_otp_is_handed_to_the_dispatcher_sms_channel(world, dispatcher, monkeypatch):
    monkeypatch.delenv("FIX_ENV", raising=False)
    browser = _Browser(world.env, world.public)
    with _in(browser) as ctrl:
        ctrl.otp_send(phone=PHONE, lang="en")
    [(url, event)] = dispatcher
    assert url == "http://127.0.0.1:8110/consume/once"
    assert event["event_type"] == "security.otp_requested"
    assert event["payload"]["addresses"] == {"audience_any": "8801712345678"}
    assert event["payload"]["variables"]["code"] == _pending(browser)["code"]
    assert event["payload"]["variables"]["valid_minutes"] == customer_api.OTP_TTL_SECONDS // 60
    assert event["payload"]["recipients"][0]["preferred_language"] == "en"


def test_otp_never_reaches_the_event_bus_or_the_logs(world, monkeypatch, caplog):
    monkeypatch.setenv("FIX_ENV", "local")
    browser = _Browser(world.env, world.public)
    outbox = world.env["fix.event.outbox"]
    before = outbox.search([]).ids
    with caplog.at_level(logging.DEBUG), _in(browser) as ctrl:
        code = ctrl.otp_send(phone=PHONE)["dev_code"]
        ctrl.otp_verify(phone=PHONE, otp=code)
    new_events = outbox.search([("id", "not in", before)])
    assert all(code not in (e.payload or "") for e in new_events)
    assert all(code not in record.getMessage() for record in caplog.records)


def test_undeliverable_otp_is_refused_outside_local(world, dispatcher, monkeypatch, caplog):
    monkeypatch.setenv("FIX_ENV", "production")
    failure = otp_delivery.OtpDeliveryError("dispatcher unreachable (URLError)")
    browser = _Browser(world.env, world.public)
    with (
        patch.object(otp_delivery, "send_otp", side_effect=failure),
        caplog.at_level(logging.WARNING),
        _in(browser) as ctrl,
    ):
        res = ctrl.otp_send(phone=PHONE)
    assert res["error"]["code"] == "otp_unavailable"
    assert _pending(browser) is None  # nothing to verify against an unsent code
    assert "017*****678" in caplog.text
    assert PHONE not in caplog.text


def test_undeliverable_otp_still_works_with_the_local_dev_echo(world, monkeypatch, caplog):
    monkeypatch.setenv("FIX_ENV", "local")
    browser = _Browser(world.env, world.public)
    failure = otp_delivery.OtpDeliveryError("dispatcher unreachable (URLError)")
    with (
        patch.object(otp_delivery, "send_otp", side_effect=failure),
        caplog.at_level(logging.WARNING),
        _in(browser) as ctrl,
    ):
        res = ctrl.otp_send(phone=PHONE)
    assert res["dev_code"] == _pending(browser)["code"]
    assert "OTP SMS hand-off" in caplog.text
    assert res["dev_code"] not in caplog.text


def test_a_session_may_request_a_new_code_once_per_resend_window(world, dispatcher):
    browser = _Browser(world.env, world.public)
    _send(browser, "111111")
    with _in(browser) as ctrl:
        again = ctrl.otp_send(phone=PHONE)
    assert again["error"]["code"] == "otp_throttled"
    assert 0 < again["error"]["retry_after"] <= customer_api.OTP_RESEND_SECONDS
    assert _pending(browser)["code"] == "111111"  # the pending code is kept
    later = customer_api.time.time() + customer_api.OTP_RESEND_SECONDS + 1
    with (
        patch.object(customer_api, "time", SimpleNamespace(time=lambda: later)),
        _in(browser) as ctrl,
    ):
        renewed = ctrl.otp_send(phone=PHONE)
    assert renewed["sent"] is True
    assert len(dispatcher) == 2  # the throttled request sent no SMS


# --- OTP verify --------------------------------------------------------------------


def _send(browser, code="654321"):
    with (
        patch.object(customer_api, "secrets", SimpleNamespace(randbelow=lambda _n: int(code))),
        _in(browser) as ctrl,
    ):
        ctrl.otp_send(phone=PHONE)


def test_the_old_universal_code_and_unsolicited_codes_are_refused(world):
    browser = _Browser(world.env, world.public)
    with _in(browser) as ctrl:
        unsolicited = ctrl.otp_verify(phone=PHONE, otp="123456")
    _send(browser, "654321")
    with _in(browser) as ctrl:
        universal = ctrl.otp_verify(phone=PHONE, otp="123456")
        missing = ctrl.otp_verify(phone=PHONE)
    assert unsolicited["error"]["code"] == "invalid_otp"
    assert universal["error"]["code"] == "invalid_otp"
    assert missing["error"]["code"] == "missing_otp"
    assert browser.session.uid is None


def test_otp_attempts_are_limited(world):
    browser = _Browser(world.env, world.public)
    _send(browser, "654321")
    with _in(browser) as ctrl:
        codes = [
            ctrl.otp_verify(phone=PHONE, otp="000000")["error"]["code"]
            for _ in range(customer_api.OTP_MAX_ATTEMPTS)
        ]
        after = ctrl.otp_verify(phone=PHONE, otp="654321")
    assert codes[:-1] == ["invalid_otp"] * (customer_api.OTP_MAX_ATTEMPTS - 1)
    assert codes[-1] == "too_many_attempts"
    assert after["error"]["code"] == "invalid_otp"  # the code was burnt
    assert browser.session.uid is None


def test_otp_expires(world):
    browser = _Browser(world.env, world.public)
    _send(browser, "654321")
    later = customer_api.time.time() + customer_api.OTP_TTL_SECONDS + 1
    clock = SimpleNamespace(time=lambda: later)
    with patch.object(customer_api, "time", clock), _in(browser) as ctrl:
        res = ctrl.otp_verify(phone=PHONE, otp="654321")
    assert res["error"]["code"] == "invalid_otp"
    assert browser.session.uid is None


def test_otp_signs_into_the_phones_own_portal_account(world):
    browser = _Browser(world.env, world.public)
    _send(browser, "654321")
    with _in(browser) as ctrl:
        res = ctrl.otp_verify(phone=PHONE, otp="654321")
        replay = ctrl.otp_verify(phone=PHONE, otp="654321")
    user = world.env["res.users"].browse(res["user"]["uid"])
    assert res["verified"] is True
    assert user.login == PHONE
    assert user.share is True
    assert not user._is_internal()
    assert browser.session.uid == user.id
    assert browser.env.uid == user.id
    assert replay["error"]["code"] == "invalid_otp"  # single use
    # a second sign-in with the same phone reuses the same account
    again = _Browser(world.env, world.public)
    _send(again, "111111")
    with _in(again) as ctrl:
        second = ctrl.otp_verify(phone=PHONE, otp="111111")
    assert second["user"]["uid"] == user.id


def test_otp_never_signs_into_an_internal_account(world):
    world.staff.login = PHONE
    browser = _Browser(world.env, world.public)
    _send(browser, "654321")
    with _in(browser) as ctrl:
        res = ctrl.otp_verify(phone=PHONE, otp="654321")
    assert res["error"]["code"] == "auth_failed"
    assert browser.session.uid is None


def test_otp_for_a_malformed_phone_is_simply_invalid(world):
    browser = _Browser(world.env, world.public)
    with _in(browser) as ctrl:
        res = ctrl.otp_verify(phone="12345", otp="654321")
    assert res["error"]["code"] == "invalid_otp"
    assert browser.session.uid is None


def test_a_failed_portal_provisioning_is_a_generic_sign_in_failure(world, caplog):
    browser = _Browser(world.env, world.public)
    _send(browser, "654321")
    with (
        patch.object(
            customer_api, "_portal_user_for_phone", side_effect=ValidationError("login taken")
        ),
        caplog.at_level(logging.WARNING),
        _in(browser) as ctrl,
    ):
        res = ctrl.otp_verify(phone=PHONE, otp="654321")
    assert res["error"]["code"] == "auth_failed"
    assert "login taken" not in res["error"]["message"]
    assert "could not provision" in caplog.text
    assert browser.session.uid is None


def test_no_customer_route_declares_cors():
    """CORS terminates at the Kong gateway's explicit origin allow-list (P-11)."""
    routes = [
        member.original_routing
        for member in vars(CustomerApiController).values()
        if hasattr(member, "original_routing")
    ]
    assert len(routes) == 10
    assert all(r.get("cors") is None for r in routes), [
        r["routes"] for r in routes if r.get("cors")
    ]


# --- tracking ----------------------------------------------------------------------


def test_tracking_requires_ownership_staff_or_signed_token(world):
    order = world.alice_order
    with _in(_Browser(world.env, world.public)) as ctrl:
        anon_ref = ctrl.tracking(ref=order.name)
        anon_id = ctrl.tracking(order_id=order.id)
        forged = ctrl.tracking(ref=order.name, token="0" * 64)
        signed = ctrl.tracking(ref=order.name, token=customer_api.tracking_token(order))
        anon_list = ctrl.tracking()
    with _in(_Browser(world.env, world.bob)) as ctrl:
        bob_id = ctrl.tracking(order_id=order.id)
        bob_list = ctrl.tracking(partner_id=world.alice.partner_id.id)
    with _in(_Browser(world.env, world.alice)) as ctrl:
        own = ctrl.tracking(order_id=order.id)
    with _in(_Browser(world.env, world.staff)) as ctrl:
        staff = ctrl.tracking(ref=order.name)
        staff_list = ctrl.tracking(partner_id=world.alice.partner_id.id)
    for res in (anon_ref, anon_id, forged, bob_id):
        assert res["error"]["code"] == "no_order"
    assert signed["tracking"]["id"] == order.id
    assert own["tracking"]["id"] == order.id
    assert staff["tracking"]["id"] == order.id
    assert anon_list == {"orders": [], "total": 0}
    assert [o["id"] for o in bob_list["orders"]] == [world.bob_order.id]
    assert [o["id"] for o in staff_list["orders"]] == [order.id]


def test_tracking_refs_are_matched_literally(world):
    """Regression: ``ref`` went into ``=ilike`` unescaped, so ``%``/``_`` were
    wildcards matching some other order's reference."""
    order = world.alice_order
    order.legacy_reference = "LEG-SEC-42"
    with _in(_Browser(world.env, world.alice)) as ctrl:
        wildcard = ctrl.tracking(ref=order.name[:-1] + "_")
        everything = ctrl.tracking(ref="%")
        backslash = ctrl.tracking(ref="\\")
        legacy = ctrl.tracking(ref="leg-sec-42")
        exact = ctrl.tracking(ref=order.name.lower())
        junk_id = ctrl.tracking(order_id="not-a-number")
    for res in (wildcard, everything, backslash, junk_id):
        assert res["error"]["code"] == "no_order"
    assert legacy["tracking"]["id"] == order.id
    assert legacy["tracking"]["legacy_reference"] == "LEG-SEC-42"
    assert exact["tracking"]["ref"] == order.name


def test_partner_id_is_honoured_for_internal_users_only(world):
    # A07 P1 (2026-11-04) M17-6: acting for a customer on the device
    # endpoints is the Device Registry Agent's support view; a plain
    # internal login gets nothing.
    with _in(_Browser(world.env, world.staff)) as ctrl:
        plain = ctrl.devices(partner_id=world.alice.partner_id.id)
    assert plain["error"]["code"] == "not_permitted" and "devices" not in plain
    world.staff.group_ids = [
        Command.link(world.env.ref("cd_device_registry.group_device_registry_user").id)
    ]
    with _in(_Browser(world.env, world.bob)) as ctrl:
        devices = ctrl.devices(partner_id=world.alice.partner_id.id)
    assert {d["serial_number"] for d in devices["devices"]} == {"SN-SEC-B"}
    with _in(_Browser(world.env, world.staff)) as ctrl:
        support = ctrl.devices(partner_id=world.alice.partner_id.id)
    assert {d["serial_number"] for d in support["devices"]} == {"SN-SEC-A"}


# --- ORM-level portal ACL (authorization audit 2026-10-23) ---------------------------


def test_customer_portal_group_is_read_only_and_partner_scoped(world):
    """The P01 group reads only its own devices / orders / estimates / consent
    and cannot write or create any of them over RPC — the controllers perform
    the writes with sudo() after their own ownership checks."""
    from odoo.exceptions import AccessError

    env = world.env
    group = env.ref("cd_customer_portal.group_fix_customer_portal")
    world.alice.write({"group_ids": [Command.link(group.id)]})
    estimate = env["fix.estimate"].create({"order_id": world.alice_order.id})
    foreign_estimate = env["fix.estimate"].create({"order_id": world.bob_order.id})
    as_alice = env(user=world.alice.id)

    Order = as_alice["fix.service.order"]
    assert Order.search([("id", "in", [world.alice_order.id, world.bob_order.id])]) == (
        world.alice_order.with_env(as_alice)
    )
    Estimate = as_alice["fix.estimate"]
    assert Estimate.search([("id", "in", [estimate.id, foreign_estimate.id])]).ids == [estimate.id]

    for model in ("fix.service.order", "fix.estimate", "fix.device", "fix.consent"):
        Model = as_alice[model]
        assert Model.has_access("read")
        assert not Model.has_access("write"), model
        assert not Model.has_access("create"), model
    with pytest.raises(AccessError):
        world.alice_order.with_env(as_alice).write({"fault_description": "tampered"})
