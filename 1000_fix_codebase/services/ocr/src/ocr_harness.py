"""ocr — P06-M08-T08 (INT-044; CD-M24-nn-adjacent).

Bengali OCR accuracy must be MEASURED, not assumed. This scaffold carries
the measurement harness contract: a scored evaluation against a labelled
corpus, not a vendor demo.

Workstation behaviour: dry-run. The engine (INT-044 vendor component)
plugs in behind `recognise()`; the harness runs wherever images exist.

The metric that matters is per-field accuracy on DOCUMENTS WE SEE (job
cards, NIDs, brand invoices), not generic Bengali OCR benchmarks.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    image_path: str
    expected_fields: dict[str, str]   # {"nid_number": "...", "name_bn": "..."}


@dataclass
class EvaluationResult:
    cases: int = 0
    field_hits: int = 0
    field_total: int = 0
    per_case: list = None

    def __post_init__(self):
        if self.per_case is None:
            self.per_case = []

    @property
    def field_accuracy(self) -> float:
        return round(100.0 * self.field_hits / self.field_total, 2) if self.field_total else 0.0


def evaluate(cases: list[EvaluationCase], recogniser) -> EvaluationResult:
    """Score a recogniser (callable: image_path -> dict[str, str]) against
    the labelled corpus. EXACT match per field — fuzzy credit is how OCR
    accuracy gets flattered into uselessness."""
    result = EvaluationResult(cases=len(cases))
    for case in cases:
        recognised = recogniser(case.image_path)
        hits = 0
        for field, expected in case.expected_fields.items():
            result.field_total += 1
            if str(recognised.get(field, "")).strip() == expected.strip():
                hits += 1
                result.field_hits += 1
        result.per_case.append({"case_id": case.case_id, "hits": hits,
                                "total": len(case.expected_fields)})
    return result


def dry_run_recogniser(image_path: str) -> dict[str, str]:
    """The workstation stand-in: recognises nothing, honestly."""
    return {}


def main() -> None:
    corpus = Path(__file__).resolve().parents[1] / "evaluation" / "corpus.json"
    cases = [EvaluationCase(c["case_id"], c["image"], c["expected"])
             for c in json.loads(corpus.read_text(encoding="utf-8"))] if corpus.exists() else []
    result = evaluate(cases, dry_run_recogniser)
    print(json.dumps({"cases": result.cases,
                      "field_accuracy": result.field_accuracy,
                      "note": "dry-run recogniser — the labelled corpus and the INT-044 engine land with the sandbox"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
