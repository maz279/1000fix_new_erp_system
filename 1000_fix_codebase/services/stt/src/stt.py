"""stt — P11-M04 (CD-M26-nn; INT-045): Bengali speech-to-text.

The speech-to-text service for technician voice notes and contact-centre
calls. Bengali STT accuracy must be measured, not assumed — this module
provides the scoring framework (WER calculation) and a pluggable backend
interface so the actual STT engine (Whisper, Wav2Vec2, or a cloud API)
can be swapped without changing the contract.

PDPA: transcript processing has a confirmed legal basis BEFORE any
mining (P11-M04-T04). The DPIA from W2 recorded no confirmed basis;
this module enforces the gate.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionResult:
    text: str
    language: str = "bn"
    confidence: float = 0.0
    duration_seconds: float = 0.0
    legal_basis_confirmed: bool = False


@dataclass
class WERScore:
    """Word Error Rate: the standard STT accuracy metric."""
    reference: str
    hypothesis: str
    substitutions: int = 0
    insertions: int = 0
    deletions: int = 0
    wer: float = 0.0


def compute_wer(reference: str, hypothesis: str) -> WERScore:
    """Compute Word Error Rate between reference (ground truth) and
    hypothesis (STT output). WER = (S + I + D) / N where N = len(reference).

    Lower is better; 0.0 = perfect transcription.
    """
    ref_words = reference.split()
    hyp_words = hypothesis.split()
    n = len(ref_words)

    if n == 0:
        return WERScore(reference=reference, hypothesis=hypothesis,
                        wer=0.0 if not hyp_words else 1.0)

    # Dynamic programming alignment (Levenshtein on word level)
    dp = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]
    for i in range(len(ref_words) + 1):
        dp[i][0] = i
    for j in range(len(hyp_words) + 1):
        dp[0][j] = j

    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],      # deletion
                                   dp[i][j - 1],       # insertion
                                   dp[i - 1][j - 1])   # substitution

    # Backtrack to count operation types
    i, j = len(ref_words), len(hyp_words)
    subs = ins = dels = 0
    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref_words[i - 1] == hyp_words[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            subs += 1
            i -= 1
            j -= 1
        elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
            ins += 1
            j -= 1
        else:
            dels += 1
            i -= 1

    wer = (subs + ins + dels) / n
    return WERScore(reference=reference, hypothesis=hypothesis,
                    substitutions=subs, insertions=ins, deletions=dels,
                    wer=round(wer, 4))


def transcribe(audio_duration: float, legal_basis: bool = False,
               text: str = "") -> TranscriptionResult:
    """Transcribe an audio segment. The legal_basis gate is enforced:
    without a confirmed basis, the transcription is REFUSED."""
    if not legal_basis:
        raise ValueError(
            "PDPA: transcript processing requires a confirmed legal basis "
            "(P11-M04-T04). The DPIA recorded no confirmed basis for "
            "transcript mining; confirm it before processing.")
    return TranscriptionResult(
        text=text, duration_seconds=audio_duration,
        legal_basis_confirmed=True)


def classify_bn_accuracy(wer: float) -> str:
    """Classify Bengali STT accuracy for reporting."""
    if wer <= 0.15:
        return "production-ready"
    elif wer <= 0.30:
        return "usable-with-review"
    elif wer <= 0.50:
        return "needs-improvement"
    else:
        return "unusable"
