# M62 Data Platform, Warehouse & Governance: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M62 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/J_Data_Analytics_and_Intelligence/M62_Data_Platform_Warehouse_and_Governance.md`. Sections used:
  - §3: scope (19 capabilities) and boundaries (M25 renders, M26 consumes features, M29 owns the classification scheme, M33 the erasure request, M63 the approvals);
  - §5: FR-DAT-001 … 038;
  - §8: the data journey, the metric definition lifecycle and the quality incident;
  - §9: BRU-DAT-01 … 24;
  - §10.1: the 23 owned entities;
  - §11: AUT-DAT-01 … 20;
  - §13: roles and segregation of duties.
- Code:
  - `cd_p03_portal/static/src/a11/m62.js`: the page registry (7 sub-module pages);
  - `cd_p03_portal/controllers/a11/m62.py`: surfaces, write whitelist, reports and KPIs;
  - `cd_metric_registry/models/fix_data_platform.py` and `fix_metric_registry.py`: pipelines, runs, contracts, metric definitions, versions and consumers, quality rules and tests, incidents, retention, declassification, entities and lineage.
- Live data (fix_real, read-only count on 18 Nov):
  - 5 entities, none mapped to an Odoo model and all in layer "none", so **none of the 3 quality rules can be measured** (no check field either);
  - 4 pipelines, 0 runs; 3 contracts "active" with **no producer signature**; 5 metric definitions "published" with **0 versions**: all are seed rows written before the A11 controls existed;
  - no lineage, test, incident, consumer, declassification or disposition evidence; 6 sensitive fields (M29); 0 erasure requests in M33;
  - the Data Governance Officer group has 1 holder (the development admin).

## 1. What was there (HEAD 32e24dc9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Ingestion | Data Pipeline | **none** | **No data source register** (spec §10.1 `fix.data.source`, FR-DAT-001…004, BRU-DAT-09): a pipeline named its source in free text, with no owner or steward. Pipelines had **no layer and no dependencies**, so "a downstream model never runs against a failed upstream load" (FR-DAT-008, AUT-DAT-01) could not be stated. The page lists runs (Replay & Backfill) with no chip, and a backfill had **no period and no reason** (FR-DAT-006, AUT-DAT-16, BRU-DAT-24). |
| 2 | Medallion & Transformation | Pipeline Run | **none** | Any run could land in Silver or Gold with **no active data contract** for the entity (BRU-DAT-10 H). A finished run's rows and stage could be **rewritten after the fact**. |
| 3 | Dimensional Model | Data Entity | **none** | **No conformed dimension** (FR-DAT-010/011: natural key, SCD type, history-tracked attributes). **No declared grain** on a fact (BRU-DAT-08 H). The entity form had **no Odoo model and no warehouse layer**: an entity captured in the workspace could never be measured by a quality rule or counted by a disposition, and the S3 layer guard (BRU-DAT-11) had nothing to act on. |
| 4 | Semantic Layer | Metric Definition | Data Contract, Metric Definition | **Metric versions, the only path to publication, were on no screen and no form**, and their write whitelist was empty: **no metric could be published from the workspace.** The **consumer register** was on no screen either, and **retiring a metric ignored it** (BRU-DAT-04 H). A published definition's formula could still be **edited in place** on the form while tiles resolved the version's text: two definitions of one number (BRU-DAT-01/02 H). A later version needed **no reason** and listed **no impact** (FR-DAT-019 P0, AUT-DAT-08). **No business glossary** (FR-DAT-022). The contract list offered **no Producer Sign or Request Activation** button, so no contract could be activated from the workspace either. |
| 5 | Quality & Observability | Quality Rule | Quality Test | Incidents listed with **no chip**. The rule form had **no check field, freshness window or severity**: a rule created in the workspace could never be measured (the runner skips it), and an incident's severity could not follow the rule (FR-DAT-024). **Measure Now** was served but offered on no list. |
| 6 | Catalogue & Lineage | Data Lineage | **none** | The catalogue (entities) and the glossary were not on the page; the lineage form had **no transformation** field. |
| 7 | Security & Cost | **none** | **none** | **The page captured nothing.** Its mapped list is M29's sensitive-field classification (`create: false`), so the existing Retention Policy form was reachable from no page. **Declassification authorisations** (the only way to lower a classification, BRU-DAT-11 H) were served by the API with **no screen and no form**. **No erasure propagation** (FR-DAT-036 P0, BRU-DAT-15 H, AUT-DAT-13). The retention list offered **no Request Shortening or Run Disposition** button; disposition evidence was on no screen. |

Several forms also let a person type the **state** (contract, metric, pipeline, run, incident); the server silently dropped it on create, so a user who picked "Active" got a draft without being told.

Guard `cd_p03_portal/tests/test_m62_capture_buttons.py` on HEAD: **23 of 46 tests fail.**

## 2. What was built

### Backend: `cd_metric_registry` 19.0.0.2.0, new file `models/fix_m62_capture.py` (imported last)

The governance rule book stays the Data Governance Officer's (plain users read only). States, stamps and measured figures are never typed through a form.

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.data.source` (spec §10.1, FR-DAT-001…004) | Code, name, source type (CDC, domain events, batch, file, API), producing module, connection reference, business owner, technical steward, active from. | Registered as a draft by an officer and **activated only with a business owner and a steward (BRU-DAT-09)**. A connection reference that **looks like a credential is refused** (password=, token=, user:pass@): it names the vault entry only. Retiring is refused while an active pipeline uses the source. Never deleted. |
| 1 | Pipeline (extended) | Data source, medallion layer, pipeline owner, **"runs after" upstream pipelines**. | A pipeline ingests only from an **active** source (the source system defaults to its code). No dependency cycle. **A run is refused while an upstream pipeline's latest load failed, is still running or never succeeded (FR-DAT-008, AUT-DAT-01).** |
| 1-2 | Run (extended) | Period from/to, the run it replays, reason. | **A backfill or replay states its period and its reason (AUT-DAT-16, BRU-DAT-24); a replay names a concluded run of the same pipeline.** **A Silver or Gold load is refused while the entity has no active data contract (BRU-DAT-10).** **A concluded run is history:** its rows, stage and terms are no longer edited (the state keeps its own "Finish or Fail" refusal). |
| 3 | Entity (extended) | Model role (fact, dimension, reference, other), declared grain. | **A fact declares its grain (BRU-DAT-08).** The Odoo model, when given, must exist. |
| 3 | `fix.data.dimension` (FR-DAT-010/011) | Catalogue entity, natural key, surrogate-key strategy, slowly-changing type, history-tracked attributes, attribute list, master-owning module, the facts that use it. | **Type 2/3 name the attributes they track.** A fact is not a dimension; only facts use one. One dimension per entity; the entity takes the dimension role. |
| 4 | Metric definition (extended) | — | **Once published, the code, formula, grain and source change only by publishing a new version (BRU-DAT-02)**, and publishing a version **copies its text onto the definition**, so there is one definition of the number (BRU-DAT-01). **Retiring is refused while a registered consumer remains (BRU-DAT-04).** |
| 4 | Metric version (extended) | Reason for the change; consumers reached (impact). | **The server numbers versions.** **A version after the first records why (FR-DAT-019)** before it is routed. **The request stamps every registered consumer (AUT-DAT-08)**, and publication notes them on the version. **A steward-reviewed text is frozen.** |
| 4 | Metric consumer (extended) | Consumer type (dashboard, report, API, ML model, portal, module). | — |
| 4, 6 | `fix.glossary.term` (FR-DAT-022) | Term in English and Bengali, plain meaning in both, business owner, synonyms, related metrics and datasets. | **One meaning per term** (case-insensitive) per company; an owner is required. |
| 5 | Quality rule (extended) | Incident severity. | **A check field must be a column of the entity's model**, else the runner could never measure the rule. **A failing rule opens its incident at the rule's own severity** (FR-DAT-024); without one, the old derivation holds. |
| 7 | Declassification authorisation (extended) | — | The "from" class **is the entity's current classification** (defaulted, and a different one is refused). |
| 7 | Retention policy (extended) | — | Named after its entity (it was "New"). |
| 7 | `fix.data.erasure` (spec §10.1 erasure request, FR-DAT-036, BRU-DAT-15, AUT-DAT-13) | The M33 erasure request and its party, the statutory due date, five layer ticks (Bronze, Silver, Gold, feature store, extracts), evidence, note. | **Opened automatically when the DPO starts an M33 erasure request**, or by an officer for one in hand; only for an erasure request, one per request. **Completed by an officer only with every layer ticked and the evidence named**; completion is final and is noted on the M33 request. **No plain-user access at all** (it names a person); DPOs read it. Never deleted. |

Security and data: ACL rows for the four new models (officer writes, plain users read the source, dimension and glossary, nobody unlinks a source, glossary term or erasure); company rules from `generate-isolation-rules.py` (only the `cd_metric_registry` file kept, the generator's drift in six other modules reverted); sequence `ERA/`; manifest now depends on `cd_party_master`.

### Workspace: `a11/m62.js` and `controllers/a11/m62.py`

- Eight new lists, on their pages and in the navigation: Data Sources, Conformed Dimensions, Metric Versions, Metric Consumers, Business Glossary, Declassification Authorisations, Analytical Erasure, Disposition Evidence (read-only).
- Seven new forms (tabbed per AGENTS.md): Data Source, Conformed Dimension, Metric Version, Metric Consumer, Glossary Term, Declassification Authorisation, Analytical Erasure. Existing forms gained the fields that make the record work: entity (Odoo model, layer, model role, grain, description), rule (check field, freshness window, severity), contract (producer signatory, source), pipeline (source, layer, upstream, owner), run (period, replay, reason), incident (classification), lineage (transformation), retention (statutory floor, legal hold). The contract, pipeline, run, incident, entity and retention forms are now tabbed, and **no form lets a person type a state** any more.
- List buttons for the governed steps that were served but offered nowhere: Producer Sign, Request Activation and New Version (contracts); Record Steward Review and Request Publication (versions); Retire (metrics); Measure Now (rules); Request Shortening, which asks for the months, and Run Disposition (retention); Request Approval (declassification); Complete Erasure; Activate and Retire (sources).
- The write whitelist covers exactly what each form lets a person type. The version whitelist was empty, so no version could be drafted.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Ingestion | Data Pipeline | Data Pipeline, **Data Source**, **Pipeline Run** (was none) |
| 2 Medallion & Transformation | Pipeline Run | **Pipeline Run** (was none) |
| 3 Dimensional Model | Data Entity | **Data Entity**, **Conformed Dimension** (was none) |
| 4 Semantic Layer | Metric Definition | Metric Definition, **Metric Version**, **Metric Consumer**, **Glossary Term**, Data Contract |
| 5 Quality & Observability | Quality Rule | **Quality Rule**, Quality Test, **Data Incident** |
| 6 Catalogue & Lineage | Data Lineage | **Data Lineage**, **Data Entity**, **Glossary Term** (was none) |
| 7 Security & Cost | **Retention Policy** (was none) | **Retention Policy**, **Declassification Authorisation**, **Analytical Erasure**, Sensitive Field (M29's own form) (was none) |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m62_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. It also checks: every list column and form field against the model; every action against the surface; that every served model sits on a page; the whitelist against each form; that no form types a state; and that no stamp or measured figure is writable. | **HEAD 32e24dc9: 23 of 46 fail.** After: **46/46.** |
| Estate page standard `test_estate_module_pages.py` (all 67 modules). | **605/605** (651 with the guard). |
| Live tests `cd_metric_registry/tests/test_m62_capture_live.py` on the private clone `fix_test_m62` (`-u all`, 166 modules, exit 0, no ERROR). They run as freshly created users: two Data Governance Officers (one requests, the other decides through the real M63 inbox), a plain user and a DPO who starts real M33 erasure requests. | **27/27.** The first run caught two real defects, fixed before this result: the publication note was posted on the metric definition, which has no chatter, so every publication with a consumer crashed; and a glossary term without an owner reached the database as a raw NOT NULL error instead of a readable refusal. |
| Mutation check: each new rule removed in turn (29: source owner and steward, credential refusal, active source, dependency cycle, upstream gate, backfill period, backfill reason, replay pipeline, contract before Silver, concluded run is history, fact grain, Odoo model exists, SCD tracked attributes, dimension not a fact, published definition frozen, no retirement with consumers, change reason, definition follows version, reviewed version frozen, server numbering, one glossary meaning, declassification from current, every erasure layer, erasure evidence, completed erasure final, erasure opened on start, erasure only for erasure, check field exists, rule severity used). | **29 of 29 mutations turned the live tests red**; the source was restored byte for byte. |
| Regression on the same clone: every `cd_metric_registry` test, the A11 control suites (M25, M62, M63, cross-area exposure sweep), the M62 guard, the estate guard and every `cd_party_master` test (its rights request is extended). | **1,059 tests: 1,057 passed, 2 failed.** The two (`test_refuse_stops_the_site[pending dealer-an invoice]`, `test_allow_still_refuses_a_pending_dealer[an invoice]`) **fail identically with the code that has none of this change** (shared tip 00326139, same clone): the commercial-document standard now asks for the buyer's BIN before the dealer-registration check is reached. Not touched here. |
| Existing tests changed, and why: `test_m62_54` pinned the metric-version whitelist as empty, which is the defect that blocked publication; it now pins that the state, stamps and impact list stay off it. The registry test's second version now records a reason (FR-DAT-019). Three refusal messages kept their old wording (the new history and declassification checks yield to the original messages). | — |
| Workspace on a private server (port 8098) over the clone, signed in as admin. | All 7 pages render with their new "+ New" (page 7: **"+ New Retention Policy"**, was none). All 20 M62 lists answer `/p03/model/records` with **no column dropped**. One record of each new form was saved through `/p03/model/write`, the form's own endpoint. Refusals came back as readable messages: activation without owner and steward, a backfill without a reason, Silver without a contract, a check field the model lacks. Publication and shortening requests were refused only because the clone has a single governance officer, so nobody else can decide them; the live tests cover that path with a second officer. |

Test traps met (recorded so the next run avoids them): the probe's measured quality row stayed on the clone and two runner tests that count the whole evidence table read 60% instead of 50% (row removed); the private server's relay cron caused a serialisation failure in a party-merge test while the regression ran (server stopped). The browser pane's cookies are shared with other sessions on 127.0.0.1, so its session expired between calls; the endpoint checks ran from a script with its own cookie jar.

## 4. Not built here (owner decisions, data, or other modules)

- **The engine behind the registers.** There is no warehouse, CDC connector or lineage emitter in this estate: a pipeline run, a backfill and an erasure tick record what the platform team did; nothing here moves data. Schema-drift detection (FR-DAT-027 P0), volume and distribution monitoring (FR-DAT-026/028), OpenLineage emission (AUT-DAT-11), the feature store (FR-DAT-038), row-level security in an analytical engine (FR-DAT-033) and platform cost by compute (FR-DAT-037; cost is still volume × rate) need that engine.
- **Subject areas** (`fix.subject.area`, BRU-DAT-20/21: degraded status and freshness per subject area): the entity's `degraded` flag stands in. **Certification** as a separate state (metric lifecycle §8.2: approved, then certified by the business owner and the CTO) is not modelled; publication through M63 is the single gate. **Deprecation with a named successor and transition window** (FR-DAT-021): retirement is blocked while consumers remain, but no successor field exists.
- **Consumer notification** (BRU-DAT-03): consumers are registered as names, not users, so "notified" means listed on the request and noted on the published version. Telling actual people needs consumer owners.
- **Who governs:** the Data Governance Officer group has one holder on fix_real (the development admin), so **no contract activation, metric publication, retention shortening or declassification can be decided there yet**: approving needs a second officer. Appointing officers (and a DPO for erasures) is the owner's decision.
- **fix_real's seed rows** (5 "published" metrics with no version, 3 "active" contracts with no producer signature, 4 pipelines whose entities map to no model): they predate the A11 controls. They are left as they are and not repaired: correcting them is a governance act for the officers, not a code change.

## 5. State

**Landed and deployed 18 Nov 2026.** The branch was rebased twice while peers landed (onto 734327d7 for M63, whose `cd_workflow_engine` change touches the approval engine that metric versions use, then onto 663d7dec for M59/M60/M61/M64/M65). Retests on the rebased code: 955/955 (cd_metric_registry, cd_workflow_engine, M62 and M63 page guards, A11 M62 controls, estate page guard) on `fix_test_m62` upgraded with the M63 code, then 706/706 page guards on the final base. Landed as e9625567 by compare-and-swap fast-forward of `fix/a03-live-data-and-pending-work` (the first attempt was refused because M63 had moved the tip; nothing was overwritten).

Deploy: backups `1000 fix/backups/fix_{real,dev}_pre_m62_capture_2026-11-18.dump` (50.7 MB / 46.2 MB); waited for the peers' running upgrades to finish; `-u cd_metric_registry,cd_p03_portal` on fix_real and fix_dev (0 ERROR lines, both at 19.0.0.2.0, the four new tables present, no other module behind its manifest); one restart each of 8069 (fix_real) and 8090 (fix_dev). Live check on both servers: all 20 M62 lists served with 0 columns dropped (including the new source, dimension, glossary and erasure registers), served bundle 2ecffda carries the new M62 forms, 0 ERROR lines since the restart. Pushed to origin: `fix/a03-live-data-and-pending-work` 00326139..bd3f4796 (fast-forward, carrying the M59-M65 landings too) and the new branch `fix/m62-capture-buttons` at e9625567. The clone `fix_test_m62` and the worktree are removed; the branch `fix/m62-capture-buttons` is kept.
