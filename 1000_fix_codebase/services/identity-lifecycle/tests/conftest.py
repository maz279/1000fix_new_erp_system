"""Fixtures: the fake Keycloak server (fake_keycloak.py) and private fix_events buses."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parent
SRC = TESTS.parent / "src"
ROOT = TESTS.parents[2]
for _p in (str(TESTS), str(SRC), str(ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fake_keycloak import ADMIN_PASSWORD, ADMIN_USER, REALM, FakeKeycloak

from libs.py.fix_events import (
    ConsumerGroupMigrationManager,
    DualWriteEventBus,
    InMemoryBus,
)
from libs.py.fix_events import dual_write as dual_write_mod
from libs.py.fix_events import kafka_bus as kafka_bus_mod
from libs.py.fix_events import migration as migration_mod
from libs.py.fix_events.dual_write import MockRedisStreamStore


@pytest.fixture
def keycloak():
    fake = FakeKeycloak()
    try:
        yield fake
    finally:
        fake.close()


@pytest.fixture
def kc_env(keycloak) -> dict[str, str]:
    """The service's environment: Keycloak settings only from env (never code)."""
    return {
        "KEYCLOAK_URL": keycloak.base_url,
        "KEYCLOAK_REALM": REALM,
        "KEYCLOAK_ADMIN_USER": ADMIN_USER,
        "KEYCLOAK_ADMIN_PASSWORD": ADMIN_PASSWORD,
        "KEYCLOAK_TIMEOUT_SECONDS": "5",
    }


@pytest.fixture
def buses(monkeypatch):
    """Private in-memory Kafka/Redis/dual bus + migration manager (fix_events singletons)."""
    kafka = InMemoryBus()
    redis = MockRedisStreamStore()
    monkeypatch.setattr(kafka_bus_mod, "_global_kafka_client", kafka)
    monkeypatch.setattr(dual_write_mod, "_global_redis_store", redis)
    bus = DualWriteEventBus()
    monkeypatch.setattr(dual_write_mod, "_global_dual_bus", bus)
    manager = ConsumerGroupMigrationManager(kafka_client=kafka, redis_store=redis)
    monkeypatch.setattr(migration_mod, "_global_migration_mgr", manager)
    return {"kafka": kafka, "redis": redis, "bus": bus, "migration": manager}
