---
id: SC-006
title: Cryptography and Key Management Standard
category: 05 — Security, Privacy & Compliance
code: SC
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Chief Technology Officer, delegated to the Security Lead
approver: Design Authority (constituted under GV-002)
standards_basis: >
  NIST SP 800-57 Part 1 Rev. 5 (key management) · FIPS 140-3 (cryptographic module validation) ·
  ISO/IEC 19790 (security requirements for cryptographic modules; key zeroization) ·
  NIST SP 800-88 Rev. 2 (media sanitization, published 26 September 2025) ·
  IEEE 2883-2022 and IEEE 2883.1-2025 (storage sanitization) · ISO/IEC 27040 (storage security) ·
  FIPS 203 / 204 / 205 (post-quantum) with NIST IR 8547 transition · ISO/IEC 27001:2022 A.8.24
traces_to: >
  PGD-000 SC-006 · M06 FR-DTS-020, -020a, -020b, -022 · M29 FR-SEC-044…046 ·
  05-06 NFR-013, NFR-061, NFR-062 · SC-001 §7.5 · LG-021 IS-04 · LG-019 · LG-009 DM-3 ·
  audit findings H-01, LG-021 O-07 (re-sealing), LG-012 RD-R5
depends_on: SC-001 (key flow) · SC-004 (token signing) · SC-007 (Z4 key separation)
verified_on: 2026-08-18
priority: P0
needed_by: W2
enumeration_timestamp: 2026-08-18 14:10 (+06)
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# SC-006 — Cryptography and Key Management Standard

### Category 05 · Code `SC` · NIST SP 800-57 Pt.1 r5 · FIPS 140-3 · ISO/IEC 19790 · NIST SP 800-88r2 · IEEE 2883

---

> **Before writing, read this.**
>
> 1. **`PG-01` Register-first.** This document's row exists in `PGD-000` Category 05 as `SC-006`.
> 2. **`PG-03` Count, do not consult.** Key-class and field figures counted at
>    **2026-08-18 14:10 (+06)**.
> 3. **`PG-06` Cite standards.** §2.1.
> 4. **`PG-M4` Verify citations.** **This is the document `H-01` was raised against.** Every
>    standard below carries a status and a date, and §2.4 states which are current, which are
>    withdrawn and which have a deprecation horizon inside this system's evidential life.

---

## 1. Purpose

This document states **what cryptography this system uses, how key material is created, held,
rotated, escrowed and destroyed, and how a cryptographic claim is made defensible years after it is
made**.

It exists for three reasons, and the third is the one that makes it commercially rather than
merely technically important.

**First**, `NFR-013`, `NFR-061` and `NFR-062` require AES-256 at rest, TLS 1.2+, field-level
encryption with separate key material, and vault-held secrets — **and no document in the estate
names an algorithm suite, a key length policy, a rotation period, a key hierarchy or a destruction
procedure.** `LG-021` `IS-04` states six policy clauses; a policy clause is not a key-management
practice statement.

**Second**, the split-residency architecture has a cryptographic consequence that no document has
yet stated: `LG-012` `RD-R5` requires **keys for residency-restricted data to be held in
Bangladesh**, and `SC-001` `SEC-KM-3` requires `S3` field keys to be **separate from the database
key**. Those two together define a key hierarchy that must be designed before `Z4` is built, not
after.

**Third — and this is the one with money attached — `M06` sells data-destruction certificates as a
commercial product, and the certificate's defensibility *is* the product.** Audit `H-01` (High)
found the module built on **NIST SP 800-88 Revision 1, withdrawn 26 September 2025**, and observed:

> *"A corporate client's security team auditing the certificate would reject it. The commercial
> premise of the module — that its certificate is defensible — is undermined."*

**`M06` has since been rebased on r2**, correctly and thoroughly. What `M06` cannot do, because it
is a module specification rather than a cryptographic standard, is state the **cryptographic-erase
practice** that r2 defers to ISO/IEC 19790 for, the **technique standard** IEEE 2883 supplies, or
the **algorithm-lifetime problem** that makes a certificate signed today questionable in 2035. That
is this document.

### 1.1 Scope

**In scope:**

| # | Covered |
|---|---|
| 1 | **Approved algorithm suite** — symmetric, asymmetric, hashing, KDF, MAC, signature, with key lengths and prohibited legacy |
| 2 | **Protocol configuration** — TLS, database, object storage, message broker, backup |
| 3 | **The key hierarchy** `K-0`…`K-6`, including the `Z4` separation `LG-012` `RD-R5` requires |
| 4 | **Key lifecycle** — generation, distribution, storage, use, rotation, archive, destruction — per SP 800-57 Pt.1 r5 |
| 5 | **Cryptoperiods** per key class, derived rather than asserted |
| 6 | **Vault design constraints** — sealing, unsealing, audit, lease, escrow |
| 7 | **Field-level encryption design** for the 9 `S3` classes |
| 8 | **Cryptographic erase** for `M06` — the `NFR-095`/`LG-009` `DM-3` purge-by-key-destruction path, to ISO/IEC 19790 zeroization |
| 9 | **Sanitisation programme** — the r2 framing, IEEE 2883 technique selection, vendor-trust verification |
| 10 | **Certificate defensibility** — what a destruction certificate must contain to survive an audit in 2035 |
| 11 | **Algorithm agility and the post-quantum transition** — the `LG-021` §4.4.6 and `LG-019` `O-07` re-sealing gap |
| 12 | **Prohibited practice** |

**Explicitly out of scope:**

| Topic | Owned by | Why |
|---|---|---|
| Where key material flows architecturally | `SC-001` §7.5 | This document specifies the material; `SC-001` places it |
| Token signing **configuration** in Keycloak | `SC-004` §7 | This document supplies the algorithm; `SC-004` configures the claim set |
| Which fields are residency-classified | `SC-007` | This document encrypts what it is told to encrypt |
| Vault deployment, HA, unseal ceremony logistics | `PE-001`, `PE-008` | Infrastructure and operations |
| The physical destruction process for media | `M06`, `M18` | This document governs the **cryptographic** technique and the evidence |
| Retention periods | `LG-009` | Referenced, never restated |
| e-signature legal effect | `LG-019` | This document supplies the crypto; `LG-019` states the legal position |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Platform Squad / `M29` developers** | §3 suite, §5 hierarchy, §7 field encryption |
| **`M06` Data Services** | §8, §9, §10 — the crypto-erase and certificate defensibility position |
| **Platform Engineering** | §6 vault constraints |
| **Security Lead** | §11 agility and the PQC horizon |
| **Corporate client security team auditing a destruction certificate** | §10 — this section is written to be handed to them |
| **Auditor / certification body** | A.8.24 crosswalk; §2.4 currency table |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | How this document conforms | Departure and rationale |
|---|---|---|
| **NIST SP 800-57 Part 1 Rev. 5** | §5 key hierarchy uses the standard's key types; §5.4 cryptoperiods are derived from originator-usage and recipient-usage periods rather than chosen | — |
| **FIPS 140-3** | §3.5: cryptographic operations use a **validated module wherever one is available in the selected stack**; where none is, §3.5 states the position rather than implying validation | **The estate budgets no commercial cryptographic module** (`SEC-CON-03`). Claiming FIPS 140-3 validation would be a `LG-021` §4.1.4-class misstatement. §3.5 states what is validated, what is not, and what that means for a client assurance question |
| **ISO/IEC 19790** | §8.2 key zeroization practice for cryptographic erase — **the standard SP 800-88r2 defers to for this purpose** | — |
| **NIST SP 800-88 Rev. 2** *(published 26 September 2025; r1 **withdrawn** the same day)* | §9 adopts the **programme framing**: media sanitisation as an enterprise programme within disposal or reuse, aligned to SP 800-53 and ISO/IEC 27040, with **trust established in vendor implementation** | r2 removed technique detail except cryptographic erase and requires compliance with IEEE 2883, NSA specifications or an organisationally approved standard. **1000FiX names IEEE 2883** |
| **IEEE 2883-2022** and **IEEE 2883.1-2025** | §9.3 technique selection by media type and disposition. **`M06` names IEEE 2883; it does not name 2883.1** | **IEEE 2883.1-2025 is a *recommended practice for use* of the 2883 methods before reuse, resale or disposal — which is exactly `M06`'s business.** Adopted here and raised to `M06` as finding `SCA-08` |
| **ISO/IEC 27040** | Storage security alignment, per r2 | — |
| **FIPS 203 / 204 / 205** *(finalised August 2024)* | §11 — ML-KEM, ML-DSA, SLH-DSA as the migration targets | **Not adopted for W1 production traffic.** §11 states the trigger conditions and the hybrid position |
| **NIST IR 8547** | §11 transition horizon: 112-bit-strength classical algorithms **deprecated after 2030, disallowed after 2035** | This is a **constraint on the evidential life of `M06` certificates and `LG-019` signatures**, not a distant curiosity. §10.4 |
| **ISO/IEC 27001:2022 A.8.24** | Use of cryptography | `SC-001` `SEC-C-046`…`SEC-C-049` |

### 2.2 Source material

| Source | What it supplies |
|---|---|
| `05-06` §4 | `NFR-013` AES-256 / TLS 1.2+ · `NFR-061` field-level encryption with separate key material · `NFR-062` vault |
| `M29` §5.6, §6 | `FR-SEC-044`…`FR-SEC-046`; `T-06` field-level key separation |
| `M06` §4, §5.3, §5.4, §9, §10 | The r2 rebasing; `FR-DTS-020`, `-020a` crypto-erase, `-020b` vendor trust, `-022` certificate; `BRU-DTS-05` per-case keys; `BRU-DTS-08`, `-09`, `-11` |
| `LG-021` `IS-04` | Six policy clauses, including **§4.4.6 algorithm agility and the `LG-019` `O-07` re-sealing gap** |
| `LG-012` `RD-R5` | **Keys for residency-restricted data held in Bangladesh** |
| `LG-009` `DM-3` | **Purge by destruction of the case key** |
| `LG-019` | e-signature evidence statement, and `O-07`: **no re-sealing policy exists** |
| `05-02` §10 | The **9 `S3` fields** requiring field-level encryption |
| `SC-001` §7.5 | The key-material flow this document populates |

### 2.3 Audit findings this document closes

| Finding | Source | Disposition |
|---|---|---|
| **`H-01`** — `M06` built on withdrawn SP 800-88 r1 | `00-06` | **Closed at the standard level.** `M06` rebased on r2; this document supplies the cryptographic-erase practice (ISO/IEC 19790), the technique standard (IEEE 2883 **and 2883.1-2025**), the vendor-trust method, and the certificate content that survives audit |
| **`LG-021` §4.4.6 / `LG-019` `O-07`** — no re-sealing policy for signatures | `LG-021`, `LG-019` | **Closed.** §11.3 specifies the re-sealing obligation and its trigger, and §10.4 states the horizon that makes it necessary |
| `LG-012` `RD-R5` — keys held in Bangladesh, *"subject to `RD8`"* | `LG-012` | **Specified.** §5.3 `K-4` |
| `SC-002` `TH-088` — biometric exfiltration, irreversible | `SC-002` | Treated. §7.3 |
| `SC-002` `TH-040`, `TH-046` — evidence chain broken; certificate without verifiable evidence | `SC-002` | Treated. §10 |
| `SC-001` `SEC-KM-1`…`SEC-KM-7` | `SC-001` | Realised in §5, §6, §7 |

### 2.4 Standards currency — the table `H-01` exists to force

`H-01` happened because a module was built on a standard nobody re-checked. This table is the
control, and it is re-verified at **every wave gate** (`SC-008` obligation `RC-01`).

| Standard | Status **at 2026-08-18** | Consequence for this system |
|---|---|---|
| **NIST SP 800-88 r1** | ❌ **WITHDRAWN 26 September 2025** | Must not be cited. `M06` rebased |
| **NIST SP 800-88 r2** | ✅ **Current**, published 26 September 2025 | §9 governing framework |
| **IEEE 2883-2022** | ✅ Current | §9.3 technique standard |
| **IEEE 2883.1-2025** | ✅ **Current — newer companion `M06` does not cite** | §9.3; finding `SCA-08` |
| **ISO/IEC 19790** | ✅ Current | §8.2 zeroization |
| **NIST SP 800-57 Pt.1 r5** | ✅ Current | §5 |
| **FIPS 140-2** | ❌ Superseded; no new validations | Must not be claimed |
| **FIPS 140-3** | ✅ Current | §3.5 |
| **FIPS 203 / 204 / 205** | ✅ Final, August 2024 | §11 migration targets |
| **NIST IR 8547** | ✅ Current | **RSA/ECC deprecated after 2030, disallowed after 2035** |
| **TLS 1.0 / 1.1** | ❌ Deprecated | Prohibited (§3.2) |
| **SHA-1** | ❌ Broken for collision resistance | Prohibited (§3.4) |
| **3DES** | ❌ Deprecated by NIST | Prohibited (§3.1) |
| **RSA-1024** | ❌ Below 112-bit strength | Prohibited (§3.3) |

> **`SC-006-F-01`. Four of the fourteen rows changed status within the last two years, and one
> changed within the last eleven months.** A standard's status is not a stable fact. `H-01`,
> `C-04a` and `RQA-05` were all **stale-citation findings** — three occurrences of the same defect
> class in one estate. §13 `RM-01` makes re-verification a wave-gate obligation rather than an
> intention.

---

## 3. Approved Algorithm Suite

### 3.1 Symmetric encryption

| Use | Algorithm | Key length | Notes |
|---|---|---:|---|
| **Data at rest — volume/database** | **AES-256-GCM** | 256 | `NFR-013` |
| **Field-level `S3`** | **AES-256-GCM** with per-field-class keys | 256 | **Distinct key material from the database key** (`NFR-061`, `T-06`) |
| **`M06` per-case recovered data** | **AES-256-GCM**, one key per case | 256 | `BRU-DTS-05`; enables `LG-009` `DM-3` purge-by-key-destruction |
| Object storage | AES-256-GCM (server-side) + client-side for `S3` objects | 256 | `DS-06` |
| Backups | AES-256-GCM | 256 | **Backup keys are escrowed separately from data keys** (§5.5) |
| **Prohibited** | 3DES · RC4 · AES-ECB · any unauthenticated mode · AES-CBC without a separate MAC | — | AEAD only |

### 3.2 Transport

| Path | Requirement |
|---|---|
| Internet → `Z0`/`Z1` | **TLS 1.3 preferred; TLS 1.2 minimum** (`NFR-013`). Cipher suites restricted to AEAD with forward secrecy |
| `Z2` service-to-service | **mTLS**, TLS 1.3, certificate-bound identity (RFC 8705) |
| `Z2` → `Z3` / `Z4` | TLS 1.3, certificate-verified, private network |
| `Z2` → `Z6` → third party | TLS 1.3 preferred; **pinned CA set**; downgrade rejected |
| Message broker | TLS 1.3 with client certificates |
| Backup transport | TLS 1.3; payload already encrypted at rest |
| **Prohibited** | TLS 1.0, 1.1 · SSL any version · plaintext on any path including inside a private network · self-signed certificates outside `local` |

> **Encryption inside the private network is not optional.** `SC-001` §10 tenet 2 — *all
> communication is secured regardless of network location* — is adopted, so "it's on the internal
> network" is not a justification anywhere in this estate.

### 3.3 Asymmetric

| Use | Algorithm | Parameters | Horizon |
|---|---|---|---|
| TLS server/client certificates | **ECDSA P-256** preferred; RSA-3072 where required for interoperability | — | **Deprecated after 2030** (IR 8547) |
| Token signing (`SC-004`) | **EdDSA Ed25519**, or ECDSA P-256 | — | Deprecated after 2030 |
| Document and certificate signing (`M06`, `LG-019`) | **ECDSA P-256** or Ed25519 | — | **§10.4 — the evidential-life problem** |
| Key establishment | ECDH P-256 / X25519 | — | Deprecated after 2030 |
| **Prohibited** | RSA < 2048 · DSA · any curve outside the NIST/Ed set · custom curves | — | — |

### 3.4 Hashing, MAC and derivation

| Use | Algorithm | Notes |
|---|---|---|
| General hashing | **SHA-256** or SHA-384 | |
| **Audit hash chain** (`SC-010`) | **SHA-256** | §11.3 re-sealing applies to the chain |
| **Certificate integrity** (`M06`, `LG-019`) | **SHA-256** minimum | §10 |
| Password storage | **Argon2id**, else bcrypt with a tuned cost | Keycloak-managed (`SC-004`) |
| Key derivation | **HKDF-SHA-256** for key hierarchy; Argon2id for password-derived | §5 |
| MAC | HMAC-SHA-256 | Webhook signature verification (`SC-002` `TH-010`) |
| **Prohibited** | MD5 · SHA-1 · unsalted hashes · a bare hash for password storage | |

### 3.5 Module validation — stated honestly

| Component | Validation position |
|---|---|
| TLS termination, database encryption, object storage | Provided by the selected open-source stack and the cloud provider. **Where a FIPS 140-3 validated module is available in the deployment, it is selected and its certificate number recorded** |
| Application-level field encryption | Uses the platform's cryptographic library. **Not independently validated** |
| Vault | **Validated module used where the deployment offers one** |

> **`SC-006-F-02`. 1000FiX does not hold, and may not claim, FIPS 140-3 validation of its
> application-level cryptography.** `SEC-CON-03` budgets no commercial cryptographic module. This
> is stated so that a tender response or a client assurance pack cannot imply otherwise — the same
> discipline `LG-021` §4.1.4 applies to ISO 27001. **What may be claimed** is that approved
> algorithms at approved strengths are used, that validated modules are selected where the platform
> offers them, and that certificate numbers are recorded where they exist. Owner: CTO. Escalated to
> `SC-008` as a **disclosure obligation**, because the difference matters to a government tender.

---

## 4. Key Management Principles

| # | Principle | Source |
|---|---|---|
| `KM-1` | **A key has exactly one purpose.** One key never both encrypts data and signs evidence | SP 800-57 §5.2 |
| `KM-2` | **The application holds a key reference, never key material** | `SEC-KM-2`, `M29` `fix.encryption.key.ref` |
| `KM-3` | **`S3` field keys are separate from the database key**, so a database compromise does not yield the sensitive fields | `NFR-061`, `T-06` |
| `KM-4` | **Keys for residency-restricted data are held in Bangladesh** | `LG-012` `RD-R5` |
| `KM-5` | **Key access is logged and separated from data access.** Holding a role that reads a field is not holding the key that decrypts it | `LG-021` §4.4.5 |
| `KM-6` | **Rotation is scheduled, automated, and does not require re-encrypting all data** — envelope encryption | SP 800-57 §5.3 |
| `KM-7` | **Destruction is verifiable.** A key is not "deleted"; it is **zeroized to ISO/IEC 19790** and the zeroization is evidenced | `M06`, `LG-009` `DM-3` |
| `KM-8` | **No single person can recover a top-level key.** Split knowledge and dual control at `K-0` | §6.2 |
| `KM-9` | **Algorithm agility is a design requirement**, not an aspiration | `LG-021` §4.4.6 |
| `KM-10` | **A cryptographic claim carries the algorithm and the date it was made**, so its strength can be assessed later | §10.4 |

---

## 5. The Key Hierarchy

### 5.1 Structure

```
  K-0  ROOT / UNSEAL                     split knowledge · dual control · offline shares
   │   held: sealed shares, offline, head-office safe + one off-site
   │   used: to unseal the vault. Nothing else.
   ▼
  K-1  VAULT MASTER                      generated in-vault · never exported
   │
   ├──► K-2  DATA-ENCRYPTION KEY ENCRYPTION KEYS (KEK), per domain
   │     │
   │     ├──► K-3  DATABASE / VOLUME DEK        regional (Z3)
   │     │
   │     ├──► K-4  ★ RESIDENT FIELD DEK         Z4 ONLY — key material held in
   │     │         per S3 field class            BANGLADESH (RD-R5), separate
   │     │                                       from K-3 (NFR-061)
   │     │
   │     ├──► K-5  PER-CASE DEK  (M06)          one key per data-recovery case
   │     │                                       ★ purge = zeroize this key
   │     │
   │     └──► K-6  OBJECT-STORAGE DEK           MinIO / evidence photographs
   │
   ├──► K-S  SIGNING KEYS                 token signing (SC-004) ·
   │                                       destruction certificates (M06) ·
   │                                       e-signature evidence (LG-019) ·
   │                                       audit chain anchoring (SC-010)
   │                                       ★ one key per purpose (KM-1)
   │
   └──► K-T  TRANSPORT / PKI              internal CA, service certificates
```

### 5.2 Key register

Every key is registered as `fix.encryption.key.ref` (`M29` §10.1) with: `key_id`, purpose, scope,
`vault_ref`, algorithm, `created_at`, `rotates_at`, `rotated_at`, `retired_at`, `access_roles`.

| Class | Purpose | Location | Rotation | Destruction |
|---|---|---|---|---|
| `K-0` | Vault unseal | **Offline shares**, split | On personnel change or use | Physical destruction of shares, witnessed |
| `K-1` | Vault master | In-vault, never exported | Annual | Vault re-key |
| `K-2` | Domain KEKs | Vault | **Annual** | Zeroize after all wrapped DEKs are re-wrapped |
| `K-3` | Database/volume DEK | Vault-wrapped | **Annual** | Zeroize after re-encryption |
| **`K-4`** | **Resident field DEK, per `S3` class** | **Vault instance in Bangladesh** | **Annual, or on suspicion** | **Zeroize; `Z4` data becomes unrecoverable — this is intentional and is the strongest residency guarantee available** |
| **`K-5`** | **Per-case `M06` DEK** | Vault | **Not rotated — case-lifetime** | **Zeroized at purge. This zeroization *is* the purge** (`LG-009` `DM-3`) |
| `K-6` | Object storage DEK | Vault-wrapped | Annual | Zeroize after re-encryption |
| `K-S` | Signing, one per purpose | Vault; **certificate/e-signature keys additionally escrowed** | **Signing keys rotate; verification keys are retained for the evidential life of what they signed** | **Never destroyed while a signature it produced must remain verifiable** — §10.4 |
| `K-T` | Transport / PKI | Vault + internal CA | Per certificate lifetime (≤ 90 days for service certs) | On revocation |

### 5.3 `K-4` — the residency key separation

> **`SC-006-D-01`. `K-4` is held in a Bangladesh-resident vault instance, not in the regional
> vault.** `LG-012` `RD-R5` requires it and `RD8` marks it subject to confirmation. This document
> takes the position that **it is not optional**, for a reason `LG-012` does not state:
>
> **A key held outside Bangladesh, capable of decrypting Bangladesh-resident data, makes the
> residency control depend on where the key is refused rather than on where the data is.** A
> regulator assessing `NFR-086` would ask *who can decrypt this*, not *where is the ciphertext*.
> Split-residency with a regional key is residency theatre.
>
> **Consequence:** two vault instances, and a `Z4` recovery path that depends on Bangladesh-resident
> key escrow (`SEC-DR-05`). This is an infrastructure cost that `PE-002` must carry, and it is
> raised here rather than discovered during DR design.

### 5.4 Cryptoperiods — derived, not chosen

SP 800-57 Pt.1 r5 derives a cryptoperiod from the originator-usage period plus the recipient-usage
period plus the protection horizon.

| Key class | Originator use | Data protection horizon | **Cryptoperiod** | Basis |
|---|---|---|---:|---|
| `K-3` database DEK | Continuous | Life of the record; `LG-009` up to 7 years | **1 year**, envelope re-wrap | Bounded by exposure, not by data life |
| **`K-4` resident field DEK** | Continuous | **Life of the record; NID retained per `LG-009`** | **1 year**, or **immediately on suspicion** | The highest-consequence class; short period bounds a compromise |
| **`K-5` `M06` case DEK** | Case duration | **Exactly the agreed retention window** | **Case lifetime — deliberately not rotated** | Rotation would create a second key that must also be destroyed. **One key, one destruction, one evidence record** |
| `K-6` object DEK | Continuous | Evidence photograph retention | 1 year | |
| `K-S` token signing | 90 days | Token lifetime ≤ 60 min | **90 days**, overlapping | Verification keys retained one period beyond |
| **`K-S` certificate signing** | **1 year** | **The evidential life of the certificate — potentially decades** | **1 year for signing; verification key retained indefinitely** | **§10.4** |
| `K-T` service certificates | ≤ 90 days | Session | 90 days | Automated |

> **`SC-006-F-03`. `K-5` is deliberately never rotated, and that is the opposite of the general
> rule.** A per-case key exists so that destroying it destroys the data (`LG-009` `DM-3`). Rotating
> it would produce a superseded key that also decrypts the case, so purge would require destroying
> **every** historical key for that case and evidencing each destruction. **One key, one
> zeroization, one certificate.** The design is chosen for the *destruction* property, not the
> *encryption* property.

### 5.5 Escrow and recovery

| # | Rule |
|---|---|
| `ES-1` | **Backup keys are escrowed separately from data keys.** A single compromise must not yield both the backup and its key |
| `ES-2` | **`K-0` shares: split knowledge, dual control**, one set in the head-office safe, one off-site. **This is the same safe `OP-08` break-glass requires and does not have** |
| `ES-3` | **`K-4` escrow is Bangladesh-resident**, or `Z4` has no recovery path — which is `SEC-DR-02` and `OP-01` |
| `ES-4` | **`K-5` is *not* escrowed.** Escrowing a case key would defeat purge-by-destruction. A lost `K-5` means unrecoverable case data, which is the correct failure direction for `M06` |
| `ES-5` | **`K-S` certificate verification keys are archived, never escrowed for signing.** They must verify; they need never sign again |
| `ES-6` | Recovery from escrow is a **break-glass event** (`SC-001` §7.6): loud, multi-party, recorded, time-boxed |

---

## 6. Vault Constraints

| # | Requirement | Source |
|---|---|---|
| `VA-1` | **All secrets originate in the vault.** Never in code, configuration, container images, manifests, logs, tickets or CI output | `NFR-062`, `SR-15` |
| `VA-2` | **Sealed at rest.** Unsealing is a break-glass event requiring `K-0` shares under dual control | `KM-8` |
| `VA-3` | **Every read is audited** with requester, purpose and timestamp | `KM-5` |
| `VA-4` | **Dynamic database credentials with short leases**; static database passwords are prohibited | `SC-001` §7.5 |
| `VA-5` | **Egress credentials are injected at the `Z6` proxy.** The calling application never possesses them | `SEC-KM-5` |
| `VA-6` | **Two instances**: regional and **Bangladesh-resident for `K-4`** | `SC-006-D-01` |
| `VA-7` | Vault availability failure: **fail closed for new leases; existing leases run to expiry** | `SC-001` §12 |
| `VA-8` | **Key access roles are distinct from data access roles.** `R33` IT Administrator holding a data role does not thereby hold the key role | `KM-5` |

---

## 7. Field-Level Encryption

### 7.1 What is field-encrypted

The **9 `S3` classes** (`05-02` §10), counted at 14:10 (+06):

| # | Field class | Key | `Z4`? | Additional |
|---|---|---|:--:|---|
| 1 | National ID number | `K-4` | Yes | Deterministic where an equality lookup is required — §7.2 |
| 2 | Bank account details | `K-3` today; **`K-4` if `RD1`/`SC-003` `A-12` is accepted** | Proposed | Masked except last four |
| 3 | Individual salary and payslip | `K-3`; **`K-4` proposed** | Proposed | |
| 4 | Recovered customer data index | **`K-5` per case** | Yes | Dual control |
| 5 | Call recordings | `K-6` | No | Object-level |
| 6 | **Biometric attendance template** | `K-4` | Yes | **Irreversible template, never exported.** §7.3 |
| 7 | Seller KYC documents | `K-4` | Yes | Object-level in `Z4` |
| 8 | Customer identity documents | `K-4` | Yes | Object-level in `Z4` |
| 9 | API and integration credentials | **Vault-native** | No | Never displayed after creation |

### 7.2 The searchability problem, stated rather than discovered

Field-level encryption breaks equality lookup, range query and sorting. Every system that adopts it
discovers this during build. The positions are fixed here:

| Requirement | Position |
|---|---|
| **Equality lookup on an encrypted field** (find the party with this NID) | **Deterministic encryption with a per-field-class key**, or a **keyed blind index** (HMAC-SHA-256 under a separate index key). Blind index preferred: it leaks equality only, not ciphertext structure |
| **Range or sort on an encrypted field** | **Not supported. Do not design a feature that needs it.** Order-preserving encryption leaks the ordering and is not adopted |
| **Full-text search over an encrypted field** | **Not supported regionally.** `LG-012` §4.4.2: if required at all, it runs in Bangladesh (`SEC-DC-3`) |
| **Reporting and analytics over `S3`** | **Aggregate over a `Z4`-side computation and return the aggregate.** The warehouse never receives the plaintext (`SC-002` `TH-056`) |
| **Uniqueness constraint** | Enforced on the blind index, not on the ciphertext |

> **`SC-006-F-04`.** The blind-index key is `K-4`-class but **distinct from the field DEK** —
> otherwise compromise of the index key yields decryption. This is a `KM-1` application and it is
> the detail most often collapsed in implementation.

### 7.3 Biometric templates — a class of their own

| # | Rule | Because |
|---|---|---|
| `BT-1` | Stored as an **irreversible template**, never as an image or a raw sample | `05-02` §10 |
| `BT-2` | **Never exported** from `Z4`, in any form, for any purpose | `LG-012` §4.3 |
| `BT-3` | Encrypted under `K-4` **with a template-specific sub-key** | `KM-1` |
| `BT-4` | **Matching occurs in `Z4`**; the regional side receives a match/no-match result, never the template | `SEC-DC-2` |
| `BT-5` | Deleted at termination (`LG-009` `RC-13`); deletion is **zeroization**, not a soft delete | `KM-7` |
| `BT-6` | `K-4` template sub-key rotation **re-enrols rather than re-encrypts** where the template format permits | Templates are not re-derivable from ciphertext |

> **`SC-002` `TH-088` rates biometric exfiltration `L2 × I5`, and `SC-003` `DPIA-04` makes the whole
> processing conditional.** The cryptographic position above is the strongest available; it does not
> make the processing proportionate, which is `SC-003`'s determination to make.

---

## 8. Cryptographic Erase

### 8.1 Where it is used

| Use | Mechanism | Evidence |
|---|---|---|
| **`M06` case purge at retention expiry** | Zeroize `K-5` for the case | Purge certificate (`FR-DTS-022`) |
| **`M06` media sanitisation where the media is self-encrypting** | Zeroize the media encryption key | Certificate of Sanitization |
| **Right-to-erasure where a record cannot be deleted for referential reasons** | Zeroize the field key for that subject's data | DSR fulfilment record |
| **`Z4` decommissioning** | Zeroize `K-4` | Recorded destruction |

### 8.2 The zeroization requirement

> **SP 800-88 r2 retains cryptographic erase in detail — and defers its key-zeroization practice to
> ISO/IEC 19790.** This is the specific link `M06` cannot make on its own, and it is the difference
> between "we deleted the key" and a defensible destruction claim.

| # | Requirement |
|---|---|
| `CE-1` | Zeroization follows **ISO/IEC 19790** practice: all copies, all cached instances, all backup instances, all key-share instances |
| `CE-2` | **Every copy of the key is enumerated before zeroization begins.** A key management system that cannot enumerate its own copies cannot perform a cryptographic erase |
| `CE-3` | Zeroization is **verified**, and the verification result is the sanitisation evidence |
| `CE-4` | **The zeroization record, not the key, is retained** — key id, purpose, scope, algorithm, zeroization time, operator, witness, verification result, hash |
| `CE-5` | **Cryptographic erase is valid only where the data was encrypted before it was written.** Encrypting after the fact leaves earlier plaintext on media. This is the most common invalid use of the technique |
| `CE-6` | Where `CE-5` cannot be assured, **fall back to an IEEE 2883 Purge or Destroy technique** and record which was used and why |
| `CE-7` | `K-5` zeroization **completes the `LG-009` `DM-3` purge**; the purge certificate references the zeroization record |

---

## 9. The Media Sanitisation Programme

### 9.1 Programme framing — what r2 changed

r2's material change is framing: **from hands-on sanitisation decisions to establishing an
enterprise media sanitisation programme** as part of disposal or reuse, aligned to SP 800-53 and
ISO/IEC 27040, with **trust established in vendor implementation**. `M06` adopted this. The
programme elements are specified here.

| # | Element | Owner |
|---|---|---|
| `MSP-1` | A **documented sanitisation programme**, approved, reviewed annually | CTO with Quality Manager |
| `MSP-2` | **Media inventory** with classification and disposition, serialised at intake | `M06`, `M45` |
| `MSP-3` | **Technique selection rules** by confidentiality, media type and final disposition (§9.3) | Quality Manager |
| `MSP-4` | **Operator competence and authorisation** — a named, trained, authorised operator per technique | HR / L&D |
| `MSP-5` | **Vendor trust verification** (§9.4) | Procurement with Security Lead |
| `MSP-6` | **Verification** of every sanitisation, recorded | `M06` |
| `MSP-7` | **Evidence retention** per `LG-009` and beyond, for the evidential life of the certificate | `M24` |
| `MSP-8` | **Programme audit** at least annually by `R49` | Internal Audit |

### 9.2 The technique standard

> **SP 800-88 r2 removed technique detail — except cryptographic erase — and requires compliance
> with IEEE 2883, NSA specifications, or an organisationally approved standard.**
>
> **1000FiX names IEEE 2883-2022 as its approved technique standard, and IEEE 2883.1-2025 as the
> recommended-practice reference for applying those methods before reuse, resale or disposal.**

### 9.3 Technique selection

IEEE 2883 defines **Clear**, **Purge** and **Destruct**. Selection is by confidentiality, media
type and disposition — never by habit.

| Data confidentiality | Disposition | Media type | Technique |
|---|---|---|---|
| `S0`/`S1` | Reuse internally | any | **Clear** |
| `S2` | Reuse internally | any | **Clear**, verified |
| `S2` | Resale / external reuse | SSD/flash | **Purge** (sanitize command) or **crypto-erase** where `CE-5` holds |
| **`S3`** | **Reuse internally** | any | **Purge**, verified |
| **`S3`** | **Resale / external reuse** | HDD | **Purge**, verified |
| **`S3`** | **Resale / external reuse** | SSD/flash | **Purge via device sanitize + crypto-erase**, both, verified |
| **`S3`** | **Disposal** | any | **Destruct** |
| **Recovered customer data (`M06`)** | any | any | **Crypto-erase of `K-5` + Purge of the media**; **Destruct where the customer requires it** |
| Unknown or unverifiable media | any | any | **Destruct.** An unverifiable Purge is not a Purge |

> **`BRU-DTS-08` already requires selection by confidentiality, media type and disposition under a
> documented programme.** This table is that programme's selection rule, made explicit so an
> operator does not choose.

### 9.4 Vendor trust verification — the r2 addition

r2 adds an explicit requirement to **establish trust in a vendor's implementation** of sanitisation.
`M06` `FR-DTS-020b` records it as a requirement; this is the method.

| # | Verification |
|---|---|
| `VT-1` | The vendor states which standard its technique implements, and which version |
| `VT-2` | Independent validation evidence, where it exists — certification, test report, or a public conformance claim traceable to a named test |
| `VT-3` | **1000FiX-performed sampling**: a periodic independent verification that sanitised media returns no recoverable data |
| `VT-4` | The **firmware or tool version** used is recorded per sanitisation event — a technique is only as trustworthy as the build that ran it |
| `VT-5` | A vendor that will not supply `VT-1` and `VT-2` **is not used for `S3` media** |
| `VT-6` | Verification is **re-performed annually** and on any vendor tool-version change |

---

## 10. Certificate Defensibility

> **This section is written to be handed to a corporate client's security team.** `H-01`'s
> consequence was precisely that such a team *"would reject"* a certificate citing a withdrawn
> standard. The content below is what makes rejection unreasonable.

### 10.1 Required certificate content

| # | Field | Why a reviewer needs it |
|---|---|---|
| 1 | Serialised certificate number | Uniqueness; the verification lookup key |
| 2 | **Media serial number** | `BRU-DTS-11`: **blanket certificates are not permitted.** A certificate that does not name the device proves nothing about that device |
| 3 | Asset identifier and customer reference | Reconciliation against the client's own asset list |
| 4 | **Technique applied** — Clear / Purge / Destruct, and the specific method | |
| 5 | **Standard and version** — *"IEEE 2883-2022, applied under NIST SP 800-88 r2"* | The `H-01` field |
| 6 | **Tool and firmware version** | `VT-4` |
| 7 | Operator identity and authorisation | `MSP-4` |
| 8 | Witness identity | `05-04` §7: data destruction requires technician + witness |
| 9 | Date and time, with timezone | |
| 10 | **Verification result and method** | A technique without verification is an assertion |
| 11 | **Where cryptographic erase was used**: key id, algorithm, **ISO/IEC 19790 zeroization confirmation** | §8.2 |
| 12 | **Hash of the certificate content, and the signing algorithm and date** | `KM-10`; §10.4 |
| 13 | Verification URL / endpoint | `M06` `T-08` |

### 10.2 Tamper evidence

| # | Requirement |
|---|---|
| `CD-1` | Certificates are **hashed and countersigned** (`M06` `T-08`) |
| `CD-2` | A **verification endpoint confirms authenticity by certificate number** within 500 ms (`M06` `T-13`) |
| `CD-3` | The certificate store is **insert-only**; a certificate is never edited, only superseded with both versions retained |
| `CD-4` | **The gate fails closed**: no certificate, no proceed to refurbishment, resale or recycling (`BRU-DTS-09`, `T-11`) |

### 10.3 What the certificate must not claim

| # | Prohibition | Because |
|---|---|---|
| `CN-1` | **Must not cite SP 800-88 r1** | Withdrawn 26 September 2025 |
| `CN-2` | **Must not imply FIPS 140-3 validation** of 1000FiX's own cryptography | §3.5 |
| `CN-3` | **Must not imply ISO 27001 certification** | `LG-021` §4.1.4 |
| `CN-4` | **Must not state "data is unrecoverable" without naming the technique and its verification** | An unqualified absolute is the claim a reviewer attacks first |
| `CN-5` | **Must not be blanket** — one certificate, one media serial | `BRU-DTS-11` |

### 10.4 The evidential-life problem — closing `LG-019` `O-07`

> **A certificate signed in 2027 is inside its evidential life when its signature algorithm becomes
> disallowed.**

**NIST IR 8547** (verified 2026-08-18): 112-bit-strength classical algorithms — RSA-2048, ECDSA
P-256 — are **deprecated after 2030 and disallowed after 2035**. `M06` certificates and `LG-019`
e-signature evidence are relied on for the life of the asset and of any dispute arising from it —
plausibly a decade or more.

`LG-021` §4.4.6 already identifies the gap and names it precisely: *"a hash or cipher chosen today
must be replaceable — and `LG-019` `O-07` records that no re-sealing policy exists for signatures,
which is the same problem."*

**The position, closing `O-07`:**

| # | Rule |
|---|---|
| `RS-1` | **Every signature and hash chain records its algorithm and the date it was applied** (`KM-10`) |
| `RS-2` | **A re-sealing obligation exists**: when a signing algorithm enters deprecation, every artefact still within its evidential life is **re-sealed** — countersigned under a current algorithm, with the original signature and its verification key preserved |
| `RS-3` | **Re-sealing preserves, never replaces.** The original signature remains verifiable; the re-seal attests that the original was valid at the time of re-sealing |
| `RS-4` | **`K-S` verification keys are archived for the evidential life of what they signed**, never destroyed on rotation (`ES-5`) |
| `RS-5` | **Re-sealing triggers**: an algorithm entering deprecation; a hash function weakened; **and unconditionally at the 2030 deprecation horizon** for anything with an evidential life beyond 2035 |
| `RS-6` | Re-sealing is **planned and budgeted as an operational activity**, not discovered in 2034. Owner: CTO. First review: W4 |

> **`SC-006-F-05`.** `RS-5`'s unconditional trigger means the programme has a **dated, foreseeable
> obligation** with a known deadline. It is registered in `SC-008` as obligation `CR-31` with a
> review date, which is the whole purpose of a currency register — the control that would have
> prevented `H-01`, `C-04a` and `RQA-05`.

---

## 11. Algorithm Agility and the Post-Quantum Transition

### 11.1 Agility as a design requirement

| # | Rule |
|---|---|
| `AG-1` | **A cipher, hash or signature algorithm is referenced through a configurable suite, never hard-coded** (`SR-19`) |
| `AG-2` | **Ciphertext and signatures carry an algorithm identifier and a version**, so a mixed estate remains decryptable and verifiable during migration |
| `AG-3` | **Key material carries its algorithm** in the key register |
| `AG-4` | The estate must be able to **re-encrypt under a new algorithm without downtime**, via envelope encryption and background re-wrap |
| `AG-5` | **Agility is tested**, not assumed: a rehearsed algorithm change on a non-production dataset at least once before W8 |

### 11.2 Position on post-quantum

| # | Position |
|---|---|
| `PQ-1` | **FIPS 203 (ML-KEM), FIPS 204 (ML-DSA) and FIPS 205 (SLH-DSA) are the migration targets.** Finalised August 2024 |
| `PQ-2` | **Not adopted for W1 production traffic.** The stack's mature support, and the 47 external integration counterparties, do not yet make it practical |
| `PQ-3` | **Hybrid key establishment (classical + ML-KEM) is adopted for TLS as soon as the deployed stack supports it without interoperability loss** — this is the lowest-risk first step and it protects against harvest-now-decrypt-later |
| `PQ-4` | **Long-lived signatures are the priority, not transport.** A TLS session decrypted in 2040 is of little value; **a destruction certificate or e-signature forged in 2040 is a live liability**. `SLH-DSA` is the conservative choice for `K-S` certificate signing when migration begins |
| `PQ-5` | **Review at every wave gate**; first substantive migration decision at **W4** |
| `PQ-6` | The **2030 deprecation and 2035 disallowance horizons are registered obligations** (`SC-008` `CR-31`), not background knowledge |

> **`SC-006-F-06`. `PQ-4` inverts the usual priority and should be read carefully.** Most PQC
> migration guidance leads with transport. For 1000FiX the **highest-value cryptographic asset is a
> signature that must remain defensible for a decade** — and that asset is a commercial product.
> **Harvest-now-decrypt-later threatens confidentiality; forge-later threatens the `M06` business
> line.** The migration order follows from the business, not from the protocol stack.

---

## 12. Prohibited Practice

| # | Prohibited | Because |
|---|---|---|
| `PR-1` | **Implementing a cryptographic primitive.** Use the approved library | `SR-14` |
| `PR-2` | Any algorithm in the §2.4 prohibited list | Superseded or broken |
| `PR-3` | **A key in source, configuration, an image, an environment variable in a manifest, a log or a ticket** | `NFR-062` |
| `PR-4` | **The same key for two purposes** | `KM-1` |
| `PR-5` | **Encrypting with the database key what `NFR-061` requires a separate key for** | `KM-3` |
| `PR-6` | **Order-preserving or format-preserving encryption to make a field searchable or sortable** | §7.2 |
| `PR-7` | **Escrowing `K-5`** | Defeats purge-by-destruction |
| `PR-8` | **Destroying a `K-S` verification key while a signature it produced is within evidential life** | `RS-4` |
| `PR-9` | **Claiming FIPS 140-3 validation, ISO 27001 certification, or unqualified unrecoverability** | §3.5, `CN-2`…`CN-4` |
| `PR-10` | **Cryptographic erase where the data was not encrypted before it was written** | `CE-5` |
| `PR-11` | Plaintext on any network path, including private | §3.2 |
| `PR-12` | **Holding `K-4` outside Bangladesh** | `SC-006-D-01` |

---

## 13. Maintenance

| # | Trigger | Action | Owner |
|---|---|---|---|
| `RM-01` | **Every wave gate** | Re-verify the §2.4 currency table. **This is the control `H-01` exists to force** | Security Lead |
| `RM-02` | A standard is withdrawn or superseded | Assess impact within 30 days; update citations; **re-issue any certificate content that names it** | Security Lead |
| `RM-03` | An algorithm is weakened or deprecated | Trigger `RS-2` re-sealing assessment and `AG-4` re-encryption planning | Security Lead |
| `RM-04` | A key is suspected compromised | Immediate rotation; `SC-011` incident; assess data encrypted under it | CTO |
| `RM-05` | A vendor sanitisation tool changes version | Re-perform `VT-1`…`VT-4` | Quality Manager |
| `RM-06` | Annually | Sanitisation programme audit (`MSP-8`); agility rehearsal (`AG-5`) | `R49` |
| `RM-07` | **2030 approaches** | Execute the PQC migration decision made at W4 | CTO |

---

## 14. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | Is a **Bangladesh-resident vault instance** funded for `K-4`? | CTO with CFO | **W1 architecture freeze** | `SC-006-D-01`; `Z4`; `PE-002` sizing |
| `Q-02` | Does `LG-012` `RD8` confirm the in-country key requirement? | Legal Counsel | W1 | `KM-4` |
| `Q-03` | Do bank details and individual payroll move to `K-4`? (`RD1`, `SC-003` `A-12`) | CDO with EA | W1 | §7.1 rows 2–3 |
| `Q-04` | Is `Z4` key escrow in Bangladesh provisioned, or does `Z4` have no recovery path? | CTO | **W2** | `ES-3`; `OP-01`; `SEC-DR-02` |
| `Q-05` | Is a FIPS 140-3 validated module available in the chosen deployment, and is its use funded? | CTO | W2 | §3.5; government tender responses |
| `Q-06` | Is re-sealing (`RS-6`) budgeted as an operational activity? | CFO with CTO | W4 | `LG-019` `O-07`; `M06` defensibility |
| `Q-07` | Does `M06` adopt **IEEE 2883.1-2025** alongside 2883-2022? | Quality Manager | W2 | `SCA-08` |
| `Q-08` | Who witnesses `K-0` share ceremonies, and where is the safe? | CTO | W1 | `ES-2`; shares the `OP-08` break-glass gap |

---

## 15. Decisions Recorded

| # | Decision | Options | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `SC-006-D-01` | `K-4` location | Regional vault · **Bangladesh-resident vault** | **Bangladesh** | A regional key that decrypts resident data makes residency depend on refusal rather than location — residency theatre | Two vault instances; `Z4` recovery depends on in-country escrow; `PE-002` cost |
| `SC-006-D-02` | `K-5` rotation | Annual like other DEKs · **Never** | **Never — case lifetime** | Rotation creates additional keys that must also be destroyed for purge to be complete | `ES-4` no escrow; a lost `K-5` is unrecoverable, which is the correct failure direction |
| `SC-006-D-03` | Encrypted-field search | OPE/FPE · Deterministic · **Blind index** | **Blind index (HMAC), separate key** | OPE leaks ordering; deterministic leaks equality through the ciphertext itself | No range or sort on `S3`; features requiring them are redesigned |
| `SC-006-D-04` | FIPS claim | Claim alignment · **State the position** | **State it** | `SEC-CON-03` funds no validated module; an implied claim is a misstatement to a government tender | `SC-008` disclosure obligation |
| `SC-006-D-05` | Certificate signing horizon | Ignore PQC · **Prioritise long-lived signatures** | **Prioritise signatures over transport** | Forge-later threatens the `M06` business line; harvest-now threatens confidentiality of already-short-lived sessions | `RS-5` unconditional 2030 trigger; W4 migration decision |
| `SC-006-D-06` | Technique standard | Organisationally approved internal standard · **IEEE 2883 + 2883.1** | **IEEE 2883-2022 + 2883.1-2025** | r2 permits an internal standard; inventing one where an accredited standard exists is the position `M06` §4 already rejected | `SCA-08` raised to `M06` |

---

## 16. Acceptance Criteria

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every algorithm in use is named with a key length and a prohibition list | §3 |
| `AC-02` | Every standard cited carries a **status and a date** | §2.4 — 14 rows, 5 marked withdrawn/prohibited |
| `AC-03` | The key hierarchy is complete from unseal to field | §5.1 — `K-0`…`K-6`, `K-S`, `K-T` |
| `AC-04` | Cryptoperiods are **derived** from usage and protection horizons | §5.4 |
| `AC-05` | The residency key separation is specified and argued | §5.3; `SC-006-D-01` |
| `AC-06` | Cryptographic erase references ISO/IEC 19790 and states when it is **invalid** | §8.2 `CE-5` |
| `AC-07` | The sanitisation programme has all eight r2 elements | §9.1 |
| `AC-08` | Technique selection is a rule, not an operator choice | §9.3 |
| `AC-09` | Vendor trust verification has a method | §9.4 |
| `AC-10` | Certificate content survives a client security review, and prohibitions are stated | §10.1, §10.3 |
| `AC-11` | The re-sealing gap `LG-019` `O-07` is closed | §10.4 `RS-1`…`RS-6` |
| `AC-12` | A PQC position exists with a trigger and a date | §11.2; `RM-07` |

---

## 17. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `SC-001` §7.5 | The key flow this populates |
| Upstream | `SC-004` §7 | Token signing algorithm consumer |
| Upstream | `SC-007` | Tells this document what is residency-classified |
| Downstream | `SC-005` | `SR-14`, `SR-19` reference §3 |
| Downstream | `SC-010` | Audit hash chain algorithm and re-sealing |
| Downstream | `SC-008` | `CR-31` the 2030/2035 obligation; the FIPS disclosure obligation |
| Downstream | `M06` | §8, §9, §10 — and `SCA-08` (IEEE 2883.1) |
| Downstream | `M29` | `FR-SEC-044`…`046` realisation |
| Downstream | `PE-002`, `PE-008` | Vault instances; `K-0` ceremony |
| Lateral | `../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_*.md` | The commercial product this defends |
| Lateral | `../../project_content/10_Legal_Policy_and_Compliance/LG-019_*.md`, `LG-021_*.md`, `LG-009_*.md`, `LG-012_*.md` | e-signature, ISMS `IS-04`, `DM-3`, `RD-R5` |

---

## 18. References

**Within this repository**
`../PGD-000_*.md` · `./_CATEGORY_OVERVIEW.md` · `./SC-001`, `./SC-004`, `./SC-005`, `./SC-007`, `./SC-010`

**Workspace**
`../../1000fix_ERP_Module/03_Modules/A_Service_Delivery_and_Operations/M06_*.md` ·
`../../1000fix_ERP_Module/03_Modules/K_Platform_and_Technology/M29_*.md` ·
`../../1000fix_ERP_Module/05_Cross_Cutting_Specifications/05-02_*.md` §10, `05-06_*.md` §4 ·
`../../1000fix_ERP_Module/00_Governance_and_Charter/00-06_*.md` (`H-01`) ·
`../../project_content/10_Legal_Policy_and_Compliance/LG-009_*.md`, `LG-012_*.md`, `LG-019_*.md`, `LG-021_*.md`

**External standards** *(all verified 2026-08-18 — see §2.4 for status)*

| Source | Version / status | Used for |
|---|---|---|
| NIST SP 800-57 Part 1 | Rev. 5 — current | §5 key management |
| FIPS 140-3 | Current (**140-2 superseded**) | §3.5 |
| ISO/IEC 19790 | Current | §8.2 zeroization |
| **NIST SP 800-88** | **r2, published 26 September 2025. r1 WITHDRAWN the same day** | §9 programme framing |
| **IEEE 2883** | **2883-2022** — technique standard | §9.3 |
| **IEEE 2883.1** | **2883.1-2025** — recommended practice for applying 2883 before reuse, resale or disposal | §9.3; `SCA-08` |
| ISO/IEC 27040 | Current — storage security | r2 alignment |
| **FIPS 203 / 204 / 205** | **Finalised August 2024** — ML-KEM, ML-DSA, SLH-DSA | §11 |
| **NIST IR 8547** | Current — **112-bit classical deprecated after 2030, disallowed after 2035** | §10.4, §11 |
| ISO/IEC 27001 | :2022 + Amd 1:2024 — A.8.24 | Control basis |

---

## 19. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Supplies the cryptographic standard `M06`'s r2 rebasing needs beneath it: ISO/IEC 19790 zeroization, IEEE 2883 **and 2883.1-2025**, vendor-trust method, certificate defensibility content and prohibitions. **Closes `LG-019` `O-07`** with a re-sealing obligation, and registers the **2030/2035 algorithm horizon** as a dated obligation. Places `K-4` in Bangladesh | *Pending — no constituted body (`PGD-A2-25`)* |

---

*`SC-006` · Category 05 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
