"""Notification dispatcher tests — P04-M05 (FF-23 companion for CD-M27-nn).

Every numbered rule gets a test: QH-01…QH-04 windows, NT-003 §2.2 caps,
BD-01/02/03 routing, CH-04/CH-06 channel rules, NT-001 §4 fallbacks and the
never-silent-drop guarantee. All channel adapters are dry-run (unconfigured),
so no test can send anything anywhere.
"""
from __future__ import annotations

import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "libs" / "py"))

from src import kpis  # noqa: E402
from src.channels import SMSChannel, SendRefused  # noqa: E402
from src.delivery import FALLBACK_REGISTER  # noqa: E402
from src.dispatcher import Dispatcher, load_registry  # noqa: E402
from src.policy import DHAKA_TZ, RecipientState, evaluate, rules_from_registry  # noqa: E402
from src.router import INTERNAL_AUDIENCES, Router, RoutingError  # noqa: E402

REGISTRY = load_registry()
RULES = rules_from_registry(REGISTRY)


def at_dhaka(hour: int, minute: int = 0) -> datetime:
    day = datetime(2026, 3, 2, tzinfo=DHAKA_TZ)  # a Monday
    return day.replace(hour=hour, minute=minute)


def customer(party_id: int = 1, **kwargs) -> RecipientState:
    return RecipientState(party_id=party_id, **kwargs)


class TestRegistry(unittest.TestCase):
    def test_all_26_nt_files_registered(self):
        self.assertEqual(len(REGISTRY["library_files"]), 26)
        self.assertEqual(set(REGISTRY["library_files"]), {f"NT-{i:03d}" for i in range(1, 27)})

    def test_every_body_event_exists_in_matrix(self):
        matrix_events = set(REGISTRY["event_matrix"])
        for key, body in REGISTRY["bodies"].items():
            if isinstance(body, dict):
                self.assertIn(body["event"], matrix_events, f"body {key} has no matrix row")

    def test_consent_class_rules_complete(self):
        self.assertEqual(set(RULES), {"security", "transactional", "service", "marketing"})


class TestWindows(unittest.TestCase):
    def test_qh01_security_never_delayed(self):
        rule = RULES["security"]
        for hour in (0, 2, 13, 23):
            self.assertEqual(evaluate(rule, customer(), now=at_dhaka(hour), channel="sms").action, "send")

    def test_qh01_transactional_24_7(self):
        rule = RULES["transactional"]
        verdict = evaluate(rule, customer(), now=at_dhaka(3), channel="sms")
        self.assertEqual(verdict.action, "send")

    def test_qh02_service_held_outside_window_not_dropped(self):
        rule = RULES["service"]
        verdict = evaluate(rule, customer(), now=at_dhaka(22), channel="sms")  # window ends 21:00
        self.assertEqual(verdict.action, "hold")
        self.assertIsNotNone(verdict.hold_until)

    def test_qh02_marketing_window_10_to_20(self):
        rule = RULES["marketing"]
        self.assertEqual(evaluate(rule, customer(), now=at_dhaka(9), channel="sms").action, "hold")
        self.assertEqual(evaluate(rule, customer(), now=at_dhaka(11), channel="sms").action, "send")
        self.assertEqual(evaluate(rule, customer(), now=at_dhaka(21), channel="sms").action, "hold")

    def test_qh03_stale_held_discarded(self):
        rule = RULES["service"]
        event_time = at_dhaka(21) - timedelta(hours=30)
        verdict = evaluate(rule, customer(), now=at_dhaka(21), channel="sms",
                           stale_after_hours=24, event_time=event_time)
        self.assertEqual(verdict.action, "discard")
        self.assertIn("QH-03", verdict.reason)

    def test_qh04_timezone_is_dhaka(self):
        # 15:00 UTC == 21:00 Dhaka — service window closes at 21:00.
        utc = datetime(2026, 3, 2, 15, tzinfo=timezone.utc)
        rule = RULES["service"]
        verdict = evaluate(rule, customer(), now=utc, channel="sms")
        self.assertEqual(verdict.action, "hold")


class TestCapsAndConsent(unittest.TestCase):
    def test_service_cap_3_per_7_days(self):
        rule = RULES["service"]
        now = at_dhaka(12)
        sent = customer()
        sent.sent = [("service", now - timedelta(days=d)) for d in (1, 2, 3)]
        verdict = evaluate(rule, sent, now=now, channel="sms")
        self.assertEqual(verdict.action, "suppress")
        self.assertEqual(verdict.reason, "frequency-cap")

    def test_marketing_cap_2_per_7_days(self):
        rule = RULES["marketing"]
        now = at_dhaka(12)
        sent = customer()
        sent.sent = [("marketing", now - timedelta(days=1))] * 2
        self.assertEqual(evaluate(rule, sent, now=now, channel="sms").action, "suppress")

    def test_combined_cap_4_non_transactional(self):
        rule = RULES["service"]
        now = at_dhaka(12)
        sent = customer()
        sent.sent = [("service", now - timedelta(days=1))] * 2 + [("marketing", now - timedelta(days=2))] * 2
        self.assertEqual(evaluate(rule, sent, now=now, channel="sms").reason, "frequency-cap")

    def test_transactional_uncapped(self):
        rule = RULES["transactional"]
        now = at_dhaka(12)
        sent = customer()
        sent.sent = [("transactional", now - timedelta(minutes=m)) for m in range(50)]
        self.assertEqual(evaluate(rule, sent, now=now, channel="sms").action, "send")

    def test_channel_optout_honoured_before_anything(self):
        rule = RULES["transactional"]
        recipient = customer(channel_preferences={"sms": False})
        verdict = evaluate(rule, recipient, now=at_dhaka(12), channel="sms")
        self.assertEqual(verdict.action, "suppress")
        self.assertEqual(verdict.reason, "opted-out:sms")

    def test_dnd_blocks_promotional_only(self):
        dnd = customer(dnd_registered=True)
        marketing = evaluate(RULES["marketing"], dnd, now=at_dhaka(12), channel="sms")
        self.assertEqual(marketing.action, "suppress")
        self.assertEqual(marketing.reason, "dnd")
        transactional = evaluate(RULES["transactional"], dnd, now=at_dhaka(3), channel="sms")
        self.assertEqual(transactional.action, "send")

    def test_default_language_is_bengali(self):
        self.assertEqual(customer().preferred_language, "bn")


class TestBDRouting(unittest.TestCase):
    def test_bd01_transactional_uses_masking(self):
        self.assertEqual(RULES["transactional"].sms_route, "masking")

    def test_bd02_marketing_never_masking(self):
        self.assertEqual(RULES["marketing"].sms_route, "non-masking")

    def test_bd03_promotional_message_cannot_carry_masking_signature(self):
        channel = SMSChannel()
        with self.assertRaises(SendRefused):
            channel.send("8801XXXXXXXXX", "Offer! -1000FiX", sms_route="non-masking")

    def test_ssrf_guard_refuses_non_allowlisted_local_host(self):
        channel = SMSChannel()
        channel.url = "http://evil.example.com/send"  # simulates a bad env var
        with self.assertRaises(SendRefused):
            channel.send("8801XXXXXXXXX", "x", sms_route="masking")

    def test_credentials_never_in_url(self):
        channel = SMSChannel()
        channel.url = "http://mailpit:8025/send?token=abc"
        with self.assertRaises(SendRefused):
            channel.send("8801XXXXXXXXX", "x", sms_route="masking")


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router(REGISTRY, active_wave="W1")

    def test_estimate_ready_carries_three_customer_channels(self):
        routings = {r.audience: r for r in self.router.resolve("service.order.estimate_ready")}
        self.assertEqual(routings["customer"].channels, ("sms", "push", "email"))

    def test_ch04_act_now_leads_with_push(self):
        routings = {r.audience: r for r in self.router.resolve("service.order.technician_enroute")}
        self.assertEqual(routings["customer"].channels[0], "push")

    def test_ch06_alert_channel_is_internal_only(self):
        # on_call receives the alert channel; no customer audience ever does.
        routings = self.router.resolve("system.integration_failed")
        on_call = next(r for r in routings if r.audience == "on_call")
        self.assertIn("alert", on_call.channels)
        for event in ("service.order.estimate_declined", "service.order.ready_for_collection"):
            for routing in self.router.resolve(event):
                self.assertNotIn("alert", routing.channels, f"{event}/{routing.audience}")

    def test_technician_keeps_push_per_nt016(self):
        routings = self.router.resolve("service.order.estimate_declined")
        technician = next(r for r in routings if r.audience == "technician")
        self.assertIn("push", technician.channels)

    def test_later_wave_event_refused(self):
        with self.assertRaises(RoutingError):
            self.router.resolve("procurement.po_issued")  # W3

    def test_unknown_event_refused(self):
        with self.assertRaises(RoutingError):
            self.router.resolve("not.an.event")

    def test_fallback_ladder_matches_nt001(self):
        self.assertEqual(self.router.fallbacks_for("sms"), ("email", "in_app"))
        self.assertEqual(self.router.fallbacks_for("push"), ("sms", "email"))


class TestDispatcher(unittest.TestCase):
    def make_dispatcher(self, now: datetime) -> Dispatcher:
        return Dispatcher(registry=REGISTRY, active_wave="W1", now=now)

    def event(self, event_type: str, recipients: list, variables: dict | None = None) -> dict:
        return {
            "event_type": event_type,
            "payload": {
                "recipients": recipients,
                "addresses": {"customer": "8801XXXXXXXXX"},
                "variables": variables or {},
                "event_time": datetime.now(timezone.utc).timestamp(),
            },
        }

    def test_w1_lifecycle_send_dry_run(self):
        dispatcher = self.make_dispatcher(at_dhaka(12))
        decisions = dispatcher.handle(self.event(
            "service.order.ready_for_collection",
            [{"audience": "customer", "party_id": 7}],
            {"customer_name": "Rahim", "tracking_ref": "TRK-1", "branch_name": "Gulshan"},
        ))
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["state"], "delivered")
        self.assertIn("dry-run", decisions[0]["reason"])  # unconfigured channels

    def test_held_at_night_for_service_class(self):
        dispatcher = self.make_dispatcher(at_dhaka(22))
        decisions = dispatcher.handle(self.event(
            "service.order.awaiting_parts",  # service class, window 08-21
            [{"audience": "customer", "party_id": 7}],
        ))
        self.assertEqual(decisions[0]["state"], "held")

    def test_transactional_sends_at_night(self):
        dispatcher = self.make_dispatcher(at_dhaka(2))
        decisions = dispatcher.handle(self.event(
            "service.order.ready_for_collection",  # transactional
            [{"audience": "customer", "party_id": 7}],
        ))
        self.assertEqual(decisions[0]["state"], "delivered")

    def test_unrouted_event_becomes_dead_letter_not_silence(self):
        dispatcher = self.make_dispatcher(at_dhaka(12))
        decisions = dispatcher.handle({"event_type": "not.an.event", "payload": {}})
        self.assertEqual(decisions[0]["state"], "dead")
        self.assertEqual(len(dispatcher.tracker.operational_tasks), 1)

    def test_kpis_exclude_otp(self):
        dispatcher = self.make_dispatcher(at_dhaka(12))
        dispatcher.handle(self.event("security.otp_requested",
                                     [{"audience": "audience_any", "party_id": 9}]))
        self.assertEqual(dispatcher.kpi_snapshot()["counts"]["total"], 0)


class TestDeliveryAndKpis(unittest.TestCase):
    def test_retry_once_per_channel(self):
        from src.delivery import DeliveryRecord, DeliveryTracker

        tracker = DeliveryTracker()
        record = tracker.open(event="e", party_id=1, recipient="r",
                              consent_class="transactional", language="bn", rendered="x")
        tracker.record_attempt(record, "sms", "failed")
        self.assertTrue(tracker.should_retry(record, "sms"))
        tracker.record_attempt(record, "sms", "failed")
        self.assertFalse(tracker.should_retry(record, "sms"))  # exactly one retry

    def test_all_channels_fail_raises_task_never_drops(self):
        from src.delivery import DeliveryTracker

        tracker = DeliveryTracker()
        record = tracker.open(event="e", party_id=1, recipient="r",
                              consent_class="transactional", language="bn", rendered="x")
        task = tracker.mark_dead(record, "all channels failed")
        self.assertEqual(task["task"], "notification.all_channels_failed")
        self.assertEqual(len(tracker.dead_letters), 1)

    def test_fallback_register_names_every_p0_channel(self):
        for integration in ("INT-010 SMS", "INT-012 WhatsApp", "INT-013 email"):
            self.assertIn(integration, FALLBACK_REGISTER)
            self.assertTrue(FALLBACK_REGISTER[integration])

    def test_channel_mix_and_rates(self):
        from src.delivery import DeliveryRecord

        records = []
        for i, channel in enumerate(["sms", "sms", "email", "push"]):
            record = DeliveryRecord(event="e", party_id=i, recipient="r",
                                    consent_class="transactional", language="bn", rendered="x")
            record.state, record.final_channel = "delivered", channel
            record.delivered_at = record.created_at + timedelta(milliseconds=100 + i * 50)
            records.append(record)
        held = DeliveryRecord(event="e", party_id=99, recipient="r",
                              consent_class="service", language="bn", rendered="x")
        held.state = "held"
        records.append(held)
        snap = kpis.snapshot(records)
        self.assertEqual(snap.delivery_rate, 1.0)  # held messages are undecided
        self.assertEqual(kpis.channel_mix(records), {"sms": 2, "email": 1, "push": 1})
        self.assertIsNotNone(snap.p95_latency_ms)


class TestProductionSsrfGuard(unittest.TestCase):
    """The audit's finding B: production mode previously only enforced
    https — a private/loopback destination passed. Now the host must
    resolve to a PUBLIC address (loopback/private/link-local/reserved all
    refused even over https — the SSRF guard's production half)."""

    def setUp(self):
        self._saved = os.environ.get("FIX_ENV")
        os.environ["FIX_ENV"] = "production"

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("FIX_ENV", None)
        else:
            os.environ["FIX_ENV"] = self._saved

    def _sms(self, url):
        channel = SMSChannel()
        channel.url = url
        return channel

    def test_private_v4_refused(self):
        with self.assertRaises(SendRefused):
            self._sms("https://10.0.0.5/send").send("88", "x", sms_route="masking")

    def test_loopback_refused(self):
        with self.assertRaises(SendRefused):
            self._sms("https://127.0.0.1/send").send("88", "x", sms_route="masking")

    def test_link_local_metadata_refused(self):
        with self.assertRaises(SendRefused):
            self._sms("https://169.254.169.254/latest").send("88", "x", sms_route="masking")

    def test_reason_names_the_guard(self):
        try:
            self._sms("https://10.1.2.3/send").send("88", "x", sms_route="masking")
            self.fail("expected SendRefused")
        except SendRefused as exc:
            self.assertIn("production SSRF guard", str(exc))


class TestInt011RedundantSMS(unittest.TestCase):
    """Test suite validating INT-011 redundant SMS secondary route and failover (CD-M02-06)."""

    def test_redundant_only_dry_run_when_unconfigured(self):
        old_env = os.environ.get("FIX_SMS_REDUNDANT_ONLY")
        try:
            os.environ["FIX_SMS_REDUNDANT_ONLY"] = "1"
            channel = SMSChannel()
            res = channel.send("8801700000000", "OTP code: 1234", sms_route="masking")
            self.assertEqual(res.status, "dry-run")
            self.assertIn("INT-011 redundant SMS dry-run", res.detail)
        finally:
            if old_env is None:
                os.environ.pop("FIX_SMS_REDUNDANT_ONLY", None)
            else:
                os.environ["FIX_SMS_REDUNDANT_ONLY"] = old_env

    def test_redundant_dispatch_with_mock_gateway(self):
        old_only = os.environ.get("FIX_SMS_REDUNDANT_ONLY")
        old_url = os.environ.get("FIX_SMS_REDUNDANT_GATEWAY_URL")
        try:
            os.environ["FIX_SMS_REDUNDANT_ONLY"] = "1"
            os.environ["FIX_SMS_REDUNDANT_GATEWAY_URL"] = "http://localhost:8080/sms/redundant"
            channel = SMSChannel()
            channel._post_gateway = lambda url, token, payload: {"id": "RED-998811"}

            res = channel.send("8801700000000", "Important alert", sms_route="masking")
            self.assertEqual(res.status, "delivered")
            self.assertEqual(res.provider_id, "RED-998811")
            self.assertIn("INT-011 redundant secondary gateway", res.detail)
        finally:
            if old_only is None:
                os.environ.pop("FIX_SMS_REDUNDANT_ONLY", None)
            else:
                os.environ["FIX_SMS_REDUNDANT_ONLY"] = old_only
            if old_url is None:
                os.environ.pop("FIX_SMS_REDUNDANT_GATEWAY_URL", None)
            else:
                os.environ["FIX_SMS_REDUNDANT_GATEWAY_URL"] = old_url

    def test_primary_failover_to_redundant_on_network_error(self):
        channel = SMSChannel()
        channel.url = "http://localhost:8069/primary_sms"
        channel.redundant_url = "http://localhost:8069/backup_sms"

        import urllib.error
        def failing_post(payload):
            raise urllib.error.URLError("Primary gateway unreachable")

        channel._post = failing_post
        channel._post_gateway = lambda url, token, payload: {"id": "FAILOVER-12345"}

        res = channel.send("8801700000000", "Critical field service dispatch", sms_route="masking")
        self.assertEqual(res.status, "delivered")
        self.assertEqual(res.provider_id, "FAILOVER-12345")
        self.assertIn("INT-011 failover", res.detail)


if __name__ == "__main__":
    unittest.main()
