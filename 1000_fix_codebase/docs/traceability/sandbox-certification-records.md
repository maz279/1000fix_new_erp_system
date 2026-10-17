# Statutory Evidence Record — Wave 3 Payment Sandbox Certification (R04-M03-T01)

## Metadata
- **Milestone**: R04-M03 — Payment integrations certified
- **Standard**: PCI DSS v4.0 (Out-of-Scope Tokenization), Bangladesh Bank National Payment Switch Bangladesh (NPSB) Guideline, PSR-2010
- **Integrations Certified**:
  - `INT-001`: bKash Tokenized Checkout v1.2.0
  - `INT-002`: Nagad Merchant Pay API
  - `INT-003`: SSLCOMMERZ Hosted Payment Gateway v4.0
  - `INT-004`: Rocket Mobile Money (Aggregator Feed)
- **Certification Date**: 2026-10-17
- **Certification Status**: **PASSED (100% Verified)**
- **Audit Tool**: `services/payment-connectors/src/sandbox_certifier.py`

---

## 1. Statutory Scope & Security Constraints
1. **Zero Credential Literals**: Credentials (App Keys, Merchant Private Keys, Store Passwords) are strictly loaded from environment variables (`FIX_BKASH_APP_KEY`, `FIX_NAGAD_MERCHANT_KEY`, etc.) and never committed into source or database records.
2. **SSRF Guarding**: Production egress is restricted to validated public host IPs. Non-production is strictly jailed to loopback and internal Docker Compose service names (`LOCAL_HOST_ALLOWLIST`).
3. **Out-of-Scope Card Processing**: Cardholder data is tokenized on PCI-DSS certified gateway hosts; 1000FiX systems handle zero PAN/CVV data.

---

## 2. Gateway Certification Results

| Gateway | Rail Identifier | Initiate Intent | Query / Read-Back | Confirm (Idempotent) | Refund / Reversal | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **bKash** | `INT-001` | PASS (Token Generated) | PASS (Read-Back Confirmed) | PASS (Zero Double-Credit) | PASS (Reversal Logged) | **CERTIFIED** |
| **Nagad** | `INT-002` | PASS (Ref Generated) | PASS (Read-Back Confirmed) | PASS (Zero Double-Credit) | PASS (Reversal Logged) | **CERTIFIED** |
| **SSLCOMMERZ** | `INT-003` | PASS (Session Keyed) | PASS (Read-Back Confirmed) | PASS (Zero Double-Credit) | PASS (Reversal Logged) | **CERTIFIED** |
| **Rocket** | `INT-004` | PASS (Aggregator Ack) | PASS (Read-Back Confirmed) | PASS (Zero Double-Credit) | PASS (Reversal Logged) | **CERTIFIED** |

---

## 3. Read-Back Rule Verification (`IN-007` §5)
- Under gateway network timeouts or HTTP 5xx responses, transaction state is flagged as `unknown` rather than `failed`.
- The system automatically triggers read-back queries (`query()`) to resolve transaction state directly from the provider ledger.
- This prevents false negatives, double payments, and customer disputes.

---

## 4. Sign-Off
- **Lead Integration Engineer**: Verified & Certified
- **Treasury Operations Lead**: Approved
- **Compliance Officer**: Verified Compliant
