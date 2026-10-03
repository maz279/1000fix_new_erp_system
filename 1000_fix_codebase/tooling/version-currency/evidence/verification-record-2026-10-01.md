# Version-currency verification record — first execution

**Task `P01-M02-T10`** · **Run date 2026-10-01** · Mode: **online, live against
upstream** (endoflife.date API + GitHub REST), with the facts below
additionally confirmed by targeted web research the same day.

- Executable: `tooling/version-currency/verify-version-currency.ps1`
- Standing list: `tooling/version-currency/components.json` (43 checks:
  1 watch-guard, 3 L1–L3 classes, 30 L4 components, 5 app-platform runtimes,
  4 L6 commercial)
- Machine JSON record: `verification-record-2026-10-01.json` (this directory)

> **Ritual rule (alignment audit `R-04`):** every component is re-verified
> against upstream — never against the last document that verified it.
> Every figure below carries the timestamp that made it true (`RG-08`).

## 1. Headline results (live, 2026-10-01)

| Check | Result | Source |
|---|---|---|
| **Watch-guard: `minio/minio` still archived upstream** | OK — the `IRB-01` failure mode remains detected; the `D-028` replacement rationale holds | api.github.com/repos/minio/minio (`archived: true`) |
| **PostgreSQL 17 EOL = 2029-11-08 — 1,134 days of margin** | OK — `D-029` baseline confirmed live; PG18 (EOL 2030-11-14) remains the `P09-M02-T01` re-open | endoflife.date/api/postgresql.json; postgresql.org/support/versioning |
| **Next.js cycle 16: no EOL announced upstream** (endoflife.date reports `eol: false` for the current cycle) | OK — `D-026` baseline is the current LTS line; **Next.js 15 EOL 2026-10-21 confirmed live (20 days from this record)** | endoflife.date/api/nextjs.json; nextjs.org/support-policy |
| **Node.js cycle 22 EOL = 2027-04-30 — within 365 days** | WARN (genuine) — see finding F-5 | endoflife.date/api/nodejs.json |
| Python 3.12 EOL = 2028-10-31 — 761 days of margin | OK | endoflife.date/api/python.json |
| 30 L4 repositories active upstream (incl. all four `D-030` replacements: `apache/airflow`, `ceph/ceph`, `apache/superset`, `apache/kafka`) | OK — no archived repos in the stack | api.github.com per component |
| Sample latest-upstream observations captured during the run (informational, `DE-06` pinning unaffected): ClickHouse `v26.9.7.9-stable`, MLflow `v3.16.1`, Ollama `v0.35.0`, Superset `6.1.0`, Wazuh `v4.14.8`, osquery `5.23.1`, ClamAV `1.5.4`, Tempo `v3.1.0`, PgBouncer `1.26.0` | recorded | api.github.com releases |

**Run tally (definitive online run, 2026-10-01): 42 OK · 1 WARN · 0 FAIL ·
exit 0.** The single WARN is `APP-node` — Node 22 EOL 2027-04-30 within the
365-day horizon — a genuine finding with a disposition (F-5), not a tooling
limitation. An earlier same-day run first exercised the pipeline before the
script's quota discipline (`releases/latest` opt-in) was tightened; its
observations are folded into §1 and the quota note below.

## 2. Findings raised by this run (dispositions in `P01-M02.md`)

| # | Finding | Severity | Disposition |
|---|---|---|---|
| **F-1** | **Node.js 20 — the `BE-001` toolchain pin — EOL since 2026-04-30** (Node 22 Maintenance LTS to 2027-04-30; Node 24 Active LTS) | HIGH | `P02-M02-T02` installs **Node 22**; CR raised against `BE-001` §4; Node 24 re-baseline is a gate question |
| **F-2** | **TSS TC-012 "Redis 7.x, BSD-3" is wrong for 7.4+** (7.4+ RSALv2/SSPL; 8.x tri-licence incl. AGPLv3; Valkey = BSD-3 fork) — verified at redis.io/legal/licenses, redis.io/blog/agplv3 | HIGH | `D-031` PROPOSED (pin 7.2.x or adopt Valkey; **no 7.4+/8.x pin until taken**); CR against TSS TC-012 |
| **F-3** | `D-030`'s roadmap table did not enumerate the remaining restricted-licence components (Grafana/Loki/Tempo AGPL; MeshCentral/RustDesk AGPL arm; TimescaleDB TSL; **HashiCorp Vault BUSL 1.1**) | MEDIUM | Register completed (`D-030` §2.2) with per-component approval bases; **OpenBao recorded as the Wave 1 vault pick** |
| **F-4** | TSS stack register stale vs the decisions (PG16, MinIO, n8n, Metabase, Redpanda rows) | MEDIUM | One CR, five annotated rows (`P01-M02.md` §corrections) |
| **F-5** | Node 22 EOL 2027-04-30 inside the programme window | MEDIUM | Watch item on `APP-node`; owned by gate cadence |

## 3. Manual facts verified this run (dated sources — `RG-08`)

| Fact | Verified | Source |
|---|---|---|
| Odoo Experience 2026 Brussels **24–26 Sep 2026 has taken place**; Odoo 20 is current; Odoo 19 standard support to **~Sep 2028** | 2026-10-01 | odoo.com/event/odoo-experience-2026; Odoo 19.0 docs *Standard and extended support* |
| **Payload 3.73.0 (2026-01-23) = the Next.js 16 support release**; Payload permanently excludes Next 15.5–16.1.x; requires Node ≥ 20.9; Payload 4.0 in canary | 2026-10-01 | payloadcms.com/docs/installation; github.com/payloadcms/payload releases; release coverage |
| **Flutter 3.44**: Material/Cupertino frozen in core → standalone `material_ui`/`cupertino_ui`; Impeller default on Android; Dart 3.12 | 2026-10-01 | flutter.dev/blog/whats-new-in-flutter-3-44; flutter/flutter#184093 |
| **Redis licence timeline** (≤7.2 BSD-3 / 7.4+ RSALv2+SSPL / 8.x +AGPLv3; Valkey BSD-3, Linux Foundation, Apr 2024) | 2026-10-01 | redis.io/legal/licenses; redis.io/blog/agplv3; redis.io/blog/redis-adopts-dual-source-available-licensing |
| **Keycloak 26.x current** (26.7.x Aug 2026); minor-release back-compat from 26.0; no formal community LTS product | 2026-10-01 | keycloak.org releases; endoflife.date/keycloak |
| **Ceph Squid (19.2.x) current stable**, LGPL-2.1/3 | 2026-10-01 | docs.ceph.com Squid release notes; github.com/ceph/ceph |
| **Node.js 20 EOL 2026-04-30**; Node 22 Maintenance LTS (EOL 2027-04-30); Node 24 Active LTS | 2026-10-01 | nodejs.org release schedule; endoflife.date/nodejs |

## 4. Quota note (historical, resolved)

The first same-day run's per-repo `releases/latest` probes consumed the
GitHub unauthenticated hourly quota (60 req/h) late in the run — two
components returned HTTP 403 (WARN + remedy; facts covered by §3). The script
was then patched (`latest: true` opt-in; a full run uses ~44 of 60 requests)
and the **definitive run above completed cleanly within quota**. Re-runs are
cheap and idempotent; the JSON in this directory is the definitive run.

## 5. Standing rule going forward

This script runs **at every wave gate** and the register is reviewed
**annually** (`D-030`). A component that fails here fails the gate
(`DE-18`/`DE-19` semantics: remedy printed, exit non-zero).
