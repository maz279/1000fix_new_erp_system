# libs/py/fix_residency — THE residency service client (P03-M09-T03, FF-09).
#
# FF-09: this is the ONLY code path that may reach the Bangladesh-resident
# store (Z4). Any other module reaching Z4 directly fails the build (FF-09
# blocking from first build).
#
# Security: SSRF-hardened — the base URL is validated against a strict
# allowlist (loopback or the Docker-network service name only); redirects
# are refused; the scheme is locked to http.
"""fix_residency — the only client of the residency service (FF-09)."""

from __future__ import annotations

import json
import logging
import os
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_TIMEOUT = 10  # seconds

# SSRF allowlist: ONLY these hosts may be reached. The residency service
# runs on loopback (local stub) or the Docker compose network. No external
# host, no cloud metadata endpoint, no private subnet scanning.
_ALLOWED_HOSTS = frozenset({
    "127.0.0.1", "localhost", "::1",
    "residency-stub", "residency-service",  # Docker compose service names
})
_ALLOWED_SCHEMES = frozenset({"http"})  # TLS terminates at the mesh, not here


class ResidencyError(Exception):
    """Raised when the residency service is unreachable or returns an error."""


class ResidencyURLBlocked(ResidencyError):
    """Raised when the configured base URL fails the SSRF allowlist check."""


def _validate_base_url(base_url: str) -> str:
    """Validate the residency base URL against the SSRF allowlist."""
    parsed = urlparse(base_url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        raise ResidencyURLBlocked(
            f"scheme {parsed.scheme!r} not allowed (expected http); "
            f"TLS terminates at the service mesh, not at this client")
    if parsed.hostname not in _ALLOWED_HOSTS:
        raise ResidencyURLBlocked(
            f"host {parsed.hostname!r} not in the residency allowlist "
            f"{sorted(_ALLOWED_HOSTS)}; fix RESIDENCY_BASE in .env")
    return base_url.rstrip("/")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse redirects — a redirect could bypass the allowlist."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: N802
        raise ResidencyURLBlocked(f"redirect to {newurl!r} refused (SSRF protection)")


class ResidencyClient:
    """The sole client of Z4 (the Bangladesh-resident store).

    All classified-field operations (NID, passport, TIN, biometric) go
    through this client. The ORM mixin intercepts writes to classified
    fields and routes them here — enforced by mechanism, not discipline.
    """

    def __init__(self, base_url: str | None = None):
        raw = base_url or os.environ.get("RESIDENCY_BASE", "http://127.0.0.1:8100")
        self._base = _validate_base_url(raw)
        # Redirect-refusing opener; no proxy (the service is always local)
        self._opener = urllib.request.build_opener(_NoRedirect)

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{self._base}{path}"
        data = json.dumps(body).encode("utf-8") if body else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with self._opener.open(req, timeout=_TIMEOUT) as resp:
                if resp.status != 200:
                    raise ResidencyError(f"HTTP {resp.status} from {path}")
                return json.loads(resp.read().decode("utf-8"))
        except ResidencyURLBlocked:
            raise  # pass through the specific error
        except (urllib.error.URLError, urllib.error.HTTPError,
                socket.timeout, TimeoutError, OSError) as exc:
            raise ResidencyError(f"residency service unreachable: {exc}") from exc

    def put(self, key: str, value: str) -> dict:
        """Store a classified field value in Z4 (write path)."""
        result = self._request("POST", "/put", {"key": key, "value": value})
        logger.debug("fix_residency: put %s (kind=%s)", key, result.get("value_kind"))
        return result

    def get(self, key: str) -> str:
        """Retrieve a classified field value from Z4 (read path).

        Per-read access logging happens server-side (NFR-070/SC-010).
        Step-up authentication for human access happens at the gateway.
        """
        result = self._request("POST", "/get", {"key": key})
        value = result.get("value", "")
        if result.get("kind") == "synthetic":
            logger.debug("fix_residency: get %s -> synthetic value", key)
        return value

    def erase(self, key: str) -> dict:
        """Erase a classified field from Z4 (PDPA erasure saga).

        Creates a tombstone; the erasure audit record is preserved for the
        statutory five-year period.
        """
        return self._request("POST", "/erase", {"key": key})

    def health(self) -> dict:
        """Check the residency service is alive and in the expected mode."""
        return self._request("GET", "/health")


# Module-level singleton — one connection, one allowlist check at init.
_client: ResidencyClient | None = None


def get_client() -> ResidencyClient:
    """Return the residency client singleton (FF-09: the only entry point)."""
    global _client
    if _client is None:
        _client = ResidencyClient()
    return _client
