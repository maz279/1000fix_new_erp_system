# P01-M07 — Legacy landscape profiling · Completion record

**IR-002 Phase 1, Milestone M07** · Implemented 2026-10-01. Closes `B-06` at
execution; this record issues the profiling instrument and the rulings that do
not depend on profile results. Basis: `MG-001…MG-007` (on disk in
`project-guide-doc/09_Data_Migration_and_Cutover`) and TSS §19.

## The 48-source register (T02) — instrument issued

`DM-002` inventories **48 sources across eight classes** — *"registered, nobody
has looked inside any of them"* (MG-002 §2). **Note (verified this run):**
`DM-002` is referenced by MG-001/002/003 but the inventory document itself is
**not yet issued** — the 48/8-classes frame is MG-002's own count, inherited
here as the register's basis; issuing `DM-002` as the formal inventory is a
migration-workstream action this register front-runs. The register below is
the profiling instrument; each row completes as profiling executes (~4-week
float item on the near-critical chain to `G1-05`). Profile acceptance test
(MG-002 §3): volume counted or sampled with method; measures P1–P6 at L1/L2/L3;
sentinels/encoding including Bengali normalisation; cross-source overlap;
consequences; remediation; assumption test; signed acceptance.

| # | Class (DM-002 eight) | Sources | Profile status | Feeds |
|---|---|---:|---|---|
| 1 | **Live tracker DBs** | 2 | ☐ extract specs below | M01, P01 (W2) |
| 2 | Per-branch service-order spreadsheets | 51+ files (one class) | ☐ mapping spec below | M01 kernel |
| 3 | Accounting history (legacy books) | per class | ☐ | M19 balances/open-items only |
| 4 | HR/payroll Excel (incl. the 2026 Amendment rates it does not contain — P01-M02 §0.7.4) | per class | ☐ | M56 |
| 5 | WordPress site content | 1 | ☐ | content migration |
| 6 | Inventory/asset lists | per class | ☐ | M15/M17 |
| 7 | Customer contact stores | per class | ☐ | M33 + dedup (T09) |
| 8 | Misc. documents/evidence | remainder | ☐ | M24 |
| | **Total registered** | **48** | | |

## Rulings issued (do not depend on profile results)

| Task | Ruling |
|---|---|
| **T03** Tracker extracts | `station.1000fix.com` and `123.0.26.238/orderTracking` profile **by database extract** (MG-002 §7 form: manifest, integrity proof, chain of custody); both feed M01/P01 in W2 |
| **T04** Spreadsheet class | Per-file mapping + validation specification against the intake template; **the most variable source class** — column drift per branch is expected and profiled, not assumed |
| **T05** Data quality first | DQ report per source (MG-005 `MIG-05`); **the business decides** what to cleanse, migrate as-is, or leave behind — engineering proposes, the business disposes |
| **T06** Non-migration ruling | **Ruled out:** workshop paper job cards (open WIP only), attendance sign-in books (opening balances only), accounting transaction history (balances and open items only). Signed at the gate — recording what is *not* migrated is as important as what is |
| **T07** Migration standards | `MIG-01…MIG-08` in force: `MIG-02` control totals; `MIG-03` permanent legacy reference on every migrated record; `MIG-04` dry run against production-sized data before every cutover |
| **T08** `MIG-06` — the easily-missed one | **Migrated personal data goes through the same `CD-M29-nn` residency service as application data.** A bulk loader bypassing the runtime ORM check (P01-M06-T05) would create the exact compliance breach the architecture exists to prevent — at scale, on day one. Bulk loaders call the residency service batch API; there is no direct-to-store path |
| **T09** Dedup/merge | Cross-source customer dedup specification: match keys (NID checksum, phone normalisation incl. Bengali digits), survivorship rules per `M33` `cd_dedup_merge` — the party kernel must not inherit the duplicate-identity problem the programme exists to remove |
| **T10** Mock migrations + staging | `migration-staging` is **production-class, at production volume — it is not `staging`** (PE-002 §5.9); mock schedule per wave with `MIG-04` dress rehearsals before every cutover |

## Gate contribution (`G1-05`)

`B-06` closes when the 48 rows above carry signed profiles and the DQ reports
are in the business's hands — the instrument, the rulings and the standards are
now in force, so profiling starts on day one rather than after discovery.
