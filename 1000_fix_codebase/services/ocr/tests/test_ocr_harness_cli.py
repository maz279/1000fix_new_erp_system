"""ocr harness CLI and result-container tests — P06-M08-T08 (INT-044)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ocr_harness
from ocr_harness import EvaluationCase, EvaluationResult, evaluate


def _point_module_at(monkeypatch, root: Path) -> Path:
    """main() locates the corpus relative to the module file; re-root it."""
    src = root / "src"
    src.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ocr_harness, "__file__", str(src / "ocr_harness.py"))
    return root / "evaluation" / "corpus.json"


def test_explicit_per_case_list_is_kept():
    seed = [{"case_id": "old", "hits": 1, "total": 1}]
    result = EvaluationResult(cases=1, per_case=seed)
    assert result.per_case is seed


def test_default_per_case_lists_are_independent():
    a, b = EvaluationResult(), EvaluationResult()
    a.per_case.append("x")
    assert b.per_case == []


def test_empty_corpus_accuracy_is_zero():
    result = evaluate([], lambda p: {})
    assert result.cases == 0
    assert result.field_accuracy == 0.0


def test_per_case_breakdown_and_rounding():
    cases = [
        EvaluationCase("c1", "a.png", {"a": "1", "b": "2", "c": "3"}),
        EvaluationCase("c2", "b.png", {"a": "1"}),
    ]
    seen = []

    def recogniser(path):
        seen.append(path)
        return {"a": 1, "b": "x"} if path == "a.png" else {"a": "1"}

    result = evaluate(cases, recogniser)
    assert seen == ["a.png", "b.png"]
    assert result.per_case == [
        {"case_id": "c1", "hits": 1, "total": 3},
        {"case_id": "c2", "hits": 1, "total": 1},
    ]
    assert (result.field_hits, result.field_total) == (2, 4)
    assert result.field_accuracy == 50.0


def test_main_scores_corpus_with_dry_run_recogniser(monkeypatch, tmp_path, capsys):
    corpus = _point_module_at(monkeypatch, tmp_path)
    corpus.parent.mkdir(parents=True)
    corpus.write_text(
        json.dumps(
            [
                {"case_id": "nid-1", "image": "nid-1.png", "expected": {"nid": "123"}},
                {"case_id": "jc-1", "image": "jc-1.png", "expected": {"name_bn": "রহিম"}},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    ocr_harness.main()
    out = json.loads(capsys.readouterr().out)
    assert out["cases"] == 2
    assert out["field_accuracy"] == 0.0
    assert "dry-run recogniser" in out["note"]


def test_main_without_corpus_reports_zero_cases(monkeypatch, tmp_path, capsys):
    _point_module_at(monkeypatch, tmp_path)
    ocr_harness.main()
    out = json.loads(capsys.readouterr().out)
    assert out["cases"] == 0
    assert out["field_accuracy"] == 0.0
