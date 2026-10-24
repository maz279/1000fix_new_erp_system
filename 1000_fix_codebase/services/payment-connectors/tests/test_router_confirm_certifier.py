"""payment-connectors — fallback router, idempotent confirm, sandbox certifier,
and the package entry point (src/__init__.py, loaded under a unique name)."""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

pytestmark = [pytest.mark.financial]

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import payment_connectors as pc
import sandbox_certifier as sc
from sandbox_stub import start_sandbox_stub

GATEWAY_ENVS = (
    "FIX_ENV",
    "FIX_PAYMENT_SANDBOX_MODE",
    "FIX_BKASH_API_URL",
    "FIX_BKASH_APP_KEY",
    "FIX_NAGAD_API_URL",
    "FIX_NAGAD_MERCHANT_KEY",
    "FIX_SSLCOMMERZ_API_URL",
    "FIX_SSLCOMMERZ_STORE_PASSWORD",
    "FIX_ROCKET_API_URL",
    "FIX_ROCKET_API_KEY",
)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for name in GATEWAY_ENVS:
        monkeypatch.delenv(name, raising=False)
    pc.reset_store()
    yield
    pc.reset_store()


def _sandbox_router(wired: bool = False, include_all: bool = True) -> tuple[dict, pc.PaymentRouter]:
    """Sandbox gateways; when wired they are pointed at the REAL in-process
    sandbox endpoint so a cascade lands on a genuine wire call (GV-009: no
    rail may report "initiated" from a canned simulation)."""
    gateways = pc.build_gateways(include_all=include_all, sandbox_mode=True)
    if wired:
        stub_url = start_sandbox_stub()
        for name, gateway in gateways.items():
            gateway.url = f"{stub_url}/{name}"
    return gateways, pc.PaymentRouter(gateways)


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


# ------------------------------------------------------------------ router


class TestPaymentRouter:
    def test_default_registry_has_all_four_rails(self):
        assert set(pc.PaymentRouter().gateways) == set(pc.ALL_GATEWAYS)

    def test_healthy_primary_returns_without_degradation(self, caplog):
        _, router = _sandbox_router(wired=True)
        with caplog.at_level(logging.WARNING, logger=pc.logger.name):
            result, trace = router.initiate_with_fallback(100, "TRX-1", "https://cb", "nagad")
        assert (result.gateway, result.status, trace) == ("nagad", "initiated", [])
        assert "degraded" not in caplog.text

    def test_rail_missing_from_registry_is_skipped_and_logged(self, caplog):
        _, router = _sandbox_router(wired=True, include_all=False)  # no rocket
        with caplog.at_level(logging.WARNING, logger=pc.logger.name):
            result, trace = router.initiate_with_fallback(100, "TRX-2", "https://cb", "rocket")
        assert result.gateway == "bkash"
        assert trace == ["rocket: not available in active gateway registry"]
        assert "degraded from rocket to bkash" in caplog.text

    def test_unwired_sandbox_rails_refuse_and_cascade_to_manual_fallback(self):
        """GV-009: with no sandbox URL every rail refuses, so the router can
        only drop to the manual fallback register — it never lands on a rail
        reporting a canned 'initiated'."""
        _, router = _sandbox_router()
        result, trace = router.initiate_with_fallback(100, "TRX-3A", "https://cb", "bkash")
        assert result.status == "failed"
        assert "Manual Fallback" in result.detail
        assert all("exception=" in step for step in trace)

    def test_unknown_status_cascades_to_next_rail(self, monkeypatch):
        _gateways, router = _sandbox_router(wired=True)

        def flaky(request, timeout):
            if request.full_url.endswith("/bkash"):
                raise urllib.error.URLError("timed out")
            return _FakeResponse(json.dumps({"paymentID": "PAY-N"}).encode())

        monkeypatch.setattr(urllib.request, "urlopen", flaky)
        result, trace = router.initiate_with_fallback(100, "TRX-3", "https://cb", "bkash")
        assert result.gateway == "nagad"
        assert trace == [
            "bkash: status=unknown detail=network uncertainty: <urlopen error timed out>"
        ]

    @pytest.mark.parametrize(
        ("rail", "register_key"),
        [
            ("bkash", "INT-001 bKash"),
            ("nagad", "INT-002 Nagad"),
            ("sslcommerz", "INT-003 SSLCOMMERZ"),
            ("rocket", "INT-004 Rocket"),
        ],
    )
    def test_regression_manual_fallback_comes_from_the_p0_register(self, rail, register_key):
        """Regression: the manual-fallback lookup built the key as
        f"INT-001 {rail.title()}" ("INT-001 Bkash", "INT-001 Nagad", ...),
        which matches NO register entry, so the T08 register was never
        consulted and every rail got the generic default text."""
        gateways, router = _sandbox_router()
        for gateway in gateways.values():
            gateway.set_simulated_outage(True)
        result, trace = router.initiate_with_fallback(100, "TRX-4", "https://cb", rail)
        assert result.status == "failed"
        assert result.gateway == rail
        assert result.detail == (
            "All digital rails failed. Manual Fallback: "
            + pc.PAYMENT_FALLBACK_REGISTER[register_key]
        )
        assert all("exception=" in step for step in trace)

    def test_unregistered_rail_gets_generic_manual_fallback(self):
        _, router = _sandbox_router()
        result, trace = router.initiate_with_fallback(100, "TRX-5", "https://cb", "upay")
        assert result.status == "failed"
        assert result.detail.endswith(
            "Fallback to cash-at-branch or bank deposit reference capture."
        )
        assert trace == ["upay: not available in active gateway registry"]


# ------------------------------------------------------------------ confirm


class TestIdempotentConfirm:
    @staticmethod
    def _wired(name):
        gateway = pc.build_gateways(include_all=True, sandbox_mode=True)[name]
        gateway.url = f"{start_sandbox_stub()}/{name}"
        return gateway

    def test_replay_returns_first_record_without_crediting_again(self):
        nagad = self._wired("nagad")
        first = pc.confirm(nagad, "TRX-10", 5000)
        replay = pc.confirm(nagad, "TRX-10", 5000)
        assert first.detail == "amount=5000 cents credited once"
        assert replay.detail == "idempotent replay — no second credit"
        assert replay.timestamp == first.timestamp
        assert pc._confirmed[("nagad", "TRX-10")]["amount_cents"] == 5000

    def test_regression_concurrent_duplicate_confirmations_credit_once(self, monkeypatch):
        """Regression: confirm() tested `key in _confirmed` and assigned the
        record in a separate step, so two concurrent duplicate gateway
        callbacks could both observe "not yet confirmed" and BOTH credit.
        The barrier below holds both threads inside confirm() before the
        store write — exactly the interleaving that double-credited."""
        barrier = threading.Barrier(2, timeout=5)
        real_datetime = pc.datetime

        class _RendezvousClock:
            @staticmethod
            def now(tz=None):
                barrier.wait()
                return real_datetime.now(tz)

        bkash = self._wired("bkash")
        monkeypatch.setattr(pc, "datetime", _RendezvousClock)
        results: list[pc.GatewayResult] = []
        lock = threading.Lock()

        def callback() -> None:
            outcome = pc.confirm(bkash, "TRX-RACE-1", 115000)
            with lock:
                results.append(outcome)

        threads = [threading.Thread(target=callback) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        details = sorted(r.detail for r in results)
        assert details == [
            "amount=115000 cents credited once",
            "idempotent replay — no second credit",
        ]
        assert results[0].timestamp == results[1].timestamp


class _AmountGateway(pc.BaseGateway):
    """A connector whose read-back reports a status and an amount."""

    gateway = "bkash"

    def __init__(self, status, amount=None, raises=None):
        super().__init__(sandbox_mode=True)
        self.status, self.amount, self.raises = status, amount, raises

    def query(self, trx_id):
        if self.raises:
            raise self.raises
        payload = {} if self.amount is None else {"amount": self.amount}
        return pc.GatewayResult(self.gateway, self.status, trx_id, raw_payload=payload)


class TestVerifiedConfirm:
    def test_amount_reported_by_the_gateway_must_match(self):
        short = pc.confirm(_AmountGateway("confirmed", amount=4000), "TRX-AMT", 5000)
        assert short.status == "unverified" and "reports amount 4000" in short.detail
        bad = pc.confirm(_AmountGateway("confirmed", amount="n/a"), "TRX-AMT", 5000)
        assert bad.status == "unverified"
        ok = pc.confirm(_AmountGateway("confirmed", amount="5000"), "TRX-AMT", 5000)
        assert (ok.status, ok.detail) == ("confirmed", "amount=5000 cents credited once")

    def test_failed_or_erroring_lookup_never_confirms(self):
        failed = pc.confirm(_AmountGateway("failed"), "TRX-F", 100)
        assert failed.status == "unverified" and "'failed'" in failed.detail
        boom = pc.confirm(_AmountGateway("confirmed", raises=pc.GatewayError("503")), "TRX-F", 1)
        assert boom.status == "unverified" and "lookup failed (503)" in boom.detail
        assert ("bkash", "TRX-F") not in pc._confirmed

    def test_sandbox_without_endpoint_is_unverified(self):
        gateway = pc.build_gateways(sandbox_mode=True)["bkash"]  # no URL: lookup refuses
        res = pc.confirm(gateway, "TRX-S", 100)
        assert res.status == "unverified" and "refusing to simulate" in res.detail


# ------------------------------------------------------------------ certifier


class _ExplodingGateway(pc.BaseGateway):
    gateway = "bkash"

    def __init__(self) -> None:
        super().__init__(sandbox_mode=True)
        # The certifier requires a live sandbox endpoint before running the
        # battery; give it one so the exploding steps are actually reached.
        self.url = "http://localhost:9/bkash"

    def initiate(self, amount_cents, trx_id, callback_ref):
        raise RuntimeError("initiate-boom")

    def query(self, trx_id):
        raise RuntimeError("query-boom")

    def refund(self, trx_id, amount_cents, reason=""):
        raise RuntimeError("refund-boom")


class TestSandboxCertifier:
    def test_unregistered_gateway_fails_registration(self):
        report = sc.SandboxCertifier().certify_gateway("upay")
        assert (report.certified, report.checks_passed, report.checks_total) == (False, 0, 1)
        assert report.checks[0].name == "registration"
        assert report.checks[0].detail == "gateway not registered"

    def test_every_failing_step_is_recorded_not_raised(self, monkeypatch):
        def confirm_boom(*args):
            raise RuntimeError("confirm-boom")

        monkeypatch.setattr(sc, "confirm", confirm_boom)
        certifier = sc.SandboxCertifier({"bkash": _ExplodingGateway()})
        report = certifier.certify_gateway("bkash")
        assert report.certified is False
        assert (report.checks_passed, report.checks_total) == (0, 4)
        assert [(c.name, c.detail) for c in report.checks] == [
            ("initiate_transaction", "exception: initiate-boom"),
            ("read_back_query", "exception: query-boom"),
            ("idempotent_confirm_no_double_credit", "exception: confirm-boom"),
            ("refund_reversal", "exception: refund-boom"),
        ]

    def test_router_exception_fails_check_and_clears_outage(self, monkeypatch):
        certifier = sc.SandboxCertifier()

        def router_boom(**kwargs):
            raise RuntimeError("router-boom")

        monkeypatch.setattr(certifier.router, "initiate_with_fallback", router_boom)
        check = certifier.certify_fallback_router()
        assert (check.name, check.passed, check.detail) == (
            "payment_router_outage_fallback",
            False,
            "exception: router-boom",
        )
        assert certifier.gateways["bkash"]._simulated_outage is False

    def test_missing_rail_fails_the_suite_and_report_serialises(self):
        gateways = pc.build_gateways(include_all=False, sandbox_mode=True)  # no rocket
        for name, gateway in gateways.items():
            gateway.url = f"{start_sandbox_stub()}/{name}"
        report = sc.SandboxCertifier(gateways).run_full_suite()
        assert report.overall_certified is False
        assert report.fallback_router_certified is True
        assert report.gateway_reports["rocket"].certified is False
        assert report.gateway_reports["bkash"].certified is True
        decoded = json.loads(report.to_json())
        assert decoded["overall_certified"] is False
        assert decoded["gateway_reports"]["rocket"]["checks"][0]["name"] == "registration"
        assert decoded["details"]["router_check"]["passed"] is True

    def test_regression_certification_run_keeps_live_idempotency_ledger(self):
        """Regression: run_full_suite()/certify_fallback_router() called
        reset_store(), wiping the process-wide confirmation ledger — a live
        transaction confirmed before a certification run was credited AGAIN
        when its gateway retried the confirmation afterwards."""
        gateways = pc.build_gateways(include_all=True, sandbox_mode=True)
        for name, gateway in gateways.items():
            gateway.url = f"{start_sandbox_stub()}/{name}"
        live = pc.confirm(gateways["bkash"], "TRX-LIVE-1", 99900)
        assert live.detail == "amount=99900 cents credited once"
        report = sc.SandboxCertifier(gateways).run_full_suite()
        assert report.overall_certified is True
        retry = pc.confirm(gateways["bkash"], "TRX-LIVE-1", 99900)
        assert retry.detail == "idempotent replay — no second credit"
        assert retry.timestamp == live.timestamp

    def test_back_to_back_runs_each_credit_their_own_cert_transaction(self):
        gateways = pc.build_gateways(include_all=True, sandbox_mode=True)
        gateways["nagad"].url = f"{start_sandbox_stub()}/nagad"
        certifier = sc.SandboxCertifier(gateways)
        for _ in range(2):
            report = certifier.certify_gateway("nagad")
            confirm_check = report.checks[2]
            assert confirm_check.passed is True
            assert confirm_check.detail.startswith("first=amount=50000 cents credited once")


# ------------------------------------------------------------------ package entry point


def _load_package():
    name = "payment_connectors_pkg"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(
        name, SRC / "__init__.py", submodule_search_locations=[str(SRC)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class TestPackageEntryPoint:
    def test_package_reexports_resolve(self):
        pkg = _load_package()
        for symbol in pkg.__all__:
            assert getattr(pkg, symbol) is not None, symbol
        assert pkg.ALL_GATEWAYS == ("bkash", "nagad", "sslcommerz", "rocket")

    def test_package_certifier_binds_relative_imports(self, monkeypatch):
        pkg = _load_package()
        # The package builds its gateways from the environment — point every
        # rail at the REAL in-process sandbox endpoint before constructing.
        for env in (
            "FIX_BKASH_API_URL",
            "FIX_NAGAD_API_URL",
            "FIX_SSLCOMMERZ_API_URL",
            "FIX_ROCKET_API_URL",
        ):
            monkeypatch.setenv(env, f"{start_sandbox_stub()}/pkg")
        certifier_mod = sys.modules["payment_connectors_pkg.sandbox_certifier"]
        connectors_mod = sys.modules["payment_connectors_pkg.payment_connectors"]
        assert certifier_mod.confirm is connectors_mod.confirm
        report = pkg.SandboxCertifier().run_full_suite()
        assert report.overall_certified is True
        connectors_mod.reset_store()
