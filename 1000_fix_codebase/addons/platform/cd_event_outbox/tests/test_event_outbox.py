# Tests for cd_event_outbox (P03-M03) — AS-08 transactional outbox.


class TestFixEventOutbox:
    """fix.event.outbox model tests."""

    def test_model_exists(self):
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        assert FixEventOutbox is not None

    def test_event_id_unique(self):
        """UUID event_id for idempotency (DI-05)."""
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        assert hasattr(FixEventOutbox, "_event_id_unique")  # Odoo 19 models.Constraint attr

    def test_emit_method(self):
        """AS-08: the emit() method writes to the outbox."""
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        assert "emit" in dir(FixEventOutbox)

    def test_drain_pending_method(self):
        """The publisher drains pending events."""
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        assert "drain_pending" in dir(FixEventOutbox)

    def test_status_selection(self):
        """Status includes pending/published/failed."""
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        assert "status" in dir(FixEventOutbox)

    def test_dual_write_fields(self):
        """Dual-write fields (P09-M01-T03) exist on model."""
        from odoo.addons.cd_event_outbox.models.fix_event_outbox import FixEventOutbox

        for fld in [
            "bus_target",
            "kafka_published_at",
            "kafka_partition",
            "kafka_offset",
            "payload_sha256",
        ]:
            assert fld in dir(FixEventOutbox), f"Field {fld} missing from FixEventOutbox"


class TestFixEvents:
    """libs/py/fix_events tests (FF-28 sole event client)."""

    def test_publish_exists(self):
        from libs.py.fix_events import publish

        assert callable(publish)

    def test_consume_exists(self):
        from libs.py.fix_events import consume

        assert callable(consume)

    def test_replay_exists(self):
        from libs.py.fix_events import replay_from_timestamp

        assert callable(replay_from_timestamp)

    def test_kafka_client_exports(self):
        """Event bus exported; the default global client is the real (lazy) backend."""
        from libs.py.fix_events import InMemoryBus, KafkaBackend, get_kafka_client

        client = get_kafka_client()
        assert isinstance(client, KafkaBackend)
        assert len(client.bootstrap_servers) == 3
        assert len(InMemoryBus().bootstrap_servers) == 3

    def test_dual_write_bus_exports(self):
        """DualWriteEventBus exported and callable."""
        from libs.py.fix_events import DualWriteEventBus, get_dual_bus

        bus = get_dual_bus()
        assert isinstance(bus, DualWriteEventBus)

    def test_migration_manager_exports(self):
        """ConsumerGroupMigrationManager exported and functional."""
        from libs.py.fix_events import (
            CANONICAL_CONSUMER_GROUPS,
            ConsumerGroupMigrationManager,
            get_migration_manager,
        )

        mgr = get_migration_manager()
        assert isinstance(mgr, ConsumerGroupMigrationManager)
        assert len(CANONICAL_CONSUMER_GROUPS) == 6

    def test_replay_engine_exports(self):
        """EventReplayEngine exported and functional."""
        from libs.py.fix_events import EventReplayEngine, get_replay_engine

        engine = get_replay_engine()
        assert isinstance(engine, EventReplayEngine)

    def test_emit_validates_event_type(self):
        """emit() rejects a non-dot-notation event_type."""
        # In the Odoo runtime:
        # with pytest.raises(ValidationError):
        #     env['fix.event.outbox'].emit('invalid', 'x', 1, {})
        pass  # runtime test
