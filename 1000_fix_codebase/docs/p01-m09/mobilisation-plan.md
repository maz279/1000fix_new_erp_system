# P01-M09 — Team mobilisation & onboarding readiness · Completion record

**IR-002 Phase 1, Milestone M09** · Implemented 2026-10-01.

| Task | Artefact | Status |
|---|---|---|
| **T01** Resource-plan reading record | `GV-007` verified on disk (`project-guide-doc/99…`/commercial set); §8.3 scarcity basis cross-read | ✅ |
| **T02** Odoo requisitions | **Draft requisitions prepared — start immediately (10–16 week hiring lead).** Basis: **278 of 331 CD items (84%) carry Odoo in their type** (measured from `cd-register.yaml` this run; the roadmap's "270 / 82%" is its own count — the measured figure governs, `RG-08`) and the scarcest role carries four-fifths of the deliverable list. Levels: 2 senior (W1 kernel/platform), 3 mid (W2–W3), 2 senior (W4+ upgrade path) | ✡ requisitions live on day 1 |
| **T03** Inverted-ramp position | **Position paper to Steering:** W1 has 3 build FTE against 239 PW demand, rising to 12 FTE by W6 against 23 PW — the heaviest architectural work sits on the smallest team the programme will ever have. Options put with figures: (a) front-load hiring (recommended — matches `D-025`'s W1 kernel), (b) extend W1 by 4 weeks, (c) descope W1 to T0/T1 only. The `MV-01…05` movements add ~40 PW to exactly this wave (CR-P01M04-01) | ✡ Steering decides |
| **T04** 1.69x over-commitment | **Steering decision paper prepared (`D-nnn` draft):** the measured over-commitment (`BEA-06`: 1,850 PW register vs ~1,100 PW planned capacity) is presented with the fund/phase/cut options — *cutting scope is legitimate, but only as a decision taken with the measured figure in front of the Committee* | ✡ Steering decides |
| **T05** Six squads | Charters prepared from roadmap §0.10.1 (names, phases and compositions verified against the roadmap's own table): **Platform** (P2: CA+SA+2OD+2DE+SL — T0/T1, pipeline, environments, residency), **Service Delivery** (P3: SA+3OD+BA+QA — categories A,F), **Commercial & Finance** (P6: SA+3OD+DA+QA — categories C,G), **Experience** (P4: UX+3FE+2MB+LL — 12 portals, design system, offline engine), **Data & Integration** (P3: IL+2BE+DA+ML — 47 integrations, 988 events, warehouse), **People & Governance** (P8: SA+2OD+QA — categories H,I) — each names its WBS-3 elements and its business owner slot (`WBS-03`: one accountable squad + one business owner per element) | ✡ named individuals on day 1 |
| **T06** `D-002` super-users | [`D-002-super-user-availability.md`](D-002-super-user-availability.md) — the decision record with the arithmetic (134–201 super-users at 30% during UAT) and the three mitigation options | ✡ Board decides |
| **T07** Branch champions | Roster framework: 1 champion per branch × **51+ branches**, 4 h/week during rollout — feeds `CH-05`'s charter | ✡ roster fills on day 1 |
| **T08** Workstations | **Procurement spec issued — and already executable:** the P02-M01 baseline (`D-WS-001`, native Windows per product-owner direction) with `verify-workstation.ps1` as the per-machine acceptance test. Recommended tier 8c/16t/32GB/512GB NVMe (this machine: RECOMMENDED class, evidence on file). **Note the deviation honestly:** the roadmap's T08 row says Ubuntu and "Windows natively not supported" — `D-WS-001` supersedes for this build, and the roadmap row's dependency on `P01-M02-T08` is satisfied by the Q-02 policy | ✅ (evidence: workstation runs 2026-09-30/10-01) |
| **T09** Encryption confirmation | **Enforced by tooling:** `verify-workstation.ps1` T03 (BitLocker) — the baseline is RED until encrypted, per the Q-02 policy; the dev machine's open T03 is tracked as the standing example. Fleet: BitLocker at imaging, keys escrowed to the Company directory | ✅ per-machine evidence |
| **T10** Change & training schedule | `CH-001…CH-005` verified on disk (`project-guide-doc/13_Training_Change_and_Adoption`); schedule drafted **from Phase 3, not Phase 11** — 51+ branches absorb ~**one major process change per quarter**, so the training calendar is built backwards from rollout waves | ✅ |

## The mobilisation arithmetic (for the Steering pack)

| Fact | Figure | Source |
|---|---|---|
| Odoo share of CD items | **278 / 331 = 84%** (measured; roadmap said 270/82%) | `cd-register.yaml` (this run) |
| Senior-Odoo hiring lead | 10–16 weeks | `GV-007` §8.3 |
| W1 demand vs team | 239 PW vs 3 build FTE | `GV-004` §5.2/§5.3 |
| UAT super-user demand | 2–3 × 67 modules = **134–201 people at 30%** | `GV-004` §6.3 |
| Over-commitment | 1,850 PW register vs planned capacity ≈ **1.69x** | `BEA-06` |
