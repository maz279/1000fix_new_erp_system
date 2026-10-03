# D-026 — Portal frontend baseline: Next.js 16.2+ with Payload CMS 3.73+

| | |
|---|---|
| **Decision ID** | `D-026` |
| **Date** | 2026-10-01 |
| **Status** | ACCEPTED (there is only one supported target — this records it, it does not choose it) |
| **Deciders** | Chief Architect (`CA`) on the authority of the ARB |
| **Allocating authority** (`DL-08`) | `GV-002`; upstream facts verified by the `P01-M02-T10` version-currency ritual; recorded in `AR-004`, cross-referenced from `GV-003` (`P01-M02-T09`) |
| **Closes** | `B-07` (portal platform version currency) |
| **Raise under** | `GV-003`; `AR-013` §4 `VC-01` |

## 1. Context — externally verified facts

Re-verified against upstream on **2026-10-01** (first record of the
`P01-M02-T10` ritual; sources in `tooling/version-currency/evidence/`):

| Fact | Source (checked 2026-10-01) |
|---|---|
| **Next.js 15 reaches end of life 21 October 2026** — released 21 Oct 2024, two-year Maintenance LTS | nextjs.org/support-policy; endoflife.date/nextjs |
| Next.js 16 released **21 October 2025**; current patch line **16.3.x** (16.3.6 at verification) — Active LTS ≈ 3 years | nextjs.org/support-policy |
| **Payload CMS gained full Next.js 16 support in 3.73.0 (23 January 2026)**, including Turbopack HMR and build | Payload 3.73 release notes; payloadcms.com/docs/installation |
| **Payload states Next.js 15.5–16.1.x "is not supported and will not be supported in the future"** — a permanent exclusion | Payload installation docs |
| Payload requires **Node.js ≥ 20.9** on the 3.73 line | payloadcms.com/docs/installation |

The existing `1000fix-portal-platform` (`CON-03`) sits on Next.js 15 +
Payload 3 — simultaneously reaching EOL (in 20 days from this record) and
permanently excluded from CMS support. **`B-07` is not a decision awaiting a
meeting; it is a migration that is already overdue.**

## 2. Decision

1. **Baseline: Next.js 16.2+ (target the 16.3 patch line) with Payload CMS
   3.73+** for all six ERP portals (`P01`, `P04`, `P07`, `P08`, `P10`, `P12`)
   **from their first commit**.
2. The `1000fix-portal-platform` migration from Next.js 15 is **mandatory and
   must complete before Wave 1** — per the roadmap verify column, recorded
   here explicitly: **migration owner = the `CON-03` platform team lead**
   (the ERP programme is blocked-by, not owner-of); **date = phases 0–3 of the
   [`W0-05` migration plan](../p01-m02/W0-05-portal-migration-plan.md),
   completed within 5 weeks of programme day 1 and in no case beyond the
   Wave-1 portal sprint start**; hard external deadline: **Next.js 15 EOL,
   21 October 2026**.
3. Node.js floor for portal work moves with Payload's requirement
   (**≥ 20.9 on the 3.73 line**) — see `D-031` context for the Node-20 EOL
   finding that forces the toolchain to Node 22.

## 3. Consequences

- No ERP portal code may be written against Next.js 15 or Payload < 3.73;
  CI pins the floors in `package.json` engines and the lockfile.
- The platform migration (`W0-05`) is tracked as a RAID item with a named
  owner and a date before Wave 1's first portal sprint.
- The version-currency ritual (`P01-M02-T10`) re-checks the Next.js support
  policy at every wave gate — the 21 Oct 2026 EOL date is inside Wave 0/1.

## 4. Revisit triggers

- Payload 4.0 reaching stable (canary observed at verification time) — a
  separate ADR decides whether the portals' first release ships 3.73 LTS or 4.x.
- Next.js 17 announcement — re-baseline within one gate, per the ritual.
