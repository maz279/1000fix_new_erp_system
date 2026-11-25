# M61 Knowledge & Technical Library: Sub-Module Capture Audit (2026-11-18)

**Trigger.** The user observed that not every M61 sub-module page has a relevant data-capture button.

**Sources**
- Spec: `1000fix_ERP_Module/03_Modules/I_Governance_Risk_Quality_and_Knowledge/M61_Knowledge_Management_and_Technical_Library.md`. Sections used:
  - §3: scope (21 capabilities) and boundaries (M24 stores the files, M22 trains, M01/M09 act on recalls, M37 owns the taxonomy);
  - §5: FR-KMS-001 … 036;
  - §8: the article and bulletin lifecycles and their transition guards;
  - §9: BRU-KMS-01 … 18;
  - §10.1: the 19 owned entities;
  - §11: AUT-KMS-01 … 18;
  - §13: roles, the reviewer ≠ author rule and the safety second approval.
- Code:
  - `cd_p03_portal/static/src/a10/m61.js`: the page registry (8 sub-module pages);
  - `cd_p03_portal/controllers/a10/m61.py`: surfaces, reports and KPIs;
  - `cd_knowledge/models/*.py`: articles, trees, media, bulletins and their recipient lines.
- Live data, read-only counts on 18 Nov:
  - fix_real has **no** M61 record (0 articles, trees, media, bulletins), 24 fault codes, 161 brands, 1 Knowledge Publisher, 1 Quality Manager;
  - fix_dev has seed content (8 articles, 3 trees, 4 media, 3 bulletins).

## 1. What was there (HEAD 32e24dc9)

The pages were evaluated with the engine's own `fregCreate` / `fregPanels` in node, which is how the browser decides what a page shows.

| Page | Sub-module | "+ New" | Chips | Defects |
|---|---|---|---|---|
| 1 | Authoring & Versioning | Article | Article | **No field capture** (FR-KMS-023/024/027 P0, BRU-KMS-08/09 H): a technician could not record a solution in their own words; there was no improvement queue. **No review request**: the "Review Workflow" list re-listed articles, and its Publish button asked for a reviewer's **numeric user ID** in a browser prompt. Ordinary content was published **with no reviewer at all**, against BRU-KMS-02 (H: "cannot be published without technical review by a qualified reviewer who is not its author"). Safety content was released on a typed reviewer ID with no Quality Manager approval (BRU-KMS-03 H). **No version history** (FR-KMS-007 P0): a revision overwrote the text. |
| 2 | Troubleshooting Trees | Troubleshooting Tree | Troubleshooting Tree | The decision steps were one free-text box (FR-KMS-005 P0 asks for nodes with checks, measurements, outcomes and links). A published tree's steps could be changed freely. |
| 3 | Technical Library | **none** (`create: false`) | **none** | The page **captured nothing**. "Manuals & Schematics" listed **articles** of three types. There was **no library entry**: no file, no brand/model index, no licence or redistribution terms (FR-KMS-004 P0, BRU-KMS-16 H). The media form existed but was on **no chip**. |
| 4 | Search & Surfacing | **none** | **none** | The page **captured nothing**. **No operational link** to the catalogue's fault codes, models or brands (FR-KMS-006 P0), so context surfacing (FR-KMS-015) could match only on free-text brand/model words. |
| 5 | Offline Distribution | **none** | **none** | The page **captured nothing**. **No technician offline set**: no scope, no storage budget, nothing removed an archived article from devices (FR-KMS-017/018 P0, BRU-KMS-05). |
| 6 | Feedback & Health | **Article** | none | "+ New" opened an **article**. **No usefulness feedback** (FR-KMS-030 P0). The "Usefulness Score" tile divided helpful votes by a `views` counter that **nothing increments**, so it was always 0, and nothing ever incremented the helpful votes either. Nothing flagged an article that did not resolve faults (AUT-KMS-17). |
| 7 | Brand Bulletins | Bulletin | Bulletin, Bulletin Recipient | None (built by A10 P1-7). Its recipient list was on no page; it is now listed here. |
| 8 | Expertise Mapping | **Article** | none | "+ New" opened an **article** over a list of articles. The expertise map is **derived** (FR-KMS-035, AUT-KMS-18): nothing is typed. No expertise report existed. |

Guard `cd_p03_portal/tests/test_m61_capture_buttons.py` on HEAD: **25 of 42 tests fail.** The failures cover:
- pages 1-6 and 8;
- the article offered on the feedback and expertise pages;
- the library list that showed articles, and the review list that showed articles;
- the typed reviewer ID;
- the creatable lists with no capture;
- the six missing registers, the tree's steps grid, the untabbed article form, and the security and load order of the new models.

## 2. What was built

### Backend: `cd_knowledge` 19.0.0.2.0, new file `models/fix_m61_capture.py`

`cd_knowledge` now depends on `cd_service_order`. That brings `cd_catalogue`, so links, captures and feedback name the catalogue's fault codes, device models and brands and the job they came from. `cd_service_order` does not depend on `cd_knowledge`, so this adds no cycle (checked over every manifest).

| Page | Record | Holds | Rules |
|---|---|---|---|
| 1 | `fix.knowledge.capture` (FR-KMS-023/024/027, BRU-KMS-08/09) | The technician's own words (Bengali is fine), a photo, a voice note, the job, and the brand, model, fault code, symptom and level. Naming the job fills in the device's brand and model and its first fault code. | The contributor is stamped and cannot be forged. Their words are editable **only by them, only while queued**; after that they are frozen. A Knowledge Publisher **other than the contributor** takes it into the improvement queue, then either **structures it into a draft article** or **merges it** into the article that already covers it. A structured article is pre-filled and carries the original words (never editable), the contributor and a fault-code link; a merge posts the words on the article. **Never discarded, never deleted.** |
| 1 | `fix.knowledge.review` (BRU-KMS-02/03, §8.1 IN REVIEW) | Article or tree, the reviewer, what to look at, the hash of the content reviewed, and whether safety sign-off is required; the comments and the stamps. | Requested on **draft** content only. The reviewer is a **Knowledge Publisher who is not the author** (creator, owner or contributor); one open review per item; a bad request leaves no row. **Only the named reviewer approves or returns it** (a return says why). An approval covers the content **as reviewed**: an edit after the request blocks approval. Safety content then needs the **Quality Manager's sign-off, by someone who neither wrote nor reviewed it**. |
| 1 | **Publish gate** (articles and trees) | — | An approved review of the current content names the reviewer. Without one, ordinary content is published only by a **publisher who did not write it**, who becomes the named reviewer. Safety content (electrical, battery, high-voltage, safety bulletins) is published **only through a review carrying the QM sign-off**. **A reviewer is never typed at publication.** Superuser code keeps the old path. |
| 1 | `fix.knowledge.article.version` (FR-KMS-007) | Each published version: titles, content (EN/BN), hash, who, when, reviewer, published or revised. | Written by publication and by revision of published content; **never typed, never edited** (read-only ACL plus guard). A new version clears the usefulness flag. |
| 2 | `fix.knowledge.tree.node` (FR-KMS-005) | Step, type (question/check/measurement/outcome), text EN/BN, expected reading, where yes/no lead, procedure article, safety note. A grid on the tree form. | **Steps change only while the tree is a draft** (add, edit and delete refused once published). The steps are part of the reviewed content: editing one after a review request blocks approval. |
| 3 | `fix.knowledge.library` (FR-KMS-004, BRU-KMS-16) | Title, entry type, brand, models covered, other models, file (upload) or M24 reference, pages, source, **licence terms**, **who may use it** (workstations only, technicians including offline, or brand-authorised only). | Registered by Knowledge Publishers (others read). **Made available only with a file, the models and the terms recorded**. After that, file, index and terms are fixed (a new edition is a new entry). Withdrawal needs a reason. Only "technicians, including offline" may go offline. |
| 4 | `fix.knowledge.link` (FR-KMS-006/014/015) | Article or tree, and **exactly one** of fault code, device model or brand, with a relevance weight 1-10. | No duplicates, nothing archived. `surface_for(fault, model, brand)` returns the published articles and trees for a job: by link relevance, then by resolution rate, plus the job brand's brand-wide articles, with review-overdue marked. Only publishers delete a link. |
| 5 | `fix.knowledge.offline.set` (FR-KMS-017/018, BRU-KMS-05) | Technician, brands, models, highest repair level, storage budget; the computed set, its size, what was left out over budget, when computed, when last synced. | Set up by publishers; **one per technician**; a technician sees only their own. "Compute" (a publisher or the technician) takes **only published, offline-flagged articles in scope up to the level**, model-linked ones first, **within the budget**. **Archiving an article removes it from every set.** Only the technician's device reports a sync. `offline_manifest()` gives each article's version and hash. |
| 6 | `fix.knowledge.feedback` (FR-KMS-030, AUT-KMS-17) | Article, version rated, given by, job, "did this resolve it?", rating 1-5, comment, given offline. | **Published content only**; the giver is stamped; **once per person, version and job**; **kept as given** (no edit, no delete). It sets the article's feedback count, resolved-it % and average rating, and increments helpful votes on a "yes". **Three "did not resolve" answers in a row, or an average below 2.5 over five or more ratings, flag the article** and give its owner a to-do. The next revision or publication clears the flag. |
| 8 | Expertise Map (report) | Per brand: who authored, captured and reviewed, and the brands whose knowledge sits with fewer than three people (KPI-C61-12). | Derived; the page has **no "+ New"**. |

Security and data:
- ACLs: captures, reviews and links are raised by any internal user. Library entries and offline sets are maintained by Knowledge Publishers and read by everyone. Versions are read-only. Feedback is create-only. Nobody deletes a capture, review, feedback or version; only publishers delete a link.
- Record rule: a technician sees their own offline set; publishers see all.
- Company rules come from `generate-isolation-rules.py`. Only the `cd_knowledge` file was kept; the generator's drift in six other modules was reverted.
- Sequences KREV/, KCAP/, OFS/.

### Workspace: `m61.js`, `controllers/a10/m61.py`, `writable.py`

- Nine new lists on their pages and in the navigation:
  - Field Captures & Improvement Queue, Version History, Operational Links, Technician Offline Sets, Usefulness Feedback;
  - Review Workflow, now the review requests;
  - Manuals & Schematics, now the library entries;
  - Expertise Map and Recall Recipients.
- Seven new forms: Field Capture, Review Request, Library Entry, Knowledge Link, Offline Set and Usefulness Feedback (tabbed where they have many fields), plus the existing Media Asset form, now on a chip.
- The Article form is now tabbed (it had 19 fields), with the contributor's original words, the latest review and the usefulness figures.
- The tree form has a Decision Steps grid.
- Publish no longer asks for a reviewer ID. Review actions ask only for comments; withdrawal asks for a reason; merge asks for the article's reference code.
- **"Article Usage & Usefulness"** now reads the feedback: feedback count, resolved-it %, average rating, and a health column (flagged / review overdue).
- **The "Usefulness Score" tile is now "Resolved It (Feedback)"**, measured from feedback.
- **The Contribution Leaderboard** counts articles owned, captures, reviews done and resolved-it answers.
- **Expertise Map** is a new report.
- `writable.py` was regenerated with `form_fields.py --a10`; only the new entries and `node_ids` on the tree were added.

| Page | "+ New" after | Chips after |
|---|---|---|
| 1 Authoring & Versioning | Article | Article, **Field Capture**, **Review Request** |
| 2 Troubleshooting Trees | Troubleshooting Tree | Troubleshooting Tree, **Review Request**, **Knowledge Link** |
| 3 Technical Library | **Library Entry** (was none) | **Library Entry**, **Media Asset** |
| 4 Search & Surfacing | **Knowledge Link** (was none) | **Knowledge Link** |
| 5 Offline Distribution | **Offline Set** (was none) | **Offline Set** |
| 6 Feedback & Health | **Usefulness Feedback** (was Article) | **Usefulness Feedback** |
| 7 Brand Bulletins | Bulletin | Bulletin, Bulletin Recipient |
| 8 Expertise Mapping | none: derived (was Article) | none; Expertise Map + Contribution Leaderboard reports |

## 3. Evidence

| Check | Result |
|---|---|
| Guard `cd_p03_portal/tests/test_m61_capture_buttons.py`. Node runs the engine's own `fregCreate`/`fregPanels` over the real registry. It also checks: every list column and form field against the model; every action against the surface; every report route against the controller; the whitelist against the forms; that no stamp or measured figure is writable; tabbing; and security. | **HEAD 32e24dc9: 25 of 42 fail.** After: **42/42.** |
| Live tests `cd_knowledge/tests/test_m61_capture_live.py`, run as freshly created non-admin users (two technicians, three Knowledge Publishers, a Quality Manager) on a private clone `fix_test_m61` (`-u all`, 166 modules, exit 0, no error). | **18/18.** The first runs caught four real defects, fixed before this result: a review request with no subject crashed instead of refusing; a refused request left a row behind, which then blocked the next request ("already has an open review"); a technician could not recompute their own offline set; and no plain user could give feedback (the version stamp needed write rights). |
| K1 controls `test_a10_k1_controls.py`, rewritten to the review path. Each original attack is kept (non-publisher, non-publisher reviewer, author as reviewer, guarded writes, the P03 endpoints), and new ones were added (author publishing their own content, a typed reviewer, safety content without the QM). | **8/8.** |
| Mutation check: each rule removed in turn (see `mutate.py`, 27 mutants). | **27 of 27 mutations turned the tests red** (author publishing unreviewed; safety without a review; typed reviewer; reviewer not a publisher; author as reviewer; two open reviews; anyone approving; approving changed content; reviewer signing off safety; non-QM sign-off; capture words edited after take; contributor structuring their own capture; original words dropped; no version history; published tree steps edited; library available without terms; library terms edited when available; link with several subjects; duplicate link; drafts in an offline set; budget ignored; archived article left offline; feedback on drafts; feedback twice; feedback rewritten; no flag after three 'no'; flag surviving a revision). The first run left one survivor (a typed reviewer on ordinary content): a test was added and it turned red. The source was restored byte for byte after each mutant. |
| Regression on the same clone: every `cd_knowledge` and `cd_contact_centre` test, the portal's A10 control suite and A10 write whitelist, the estate page guard (all 67 modules), KPI tiles, declared-gap reports, Tell-Me registry, A03 registry coverage and the M61 guard. | **1,417 tests: 1,410 passed, 7 failed.** One was mine (an offline set's size rounded to 0.0 MB at three decimals; now six), fixed and re-run green. **The other six fail identically with HEAD code on the same database:** the recall-routing relay (3), the contact-centre knowledge binding (2) and the approval e-mail/SMS wire (1). The clone's `fix_test` template carries **53,624 pending outbox events**, and the relay takes the oldest first; this is the relay class recorded in the M51/M56/M57 audits, not touched here. |
| Workspace UI on a private server (port 8094, host `m61.localhost`) over the clone, signed in as admin. | All eight pages read live from the page: (1) "+ Article" with Article, Field Capture and Review Request chips; (2) "+ New Troubleshooting Tree" with Tree, Review Request and Knowledge Link; (3) **"+ New Library Entry"** with Library Entry and Media Asset (was nothing); (4) **"+ New Knowledge Link"** (was nothing); (5) **"+ New Offline Set"** (was nothing); (6) **"+ New Usefulness Feedback"** (was Article); (7) "+ New Bulletin" with Bulletin and Bulletin Recipient; (8) **no "+ New"**, showing the Expertise Map (was Article). A Field Capture was **saved from the tabbed form** with Bengali text: KCAP/2026/0014, queued, contributor stamped by the server. The Expertise Map page then showed it (Zeltrix, 1 capture, CONCENTRATED). Server log: no ERROR. |
| Lint and format with the pinned ruff 0.8.4. | All checks passed; files formatted. |

## 4. Not built here (owner decisions or other modules)

- **Reviewer competence against M22** (FR-KMS-008, §8 guard "reviewer holds current competence on the relevant brand or repair level"): the reviewer must be a Knowledge Publisher and not the author. There is no brand/level competence check, because which M22 competencies qualify a reviewer is a Quality Manager decision.
- **Seven article types with per-type templates and a completeness score** (FR-KMS-001/011): the existing seven categories differ from the spec's eight types (no FAQ/how-to/known issue/technique/tool guide). Changing the selection re-classifies content: an owner decision.
- **Customer-facing derivative** (FR-KMS-010 P1, BRU-KMS-11): needs the Customer Service Manager role as second approver; none is defined in the estate.
- **Superseding / contradiction control** (BRU-KMS-04): two published articles for the same model and fault can still coexist. The version history now records every revision of one article.
- **Capture prompts and definition-of-done on complex repairs** (FR-KMS-025/026, AUT-KMS-01/02, BRU-KMS-10): the trigger sits in M01/M31 job closure, and which repair classes it applies to is an Ops Director decision. The capture itself can now be raised from a job.
- **Usage events, resolution attribution and first-time-fix attribution** (FR-KMS-019/036, BRU-KMS-17): these need the technician app to report opens. The `views` counter still counts nothing and is no longer shown as a usefulness figure.
- **Bilingual typo-tolerant search, M32 corpus API, P01 customer self-help, OCR of manuals** (FR-KMS-013/016/021/022): integrations, not captures.
- **Bulletin acknowledgement per technician** (spec §10.1 `fix.bulletin.acknowledgement`): bulletins are acknowledged per branch (A10 P1-7); per-technician tracking is unchanged.
- **Data**: fix_real has no M61 content, one Knowledge Publisher and one Quality Manager. Everything above is ready for the Technical Library Owner to take on content; nothing was seeded.

## 5. State

**Deployed on fix_real (8069) and fix_dev (8090), 18 Nov 2026 08:20 +0800.** Not pushed.

1. Committed on `fix/m61-capture-buttons` and rebased twice, first onto M63 and then onto M59 and M60. M60 had also changed `controllers/a10/writable.py`; regenerating it with `form_fields.py --a10` gave the same file both times. The rebased code passed a rehearsal `-u cd_workflow_engine,cd_knowledge,cd_p03_portal` on the clone, and the M61 and M63 tests ran 121 with 0 failures.
2. Backups were taken before the upgrade: `1000 fix/backups/fix_{real,dev}_pre_m61_capture_2026-11-18.dump` (51.0 MB and 46.5 MB).
3. Landed by a fast-forward of `fix/a03-live-data-and-pending-work` to f8784f17, the code commit baded47b plus the report.
4. Ran `-u cd_knowledge,cd_p03_portal` on fix_real and fix_dev; both exited 0 with no ERROR lines. cd_knowledge is now 19.0.0.2.0 on both, with all 8 new tables and the KCAP/, KREV/ and OFS/ sequences.
5. Restarted each server once at 08:20, after the M64 and M65 upgrades that landed after M61, so the one restart covers M59, M60, M61, M63, M64 and M65. 8069 is now PID 7840 and 8090 is PID 71092. Both boot logs show no registry failure and no missing table, and version_gap shows 0 on both databases.
6. Rebuilt the asset bundle from an odoo shell. Bundle d91fc14 on both databases carries the M61 captures and the Expertise Map report. The running servers return `/p03/model/records` for all eight M61 surfaces on both ports.
7. Dropped the clone `fix_test_m61` and its filestore.

fix_real holds no M61 record, so no existing data changes. The behaviour that does change: an article or tree can no longer be published by its own author without a review, and safety content needs the Quality Manager's sign-off. fix_real has one Knowledge Publisher and one Quality Manager. Content written by that publisher can only be released once **a second Knowledge Publisher is appointed** (owner decision B1 of the A10 report); content written by anyone else can be reviewed and published by the one publisher.