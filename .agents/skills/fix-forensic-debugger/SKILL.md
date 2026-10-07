---
name: fix-forensic-debugger
description: >-
  Top-of-the-line forensic debugging skill for the 1000FiX ERP v2.0 estate —
  Odoo 19 (64 cd_* modules, 123 models), Next.js 16 portals (8 apps),
  Flutter mobile (4 apps + fix_offline), Kong/Keycloak/PostgreSQL/Docker.
  Method: Evidence-First Debugging (reproduce → bisect the layer cake →
  prove root cause → fix → regression-lock). Encodes every battle scar from
  PP0–PP6 live audits: Turbopack client crashes, build-time env baking,
  unbound-fetch Illegal invocation, Kong strip_path defaults, Odoo controller
  kwargs double-pass, module hot-reload traps, in-app-browser pane limits.
  Use when anything in this repo is broken, slow, mismatched, or "not working".
---

# 1000FiX Forensic Debugger — Evidence-First, Layer-Cake, Battle-Scarred

You are the estate's incident responder. The system spans six layers
(browser → Next portal → Kong → Odoo → Python models → PostgreSQL) plus
Flutter mobile and a Docker stack. **Symptoms lie; evidence doesn't.**
A green build, a passing test, and a plausible theory are all hypotheses —
never conclusions.

---

## 1. The Method (non-negotiable order)

```
1. REPRODUCE   — one exact, repeatable stimulus → symptom pair
2. LOCALIZE    — bisect the layer cake; find the FIRST layer where truth breaks
3. EXPLAIN     — a causal mechanism that predicts the symptom exactly
4. FIX         — the minimal change at the layer where the cause lives
5. PROVE       — re-run the original failing stimulus; it must now pass
6. LOCK        — add a regression test/gate so it cannot return
7. RECORD      — one paragraph in ITERATIONS.md; update this skill if new scar
```

**Laws:**
- **Law of One Layer:** the root cause lives in exactly ONE layer; every
  other layer only *propagates* the symptom. Find the first layer whose
  OUTPUT is wrong given its INPUT is right — that's the culprit layer.
- **Law of No Green Trust:** builds and static checks prove nothing about
  runtime. Every fix is proven by exercising the real path (HTTP call,
  real browser, real DB) — see §5 Probes.
- **Law of Two Strikes:** the same approach failing twice = STOP; change
  the *approach*, not the patience (re-read evidence, bisect differently).
- **Law of Minimal Diff:** fix at the cause layer; resist drive-by refactors.
- **Rubber-duck first:** state the expected-vs-actual in one sentence
  before touching anything. If you can't, you don't understand the bug yet.

**5 Whys is for humans. For machines, prefer the bisect:** halve the
search space with every experiment (git bisect for commits, layer bisect
for the stack, header bisect for HTTP, chunk bisect for JS bundles).

---

## 2. The Layer Cake — ports, proofs, and first probes

| # | Layer | Where | Port(s) | Liveness probe (one command) |
|---|-------|-------|---------|-------------------------------|
| 6 | Browser (user) | desktop Chrome/Edge or IAB pane | — | `msedge --headless --dump-dom URL` (see §7) |
| 5 | Portal app | Next.js 16 start/dev | 3001,3010–17 prod; 3020/21 dev | `curl -s -o /dev/null -w %{http_code} localhost:3017/` |
| 4 | Gateway | Kong (DB-less, kong.yml) | 8000/8001 | `curl -s -X OPTIONS localhost:8000/... -H "Origin:..."` preflight |
| 3 | Odoo server | `odoo-bin -c infra/odoo-conf/local.resolved.conf -d fix_dev --dev=all` (host python, **PYTHONPATH=repo root**) | 8069 | `curl -s localhost:8069/web/database/selector` → 200 |
| 2 | Python models | addons/**, libs/py | — | `python -m pytest addons -q` (646+) |
| 1 | Data | PostgreSQL 17 (docker, fix_dev) | 5433 | `docker exec compose-postgres-1 pg_isready -U fix`

Support: Keycloak 8080 · Redis 6380 · Mailpit 8025 · Ceph 9002 ·
residency-stub 8100 · prototype 3030 (pure static — always works).

**Layer bisect recipe:** probe each layer top-down with its one-liner.
The highest layer that answers WRONG (or the lowest that answers RIGHT,
depending on direction) brackets the fault. Everything those probes
don't cover (Kong → Odoo routing, CORS, cookies) is layer 4→3 glue:
test it directly with the gateway probe in §5.

---

## 3. Triage matrix — symptom → most likely layer → first move

| Symptom | Likely layer | First move |
|---|---|---|
| Page "couldn't load" in ZCode IAB pane only | 6 (pane) | Test same URL in desktop Edge headless (§7). IAB pane cannot run prod Next builds (§7.3) — not a code bug |
| Portal 200 but grids show "Failed to load …" | 5→4 glue | Is it CORS/preflight? `curl -X OPTIONS` w/ Origin (§5.2). Then authenticated call via Kong (§5.3). No Odoo login = "Odoo Session Expired" is CORRECT behavior |
| "Illegal invocation" on fetch in browser | 5 | Unbound `fetch` stored as method — wrap in arrow (battle scar #2, §6) |
| Hydration dead (SSR shows, clicks do nothing) | 5 | Check `data-theme` attribute post-load; console via Edge headless `--enable-logging=stderr` (§7.2). If Turbopack build → rebuild `--webpack` (scar #1) |
| API 404 through gateway but works on 8069 | 4 | Kong route missing / `strip_path` default stripped the first path segment (scar #3). Odoo access log shows the STRIPPED path — read it |
| CORS blocked in browser | 4 | Kong cors plugin must echo origin + credentials:true; wildcard `*` is FORBIDDEN with credentials |
| Route TypeError "got multiple values for argument" | 3 | Odoo dispatcher passes EVERY param as kwarg; `pop` positional keys before calling helpers with `**kwargs` (scar #4) |
| Create fails "Missing required value" for a field I set | 3 | Explicit `None` in create() vals OVERRIDES the model default — omit absent keys (scar #5) |
| New controller/module 404 after editing | 3 | **Controllers don't hot-reload** under `--dev=all` on Windows — restart the Odoo process (scar #6) |
| `ModuleNotFoundError: libs.py` at Odoo boot | 3 | Start Odoo with `PYTHONPATH=<repo root>` (scar #7) |
| Float/Decimal TypeError in computes | 2 | Tax engine returns `Decimal`; coerce once at the boundary (`float(sum(...))`) (scar #8) |
| Portal data wrong numbers | 2 | Money is backend-only (AS-09/10). Verify the *controller* field names against the model (`fix.ar.invoice.taxable_amount` NOT `amount_total`) — live-fire it (§5.3) |
| Slow screen | 1→2 | `EXPLAIN (ANALYZE, BUFFERS)` + pg_stat_statements (§8); then N+1 read_group audit in controller |
| Mobile app build/logic issue | Flutter | No Dart SDK on this box — structural validation only (FF-41/42); see §9 |
| Anything "was working yesterday" | git | `git bisect start … bad/good … run <probe>` (§10) |

---

## 4. Tool catalog (what to reach for, by layer)

**Odoo (3/2):**
- `--dev=all` (reload,qweb,xml…) BUT know its limits (scar #6).
- `--dev=pudb` for post-mortem on exception; plain `--debug` = pdb.
- Log pseudo-levels: `--log-level=debug_sql` (every query),
  `debug_rpc`/`debug_rpc_answer` (HTTP payloads),
  `--log-handler=odoo.addons.cd_:DEBUG` (already set in local conf).
- Odoo shell for ORM experiments: `odoo-bin shell -d fix_dev` (with PYTHONPATH).
- UI debug mode `/web?debug=1` for field metadata/view inspection.
- pytest battery `python -m pytest addons -q -o 'addopts='` = the 646+ net.

**Next.js 16 (5):**
- `next dev` (Turbopack OK for dev) vs `next build --webpack` for prod
  (Turbopack prod emits crashing chunks — scar #1; `--webpack` flag exists).
- Hydration truth-test: headless Edge dump (§7.2) — grep `data-theme`.
- `next dev --inspect` for Node debugger attach; React DevTools ext.
- Next DevTools MCP (16.x) for AI-assisted debugging; bundle analyzer
  for size work.
- Remember: `NEXT_PUBLIC_*` bakes at BUILD time (scar #9) — rebuild, don't just restart.

**Kong (4):**
- `docker exec compose-kong-1 kong health`; Admin API :8001.
- `KONG_LOG_LEVEL=debug` + `docker logs compose-kong-1`.
- Config IS `infra/compose/kong/kong.yml` (DB-less, read-only mount);
  apply with `docker exec compose-kong-1 kong reload`.
- Route bugs: check `strip_path` (default true = first path segment gone!).

**PostgreSQL (1):**
- `docker exec -it compose-postgres-1 psql -U fix -d fix_dev`.
- `pg_stat_statements` for offenders; `EXPLAIN (ANALYZE, BUFFERS)`;
  `pg_locks` + `log_lock_waits` for contention; `auto_explain` for plans.

**Cross-cutting:**
- `git bisect run` with any §5 probe as the script.
- Docker: `docker ps` liveness; `docker top` for wedges (CPU ≠ 100% = blocked).
- Observability stack exists (prometheus/tempo/grafana/otelcol in compose) —
  for perf mysteries, prefer traces over guessing.

---

## 5. The probe cookbook (copy-paste, loopback-allowlisted)

All probes honor the estate rule: HTTP(S) only, exact allowlisted host:port,
no redirects to unknown hosts. Server-side fetch code we WRITE must keep
this guard (see any probe file for the `validate()` pattern).

**5.1 Layer liveness sweep**
```bash
for p in 5433 6380 8080 8000 8069 3001 3010 3012 3013 3014 3015 3016 3017 3030; do
  printf "%s:%s " "$p" "$(curl -s -o /dev/null -w '%{http_code}' -m 4 http://127.0.0.1:$p/ 2>/dev/null)"
done; echo
```

**5.2 Kong CORS preflight (exact browser shape)**
```bash
curl -s -X OPTIONS http://127.0.0.1:8000/vendor/purchase-orders \
  -H "Origin: http://localhost:3017" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type" -D - -o /dev/null
# PASS = 200/204 + access-control-allow-origin ECHOES the origin + credentials: true
```

**5.3 Live-fire an API as the browser does (login via gateway → call)**
```bash
python tooling/scripts/livefire-pp5.py          # all 25 portal routes, 45 checks
```
or ad-hoc: `web/session/authenticate` (db fix_dev, admin) via 8000 with
Origin header → then call the portal route with the session cookie.
**Every controller fix must be live-fired** — source tests prove shape,
not behavior (PP3/PP5 audit law).

**5.4 SSR shell check (cheap, no browser)**
```bash
python - <<'EOF'
import urllib.request
html = urllib.request.urlopen("http://127.0.0.1:3010/", timeout=10).read().decode()
assert 'lang="bn"' in html or 'lang="en"' in html
# CFM-01: every hex in rendered HTML must be a token value
import re, pathlib
toks = set(re.findall(r'"(#[0-9a-fA-F]{6,8})"',
         pathlib.Path("libs/ts/ui/src/tokens/tokens.generated.ts").read_text()))
stray = [h for h in set(re.findall(r'#[0-9a-fA-F]{6,8}\b', html)) if h not in toks]
print("stray hex:", stray)   # [] = CFM-01 clean
EOF
```

**5.5 Battery (after any backend fix)**
```bash
python -m pytest addons -q -p no:cacheprovider -o 'addopts=' &&
powershell -File tooling/scripts/tasks.ps1 -Target verify-repo &&   # fitness FF-02..45
powershell -File tooling/scripts/tasks.ps1 -Target test-smoke        # 15 live checks
```

---

## 6. Battle scars — the eight (and counting) that built this skill

Each was found ONLY by live evidence; every one is now regression-locked.

1. **Turbopack prod crash**: `next build` (Turbopack default in 16.3.8)
   emits chunks that throw `(void 0) is not a function` in real browsers;
   Next renders its client error page; curl sees nothing wrong.
   → Prod = `next build --webpack` in all 8 apps. Verify hydration, not 200s.
2. **Unbound fetch**: `this.fetchImpl = opts.fetchImpl ?? fetch` throws
   "Illegal invocation" in browsers. → wrap: `((...a) => fetch(...a))`.
3. **Kong strip_path**: default TRUE strips the first path segment;
   Odoo got `/purchase-orders` → 404. The **Odoo access log** revealed the
   stripped path. → `strip_path: false` on portal routes. Also: the scaffold
   kong.yml had a catch-all `/`→:3000 that served WRONG-BACKEND 404s that
   looked like CORS success. Read the log at the receiving end, always.
4. **Odoo controller kwargs**: helpers taking `brand_id` positionally +
   `**kwargs` → "got multiple values for argument" (dispatcher passes ALL
   params as kwargs). → `kwargs.pop("brand_id", None)` first.
5. **Explicit None overrides defaults**: `create({... "invoice_date": None})`
   kills the model's `default=today`. → build vals dict; add keys only when present.
6. **No controller hot-reload on Windows**: `--dev=all` reloads models,
   NOT new controller modules — 404s until process restart. After adding
   routes: restart Odoo (with PYTHONPATH!), then re-probe.
7. **PYTHONPATH for libs/py**: Odoo host process must start with repo root
   on PYTHONPATH or `from libs.py.fix_events import publish` fails at boot
   (500 on every page).
8. **Decimal in float compute**: tax engine returns Decimal;
   `subtotal - tds` (float − Decimal) TypeErrors only when a
   portal-created record runs the compute. → coerce at the boundary.
9. **NEXT_PUBLIC bakes at build**: `next start` env is irrelevant to
   client code. Changing API base = **rebuild** each app.
10. **Session-expired is not a bug**: portals without an Odoo login show
    styled error states with that exact message — verify WITH a session
    before declaring a data bug.

---

## 7. Browser-layer forensics (the hard-won chapter)

**7.1 The three browser surfaces, ranked by trust:**
1. Desktop Chrome/Edge (user-real) — ground truth.
2. **Headless Edge as an instrument** — reproducible, scriptable:
```bash
MSEDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
[ -f "$MSEDGE" ] || MSEDGE="/c/Program Files/Microsoft/Edge/Application/msedge.exe"
"$MSEDGE" --headless=new --disable-gpu --user-data-dir="$(cygpath -w /tmp/ep)" \
  --virtual-time-budget=12000 --dump-dom "http://127.0.0.1:3017/" | grep -o 'data-theme="[a-z]*"'
```
   `data-theme` present ⇒ hydration ran. Fresh `--user-data-dir` every run
   (stale profiles replay cached error pages!). Budget ≥12s for data calls.
3. ZCode IAB pane — LAST resort, know its limits (7.3).

**7.2 Console capture without DevTools:**
```bash
... --enable-logging=stderr --v=0 --dump-dom URL 2> console.log
grep CONSOLE console.log | grep -viE "GPU|dbus|extension"
```
For in-page traps (works anywhere, even through proxies):
inject FIRST in `<head>`: onerror/unhandledrejection → `document.title`,
then read the title from dump-dom (technique proven on this estate).

**7.3 ZCode IAB pane limits (measured on this machine — don't re-litigate):**
- Cannot fetch >6 script resources per page (prod Next builds = 8–9 → dead);
  substitutes HTML error bodies for chunk fetches; truncates large inline
  scripts (~>600KB). Engine itself is Chromium 146 (modern).
- CAN run: static HTML, the prototype (:3030), inline-only pages,
  **Next dev servers** (3020/3021), Odoo (:8069).
- Prod-portals in the pane failing is NOT a code bug — verify in Edge first.
- Network isolation quirks: reaches `localhost` (not `127.0.0.1`); its
  fetches fail cross-origin (Kong) cleanly.
- If a page must work in the pane: ≤6 script tags, or all-inline via
  the scratch tools (`tooling/scripts/scratch/bisect_proxy.py` repertoire:
  BODYMODE extscript/inlineall/keep:N — the chunk-bisect method).

**7.4 Chunk bisect (when a page dies and you must know which script):**
Serve the page through `bisect_proxy.py` (3019→upstream) and mutate one
variable per run: strip headers → strip script families (external/inline)
→ keep first N src tags → empty chunk bodies. The pane's failure boundary
(6 tags) was found exactly this way. Also `tee_logger.py` to see what the
server ACTUALLY returned to the browser (vs what curl gets).

---

## 8. Data-layer debugging (PostgreSQL / Odoo ORM)

```sql
-- top offenders (if pg_stat_statements enabled)
SELECT calls, round(mean_exec_time::numeric,1) ms, left(query,90)
FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
-- locks right now
SELECT pid, wait_event_type, wait_event, query
FROM pg_stat_activity WHERE wait_event_type IS NOT NULL;
```
- Plan truth: `EXPLAIN (ANALYZE, BUFFERS) <query>;`
- Odoo query log: restart with `--log-level=debug_sql` (never leave on).
- read_group N+1s: count queries per one HTTP call in the log; >50 = smell.
- Seed data rule: dev DB is seeded (`db/seeds/seed.py`, refuses double-run
  exit 2 by design). "Wrong numbers" → check WHICH records (`PP5-LIVEFIRE`
  tag vs SEED- prefix) before blaming logic.

---

## 9. Flutter / Dart layer (structural mode only — no SDK on this box)

- No Dart SDK/Flutter toolchain here: NEVER claim a Flutter fix is verified.
- Structural gates exist and are blocking: `check-dart-offline.py` (FF-41:
  AR-010 mandates in the engine), `check-dart-apps.py` (FF-42: tokens-only,
  one engine, Bengali-first customer app). Run them after any dart edit.
- Offline-engine invariants to preserve while editing: SP-07 upload-first
  order, DI-05 idempotent retry (no firstWhere-without-orElse!),
  §6 two-state conflict disclosure, SP-09 deferred evidence channel.
- First SDK-equipped machine must run `flutter analyze` on all 4 apps
  before any mobile claim closes.

---

## 10. Time-travel & regression locking

- `git bisect start` → `bad` (current) → `good <last-green>` →
  `git bisect run <probe-script>` where probe = any §5 one-liner exiting 0/1.
  With 600+ commits, ≤10 runs — always cheaper than re-reading.
- After every fix: add the regression to the layer's own net (pytest for
  Odoo, fitness check for architecture, livefire for routes) and re-run §5.5.
- Log the incident: one paragraph in `prototype_porting/ITERATIONS.md`
  (symptom → layer → cause → fix → proof). Future debuggers read it first.

---

## 11. Anti-patterns (each line is a scar)

- Trusting `curl 200` as "the page works" (it never sees hydration).
- Fixing CORS by disabling credentials or adding wildcard `*`.
- Restarting Odoo "to be sure" without capturing the failing request first.
- Debugging Kong by reading kong.yml only — the RUNNING config may be a
  stale container mount; `kong reload` after edits, then re-probe.
- Believing the IAB pane over desktop Edge (see §7.3 — pane is the least
  trustworthy surface).
- `firstWhere` without `orElse` on retry paths (DI-05 crash — PP4 scar).
- Skipping the battery because "it's just a small fix" — scars 3,4,5,8 were
  all "small fixes" until they weren't.
- Leaving diagnostic servers running on scratch ports (3018/3019/3021/3022)
  — kill them; they confuse the next session's port sweep.

---

## 12. When you're stuck (the escalation ladder)

1. Re-read the exact error STRING — grep the codebase for it verbatim.
2. Reproduce with maximum verbosity at the failing layer (debug_sql /
   KONG_LOG_LEVEL=debug / Edge console / pytest -x).
3. Bisect a different axis: layer → commit → header → chunk → record.
4. Build the smallest reproducer OUTSIDE the estate (scratch probe) —
   if it fails there too, the bug is in a dependency/assumption, not your code.
5. Compare against the last known good: `git bisect`, or docker image tags.
6. Only then: hypothesize a NEW mechanism, and design the experiment that
   would DISPROVE it (Popper, not confirmation).

References (deeper runbooks): `references/odoo.md`, `references/next.md`,
`references/gateway.md`, `references/data.md`, `references/browser.md`,
`references/mobile.md` in this skill folder.

Sources (2025–26 research baked into this skill):
systematic debugging frameworks ([navid.tr](https://blog.navid.tr),
[ideafloats.com](https://blog.ideafloats.com)); Odoo `--dev`/log pseudo-levels
([Odoo 18 CLI guide](https://www.scribd.com), [fundamentos-de-odoo](https://fundamentos-de-desarrollo-en-odoo.readthedocs.io));
Next.js 16 Turbopack/DevTools-MCP ([tapflare.com](https://tapflare.com));
Flutter DevTools ([docs.flutter.dev](https://docs.flutter.dev), [glukhov.org](https://www.glukhov.org));
Kong `log_level`/Admin-API practice ([developer.konghq.com](https://developer.konghq.com),
[Kong #8399](https://github.com)); PostgreSQL pg_stat_statements/EXPLAIN
([pganalyze.com](https://pganalyze.com), [postgresql.org](https://www.postgresql.org/docs/current/pgstatstatements.html), [dev.to 7 ways](https://dev.to));
git bisect ([blog.git-init.com](https://blog.git-init.com), [plainconcepts.com](https://www.plainconcepts.com)).
