# Statutory Evidence Record — P0 Payment Fallback & Outage Simulation (R04-M03-T04)

## Metadata
- **Milestone**: R04-M03 — Payment integrations certified
- **Requirement**: IP-09 / 05-03 Section 7 P0 Payment Fallback Register execution under live simulated outage conditions.
- **Verification Date**: 2026-10-17
- **Verification Status**: **VERIFIED (Graceful Multi-Tier Degradation)**
- **Test Suite**: `services/payment-connectors/tests/test_payment_connectors.py::TestFallbackRouterOutageSimulation`

---

## 1. Statutory Fallback Register Architecture
The P0 Fallback Register mandates that external digital rail outages MUST NOT halt commercial trading. If a payment channel becomes unavailable, the system cascades automatically:

```
[bKash (INT-001)] ──(Outage)──> [Nagad (INT-002)] ──(Outage)──> [SSLCOMMERZ (INT-003)] ──(Outage)──> [Manual Cash/Deposit Ref]
```

---

## 2. Live Outage Simulation Battery Results

| Test ID | Outage Injected | Preferred Rail | Automated Degradation Path | Final Outcome | Trade Interrupted? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `OUT-SIM-01` | bKash HTTP 503 / Timeout | bKash | bKash $\rightarrow$ Nagad | **Nagad Initiated** (Session OK) | **NO** |
| `OUT-SIM-02` | bKash & Nagad Outage | bKash | bKash $\rightarrow$ Nagad $\rightarrow$ SSLCOMMERZ | **SSLCOMMERZ Initiated** (Card OK) | **NO** |
| `OUT-SIM-03` | All Digital Gateways Down | bKash | Digital Rails $\rightarrow$ Cash-at-Branch Instruction | **Manual Fallback Logged** | **NO** |

---

## 3. Degradation Telemetry & Audit Trail
Whenever the `PaymentRouter` cascades to a secondary rail:
1. Warning log with structured breadcrumbs is emitted: `Payment TRX-OUTAGE-01 degraded from bkash to nagad`.
2. Outbox event `payment.rail_degraded` is queued for monitoring telemetry.
3. Customer invoice remains open with transparent payment options.

---

## 4. Sign-Off
- **Principal SRE**: Verified Circuit Breaker & Fallback Chain
- **Chief Operations Officer**: Confirmed Business Continuity
