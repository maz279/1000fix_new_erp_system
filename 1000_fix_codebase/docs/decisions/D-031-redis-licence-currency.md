# D-031 — Redis licence currency: pin 7.2.x (BSD-3) or adopt Valkey

| | |
|---|---|
| **Decision ID** | `D-031` |
| **Date** | 2026-10-01 |
| **Status** | **PROPOSED** — awaiting ARB ratification (registered by the first `P01-M02-T10` version-currency verification) |
| **Deciders** | Chief Architect (`CA`) proposes; ARB ratifies |
| **Allocating authority** (`DL-08`) | `GV-002`; the finding is a direct application of the `D-030` rule to TSS TC-012 |
| **Blocks** | `P02-M05-T02` (`core` profile definition) and every Redis image pin |
| **Raise under** | `GV-003`; `RG-08` (the TSS licence column carries no timestamp — that is how it went stale) |

## 1. Finding (verified against upstream 2026-10-01)

| Redis line | Licence | Source |
|---|---|---|
| ≤ 7.2 | BSD-3-Clause (permissive) | redis.io licensing history |
| 7.4+ (Mar 2024 onward) | **RSALv2 + SSPLv1** — source-available; SSPL requires open-sourcing the entire service stack if offered as a managed service | redis.io/legal/licenses; Redis dual-licensing announcement |
| 8.0+ (May 2025 onward) | Tri-licence RSALv2 / SSPL / **AGPLv3** | redis.io/blog/agplv3 |
| **Valkey** (Linux Foundation fork of Redis 7.2.4, Apr 2024) | **BSD-3** | Linux Foundation announcement |

**TSS TC-012 declares "Redis 7.x, BSD-3"** — true only for 7.2.x and earlier.
Any 7.4+ pin makes the TSS licence column factually wrong; a Redis 8 pin on
AGPLv3 falls under the `D-030` approval rule; RSAL/SSPL are "fair-code-class"
source-available licences the same rule catches. **The estate's stated "BSD-3"
position is only achievable on 7.2.x or Valkey.**

## 2. Options

| Option | Assessment |
|---|---|
| **A — pin Redis 7.2.x (last BSD line)** | Zero functional change vs the estate design; misses 7.4+ features (none of which the design names); support: 7.2 is past upstream EOL for community releases — flag for evaluation |
| **B — adopt Valkey (BSD-3)** | Licence-clean at the current line; wire-protocol and command compatible with the 7.2 base; Linux Foundation governance; used as the default by major clouds |
| C — Redis 8 on AGPLv3 with `D-030` approval | Keeps upstream Redis; adds an AGPL component to the estate and an approval row — against the direction of every replacement taken in `D-030` |

**Recommendation: Option B (Valkey)**, with Option A as the fallback if the
ARB weighs ecosystem familiarity over licence cleanliness. Option C is
recommended against.

## 3. Interim ruling (until the ARB ratifies)

**No Redis 7.4+ or 8.x image may be pinned anywhere** (versions.lock, Compose
profiles, CI). The `core` profile (`P02-M05-T02`) holds until this decision is
taken — it is a Phase-2 task and the ARB sits before Phase 2 starts.

## 4. Consequences (of the recommended option)

- TSS TC-012 corrected: Redis → Valkey, BSD-3, current line (`CR-P01M02-02` raised by
  the traceability record).
- `DE-06`: Valkey image pinned by digest; `D-030` register adds Valkey at
  BSD-3 (no approval condition).
- Redis Streams (the W1–W5 event bus) is command-compatible on the 7.2 base;
  the W6 Kafka migration (`D-030` row 4) is unaffected either way.

## 5. Revisit triggers

- Valkey/Redis divergence affecting the Streams command set used by the event
  bus → re-open before W2.
- Redis relicensing back to BSD → re-run the option table.
