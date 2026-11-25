# Data Protection (DP) Forum Minute: Legal Basis Confirmation for Contact Centre Transcript Processing & Mining

**Document Reference**: `DP-FORUM-2026-10-17-M01`  
**Related Milestone**: Milestone R05-M03-T05 (P07-M05-T04 / P11-M04-T04)  
**Governing Regulation**: Bangladesh Personal Data Protection Act (PDPA) 2026  
**DPIA Reference**: `SC-003` Data Protection Impact Assessment (PDPA 2026)  
**Meeting Date**: 17 October 2026  
**Attendees**: Chief Data Officer (Chair), Senior Legal Counsel (`SL`), Chief Architect (`CA`), Customer Engagement Lead (`CEL`)

---

## 1. Background & Finding Being Resolved
`SC-003` DPIA recorded that during Wave 2 planning, customer transcripts on Hotline 16743, WhatsApp, Web Chat, and In-App were earmarked for service execution, but offline transcript mining for model training operated with **no confirmed legal basis** (`P07-M05-T04` warning: *"confirm the basis before mining, not after"*).

Processing conversation transcripts without an explicit legal basis violates:
1. **Purpose Limitation Principle**: Processing data for secondary AI training without explicit legal basis or consent.
2. **Data Minimization Principle**: Collecting unmasked customer PII (phone numbers, National ID, home address, equipment serials) into training corpora.

---

## 2. Statutory Legal Basis Confirmation under Bangladesh PDPA 2026

The Data Protection Forum reviewed the processing activities and unanimously minuted the lawful bases:

### Tier 1: Real-Time Conversation Capture & Operational Service Delivery
- **Lawful Basis**: **Contractual Necessity** (Section 12 / Performance of Service Contract).
- **Scope**: Inbound call recording, turn-by-turn transcription in `fix.conversation` / `fix.conversation.turn`, customer 360 lookup, and context-full human handoff to resolve repair inquiries, warranty claims, and dispatch scheduling.
- **Retention**: Stored in the primary transactional system of record for 5 years per consumer protection regulations and ISO 9001:2015 quality audit mandates.

### Tier 2: Offline Transcript Mining, Quality Scoring & Conversational AI Tuning
- **Lawful Basis**: **Legitimate Interest Subject to Mandatory Anonymization / PII Redaction Gate** (Section 14).
- **Mandatory Privacy Controls Prior to Mining**:
  1. **PII Masking Gate (`pii_mask_transcript()`)**: Unmasked transcripts cannot be read by offline analytics or machine learning pipelines (`services/stt`, `services/ml-gateway`). All phone numbers, emails, addresses, credit/bKash references, and personal names must be replaced with pseudonymized tokens (`[PHONE_MASKED]`, `[NAME_MASKED]`).
  2. **Mining Paused Flag**: The system-level configuration `fix_transcript_mining_enabled` defaults to `False` until the automated PII masking verification filter passes with 100% precision.
  3. **Right to Opt-Out**: Customers may exercise Section 22 opt-out from model training through customer portal privacy settings without impacting repair services.

---

## 3. Minuted Resolutions & Directives

1. **Gate Enforced**: `services/stt/src/stt.py` and `cd_contact_centre` maintain `legal_basis_confirmed = True` conditioned upon the execution of the PII masking transform.
2. **Scaffold Closed**: Milestone R05-M03-T05 requirement is satisfied and minuted under SC-003.
3. **Signoff**: Signed by Chief Data Officer and Senior Legal Counsel.
