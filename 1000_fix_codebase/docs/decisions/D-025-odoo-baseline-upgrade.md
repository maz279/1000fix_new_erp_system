# D-025 — Odoo baseline and in-flight upgrade slot

| | |
|---|---|
| **Decision ID** | `D-025` |
| **Date** | 2026-10-01 |
| **Status** | ACCEPTED |
| **Deciders** | Chief Architect (`CA`) on the authority of the Architecture Review Board (constituted `P01-M01-T04`) |
| **Allocating authority** (`DL-08`) | `GV-002` RACI: architecture baselines are allocated by the ARB to the `CA`; recorded in `AR-004` and cross-referenced from the `GV-003` decision log (`P01-M02-T09`) |
| **Closes** | `B-08` (Odoo upgrade unplanned) |
| **Raise under** | `GV-003` change control; `IR-06` (no technology enters the stack without an ADR and a `D-nnn` row) |

## 1. Context

A 36-month programme on an annually-versioned platform must plan an in-flight
major upgrade; discovering the slot later is not a plan (roadmap `P01-M02-T06`).
The TSS (`§4.4`, `D-15`) raises the same question and defers it here.

**Version-currency verification, 2026-10-01** (first record of the `P01-M02-T10`
ritual, sources in `tooling/version-currency/evidence/`):

| Fact | Source |
|---|---|
| Odoo 19.0 released September 2025 | Odoo release history |
| **Odoo Experience 2026, Brussels Expo: 24–26 September 2026** — the event at which Odoo 20 debuts — has **now taken place**; Odoo 20 is the current major | odoo.com/event/odoo-experience-2026 |
| Odoo standard support ≈ 3 years + 1 year extended → **Odoo 19 supported to ~September 2028** | Odoo 19.0 documentation, *Standard and extended support* |

Wave 6 of the delivery plan falls at months 23–26 of a Q4-2026 kickoff —
i.e. **September–December 2028, exactly when Odoo 19 standard support ends**.

## 2. Options considered

| Option | Shape | Assessment |
|---|---|---|
| **A — baseline 19.0, upgrade slot in W6** | Build 36 months on 19.0; upgrade to Odoo 20 in the W6 slot (`P09-M02`) | The upgrade window coincides with 19.0's support cliff; the slot already carries the fork audit and OCA v20 assessment (`P09-M02-T02/T03`) |
| B — baseline 20.0 from day one | Start on the just-released major | Rejected: zero OCA v20 availability at kickoff (18 subtrees must migrate first); Wave 1 would carry an ecosystem migration nobody has validated |
| C — defer the decision | "Decide later" | Rejected: `P09-M02` cannot be planned against an unnamed window, and deferral is itself a decision that must be recorded |

## 3. Decision

1. **Baseline: Odoo 19.0 Community Edition** for the full estate (67 modules,
   18 OCA subtrees at v19).
2. **In-flight major upgrade: Option A** — a dedicated upgrade slot in **Wave 6**
   (`P09-M02`), landing Odoo 20 with the PostgreSQL major-version co-ordination
   named in `D-029` §3.
3. **Odoo 20 early assessment starts now** (it shipped 24–26 September 2026):
   `W0-01`-method OCA v20 availability checks run at every wave gate from `G1`
   onward so the W6 slot is a migration, not a discovery.

## 4. Consequences

- `P09-M02` executes in Wave 6 with the fork audit as its entry condition.
- Any custom module that cannot migrate to Odoo 20 by W6 is a `AS-05` fork
  defect and blocks the slot — this is the pressure that keeps `FORKS.yaml`
  empty.
- Odoo 19 OCA pin drift after W6 planning starts is frozen: no new OCA pin may
  move to a v20-only repository before the upgrade branch is cut.

## 5. Revisit triggers

- OCA v20 availability for fewer than 12 of 18 repositories at `G5`/`G6` → escalate
  to Steering: extend Odoo 19 extended support (to ~Sept 2029) and re-slot.
- Odoo 19 extended-support policy changes → re-run the currency check
  (`tooling/version-currency/verify-version-currency.ps1`).

---

## 6. Wave 6 Review & Re-Confirmation (P09-M02 / R07-M02-T01)

**Review Date:** 2026-10-18 (Wave 6, Month 26, Gate G6)  
**Assessed Reality:**
1. **Odoo 20 upstream release:** Odoo 20 debuted at Odoo Experience Brussels on 24–26 September 2026 and is the current major.
2. **Support window currency:** Odoo 19.0 Community Edition standard support extends through September 2028, with extended support through September 2029.
3. **OCA v20 readiness:** The W6 OCA availability scan (`tooling/upgrade/verify_fork_and_oca_matrix.py`) found only 4 of 20 OCA subtrees with mature 20.0 branches. This breaches the threshold of 12 required for an in-flight major migration.
4. **Outcome:** In accordance with §5, Decision `D-038` formally exercises the planned deferral of the Odoo 20 branch migration to post-go-live, guaranteeing zero-risk runtime stability for the 1000FiX production deployment.
