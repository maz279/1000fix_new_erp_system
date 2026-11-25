"""rmm-collector — P08-M07-T04 (CD-M05-04 companion; TSS §20.2 W5).

An L5 standalone service: endpoint-telemetry ingestion and alert
evaluation for the MSP business (M05). PURE stdlib, no Odoo imports —
unit-testable anywhere; it speaks HTTP to the Odoo JSON-RPC surface
(the same validated-boundary client pattern as test-smoke) and decides
when telemetry becomes an ALERT (journey 6's opening).

Decision rules (M05):
  - heartbeat gap      -> OFFLINE alert (major)   after N missed windows
  - reported condition -> DEGRADED alert (minor) on unhealthy flags
The collector NEVER writes Odoo directly: it evaluates, then pushes the
decision through the validated client. Idempotent per (agent, window).
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlparse

# Boundary rule (same as test-smoke): every request target is allowlisted by
# scheme+host+port BEFORE it is sent. Default = the local Odoo only. A
# deployment names its ONE Odoo target in FIX_RMM_ODOO_URL; that origin (and
# nothing else) joins the allowlist after validate_configured_target().
BIND = "http://127.0.0.1:8069"
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}
TARGET_ENV = "FIX_RMM_ODOO_URL"
_DEFAULT_PORTS = {"http": 80, "https": 443}
# Plain http is accepted only for loopback and cluster-/compose-internal
# service names (single label such as `odoo`, or *.svc / *.svc.cluster.local);
# any other host must be https.
_INTERNAL_HOST = re.compile(
    r"^(?:localhost|127\.0\.0\.1|[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"
    r"(?:\.[a-z0-9-]+)*\.svc(?:\.cluster\.local)?|[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)$"
)

OFFLINE_AFTER_WINDOWS = 3  # heartbeat windows missed -> offline
WINDOW_SECONDS = 60


def _origin(url: str) -> tuple[str, str | None, int]:
    p = urlparse(url)
    return (p.scheme, p.hostname, p.port or _DEFAULT_PORTS.get(p.scheme, 80))


def validate_configured_target(url: str) -> str:
    """Validate a deployment-supplied Odoo base URL (FIX_RMM_ODOO_URL).

    Only an origin is accepted (scheme://host[:port], optional trailing '/'):
    no credentials, path, query or fragment. https is required unless the host
    is loopback or a compose/cluster-internal service name. Returns the URL
    without a trailing slash; raises ValueError otherwise."""
    raw = url.strip()
    p = urlparse(raw)
    if p.scheme not in _DEFAULT_PORTS or not p.hostname:
        raise ValueError(f"rmm-collector: {TARGET_ENV} must be an http(s) origin, got {url!r}")
    if p.username or p.password:
        raise ValueError(f"rmm-collector: {TARGET_ENV} must not embed credentials")
    if p.path not in ("", "/") or p.params or p.query or p.fragment:
        raise ValueError(f"rmm-collector: {TARGET_ENV} must be an origin only, got {url!r}")
    try:
        p.port  # noqa: B018 - raises ValueError on an invalid port
    except ValueError as exc:
        raise ValueError(f"rmm-collector: {TARGET_ENV} has an invalid port: {exc}") from exc
    if p.scheme == "http" and not _INTERNAL_HOST.match(p.hostname):
        raise ValueError(
            f"rmm-collector: {TARGET_ENV} must use https for non-internal host {p.hostname!r}"
        )
    return raw.rstrip("/")


def configured_target() -> str:
    """The Odoo base URL: FIX_RMM_ODOO_URL when set (validated), else BIND."""
    raw = os.environ.get(TARGET_ENV, "").strip()
    return validate_configured_target(raw) if raw else BIND


def allowed_targets() -> set[tuple[str, str | None, int]]:
    return ALLOWED | {_origin(configured_target())}


def validate_target(url: str) -> None:
    if _origin(url) not in allowed_targets():
        raise ValueError(f"rmm-collector: refusing non-local endpoint {url!r}")


@dataclass
class Telemetry:
    """One agent report."""

    agent_id: str
    health: str  # healthy | degraded | offline
    flags: list[str] = field(default_factory=list)
    reported_at: float = field(default_factory=time.time)


@dataclass
class AlertDecision:
    agent_id: str
    severity: str  # minor | major
    message: str


def evaluate(history: list[Telemetry], latest: Telemetry) -> AlertDecision | None:
    """The evaluation core (pure, 100% covered): decide whether the latest
    report warrants an alert. OFFLINE after a heartbeat gap; DEGRADED on
    unhealthy flags — healthy telemetry never alerts."""
    if latest.health == "offline":
        return AlertDecision(latest.agent_id, "major", f"{latest.agent_id} reported offline")
    if latest.health == "degraded":
        flags = ", ".join(latest.flags) or "unspecified"
        return AlertDecision(latest.agent_id, "minor", f"{latest.agent_id} degraded ({flags})")
    # heartbeat gap: last WINDOW before now was older than the threshold
    gap = latest.reported_at - (history[-1].reported_at if history else latest.reported_at)
    if history and gap > OFFLINE_AFTER_WINDOWS * WINDOW_SECONDS:
        return AlertDecision(
            latest.agent_id,
            "major",
            f"{latest.agent_id} silent for {int(gap // WINDOW_SECONDS)} windows",
        )
    return None


class OdooClient:
    """Minimal JSON-RPC client with the validated boundary."""

    def __init__(self, base: str | None = None):
        # default = the configured target (FIX_RMM_ODOO_URL) or the local Odoo
        self.base = base if base is not None else configured_target()
        self.cookie = ""

    def _post(self, path: str, payload: dict) -> dict:
        validate_target(self.base + path)
        req = urllib.request.Request(  # noqa: S310 - URL pinned by validate_target() above
            self.base + path,
            data=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310 - URL pinned by validate_target() above
            sc = resp.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(resp.read())

    def login(self, db: str, login: str, password: str) -> None:
        r = self._post(
            "/web/session/authenticate",
            {"params": {"db": db, "login": login, "password": password}},
        )
        if "error" in r:
            raise RuntimeError(r["error"]["data"]["message"])

    def call(self, model: str, method: str, *args, **kw):
        r = self._post(
            "/web/dataset/call_kw",
            {"params": {"model": model, "method": method, "args": list(args), "kwargs": kw}},
        )
        if "error" in r:
            raise RuntimeError(r["error"]["data"].get("message", "rpc error"))
        return r.get("result")


def push_alert(client: OdooClient, decision: AlertDecision) -> int:
    """Record the decision as telemetry + (on alert) an M05 alert row via
    the monitored-asset ingestion path (which raises the alert itself)."""
    import datetime as _dt

    seen_at = _dt.datetime.fromtimestamp(time.time(), tz=_dt.UTC).replace(
        tzinfo=None, microsecond=0
    )
    client.call(
        "fix.monitored.asset",
        "ingest_telemetry",
        decision.agent_id,
        "offline" if decision.severity == "major" else "degraded",
        seen_at,
    )
    return 0


def main() -> int:
    print(
        "rmm-collector: evaluation library + HTTP push; run under the "
        "MSP profile with `python -m rmm_collector` in its container"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
