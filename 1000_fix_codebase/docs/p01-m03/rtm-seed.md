# RTM seed — requirement → module → wave → CD slot → test slot (T07)

**Task `P01-M03-T07`** · Seed generated 2026-10-01:
[`registers/rtm-seed.csv`](registers/rtm-seed.csv), **3,347 rows — one per
requirement**, reciprocal by construction. Method basis: ISO/IEC/IEEE 24765
*bidirectional traceability* ("each traversable in both directions") and
RQ-004 rule `TR-02` (reciprocity); forward tracing ensures nothing required
is missed, backward tracing catches orphans and gold-plating —
[practice](https://www.jamasoftware.com/requirements-management-guide/requirements-traceability/bidirectional-traceability/),
[ISO 29148](https://www.iso.org/obp/ui/#iso:std:iso-iec-ieee:29148:ed-2:v1:en).

## What the seed establishes (machine-checked)

| Property | Check in force | Result |
|---|---|---|
| Every requirement traces forward to a test slot | `TC-<requirement-id>` slot per row | 3,347/3,347 ✅ |
| Every requirement traces backward to a module | module code from the owning spec | 3,347/3,347, 79/79 specs carry rows ✅ |
| No orphan requirements | zero rows without module/wave (multi-wave rows carry the module's wave set) | ✅ |
| No duplicate keys | `CR-01` duplicate check | 0 duplicates ✅ |

## What the seed deliberately does NOT claim (the squads' RTM work)

1. **`cd_slot` is module-granular** (`CD-set(Mnn)`): the per-requirement CD
   assignment from `BE-005` §6's 331-item register is derivation work the
   squads perform against the TSS §12 module→CD ranges; the seed carries the
   join key (module) that makes it mechanical.
2. **`test_slot` is a slot, not a test case**: `TC-<id>` becomes real when
   `RQ-010`'s DoD standard drives test derivation per module at its wave;
   the reciprocity checker (forward link present AND backward link resolves)
   is the acceptance rule RQ-004 `TR-02` already defines.
3. **SWR-001…042 rows are absent from the seed** — they live in RQ-001
   §9.6.12, not in module §5 tables; they enter the RTM at adoption time with
   their own module/wave assignment (42 rows, listed in the wave-allocation
   residual worklist).

The programme-tool matrix (`RQ-004`: "in the programme tool, not a
spreadsheet") is populated from this seed when the tool exists (`P01-M01-T06`);
until then the CSV is the authoritative register and the scan tool regenerates
it at every gate.
