"""ollama_client.py — the self-hosted generation client for M32 (S7).

WHY THIS EXISTS, and why it is not a vendor guess. The estate has already
CHOSEN its model runtime and written the choice down in three places:

  * `cd_contact_centre/__manifest__.py`: "M32 runs on self-hosted Ollama
    (customer data must not leave the Company under PDPA transfer
    restrictions)";
  * `services/conversational-ai/benchmark_ollama_latency.py`, which pins the
    image digest (sha256:926d40fd…) and records the latency SLAs the choice
    was made against — voice IVR <= 400 ms, text chat <= 2000 ms;
  * the A03 gap plan's S7 row, which asks for exactly this behind the
    existing guardrail and dataset gates.

So the runtime is settled and its HTTP contract is a documented, stable,
public one (`POST /api/generate`, `POST /api/chat`). Implementing it is
executing a decision, not inventing a contract — which is the distinction
that matters, and the reason the CPaaS *vendor* question is still open while
this one is not.

DESIGN RULES, all of which exist because this talks to a network:

1. SSRF-guarded like the notification adapters: the endpoint must resolve to
   loopback or a known in-cluster service name. A model endpoint that can be
   pointed at an arbitrary host is an exfiltration channel for exactly the
   customer data PDPA says must not leave.
2. Redirects are refused. A redirect from a model endpoint is a policy
   violation, not something to follow.
3. Streaming is off. The caller needs one complete answer to put through a
   guardrail before any of it reaches a customer; a streamed token is a
   token nobody has checked yet.
4. Timeouts come from the recorded SLA budgets, not from a default, and a
   timeout is a FAILURE with a reason rather than an exception that aborts a
   conversation.
5. Nothing is retried. A generation retry doubles the latency budget and the
   caller has a human-handoff path that is better than a slow answer.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

# The environment variable holding the runtime endpoint. Env, not database:
# a model endpoint is deployment configuration and must not be settable by
# anyone with write access to a configuration table.
URL_ENV = "FIX_OLLAMA_URL"
MODEL_ENV = "FIX_OLLAMA_MODEL"

# Latency budgets from benchmark_ollama_latency.py. A request that cannot
# answer inside its budget is useless to the caller: a contact centre agent
# waiting six seconds has already started typing.
TIMEOUT_SECONDS = {
    "voice": 1.0,  # the recorded voice SLA is 400 ms; 1 s is the hard ceiling
    "chat": 5.0,  # the recorded text SLA is 2000 ms
    "batch": 30.0,  # offline work: drafts, translation backfill, mining
}
DEFAULT_PROFILE = "chat"

# SSRF allowlist. Ollama is SELF-HOSTED by mandate, so the only legitimate
# hosts are loopback and the compose/cluster service name.
_ALLOWED_HOSTS = frozenset(
    {
        "127.0.0.1",
        "localhost",
        "::1",
        "ollama",
        "ollama.fix.svc.cluster.local",
        "conversational-ai",
    }
)


class GenerationRefused(RuntimeError):
    """The request was refused before anything left the process."""


@dataclass
class GenerationResult:
    ok: bool
    text: str = ""
    model: str = ""
    detail: str = ""
    latency_ms: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class _NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GenerationRefused(f"model endpoint attempted a redirect to {newurl}; refused")


_OPENER = urllib.request.build_opener(_NoRedirects)


def _validate_url(url: str) -> str:
    """Refuse anything that is not a self-hosted http endpoint."""
    if not url:
        raise GenerationRefused(f"{URL_ENV} is not set")
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise GenerationRefused(f"model endpoint scheme {parsed.scheme!r} refused")
    host = (parsed.hostname or "").lower()
    if host not in _ALLOWED_HOSTS:
        raise GenerationRefused(
            f"model endpoint host {host!r} is not a self-hosted host. M32 runs "
            "self-hosted because customer data must not leave the Company "
            "under PDPA transfer restrictions; an arbitrary endpoint would be "
            "an exfiltration channel for exactly that data."
        )
    if parsed.query:
        raise GenerationRefused("model endpoint must not carry a query string")
    return url


def endpoint() -> str:
    return os.environ.get(URL_ENV, "").strip()


def model_name() -> str:
    return os.environ.get(MODEL_ENV, "").strip()


def configured() -> bool:
    """Is a self-hosted runtime actually reachable-by-configuration?

    False is a normal, reportable answer: the caller falls back to its
    rule-based grounders and says so, rather than failing.
    """
    try:
        _validate_url(endpoint())
    except GenerationRefused:
        return False
    return bool(model_name())


def generate(
    prompt: str,
    *,
    system: str = "",
    profile: str = DEFAULT_PROFILE,
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> GenerationResult:
    """One non-streaming completion. Never raises for a transport failure.

    A low default temperature on purpose: this serves transactional intents
    and agent assistance, where a surprising answer is a worse answer.
    """
    url_base = endpoint()
    try:
        _validate_url(url_base)
    except GenerationRefused as exc:
        return GenerationResult(False, detail=str(exc))
    model = model_name()
    if not model:
        return GenerationResult(
            False,
            detail=f"{MODEL_ENV} is not set, so no model was named and nothing was " "generated.",
        )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # see rule 3 in the module docstring
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if system:
        payload["system"] = system

    url = url_base.rstrip("/") + "/api/generate"
    timeout = TIMEOUT_SECONDS.get(profile, TIMEOUT_SECONDS[DEFAULT_PROFILE])
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310 - host/scheme validated above
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )

    import time

    started = time.perf_counter()
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            raw = response.read()
    except GenerationRefused as exc:
        return GenerationResult(False, model=model, detail=str(exc))
    except TimeoutError as exc:
        return GenerationResult(
            False,
            model=model,
            detail=f"model did not answer within the {timeout:.1f}s {profile} budget ({exc})",
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
    except (urllib.error.URLError, OSError) as exc:
        return GenerationResult(False, model=model, detail=f"model endpoint error: {exc}")
    latency_ms = int((time.perf_counter() - started) * 1000)

    try:
        body = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        return GenerationResult(
            False,
            model=model,
            detail=f"model reply was not JSON: {exc}",
            latency_ms=latency_ms,
        )
    text = (body.get("response") or "").strip()
    if not text:
        return GenerationResult(
            False,
            model=model,
            latency_ms=latency_ms,
            detail="model returned an empty completion",
        )
    return GenerationResult(
        True,
        text=text,
        model=model,
        latency_ms=latency_ms,
        prompt_tokens=int(body.get("prompt_eval_count") or 0),
        completion_tokens=int(body.get("eval_count") or 0),
    )


def translate(text: str, target_language: str, *, profile: str = "batch") -> GenerationResult:
    """Translate a transcript turn between Bengali and English.

    A tightly-bounded instruction on purpose. This is working text for an
    agent, not published copy: T08 forbids machine-translated AUTHORED
    content (intent utterances, templates), and the distinction is kept by
    the CALLER recording `translation_engine='llm'` on the turn.
    """
    language = {"bn": "Bengali", "en": "English"}.get(target_language, target_language)
    return generate(
        f"Translate the following customer-service message into {language}. Reply with "
        "the translation only, with no preamble, no transliteration and no "
        f"explanation.\n\n{text}",
        system="You are a translator for a Bangladeshi electronics repair "
        "company. Preserve order numbers, model names and amounts exactly.",
        profile=profile,
        temperature=0.0,
    )


__all__ = [
    "MODEL_ENV",
    "TIMEOUT_SECONDS",
    "URL_ENV",
    "GenerationRefused",
    "GenerationResult",
    "configured",
    "endpoint",
    "generate",
    "model_name",
    "translate",
]
