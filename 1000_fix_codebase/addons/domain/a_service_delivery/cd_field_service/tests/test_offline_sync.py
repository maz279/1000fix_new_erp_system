"""test_offline_sync — Unit and integration tests for offline sync engine and evidence channel (CD-M02-04)."""

import base64
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from odoo.addons.cd_field_service.controllers.evidence_api import (
    _ACTIVE_CHUNKS,
    OfflineEvidenceApiController,
)
from odoo.addons.cd_field_service.controllers.offline_sync_api import OfflineSyncApiController
from odoo.addons.cd_field_service.models.fix_offline_idempotency_ledger import (
    FixOfflineIdempotencyLedger,
)
from odoo.addons.cd_service_order.controllers.technician_api import batch_digest


class TestOfflineSyncSuite:
    """Comprehensive test suite for SP-07, SP-01..03, DI-05, and SP-09 invariants."""

    def test_idempotency_ledger_cache_hit_and_miss(self):
        """Test DI-05 idempotency ledger returns cached payload on repeat calls."""
        mock_model = MagicMock(spec=FixOfflineIdempotencyLedger)

        # 1. Cache miss
        mock_model.search.return_value = False
        res = FixOfflineIdempotencyLedger.get_cached_result(mock_model, "cmd-uuid-nonexistent")
        assert res is None

        # 2. Cache hit
        mock_entry = MagicMock()
        mock_entry.status = "applied"
        mock_entry.response_payload = json.dumps({"order_id": 42, "state": "in_progress"})
        mock_entry.conflict_reason = None
        mock_entry.applied_at = "2026-10-17 08:30:00"
        mock_model.search.return_value = mock_entry

        hit = FixOfflineIdempotencyLedger.get_cached_result(mock_model, "cmd-uuid-existing")
        assert hit is not None
        assert hit["status"] == "applied"
        assert hit["response"]["order_id"] == 42
        assert hit["idempotent_replay"] is True

    @patch("odoo.addons.cd_field_service.controllers.offline_sync_api._su_env")
    @patch("odoo.addons.cd_field_service.controllers.offline_sync_api.resolve_technician")
    def test_offline_sync_upload_first_and_checksum(self, mock_resolve_tech, mock_su_env):
        """Test SP-07 upload-first processing and batch checksum calculation."""
        mock_tech = MagicMock()
        mock_tech.id = 5
        mock_resolve_tech.return_value = (mock_tech, None)

        mock_ledger = MagicMock()
        mock_ledger.get_cached_result.return_value = None  # fresh commands

        mock_order = MagicMock()
        mock_order.exists.return_value = mock_order  # recordset.exists() -> recordset
        mock_order.state = "assigned"
        mock_order.name = "FO-00123"
        mock_order.technician_id.id = 5

        mock_orders_model = MagicMock()
        mock_orders_model.browse.return_value = mock_order
        mock_orders_model.search.return_value = [mock_order]
        mock_orders_model.env.cr.now.return_value = datetime(2026, 10, 17, 9, 0)

        env_dict = {
            "fix.offline.idempotency.ledger": mock_ledger,
            "fix.field.order": mock_orders_model,
        }
        mock_env = MagicMock()
        mock_env.__getitem__.side_effect = lambda key: env_dict[key]
        mock_env.get.side_effect = lambda key: env_dict.get(key)
        mock_su_env.return_value = mock_env

        controller = OfflineSyncApiController()

        payload = {
            "client_id": "P02-TECH-001",
            "device_id": "DEV-TEST-001",
            "sync_token": "TOKEN-PREV",
            "commands": [
                {
                    "command_id": "cmd-001",
                    "model": "fix.field.order",
                    "record_id": 123,
                    "operation": "start_order",
                    "payload": {"order_id": 123},
                }
            ],
        }

        payload["batch_checksum"] = batch_digest(payload["commands"])
        result = controller.offline_sync(**payload)

        assert result["status"] == "success"
        assert "cmd-001" in result["acknowledged"]
        assert result["batch_checksum"] is not None
        assert len(result["batch_checksum"]) == 16
        assert len(result["deltas"]) == 1
        assert result["stats"]["total_uploaded"] == 1
        assert result["stats"]["acknowledged_count"] == 1

        # Verify ledger recorded the execution (DI-05)
        mock_ledger.record_execution.assert_called_once()
        assert mock_ledger.record_execution.call_args.kwargs["command_id"] == "cmd-001"
        assert mock_ledger.record_execution.call_args.kwargs["status"] == "applied"

    @patch("odoo.addons.cd_field_service.controllers.offline_sync_api._su_env")
    @patch("odoo.addons.cd_field_service.controllers.offline_sync_api.resolve_technician")
    def test_conflict_matrix_rejection_on_terminal_state(self, mock_resolve_tech, mock_su_env):
        """Test conflict matrix rejects technician transitions on terminal/cancelled orders."""
        mock_tech = MagicMock()
        mock_tech.id = 5
        mock_resolve_tech.return_value = (mock_tech, None)

        mock_ledger = MagicMock()
        mock_ledger.get_cached_result.return_value = None

        mock_order = MagicMock()
        mock_order.exists.return_value = mock_order  # recordset.exists() -> recordset
        mock_order.state = "cancelled"  # server authoritative cancelled state
        mock_order.name = "FO-00999"
        mock_order.technician_id.id = 5

        mock_orders_model = MagicMock()
        mock_orders_model.browse.return_value = mock_order

        env_dict = {
            "fix.offline.idempotency.ledger": mock_ledger,
            "fix.field.order": mock_orders_model,
        }
        mock_env = MagicMock()
        mock_env.__getitem__.side_effect = lambda key: env_dict[key]
        mock_env.get.side_effect = lambda key: env_dict.get(key)
        mock_su_env.return_value = mock_env

        controller = OfflineSyncApiController()

        payload = {
            "device_id": "DEV-TEST-002",
            "commands": [
                {
                    "command_id": "cmd-reject-001",
                    "model": "fix.field.order",
                    "record_id": 999,
                    "operation": "start_order",
                    "payload": {"order_id": 999},
                }
            ],
        }

        payload["batch_checksum"] = batch_digest(payload["commands"])
        result = controller.offline_sync(**payload)

        assert "cmd-reject-001" in result["rejected"]
        assert "cancelled" in result["rejected"]["cmd-reject-001"]
        assert result["stats"]["rejected_count"] == 1

    @patch("odoo.addons.cd_field_service.controllers.evidence_api._su_env")
    @patch("odoo.addons.cd_field_service.controllers.evidence_api.resolve_technician")
    def test_deferred_evidence_chunked_upload_and_reassembly(self, mock_resolve_tech, mock_su_env):
        """Test SP-09 resumable chunked upload reassembles multi-part media without blocking."""
        _ACTIVE_CHUNKS.clear()
        mock_tech = MagicMock()
        mock_tech.id = 5
        mock_resolve_tech.return_value = (mock_tech, None)

        mock_att = MagicMock()
        mock_att.id = 456
        mock_att_model = MagicMock()
        mock_att_model.create.return_value = mock_att

        mock_env = MagicMock()
        mock_env.__getitem__.return_value = mock_att_model
        mock_su_env.return_value = mock_env

        controller = OfflineEvidenceApiController()
        media_id = "test-media-photo-uuid"

        # Test binary data split into 2 chunks
        raw_bytes = b"EXIF_JPEG_IMAGE_CONTENT_SAMPLE_FOR_TESTING_EVIDENCE"
        b64_full = base64.b64encode(raw_bytes).decode("ascii")
        half = len(b64_full) // 2
        chunk0 = b64_full[:half]
        chunk1 = b64_full[half:]

        # Upload Chunk 0
        res0 = controller.upload_chunk(
            media_uuid=media_id,
            chunk_index=0,
            total_chunks=2,
            chunk_data=chunk0,
            media_type="photo",
            model="fix.field.order",
            record_id=10,
            filename="diagnosis_photo.jpg",
        )
        assert res0["status"] == "chunk_accepted"
        assert res0["complete"] is False
        assert res0["received_chunks"] == 1

        # Upload Chunk 1
        res1 = controller.upload_chunk(
            media_uuid=media_id,
            chunk_index=1,
            total_chunks=2,
            chunk_data=chunk1,
            media_type="photo",
            model="fix.field.order",
            record_id=10,
            filename="diagnosis_photo.jpg",
        )
        assert res1["status"] == "complete"
        assert res1["complete"] is True
        assert res1["attachment_id"] == 456
        assert media_id not in _ACTIVE_CHUNKS
