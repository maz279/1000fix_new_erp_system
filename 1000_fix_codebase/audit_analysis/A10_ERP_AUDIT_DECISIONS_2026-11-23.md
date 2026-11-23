# A10 (Quality & Governance) — Owner Decisions

Date: 2026-11-23. Source: A10 deep audit (5 read-only auditors + lead verification), register
`1000_fix_codebase/scratch/a10_deep/REGISTER.md`, findings in `scratch/a10_deep/findings/A1..A5`.
Deployed fixes: 06793b20, b26b7fb3, 0f1d892b, cb1f1808, 890ad2bd, 7cc0a429 (fix_real + fix_dev upgraded).

Each item below needs YOUR decision. My recommendation is first.

---

## D-A10-1 — Registry cross-claims that are fiction today
The registry claims 16 cross-links for A10. Measured: **4 wired, 8 partial, 4 missing**:
- "M36 quote e-sign" (M24): quotes sign through their own HMAC stack; only M08 contracts use M24 envelopes.
- "Every transaction auto-files" (M24): no producer exists for finance documents (invoices/mushak); operational
  flows do file (8 modules) but their tables are empty on live.
- "P02 offline library" (M61): `get_offline_manuals()` has no route/caller; the technician PWA is a stub.
- "M32 RAG grounding" (M61): assistant answers knowledge intents from hardcoded text; no article retrieval.
- "M31 repair methods" / "M01 diagnostic trees" (M61): `surface_for()` has no production caller.
- "M29 SoD" (M60): **fixed** — the M60 register now derives 61 rows from the enforced controls (live).

**Recommendation:** wire the ones that carry statutory/operational weight now (M24 finance auto-file, M60 SoD
already done), and REWORD the registry for the rest until built (M36→"M08 contract e-sign", M61→"M27 agent
knowledge bindings", drop P02/M31/M01 claims or mark "planned"). Alternative: build all five integrations
(est. 3-4 weeks). **Your call: reword now vs build now.**

## D-A10-2 — M24 finance auto-file scope
Invoices and VAT evidence currently live outside the governed repository (tax engine's own attachments).
**Recommendation:** add one producer — `account_move` posted invoices → `fix.document` (type invoice,
retention FIN-7Y) — so Mushak evidence is inside retention/legal-hold. Scope: ~2 days + a backfill decision.

## D-A10-3 — "Bilingual Full-Text + OCR" screen
The screen exists but serves the Access Audit grid; no OCR/full-text code exists.
**Recommendation:** retitle the screen to what it serves now (1 hour), schedule real search later
(Postgres trigram on name/name_bn + attachment text extraction, ~2 weeks). Retitling alone would make the
registry honest immediately.

## D-A10-4 — Quote e-sign path
Two e-sign stacks coexist (M24 envelopes vs M36 local HMAC).
**Recommendation:** route M36 quote acceptance through `fix.esignature.envelope` (one evidence model, tamper
evidence, wet-ink fallback for free) — ~3 days. Alternative: keep local and document the exception.

## D-A10-5 — Live configuration is EMPTY (go-live blocker class)
On fix_real today: 0 risks, 0 controls, 0 compliance obligations, 0 policies, 0 documents, 0 knowledge
articles, 0 PDPA processing records, 0 ISO certifications, 0 SoD rules (now 61 derived). The system is
capable; the governance CONTENT was never loaded (the 2026-11-05 "SoD live" verification ran on the old
synthetic estate).
**Recommendation:** a content-load package in this order (owner supplies facts, I load):
1. ISO 9001:2015 certificate + surveillance schedule (certificate no., body, dates) — 1 hour, unlocks the new surveillance clock.
2. PDPA 2026 RoPA (processing activities) + retention classes — the real customer PII (24,194 partners) is already live; a DPIA-lite is prudent.
3. Risk register (top 15-20 operational/financial risks) + linked controls with owners — feeds heat map, appetite routing, M63.
4. Compliance obligations from the statutory calendar (Mushak 9.1, TDS, VDS, WHT, CIT) — the M51 calendar has real overdue rows and M60 cannot see them.
5. Knowledge seed (repair procedures from the dev library fixtures) if technicians go live.
6. Staff the 13 A10 groups: today only `admin` holds them; 349 real users hold none.

## D-A10-6 — M24 access audit is external-only
Internal reads of T3/T5 documents leave no trace; the "Access Audit Export" report exports repository
signals, not accesses.
**Recommendation:** keep as-is for now (the tier gate now blocks reads at all — the exposure dropped), and add
read logging when the internal-read hook lands (M24 backlog). Alternative: reword the report to "external
access log" today.

## D-A10-7 — Registry vs fragment drift (M23/M24/M61)
The fragments carry 17-23 screens each (capture-pass additions) while `contracts/nav/registry.json` declares
9-12; the mega menu / Tell-ME / Report Center therefore miss the newer screens. Same for 2 retired KPI labels
still advertised for M61.
**Recommendation:** regenerate the registry from the fragments and run the FF-38 gate (this is the repo's
stated flow) — ~1 day including the check sweep. Note: registry.json is GENERATED and feeds governance docs;
regeneration must be reviewed.

## D-A10-8 — DoA ladders / approval matrix coverage
Only 2 of ~40 governed models have an in-force DoA ladder (loyalty ledger, complaint); the approval matrix
has 6 rows, all with NULL approver groups and 2 `seed_role` artifacts. Fail-mode is the coded default
(fail-closed — never ungated), but the register is thin.
**Recommendation:** appoint the authority owners and rule the ladders for the money models first
(purchase, AP, AR write-off, payroll) — owner decision on who holds Tier 3-5.

## D-A10-9 — M33 DSR intake ↔ M60 PDPA register
No wiring: a data-subject request arrives through M33 and never opens a `fix.grc.pdpa` clock.
**Recommendation:** add a 30-line consumer (M33 DSR create → fix.grc.pdpa) so the new 30-day clock runs on
real requests — ~1 day.

## D-A10-10 — Published knowledge edit policy (already enforced)
Published articles are revised by the author or a Knowledge Publisher; a revision clears the old review
stamps; safety-tag edits are revisions.
**Recommendation:** confirm this policy stands (it closes the "any clerk edits field content" hole). If field
supervisors should also propose edits, use the capture queue (already built) rather than widening write.

---

## Backlog accepted without decision (P2/P3, not blocking)
M24: stale note fixed (live); system-generated certificate types will queue as exceptions once document
classes activate (seed classes at activation); controlled-document lineage by name (add root + unique index
when volumes grow); release index logs per-document view (downgrade to one page view).
M60: control_tests_due ignores frequency (P2); editing an old control test back-stamps the control conclusion
(P2); whistle read-log volume (P3); DSR broad read ACL (P3).
M61: tree node targets unvalidated (free text, no cycle risk structurally); version history forward-only (seeded
content starts at v1); drafts visible to every internal user; bn_BD.po covers 40 msgids; offline sets never
auto-refresh; phantom OpenAPI endpoint `GET /projects/portfolios` assigned to M61.
M23: `capa_on_time` now honest (dash on empty; only due-dated verdicts measured); P11 auditor app has no
backend API (data layer exists); `action_fail_with_ncr` now wired (failed completion raises MAJOR NCR once).
