# CR-P01M04-01 — Wave-1 scope movements MV-01…MV-05 (T03)

| | |
|---|---|
| **CR ID** | `CR-P01M04-01` |
| **Date** | 2026-10-01 |
| **Raised against** | Wave plan (`06-01`/`GV-004`); AR-006 §5.5; roadmap §0.4.3 |
| **Allocating authority** | Steering Committee (Wave-1 scope increase requires explicit approval) |
| **Effect** | Resolves **19 of 32 wave-order violations directly, 6 more by consequence** |

| MV | Movement | From → To | Why (from the regenerated graph) |
|---|---|---|---|
| **MV-01** | M21 employee master + joiner/mover/leaver events | W5 → **W1** | M29 in-degree **53**; `KPI-090` (deprovision ≤1h on `employee.left`) unachievable otherwise; breaks the M21↔M29 mutual pair at its serious end |
| **MV-02** | M24 `fix.document` kernel + retention class + attachment API | W3 → **W1** | Kernel concept; in-degree 23; 17 W1–W2 consumers |
| **MV-03** | M51 VAT determination + Mushak 6.3 issuance | W4 → **W3** | Statutory; the W3 gate already requires it |
| **MV-04** | M64 MDM governance core | W2 → **W1** | Governs the W1 kernels (M33/M37 ↔M64 mutual pairs) |
| **MV-05** | M17 device registry core — *declaration correction only* | W2 → W1 | Already W1 in `06-01`; this CR corrects the inconsistent register |

**Cost:** ~**40 PW added to Wave 1** — `GV-004` must cost them against the
inverted-ramp position (P01-M09-T03 records that W1 is already the smallest
team the programme will ever have). **Steering approval is the external step**;
this CR is the architectural input the capacity re-plan requires.
