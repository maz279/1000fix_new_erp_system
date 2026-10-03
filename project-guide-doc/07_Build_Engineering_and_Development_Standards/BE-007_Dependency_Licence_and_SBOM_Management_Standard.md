---
id: BE-007
title: Dependency, Licence & SBOM Management Standard
category: 07 — Build Engineering & Development Standards
code: BE
project: 1000FiX ERP System v2.0
version: 1.0
date: 2026-08-18
status: DRAFT FOR APPROVAL
classification: CONFIDENTIAL — Internal Use Only
owner: Engineering Lead
approver: Chief Architect
standards_basis: >
  CycloneDX 1.7 (ECMA-424, 2nd edition) · SPDX 3.0.1 · OpenVEX · SPDX licence identifiers ·
  NIST SP 800-218 (SSDF) PW.4, PS.3, RV.1–RV.3 · SLSA build levels · Semantic Versioning 2.0.0
traces_to: >
  PGD-000 BE-007 · 02-05 §4 (licence compliance notes) · Technology Stack Specification §7.3, §18.5, §25.2 ·
  risk TR-09 (upstream licence change) · TR-04 (OCA fork) · AR-012 FF-30 · DoD-15
depends_on: BE-004 (lockfile placement, vendoring) · BE-006 (component SBOM contribution)
verified_on: 2026-08-18
enumeration_timestamp: 2026-08-18 13:06 (+06)
priority: P1
needed_by: W1
register: ../PGD-000_Master_Register_of_Project_Guiding_Documents.md
---

# BE-007 — Dependency, Licence & SBOM Management Standard

### Category 07 · Code `BE` · CycloneDX 1.7 · SPDX 3.0.1 · NIST SP 800-218 · SLSA

---

## 1. Purpose

`PGD-000` records this document as **◐ — partial, covered by `02-05` §4**, and that assessment is
generous in one direction and harsh in the other.

`02-05` §4 and TSS §7.3 are **good licence analysis**. They correctly identify AGPL-3 network-use
obligations, LGPL-3's modification rule, n8n's Sustainable Use restriction, Redpanda's BSL conversion
and TimescaleDB's TSL boundary, and they name a fallback for each. That analysis is not repeated
here; it is adopted.

What does not exist is the **mechanism**. TSS §7.3 states that *"a licence register is maintained in
M30, reviewed annually"* — M30 is a Wave 1 module that has not been built, so the register does not
exist and has never been reviewed. Compliance therefore rests on developers remembering an analysis
written in a document they may not have read.

This document supplies the mechanism: how a dependency is added, pinned, scanned, updated and
retired; what the licence register is as a file; how the SBOM is produced and what it is for; and how
long the programme has to respond when a vulnerability is published.

> **The analysis has already been overtaken once, and nobody noticed.** §7.1 records that **MinIO —
> the Wave 1 object store — had its open-source repository archived on 25 April 2026**, four months
> before this document's date and eight months before Wave 1 would deploy it. TSS was version-verified
> on 13 August 2026 and still lists MinIO as a current L4 component. This is `TR-09` materialising on
> a foundation component, and an annual review would not have caught it.

### 1.1 Scope

**In scope**

| # | Covered |
|---|---|
| 1 | The dependency **admission** procedure — what must be true before a dependency is added |
| 2 | **Pinning** across five ecosystems, and what `versions.lock` is |
| 3 | **Update cadence** — routine, security and major |
| 4 | **Vulnerability response** — severity model, service levels, and the VEX position |
| 5 | The **licence register** as a file, and its automated check |
| 6 | The **AGPL-3 modification test**, applied to this stack specifically |
| 7 | **SBOM** — format, generation point, retention and consumers |
| 8 | **Licence and lifecycle currency watch**, and the MinIO finding |
| 9 | The **Odoo and OCA** upgrade path, including the "LTS" claim |
| 10 | Supply-chain integrity — provenance, SSDF and SLSA position |
| 11 | Regulatory applicability, including what does **not** apply and why |

**Explicitly out of scope**

| Topic | Owned by | Why |
|---|---|---|
| Which technology is selected | `02-05` §7, `AR-013` | Selection vs stewardship |
| Vendoring mechanics — submodule, subtree, `FORKS.yaml` | `BE-004` §5 | This document governs versions and licences; `BE-004` governs placement |
| Security control design, penetration testing | `SC-005`, `SC-008` | §5 is the dependency slice only |
| Commercial licence procurement (L6) | `CO-002`, `CO-004` | This document covers open-source obligations |
| Runtime container and infrastructure scanning | `PE-007` | §5.4 states the requirement |
| Contract versioning between services | `BE-003` `GW-10`, `IN-002` | Internal interfaces, not third-party dependencies |

### 1.2 Intended audience

| Audience | Use |
|---|---|
| **Every developer** | §3 — what to do before adding a dependency, and why the answer is sometimes no |
| Chief Architect | §3.3's approval gate for AGPL, BSL, TSL and fair-code components |
| Security Lead | §5's response service levels; §9's SSDF and SLSA position |
| Legal / Company Secretary | §6's obligation register and §6.3's AGPL test |
| Platform Engineering | §7's SBOM generation and §4's update automation |
| CFO / procurement | §7.1 — a component going end-of-life is a cost event, not only a technical one |

---

## 2. Basis and Inputs

### 2.1 Standards conformance

| Standard | Conformance | Departure and rationale |
|---|---|---|
| **CycloneDX 1.7** (ECMA-424, 2nd edition) | The build-time SBOM format for every artefact | Full. Chosen over SPDX for build integration; §7.2 |
| **SPDX 3.0.1** | Produced on demand for external exchange — corporate clients, auditors, brand partners | Both formats are produced; §7.2 gives the reasoning |
| **OpenVEX** | Vulnerability exploitability statements accompany the SBOM | Full. Without VEX, a scanner's raw output is unactionable at this dependency count |
| **SPDX licence identifiers** | Every dependency records a valid SPDX identifier | Full |
| **NIST SP 800-218 (SSDF) v1.1** | PW.4 (reuse well-secured software), PS.3 (archive and protect releases), RV.1–RV.3 (identify, assess and respond to vulnerabilities) | Full; §9.1 maps the practices |
| **SLSA** | Build provenance and integrity | **Target Build Level 2 by the W1 gate, Level 3 by the W3 gate.** §9.2 states why not Level 3 immediately |
| **Semantic Versioning 2.0.0** | Internal library versioning and dependency range policy | Full; `LX-08` |

### 2.2 Source material relied on

| Source | Contribution |
|---|---|
| `02-05` §4 "Licence Compliance Notes" | The original obligation analysis — AGPL-3, LGPL-3, Sustainable Use, BSL, TSL |
| **TSS §7.3** | The extended obligation table — **six** AGPL-3 components, GPL-2 for Wazuh, the attribution register, and `TR-09` |
| TSS §18.5 | Pinning, vulnerability alerts, monthly cadence, licence scan on every dependency addition, AGPL/BSL/TSL architecture approval |
| TSS §25.2 | The five version-currency findings, including Odoo, Next.js, PostgreSQL, Keycloak and the mobile framework |
| TSS §7.4 | The registered fallback for each at-risk component — the input to §7.3's watch |
| `02-05` §3 | 18 OCA repositories, their v19 migration status, and the contribute-back commitment |
| `AR-007` §3.3 | The module licence rule: LGPL-3, with architecture approval for any AGPL-3 dependency |
| `AR-012` `FF-30` | SAST, dependency, container, IaC and licence scans; block on high or critical |
| `BE-004` §5 | `vendor/`, the submodule pin and the eighteen subtrees this document versions |

### 2.3 One inherited inconsistency, corrected

`02-05` §4 lists the AGPL-3 components as **"Metabase, Grafana, MinIO, RustDesk"** — four. TSS §7.3
lists **"Metabase, Grafana, MinIO, RustDesk, Loki, Tempo"** — six.

TSS is correct. Grafana Labs relicensed Grafana, Loki and Tempo from Apache-2.0 to AGPLv3 in April
2021; the observability stack that TSS §20.2 deploys in Wave 3 therefore carries three AGPL
components, not one. `02-05` §4 predates the recount and understates the AGPL surface by half.

**This document uses the TSS list.** Raised as finding `BEA-14`, and it is a small illustration of the
larger point: a licence position stated in prose in two documents will diverge, which is why §6.1
makes it a file.

---

## 3. Admission

### 3.1 The rule

| # | Rule |
|---|---|
| **`LX-01`** | A dependency is added by a **pull request that adds it and nothing else** (`REPO-18`). It is never a side effect of a feature change |
| **`LX-02`** | The PR states: what it is for; the licence (SPDX identifier); the maintenance signal — last release, release cadence, maintainer count, open critical issues; the transitive count it brings; and **what would be done if it were abandoned** |
| **`LX-03`** | Every dependency is recorded in `tooling/versions.lock` with an exact version or commit, and in the ecosystem lockfile |
| **`LX-04`** | A lockfile change is reviewed. A lockfile that changes without a corresponding manifest change is investigated, not approved |

### 3.2 The maintenance test

`LX-02`'s "what would be done if it were abandoned" is not a formality. The programme runs on a stack
of open-source components for **36 months**, and §7.1 shows one of them reaching end of life inside
the specification period.

| Signal | Threshold that requires justification |
|---|---|
| Last release | > 12 months ago |
| Maintainers | 1 |
| Open critical issues | > 5, or any older than 6 months |
| Transitive dependencies introduced | > 20 |
| Downloads / adoption | Materially below alternatives |

### 3.3 The approval gate

| Licence class | Approval | Rationale |
|---|---|---|
| MIT, Apache-2.0, BSD, ISC, PostgreSQL | Squad reviewer | Attribution only |
| **LGPL-3** | Squad reviewer | The estate is already LGPL-3; `AR-007` §3.3 |
| **AGPL-3** | **Chief Architect** | Network-use disclosure. §6.3's test must be answered in writing |
| **BSL, TSL, SSPL, Elastic, fair-code (n8n), Sustainable Use** | **Chief Architect + CFO** | A commercial obligation can arise from a usage change, not only a code change |
| **GPL-2 / GPL-3** *(linked, not merely deployed)* | **Chief Architect + Legal** | Copyleft propagation |
| Unknown, custom, or no licence | **Prohibited** | Not a review question |

| # | Rule |
|---|---|
| **`LX-05`** | An approval is recorded in `tooling/LICENCES.yaml` (§6.1), with the approver, the date and the **reason**. An approval that is not in the file did not happen |
| **`LX-06`** | The gate applies to **transitive** dependencies. A permissive package that pulls in an AGPL transitive dependency requires the AGPL approval |

> **`LX-06` is where licence compliance is actually lost.** Nobody adds MongoDB's SSPL driver
> deliberately; it arrives four levels down a dependency tree, and the licence scan is the only thing
> that sees it.

---

## 4. Pinning and Update Cadence

### 4.1 Pinning, by ecosystem

| Ecosystem | Manifest | Lockfile | Pin form |
|---|---|---|---|
| Python | `pyproject.toml` | `uv.lock` | Exact version + hash |
| Node / TypeScript | `package.json` | `pnpm-lock.yaml` | Exact version + integrity |
| Dart / Flutter | `pubspec.yaml` | `pubspec.lock` | Exact version |
| Go | `go.mod` | `go.sum` | Version + hash |
| Containers | Compose / Helm | `tooling/versions.lock` | **Digest**, never a tag |
| Odoo core | `.gitmodules` | `tooling/versions.lock` | Commit SHA |
| OCA (×18) | subtrees | `tooling/versions.lock` | Repository + commit SHA |

| # | Rule |
|---|---|
| **`LX-07`** | **Everything is pinned exactly.** No range operators (`^`, `~`, `>=`) in any manifest, in any ecosystem. A range is a promise that upstream will not break, made by someone who cannot keep it |
| **`LX-08`** | Internal libraries in `libs/**` are SemVer-versioned; consumers pin exact and upgrade deliberately. A public signature change is MAJOR (`PYS-11`) |
| **`LX-09`** | `tooling/versions.lock` is the **single index** of every non-language-ecosystem pin — containers, Odoo, OCA, tool binaries. It is what `BE-001` `make doctor` and `PE-004` read |

### 4.2 Cadence

| Class | Cadence | Route | Approval |
|---|---|---|---|
| Patch, no CVE | **Monthly**, batched by ecosystem | Automated PR, full CI | Squad |
| Minor, no CVE | Monthly, reviewed individually | Automated PR | Squad |
| **Security patch** | **Out of cycle**, per §5.2 | Expedited | Security Lead |
| Major | **Deliberate**, planned into a wave | Its own PR with a migration note | Chief Architect |
| **Odoo core** | Monthly patch within 19.0 | Submodule pin bump | Platform Engineering |
| **OCA subtrees** | Monthly, with staging regression | Subtree pull | Solution Architect |
| **Major platform upgrades** (Odoo 20, Next.js 16, PostgreSQL 17/18) | Wave-planned | §8 | Steering |

| # | Rule |
|---|---|
| **`LX-10`** | The monthly batch runs on a fixed calendar date so it is planned capacity, not an interruption. `GV-004`'s sprint model absorbs it as a standing item (`BE-008` `SPR-11`) |
| **`LX-11`** | An update that does not pass full CI is **not merged and not deferred silently**. It becomes a `BE-009` `DBT-` entry with an owner |
| **`LX-12`** | A dependency deferred for **three consecutive months** is escalated to the Chief Architect. Three deferrals is not a scheduling problem; it is an incompatibility nobody has diagnosed |

---

## 5. Vulnerability Response

### 5.1 Detection

| Layer | Tool class | Frequency |
|---|---|---|
| Language dependencies | SCA against OSV / GHSA / NVD | Every build **and** daily on `main` and `develop` |
| Container images | Image scanner | Every build and daily on published images |
| Odoo and OCA | Odoo security advisories; OCA repository watches | Continuous |
| L4 systems | Upstream advisory feeds per component | Continuous |
| Code | SAST | Every build (`FF-30`) |
| IaC | IaC scanner | Every build |

| # | Rule |
|---|---|
| **`LX-13`** | Scanning runs on a **schedule**, not only on commit. A vulnerability published on Tuesday must not wait for Friday's commit |
| **`LX-14`** | Findings are triaged against a **VEX** statement (§5.3). An untriaged backlog of scanner output is indistinguishable from no scanning |

### 5.2 Service levels

Severity is CVSS v3.1/v4.0 base **adjusted for exploitability and exposure in this estate** — a
critical CVE in a component with no reachable path is not a critical for this programme, and saying
so in a VEX document is the point of §5.3.

| Adjusted severity | Assess | Remediate or mitigate | Escalation |
|---|---|---|---|
| **Critical**, internet-reachable | 4 hours | **24 hours** | CTO immediately; `SV-003` incident |
| **Critical**, internal only | 1 working day | **5 working days** | Security Lead |
| **High**, internet-reachable | 1 working day | **7 days** | Security Lead |
| High, internal only | 3 working days | 30 days | Squad |
| Medium | 5 working days | Next monthly batch | Squad |
| Low | Recorded | Next major update | Squad |

| # | Rule |
|---|---|
| **`LX-15`** | **`FF-30` blocks a build on any open high or critical** (`DoD-15`). The service levels above govern how quickly the block is cleared, not whether it applies |
| **`LX-16`** | Where remediation is not available, a documented **mitigation** — network policy, feature flag, WAF rule — is applied and recorded with a review date |
| **`LX-17`** | Any critical affecting personal or residency-classified data is an incident under `SC-009` regardless of exploitability, because the statutory notification clock is not conditional on our assessment |

### 5.3 VEX

| # | Rule |
|---|---|
| **`LX-18`** | Every SBOM is accompanied by an **OpenVEX** document stating, per finding: `not_affected`, `affected`, `fixed` or `under_investigation`, with a justification |
| **`LX-19`** | `not_affected` requires a stated justification — component not present in the execution path, vulnerable configuration not enabled, inline mitigation applied. **"We looked and it seemed fine" is not one** |
| **`LX-20`** | VEX statements are versioned with the artefact and are re-evaluated at every wave gate |

---

## 6. Licences

### 6.1 The register as a file

TSS §7.3 places the licence register *"in M30, reviewed annually"*. M30 is unbuilt, so no register
exists. Until `cd_platform_ops` ships, and after it, the authoritative form is a file the build reads:

```yaml
# tooling/LICENCES.yaml — the licence position, checked on every build
policy:
  allow:  [MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, PostgreSQL, LGPL-3.0-or-later]
  gated:  [AGPL-3.0-only, AGPL-3.0-or-later, BSL-1.1, Elastic-2.0, SSPL-1.0, TSL, n8n-sustainable-use]
  deny:   [GPL-3.0-only, "NOASSERTION", "UNKNOWN"]     # GPL linked; deployed-only is gated

approvals:
  - component: metabase
    licence: AGPL-3.0-or-later
    obligation: "Source disclosure if modified and served over a network"
    position: "Deployed unmodified. Embedded via signed tokens only — see §6.3 test."
    fallback: "Apache Superset (TSS §7.4)"
    approved_by: Chief Architect
    approved_on: 2026-08-18
    review_at: every wave gate
  - component: n8n
    licence: n8n-sustainable-use
    obligation: "Internal business purposes only; not resold as a competing service"
    position: "Internal orchestration only. NOT exposed to marketplace sellers or brand partners."
    fallback: "Temporal / Apache Airflow"
    approved_by: Chief Architect + CFO
    approved_on: 2026-08-18
    review_at: every wave gate
  # … one entry per gated component
```

| # | Rule |
|---|---|
| **`LX-21`** | Every dependency, direct and transitive, resolves to an SPDX identifier in the `allow` list, or has an approval entry. `NOASSERTION` fails the build |
| **`LX-22`** | The register is checked **on every build**, not annually. TSS's annual cadence is retained as the **human review** of positions; the machine check is continuous |
| **`LX-23`** | Every gated entry carries a **named fallback**. TSS §7.4 supplies them; an entry without one is an unmanaged single point of dependency |
| **`LX-24`** | The attribution notice for every deployed component is generated from the register into `NOTICE.md` at build time |

### 6.2 The obligations, adopted from TSS §7.3

Not restated — adopted, with the mechanism for each named.

| Licence | Components | Obligation | Mechanism here |
|---|---|---|---|
| **AGPL-3** | Metabase, Grafana, MinIO, RustDesk, **Loki, Tempo** | Disclosure if **modified and served over a network** | `FF-03` blocks any `vendor/` diff; §6.3's test is answered per component in `LICENCES.yaml` |
| **LGPL-3** | Odoo, most OCA | Modifications to the library must be shared | `AS-05` + `FF-03` + `vendor/FORKS.yaml`. A registered fork is a **disclosure obligation**, and `REPO-11`'s upstream-PR field is how it is discharged |
| **Sustainable Use** | n8n | Internal business purposes only | §6.4 — a **usage** control, not a code control |
| **BSL** | Redpanda | Converts to Apache-2.0 four years after each merge; production use within limits | Wave-gate review; Kafka registered as fallback |
| **TSL** | TimescaleDB advanced features | Some features are commercially licensed | Apache-2.0 features only; CI check on feature use |
| **GPL-2** | Wazuh | Copyleft on distribution | Deployed, never distributed. §6.4 |
| Apache-2.0 / MIT / BSD | The remainder | Attribution | `NOTICE.md`, generated (`LX-24`) |

### 6.3 The AGPL-3 test, applied

AGPL-3's §13 obligation triggers on **modification** combined with **network service**. The estate
deploys six AGPL components and embeds one of them in a customer-facing surface, so the test is
answered explicitly rather than assumed.

| Question | Metabase | Grafana / Loki / Tempo | MinIO | RustDesk |
|---|---|---|---|---|
| Modified? | **No** — deployed as published | No | No | No |
| Served over a network to third parties? | **Yes** — embedded in P06, and via signed embed tokens in P03/P04/P07/P08 | Internal only | Internal only | Support sessions with clients |
| **Disclosure obligation?** | **No**, because unmodified | No | No | No |
| What would trigger it | Patching Metabase to change embedding, theming or authentication | Patching a dashboard renderer | Patching the server | Patching the client |
| Control | `FF-03` + `FORKS.yaml`; Chief Architect approval before any change | as left | as left | as left |

| # | Rule |
|---|---|
| **`LX-25`** | **Configuration, theming through supported extension points, and embedding are not modification.** Patching source is. The boundary is `vendor/` — anything requiring a diff there triggers the obligation |
| **`LX-26`** | Any proposed modification to an AGPL component requires Chief Architect approval **and** a published-source plan **before** the change is written |

> **The realistic trigger is Metabase.** `P06` embeds it in six portals with signed tokens, and the
> gap between "configure the embed" and "patch the embed to look right" is one frustrated afternoon.
> `FF-03` catching it is the difference between a styling change and an obligation to publish source.

### 6.4 Two obligations that no code check can see

| Obligation | Why a code check misses it | Control |
|---|---|---|
| **n8n Sustainable Use** — internal business purposes only | The breach is a **product decision**, not a commit. Exposing n8n workflow authoring to marketplace sellers or brand partners as a feature would breach it, with no code change to the component | `LX-27`: any proposal to expose an L4 component's own interface to an external party goes to the Chief Architect **and** CFO. `AR-002` records the portal surfaces this applies to |
| **Wazuh GPL-2** — copyleft on distribution | The breach is shipping the agent to a **client's** estate under M05 managed services, which is distribution | `LX-28`: the MSP agent-deployment design (`M05`, `CD-M05-*`) must state whether Wazuh is distributed to client endpoints. **If it is, the GPL-2 source obligation applies to the client, and this has not been assessed.** Raised as `BEA-15` |

> **`BEA-15` is a real exposure.** `M05` Remote Support & Managed Services runs monitoring on **client**
> estates, and TSS §7.3 records Wazuh's position as *"deployed, not distributed."* Installing an agent
> on a customer's Windows endpoint is, on the ordinary reading, distribution. It may be entirely
> compliant — GPL-2 permits distribution with source availability — but nobody has asked, and the
> answer changes what M05 must ship alongside the agent.

---

## 7. Currency Watch

### 7.1 MinIO — a Wave 1 component that has reached end of life

| Fact | Verified 2026-08-18 |
|---|---|
| Licence | Moved from Apache-2.0 to **AGPL-3** in 2021 |
| Community edition | Full admin console removed in **May 2025**, leaving a minimal object browser |
| Repository | Placed in maintenance mode **December 2025**; end-of-life language added **February 2026**; **formally archived 25 April 2026** |
| Position in this stack | **Wave 1 object storage** — `02-05` §4, TSS §7.1, TSS §20.2 W1 |
| Registered fallback in TSS §7.4 | *"Cloud-native object storage only"* was **assessed and rejected**; no open-source fallback is named |
| Recorded in the estate? | **No.** TSS was version-verified 13 August 2026 and lists MinIO as current |

**This is `TR-09` materialising on a foundation component**, and the annual review cadence TSS §7.3
prescribes would have found it somewhere between four and sixteen months late.

| Action | Owner | By |
|---|---|---|
| Raise as a `D-nnn` decision in `GV-003` and a Critical risk in `GV-005` | Chief Architect | **Immediately** |
| Assess options: a maintained community fork · **Garage** (AGPL-3, single binary, S3-compatible) · SeaweedFS · a cloud-native object store subject to the split-residency constraint (`A-01`) | Solution Architect | **W0 — blocking Wave 1** |
| Name a fallback in `LICENCES.yaml` and TSS §7.4 | Chief Architect | W0 |
| Re-run §7.3's watch across **every** L4 component before Wave 1 | Platform Engineering | **W0** |

Raised as **`BEA-16`, Critical**.

> **The choice is constrained, not free.** `A-01` assumes a Bangladesh-resident hosting option, and
> object storage holds evidence photographs, signed documents and Mushak invoices. A managed cloud
> object store may not satisfy `NFR-086`'s residency rule, which is why *"cloud-native object storage
> only"* was rejected in the first place. This must be decided by an architect against the residency
> constraint, not by a developer picking a drop-in replacement.

### 7.2 Odoo — the "LTS" claim

TSS §4.1 records Odoo 19.0's **Release class** as *"Long-Term Support (LTS)"*, verified 13 August
2026, and states support to approximately September 2028.

Verified against Odoo's own administration documentation on **2026-08-18**:

| Claim | Position |
|---|---|
| Released 18 September 2025 | **Confirmed** |
| Supported approximately three years, to ~September 2028 | **Confirmed** — Odoo provides standard support for all major versions for three years |
| **Release class "LTS"** | **Not established by the vendor.** Odoo's standard-and-extended-support documentation does not classify 19.0 as LTS; three-year standard support is the ordinary treatment of every major version |
| Extended support beyond three years | Available **for a fee**, and framed around the Enterprise subscription agreement. **A Community Edition deployment has no extended-support path** |

**Consequence.** TSS §25.2.1 already draws the right conclusion — *"a 36-month programme will reach
steady state within about a year of 19.0 leaving support"* — and recommends an upgrade slot between
W5 and W6 (`ADR-027`, `D-025`). This document adds only that the "LTS" label makes the position sound
safer than it is, and that for CE there is no paid extension to fall back on. Raised as **`BEA-13`**.

### 7.3 The watch itself

| # | Rule |
|---|---|
| **`LX-29`** | Every L4 system, every L3 module and both platform runtimes carry a **currency watch entry**: upstream release feed, licence page, end-of-life signal and the registered fallback |
| **`LX-30`** | The watch is checked **at every wave gate**, not annually, and the check is evidenced in the `GV-009` gate pack |
| **`LX-31`** | An upstream licence change, archival or end-of-life announcement is a **Critical `GV-005` risk within 5 working days** of publication, and a `GV-003` decision within 20 |
| **`LX-32`** | Every gated component has a **named, assessed fallback with an effort estimate**. *"There are alternatives"* is not a fallback |

> **The 2021–2026 relicensing pattern is the base rate, not the exception.** MongoDB, Redis, Elastic,
> HashiCorp, Grafana Labs, Timescale, Redpanda and now MinIO have all changed licence or lifecycle
> posture inside the window this programme spans. **A 36-month programme on a 24-system open-source
> stack should expect two to four such events.** `LX-29`…`LX-32` exist so the next one is found in
> days rather than at the wave gate that depends on it.

---

## 8. SBOM

### 8.1 What it is for

Four consumers, each needing something different, which is why two formats are produced.

| Consumer | Need | Format |
|---|---|---|
| Vulnerability response (§5) | Precise component inventory to answer *"are we affected?"* in minutes | CycloneDX 1.7 + VEX |
| Licence compliance (§6) | Every licence in the tree including transitive | CycloneDX 1.7 |
| **Corporate clients and brand partners** | Supply-chain evidence in their own procurement process | **SPDX 3.0.1** |
| Wave-gate assurance (`GV-009`) | Evidence that what was assessed is what was deployed | Both, attested |

### 8.2 Generation

| # | Rule |
|---|---|
| **`LX-33`** | The SBOM is generated **at build time from the built artefact**, never from a manifest. A manifest states intent; the artefact is what ships |
| **`LX-34`** | **CycloneDX 1.7** is the primary format. **SPDX 3.0.1** is produced from the same build for external exchange |
| **`LX-35`** | An SBOM is produced per **artefact** (container image, application bundle) and aggregated per **release tag** |
| **`LX-36`** | The SBOM covers all five ecosystems **plus** the vendored estate — Odoo core at its pinned commit and all eighteen OCA subtrees. A vendored dependency omitted from the SBOM is the one that will be asked about |
| **`LX-37`** | SBOMs are **signed and retained for the life of the release plus seven years**, matching the financial-record retention the ERP itself is subject to |
| **`LX-38`** | The SBOM is attached to the release tag (`GW-35`) and is part of the `GV-009` gate pack |

### 8.3 Why both formats

CycloneDX 1.7 was published in October 2025 and adopted as ECMA-424, 2nd edition in December 2025; it
is the last release of the 1.x line and remains backward-compatible with 1.4–1.6. It is the better
build-integration format and carries the cryptography and provenance detail §9 needs. SPDX 3.0.1 is
what large corporate procurement functions ask for by name. Producing both from one build costs a
pipeline step; producing the wrong one costs a customer conversation at the worst moment.

---

## 9. Supply-Chain Integrity

### 9.1 SSDF mapping

| SSDF practice | How it is met |
|---|---|
| **PW.4** — reuse existing, well-secured software | §3's admission procedure and maintenance test |
| **PS.1** — protect all forms of code from unauthorised access | `BE-003` §3.3 branch protection, signed commits, no administrator bypass |
| **PS.2** — provide a mechanism to verify integrity | §9.2 provenance attestation; `LX-37` signed SBOMs |
| **PS.3** — archive and protect each release | `LX-37` retention; immutable tags (`GW-36`) |
| **PW.7 / PW.8** — review and test code | `BE-003` §6; `BE-006` §5 |
| **RV.1** — identify vulnerabilities on an ongoing basis | §5.1 scheduled scanning |
| **RV.2** — assess, prioritise and remediate | §5.2 service levels; §5.3 VEX |
| **RV.3** — analyse root causes | `BE-009` `DBT-11`; post-incident review (`BE-003` §9 step 8) |

### 9.2 SLSA

| Level | Requirement | Position |
|---|---|---|
| Build L1 | Provenance exists | **W1** — the CI pipeline emits provenance for every artefact |
| **Build L2** | Signed provenance from a hosted build service | **Target: W1 gate** |
| **Build L3** | Hardened, non-falsifiable builds; isolated build environment | **Target: W3 gate** |

| # | Rule |
|---|---|
| **`LX-39`** | Every artefact carries provenance naming the source commit, the build, the inputs and a digest of the output |
| **`LX-40`** | Deployment verifies provenance. An artefact with no verifiable provenance does not reach `staging` or `prod` |

**Why not Level 3 in Wave 1.** Level 3 requires build isolation and non-falsifiable provenance, which
means hardened, ephemeral runners and a key-management posture that `PE-006` builds. Wave 1 already
carries fifteen infrastructure components and `GV-004` rates it infeasible at 5.33×. Claiming L3 in
W1 would produce a claim rather than a control.

### 9.3 Regulatory applicability

Stated including what does **not** apply, so that nobody later assumes it did.

| Regime | Applies? | Reasoning |
|---|---|---|
| **EU Cyber Resilience Act** | **No** | The CRA binds products with digital elements **placed on the EU market**. The ERP and its portals serve 1000FiX's Bangladesh operations, its customers and its partners; nothing is placed on the EU market. **Reassess if an EU-facing product or an EU client estate is ever in scope** — the vulnerability-reporting obligations commenced 11 September 2026 and the SBOM-in-technical-documentation obligation applies from 11 December 2027 |
| **Bangladesh PDPA 2026** | **Yes** | Not an SBOM regime, but §5's response times and §6's residency-adjacent controls feed `SC-002` and `SC-009`. `LX-17` exists for this reason |
| **NIST SSDF / US federal attestation** | **Indirectly** | Not binding on 1000FiX, but corporate clients increasingly ask for the posture in procurement. §9.1 answers it |
| **ISO/IEC 27001** | **Yes**, via M23 | A.8.30 and A.8.31 supplier and development controls; this document is part of the evidence |

> **The CRA row is here because it is the kind of thing that gets assumed either way.** Building CRA
> conformance the ERP does not need would be waste; discovering in 2028 that an EU brand partner's
> portal integration brought it into scope would be worse. The trigger condition is written down.

---

## 10. Decisions Recorded

| # | Decision | Options considered | Chosen | Rationale | Consequence |
|---|---|---|---|---|---|
| `BE-007-D-01` | SBOM format | (a) CycloneDX only; (b) SPDX only; (c) **both** | **(c)** | CycloneDX integrates with the build; SPDX is what corporate procurement asks for by name | One extra pipeline step |
| `BE-007-D-02` | Licence register location | (a) M30, per TSS §7.3; (b) **`tooling/LICENCES.yaml`, checked on every build** | **(b)** | M30 is unbuilt, so the register does not exist. A build-checked file works from day one and survives M30's arrival | Two registers exist once M30 ships; `Q-03` resolves |
| `BE-007-D-03` | Review cadence | (a) Annual, per TSS §7.3; (b) **continuous machine check + wave-gate human review** | **(b)** | §7.1 shows an annual cadence missing an end-of-life event by up to sixteen months | Gate packs carry a currency section |
| `BE-007-D-04` | Version ranges | (a) Permit caret ranges; (b) **exact pins everywhere** | **(b)** | Reproducibility across six environments and 36 months; a range delegates a decision to an upstream maintainer | Monthly batch updates become mandatory, not optional |
| `BE-007-D-05` | SLSA target | (a) L3 in W1; (b) **L2 by W1 gate, L3 by W3 gate** | **(b)** | L3 needs hardened ephemeral runners that `PE-006` has not built, in the wave `GV-004` rates infeasible | The gap is stated rather than claimed away |
| `BE-007-D-06` | Vulnerability triage | (a) Raw CVSS; (b) **CVSS adjusted for exposure, with VEX** | **(b)** | At this dependency count raw scanner output is unactionable, and an unactionable backlog is ignored | VEX justifications must be written, and `LX-19` forbids the empty one |

---

## 11. Open Questions

| # | Question | Owner | Needed by | Blocks |
|---|---|---|---|---|
| `Q-01` | **What replaces MinIO** (`BEA-16`), given the residency constraint on evidence and statutory documents? | Chief Architect | **W0 — blocking Wave 1** | Object storage in every wave |
| `Q-02` | Is Wazuh **distributed** to client endpoints under M05, and if so what discharges GPL-2 (`BEA-15`)? | Chief Architect / Legal | **W5, assess by W1** | M05 agent design |
| `Q-03` | When M30 `cd_platform_ops` ships, does it consume `LICENCES.yaml` or replace it? | Solution Architect | W1 | Two registers otherwise |
| `Q-04` | Who owns the currency watch operationally — Platform Engineering or the Architecture function? | CTO | **W0** | `LX-29`…`LX-32` |
| `Q-05` | Does the implementation vendor's own toolchain enter our SBOM, and who attests it? | Procurement / Security Lead | W1 | SBOM completeness; `LX-36` |
| `Q-06` | Are corporate-client contracts already committing us to an SBOM or a vulnerability-notification service level? | Legal / `CO-003` | W1 | §5.2, §8.1 |

---

## 12. Acceptance Criteria for This Document

| # | Criterion | Evidence |
|---|---|---|
| `AC-01` | Every ecosystem has a stated pinning mechanism and lockfile | §4.1, five ecosystems plus vendored code |
| `AC-02` | Every licence class has an approval route and a named approver | §3.3 |
| `AC-03` | The licence register exists as a build-checked file, not as a future module | §6.1, `LX-22` |
| `AC-04` | The AGPL test is answered per component, not stated in general | §6.3 |
| `AC-05` | Vulnerability response has service levels by adjusted severity | §5.2 |
| `AC-06` | SBOM format, generation point, retention and consumers are all stated | §8 |
| `AC-07` | Currency watch is continuous and produces gate evidence | §7.3, `LX-30` |
| `AC-08` | Regulatory applicability includes what does not apply, with the trigger to reassess | §9.3 |
| `AC-09` | Every version and licence claim carries a verification date | Front matter, §7, §13 |

**Definition of done.** Complete when every criterion is met, `LICENCES.yaml` is committed and
failing the build on an unapproved licence, the first SBOM is attached to a release tag, `BEA-16` has
a decision, `PGD-000`'s `BE-007` row moves from ◐ to ✅ with a fresh timestamped enumeration, and the
approver has signed.

---

## 13. Traceability

| Direction | Artefact | Relationship |
|---|---|---|
| Upstream | `02-05` §4 | The original licence analysis; corrected by `BEA-14` |
| Upstream | TSS §7.3, §7.4, §18.5, §25.2 | Obligations, fallbacks, cadence, version currency |
| Upstream | `BE-004` §5 | `vendor/`, submodule and subtree pins this document versions |
| Downstream | `BE-001` | `versions.lock` supplies every pin `make doctor` checks |
| Downstream | `BE-006` | Components contribute to the SBOM; §5 criterion 17 |
| Downstream | `PE-004`, `PE-007` | Scanning, SBOM generation, provenance attestation |
| Downstream | `SC-005`, `SC-009` | Security review and incident routes |
| Downstream | `GV-005` | `LX-31` raises risks; `BEA-16` is one |
| Downstream | `GV-009` | Currency and SBOM evidence in the gate pack |
| Lateral | `CO-004` | Commercial licence register for L6 components |
| Lateral | `AR-013` | Technology radar; a fallback becoming primary is a radar movement |

---

## 14. References

**Within this repository**
`../PGD-000_Master_Register_of_Project_Guiding_Documents.md` ·
[`_CATEGORY_OVERVIEW.md`](_CATEGORY_OVERVIEW.md) ·
[`BE-001`](BE-001_Development_Environment_Setup_Guide.md) ·
[`BE-004`](BE-004_Repository_and_Monorepo_Structure_Standard.md) ·
[`BE-006`](BE-006_Component_Build_Specification_Standard.md) ·
[`BE-009`](BE-009_Technical_Debt_Register_and_Refactoring_Policy.md) ·
`../02_Architecture_and_Design/AR-012_Architecture_Compliance_and_Fitness_Function_Standard.md` ·
`../02_Architecture_and_Design/AR-013_Technology_Radar_and_Build_vs_Buy_Register.md`

**Workspace**
`../../1000fix_ERP_Module/02_Architecture/02-05_Technology_Stack_and_Build_vs_Buy.md` §3, §4 ·
`../../primary-doc/1000FiX_ERP_Technology_Stack_Specification.md` §4.1, §7.1, §7.3, §7.4, §18.5, §20.2, §25.2

**External standards and sources** *(all verified 2026-08-18)*
CycloneDX 1.7 — released October 2025, adopted as **ECMA-424, 2nd edition** December 2025; final 1.x
release; backward-compatible with 1.4–1.6 ·
SPDX 3.0.1 — the current 3.0-line release ·
OpenVEX · SPDX Licence List ·
NIST SP 800-218 *Secure Software Development Framework v1.1* — PO, PS, PW, RV practice groups ·
SLSA build levels 1–3 ·
**Odoo 19.0 standard and extended support documentation** — three-year standard support for major
versions; **no "LTS" classification**; extended support is a paid Enterprise offering ·
**MinIO** — Apache-2.0 → AGPL-3 (2021); admin console removed from the community edition May 2025;
maintenance mode December 2025; **repository archived 25 April 2026** ·
Grafana Labs relicensing — Grafana, Loki and Tempo moved from Apache-2.0 to **AGPLv3** in April 2021 ·
n8n Sustainable Use Licence — fair-code, internal business use ·
EU Cyber Resilience Act — vulnerability-reporting obligations from **11 September 2026**;
SBOM in technical documentation from **11 December 2027**; applies to products placed on the EU market

---

## 15. Revision History

| Version | Date | Author | Change | Approver |
|---|---|---|---|---|
| 1.0 | 2026-08-18 | Enterprise Architecture | Initial issue. Admission gate, five-ecosystem pinning, update cadence, vulnerability service levels with VEX, the licence register as a build-checked file, the AGPL test applied per component, currency watch, dual-format SBOM, SSDF and SLSA position, regulatory applicability. Raises `BEA-13`, `BEA-14`, `BEA-15`, `BEA-16` | *(unsigned — no constituted body, `PGD-A1-09`)* |

---

*`BE-007` · Category 07 · 1000FiX ERP System v2.0 · CONFIDENTIAL*
