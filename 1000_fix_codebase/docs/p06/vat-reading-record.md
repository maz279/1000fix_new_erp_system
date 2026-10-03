# P06-M02-T01 — VAT reading record (DoD-17)

| Item | Value |
|---|---|
| Read | M51 module spec; VAT & Supplementary Duty Act 2012 obligations (§ Mushak 6.3, § returns); NBR compliance guides |
| Currency check | **Verified current 2026-10-02** against: PwC Bangladesh tax summaries (15% standard; reduced 5/7.5/10; BIN on both parties; VAT shown separately); NBR tax-type guide (Mushak 6.3 content requirements); VATupdate Bangladesh e-invoicing deck (invoice mandatory > Tk 25,000; Mushak 9.1 monthly by the 15th) |
| Implemented in | `addons/domain/g_finance/cd_tax_engine_bd` — treatments standard_15 / reduced{5,7.5,10} / zero_rated / exempt / truncated; Mushak 6.3 register + statutory QWeb report; TDS schedule defaults |
| Re-verify due | Next statutory review cycle (DoD-17) or before first NBR filing |

## T09 — W4 deferral (recorded in the backlog)

VAT **returns and filing** (Mushak 9.1 monthly return, e-invoicing integration, income-tax schedules CD-M51-04/06/07) remain **W4** per `MV-03`: determination and Mushak issuance moved to W3; returns and filing did not. The register (`fix.mushak.register`) is built so the W4 return reads from it without schema change.
