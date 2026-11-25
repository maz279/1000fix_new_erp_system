# PDPA Statutory Cross-Border Data Transfer Register: AI & External Model Invocations

**Document ID:** PDPA-REG-AI-2026-01  
**Statutory Authority:** Bangladesh Personal Data Protection Act (PDPA) §§ 20–21  
**Oversight Body:** 1000FiX Data Protection Forum (DP Forum)  
**Classification:** Confidential — Statutory Regulatory Compliance Record  
**Effective Date:** 2026-10-18  
**Review Cycle:** Semi-Annual / Mandatory Pre-Release Review  

---

## 1. Statutory Context & The Sovereign Data Rule

Sections 20 and 21 of the Bangladesh Personal Data Protection Act (PDPA) strictly regulate the cross-border transfer of sensitive personal data, operational logs, and citizen communications outside the territorial boundaries of the People's Republic of Bangladesh.

### The Non-Negotiable Core Principle:
> **Customer conversation data, repair transcripts, device diagnostics, and recovered file payloads NEVER leave 1000FiX sovereign infrastructure by default.**

All natural language processing (NLP), conversational intent understanding (M32), technician dispatch scoring (M26), and demand forecasting (M26) execute within local, on-premise container runtimes:
- **M32 Contact Centre NLU:** Pure-Python authored bilingual engine (`cd_contact_centre`) running within Odoo.
- **Sovereign LLM Inference:** Self-hosted on-premise Ollama instance (`ollama/ollama@sha256:926d40fd6eeeebd346b5c358a63de2a10ec995371cd93dd22f1843200694b1a6`) mounted on sovereign volumes.
- **M26 Operational ML:** Scikit-learn and MLflow running inside private virtual networks (`services/ml-gateway`).

---

## 2. DP Forum Review & External LLM Transfer Rules (`INT-036` / `INT-043`)

External Large Language Model (LLM) APIs (including hyperscaler cloud inference endpoints) present significant data sovereignty risks:
- Potential retention of prompt inputs for third-party foundation model training.
- Trans-border network routing through jurisdictions lacking reciprocal data protection adequacy treaties with Bangladesh.
- Indeterminate sub-processor supply chains.

### Mandatory 5-Point DP Forum Gate for Any External AI Invocation:
1. **Genuine Necessity Test:** The system owner must demonstrate that on-premise models (Ollama, local transformers) cannot technically fulfill the requirement.
2. **Exclusion of Raw Customer Data:** Customer chat transcripts, audio recordings, customer names, phone numbers, delivery addresses, and financial identifiers are **categorically forbidden** from being sent to external LLMs.
3. **Mandatory PII Scrubbing:** All input payloads must pass through an automated, deterministic PII sanitization pipeline (regex masking + named entity redaction) before egress.
4. **Zero-Retention Guarantee:** External providers must maintain contractual enterprise Data Protection Agreements (DPAs) with Zero Data Retention (ZDR) clauses.
5. **DP Forum Minuted Approval:** Every external integration must be formally approved by the DP Forum and recorded in this Statutory Transfer Register.

---

## 3. Statutory Cross-Border AI Transfer Register

| Flow ID | System & Interface | Destination / Provider | Data Category | PII Sanitization | Legal Basis (PDPA §20) | DP Forum Status |
|---|---|---|---|---|---|---|
| **AI-REG-001** | **M32 Conversational AI**<br>(Hotline 16743, WhatsApp, Web) | **Local Container**<br>(Odoo + Ollama on-prem) | Customer queries, intent classifications | N/A (Internal Sovereign Z4) | Performance of Service Contract; Consent | **APPROVED — DEFAULT ON-PREMISE** |
| **AI-REG-002** | **M26 Dispatch Scoring**<br>(`services/ml-gateway`) | **Local Container**<br>(MLflow + Scikit-Learn) | Technician skills, SLA metrics, branch workload | N/A (Internal Operational Telemetry) | Legitimate Business Operation | **APPROVED — DEFAULT ON-PREMISE** |
| **AI-REG-003** | **M26 Demand Forecasting**<br>(`services/ml-gateway`) | **Local Container**<br>(MLflow + Time-Series) | Aggregated spare parts consumption counts | Anonymized Aggregated Counts | Legitimate Business Operation | **APPROVED — DEFAULT ON-PREMISE** |
| **AI-REG-004** | **INT-036 External Translation**<br>(Technical Manual Translation) | **Enterprise Cloud LLM**<br>(e.g. Claude / Gemini API) | Generic technical hardware documentation, vendor service bulletins | Strictly prohibited from containing customer or case references | Legitimate Business Operation (Language Access) | **CONDITIONALLY APPROVED**<br>Documentation text only; 0 customer data |
| **AI-REG-005** | **INT-043 Generative Diagnosis**<br>(Complex Multi-Fault Inquiries) | **External Cloud LLM** | Hypothetical complex hardware triage scenarios | Mandatory PII Redaction (`[REDACTED_DEVICE]`, `[REDACTED_SN]`) | Explicit Customer Consent | **RESTRICTED**<br>Requires pre-approved tokenized payload; customer chats use Ollama |

---

## 4. Technical PII Scrubbing & Pre-Egress Guardrail

For any technical document translation under `INT-036`, the following scrubbing engine is enforced prior to API invocation:

```python
# Technical pre-egress redaction guardrail
import re

PATTERNS = {
    "phone": r"(\+?880|0)1[3-9]\d{8}",
    "nid": r"\b\d{10}\b|\b\d{13}\b|\b\d{17}\b",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "imei": r"\b\d{15}\b",
    "serial": r"\b[A-Z0-9]{10,20}\b",
}

def scrub_pii(text: str) -> str:
    scrubbed = text
    for p_type, regex in PATTERNS.items():
        scrubbed = re.sub(regex, f"[{p_type.upper()}_REDACTED]", scrubbed)
    return scrubbed
```

If an external LLM request detects unredacted PII patterns, the gateway aborts transit immediately and emits a `pdpa.transfer_blocked` security alert.

---

## 5. DP Forum Review Minutes & Attestation

- **Meeting Date:** 2026-10-18  
- **Quorum Present:**  
  - Data Protection Officer (DPO) — Chair  
  - Chief Information Security Officer (CISO)  
  - Lead Solutions Architect  
  - Head of Legal & Regulatory Affairs  
- **Resolution:**  
  > *"The Data Protection Forum formally ratifies Register PDPA-REG-AI-2026-01. Customer conversation data, repair transcripts, and data recovery cases are permanently restricted to sovereign on-premise infrastructure (Ollama/Odoo/ML Gateway). Any cross-border transit of conversational data without explicit DP Forum approval and automated PII sanitization constitutes a Tier-1 compliance breach."*

- **Signed:**  
  *Chair, Data Protection Forum* — 1000FiX Services Ltd.  
  *Data Protection Officer (DPO)* — Statutory Compliance Division  
