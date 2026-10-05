# Codebase Risk Register — prototype_porting overlay (2026-10-05 forensic audit)

Companion to `AUDIT_REPORT.md`. Each row: finding → exact remediation (applied) →
verification. Status **R** = remediated & committed; **W** = watch (non-normative,
ratify before normative).

| # | Sev | Risk (had it shipped) | File:section | Remediation applied | Verify |
|---|---|---|---|---|---|
| K-1 | CRIT | False incident history + phantom implementation ("fix_offline implemented") poisons future decisions and M&A diligence | LEARNINGS L-06/L-07 | Reclassified as DESIGN CAUTIONS with not-an-incident banners; UNBUILT status stated | R — grep: no past-tense incident claims remain |
| K-2 | CRIT | Client-side money math (AS-09/AS-10 breach) would put tax/balancing authority in browsers | 03 §8 | Backend-computes/client-renders rewrite; lint/review rule added to PP3 verify column | R |
| K-3 | HIGH | Three fabricated model names would fail PP6 parity tests and mislead PP1 API design | 03 §9 | Replaced with real models; endpoints flagged PROPOSED | R — `grep _name` all hit |
| K-4 | HIGH | Wrong-domain statutes (CDBL/BSEC/BFIU) would create phantom compliance obligations and scope | ARCH_STATE §5, LEARNINGS §3, 04 R-17/R-18 | Removed with in-place removal notes; R-18 → PDPA SC-003/SC-008 | R — only removal-notes remain |
| K-5 | HIGH | Unsourced perf scope (60 FPS/10k, MDI LRU, currency multipliers) inflates PP2/PP3 cost and un-achievable DoD | 01 PP2/PP3 cells | 12 cells re-grounded to contracts A2/A4/A5 + shell port; options marked non-normative | R |
| K-6 | MED | False infra facts (PG 17.2, local TimescaleDB, "all traffic via Kong") mislead environment design | ARCH_STATE §1/§6 | [FACT] 17.4 + Timescale-not-local; §6 re-headed [TARGET — nothing exists yet] | R — vs compose pins |
| K-7 | MED | DoD thresholds off-contract (48px vs 44px token; 7:1 as AA) | 05 D9/D10 | Re-grounded to DTCG token + WCAG-AA; INP/LCP → proposed-until-benchmarked | R |
| K-8 | MED | Invented validation rules (NBR Luhn, EC sandbox) | 03 §7 | Length/digit rules as actually enforced; unverified checks removed | R |
| K-9 | LOW | Fact/target/aspiration unlabeled across the two new docs | ARCH_STATE all §, LEARNINGS C-0x | [FACT]/[TARGET] banners + reclassification notes; README map updated | R |
| K-10 | W | Windowing/sticky-columns option may still be read as required by a scanning implementer | 01 PP2-M02-T01 note | Kept as explicitly-conditional option (">~1k rows in UAT — benchmark first") | W — PP2 ratifies |
| K-11 | W | Tab-eviction/sessionSnapshot option incl. benchmark figure | 01 PP2-M07-T01, LEARNINGS C-03 | Marked aspiration-to-benchmark, NOT-a-requirement | W — PP2/PP3 ratify |
| K-12 | W | INP/LCP thresholds | 05 D10, 01 PP7-M04 | Proposed-until-benchmarked; contracted budget remains P01<400KB/3G | W — PP7 ratifies |

**Standing control added**: the AUDIT_REPORT §5.2 rule — normative cells cite a source
(prototype payload, roadmap task, DTCG token, or vendored file); anything else must be
labelled *(non-normative design option)*. The next overlay that violates it fails review
on sight.
