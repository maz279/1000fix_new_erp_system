# Migration protocol — expand / migrate / contract (P02-M09-T10)

**Zero-downtime deployment requires forward-only, backward-compatible
migrations: a release ADDS a column before code uses it, and REMOVES a column
only after no code references it — three releases, never one** (`RL-002` §5,
`EP-05`; `SQL-05` is the review-only rule that polices the same seam).

| Release | Migration phase | What may land | Rollback |
|---|---|---|---|
| **R(n)** | **Expand** | New columns/tables/indexes, nullable, no code reads them | Trivial — unused schema is inert |
| **R(n+1)** | **Migrate** | Code reads and writes the new shape; backfill jobs run; old shape still maintained | Code reverts; old shape is still there |
| **R(n+2)** | **Contract** | Drop the old column/table — only after no code references it (verified by grep + fitness check) | The three-release structure IS the rollback |

## Rules

1. **No destructive DDL in the same release as the code that needs the old
   shape.** The stage-14 dry run (`make odoo-upgrade-dryrun`) rehearses the
   full sequence against a production-sized clone on `migration-staging`
   (production-class, masked inline — `NFR-086c`).
2. **Column lifecycle is a review item (`SQL-05`)** — no tool catches it;
   the PR checklist asks, the reviewer answers.
3. **Secrets** come from the environment's secret store (Vault→OpenBao in
   Wave 1 per `D-030`), never from files, commits or this repository.
