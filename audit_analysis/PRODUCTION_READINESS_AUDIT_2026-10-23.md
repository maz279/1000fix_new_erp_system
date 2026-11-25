# 1000FiX ERP — Production-Readiness Audit (2026-10-23)

> **Update after same-day remediation (§5a):**
> - **Fixed in code:** the critical security holes, the fabricated business outputs, the mock portal pages and the data defects listed in §3 are fixed in the working tree.
> - **Tests:** 5,087 pass with 0 failures.
> - **Verdict unchanged — still not deployable.** The external dependencies, missing infrastructure, mobile apps, missing engines and unmet gates are listed under "Still open" in §5a.

**Verdict: NOT production-ready. Not deployable.** No roadmap gate passes. The code base is
substantial and much of it is real, but it contains fabricated business outputs, critical
authorisation holes, simulated integrations, and unconfigured production basics. Every
R11 "cutover / go-live / decommissioning / benefits" claim describes events that have not
happened.

Scope: `roadmap/Revise_roadmap` (11 phases, 55 milestones) vs `1000_fix_codebase`
(71 `cd_*` Odoo 19 addons, 23 services, 8 Next.js portals, 4 Flutter apps). Method: read
every roadmap file; ran Odoo against `fix_dev` and swept all 196 custom menus via RPC;
opened the portals in a browser; ran test suites; five parallel code audits; every
critical finding below was re-checked by hand (file:line).

---

## 1. Roadmap status (55 milestones)

| Class | Count | Milestones |
|---|---|---|
| Done in code, runnable | ~5 | R01-M04, R02-M01, R07-M01 (local only), R10-M01, R08-M01 (arguably) |
| Partial (real code, below gate depth) | ~34 | most of R01–R10 |
| External / not possible in a repo, or fabricated | ~15 | all of R11, R10-M05, R08-M05, R01-M01, R04-M03 … |
| Docs only | 1 | R07-M02 |

- **Gates** (`tooling/gate/evidence/gate-*-latest.json`): none pass. G0a, G0b, G2, G7, G8 and G9 are **RED**. G1a, G1, G3, G4, G5 and G6 are **CONDITION**.
- **Git**: committed history ends at R05-M03 (`5e637b4464`). Everything from R05-M04 to R11 sits in **2,265 uncommitted paths**, so it is unversioned.
- **R07–R11 bodies say `[COMPLETED]`, but their own frontmatter says otherwise.** For example, R11's frontmatter reads "NOT EXECUTED… no production cutover has occurred". The R11 body still claims all of these:
  - 53/53 branches live
  - a 380-employee payroll paid by BEFTN
  - ৳81.22M monthly revenue
  - an ISO certificate number
  - a Mushak filing
  - a named Head of IT

  None of it happened. The summary audits for R11-M01..M04 all report FAIL.
- **Fabricated approvals that are still live, not quarantined:**
  - `docs/governance/GV-003-production-readiness-go-decision.md` (a "unanimous GO" with seven named voters)
  - `BM-2026-10-D001-charter-and-governance.md` (a board minute)
  - `DEP-31-legal-opinion-pdpa-residency.md` (a legal opinion)
  - `docs/p01-m08/SoW-F08-signed-amendment.md`
  - `v1.0-scope-completion-statement.md` ("100% UNCONDITIONAL PASS")
  - `r11-m01-cutover-runbook.md` (named approvers)
  - `aut-60-automation-register-report.md` ("100% Certified", but 0 of 60 engines are deployed)
  - `r04-m02-loyalty-redemption-report.md` ("stub permanently closed", but the code still returns `stub_active: True`)
- **`1000_fix_codebase/README.md:13-16` overclaims**: it marks R10-M02 and R10-M04 COMPLETED, but their summary audits say FAIL.

## 2. Runtime checks (this session)

| Check | Result |
|---|---|
| Odoo 19 boots on `fix_dev`; 142 modules / 71 `cd_*` installed | PASS (only with `PYTHONPATH=<repo>` — 87 addon files import `libs.py`; the project `.venv` is **empty**, Odoo deps live in global Python) |
| 196 custom menus: action + views + sample read | 191 OK; **5 Field Service menus visible to admin but raise AccessError** (menus not group-restricted) |
| Empty screens | 30 (Chart of Accounts, Workshop repair orders, Loyalty, Consolidation, Compliance, HSE …) |
| Company setup | **3 companies, all Odoo demo ("My Company (San Francisco)") in USD/US; BDT not even active**; demo user "Mitchell Admin"; approvals queue full of Odoo demo activities ("Eat cookies", "5 VP Chairs") |
| Service-order numbering | **825 of 920 orders named `NEW`** — field default `next_by_code(...) or "NEW"` (`cd_service_order/models/fix_service_order.py:72`), no uniqueness constraint |
| Dashboard "Revenue MTD" | shows **৳ -200.3**: the code fix exists (`fix_estimate.py:113-127`), but a pre-fix negative estimate remains in the DB |
| Schema | `fix.withholding.certificate.supplier_name` missing NOT NULL |
| Analytics portal (:3002) | Backend replies `Session expired` (portal has no login); page silently renders hard-coded `DEMO_KPIS` (12,480 orders vs 920 real) under a "live" label — `apps/web/analytics/app/page.tsx:85,278-291` |
| Seller portal disputes | renders hard-coded `DEMO_DISPUTES`; form only edits local state |
| Customer portal | real bookings from Odoo, but shows `NEW` refs and smoke-test text ("PP5-LIVEFIRE …") |
| Vendor portal `next build` | PASS; `tsc --noEmit` PASS in all 8 portals |
| Services/libs tests | 1,675 passed, 2 skipped |
| Addon tests | see §6 |

## 3. Critical defects (deployment blockers, all verified by hand)

### Security
1. **Unauthenticated technician relay.** `apps/web/customer/app/api/technician/[...path]/route.ts:42-53` attaches the server-side `FIX_TECHNICIAN_API_KEY` to any request, and accepts requests that send no `Origin` header. Anyone can clock in, change job status or consume van stock, and every technician shares one identity.
2. **One-click admin/admin login on the public customer portal.** See `customer/components/auth-modal.tsx:110-111,473`. Corporate also pre-fills admin/portal/demo personas.
3. **OIDC client secret shipped to the browser.** `NEXT_PUBLIC_OIDC_CLIENT_SECRET` is read at `corporate/lib/auth.ts:165`, and the flow has no `state` or PKCE. A Keycloak login never creates an Odoo session, so SSO users cannot load data.
4. **Six portals have no authentication**: analytics, seller, brand, agent-console, partner and vendor.
5. **Kong has no auth plugin.** Only cors, rate-limiting and response-transformer are configured. It routes nothing except Odoo, and the customer portal bypasses Kong entirely.
6. **The identity-lifecycle `POST /consume/once` endpoint is unauthenticated.** I verified HTTP 200 without credentials. The endpoint can disable or provision Keycloak users.
7. **P03 staff APIs need only a logged-in user.** They have no internal-staff check and make 12 `sudo()` calls across companies (`cd_p03_portal/controllers/p03_service_order_api.py`). Because any phone number can become a portal user through OTP, anyone could read all customers, orders and technician GPS positions.
8. **Portal customers have ORM write and create rights on `fix.service.order` and write rights on `fix.estimate`** (`cd_customer_portal/security/ir.model.access.csv:4-5`). The QC gate exists only in `action_ready`, so `write()` and `/p03/order/advance_stage` bypass it.
9. **Overly broad access rights.** Payroll, payslips, BEFTN batches, tax returns, the commission ledger, and the RBAC/SoD tables can be read and written by every internal user (`base.group_user`; e.g. `cd_payroll_bd/security/ir.model.access.csv:2-4`). The 53 roles map to no groups, and field rules are never enforced.
10. **Vendor portal IDOR.** `_vendor_domain` returns `[]` (`cd_vendor_portal/controllers/vendor_api.py:43-49`), and vendors can self-record receipts, which defeats the three-way match.

### Fabricated business outputs
11. **Consolidation inserts a hard-coded ৳50,000 "management fee" elimination** whenever no inter-company transactions exist (`cd_multi_entity/.../fix_consolidation.py:220-238`). IC eliminations also reduce consolidated profit.
12. **TDS return filing mints its own NBR acknowledgement** (`"NBR-TDS-%s-%04d"`, `fix_tax_returns.py:435`). VAT sub-ledger reconciliation compares the return with itself (`:323-326`), and a test locks that behaviour in.
13. **Payout read-back takes its outcome from the caller** (default CONFIRMED) and invents transaction ids (`int007_rail.py:453-509`). Generating the BEFTN file alone marks a payout confirmed and posts the GL (`fix_settlement_ext.py:596-602`).
14. **Payment `confirm()` credits money without asking the gateway**, and its idempotency store is a process-local dict (`payment_connectors.py:406-441`). All four gateways send one generic JSON POST, which is not the real bKash, Nagad or SSLCOMMERZ protocol.
15. **The chatbot's "grounded" answers are fixed strings.** It tells every customer their repair is complete and in QC, that bookings and invoice dispatches happened, and it counts those replies as AI resolutions (`cd_contact_centre/.../assistant_engine.py:476-499`).
16. **Data-wipe certificates are fabricated**: hard-coded sector count, status "verified", and a hash computed from the name plus a timestamp (`fix_data_case.py:372-403`). Trade-in creates them automatically.
17. **Dashboards show placeholder figures as if they were measured:**
    - MDM quality defaults to 95/98.5/99.
    - Seller tier is computed from default KPIs (0.95/0.92/4.8).
    - Partner commission is a constant 500.
    - The analytics `/governance/*` and `/analytics/kpis/register` routes serve static JSON from `docs/`.
    - Storefront marks orders paid with a made-up `TRX-<timestamp>` reference.

### Finance, tax and payroll correctness
18. **AR invoices create no `account.move`.** Mushak 6.3 numbering uses `search_count+1`, which is racy and never resets.
19. **Mushak 9.1 lumps every row into the 15% standard rate.** The VAT tariff table is never read, and input VAT defaults to 0.
20. **Payroll reads five contract fields that do not exist** via `getattr` (`fix_payroll.py:180-196`). As a result, everyone is taxed as general/Dhaka with no rebate.
21. **Payroll tax rules have three problems:**
    - The ITA-2023 salary exemption is not applied.
    - One-off overtime is annualised ×12.
    - The tax-free thresholds mix fiscal years.
22. **Inventory consumption never posts COGS.** Suspense is "reconciled" by a status write, the financial-report generator writes the constant `{"status":"computed"}`, and fixed-asset depreciation never posts to the GL.

### Integrations and infrastructure
23. **The live event consumer reads an in-memory mock stream** unless `FIX_EVENT_BUS_LIVE=1`, and the container cannot import `kafka`. `fix_events.consume()` is a no-op, so leaver deprovisioning never fires.
24. **There is no OpenTelemetry export.** The hand-rolled tracer keeps spans in an unbounded list.
25. **The OpenAPI contracts do not match any implemented service route**, and security is never applied to any operation.
26. **Offline mode and the mobile apps are not real:**
    - The SQLCipher offline store is in-memory `List`/`Map` (`libs/dart/fix_offline/lib/src/sqlcipher_journal_store.dart:40-51`).
    - All four Flutter apps are single-file UI scaffolds with no HTTP client.
    - The customer app's SSO login is a `Future.delayed`.
27. **Several services have no working engine:** OCR, STT, conversational-ai (whose benchmark numbers are hard-coded) and document-generation (which reports "rendered" without rendering).
28. **The deployment path is incomplete:**
    - `infra/k3s` and `infra/terraform` are empty.
    - `docker-compose.prod.yml` contains only postgres, redis and odoo: no portals, services, Kong or Keycloak.
    - Every service Dockerfile refuses to start outside local or staging.
    - notification-dispatcher binds 127.0.0.1 inside its container, so its published port is dead.
    - rmm-collector is hard-locked to `localhost:8069`.
29. **Portal Docker images bake in localhost API and CSP defaults**, because `Dockerfile.portal` passes no `NEXT_PUBLIC_*` build args. Login also hard-codes `db="fix_dev"`.

### Mock pages that look live (about 11 of 33 portal pages)
- **Seller**: quotes, disputes, statements, and KYC onboarding (which "verifies" via `setTimeout`).
- **Partner**: leads and attribution.
- **Analytics**: the whole dashboard falls back to demo data.
- **Agent console**: falls back to demo data, and reports success when writes fail.
- **Corporate tender page**: names real Bangladeshi companies, shows a "G4-03 Evidence Verified" pill and a static ৳4.44 crore, and its backend route `/corporate/tenders` does not exist.

## 4. What is genuinely solid

- **Odoo estate**: all 71 addons install and load. Manifests resolve, every model has ACL rows, and none of the 196 menu views is broken. Company and operating-unit record rules exist in most modules.
- **Real logic**:
  - service-order state machine, warranty gate and idempotency
  - field-service routing (haversine/OSRM with 2-opt)
  - warranty claims, quotation and contract core
  - customer OTP and storefront session hardening
  - the technician bearer API itself
  - the Decimal tax and payroll engines (correctness gaps listed above)
- **Portals that are really wired to Odoo**: customer (except the relay), the corporate core pages, vendor and brand, plus the core pages of seller and partner.
- **Services**: the telemetry collector (Go, real pgx inserts) and the evat-adapter (fails closed).
- **Quality checks**: the `tsc` checks and the service test suites are green.
- **Honest self-audit**: the 2026-10-22 audit quarantined many fabrications and fixed several defects (STT echo, ML metrics, telemetry flush, DSR adapter, negative estimates, the route optimiser).

## 5. What "100% ready" would require (in order)

1. **Remove fabrications.**
   - Quarantine or retract the live governance and approval documents listed in §1.
   - Strip the `[COMPLETED]` text from the R07–R11 bodies and correct `README.md`.
   - Remove every hard-coded business output listed in §3 items 11–17 and the mock portal pages.
2. **Close the security blockers** (§3 items 1–10): the relay, default credentials, the OIDC secret, portal auth, Kong JWT/OIDC, service auth, the P03 staff check, the portal ACLs, and finance/payroll group scoping.
3. **Fix finance correctness** (§3 items 18–22) and pass the 100% financial-coverage gate. Coverage is currently 72.7% for financial code and 34.7% for payroll.
4. **Make the deployment path real.**
   - Set up the 1000 FiX company in BDT and Bangladesh, and run without demo data.
   - Fix the "NEW" numbering.
   - Write a production compose or k8s definition covering all components.
   - Fix the project `.venv`.
   - Commit the 2,265 changes and get a real CI run.
5. **External items** (not code): real gateway and NBR credentials, bank BEFTN, an independent pentest, Board and Steering decisions, data migration with sign-off, and cutover.

## 5a. Remediation applied the same day (2026-10-23, uncommitted)

Every item below was changed in the working tree, verified by tests and, where marked, live against the running stack. Nothing is committed.

| § 3 item | Fix | Verified |
|---|---|---|
| 1 Technician relay | Requires a same-origin POST and an internal Odoo session (`/web/session/get_session_info`). The bearer key works only when the session belongs to the key's own technician. | Live: no Origin → 403; no cookie → 401; forged session → 401 |
| 2 admin/admin and personas | Removed from the customer and corporate portals, with no environment back door. Inputs start empty. | grep + build bundles |
| 3 OIDC secret | Token exchange moved server-side (`app/api/auth/{login,callback}`) with PKCE S256 and `state` in httpOnly cookies. Uses a non-public `OIDC_CLIENT_SECRET`, and no `NEXT_PUBLIC_*SECRET` remains. | curl matrix (agent) + grep |
| 4/5 Portal and gateway auth | `kong.prod.yml` adds a JWT (RS256, Keycloak issuer) for staging and production. **It is not active**: portals still use Odoo session cookies and must send Keycloak bearer tokens before it is switched on. | Both YAML files parse |
| 6 identity-lifecycle | `X-Identity-Lifecycle-Token`, compared in constant time. Outside local, the endpoints return 503 when no token is set. | Tests |
| 7 P03 APIs | `_require_internal` on all 12 routes. sudo reads are fenced to the user's companies. Clients get generic errors. `advance_stage` goes through `action_ready`. | Tests |
| 8 Portal ORM write and QC gate | Customer-portal ACLs are read-only, with own-record rules. The QC gate is enforced in `_validate_transition`, so every `write()` path to `ready` passes through it. | Tests |
| 9 Finance and payroll ACLs | New payroll officer and manager groups; plain employees have no payroll access. Tax, settlement, GL and billing writes are restricted to `account.group_account_user`/`manager`. RBAC and outbox tables are read-only for employees. The SoD context bypass is removed. | Tests, both DBs upgraded |
| 10 Vendor IDOR | Scoped to `commercial_partner_id`; vendors can no longer record receipts. | Tests |
| 11 Consolidation | The 50,000 elimination is removed. Eliminations no longer reduce profit. P&L is year-to-date. The self-minted nil-return acknowledgement is removed. | Tests |
| 12 Tax | The TDS and nil-return acknowledgements must be entered by the user. The VAT reconciliation is computed from posted GL. Mushak 9.1 is classified by treatment. The e-VAT declarant must be a real configured officer, not a fake NID. | Tests |
| 13 Payout | The library read-back requires the bank's outcome and reference. No transaction ids are invented. A BEFTN file stays UNKNOWN until the bank confirms. In Odoo, BEFTN generation reaches `file_generated`, and confirmation needs a bank reference. Account lookup is fail-closed. | Tests |
| 14 Payment confirm | Credits only after the connector's `query()` confirms and the amounts match; otherwise the payment is `unverified`. Documented as not provider-certified, with process-local idempotency. | Tests |
| 15 Chatbot | Order status, price and branch answers are grounded in real records or handed off. Nothing claims a booking or invoice dispatch happened. Only grounded answers count as AI-resolved. | Tests |
| 16 Wipe certificates | Operator evidence (log, sector count, method) is required. The certificate starts `pending_verification`, and its hash covers the evidence. Trade-in, data-case purge and e-waste recycling all require a verified certificate. | Tests |
| 17 Fake KPIs | MDM scores are measured or `no_data`. Seller KPIs are measured, defaulting to `unrated`. Partner commission is rate × base. The storefront needs a real gateway reference. Campaign PDPA consent is filtered at launch. Loyalty redemption is validated, with no stub. | Tests |
| 18 Mushak numbering | Gapless `ir.sequence` per company with a fiscal-year reset. | Tests |
| 20 GL report and suspense | A real trial balance, P&L and balance sheet are built from posted lines. Suspense reconciliation requires a balancing posted move. Close steps need evidence. | Tests |
| Mock portal pages | All `DEMO_*` data removed. Pages are wired where a backend exists; otherwise they show an honest unavailable state (seller dispute filing, KYC submission, partner leads, corporate tender). Analytics shows a sign-in message instead of fake KPIs. | Live (analytics) + builds |
| `NEW` order numbers | 825 orders renumbered (pre-migration). Numbering fails closed and `UNIQUE(name)` is enforced. | DB: 920 rows, 920 distinct names |
| Company setup | The main company is bootstrapped to *1000 FiX Services Ltd.*, BDT, Bangladesh. | Live dashboard |
| Discuss hijack | The override is removed and a migration restores Odoo's Discuss app. | DB |
| Data repairs (dev DB) | Estimate #4 (−200.30, no lines) is marked rejected with a chatter note. The NULL `supplier_name` was backfilled from its linked vendor bill. | Dashboard shows ৳0; schema warning gone |
| Fabricated documents | 15 governance and traceability docs carry a provenance banner. The 2 competing G1/G1a "latest" files are quarantined. The R07–R11 roadmap bodies are warned. README R10 rows are corrected. | grep |


### Second remediation round (same day)

| Item | Fix | Verified |
|---|---|---|
| Six portals without login | Analytics, seller, brand, agent-console, partner and vendor now have an Odoo-session sign-in gate. Inputs start empty, there are no personas, and the db name comes from env. Analytics and agent-console are staff-only. Expired sessions return to the sign-in screen, and a sign-out button is provided. | tsc + build ×6. Live in the browser: the seller portal sign-in screen, a successful local sign-in, then the backend's real "no seller profile — complete KYC" response |
| Production deployment definition | Full stack in `docker-compose.prod.full.yml`: odoo, postgres, redis, keycloak, kong, the 8 portals and 4 services. All secrets are required, there are healthchecks, and only Kong is published. Also added: `infra/k3s` (Kustomize base and production overlay, 62 objects, default-deny NetworkPolicies), `infra/terraform` (DigitalOcean sgp1: VPC, DOKS, managed Postgres and Valkey, optional Kafka, Spaces, registry) and `infra/README-production.md`. The portal image's static-asset 404 bug is fixed. | `docker compose config`; `kubectl kustomize`; `kong config parse` → parse successful; Odoo, portal and service images built and run |
| identity-lifecycle could not start in prod | `check_environment` accepts prod/production. Its ops endpoints stay closed without a token. The compose and k8s gates were removed. | Tests |
| Event bus could not reach a production broker | `kafka-python-ng==2.2.3` added to `uv.lock` (nothing else moved), the Odoo image and the identity-lifecycle image. `fix_events` gained `KAFKA_SECURITY_PROTOCOL`/`KAFKA_SASL_*`/`KAFKA_SSL_CAFILE` and refuses a half-configured setup. Compose and k8s wire them from `fix-kafka`. | New tests. Inside the Odoo prod image: `kafka 2.2.3`, SASL_SSL resolves |
| Prod Kong JWT rejected every portal call | Portal JSON-RPC routes are authenticated by Odoo (session cookie, Odoo API key, P03 staff check), with Kong doing CORS, rate limiting and size limits. JWT stays on `/api/odoo` (API host) and `/svc/*`. | `kong config parse` → parse successful |
| Chart of Accounts empty | MD-035 loaded through the module's own loader into **fix_dev only**: 79 accounts, 60 postable, sha256 recorded. MD-035 is still **Draft**, awaiting CFO approval, and production needs the approved version. | DB count |

**Final test run:** `addons services libs tests tooling/tests` → **5,146 passed, 2 skipped, 0 failed** (10 min 16 s).

### Still open after remediation (cannot be closed in code, or not yet done)
- **External items:** real bKash, Nagad and SSLCOMMERZ protocols and credentials; NBR IVAS access; bank BEFTN/read-back integration; independent penetration test; Board and Steering decisions; signed contracts; legacy data migration with business sign-off; production cutover. **No gate (G0a–G9) can pass until these exist.**
- **Infrastructure — mostly resolved, still unproven against a real environment:** compose, k3s and Terraform definitions now exist and validate locally. Nothing has been deployed to a real cluster: `terraform validate` was not run because Terraform isn't installed, and there was no server-side Kubernetes dry-run. TLS, DNS, registry push, the real residency service and Kafka credentials are still external.
- **Mobile:** all four Flutter apps are UI shells with no HTTP layer, and the SQLCipher store is in memory.
- **Engines that don't exist:** OCR, STT, conversational AI, document rendering, the ML models, and OpenTelemetry export.
- **Functional gaps now shown honestly:** seller dispute filing and KYC submission, partner leads and attribution, corporate tenders, certified seller statements.
- **Technician identity:** one technician key per deployment; per-technician identity needs a backend change.
- ~~**Six portals without login**~~ — resolved in the second round.
- **Content and master data:** the CoA is loaded in dev from the draft MD-035; CFO approval of MD-035 and the rest of the MD-* set is still needed. The remaining empty screens are transactional data, not defects.
- **Coverage gate:** the 100% financial coverage gate and the 80% estate gate are unmet.
- **Dev DB:** still contains Odoo demo data (production config sets `without_demo = all`). The project `.venv` is still empty.
- **2,329 uncommitted paths:** nothing from R05-M04 onward is versioned, and CI has never run on a real runner.

## 6. Test runs

- services + libs/py: **1,675 passed, 2 skipped, 0 failed** (system Python 3.12.10; project `.venv` empty).
- addons (pytest, `--import-mode=importlib`, live `odoo_env` fixture): **2,786 passed, 0 failed** (8 min 5 s).
- **Green does not mean correct.** Several tests assert the fabricated behaviour itself:
  - `test_tax_engine_orm.py:469-476` covers the self-compare VAT reconciliation.
  - `test_gl_ext_orm.py:554` covers the constant financial report.
  - `cd_partner/tests/test_partner_live.py:102` covers the 500.0 commission.
  - `test_multi_entity.py:28-34` runs on `MagicMock`s.
- Many other tests only check that a class exists.
- Coverage is 56% for the estate, 72.7% for financial code and 34.7% for payroll. The gate requires 80% for the estate and 100% for financial and tax code.

**After remediation**:
- **Full estate** (`addons services libs tests`): **5,087 passed, 2 skipped, 0 failed**, in 10 min 40 s.
- **cd_p03_portal**: re-run after its final change, 122 passed.
- **Portal builds**: all 8 `next build` runs succeed.
- **Odoo**:
  - The menu sweep finds 0 broken screens visible to admin.
  - No schema warnings remain.
  - Changed modules are upgraded on `fix_dev` and `fix_test`.
