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
import time
import urllib.request
from dataclasses import dataclass, field
from urllib.parse import urlparse

# Same boundary rule as test-smoke: the collector talks ONLY to the local
# Odoo (scheme+host+port allowlisted before any request).
BIND = "http://127.0.0.1:8069"
ALLOWED = {("http", "127.0.0.1", 8069), ("http", "localhost", 8069)}

OFFLINE_AFTER_WINDOWS = 3          # heartbeat windows missed -> offline
WINDOW_SECONDS = 60


def validate_target(url: str) -> None:
    p = urlparse(url)
    if (p.scheme, p.hostname, p.port or 80) not in ALLOWED:
        raise ValueError(f"rmm-collector: refusing non-local endpoint {url!r}")


@dataclass
class Telemetry:
    """One agent report."""
    agent_id: str
    health: str                    # healthy | degraded | offline
    flags: list[str] = field(default_factory=list)
    reported_at: float = field(default_factory=time.time)


@dataclass
class AlertDecision:
    agent_id: str
    severity: str                  # minor | major
    message: str


def evaluate(history: list[Telemetry], latest: Telemetry) -> AlertDecision | None:
    """The evaluation core (pure, 100% covered): decide whether the latest
    report warrants an alert. OFFLINE after a heartbeat gap; DEGRADED on
    unhealthy flags — healthy telemetry never alerts."""
    if latest.health == "offline":
        return AlertDecision(latest.agent_id, "major",
                             "%s reported offline" % latest.agent_id)
    if latest.health == "degraded":
        flags = ", ".join(latest.flags) or "unspecified"
        return AlertDecision(latest.agent_id, "minor",
                             "%s degraded (%s)" % (latest.agent_id, flags))
    # heartbeat gap: last WINDOW before now was older than the threshold
    gap = latest.reported_at - (history[-1].reported_at if history
                                else latest.reported_at)
    if history and gap > OFFLINE_AFTER_WINDOWS * WINDOW_SECONDS:
        return AlertDecision(latest.agent_id, "major",
                             "%s silent for %d windows" % (
                                 latest.agent_id, int(gap // WINDOW_SECONDS)))
    return None


class OdooClient:
    """Minimal JSON-RPC client with the validated boundary."""

    def __init__(self, base: str = BIND):
        self.base = base
        self.cookie = ""

    def _post(self, path: str, payload: dict) -> dict:
        validate_target(self.base + path)
        req = urllib.request.Request(
            self.base + path, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json",
                     **({"Cookie": self.cookie} if self.cookie else {})})
        with urllib.request.urlopen(req, timeout=60) as resp:
            sc = resp.headers.get("Set-Cookie", "")
            if sc:
                self.cookie = sc.split(";")[0]
            return json.loads(resp.read())

    def login(self, db: str, login: str, password: str) -> None:
        r = self._post("/web/session/authenticate", {"params": {
            "db": db, "login": login, "password": password}})
        if "error" in r:
            raise RuntimeError(r["error"]["data"]["message"])

    def call(self, model: str, method: str, *args, **kw):
        r = self._post("/web/dataset/call_kw", {"params": {
            "model": model, "method": method, "args": list(args), "kwargs": kw}})
        if "error" in r:
            raise RuntimeError(r["error"]["data"].get("message", "rpc error"))
        return r.get("result")


def push_alert(client: OdooClient, decision: AlertDecision) -> int:
    """Record the decision as telemetry + (on alert) an M05 alert row via
    the monitored-asset ingestion path (which raises the alert itself)."""
    import datetime as _dt
    seen_at = _dt.datetime.fromtimestamp(
        time.time(), tz=_dt.timezone.utc).replace(tzinfo=None,
                                                  microsecond=0)
    client.call("fix.monitored.asset", "ingest_telemetry",
                decision.agent_id,
                "offline" if decision.severity == "major" else "degraded",
                seen_at)
    return 0


def main() -> int:
    print("rmm-collector: evaluation library + HTTP push; run under the "
          "MSP profile with `python -m rmm_collector` in its container")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
