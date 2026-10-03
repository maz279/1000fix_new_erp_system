# Squad Working Agreement & Velocity Record (P03-M01-T09/T10)

## Working agreement (T09 — `BE-008` §4.1–§4.2, `SPR-15`)

| Ceremony | Cadence | Duration | Notes |
|---|---|---|---|
| Sprint | 2 weeks, **starts Wednesday** | — | Aligns with the sprint calendar (CR-E) |
| Daily scrum | Async, every working day | 10 min | **Impediments only** — not a status report; blockers get names and dates |
| Refinement | Weekly | 30 min | Backlog items prepared to "ready"; stories sized ≤ 8 points |
| Review | End of sprint | 30 min | Working software, not slides; the P03 admin portal is the surface |
| Retro | End of sprint | 20 min | One improvement action with an owner; carried to the next retro |

**`SPR-15`: ceremony time IS capacity and is accounted for explicitly.**
At 3–5 FTE, ~2.5 hours per sprint per person on ceremonies ≈ **6% of
capacity** — deducted from the 0.78 delivery factor, not added on top.

**Ceremony accounting (per sprint, per person):**

| Item | Hours |
|---|---:|
| Daily scrum (10 × 10 min) | 1.7 |
| Refinement (1 × 30 min) | 0.5 |
| Review (1 × 30 min) | 0.5 |
| Retro (1 × 20 min) | 0.3 |
| **Total** | **3.0** (= ~3.75% of a 80-hour sprint) |

## Velocity record (T10 — `BE-008` §5.2–§5.3, `SPR-17`/`SPR-19`, `GV-004-A1`)

**The 0.78 delivery factor is an industry convention, NOT a 1000FiX
measurement.** `BE-008` must establish a measured factor by the end of Wave
1. **A lower factor makes every capacity conclusion worse, not better.**

| Sprint | Dates | Planned (pts) | Completed (pts) | Velocity | Factor (completed/planned) | Provisional? |
|---|---|---|---|---|---|---|
| 1 | — | — | — | — | — | **YES** (no history) |
| 2 | — | — | — | — | — | **YES** (< 3 sprints) |
| 3 | — | — | — | — | — | **First measured** (3-sprint history) |
| 4 | — | — | — | — | — | Measured |
| 5 | — | — | — | — | — | **G1a report** (the capacity position) |

**Reporting rule (`SPR-19`):** every velocity report states **"provisional
factor"** until three sprints of history exist. After sprint 3, the factor
becomes measured and the label changes — but the first three reports MUST
carry the provisional caveat. **Every report says which it is.**

**Capacity position at G1a (`P03-M10-T09`):**
- Nominal Wave 1 demand: **~120 PW**
- Available capacity: ~20 effective PW at 3 build FTE over 8.7 weeks
- **The 5.87x over-commitment becomes a MEASUREMENT at G1a, not a projection**
- Report the measured velocity; if G1 at Month 4 is unreachable, **say so now**
- Descoping is still cheap at this point; it gets more expensive every wave

**Conversion factor formula (`GV-004-A1`):**

```
delivery_factor = completed_story_points / planned_story_points
                (cumulative across all sprints, not per-sprint)
```

Track from sprint 1. Use the industry 0.78 until sprint 3 closes, then
switch to the measured value and re-baseline the capacity model.
