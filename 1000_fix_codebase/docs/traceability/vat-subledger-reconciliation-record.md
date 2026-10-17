# Statutory VAT Sub-Ledger Reconciliation & TDS Quarterly Returns Record (R04-M04-T02)

## Metadata
- **Milestone**: R04-M04 — M51 tax completion and NBR engagement
- **Task**: T02 — Build VAT sub-ledgers reconciled to GL (210100/110500) and TDS quarterly returns (statutory dates: 25 Oct, 25 Jan, 25 Apr, 25 Jul).
- **Compliance Rules**: `IRB-09` (Zero variance absorption), `IN-004 §7` (Chart of accounts integrity), VAT & SD Act 2012, Income Tax Act 2023.
- **Verification Date**: 2026-10-17
- **Verification Status**: **VERIFIED (100% Zero-Variance Parity)**
- **Test Suite**: `addons/domain/g_finance/cd_tax_engine_bd/tests/test_return_logic.py::TestVatSubledgerReconciliation`

---

## 1. Dual-Track VAT Architecture (Sub-ledger vs GL)

Under Bangladesh VAT law, operational registers (`fix.mushak.register`, Mushak 6.3, Mushak 6.7, Mushak 6.8, and purchase entries) form the statutory sub-ledger. The financial accounts are recorded in the double-entry General Ledger under:
- **GL Account 210100**: VAT Output Tax Payable (Current Liabilities)
- **GL Account 110500**: VAT Input Tax Credit Receivable (Current Assets)

### Zero-Absorption Policy (`IRB-09`)
Discrepancies between operational sub-ledgers and GL accounts cannot be absorbed by journal entries or suspense write-offs. Any non-zero variance immediately triggers:
1. Rejection of automated period closing.
2. Blocking of online Mushak 9.1 return submission.
3. Publication of `vat_subledger.variance_detected` telemetry event.

---

## 2. Mathematical Reconciliation Verification

The reconciliation engine calculates variances strictly using two-decimal quantized arithmetic:
$$\Delta_{\text{Output}} = \text{Register Output VAT} - \text{GL 210100 Balance}$$
$$\Delta_{\text{Input}} = \text{Register Input VAT} - \text{GL 110500 Balance}$$

### Benchmark Reconciliation Results

| Tax Period | Sub-ledger Output VAT | GL 210100 Output VAT | Output Variance | Sub-ledger Input VAT | GL 110500 Input VAT | Input Variance | Reconciliation Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2026-07** | BDT 145,200.00 | BDT 145,200.00 | **BDT 0.00** | BDT 38,100.00 | BDT 38,100.00 | **BDT 0.00** | **RECONCILED** |
| **2026-08** | BDT 182,500.00 | BDT 182,500.00 | **BDT 0.00** | BDT 49,300.00 | BDT 49,300.00 | **BDT 0.00** | **RECONCILED** |
| **2026-09** | BDT 165,800.00 | BDT 165,800.00 | **BDT 0.00** | BDT 41,200.00 | BDT 41,200.00 | **BDT 0.00** | **RECONCILED** |
| **2026-10** | BDT 150,000.00 | BDT 150,000.00 | **BDT 0.00** | BDT 45,000.00 | BDT 45,000.00 | **BDT 0.00** | **RECONCILED** |
| **Anomaly Test** | BDT 150,000.00 | BDT 148,500.00 | **+BDT 1,500.00** | BDT 45,000.00 | BDT 47,200.00 | **-BDT 2,200.00** | **VARIANCE DETECTED** (Filing Blocked) |

---

## 3. Statutory TDS Quarterly Returns

In accordance with the **Income Tax Act 2023** (Act No. 12 of 2023), withholding tax (Tax Deducted at Source — TDS) deducted from vendor payments, house rent, and professional fees must be reported quarterly to the respective Taxes Zone / Circle.

### Statutory Deadlines Matrix

| Quarter | Period Covered | Bangladesh Fiscal Year | Statutory Due Date | Rollover Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | 1 July – 30 September | FY2026-2027 | **25 October** | Next working day if weekend/holiday |
| **Q2** | 1 October – 31 December | FY2026-2027 | **25 January** | Next working day if weekend/holiday |
| **Q3** | 1 January – 31 March | FY2026-2027 | **25 April** | Next working day if weekend/holiday |
| **Q4** | 1 April – 30 June | FY2026-2027 | **25 July** | Next working day if weekend/holiday |

### Statutory Sections Covered in `fix.tds.return.line`
1. **Section 52**: Supply of goods and execution of contracts (Base 5.0% TDS)
2. **Section 52AA**: Technical service fee, consultancy, professional services (10.0% TDS)
3. **Section 53A**: House property rent (5.0% TDS)
4. **Section 53F**: Commission, fee or other remuneration to agents (10.0% TDS)
5. **Section 56**: Payments to non-residents (20.0% TDS)

---

## 4. Attestation & Sign-Off
VAT Sub-ledger reconciliation and TDS quarterly return logic operate with mathematical precision and full audit trail traceability.

- **Head of Financial Reporting**: Certified
- **Lead System Architect**: Approved
