# GV-003 decision-log entries — P01-M02 output, ready to paste

**Task `P01-M02-T09`** requires the decisions to be "recorded in `AR-004` as
ADRs, and cross-referenced from `GV-003`". The `GV-003` decision log is a live
programme artefact opened in the programme tool at `P01-M01-T06` — which does
not exist yet. **These are the rows to paste when it opens**, so the
cross-reference is completed on the day the tool exists rather than
reconstructed later. Every row names its allocating authority (`DL-08`).

| D-nnn | Date | Title | Status | Authority | ADR (path in this codebase) | Closes / blocks |
|---|---|---|---|---|---|---|
| `D-001` | 2026-10-01 | Programme Charter Approval & Statutory Appointments (CDO & Committees) | APPROVED | Board (`BM-2026-10-01-D001`) | `docs/governance/BM-2026-10-D001-charter-and-governance.md` | **Closes `B-01`**; establishes statutory governance |
| `DEP-31-ENG` | 2026-10-01 | DEP-31 Legal Counsel Engagement Letter Signed & Sent (Dr. Kamal Hossain & Associates) | EXECUTED | Managing Director & CEO | `docs/governance/DEP-31-engagement-letter-signed.md` | **R01-M01-T01**; mandates PDPA opinion Q1-Q5 |
| `D-013` | 2026-10-12 | Split-residency data architecture: Option B adopted on `DEP-31` legal opinion | ACCEPTED | Board (`BM-2026-10-D013`); `CA` records | `docs/decisions/D-013-split-residency.md` | **Closes `B-02`**; unblocks all persistent-state build |
| `D-025` | 2026-10-01 | Odoo baseline 19.0, in-flight upgrade slot W6 (Option A) | ACCEPTED | ARB → `CA` | `docs/decisions/D-025-odoo-baseline-upgrade.md` | Closes `B-08`; governs `P09-M02` |
| `D-026` | 2026-10-01 | Portal frontend baseline Next.js 16.2+/16.3 + Payload 3.73+ | ACCEPTED | ARB → `CA` | `docs/decisions/D-026-portal-frontend-baseline.md` | Closes `B-07`; governs `W0-05`, `P05-M07-T01` |
| `D-027` | 2026-10-01 | Mobile framework: Flutter; P07 mobile surface = PWA (`CR-P01M02-05`) | ACCEPTED | ARB → `CA` with `MB`; CTO confirms `D-17` at W6 | `docs/decisions/D-027-mobile-framework.md` + `docs/p01-m02/CR-mobile-reallocation-D027.md` | Closes `B-09`, `BE-001 Q-01`; resolves TSS `D-17` by position |
| `D-028` | 2026-10-01 | Object store: Ceph Object Storage (replaces MinIO, archived 2026-04-25) | ACCEPTED | ARB → `CA` | `docs/decisions/D-028-object-store.md` | Closes `B-19`; governs `P02-M05-T02` |
| `D-029` | 2026-10-01 | PostgreSQL baseline 17 (EOL 2029-11-08; PG18 re-opened at `P09-M02-T01`) | ACCEPTED | ARB → `CA` | `docs/decisions/D-029-postgresql-major.md` | Closes `B-21`; CR raised vs TSS (16) |
| `D-030` | 2026-10-01 | Restricted-licence register — complete enumeration incl. Grafana/Loki/Tempo/TimescaleDB/Vault; OpenBao = W1 vault pick | ACCEPTED (register, annual review) | ARB → `CA`; `SL` co-signs | `docs/decisions/D-030-restricted-licence-register.md` | Closes `B-22`; gate at `P02-M08-T04` |
| `D-031` | 2026-10-01 | Redis licence currency — pin 7.2.x (last BSD) or adopt Valkey; no 7.4+/8.x pin until taken | PROPOSED | ARB (`CA` proposes) | `docs/decisions/D-031-redis-licence-currency.md` | Blocks `P02-M05-T02` Redis pin |
| `CO-003-AMD` | 2026-10-05 | SoW F-08 Scope Gap Settlement & Living Baseline Adoption | EXECUTED | Client & Partner Signatories | `docs/p01-m08/SoW-F08-signed-amendment.md` | **Closes `B-11`**; sets baseline at 3,389 / 122 NFRs |
| `D-002` | 2026-10-05 | Super-User Availability Roster (Option C Phased Model — 85 Names) | APPROVED | Board (`BM-2026-10-D002`) | `docs/p01-m09/D-002-super-user-named-roster.md` | **Closes `B-12`**; commits 30% UAT time |
| `MIG-01` | 2026-10-10 | 48 Legacy Sources Profiled across 8 Classes & Non-Migration Rulings | ACCEPTED | Migration Lead & ARB | `docs/p01-m07/legacy-source-profiles-completed.md` | **Closes `B-06`**; 100% profiles completed |
| `D-034` | 2026-10-17 | L6 Commercial Software: Cloud Telephony / CPaaS for Hotline 16743 (TC-070) | ACCEPTED | CFO, CTO, `CA` | `docs/decisions/D-034-l6-cpaas-telephony.md` | **R05-M03-T01**; written Asterisk review; carrier interconnect |
| `D-035` | 2026-10-17 | L6 Commercial Software: Qualified E-Signature under Bangladesh ICT Act 2006 (TC-071) | ACCEPTED | CFO, `SL`, `CA` | `docs/decisions/D-035-l6-qualified-e-signature.md` | **R05-M03-T01**; written OSS review; CCA evidentiary presumption |
| `D-017` | 2026-10-18 | Gate G4 Tranche Decision: Formal Re-Authorisation of Waves 5–9 | RATIFIED | Executive Steering Committee | `docs/decisions/D-017-g4-tranche-decision-waves-5-9.md` | **R05-M05-T05 / G4-08**; unblocks Tranche 2 (Waves 5–9) |
| `D-037` | 2026-10-18 | Kafka Event Bus Migration & Redis Streams Retirement (P09-M01) | ACCEPTED | ARB, `CA`, Integration Lead | `docs/decisions/D-037-kafka-event-bus-migration.md` | **R07-M01**; 3-node HA KRaft cluster, G6-3 PASS |
| `D-038` | 2026-10-18 | Odoo 20 Upgrade Slot Execution: Formal Controlled Deferral (P09-M02) | RATIFIED | Executive Steering Committee & ARB | `docs/decisions/D-038-odoo20-upgrade-slot-execution.md` | **R07-M02**; D-025 §5 trigger; Odoo 19 extended support to Sep 2029 |

Also paste (context rows, not new decisions):

| Ref | Note |
|---|---|
| `D-WS-001` | Windows-native workstation baseline (2026-09-30) — supersedes `BE-001-D-06` for this build; ADR in this codebase |
| Findings F-1…F-5 | First version-currency verification record (2026-10-01): Node 20 EOL → Node 22 (`CR-P01M02-04`); Redis licence column (`D-031`); `D-030` enumeration completion; TSS stale rows (`CR-P01M02-01…03`); Node 22 in-window EOL watch |

## Change requests raised by this milestone (paste into the CR register)

| CR | Against | One-line change |
|---|---|---|
| `CR-P01M02-01` | TSS §3.2, §4.1, TC-010 | PostgreSQL 16 → 17 (`D-029`) |
| `CR-P01M02-02` | TSS TC-012 | Redis licence column corrected for 7.4+; `D-031` reference |
| `CR-P01M02-03` | TSS §7.1 register (TC-017/019/029/034) **and §11.9 ("Disputes… + MinIO")** | Superseded-component annotations (n8n→Airflow, MinIO→Ceph ×2, Metabase→Superset, Redpanda→Kafka) |
| `CR-P01M02-04` | `BE-001` §4 + the inherited workspace `AGENTS.md` (Node 20) | Node 20 LTS → Node 22 LTS (Node 20 EOL 2026-04-30, verified); roadmap `P02-M02-T02` annotated accordingly |
| `CR-P01M02-05` | `04-00` §2, `BE-005` §9.1 | P07/APP-09 mobile surface: React Native → PWA on Next 16.3 (W7), native-in-Flutter if separately approved (`D-027`) |
| `CR-P01M03-01` | `02-02` §3 + Category K table | M66/M67 are **written** (30/32 rows, 14/17 PW measured); 67/67 complete |
| `CR-P01M04-01` | Wave plan / `GV-004` | MV-01…05 scope movements into Wave 1 (~40 PW; resolves 19+6 violations) |
| `CR-P01M05-01` | `AR-007` §3.2 | Manifest example: `CD-<UNIT>-<nn>` form, not flat `CD-nnn` |
| `CR-P01M05-02` | `M07`/`M20`/`M50`/`M51` specs | Effort reconciliation (−4/+2/+6/+4 PW per BE-005 §7.2) |
| `CR-P01M08-01` | `primary-doc` TSS §8.2, §25.3.1 | CD count 248 → **331** (machine-verified) |
| `CR-P01M09-01` | `BE-005` §6 type strings | 6 rows typed "Next.js **15** application" → re-label to the `D-026` baseline |
