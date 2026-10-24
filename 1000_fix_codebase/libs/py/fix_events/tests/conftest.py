"""Shared fixtures for the fix_events suite.

Every test gets private, in-memory bus instances: the module-level singletons
(Kafka client, Redis stream store, dual bus, migration manager, replay engine)
are swapped for fresh ones via ``monkeypatch`` and restored afterwards, so the
suite never leaks state into (or inherits state from) other suites sharing the
pytest process. No broker or network is ever touched.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Iterable, Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from libs.py.fix_events import dual_write, kafka_bus, migration, replay


class FakeClock:
    """Deterministic stand-in for the ``time`` module used by the bus modules.

    ``time()`` returns ``now`` (moved with :meth:`advance`); ``perf_counter()``
    replays a scripted sequence when one is given, else delegates to the real one.
    """

    def __init__(self, now: float = 1_792_000_000.0) -> None:
        self.now = now
        self._perf: Iterator[float] | None = None

    def time(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def gmtime(self, secs: float | None = None) -> time.struct_time:
        return time.gmtime(self.now if secs is None else secs)

    @staticmethod
    def strftime(fmt: str, t: time.struct_time) -> str:
        return time.strftime(fmt, t)

    def script_perf_counter(self, values: Iterable[float]) -> None:
        self._perf = iter(values)

    def perf_counter(self) -> float:
        if self._perf is None:
            return time.perf_counter()
        return next(self._perf)


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    """Freeze the clock seen by kafka_bus, dual_write and migration."""
    fake = FakeClock()
    for module in (kafka_bus, dual_write, migration):
        monkeypatch.setattr(module, "time", fake)
    return fake


@pytest.fixture
def kafka(monkeypatch: pytest.MonkeyPatch) -> kafka_bus.InMemoryBus:
    """A fresh 3-partition in-memory bus installed as the global client."""
    client = kafka_bus.InMemoryBus()
    monkeypatch.setattr(kafka_bus, "_global_kafka_client", client)
    return client


@pytest.fixture
def redis(monkeypatch: pytest.MonkeyPatch) -> dual_write.MockRedisStreamStore:
    """A fresh Redis stream store installed as the global store."""
    store = dual_write.MockRedisStreamStore()
    monkeypatch.setattr(dual_write, "_global_redis_store", store)
    return store


@pytest.fixture
def no_singletons(monkeypatch: pytest.MonkeyPatch, kafka, redis) -> None:
    """Reset the lazily-built singletons so get_*() builds them from the fresh globals."""
    monkeypatch.setattr(dual_write, "_global_dual_bus", None)
    monkeypatch.setattr(migration, "_global_migration_mgr", None)
    monkeypatch.setattr(replay, "_global_replay_engine", None)
