# W0-05 — `1000fix-portal-platform` migration plan (Next.js 15 → 16.3 / Payload 3.73+)

**Task `P01-M02-T05`** · Prepared 2026-10-01 · Owner (platform migration):
`CON-03` platform team lead — **the ERP programme does not own this
migration; it is blocked by it** (roadmap wording). ERP-side owner (unblock
tracking): Frontend lead (`FE`).

| | |
|---|---|
| **Baseline decision** | `D-026` — Next.js 16.2+ (16.3 line) with Payload 3.73+ |
| **Hard deadline** | **Before Wave 1 portal sprints**, and upstream: **Next.js 15 EOL is 21 October 2026** — no security patches after that date |
| **Status at preparation** | Not started (`CON-03` team to confirm the plan within 5 working days of programme day 1) |

## 1. Why this is a plan, not an assessment

The external verification (IR-002 §0.7.2) closed the question: there is
exactly one supported target and the current platform is permanently excluded
from CMS support on it (Payload: Next.js 15.5–16.1.x "is not supported and
will not be supported in the future"). Any `W0-05` output other than a dated
migration plan is a defect.

## 2. Migration phases (platform team; ERP gate dates attached)

| Phase | Work | Exit |
|---|---|---|
| **0 — Inventory** (week 1) | Dependency audit against Next 16 breaking changes; Payload plugins/fields inventory vs 3.73; Node runtime floor check (**≥ 20.9 required by Payload 3.73; Node 20 itself is past EOL since 30 Apr 2026 — see `D-026` §2.3 and the Node finding in the 2026-10-01 verification record: plan lands on **Node 22 LTS** directly) | Dependency matrix with go/no-go per package |
| **1 — Branch & upgrade** (weeks 2–3) | `next` 15 → 16.3.x; `payload` → ≥ 3.73; Turbopack build/HMR on; Codex/eslint configs | Build green on 16.3; visual-regression suite on the 20 top pages |
| **2 — CMS surface** (weeks 3–4) | Payload 3.x migration notes; admin panel UAT; RichText/media storage against the new object store (`D-028` Ceph) | Content team UAT sign-off |
| **3 — Soak & cutover** (week 5) | Staging soak ≥ 5 days incl. a Bengali-content rendering pass (TR-07 shaping on both engines); cutover window with instant rollback | Production on 16.3; `CON-03` contract note updated |
| **4 — Contract re-baseline** | The `IN-002` portal contract version pinned for ERP integration assumes 16.3 semantics — re-issue the contract on cutover | `IN-002` vNext signed |

## 3. ERP-side integration gates (what the ERP programme watches)

- **G0a (G0b at latest):** Phase 0 inventory exists. If not, escalate to
  Steering as a Wave-1 blocker (`B-07` reopened).
- **Before first portal sprint:** Phases 1–3 complete. The six ERP portals
  (`P01`, `P04`, `P07`, `P08`, `P10`, `P12`) **target 16.3/3.73+ from their
  first commit regardless** — they do not wait for the platform.
- **Rollback rule:** if cutover slips past the ERP's first portal sprint, the
  ERP portals proceed on 16.3 in their own deployments; the platform
  migration continues independently. No ERP code is ever written on Next 15.

## 4. Risks (named, with owners)

| Risk | Owner | Mitigation |
|---|---|---|
| Next 15 EOL (21 Oct 2026) arrives mid-migration — no security patches on the old line | Platform lead | Phase 1 lands before that date; interim: accept a documented exposure window or hold releases |
| Payload plugin incompatibility on 3.73 | Platform lead | Inventory (Phase 0) is the gate; blocked plugins get 10 days' effort cap, then replacement |
| Bengali content rendering differences under Turbopack | Platform + ERP `FE` | Soak phase includes the TR-07 two-engine conjunct check |

## 5. Verification of this plan

This plan satisfies `P01-M02-T05`'s verify column ("migration plan with an
owner and a date"). The owner is named above; the dates are relative to
programme day 1 because the `CON-03` team's calendar is not the ERP's to
commit — the plan is handed over at day 1 with the gate dates attached.
