"""dsr-orchestrator — the HTTP residency client against the LIVE local stub.

The residency stub (services/local-residency-stub, "SYNTHETIC VALUES ONLY")
is UP at 127.0.0.1:8100 during development (docker compose). These tests
speak its real HTTP contract:

- health / mode reporting;
- GV-009 fail-closed: a synthetic-only stub never yields exportable
  resident data and never lets a DSR report data it cannot vouch for;
- erasure over HTTP (the erase is real work against the configured store);
- connection failures raise — no canned success when unreachable.

If the stub is not reachable the live tests SKIP with an honest reason;
they are never faked (that would defeat the point).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dsr_orchestrator import (
    FixResidencyAdapter,
    ResidencyServiceError,
    SagaState,
    SagaStep,
    assemble_export,
    run_erasure_saga,
)

from libs.py.fix_residency import ResidencyClient

STUB_URL = os.environ.get("RESIDENCY_STUB_URL", "http://127.0.0.1:8100")


def _stub_reachable() -> bool:
    import http.client
    from urllib.parse import urlparse

    parsed = urlparse(STUB_URL)
    try:
        conn = http.client.HTTPConnection(
            parsed.hostname or "127.0.0.1", parsed.port or 80, timeout=2
        )
        conn.request("GET", "/health")
        resp = conn.getresponse()
        resp.read()
        conn.close()
        return resp.status == 200
    except OSError:
        return False


requires_stub = pytest.mark.skipif(
    not _stub_reachable(),
    reason=(
        f"local residency stub not reachable at {STUB_URL} - start it with "
        "`docker compose up residency-stub`; these tests exercise the real "
        "HTTP contract and are never faked"
    ),
)


# ------------------------------------------------------------- fail closed --


class TestFailClosedWhenUnreachable:
    """No stub needed: a closed port must raise, never return canned data."""

    def _client(self) -> FixResidencyAdapter:
        return FixResidencyAdapter(base_url="http://127.0.0.1:1")

    def test_health_raises(self):
        with pytest.raises(ResidencyServiceError, match="unreachable"):
            self._client().health()

    def test_fetch_resident_raises_never_canned_data(self):
        with pytest.raises(ResidencyServiceError, match="unreachable"):
            self._client().fetch_resident("party:1")

    def test_tombstone_raises_never_a_canned_erasure(self):
        with pytest.raises(ResidencyServiceError, match="unreachable"):
            self._client().tombstone("party:1", "all")

    def test_base_url_defaults_and_env_override(self, monkeypatch):
        assert FixResidencyAdapter().base_url == "http://127.0.0.1:8100"
        # get_client() caches a singleton, so an env override is proven on a
        # FRESH canonical client, not through the cached adapter default.
        monkeypatch.setenv("RESIDENCY_BASE", "http://localhost:8100/")
        assert ResidencyClient().base_url == "http://localhost:8100"
        assert (
            FixResidencyAdapter(base_url="http://localhost:8100/").base_url
            == "http://localhost:8100"
        )


# ------------------------------------------------------- live stub (it is UP)


@requires_stub
class TestLiveStubHealth:
    def test_health_reports_up_and_synthetic_only_mode(self):
        state = FixResidencyAdapter().health()
        assert state["status"] == "UP"
        assert state["mode"] == "synthetic-only"


@requires_stub
class TestFailClosedOnSyntheticOnly:
    """The stub is honest about being synthetic; the client must be too."""

    def test_assert_service_ready_names_the_synthetic_mode(self):
        with pytest.raises(ResidencyServiceError, match="synthetic-only mode"):
            FixResidencyAdapter().assert_service_ready()

    def test_fetch_resident_refuses_synthetic_values(self):
        with pytest.raises(ResidencyServiceError, match="refusing to export"):
            FixResidencyAdapter().fetch_resident("party:stub-1")

    def test_assemble_export_through_the_live_client_fails_closed(self):
        """T03 through the real wire: a synthetic-only store cannot supply
        the resident half of a portability export — the export fails closed
        instead of shipping synthetic values as the subject's data."""
        with pytest.raises(ResidencyServiceError, match="refusing to export"):
            assemble_export("party:stub-2", lambda ref: {"name": "x"}, FixResidencyAdapter())


@requires_stub
class TestErasureOverHttp:
    def test_tombstone_erases_the_party_record(self):
        client = FixResidencyAdapter()
        result = client.tombstone("party:stub-3", "all")
        assert result["erased"] is True
        assert result["key"] == "party:stub-3"  # "all" maps to the party record
        assert str(result["tombstone"]).startswith(FixResidencyAdapter.SYNTHETIC_BANNER)

    def test_erasure_saga_tombstones_through_the_live_client(self):
        """The T04 saga's Z4 step runs over real HTTP; the other steps are
        the caller's executors (no-ops here)."""
        executors = {step: (lambda party_ref: None) for step in SagaStep}
        state = SagaState("S-LIVE-1", "party:stub-saga")
        run_erasure_saga(state, executors, FixResidencyAdapter())
        assert state.status == "completed"
