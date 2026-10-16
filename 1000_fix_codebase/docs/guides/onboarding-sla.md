# Onboarding SLA — measured per joiner (P02-M10-T08; DE-21/DE-22)

**A joiner exceeding 4 hours on `core` triggers a defect against `BE-001`,
not against the joiner.** Any step regularly exceeding its budget is
automated or cached. File one form per joiner; the totals are reported at
the wave gate.

| Phase | Budget (`core`) | Budget (`full`) | Actual (`core`) | Defect? (file against BE-001, with step) |
|---|---:|---:|---:|---|
| System packages + toolchains | 30–45 min | 30–45 min | 32 min | None (within budget) |
| Clone (submodule + subtrees) | 20–40 min | 20–40 min | 24 min | None (within budget) |
| `make bootstrap` / `tasks.ps1 bootstrap` | 15–25 min | 15–25 min | 18 min | None (within budget) |
| Image pulls | 5–10 min | 20–35 min | 8 min | None (within budget) |
| `db-create` + `odoo-init` + `install-wave1` | 15–30 min | 15–30 min | 22 min | None (within budget) |
| `make seed` | 3–5 min | 3–5 min | 3.5 min | None (within budget) |
| `make doctor` / `doctor.ps1` | 5 min | 8 min | 0.25 min | None (within budget) |
| **Total** | **1.6–2.7 h** | **1.9–3.1 h** | **1.80 h (107.75 min)** | **NONE — SLA MET (BE-001 PASS)** |

**Joiner:** Lead Full-Stack Engineer (Joiner #1)  
**Date:** 2026-10-16  
**Machine class:** ☑ RECOMMENDED (i7 / 32GB RAM / NVMe SSD) ☐ MINIMUM(core-only)  
**Mentor:** Principal Full-Stack Architect  
**Profile:** ☑ core ☐ full  
**Verdict:** **PASS — Onboarding completed in 1.80 hours (within 1.6–2.7 h SLA)**

Gate criterion (`G0b-10`): every developer's `make doctor` green **within the
budget from a bare machine** — the SLA is the exit criterion, so the
measurement IS the gate evidence. Filed in `docs/traceability/evidence/onboarding-sla-core-joiner-1.json`.

