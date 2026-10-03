# P01-M08 — Commercial closure, licence policy & vendor position · Completion record

**IR-002 Phase 1, Milestone M08** · Implemented 2026-10-01. Settles `B-11` at
preparation; signature steps are external and tracked.

| Task | Artefact / position | Status |
|---|---|---|
| **T01** Commercial reading record | `CO-003`…`CO-006` verified on disk in `project-guide-doc/14_Commercial_Vendor_and_Contract`; `CO-003` cross-read against the `CR-01` baseline | ✅ |
| **T02** `CO-003-F-08` resolved | [`SoW-F08-resolution.md`](SoW-F08-resolution.md) — baseline-citing amendment clauses; 2,930/101 → maintained 3,389/122 | ✅ prepared (signature external) |
| **T03** Cite the maintained baseline | Clause 1 of the amendment (above) — fixed figures eliminated from the contract | ✅ |
| **T04** Effort restated | 1,842 PW with the 298 PW portal omission recorded; 2.2x the 834 PW approved model (`AF-08`); register cross-check 1,850 PW noted | ✅ |
| **T05** CD count corrected | `CR-P01M08-01` vs `primary-doc` TSS §8.2/§25.3.1: 248 → **331** (machine-verified `cd-register.yaml`) | ✅ CR raised |
| **T06** Licence policy in the pipeline | **Rule (in force):** AGPL-3, BSL, TSL and fair-code components require architecture approval — the `D-030` register (P01-M02, complete enumeration incl. Grafana/Loki/Tempo/Vault conditions) **is** the pipeline's licence policy; automated scan on every dependency addition (`P02-M08-T04` implements the gate; `verify-version-currency.ps1` re-checks upstream licence drift at every gate) | ✅ |
| **T07** Four L6 approvals | Approval records prepared for **TC-070 CPaaS, TC-071 e-signature, TC-072 KYC, TC-073 RMM** — each with the TSS §9 written OSS-alternative assessment already on record (CPaaS: Asterisk viable-but-carrier-gap; e-signature: OSS lacks accreditation; KYC: no OSS equivalent; RMM: deferred to W5 pilot). CFO signature external; **annual review** rides the `D-030` cadence | ✅ prepared |
| **T08** Continuous source delivery | **Position:** all source, configuration, migrations, tests and documentation deliver **continuously** to the Company-controlled repository — the repository is 1000FiX property from commit one (TSS §18.1/RFP §5.10). Contractual confirmation clause prepared; the P02-M03 repository initialisation enforces it structurally | ✅ prepared |
| **T09** SBOM policy + VEX | **Policy:** SBOM (CycloneDX) generated on every build; response windows — **Critical: 48h triage/7d fix-or-VEX · High: 5bd/30d · Medium: 10bd/90d · Low: next release**. `SE-04`: a vulnerability with no fix follows the VEX position — recorded, justified, time-boxed, **never silently suppressed** | ✅ |
| **T10** Three unfunded items | Decision records prepared, each fund-or-descope: **(1)** mobile device lab (`TAF-58`/`Q-04`) — emulator-first policy recorded, real-device coverage at gates only, *the reduction declared*; **(2)** 48 `MD-*` master-data files (`AF-09`) — funded via the W1 content workstream or descoped by name; **(3)** 1,152 unauthored API operations (169–338 PW, `IN-A-01`) — phased: contract-first for W1 consumers, spec-generated for the rest. **`WBS-05`: work with no WBS element will not be resourced** — each record names its WBS element or its descope | ✡ prepared (Steering decides) |

## Standing commercial position (one paragraph for the vendor pack)

The contracted scope is the maintained `CR-01` baseline (3,389/122 today),
delivered continuously into the Company repository, priced against the
restated 1,842 PW effort basis and the 331-item CD register, under the `D-030`
licence policy (four restricted classes replaced, remaining AGPL components
approved with conditions), with SBOM+VEX vulnerability discipline and four
individually-CFO-approved L6 components under annual review.
