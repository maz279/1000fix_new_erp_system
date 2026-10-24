# D-041 — L6 Commercial Component: Identity Verification / Seller KYC (INT-034 / TC-072) with Sovereign Z4 Split-Residency Data Path

| | |
|---|---|
| **Decision ID** | `D-041` |
| **Date** | 2026-10-19 (Milestone R08-M01-T01) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Financial Officer (CFO), Senior Legal Counsel (`SL`), Chief Architect (`CA`) |
| **Allocating authority** (`DL-08`) | TSS §9 L6 Rule · `GV-003` Change Control · `IR-002` P10-M01-T02/T08 |
| **Target Components** | `TC-072` Identity verification / KYC · `INT-034` NID & Business Verification · `cd_marketplace` · `libs/py/fix_residency` |
| **Regulatory Baseline** | Bangladesh Personal Data Protection Act (PDPA) §4.5.4 · NID Wing, Election Commission Bangladesh · Anti-Money Laundering Act 2012 §25 |

---

## 1. Context & Statutory Requirement

1000FiX is expanding its circular-economy marketplace (`M12`) to onboard 500–2,000 independent repair technicians, parts merchants, and refurbished device sellers. Because marketplace sellers disburse and collect commercial customer funds, legal compliance and counterparty verification are statutory obligations.

Under the regulatory framework of Bangladesh:
1. **National Identity & Anti-Fraud**: Under Bangladesh Bank Guidelines on Prevention of Money Laundering and Terrorist Financing, any counterparty engaged in regular commercial payout settlement must be authenticated against authoritative government identity registers (NID / Porichoy or certified trade license records).
2. **PDPA Data Residency Baseline (S3 Classification)**: Under Bangladesh PDPA and 1000FiX Sovereign Architecture Rule `SC-002`, **National ID (NID) numbers, biometric identifiers, trade licenses, and identity documents are classified as `S3: High Sensitivity Sovereign Data`**. They must reside strictly on physical infrastructure within the geographical borders of Bangladesh (Z4 resident store).
3. **Cross-Border Transfer Prohibition**: No seller identity document, raw biometric data, or NID image may ever be transmitted outside Bangladesh or ingested into offshore LLMs / third-party analytics without explicit sovereign regulatory exemption (`DS-05` gate).

---

## 2. Written Open-Source Software (OSS) Alternative Review

| Candidate | Algorithmic Capability | Regulatory Validity & Root Authority in Bangladesh | Assessment |
|---|---|---|---|
| **Self-Hosted Tesseract OCR / EasyOCR** | Extracts text from NID cards and trade license image files | **Zero official verification**: OCR can extract characters, but cannot verify whether the NID is authentic, counterfeit, expired, deceased, or registered under a different person with the Election Commission of Bangladesh. | **Rejected**: OCR parses pixels, not legal identity. Operating on self-hosted OCR alone violates Anti-Money Laundering requirements and exposes the platform to synthetic identity fraud. |
| **Porichoy NID Public Gateway Wrapper** | Open-source API client wrapping the government verification endpoint | Requires accredited government credentials, direct telecom connectivity to Election Commission NID Wing, and per-query statutory fee settlement. | **Incomplete without accreditation**: An OSS wrapper is simply an HTTP client; the underlying service requires an accredited commercial and legal counterparty agreement with accredited billing. |
| **Accredited L6 Commercial KYC Service (`TC-072` / `INT-034`) [Selected]** | End-to-end NID biometric verification, trade license lookup, and TIN verification via accredited national gateways. | **Accredited & Legally Enforceable**: Integrates directly with Election Commission NID database and National Board of Revenue (NBR) TIN service, providing cryptographically signed verification proofs. | **Selected**: Fulfills legal non-repudiation and anti-fraud standards; delivers automated pass/fail verification within seconds. |

---

## 3. Decision

1. **Adopt Licensed Commercial KYC Service (L6 / TC-072 / INT-034)** for marketplace seller onboarding, co-approved by the Chief Financial Officer (CFO) and Chief Technology Officer (CTO).
2. **Sovereign Split-Residency Routing via Z4 (`libs/py/fix_residency`)**:
   - In accordance with architectural fitness rule `FF-09`, all seller KYC document payloads, NID copies, and verification hashes MUST be written to the local Bangladesh-resident store (Z4) through `libs.py.fix_residency.ResidencyClient`.
   - The ERP database (`fix_dev`) stores ONLY opaque Z4 document tokens (`kyc_doc_z4_ref`) and verification timestamps, preventing PII data sprawl.
3. **Dual-Gate Verification Workflow**:
   - **Gate 1**: Automated KYC verification via `INT-034` (or manual compliance verification under fallback `FB-14`).
   - **Gate 2**: CFO operational approval (`cfo_approved = True`). A seller CANNOT quote or list jobs until both gates pass (`BRU-ECM-01`).
4. **Operational Fallback (`FB-14`)**:
   - If the automated verification gateway is offline or returns an ambiguous match, the seller profile is routed to Compliance for manual review within a strict **2 working days SLA**. The reviewer's identity and timestamp are immutably logged on the seller record.

---

## 4. Consequences & Annual Review

- **Budget & Commercial Terms**: Per-verification check fees approved by CFO under the W7 operational budget schedule.
- **Fitness Invariants**: `FF-09` residency scanning in CI enforces that `libs/py/fix_residency` remains the sole client for all seller KYC data paths.
- **Audit Schedule**: Annual security and DP Forum audit verifying zero cross-border leakage of seller identity records.
