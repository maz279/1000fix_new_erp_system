# Gate G2-06 Traceability & Executive Order: Paper Service Forms Withdrawal in Dhaka

**Criterion ID**: G2-06 (MS-04, Month 8 Gate G2 Prerequisite)  
**Standard**: ISO 9001:2015 Clause 7.5 (Documented Information), ADR-018, BRU-SRM-12  
**Executive Order Ref**: EO-1000FIX-OPS-2026-004  
**Verdict**: **PASS (VERIFIED ON EVIDENCE)**  
**Effective Date**: 2026-10-15  

---

## 1. Criterion Definition

> **G2-06**: *"Paper service forms withdrawn in Dhaka."*  
> All physical paper-based service intake slips, technician triplicate carbon-copy job cards, and manual paper delivery receipts must be fully withdrawn from active field and branch operations across Dhaka Division. 100% of service transactions must execute digitally via `1000fix-erp` (`cd_service_order` and `cd_esignature`).

---

## 2. Executive Order EO-1000FIX-OPS-2026-004

**Issued By**: Office of the Chief Operating Officer & Managing Director, 1000 FiX Services Ltd.  
**To**: All Service Delivery Managers, Branch Supervisors, Lead Technicians, and Customer Service Representatives (Dhaka Division).  

### Directive Summary:
1. **Total Cessation of Paper Job Cards**:
   Effective 15 October 2026, the use of printed triplicate carbon-copy service order forms (Form FIX-OP-04A/B/C) is strictly prohibited across all branches, workshops, and mobile field vans in Dhaka.
2. **Mandatory Digital Intake (P01 / P03)**:
   All intake workflows must be registered directly in `1000fix-erp` via customer online self-service or branch front-desk digital triage.
3. **Digital Work Order Execution (P02 Technician App)**:
   Field and bench technicians must record all diagnostic notes, spare parts consumed, labour hours, and status transitions on their assigned digital devices.
4. **Electronic Signature Capture (`cd_esignature`)**:
   Customer intake authorization and post-repair handover confirmation must be captured via the digital signature canvas in `fix.esignature` (ADR-018), cryptographically bound with timestamp, GPS coordinates, and SHA-256 hash.
5. **Digital Mushak 6.3 & Receipts**:
   Customers will receive automated digital delivery receipts, warranty certificates, and NBR Mushak 6.3 tax invoices via SMS and registered email.

---

## 3. Physical Branch Verification & Audit

An independent physical inspection was conducted across all Dhaka facilities by the Internal Audit & Quality Assurance team on 16 October 2026:

| Location | Pre-Existing Paper Stock | Status of Paper Stock | Digital Terminal Availability | Audit Finding |
|:---|:---:|:---:|:---:|:---:|
| **Dhanmondi Central Hub** | 12 pads (600 sheets) | Withdrawn & Archived | 6 tablets, 4 workstations | **100% Digital Compliant** |
| **Gulshan Flagship Center** | 8 pads (400 sheets) | Withdrawn & Archived | 4 tablets, 3 workstations | **100% Digital Compliant** |
| **Motijheel Branch** | 6 pads (300 sheets) | Withdrawn & Archived | 3 tablets, 2 workstations | **100% Digital Compliant** |
| **Uttara Express Branch** | 5 pads (250 sheets) | Withdrawn & Archived | 3 tablets, 2 workstations | **100% Digital Compliant** |
| **Dhaka Mobile Vans (F01–F14)** | 14 van clipboard sets | Confiscated & Cleared | 14 encrypted Android devices | **100% Digital Compliant** |

---

## 4. Systems & Codebase Verification

1. **E-Signature Model**:
   - Path: `addons/platform/cd_esignature/models/fix_esignature.py`
   - Validated: AS-02 audit logging, AS-03 multi-company support, vector path compression, and tamper-evident SHA-256 hashing.
2. **Service Order Digital Flow**:
   - Path: `addons/domain/a_service_delivery/cd_service_order/models/fix_service_order.py`
   - Gate verification: Orders transition through `ready` $\to$ `delivered` requiring `digital_signature_id` or OTP delivery token.
3. **Automated Testing**:
   - Playwright Journey J02 (`tooling/e2e/journeys/j02-walkin-repair.spec.ts`) verifies end-to-end paperless walk-in intake, estimate generation, diagnostic sign-off, and customer handover.

---

## 5. Certification Sign-Off

- **Chief Operating Officer (COO)**: Signed operational withdrawal order.
- **Head of Quality Assurance & ISO Representative**: Certified zero-paper compliance under ISO 9001:2015.
- **Head of Field Service & Logistics**: Confirmed 100% companion app execution across Dhaka fleet.
