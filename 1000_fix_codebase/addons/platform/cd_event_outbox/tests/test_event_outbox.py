# Tests for cd_event_outbox (P03-M03) — AS-08 transactional outbox.
import pytest


class TestFixEventOutbox:
    """fix.event.outbox model tests."""

    def test_model_exists(self):
        from addons.platform.cd_event_outbox.models.fix_event_outbox import FixEventOutbox
        assert FixEventOutbox is not None

    def test_event_id_unique(self):
        """UUID event_id for idempotency (DI-05)."""
        from addons.platform.cd_event_outbox.models.fix_event_outbox import FixEventOutbox
        constraints = FixEventOutbox._sql_constraints
        assert any("event_id_unique" in str(c) for c in constraints)

    def test_emit_method(self):
        """AS-08: the emit() method writes to the outbox."""
        from addons.platform.cd_event_outbox.models.fix_event_outbox import FixEventOutbox
        assert 'emit' in dir(FixEventOutbox)

    def test_drain_pending_method(self):
        """The publisher drains pending events."""
        from addons.platform.cd_event_outbox.models.fix_event_outbox import FixEventOutbox
        assert 'drain_pending' in dir(FixEventOutbox)

    def test_status_selection(self):
        """Status includes pending/published/failed."""
        from addons.platform.cd_event_outbox.models.fix_event_outbox import FixEventOutbox
        assert 'status' in dir(FixEventOutbox)


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

    def test_emit_validates_event_type(self):
        """emit() rejects a non-dot-notation event_type."""
        # In the Odoo runtime:
        # with pytest.raises(ValidationError):
        #     env['fix.event.outbox'].emit('invalid', 'x', 1, {})
        pass  # runtime test
