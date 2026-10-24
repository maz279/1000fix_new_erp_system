# SC-002 Targeted Threat Model: M06 Data Recovery Services

**Document ID:** TM-SC-002  
**System / Module:** M06 Data Services (`cd_data_case`)  
**Classification:** Bangladesh Sovereign Data (Residency Zone Z4)  
**Security Category:** Tier 0 (Highest-Value Target in Estate)  
**Applicable Frameworks:** ISO 27001:2022, NIST SP 800-88 Rev 1, Bangladesh Cyber Security Act 2023, PDPA §20-21  

---

## 1. Executive Summary & Asset Valuation

The **M06 Data Recovery** service processes damaged, corrupted, or failing storage media (HDDs, SSDs, mobile flash NAND, enterprise RAID volumes) belonging to retail consumers, corporate enterprises, and statutory bodies in Bangladesh.

The recovered data payload represents the **single highest-value data asset in the entire 1000FiX enterprise estate**. If compromised, the impact includes:
- **Catastrophic Privacy Violation:** Exposure of unencrypted customer photographs, confidential corporate financial ledgers, intellectual property, and government records.
- **Extortion & Ransom Risk:** Threat actors holding recovered customer datasets for ransom or extortion.
- **Statutory Non-Compliance:** Violation of Bangladesh Data Protection Act (PDPA) cross-border data transfer prohibitions and confidentiality duties, incurring license revocation and criminal liability.

Therefore, M06 is architected under **Zero-Trust Sovereign Enclave Principles (SC-007, FF-09)**.

---

## 2. System Architecture & Trust Boundaries

```
[ Customer Media Ingestion ]
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trust Boundary: Public / Branch Intake (Zone 1)                 │
│ - Device registered in fix.device                               │
│ - Initial custody receipt issued                                │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Physical Air-Gapped Transport
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ Trust Boundary: Sovereign Cleanroom Laboratory (Zone Z4)        │
│ - Physical access control (Biometric + Man-trap)               │
│ - Dedicated recovery hardware with NO WAN egress                │
│ - Recovered storage volume mounted in encrypted loopback        │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Security Controls (SC-002 / SC-007):                      │  │
│  │ 1. Hard Z4 Routing Gate (action_start_recovery)          │  │
│  │ 2. Continuous Chain of Custody (action_take_custody)      │  │
│  │ 3. Mandatory Step-Up 2FA (action_access_recovered_data)  │  │
│  │ 4. Immutable Per-Read Audit Log (fix.z4.access.audit)     │  │
│  │ 5. Cryptographic NIST Purge (fix.data.wipe.certificate)   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Threat Actors & Threat Scenarios

| Threat Actor ID | Profile | Motivation | Capabilities |
|---|---|---|---|
| **TA-01: Rogue Insider** | Disgruntled or bribed technician in cleanroom lab | Financial gain, corporate espionage, data theft | Physical cleanroom access, valid Odoo operator credentials |
| **TA-02: Compromised Workstation** | Malware / Trojan on technician desktop via infected USB | Exfiltration of recovered files over local network | Process execution, memory dump, network sniffing |
| **TA-03: Lateral Network Intruder** | External attacker pivoting from corporate Wi-Fi or public web | System-wide compromise, ransomware | Network scanning, credential stuffing, lateral movement |
| **TA-04: Fraudulent Customer / Impostor** | Unauthorized third-party claiming recovered storage media | Identity theft, industrial espionage | Social engineering, forged ID or stolen claim check |

---

## 4. Attack Vectors & Technical Mitigations

### 4.1. AV-01: Unauthorized Read Access to Recovered Data
- **Attack:** An operator or compromised service account queries customer recovery files directly from the UI or API without active customer engagement.
- **Technical Mitigation (SC-002):**
  - **Hard Step-Up Authentication Gate:** Any invocation of `action_access_recovered_data()` strictly requires a valid, time-limited step-up verification token (`step_up_token`).
  - **Per-Read Immutable Audit Trail:** Every access generates a record in `fix.z4.access.audit` logging:
    - `case_id`: The exact recovery case.
    - `user_id` & `user_name`: Snapshot of authenticated operator.
    - `access_time`: Microsecond timestamp.
    - `access_type`: `metadata_read`, `file_list_read`, `file_download`, `preview_read`, `export`.
    - `purpose`: Mandatory statutory justification.
    - `ip_address`: Originating network endpoint IP.
    - `sha256_audit_hash`: Cryptographic SHA-256 integrity hash linking access parameters.
  - **Immutable Storage:** `fix.z4.access.audit` overrides `write()` and `unlink()` at the ORM layer, throwing `UserError` on any modification or deletion attempt.

### 4.2. AV-02: Recovered Data Stored in Non-Z4 Cloud Storage
- **Attack:** Data recovery process started while database/media records are residing in foreign or multi-tenant general cloud buckets (Zone 1/Zone 2).
- **Technical Mitigation (SC-007 / FF-09):**
  - **Hard Pre-Execution Gate:** `action_start_recovery()` checks `rec.residency_zone == 'z4'`. If false, execution throws:
    ```
    "SC-007: recovered data must be routed to Z4 BEFORE recovery starts. Not transiently, not in a cache."
    ```
  - Data transfer into Z4 is cryptographically isolated and physically pinned to Bangladesh sovereign data centers.

### 4.3. AV-03: Custody Tampering & False Handoff
- **Attack:** Rogue actor claims media was lost or handed over to customer without record.
- **Technical Mitigation:**
  - **Append-Only Custody Log:** `custody_chain` preserves every physical and logical transfer in chronological sequence (`action_take_custody()`, `action_log_custody_transfer()`, `action_handover()`).
  - **Event Bus Notification:** Every custody transition emits a signed event (`data_case.custody_taken`, `data_case.custody_transferred`, `data_case.recovered`) to the event bus.

### 4.4. AV-04: Incomplete Data Destruction Post-Handover
- **Attack:** Residual customer data remains on recovery cleanroom storage after handover, allowing subsequent operators to harvest deleted files.
- **Technical Mitigation (NFR-095):**
  - **Cryptographic NIST SP 800-88 Purge:** When `action_purge()` executes, it generates a `fix.data.wipe.certificate` with:
    - `method`: `nist_800_88_purge` (multi-pass overwrite and cryptographic key destruction).
    - `sanitization_status`: `verified`.
    - `verification_hash`: Deterministic SHA-256 verification token.
    - `statutory_record_retained`: `True`.
  - **Permanent Statutory Preservation:** The wipe certificate is immutable and cannot be deleted (`unlink()` blocked with `UserError`), ensuring an auditable proof of destruction remains permanently accessible for regulatory audits.

---

## 5. Verification Matrix & Nightly Assertion

| Requirement | Guardrail | Test Assertion | Nightly Job |
|---|---|---|---|
| **SC-007** | Recovery blocked unless `residency_zone == 'z4'` | `test_recovery_blocked_until_z4` | `test_journey_11_data_services.py` |
| **SC-002** | Step-up auth required for file access | `test_step_up_auth_enforced` | `test_journey_11_data_services.py` |
| **SC-002** | Per-read audit log created on every access | `test_per_read_access_logged` | `test_journey_11_data_services.py` |
| **SC-002** | Audit log is immutable (no write, no delete) | `test_audit_log_immutability` | `test_journey_11_data_services.py` |
| **NFR-095** | Purge issues verifiable wipe certificate | `test_purge_generates_statutory_certificate` | `test_journey_11_data_services.py` |
| **NFR-095** | Wipe certificate cannot be deleted | `test_wipe_certificate_permanent` | `test_journey_11_data_services.py` |

---

## 6. Approvals & Sign-Off

- **Chief Security Officer (CSO):** Approved — Zero-Trust Sovereign Enclave Architecture  
- **Data Protection Officer (DPO):** Approved — PDPA §20-21 Statutory Compliance  
- **Lead Architect:** Approved — Integrated with M06 / `cd_data_case`  
