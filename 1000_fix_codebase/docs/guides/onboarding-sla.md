# Onboarding SLA — measured per joiner (P02-M10-T08; DE-21/DE-22)

**A joiner exceeding 4 hours on `core` triggers a defect against `BE-001`,
not against the joiner.** Any step regularly exceeding its budget is
automated or cached. File one form per joiner; the totals are reported at
the wave gate.

| Phase | Budget (`core`) | Budget (`full`) | Actual | Defect? (file against BE-001, with step) |
|---|---:|---:|---:|---|
| System packages + toolchains | 30–45 min | 30–45 min | | |
| Clone (submodule + subtrees) | 20–40 min | 20–40 min | | |
| `make bootstrap` / `tasks.ps1 bootstrap` | 15–25 min | 15–25 min | | |
| Image pulls | 5–10 min | 20–35 min | | |
| `db-create` + `odoo-init` + `install-wave1` | 15–30 min | 15–30 min | | |
| `make seed` | 3–5 min | 3–5 min | | |
| `make doctor` / `doctor.ps1` | 5 min | 8 min | | |
| **Total** | **1.6–2.7 h** | **1.9–3.1 h** | | |

Joiner: ______________  Date: __________  Machine class: ☐ RECOMMENDED ☐ MINIMUM(core-only)
Mentor: ______________  Profile: ☐ core ☐ full

Gate criterion (`G0b`): every developer's `make doctor` green **within the
budget from a bare machine** — the SLA is the exit criterion, so the
measurement IS the gate evidence.
