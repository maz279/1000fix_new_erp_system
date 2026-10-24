"""payment-connectors tests — P06-M05 (T06 idempotency, T08 fallbacks, R04-M03 certification)."""

from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from payment_connectors import (
    PAYMENT_FALLBACK_REGISTER,
    GatewayError,
    PaymentRouter,
    Refused,
    RocketGateway,
    build_gateways,
    confirm,
    reset_store,
)
from sandbox_certifier import SandboxCertifier
from sandbox_stub import start_sandbox_stub


def _wired_sandbox_gateways(include_all: bool = True):
    """Sandbox-mode gateways pointed at the REAL in-process stub endpoint, so
    an end-to-end flow exercises the wire, not a canned simulation (GV-009)."""
    stub_url = start_sandbox_stub()
    gateways = build_gateways(include_all=include_all, sandbox_mode=True)
    for name, gateway in gateways.items():
        gateway.url = f"{stub_url}/{name}"
    return gateways


class TestDryRun(unittest.TestCase):
    def test_unconfigured_gateways_dry_run(self):
        for name, gateway in build_gateways().items():
            result = gateway.initiate(115000, "TRX-1", "https://callback")
            self.assertEqual(result.status, "dry-run", name)

    def test_all_three_p0_gateways_present(self):
        self.assertEqual(set(build_gateways()), {"bkash", "nagad", "sslcommerz"})

    def test_all_gateways_includes_rocket(self):
        all_gws = build_gateways(include_all=True)
        self.assertEqual(set(all_gws), {"bkash", "nagad", "sslcommerz", "rocket"})
        self.assertIsInstance(all_gws["rocket"], RocketGateway)


class TestSandboxCertification:
    """R04-M03 certification battery. GV-009: certification is only issued
    against a REAL reachable sandbox endpoint — with no URL the certifier
    refuses ("not certifiable"), and a passing battery is earned over the
    wire against the in-process stub."""

    def test_no_sandbox_url_is_not_certifiable(self):
        reset_store()
        report = SandboxCertifier().run_full_suite()
        assert report.overall_certified is False
        assert report.fallback_router_certified is False
        for gw in ("bkash", "nagad", "sslcommerz", "rocket"):
            gw_rep = report.gateway_reports[gw]
            assert gw_rep.certified is False
            assert (gw_rep.checks_passed, gw_rep.checks_total) == (0, 1)
            check = gw_rep.checks[0]
            assert check.name == "live_sandbox_endpoint"
            assert "not certifiable without a live sandbox endpoint" in check.detail

    def test_full_battery_certifies_against_a_live_sandbox_endpoint(self):
        reset_store()
        certifier = SandboxCertifier(_wired_sandbox_gateways())
        report = certifier.run_full_suite()
        assert report.overall_certified is True, report.to_json()
        assert report.fallback_router_certified is True

        for gw in ("bkash", "nagad", "sslcommerz", "rocket"):
            gw_rep = report.gateway_reports.get(gw)
            assert gw_rep is not None, f"Gateway {gw} missing report"
            assert gw_rep.certified, f"{gw} failed certification: {gw_rep.checks}"
            assert gw_rep.checks_passed == gw_rep.checks_total
            assert gw_rep.checks_total == 4  # initiate, query, confirm, refund


class TestReadBackResolution(unittest.TestCase):
    """IN-007 §5: The Read-Back Rule + GV-009: without a sandbox endpoint
    there is no provider ledger, so the gateway refuses instead of minting a
    "verified via sandbox read-back" confirmation."""

    def test_sandbox_without_url_refuses_instead_of_confirming(self):
        bkash = build_gateways(sandbox_mode=True)["bkash"]
        with self.assertRaises(GatewayError) as ctx:
            bkash.initiate(25000, "TRX-READBACK-01", "https://1000fix.local/cb")
        self.assertIn("refusing to simulate a gateway result", str(ctx.exception))
        with self.assertRaises(GatewayError):
            bkash.query("TRX-READBACK-01")

    def test_simulated_outage_readback_reports_unknown(self):
        bkash = build_gateways(sandbox_mode=True)["bkash"]

        # Simulated outage makes read-back report unknown (never a
        # false-negative failed) — outage simulation is honest, success is not.
        bkash.set_simulated_outage(True)
        outage_query = bkash.query("TRX-READBACK-01")
        self.assertEqual(outage_query.status, "unknown")
        bkash.set_simulated_outage(False)


def test_sandbox_read_back_confirms_over_the_wire():
    """IN-007 §5 with a REAL sandbox endpoint: initiation and the read-back
    query both resolve over HTTP — the confirmation comes from the stub's
    ledger response, not from a locally minted status."""
    bkash = _wired_sandbox_gateways()["bkash"]

    res = bkash.initiate(25000, "TRX-READBACK-WIRE", "https://1000fix.local/cb")
    assert res.status == "initiated"

    query_res = bkash.query("TRX-READBACK-WIRE")
    assert query_res.status == "confirmed"
    assert query_res.detail == "Paid TRX-READBACK-WIRE"


class TestFallbackRouterOutageSimulation:
    """T04 / IP-09: Live outage simulations testing multi-tier degradation.
    The gateways point at the REAL in-process sandbox stub: a cascade lands on
    a rail that genuinely initiated over the wire (GV-009)."""

    def _router(self):
        gateways = _wired_sandbox_gateways()
        return gateways, PaymentRouter(gateways)

    def test_bkash_outage_fails_over_to_nagad(self):
        gateways, router = self._router()
        gateways["bkash"].set_simulated_outage(True)
        res, trace = router.initiate_with_fallback(
            amount_cents=50000,
            trx_id="TRX-OUTAGE-01",
            callback_ref="https://1000fix.local/cb",
            preferred_rail="bkash",
        )
        assert (res.gateway, res.status) == ("nagad", "initiated")
        assert any("bkash" in t for t in trace)

    def test_bkash_and_nagad_outage_fails_over_to_sslcommerz(self):
        gateways, router = self._router()
        gateways["bkash"].set_simulated_outage(True)
        gateways["nagad"].set_simulated_outage(True)
        res, _trace = router.initiate_with_fallback(
            amount_cents=50000,
            trx_id="TRX-OUTAGE-02",
            callback_ref="https://1000fix.local/cb",
            preferred_rail="bkash",
        )
        assert (res.gateway, res.status) == ("sslcommerz", "initiated")

    def test_all_digital_rails_down_drops_to_manual_fallback(self):
        gateways, router = self._router()
        for gw in gateways.values():
            gw.set_simulated_outage(True)

        res, _trace = router.initiate_with_fallback(
            amount_cents=50000,
            trx_id="TRX-OUTAGE-03",
            callback_ref="https://1000fix.local/cb",
            preferred_rail="bkash",
        )
        assert res.status == "failed"
        assert "Manual Fallback" in res.detail


class TestIdempotentConfirmation(unittest.TestCase):
    def setUp(self):
        reset_store()
        # verified confirmations: each connector reads back from the stub
        self.gw = _wired_sandbox_gateways()

    def test_retried_confirmation_never_double_credits(self):
        first = confirm(self.gw["bkash"], "TRX-9", 115000)
        second = confirm(self.gw["bkash"], "TRX-9", 115000)
        third = confirm(self.gw["bkash"], "TRX-9", 115000)
        self.assertEqual(first.detail, "amount=115000 cents credited once")
        self.assertIn("idempotent replay", second.detail)
        self.assertIn("idempotent replay", third.detail)

    def test_different_trx_ids_credit_separately(self):
        confirm(self.gw["bkash"], "TRX-A", 100)
        confirm(self.gw["bkash"], "TRX-B", 100)
        self.assertIn("credited once", confirm(self.gw["bkash"], "TRX-C", 100).detail)

    def test_same_trx_different_gateway_are_distinct(self):
        confirm(self.gw["bkash"], "TRX-X", 100)
        self.assertIn("credited once", confirm(self.gw["nagad"], "TRX-X", 100).detail)

    def test_unverified_payment_is_never_confirmed(self):
        """Regression: confirm() credited on the caller's word without asking
        the gateway. An unconfigured connector (dry-run), an outage or a
        refused lookup now yields "unverified" and records nothing."""
        for gateway in ("bkash", build_gateways()["nagad"]):  # unconfigured: dry-run
            res = confirm(gateway, "TRX-NOGW", 100)
            self.assertEqual(res.status, "unverified")
        self.gw["bkash"].set_simulated_outage(True)
        res = confirm(self.gw["bkash"], "TRX-OUT", 100)
        self.assertEqual(res.status, "unverified")
        self.assertIn("'unknown'", res.detail)
        self.assertEqual(confirm("upay", "TRX-U", 1).status, "unverified")
        # nothing was credited, so a later verified confirmation still credits once
        self.gw["bkash"].set_simulated_outage(False)
        self.assertIn("credited once", confirm(self.gw["bkash"], "TRX-OUT", 100).detail)

    def test_concurrent_or_retried_confirmations_preserve_original_timestamp(self):
        first = confirm(self.gw["bkash"], "TRX-IDEMP-01", 10000)
        second = confirm(self.gw["bkash"], "TRX-IDEMP-01", 10000)
        self.assertEqual(first.status, "confirmed")
        self.assertEqual(second.status, "confirmed")
        self.assertEqual(first.timestamp, second.timestamp)
        self.assertIn("idempotent replay", second.detail)


class TestSsrfGuard(unittest.TestCase):
    def test_non_allowlisted_host_refused(self):
        gateways = build_gateways()
        gateways["bkash"].url = "http://evil.example.com/create"
        with self.assertRaises(Refused):
            gateways["bkash"].initiate(100, "TRX", "https://cb")

    def test_credentials_in_url_refused(self):
        gateways = build_gateways()
        gateways["nagad"].url = "http://localhost:1/pay?token=abc"
        with self.assertRaises(Refused):
            gateways["nagad"].initiate(100, "TRX", "https://cb")


class TestFallbackRegister(unittest.TestCase):
    def test_every_p0_payment_gateway_has_a_named_fallback(self):
        for key in ("INT-001 bKash", "INT-002 Nagad", "INT-003 SSLCOMMERZ"):
            self.assertIn(key, PAYMENT_FALLBACK_REGISTER)
            self.assertTrue(PAYMENT_FALLBACK_REGISTER[key])


class TestNoCredentialLiterals(unittest.TestCase):
    def test_source_has_no_hardcoded_secret_values(self):
        source = (Path(__file__).resolve().parents[1] / "src" / "payment_connectors.py").read_text(
            encoding="utf-8"
        )
        secrets = re.findall(
            r'(?:key|token|secret)\s*=\s*["\'][A-Za-z0-9+/]{12,}["\']', source, re.IGNORECASE
        )
        self.assertEqual(secrets, [])

    def test_gateways_read_credentials_from_env_only(self):
        import inspect

        import payment_connectors

        source = inspect.getsource(payment_connectors)
        self.assertIn("os.environ.get", source)


class TestProductionSsrfGuard(unittest.TestCase):
    """The audit's finding B: production mode previously only enforced
    https — a private/loopback destination passed validation. Now the host
    must resolve to a PUBLIC address (loopback/private/link-local/reserved
    all refused even over https)."""

    def setUp(self):
        self._saved = os.environ.get("FIX_ENV")
        os.environ["FIX_ENV"] = "production"
        reset_store()

    def tearDown(self):
        if self._saved is None:
            os.environ.pop("FIX_ENV", None)
        else:
            os.environ["FIX_ENV"] = self._saved

    def _bkash(self, url):
        gws = build_gateways()
        gws["bkash"].url = url
        return gws["bkash"]

    def test_private_v4_refused(self):
        with self.assertRaises(Refused):
            self._bkash("https://10.0.0.5/create").initiate(100, "TRX", "https://cb")

    def test_loopback_refused(self):
        with self.assertRaises(Refused):
            self._bkash("https://127.0.0.1/create").initiate(100, "TRX", "https://cb")

    def test_link_local_metadata_refused(self):
        with self.assertRaises(Refused):
            self._bkash("https://169.254.169.254/latest/meta-data").initiate(
                100, "TRX", "https://cb"
            )

    def test_ipv6_loopback_refused(self):
        with self.assertRaises(Refused):
            self._bkash("https://[::1]/create").initiate(100, "TRX", "https://cb")

    def test_reason_names_the_guard(self):
        try:
            self._bkash("https://10.0.0.5/create").initiate(100, "TRX", "https://cb")
            self.fail("expected Refused")
        except Refused as exc:
            self.assertIn("production SSRF guard", str(exc))


if __name__ == "__main__":
    unittest.main()
