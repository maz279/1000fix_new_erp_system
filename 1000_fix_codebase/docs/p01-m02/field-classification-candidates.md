# Candidate field classification for counsel (DEP-31 Q1 input)

**Task `P01-M02-T02`** · Prepared 2026-10-01 · Owner: Data Architect (`DA`)
**Rule:** every candidate field names its **model** and its **business
purpose** (roadmap verify column) — **field by field**, not by group. This is
a *candidate* list — counsel's Q1 answer is the authority on which fields are
"restricted personal data" under the Act; nothing here pre-classifies finally.
Serves as **Annex A** of the DEP-31 engagement letter.

---

## Field-level register (22 fields across 9 groups)

The roadmap's seven candidate categories (national identity, identity
documents, tax identity, authentication factors, recovered customer data,
seller KYC, vetting records) plus two the estate also holds that counsel
should see (consent, identity resolution / DSR).

| # | Field | Group | Estate model | Business purpose | Residency design today (`NFR-086`) |
|:--:|---|---|---|---|---|
| 1 | `nid_number_10` (10-digit NID) | National identity | `M33` — `cd_party_master` (res.partner extension) | Primary national identifier for customers; duplicate prevention | Resident-only (Z4) |
| 2 | `nid_number_17` (17-digit NID) | National identity | `M33` — `cd_party_master` | Modern-form identifier; linkage across records | Resident-only |
| 3 | `nid_checksum_valid` (validation outcome) | National identity | `M33` — `CD-086 cd_nid` (TSS §4.5) | Data-quality flag; 10/17-digit format + checksum validation | Resident-only (derived from the number) |
| 4 | `passport_number` | Identity documents | `M33` — `cd_identity_document` | Identity verification for corporate contacts and cross-border warranty claims | Resident-only |
| 5 | `passport_biographical_page` (stored scan/image) | Identity documents | `M33` — `cd_identity_document` (file held in the object store under `D-028`, residency-classified) | Evidence of identity; KYC corroboration | Resident-only; T5 isolation |
| 6 | `nid_document_scan` (stored scan/image) | Identity documents | `M33` — `cd_identity_document` (as above) | Evidence of identity for onboarding | Resident-only; T5 isolation |
| 7 | `tin` (Tax Identification Number) | Tax identity | `M33` — `cd_party_master` (seller & corporate records) | Statutory tax reporting; TDS deduction basis | Resident-only |
| 8 | `tin_on_invoice_mushak` (TIN as printed on VAT instruments) | Tax identity | `M19` — `CD-083…089` (Mushak/VAT register) | NBR-compliant invoicing (Mushak 6.3 et al.) | Resident-only (statutory instrument data) |
| 9 | `webauthn_credential` (FIDO2 credential/reference) | Authentication factors | `M29` — Keycloak (TC-015) | MFA for privileged roles (`NFR-012`) | Resident-only; never leaves the IdP |
| 10 | `biometric_template_ref` (pointer to an IdP-held biometric factor) | Authentication factors | `M29` — Keycloak | Step-up authentication for T5 actions (`NFR-065`) | Resident-only; the estate builds **no biometric database** — only the reference exists |
| 11 | `recovered_file_content` (data recovered from client devices) | Recovered customer data | Data-services custody `CD-030…032`; stored via object store (`D-028`) with residency classification | Third-party personal data held in custody during service | Resident-only; T5 isolation; field-level encryption (`AS-14`) |
| 12 | `custody_chain_record` (who held what, when) | Recovered customer data | `CD-030…032` chain-of-custody model | Regulated, evidence-bearing workflow with destruction certification | Resident-only |
| 13 | `destruction_certificate` | Recovered customer data | `CD-030…032` | Proof of compliant disposal on service completion | Resident-only |
| 14 | `seller_trade_licence` (number + stored scan) | Seller KYC | `CD-053` seller module (+ `TC-072` verification, `CD-233` residency service) | Marketplace onboarding (500–2,000 sellers) | Resident-only |
| 15 | `seller_bank_details` (account for payouts) | Seller KYC | `CD-053` + `CD-242` settlement engine | Commission payout compliance | Resident-only |
| 16 | `seller_beneficial_owner_identity` (NID/passport of the owner) | Seller KYC | `CD-053`; identity fields per #1–#6 | Beneficial-ownership verification | Resident-only |
| 17 | `seller_reference_contact` (referee personal data) | Seller KYC | `CD-053` | Onboarding references and work-sample vetting | Resident-only |
| 18 | `criminal_record_check_result` (where lawfully obtained) | Vetting records | `M05` MSP technician vetting; `M12` seller trust screening | Legally-permitted employment/vendor vetting only | Resident-only; retention-limited |
| 19 | `vetting_consent_and_scope` | Vetting records | `M05` / `M12` consent capture | Lawful-basis evidence for #18 | Resident-only |
| 20 | `consent_registry_entry` (privacy consents per party) | Consent | `M33` — `cd_consent_registry` | PDPA consent evidence and data-subject request handling | Resident-only |
| 21 | `dedup_merge_link` (identity-resolution links between records) | Identity resolution | `M33` — `cd_dedup_merge` | Duplicate prevention; survivorship audit | Resident-only |
| 22 | `data_subject_request_record` (DSR intake and outcome) | Consent | `M33`/`M29` (TSS §3.6.4 flow) | Statutory data-subject request handling | Resident-only |

## Notes for counsel's Q1 pass

- Fields 1–8 and 14–17 are the classes the statute most plainly reaches
  (identity and tax identifiers, financial payout data).
- **Field 11 is third-party data held in custody** — the "processor, not
  controller" question matters most here; the destruction chain (#12–#13) is
  the control the estate already designs around it.
- Fields 9–10 exist only inside the identity provider; if the Act reaches
  biometric templates, the design is already resident-only — the question is
  confirmatory, not architectural.
- **Every field above sits in a model named in the estate's CD register**
  (`BE-005` §6 / TSS §12); none is proposed "free-floating", and no field is
  collected without a named business purpose (the table's column).
