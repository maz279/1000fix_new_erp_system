# Troubleshooting register (P02-M10-T09)

**Maintained by the person who solved the problem, not by the document
owner.** Solved something not here? Add the row in your PR - that is the
convention. Seeded with the 13 known failures (`BE-001` §9) plus the
Windows-native additions this programme has already met.

| # | Symptom | Cause | Remedy |
|---|---|---|---|
| 1 | `lxml`/`python-ldap` build fails on first `uv sync` (Linux) | Missing `libxml2-dev libxslt1-dev libsasl2-dev libldap2-dev` | `sudo apt install …` (BE-001 §3.4 block) — the single most common first-hour failure |
| 2 | Module not found at install; `addons_path` stale | Path not regenerated after adding a category | `make odoo-conf` and commit (REPO-15; doctor check 5) |
| 3 | Breakpoints never hit | `workers > 0` — Odoo forked; the debugger is on the parent | `workers = 0` in local.conf (it is a debugger truth, not a perf setting) |
| 4 | PDF reports blank/unstyled | Distribution `wkhtmltopdf`, not the patched-Qt build | P02-M01-T08 installer; `make doctor` check 10's lineage |
| 5 | Bengali shows boxes/tofu | Bengali fonts absent | P02-M01-T05 (`verify-workstation.ps1` T05); restart the browser |
| 6 | `port is already allocated` | Host service or sibling stack on 5432/6379/9000 | `verify-workstation.ps1` T10; stop the sibling stack or remap (DE-01) |
| 7 | Everything is glacially slow on WSL/`/mnt/c` | Cross-OS filesystem boundary | Keep the repo on the native FS; on Windows-native baseline (D-WS-001) use the container volume mounts, never `/mnt/c` equivalents |
| 8 | `full` profile OOMs the laptop | 15 services ≈ 10–12 GB on a 16 GB machine | Use `core` (the default); `full` is for integration testing (BE-001 §5.2) |
| 9 | Clone ran 45 minutes | Full Odoo history | Partial clone (`--filter=blob:none`) — `docs/guides/clone-budget.md` |
| 10 | gitleaks flags a sha256/commit hash | Allowlist regex missing | Confirm it is a digest, extend `.gitleaks.toml` allowlist in the same PR |
| 11 | `FF-03` fails on a file you never touched | Subtree re-sync or line-ending churn under `vendor/` | `git status vendor/`; if CRLF churn: `git config core.autocrlf false` and re-checkout (XS-01) |
| 12 | Keycloak realm import loop | Realm JSON edited by hand after first import | The realm file is **generated** (DE-09 synthetic); regenerate, `down -v` the keycloak volume |
| 13 | Compose `up` returns but services unhealthy | Healthcheck grace too short on cold cache | `up --wait` retries; if still red, `docker compose logs <svc>` first, not a restart |
| 14 | *(Windows)* `pre-commit` hooks silently skipped | `core.hooksPath` not set | `tasks.ps1 -Target bootstrap` (sets `.githooks`) |
| 15 | *(Windows)* doctor 6 SKIP though Odoo "runs" | Odoo is containerised (D-WS-001); port not published yet | Start the dev container; doctor 6 probes `127.0.0.1:8069` |
| 16 | doctor 12 reports classified-pattern hits | Someone loaded a real dataset | **Stop.** This is a DE-12 incident: report under SC-009, purge the volume (`reset`), never "mask and continue" |
