"""stt — P11-M04 (CD-M26-nn; INT-045): Bengali speech-to-text.

The speech-to-text service for technician voice notes and contact-centre
calls. Bengali STT accuracy must be measured, not assumed — this module
provides the scoring framework (WER calculation) and a pluggable backend
interface so the actual STT engine (Whisper, Wav2Vec2, or a cloud API)
can be swapped without changing the contract.

HONESTY CONTRACT (GV-009): NO STT backend is deployed in this stack. Without
one, ``transcribe()`` REFUSES with ``STTBackendNotConfigured`` — it never
echoes its input back as a "transcript". The optional backend seam is a
whisper.cpp-style HTTP server configured through env (``STT_BACKEND``,
``STT_BACKEND_URL``). Likewise, the drift tracker carries no invented
production WER: without a measured baseline it reports
``BASELINE_UNMEASURED``.

PDPA: transcript processing has a confirmed legal basis BEFORE any
mining (P11-M04-T04). The DPIA from W2 recorded no confirmed basis;
this module enforces the gate.
"""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from datetime import UTC
from typing import ClassVar


class STTBackendNotConfigured(RuntimeError):
    """Raised when transcribe() is called without a real STT backend.

    The previous behaviour echoed the caller's text back as the
    "transcript"; that fabricated output is gone.
    """


@dataclass
class TranscriptionResult:
    text: str
    language: str = "bn"
    confidence: float = 0.0
    duration_seconds: float = 0.0
    legal_basis_confirmed: bool = False
    backend: str = ""


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
        return WERScore(
            reference=reference, hypothesis=hypothesis, wer=0.0 if not hyp_words else 1.0
        )

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
                dp[i][j] = 1 + min(
                    dp[i - 1][j],  # deletion
                    dp[i - 1][j - 1],  # substitution
                    dp[i][j - 1],  # insertion
                )

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
    return WERScore(
        reference=reference,
        hypothesis=hypothesis,
        substitutions=subs,
        insertions=ins,
        deletions=dels,
        wer=round(wer, 4),
    )


def resolve_backend() -> str | None:
    """Returns the configured backend label, or None when no backend exists.

    ``STT_BACKEND`` selects the engine; today the only implemented seam is
    ``whisper-server`` (a whisper.cpp-compatible HTTP server at
    ``STT_BACKEND_URL``).
    """
    backend = os.environ.get("STT_BACKEND", "").strip()
    if not backend:
        return None
    if backend != "whisper-server":
        raise ValueError(
            f"unknown STT_BACKEND {backend!r}: supported values are 'whisper-server' "
            "(or unset, which disables transcription honestly)"
        )
    return backend


def _transcribe_via_whisper_server(audio: bytes, language: str) -> tuple[str, float]:
    """Calls a whisper.cpp-style /v1/audio/transcriptions endpoint."""
    url = os.environ.get("STT_BACKEND_URL", "").strip()
    if not url:
        raise STTBackendNotConfigured(
            "STT_BACKEND=whisper-server requires STT_BACKEND_URL (e.g. "
            "http://127.0.0.1:9000); no URL is configured"
        )
    req = urllib.request.Request(  # noqa: S310 - URL from operator-configured env
        url.rstrip("/") + "/v1/audio/transcriptions",
        data=audio,
        headers={"Content-Type": "audio/wav", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
        payload = json.loads(resp.read().decode("utf-8"))
    return payload.get("text", ""), float(payload.get("confidence", 0.0))


def transcribe(
    audio_duration: float, legal_basis: bool = False, audio: bytes | None = None
) -> TranscriptionResult:
    """Transcribe an audio segment with a REAL backend.

    The legal_basis gate is enforced first: without a confirmed basis the
    transcription is REFUSED. Without a configured backend the call FAILS
    loudly with STTBackendNotConfigured — it never echoes an input string
    back as if it were a transcript.
    """
    if not legal_basis:
        raise ValueError(
            "PDPA: transcript processing requires a confirmed legal basis "
            "(P11-M04-T04). The DPIA recorded no confirmed basis for "
            "transcript mining; confirm it before processing."
        )

    backend = resolve_backend()
    if backend is None:
        raise STTBackendNotConfigured(
            "no STT backend is configured: set STT_BACKEND (and STT_BACKEND_URL) "
            "to enable transcription. Refusing to fabricate a transcript."
        )
    if audio is None:
        raise ValueError("audio payload is required: no backend can transcribe nothing")

    if backend == "whisper-server":
        text, confidence = _transcribe_via_whisper_server(audio, "bn")
    else:  # pragma: no cover - resolve_backend() rejects unknown values first
        raise ValueError(f"unknown STT_BACKEND {backend!r}")

    return TranscriptionResult(
        text=text,
        confidence=confidence,
        duration_seconds=audio_duration,
        legal_basis_confirmed=True,
        backend=backend,
    )


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


# --- M26 W8 STT Productionisation & Drift Monitoring Loop ---

try:
    import ml_gateway
except ImportError:
    try:
        import sys
        from pathlib import Path

        _ml_gw_path = Path(__file__).resolve().parents[2] / "ml-gateway" / "src"
        if str(_ml_gw_path) not in sys.path:
            sys.path.insert(0, str(_ml_gw_path))
        import ml_gateway
    except Exception:
        ml_gateway = None


class STTProductionTracker:
    """Tracks evaluated Bengali STT accuracy (WER) and monitors drift.

    There is no deployed STT backend and no measured production baseline:
    the tracker therefore reports ``baseline_wer=None`` and the drift status
    ``BASELINE_UNMEASURED`` until a gateway model card carries a REAL
    measured ``metrics.wer``. It never seeds itself with an invented WER.
    """

    # Honest card used when no ml_gateway is importable: nothing is claimed.
    UNREGISTERED_MODEL_CARD: ClassVar[dict] = {
        "version": "unregistered",
        "stage": "not-deployed",
        "type": "external-backend-required",
        "model_backend": None,
        "metrics": {},
    }

    def __init__(self):
        self.evaluation_history: list[dict] = []
        self.active_batch_count: int = 0
        self.total_samples: int = 0
        self.last_drift_check: dict | None = None

    def _baseline_wer(self) -> float | None:
        """The gateway card's measured WER, or None when unmeasured."""
        if ml_gateway:
            info = ml_gateway.get_model_info("bengali-stt")
            if info:
                return info.get("metrics", {}).get("wer")
        return None

    def record_evaluation_batch(self, batch_id: str, pairs: list[tuple[str, str]]) -> dict:
        """Evaluate a batch of (reference, hypothesis) transcript pairs."""
        if not pairs:
            return {"batch_id": batch_id, "samples": 0, "average_wer": 0.0}

        scores = [compute_wer(ref, hyp) for ref, hyp in pairs]
        avg_wer = sum(s.wer for s in scores) / len(scores)
        subs = sum(s.substitutions for s in scores)
        inss = sum(s.insertions for s in scores)
        dels = sum(s.deletions for s in scores)
        cls_name = classify_bn_accuracy(avg_wer)

        from datetime import datetime

        batch_summary = {
            "batch_id": batch_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "samples": len(pairs),
            "average_wer": round(avg_wer, 4),
            "substitutions": subs,
            "insertions": inss,
            "deletions": dels,
            "accuracy_class": cls_name,
        }
        self.evaluation_history.append(batch_summary)
        self.total_samples += len(pairs)
        self.active_batch_count += 1
        return batch_summary

    def check_drift_and_retrain(self, threshold: float = 0.15) -> dict:
        """Check if evaluated WER drifted from the baseline in ml_gateway,
        triggering retraining bookkeeping if breached.

        Drift is only decidable against a MEASURED baseline: without one the
        check reports BASELINE_UNMEASURED (drift_detected=None) instead of
        inventing a baseline.
        """
        from datetime import datetime

        now_ts = datetime.now(UTC).isoformat()

        baseline_wer = self._baseline_wer()
        recent_wers = [b["average_wer"] for b in self.evaluation_history[-5:]]
        current_wer = sum(recent_wers) / len(recent_wers) if recent_wers else baseline_wer

        retraining_event = None
        if baseline_wer is None:
            # No measured baseline exists (no backend, never evaluated in
            # production): drift is UNMEASURABLE, never "healthy".
            status_result = {
                "timestamp": now_ts,
                "baseline_wer": None,
                "current_wer": None if current_wer is None else round(current_wer, 4),
                "drift_detected": None,
                "threshold": threshold,
                "retraining_event": None,
                "status": "BASELINE_UNMEASURED",
                "reason": "no measured WER baseline exists for bengali-stt; "
                "drift cannot be evaluated",
            }
            self.last_drift_check = status_result
            return status_result

        drift = False
        if ml_gateway and hasattr(ml_gateway, "detect_drift"):
            drift = ml_gateway.detect_drift(
                "bengali-stt", actual=current_wer, predicted=baseline_wer, threshold=threshold
            )
        else:
            drift = (
                (current_wer - baseline_wer) / baseline_wer > threshold
                if baseline_wer > 0
                else False
            )

        if drift and ml_gateway and hasattr(ml_gateway, "trigger_retraining"):
            retraining_event = ml_gateway.trigger_retraining(
                "bengali-stt",
                trigger_reason=f"WER drifted from {baseline_wer:.3f} to {current_wer:.3f} (threshold={threshold})",
            )

        status_result = {
            "timestamp": now_ts,
            "baseline_wer": round(baseline_wer, 4),
            "current_wer": round(current_wer, 4),
            "drift_detected": drift,
            "threshold": threshold,
            "retraining_event": retraining_event,
            "status": "RETRAINED"
            if retraining_event
            else ("HEALTHY" if not drift else "DRIFT_DETECTED"),
        }
        self.last_drift_check = status_result
        return status_result

    def get_dashboard_metrics(self) -> dict:
        """Generate STT dashboard payload for the Analytics API.

        Every figure is measured or explicitly None - no invented WER/CER/RTF.
        """
        from datetime import datetime

        now_ts = datetime.now(UTC).isoformat()

        model_info = (ml_gateway.get_model_info("bengali-stt") if ml_gateway else None) or dict(
            self.UNREGISTERED_MODEL_CARD
        )

        metrics = model_info.get("metrics", {})
        recent_wers = [b["average_wer"] for b in self.evaluation_history]
        measured_wer = round(sum(recent_wers) / len(recent_wers), 4) if recent_wers else None
        baseline_wer = metrics.get("wer")

        return {
            "timestamp": now_ts,
            "model_name": "bengali-stt",
            "active_version": model_info.get("version", "unregistered"),
            "stage": model_info.get("stage", "not-deployed"),
            "model_architecture": model_info.get("type", "external-backend-required"),
            "model_backend": model_info.get("model_backend"),
            "backend_configured": bool(os.environ.get("STT_BACKEND")),
            "baseline_wer": baseline_wer,
            "measured_wer": measured_wer,
            "accuracy_class": (
                classify_bn_accuracy(measured_wer) if measured_wer is not None else "unmeasured"
            ),
            "total_transcriptions_evaluated": self.total_samples,
            "evaluation_batches_recorded": len(self.evaluation_history),
            "metrics_breakdown": {
                "character_error_rate": metrics.get("cer"),
                "real_time_factor_rtf": metrics.get("rtf"),
                "supported_dialects": ["Standard Bengali (Dhaka/Chittagong/Sylhet)"],
                "audio_formats": ["WAV", "OGG_OPUS", "MP3", "FLAC"],
            },
            "drift_monitoring": self.last_drift_check
            or {"drift_detected": None, "status": "BASELINE_UNMEASURED", "threshold": 0.15},
            "pdpa_compliance": {
                "legal_basis_gate_enforced": True,
                "dpia_reference": "DPIA-2026-W2-VOICE",
                "retention_policy": "Transcripts retained for 90 days with audit logging",
            },
            "recent_batches": self.evaluation_history[-5:],
        }


# Singleton tracker instance for the module
_DEFAULT_TRACKER = STTProductionTracker()


def get_stt_dashboard_metrics() -> dict:
    return _DEFAULT_TRACKER.get_dashboard_metrics()
