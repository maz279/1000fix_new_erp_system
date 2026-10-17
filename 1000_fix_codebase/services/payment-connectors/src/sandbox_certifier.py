"""sandbox_certifier — Automated Sandbox Certification Battery for Wave 3 Payment Rails.

Certifies INT-001 (bKash), INT-002 (Nagad), INT-003 (SSLCOMMERZ), and INT-004 (Rocket)
against statutory sandbox criteria:
1. Initiate session / intent generation
2. Idempotent read-back query resolution for 'unknown' state
3. Idempotent confirmation with zero double-crediting
4. Partial & full refund / reversal execution
5. Circuit breaker outage failover simulation
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    from .payment_connectors import (
        ALL_GATEWAYS,
        BaseGateway,
        GatewayResult,
        PaymentRouter,
        build_gateways,
        confirm,
        reset_store,
    )
except ImportError:
    from payment_connectors import (
        ALL_GATEWAYS,
        BaseGateway,
        GatewayResult,
        PaymentRouter,
        build_gateways,
        confirm,
        reset_store,
    )


logger = logging.getLogger(__name__)


@dataclass
class CertificationCheck:
    name: str
    gateway: str
    passed: bool
    detail: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class GatewayCertificationReport:
    gateway: str
    certified: bool
    checks_passed: int
    checks_total: int
    checks: list[CertificationCheck] = field(default_factory=list)


@dataclass
class SuiteCertificationReport:
    timestamp: str
    overall_certified: bool
    gateway_reports: dict[str, GatewayCertificationReport] = field(default_factory=dict)
    fallback_router_certified: bool = False
    details: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


class SandboxCertifier:
    """Executes statutory certification runs for Bangladesh digital payment rails."""

    def __init__(self, gateways: dict[str, BaseGateway] | None = None) -> None:
        self.gateways = gateways or build_gateways(include_all=True, sandbox_mode=True)
        self.router = PaymentRouter(self.gateways)

    def certify_gateway(self, gateway_name: str) -> GatewayCertificationReport:
        gateway = self.gateways.get(gateway_name)
        if not gateway:
            return GatewayCertificationReport(
                gateway=gateway_name,
                certified=False,
                checks_passed=0,
                checks_total=1,
                checks=[CertificationCheck("registration", gateway_name, False, "gateway not registered")],
            )

        checks: list[CertificationCheck] = []
        test_trx_id = f"CERT-{gateway_name.upper()}-TX{int(datetime.now(timezone.utc).timestamp())}"
        test_amount = 50000  # 500.00 BDT in cents

        # 1. Initiate Lifecycle Check
        try:
            init_res = gateway.initiate(test_amount, test_trx_id, "https://1000fix.local/pay/callback")
            init_passed = init_res.status in ("initiated", "dry-run")
            checks.append(CertificationCheck(
                name="initiate_transaction",
                gateway=gateway_name,
                passed=init_passed,
                detail=f"status={init_res.status}, token={init_res.detail[:30]}",
            ))
        except Exception as e:
            checks.append(CertificationCheck(
                name="initiate_transaction",
                gateway=gateway_name,
                passed=False,
                detail=f"exception: {e}",
            ))

        # 2. Read-Back Query Resolution (IN-007 §5)
        try:
            query_res = gateway.query(test_trx_id)
            query_passed = query_res.status in ("confirmed", "dry-run")
            checks.append(CertificationCheck(
                name="read_back_query",
                gateway=gateway_name,
                passed=query_passed,
                detail=f"status={query_res.status}, detail={query_res.detail}",
            ))
        except Exception as e:
            checks.append(CertificationCheck(
                name="read_back_query",
                gateway=gateway_name,
                passed=False,
                detail=f"exception: {e}",
            ))

        # 3. Idempotent Confirmation Check (DI-04)
        try:
            first_conf = confirm(gateway_name, test_trx_id, test_amount)
            second_conf = confirm(gateway_name, test_trx_id, test_amount)
            idempotent_passed = (
                first_conf.status == "confirmed"
                and second_conf.status == "confirmed"
                and "idempotent replay" in second_conf.detail
                and first_conf.timestamp == second_conf.timestamp
            )
            checks.append(CertificationCheck(
                name="idempotent_confirm_no_double_credit",
                gateway=gateway_name,
                passed=idempotent_passed,
                detail=f"first={first_conf.detail}, second={second_conf.detail}",
            ))
        except Exception as e:
            checks.append(CertificationCheck(
                name="idempotent_confirm_no_double_credit",
                gateway=gateway_name,
                passed=False,
                detail=f"exception: {e}",
            ))

        # 4. Refund / Reversal Capability (IN-007 §6)
        try:
            refund_res = gateway.refund(test_trx_id, test_amount // 2, "Warranty inspection fee adjustment")
            refund_passed = refund_res.status in ("refunded", "dry-run")
            checks.append(CertificationCheck(
                name="refund_reversal",
                gateway=gateway_name,
                passed=refund_passed,
                detail=f"status={refund_res.status}, detail={refund_res.detail}",
            ))
        except Exception as e:
            checks.append(CertificationCheck(
                name="refund_reversal",
                gateway=gateway_name,
                passed=False,
                detail=f"exception: {e}",
            ))

        passed_count = sum(1 for c in checks if c.passed)
        is_certified = passed_count == len(checks)
        return GatewayCertificationReport(
            gateway=gateway_name,
            certified=is_certified,
            checks_passed=passed_count,
            checks_total=len(checks),
            checks=checks,
        )

    def certify_fallback_router(self) -> CertificationCheck:
        """Verify dynamic failover when primary rail experiences an outage."""
        bkash = self.gateways["bkash"]
        nagad = self.gateways["nagad"]
        reset_store()

        try:
            # Simulate bKash outage
            bkash.set_simulated_outage(True)
            res, deg_log = self.router.initiate_with_fallback(
                amount_cents=10000,
                trx_id="TEST-FALLBACK-01",
                callback_ref="https://1000fix.local/cb",
                preferred_rail="bkash",
            )
            bkash.set_simulated_outage(False)

            passed = (
                res.gateway == "nagad"
                and res.status in ("initiated", "dry-run")
                and any("bkash" in log.lower() for log in deg_log)
            )
            return CertificationCheck(
                name="payment_router_outage_fallback",
                gateway="router",
                passed=passed,
                detail=f"active_rail={res.gateway}, status={res.status}, trace={' -> '.join(deg_log)}",
            )
        except Exception as e:
            bkash.set_simulated_outage(False)
            return CertificationCheck(
                name="payment_router_outage_fallback",
                gateway="router",
                passed=False,
                detail=f"exception: {e}",
            )

    def run_full_suite(self) -> SuiteCertificationReport:
        reset_store()
        gw_reports: dict[str, GatewayCertificationReport] = {}
        all_gw_certified = True

        for gw in ALL_GATEWAYS:
            report = self.certify_gateway(gw)
            gw_reports[gw] = report
            if not report.certified:
                all_gw_certified = False

        router_check = self.certify_fallback_router()
        overall = all_gw_certified and router_check.passed

        return SuiteCertificationReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            overall_certified=overall,
            gateway_reports=gw_reports,
            fallback_router_certified=router_check.passed,
            details={"router_check": asdict(router_check)},
        )
