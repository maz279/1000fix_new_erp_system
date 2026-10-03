# D-028 — Object store: Ceph Object Storage (replacing MinIO)

| | |
|---|---|
| **Decision ID** | `D-028` |
| **Date** | 2026-10-01 (decision taken in Phase 1 per IR-002 §0.7.3; this ADR records it, `P01-M02-T10`) |
| **Status** | ACCEPTED |
| **Deciders** | Chief Architect (`CA`) on the authority of the ARB |
| **Allocating authority** (`DL-08`) | `GV-002`; surfaced by the external verification of 2026-08-19 (`IRB-01`, Appendix I of IR-002); recorded in `AR-004`, cross-referenced from `GV-003` |
| **Closes** | `B-19` (object store archived / unpinnable) |
| **Raise under** | `GV-003`; `IR-06` |

## 1. Context

`minio/minio` was archived on **25 April 2026** ("THIS REPOSITORY IS NO
LONGER MAINTAINED"); the community edition is source-only with no pre-compiled
binaries, the admin console was removed from community in March 2025, and the
vendor directs distributed use to the commercial AIStor editions. TSS §21.3
requires **erasure coding across nodes** at 20 TB growing toward 50 TB,
holding evidence packs, service reports, custody photographs and identity
documents from Wave 1 — the distributed edition is exactly what went
commercial.

## 2. Options evaluated (discriminator: erasure coding, per TSS §21.3)

| Candidate | Licence | Erasure coding | Assessment |
|---|---|:--:|---|
| Garage | AGPL-3 | Yes | Lightweight, geo-distributed; closest match to `NFR-086` topology — but AGPL-3 falls under the `D-030` approval class |
| **Ceph RADOS Gateway** | **LGPL-2.1/3** | **Yes** | Full-featured, heaviest to operate; justified by erasure coding + split-residency compatibility + permissive licence |
| SeaweedFS | Apache-2.0 | No — replication | Fails the erasure-coding requirement **as written** |
| RustFS | Apache-2.0 | Yes | Closest to the MinIO developer experience; youngest of the four — insufficient operational track record for Wave-1 evidence storage |

**Version currency (verified 2026-10-01):** Ceph **Squid (v19.2.x)** is the
current stable series (v19.2.6 at verification), LGPL-2.1/3 — the selection
remains valid; pin by digest (`DE-06`) when `P02-M05-T02` defines the `core`
profile.

## 3. Decision

1. **Ceph Object Storage (RADOS Gateway)** replaces MinIO as the estate object
   store (Wave 1, `core` and `full` Compose profiles; production deployment
   erasure-coded per TSS §21.3).
2. `minio/minio` images are **never pinned** — archived upstream; `P02-M05-T02`
   pins the Ceph image by digest.
3. Migration of any existing MinIO-held objects is a Wave 1 runbook task (the
   staging estate has none at decision time).

## 4. Consequences

- Operational weight: Ceph is the heaviest candidate; the `core` profile runs
  a single-node RGW for local development, production runs the erasure-coded
  cluster — the profiles differ, and that is accepted.
- `D-030` register carries Ceph at LGPL-2.1/3 (permissive — no approval
  condition beyond the register's annual review).
- RustFS is the named fallback if Ceph's operational cost proves unsustainable
  before Wave 2 — revisit trigger below.

## 5. Revisit triggers

- Ceph RGW operational burden exceeding 0.5 FTE sustained for a quarter →
  re-run the four-candidate table with RustFS's maturity re-assessed.
- Ceph licence change (upstream) → immediate `D-030` annual-review escalation.
