# D-035 — L6 Commercial Component: Qualified E-Signature for Enterprise Contracts & Warranties

| | |
|---|---|
| **Decision ID** | `D-035` |
| **Date** | 2026-10-17 (Milestone R05-M03-T01) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Financial Officer (CFO), Senior Legal Counsel (`SL`), Chief Architect (`CA`) |
| **Allocating authority** (`DL-08`) | TSS §9 L6 Rule · `GV-003` Change Control · `IR-002` P07-M05-T01 |
| **Target Components** | `TC-071` Qualified E-Signature · `INT-016` E-Signature Integration · `cd_contract_core` · Corporate B2B AMC Agreements |
| **Regulatory Baseline** | Bangladesh Information & Communication Technology (ICT) Act 2006 (amended 2013) §7 & §16 |

---

## 1. Context & Statutory Requirement
1000FiX executes high-value Annual Maintenance Contracts (AMC) with corporate enterprises (banks, telecom operators, educational institutions) and brand warranty reimbursement agreements with 18 international hardware manufacturers. 

Under the **Bangladesh Information and Communication Technology (ICT) Act 2006 (amended 2013)**:
- **Section 7 (Legal recognition of electronic records)**: Electronic contracts are enforceable provided electronic signatures comply with designated authentication procedures.
- **Section 16 (Presumption as to electronic signatures)**: Electronic signatures carry a legal presumption of authenticity and non-repudiation in a court of law **only if issued by a Certifying Authority (CA) licensed by the Controller of Certifying Authorities (CCA) Bangladesh** or a mutually recognized international qualified trust provider (eIDAS / Adobe Approved Trust List).
- Unaccredited digital signatures or arbitrary image stamps lack legal evidentiary presumption, shifting the burden of proof to 1000FiX in litigation.

---

## 2. Written Open-Source Software (OSS) Alternative Review

| Candidate | Cryptographic Capability | Legal & Regulatory Admissibility in Bangladesh | Assessment |
|---|---|---|---|
| **DocuSeal / LibreSign** | Open-source e-signature (AGPL-3 / MIT), PDF signature generation | Uses self-signed X.509 certificates without Controller of Certifying Authorities (CCA) Bangladesh root trust | **Cryptographically sound, legally unaccredited**: Self-signed certificates fail Section 16 of the ICT Act 2006. In corporate dispute or arbitration, non-repudiation cannot be presumed, exposing 1000FiX to contract invalidation risk. |
| **GnuPG / OpenSSL PKI** | CLI public-key signing (GPL / Apache) | Developer-facing tooling with no non-technical signatory workflow, no audit trail hashing, and no CCA accreditation | Infeasible for corporate procurement officers and vendor directors; lack of tamper-evident audit certificate. |
| **Licensed Qualified E-Signature (Selected)** | Enterprise digital signature platform | Holds licensed Certifying Authority (CCA) compliance or qualified AATL certificate authority integration with verifiable cryptographic timestamping | **Selected**: Guarantees court admissibility under Section 7 & 16 of Bangladesh ICT Act 2006; provides tamper-evident audit trail certificate for corporate B2B contracts. |

---

## 3. Decision

1. **Adopt Licensed Qualified E-Signature Service (L6 / TC-071)** for high-value B2B subscription contracts, brand warranty authorizations, and corporate master service agreements.
2. **REST Integration Seam**: E-signature initiation and status webhooks integrate via standard envelope API in `cd_contract_core`, receiving countersigned PDF artifacts with cryptographic certificate validation.
3. **Storage & Audit Trail**: Countersigned agreements and their cryptographic certificate sheets are stored permanently in the Company's tamper-evident Ceph object store (`D-028`) with SHA-256 integrity validation.

---

## 4. Consequences & Annual Review

- **Commercial Terms**: Per-envelope / enterprise volume subscription approved by CFO.
- **Annual Review**: Annual compliance audit co-signed by Senior Legal Counsel (`SL`) and CFO to verify continuous accreditation under CCA guidelines and `D-030` schedule.
