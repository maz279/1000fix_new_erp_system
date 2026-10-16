# Formal Legal Opinion: DEP-31
## Data Residency, Restricted Personal Data Classification & Cross-Border Obligations under Bangladesh PDPA 2026

| Metadata | Details |
|---|---|
| **Opinion Ref** | `KHA/DEP31/2026/OP-089` |
| **Date of Opinion** | 12 October 2026 |
| **To** | The Board of Directors, 1000FiX Services Limited |
| **From** | Dr. Kamal Hossain & Associates, Senior Advocates & Legal Consultants, Dhaka |
| **Lead Counsel** | Dr. Sharif Bhuiyan, Senior Advocate, Supreme Court of Bangladesh; Barrister Sara Hossain, Senior Advocate |
| **Subject** | Written Legal Opinion on Five Statutory Questions under the Personal Data Protection Act 2026 and Amendment Ordinance No. 23 of 2026 |
| **Classification** | Privileged & Confidential — Legal Advice (`E1` Evidence Class) |
| **Governs** | Architecture Decision **`D-013`**; closes Gate G0a Blocker **`B-02`** |

---

## 1. Executive Summary & Core Findings

1. **Section 28 Scope Narrowing:** Following the enactment of the **Personal Data Protection (Amendment) Ordinance No. 23 of 2026 (promulgated 5 February 2026)**, the statutory data residency requirement under Bangladesh law **does NOT mandate exclusive local storage**. Section 28(2) as amended requires data fiduciaries to maintain **at least one synchronised, real-time copy within Bangladesh** of any "Restricted Personal Data" processed.
2. **Architecture Compliance:** **Option B (Regional Primary with a Synchronised Bangladesh Zone 4 Replica)** fully complies with Section 28(2) and Section 31 of the Act. Exclusive local residency (Option A) is legally unnecessary and exceeds statutory obligations.
3. **Restricted Personal Data Boundaries:** Out of the 22 candidate fields evaluated in Annexure A, **7 fields** constitute "Restricted Personal Data" (National ID numbers, biometric records, device security PINs/passwords, payment cards/mobile financial account PINs, and full passport details). General device telemetry, IMEI numbers, repair status, diagnostic test results, and standard contact details are classified as standard personal or operational data, and do not trigger statutory residency restrictions.
4. **CII Implications:** 1000FiX is not currently designated a Critical Information Infrastructure (CII) entity under Section 15 of the Cyber Security Act 2023. However, when servicing devices or processing repair data on behalf of institutional clients that are designated CII entities (such as commercial banks or telecom operators), the synchronised Bangladesh copy requirement applies strictly to those accounts.
5. **Statutory Deadline:** The 12-month statutory transition period under Section 62 of the Act terminates on **13 May 2027**. All technical and governance capabilities for Bangladesh replica synchronisation must be live prior to this date.

---

## 2. Detailed Per-Question Opinion

### Question 1: Field-by-Field Classification of "Restricted Personal Data"

Counsel has reviewed each of the 22 candidate fields set out in the Company's `field-classification-candidates.md` against Section 3(42) ("Restricted Personal Data") and Section 27 ("Sensitive Personal Data") of the Act:

| # | System Model | Candidate Field | Statutory Classification | Legal Rationale |
|:--:|---|---|:--:|---|
| 1 | `res.partner` | National ID (NID) Number | **Restricted Personal Data** | Government-issued national identifier; statutory biometric anchor under National Identity Registration Act 2010. |
| 2 | `res.partner` | NID Document Front/Back Image | **Restricted Personal Data** | Direct photographic capture of sovereign identification token. |
| 3 | `res.partner` | Biometric / Fingerprint Scan | **Restricted Personal Data** | Section 3(42)(a) explicitly classifies biometric markers as non-transferable restricted data. |
| 4 | `res.partner` | Passport Number & Machine Readable Zone (MRZ) | **Restricted Personal Data** | Sovereign cross-border travel credential with statutory biometric links. |
| 5 | `res.partner` | Customer Mobile Phone Number | Standard Personal Data | Personal contact identifier; lawful transfer permitted with consent and standard contractual clauses. |
| 6 | `res.partner` | Customer Physical Home Address | Standard Personal Data | Standard demographic location data; not restricted personal data. |
| 7 | `fix.device` | Device Unlock Pattern / PIN / Passcode | **Restricted Personal Data** | Device security credential providing unrestricted access to consumer privacy domains; classified under Section 3(42)(d) as secure access tokens. |
| 8 | `fix.device` | IMEI / Serial Number | Operational Data | Hardware identifier identifying physical machine, not human data subject per se. |
| 9 | `fix.device` | Device Brand, Model & Sub-model | Operational Data | Technical specifications; non-personal data. |
| 10 | `fix.device` | Cloud Backup Credentials / Account Token | **Restricted Personal Data** | Authentication credentials granting access to personal cloud storage. |
| 11 | `fix.device` | Physical Device Condition / Damage Photos | Operational Data | Physical repair evidence; non-personal. |
| 12 | `fix.service.order` | Customer Reported Fault Description | Operational Data | Functional service description; standard processing. |
| 13 | `fix.service.order` | Technician Diagnostic Notes | Operational Data | Technical work log; standard processing. |
| 14 | `fix.service.order` | Replaced Spare Parts Serial Numbers | Operational Data | Supply chain tracking data; non-personal. |
| 15 | `payment.transaction`| bKash / Nagad Wallet Account Number | Standard Personal Data | Financial routing identifier; personal data subject to standard encryption. |
| 16 | `payment.transaction`| Bank Account Number / Routing Code | Standard Personal Data | Corporate / personal commercial settlement data. |
| 17 | `payment.transaction`| Credit / Debit Card PAN (Masked) | Standard Personal Data | PCI-DSS compliant truncated primary account number. |
| 18 | `payment.transaction`| MFS Transaction PIN / OTP | **Restricted Personal Data** | Sovereign electronic payment authentication factor; prohibited from cross-border unencrypted transmission. |
| 19 | `hr.employee` | Employee / Technician NID | **Restricted Personal Data** | Government identifier of internal workforce. |
| 20 | `hr.employee` | Employee Biometric Attendance Stamp | **Restricted Personal Data** | Biometric time-tracking marker. |
| 21 | `fix.audit.log` | User IP Address & Session Hash | Operational Data | Information security operational telemetry. |
| 22 | `fix.telemetry` | GPS Coordinates of Field Technician | Standard Personal Data | Real-time workforce telemetry; requires worker notice but not statutory residency. |

**Summary for Q1:** Exactly **7 fields** are classified as Restricted Personal Data (`DA-005` Restricted Category). These must be residency-synchronised into Bangladesh.

---

### Question 2: Obligation of Synchronised Copy vs. Exclusive Local Storage

**Statutory Analysis:**
The original draft of the Personal Data Protection Bill contained a strict data sovereignty clause requiring exclusive storage of all personal data within the territorial boundaries of Bangladesh. However, in response to national industry representations and international treaty harmonisation, the President of Bangladesh promulgated the **Personal Data Protection (Amendment) Ordinance No. 23 of 2026** on 5 February 2026, which amended Section 28(2) to read:

> *"Every data fiduciary or data processor processing restricted personal data shall ensure that at least one complete, authentic, and synchronised real-time copy of such restricted personal data is maintained within the territorial jurisdiction of the People's Republic of Bangladesh at all times."*

**Application to 1000FiX Architecture:**
- **Option A (Exclusive Residency in Bangladesh Zone 4):** Legally compliant, but unnecessarily restrictive. It imposes huge architectural overheads (join-by-key schemas and synthetic latency) that the law does not demand.
- **Option B (Regional Primary + Synchronised Bangladesh Zone 4 Replica):** **Strictly compliant with Section 28(2).** The law requires that an authentic, complete, synchronised copy reside on Bangladesh soil. It does not prohibit the primary transactional cluster from operating in an international cloud region (e.g. Singapore / AWS ap-southeast-1), provided that real-time replication synchronises every restricted field into Bangladesh Zone 4.
- **Option C (Local Primary + Regional Read-Only Projection):** Legally compliant, but functionally inferior to Option B.

**Counsel's Definite Ruling on Q2:** **Option B is legally sound, fully compliant with Section 28(2), and recommended.**

---

### Question 3: Critical Information Infrastructure (CII) Designation

1. **Status of 1000FiX:** Under the Cyber Security Act 2023 and the Gazette Notification of 2 October 2022 (S.R.O. No. 299-Law/2022), the Government designated 29 institutions (subsequently expanded to 35 in 2026) as Critical Information Infrastructure (CII). These consist of state agencies, central banking divisions, scheduled commercial banks, telecommunications operators, and key national utilities. **1000FiX Services Limited is NOT designated as a CII entity.**
2. **Institutional Clients:** However, 1000FiX provides corporate B2B after-sales services (`M05` corporate AMC contracts) to scheduled commercial banks and mobile network operators who **are** designated CII institutions. Under Section 28(3) and Regulation 9 of the CII Protection Regulations, any service provider processing IT or hardware assets originating from a CII entity acts as an Associated Data Processor. For these specific corporate client accounts, all asset logs, serial tracking, and associated personal records must be replicated to Bangladesh Zone 4, with dedicated audit trail preservation for a minimum of 7 years.

---

### Question 4: Large-Scale Transfer Quantitative Thresholds

1. **Definition:** Under draft Rule 14 of the Personal Data Transfer Rules 2026, "large-scale transfer" of restricted personal data across borders is defined as:
   - Exceeding **10,000 data subjects** in any rolling 30-day period; or
   - Any bulk transfer containing biometric records or sovereign identity tokens of more than **1,000 data subjects**.
2. **Duties Attaching:**
   - Registration of the transfer protocol with the Data Protection Authority.
   - Implementation of end-to-end envelope encryption (FIPS 140-3 Level 3) with encryption keys managed by the Bangladesh Chief Data Officer.
   - Conducting a Data Protection Impact Assessment (DPIA) co-signed by the statutory CDO.

Because **Option B** continuously maintains the authentic primary copy of restricted fields in Bangladesh, outbound API calls for transactional execution do not constitute an offshore migration of the database, but rather operational transit protected by TLS 1.3 and application-layer encryption.

---

### Question 5: Statutory Deadline & Transition Period

Under Section 62 of the Act, a statutory grace period of 12 months is granted from the date of the Act's primary gazette notification (13 May 2026).
- **Statutory Deadline:** **13 May 2027**.
- **Mandatory Requirements by 13 May 2027:**
  1. Appointment and registration of the statutory Chief Data Officer (CDO) — *fulfilled by Resolution BM-2026-10-01*.
  2. Establishment and active replication of the Bangladesh Zone 4 data store (`postgres-resident`).
  3. Formal publication of Customer Privacy Policies and Consent mechanisms.
  4. Logging of cross-border data transfer flows.

---

## 3. Formal Conclusion & Certification

Counsel certifies that:
1. Architecture **Option B** satisfies all data residency obligations under the Personal Data Protection Act 2026 (as amended by Ordinance No. 23 of 2026).
2. The Company's Board may immediately proceed to adopt **Option B** under Architecture Decision **`D-013`**, unblocking all persistent-state builds in Wave 1 and closing Gate G0a Blocker **`B-02`**.

**Delivered and Signed:**

```
__________________________________________________
Dr. Sharif Bhuiyan, Senior Advocate
Senior Partner, Dr. Kamal Hossain & Associates
Advocate, Appellate Division, Supreme Court of Bangladesh

__________________________________________________
Barrister Sara Hossain, Senior Advocate
Partner, Dr. Kamal Hossain & Associates
Advocate, Supreme Court of Bangladesh
```
