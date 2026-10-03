---
id: PGD-CAT-05
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 2.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
owner: CISO / Chief Data Officer (both unappointed — see §"What is still missing")
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
enumeration_timestamp: 2026-08-18 20:05 (+06)
audit: ../_AUDIT/PGD-AUDIT-008_Category_05_Security_Privacy_and_Compliance_Audit.md
---

# Category 05 — Security, Privacy & Compliance (`SC`)

> **✅ All eleven authored and issued 2026-08-18.** Audited the same day in
> [`PGD-AUDIT-008`](../_AUDIT/PGD-AUDIT-008_Category_05_Security_Privacy_and_Compliance_Audit.md).
> The ✅ is **qualified** by `PGD-A2-25`: none carries an approval record, because no constituted
> body can approve one until `GV-001` `CC-01` completes. **Three of the eleven carry a second
> qualification** — `SC-003` cannot be *signed* at all until a Chief Data Officer exists
> (`NFR-096`), which is a statutory gap rather than a procedural one.

## Purpose

**This is the category with legal consequence.**

The Personal Data Protection Act 2026 (Law 63 of 2026) reaches full enforcement of its complaint
and enforcement mechanisms around **13 May 2027 — inside Wave 4** of the implementation roadmap.
Penalties run to **BDT 25 lakh, or BDT 50 lakh for a significant data fiduciary**. At 250,000+
customers a month, 1000FiX will almost certainly be classified as one.

Before 2026-08-18 the source estate contained **zero occurrences of the phrase "threat model"**
and **no assessment of any kind** — 17 references to a DPIA across 7 files, and no DPIA.

## Documents

| ID | Document | What it delivered | Status | Pri | Needed by |
|---|---|---|:--:|:--:|:--:|
| `SC-001` | **Security Architecture Document** | 7 trust zones (**adds `Z7` remote-support enclave** to `AR-001`'s six), a permitted-flow matrix, 7 enforcement points with failure modes, **68 controls mapped to ISO/IEC 27001:2022 Annex A**, and the **22 Annex A controls this architecture cannot discharge**, named with owners. Closes the architecture half of `OP-08` | ✅ | **P0** | **W1** |
| `SC-002` | **Threat Model (STRIDE) & Abuse Case Register** | **The first threat model in the programme's history.** 59 DFD elements, 9 trust boundaries, **97 threats**, **32 abuse cases**, 3 attack trees. **39 controls buildable, 50 specified-but-absent, 8 threats with no control at all** — the last escalated to `GV-005` as 5 risks | ✅ | **P0** | **W1** |
| `SC-003` | **DPIA — PDPA 2026** | **The first DPIA in the programme's history.** 20 purposes threshold-assessed, **10 full assessments**, 38 privacy risks scored on **harm to individuals**, 13 actions. **Determines `P-14` transcript mining DO NOT PROCEED**, answering `AUDIT-010` `HC-01`. Makes biometric attendance conditional | ✅ ⚠ | **P0** | **Now** |
| `SC-004` | **Identity, Authentication & Authorisation Design** | Extends the role register **38 → 50**, sub-types `R38` into **17** external identities, rules the `R60`/`R49`/`R32` contradiction between two audits, and closes `OP-10` with a **67-profile** template. Rules the `OP-15` leaver-deadline conflict in favour of **one hour** | ✅ | **P0** | **W1** |
| `SC-005` | **Secure Development Lifecycle (SSDLC) Standard** | Converts `LG-021` `IS-06`'s six policy clauses into **15 gates, 31 coding rules, 4 review checkpoints and 99 security test artefacts**. Raises **`G-00`: version control is a precondition — SSDF `PS.1` cannot be met without it** | ✅ | **P0** | W1 |
| `SC-006` | **Cryptography & Key Management Standard** | The standard beneath `M06`'s r2 rebasing: ISO/IEC 19790 zeroization, **IEEE 2883 and 2883.1-2025**, vendor-trust method, certificate defensibility. **Closes `LG-019` `O-07`** with a re-sealing obligation and registers the **2030/2035 algorithm horizon**. Places `K-4` in Bangladesh | ✅ | P0 | W2 |
| `SC-007` | **Data Residency & Cross-Border Transfer Design** | Three-layer write-time enforcement, the transfer gate, the **suspension design `LG-012` §4.5.5 asked for**, 8 quiet-copy prohibitions, and — **closing the design half of `OP-01`** — a `Z4` DR design with three costed options and a recommendation | ✅ | **P0** | **Now** |
| `SC-008` | **Regulatory Compliance Obligations Register** | **Implements the "regulatory currency review" control `00-06` §9 proposed and nobody built.** 9 statutes + 36 standards rows with status and verification date; **10 superseded entries retained and swept, 2 found still live**; 38 engineering obligations; 4 notification clocks; **6 disclosure prohibitions** | ✅ | **P0** | **Now** |
| `SC-009` | **Vulnerability Management & Penetration Test Plan** | **Closes `LG-021` `O-09`** — supplies the discovery mechanism `BRU-SEC-21` presumed. 9 scan classes, CVSS v4.0 with **`Z4`/`Z7` exposure modifiers**, SLAs clocked from discovery, 9 pen-test types on a wave-matched schedule | ✅ | P0 | W2 |
| `SC-010` | **Audit Logging & Forensic Readiness Specification** | Six log classes, three-layer immutability with **external anchoring**, redaction at emission, ISO/IEC 27037 readiness. Raises **`SCA-11`: the audit trail must split across `Z3`/`Z4` or it defeats `SC-007`** | ✅ | P1 | W2 |
| `SC-011` | **Security Incident Response Plan** | The plan behind `OP-004`'s 26 templates. 12 incident classes, a severity scale reconciled with `M66` (**closing `OP-04`**), **11 pre-authorised containment decisions**, the `NFR-094` breach assessment, and a published readiness list — **15 items, 15 absent, 4 closeable before any code is written** | ✅ | **P0** | W2 |

**Counted: 11 documents, 11 ✅ (qualified).** Regenerated by counting rows, per `PG-M10`.

## The four open regulatory exposures — position after authoring

| # | Exposure | Source finding | Closed by | State |
|---|---|---|---|---|
| 1 | The cited data-protection statute (**Digital Security Act 2018**) had been **repealed twice** | `00-06` **C-04a** | `SC-008` | ✅ **Closed at the register level.** 10 superseded instruments now retained with ❌ status and swept; **2 stale citations found still live** and raised |
| 2 | The **PDPA 2026 was not referenced anywhere** — no notices, no CDO, no breach notification, **no regulator named** | `00-06` **C-04b** | `SC-003`, `SC-008`, `SC-011` | ◐ **Substantially closed.** The DPIA exists, obligations are registered, four notification clocks are owned. **The CDO is still unappointed** (`NFR-096`) |
| 3 | The **Singapore-region topology may be unlawful** | `00-06` **C-05** | `SC-007` | ◐ **Closed at the design level.** The legal opinion (`DEP-31`, `D-13`) is still outstanding — and the design is built to survive either answer |
| 4 | **No lawful DR path for Bangladesh-resident personal data** | `AUDIT-017` **OP-01** | `SC-007` §9, `PE-007` | ◐ **Design supplied, three options costed, one recommended. Provisioning outstanding** |

Plus the commercial exposure: **M06 sells data-destruction certificates** built on **NIST SP 800-88
r1, withdrawn 26 September 2025** (`H-01`). `M06` was rebased on r2; **`SC-006` supplies the
cryptographic standard beneath it** — and adds **IEEE 2883.1-2025**, which `M06` does not yet cite.

## What this category found that nobody had asked

| # | Finding | Where |
|---|---|---|
| 1 | **The published "four DPIA references" figure is 4.25× low** — 17 occurrences across 7 files, none of them an assessment. Six consumers, zero producers | `SC-001` §2.4 |
| 2 | **The role target is 50, not 46.** `AR-001` §9.1 is superseded by the later module-set audit | `SC-004` §4.2 |
| 3 | **`00-07` proposed merging `R60` into `R32` — which would have merged an auditor with the auditee** and created an `SOD-20` violation to fix an identifier collision | `SC-004` §4.1 |
| 4 | **The estate cites OWASP ASVS 4** — superseded by 5.0.0 (30 May 2025). **This overview was one of the two documents citing it** | `SC-008` §4.3 |
| 5 | **The audit trail defeats residency unless it is split `Z3`/`Z4`** — an `L1` entry holding an NID's before-value in the regional store is a regional copy of a resident value | `SC-010` §6.3 |
| 6 | **A generated document inherits the classification of the most restricted field it contains** — a tax invoice carrying a TIN is a resident artefact | `SC-007` §6.5 |
| 7 | **A CII designation would require 1000FiX to run its own CERT/CIRT and SOC with quarterly NCSA reporting** — an obligation set nobody has costed | `SC-008` §5.2 |
| 8 | **`M06` destruction certificates outlive their signature algorithm.** RSA/ECC are deprecated after 2030 and disallowed after 2035 (NIST IR 8547) | `SC-006` §10.4 |

## What is still missing — and cannot be closed inside this category

| # | Gap | Owner | Consequence |
|---|---|---|---|
| 1 | **No CISO, no CDO, no Security Lead.** 68 controls, 38 obligations and every SLA name a role that does not exist | CEO / Board | `SC-003` **cannot be signed**; `NFR-096` unmet as enforcement approaches |
| 2 | **Nothing is under version control** — 644+ files | CTO | SSDF `PS.1` cannot be met; `SC-005` `G-00` blocks every other gate |
| 3 | **Break-glass: 6 of 6 readiness items absent** | CTO | The compensating control for a single-IdP architecture. *"Days of work, not months"* |
| 4 | **On-call rota: 0 of 10 named** | CTO / HR | There is nobody to page |
| 5 | **8 of 8 cross-border transfers unregistered**; sub-processor register does not exist | CDO | `SC-005` `G-13` will correctly fail the build for all eight |
| 6 | **No lawful `Z4` DR path; no immutable backup** | CTO | `NFR-007` does not apply to residency-classified data, and the programme must say so |

## Dependencies

| Direction | Category | Relationship |
|---|---|---|
| Upstream | `02_Architecture` | `SC-001` inherits `AR-001` §8's zones and tiers; `SC-002` attacks them |
| Upstream | `03_Data` | `SC-003` and `SC-007` require `DA-002` field classification |
| Downstream | `08_Quality` | **`QA-007` derives from `SC-002` §8 and `SC-004` `AP-12` — 99 test artefacts** |
| Downstream | `10_Infrastructure` | `PE-001` builds `SC-001` §5.2; `PE-007` must answer `SC-007` §9 |
| Downstream | `07_Build` | `SC-005` sets the gates `PE-004` enforces |

## Audience and change frequency

| Attribute | Value |
|---|---|
| Primary audience | CISO, DPO/CDO, legal counsel, architects, auditors, regulators |
| Change frequency | **Medium** — but re-verified at **every wave gate** without exception (`SC-008` §8 `VP-1`) |
| Standards basis | PDPA 2026 (BD) · Cyber Security Ordinance 2025 (BD) · ISO/IEC 27001:2022 + Amd 1:2024 · **ISO/IEC 27701:2025** · **ISO/IEC 29134:2023** · NIST SP 800-88 r2 · IEEE 2883 / **2883.1-2025** · ISO/IEC 19790 · **NIST SP 800-61r3** · NIST SP 800-218 SSDF v1.1 · **OWASP ASVS 5.0.0** · **OWASP Top 10:2025** · CVSS v4.0 · STRIDE |

> **Standards currency corrected at v2.0.** The v1.0 issue of this overview cited **"OWASP ASVS 4"**
> and **"SOC 2"** without qualification. ASVS 4.0.3 is superseded by **5.0.0 (30 May 2025)**, and
> `NFR-089` commits to SOC 2 / ISO 27001 *readiness*, not certification — `SC-008` §10 `DP-1`
> prohibits any claim otherwise. Recorded as `SCA-03`.

## Existing material this category built from

`1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29` (52 `FR-SEC` requirements) ·
`I_Governance_Risk_Quality_and_Knowledge/M60` · `A_Service_Delivery_and_Operations/M06` ·
`05_Cross_Cutting_Specifications/05-02` §10, `05-04`, `05-06` §4 and §6 ·
`00_Governance_and_Charter/00-06` §3 and §9, `00-07` H2-07 · `03_Modules/_MODULE_SET_AUDIT_REPORT` ·
`project_content/10_Legal_Policy_and_Compliance/LG-008`…`LG-012`, `LG-019`, `LG-021`, `LG-024` ·
`06_Process_SOP_and_Workflow/06A_Process_Architecture/SP-006` ·
`17_Operations_Support_and_Runbooks/OP-004`, `OP-009`, `OP-012`, `OP-013`, `OP-015`, `OP-016` ·
`_AUDIT/AUDIT-010` (`HC-01`), `AUDIT-017` (`OP-01`, `OP-02`, `OP-08`, `OP-09`, `OP-10`, `OP-15`, `OP-18`, `OP-19`, `OP-20`)

---

*Category 05 · `SC` · 1000FiX ERP System v2.0 · CONFIDENTIAL*
