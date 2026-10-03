"""payment-connectors tests — P06-M05 (T06 idempotency, T08 fallbacks)."""
from __future__ import annotations

import os
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from payment_connectors import (  # noqa: E402
    PAYMENT_FALLBACK_REGISTER,
    Refused,
    build_gateways,
    confirm,
    reset_store,
)


class TestDryRun(unittest.TestCase):
    def test_unconfigured_gateways_dry_run(self):
        for name, gateway in build_gateways().items():
            result = gateway.initiate(115000, "TRX-1", "https://callback")
            self.assertEqual(result.status, "dry-run", name)

    def test_all_three_p0_gateways_present(self):
        self.assertEqual(set(build_gateways()), {"bkash", "nagad", "sslcommerz"})


class TestIdempotentConfirmation(unittest.TestCase):
    def setUp(self):
        reset_store()

    def test_retried_confirmation_never_double_credits(self):
        first = confirm("bkash", "TRX-9", 115000)
        second = confirm("bkash", "TRX-9", 115000)
        third = confirm("bkash", "TRX-9", 115000)
        self.assertEqual(first.detail, "amount=115000 cents credited once")
        self.assertIn("idempotent replay", second.detail)
        self.assertIn("idempotent replay", third.detail)

    def test_different_trx_ids_credit_separately(self):
        confirm("bkash", "TRX-A", 100)
        confirm("bkash", "TRX-B", 100)
        self.assertIn("credited once", confirm("bkash", "TRX-C", 100).detail)

    def test_same_trx_different_gateway_are_distinct(self):
        confirm("bkash", "TRX-X", 100)
        self.assertIn("credited once", confirm("nagad", "TRX-X", 100).detail)


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
        source = (Path(__file__).resolve().parents[1]
                  / "src" / "payment_connectors.py").read_text(encoding="utf-8")
        secrets = re.findall(
            r'(?:key|token|secret)\s*=\s*["\'][A-Za-z0-9+/]{12,}["\']',
            source, re.IGNORECASE)
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
            self._bkash("https://169.254.169.254/latest/meta-data").initiate(100, "TRX", "https://cb")

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
