# D-030 — Restricted-licence register (annual review)

| | |
|---|---|
| **Decision ID** | `D-030` |
| **Date** | 2026-10-01 (register created by the 2026-08-19 external verification; this ADR records it and completes the enumeration, `P01-M02-T10`) |
| **Status** | ACCEPTED — **a register with an annual review, not a one-off sign-off** |
| **Deciders** | Chief Architect (`CA`) on the authority of the ARB; Security Lead (`SL`) co-signs the classification gate design |
| **Allocating authority** (`DL-08`) | `GV-002`; rule source: TSS §18.5 and `BE-007` — *"AGPL, BSL, TSL and fair-code components require architecture approval"*; recorded in `AR-004`, cross-referenced from `GV-003` |
| **Closes** | `B-22` (restricted licences unapproved) |
| **Gate implementation** | `P02-M08-T04` (gitleaks + licence classification across all L4 systems) |

## 1. Rule

No component licensed AGPL-3, BSL, TSL or fair-code (Sustainable Use Licence
class) enters the estate without an entry in this register and ARB approval.
**Approval is recorded per component, with the use case that makes the licence
safe** — the estate's own failure mode (IRB-06) was components safe for
today's architecture and unsafe for the marketplace + MSP business the
programme is building.

## 2. Register (complete enumeration, verified 2026-10-01)

### 2.1 The four original findings — all replaced

| Original | Licence | Replacement | Licence | Wave | Resolution |
|---|---|---|---|:--:|---|
| MinIO | AGPL-3 | **Ceph Object Storage** (`D-028`) | LGPL-2.1/3 | W1 | Archived upstream 25 Apr 2026; replaced |
| Metabase OSS | AGPL-3 | **Apache Superset** | Apache-2.0 | W4 | AGPL network-use clause eliminated; `P06` embeds Superset without source-provision duties |
| n8n | Sustainable Use License | **Apache Airflow** | Apache-2.0 | W1 | Fair-code restriction on external-user value eliminated. **Condition:** Airflow serves orchestration only; if the `INT-047` business-process automation gap proves material, a separate ADR decides the automation engine — it does not silently revert to n8n |
| Redpanda | BSL | **Apache Kafka** | Apache-2.0 | W6 | BSL third-party-streaming restriction eliminated; Kafka was already the declared alternative |

### 2.2 Restricted-licence components that REMAIN in the stack — approved with conditions

*The roadmap's §0.7.3 table stops at the four replacements; TSS §18.5's rule
reaches further. The L4 register still names AGPL components, and the rule
requires them to be approved, not ignored. This section is that approval.*

| Component (TC) | Licence | Use case that makes it safe (the approval basis) | Condition |
|---|---|---|---|
| **Grafana** (TC-024) | AGPL-3 | Internal operational monitoring only; dashboards are not exposed to external users as a service | No Grafana-hosted multi-tenant offering; `P06` real-time board is internal-staff-facing |
| **Loki** (TC-027) | AGPL-3 | Log aggregation behind the trust boundary | Logs may contain client identifiers — never offered as a log service to third parties |
| **Tempo** (TC-028) | AGPL-3 | Trace storage, internal | Same class as Loki |
| **MeshCentral / RustDesk** (TC-031) | Apache-2.0 / **AGPL-3** | Attended/unattended remote support to `M05` MSP clients | AGPL half applies only if MeshCentral is the chosen arm; RustDesk (AGPL) self-hosted for client endpoints — **approval conditional on the Wave-5 pilot picking the Apache-2.0 arm (MeshCentral) wherever the choice is neutral** |
| **TimescaleDB** (TC-023) | Apache-2.0 / **TSL** (community features) | Time-series for telemetry/GPS | **Condition already in the TSS: Apache-2.0-licensed features only** — the TSL-licensed features must never be enabled; the licence gate tests for this |
| **HashiCorp Vault** (TC-039, registered 2026-10-01) | **BUSL 1.1** (since 2023) | Secrets management (`NFR-062`, `IP-07`) — the TSS names "Vault *(or OpenBao)*" | **Prefer OpenBao (MPL-2.0 Linux Foundation fork)** — BSL-class licence avoided entirely; HashiCorp Vault itself needs an explicit register row + ARB approval if ever chosen. The Wave 1 pick is recorded here: **OpenBao** |

### 2.3 New finding raised at this verification (2026-10-01) — see `D-031`

**Redis**: TSS TC-012 declares "Redis 7.x, BSD-3". Upstream reality: Redis
≤ 7.2 is BSD-3; **7.4+ is RSALv2/SSPL (source-available, not BSD)**; Redis 8
adds AGPLv3 to a tri-licence. The TSS licence column is therefore wrong for
any 7.4+ pin, and Redis 8's AGPLv3 option would fall under this register's
approval rule. **Disposition: PROPOSED `D-031`** — pin Redis 7.2.x (last
BSD-3 line) or adopt Valkey (Linux Foundation BSD-3 fork). Until `D-031` is
taken, **no Redis 7.4+ or 8.x image may be pinned**.

## 3. Annual review (and gate cadence)

- The register is re-verified by the **version-currency ritual**
  (`tooling/version-currency/verify-version-currency.ps1`) at every wave gate
  and formally reviewed annually (`GV-003` calendar).
- The `P02-M08-T04` licence classification gate reads this register as data —
  a new dependency whose licence matches the rule classes fails CI until a
  register row exists.
- Every new L4/L6 component enters the register at adoption time, not at the
  annual review.

## 4. Revisit triggers

- Upstream licence change on any registered component (e.g. Grafana relicensing,
  Redis path changes) → out-of-cycle review.
- The `M05` MSP business model adding a client-facing analytics or streaming
  offering → re-run the IRB-06 pattern analysis against the register.
