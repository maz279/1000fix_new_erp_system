# DEP-31 — External legal opinion on PDPA 2026 data residency: engagement scope

**Task `P01-M02-T01`** · Prepared 2026-10-01 · Owner: Security Lead (`SL`)
**Status: READY TO EXECUTE — engagement letter to be signed on Programme day 1
(6–10 week lead; the critical path's longest single item, `B-02`).**

---

## 1. Mandate (single sentence)

Counsel is engaged to answer, **in writing**, the five questions below — and
nothing else; "residency in general" is explicitly out of scope (IR-002
§0.7.1: the open-ended engagement is the failure mode that produced the
current ambiguity).

## 2. The five questions (verbatim from IR-002 §0.7.1)

| # | Question counsel must answer in writing |
|:--:|---|
| **Q1** | Which of the Company's fields fall within the Act's defined term **"restricted personal data"** — field by field, against the `DA-005` candidate list (attached as `field-classification-candidates.md`)? |
| **Q2** | Is the obligation **a synchronised local copy** or **exclusive local storage**? If a copy, is a regional primary with a Bangladesh replica compliant? |
| **Q3** | Is 1000FiX, or any part of it, capable of **CII designation**? What triggers it, and what changes if a **client** is designated? |
| **Q4** | What does **"large-scale transfer"** mean quantitatively for the restricted categories, and what notification and safeguard duties attach? |
| **Q5** | What is required by **~13 May 2027** specifically, as distinct from what is good practice? |

## 3. Materials provided to counsel

1. The candidate field classification list (`field-classification-candidates.md`) — Q1's input.
2. `SC-007` residency architecture and `NFR-086` (exclusive-residency design as drafted).
3. The three `D-013` option architectures (A/B/C) with their data-flow descriptions.
4. `05-06` §6.3–§6.4 (privacy controls), TSS §3.4 (trust zones and network
   segmentation) and TSS §14.4 (split residency — the enforcement mechanism).

## 4. Facts counsel should weigh (provided for completeness, not as answers)

The external verification of 2026-08-19 (IR-002 Appendix I, `IRB-02`) found:
the **Amendment Ordinance No. 23 of 2026 (5 February 2026)** narrows the
obligation to **at least one synchronised real-time copy within Bangladesh**,
applicable only to *restricted personal data* and processors designated
Critical Information Infrastructure (35 institutions designated to date).
Counsel confirms or refutes this reading — the programme does not rely on it
until then (interim: `D-013` Option A is built).

## 5. Deliverable and acceptance

- **Form:** written opinion, per-question answers, citing the statutory
  instrument and section for each answer; addressed to the Board.
- **Acceptance:** every question answered with a definite position; "it
  depends" is acceptable only with the dependency named and testable.
- **On receipt:** `D-013` is taken within one working day using the prepared
  option table (`docs/decisions/D-013-split-residency.md` §2); `P01-M10-T03`
  verifies `B-02` closed at Gate `G0a`.

## 6. Handling

Attorney-client privileged. The opinion itself is stored outside the
repository; the `D-013` ADR records only its conclusions and the date.
No personal data of any kind accompanies this engagement.

---

## 7. Draft engagement letter (ready for signature — the T01 "Produces" artefact)

> 1000FiX Services Limited ("the Company"), Dhaka, Bangladesh
>
> [Date] — addressed to [Counsel firm], Dhaka
>
> **Re: Engagement for a written legal opinion on data-residency obligations
> under the Personal Data Protection Act 2026 (as amended)**
>
> Dear [Counsel],
>
> The Company engages your firm to provide a **written legal opinion** on five
> questions concerning data residency under the Personal Data Protection Act
> 2026 (including the Amendment Ordinance No. 23 of 2026) and any subordinate
> instruments in force at the date of your opinion. The opinion is required to
> support an architecture decision ("D-013") of the Company's ERP programme.
>
> **The five questions** — your opinion must answer each in writing, citing
> the statutory instrument and section relied upon:
>
> **Q1.** Which of the Company's fields fall within the Act's defined term
> "restricted personal data" — field by field, against the candidate list
> annexed (Annex A: 22 fields across 9 groups, each naming its system model)?
>
> **Q2.** Is the obligation a synchronised local copy or exclusive local
> storage? If a copy, is a regional primary with a Bangladesh replica
> compliant?
>
> **Q3.** Is the Company, or any part of it, capable of Critical Information
> Infrastructure designation? What triggers it, and what changes if a client
> of the Company is designated?
>
> **Q4.** What does "large-scale transfer" mean quantitatively for the
> restricted categories, and what notification and safeguard duties attach?
>
> **Q5.** What is required by approximately 13 May 2027 specifically, as
> distinct from what is good practice?
>
> **Materials:** Annex A (candidate field classification); the residency
> architecture description and the three option architectures (Annex B);
> the Company's privacy-control and trust-zone summaries (Annex C).
>
> **Deliverable and form:** a written opinion addressed to the Board,
> answering each question with a definite position. "It depends" is
> acceptable only where the dependency is named and testable. **Timeliness is
> material:** the Company's build plan holds a provisional architecture
> until your opinion is received; please indicate your delivery date on
> signature (the Company's planning assumption is 6–10 weeks).
>
> **Fees and terms:** [as per your engagement terms attached].
>
> Yours faithfully,
>
> _________________________________
> For and on behalf of 1000FiX Services Limited
> [Name, title]
>
> **Accepted:**
> _________________________________
> For and on behalf of [Counsel firm]
> [Name, title]     Date: ____________

*Annexes A–C are the sections of this folder's companion documents
(`field-classification-candidates.md`; `D-013-split-residency.md` §2; TSS
§14.4 extract) — attach on issue.*
