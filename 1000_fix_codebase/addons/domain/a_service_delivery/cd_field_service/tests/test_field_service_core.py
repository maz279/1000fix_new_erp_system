# tests/test_field_service_core.py — Unit Tests for cd_field_service (CD-M02-01)
import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from odoo.addons.cd_field_service.models.fix_field_order import FixFieldOrder
from odoo.addons.cd_field_service.models.fix_field_route import FixFieldRoute
from odoo.addons.cd_field_service.models.fix_technician_location import FixTechnicianLocation
from odoo.exceptions import UserError


class TestFieldServiceCore:
    """Unit test suite for field service orders, routes, decline logs, and telemetry."""

    def test_haversine_distance_calculation(self):
        """Test Haversine distance accuracy between known Dhaka coordinates."""
        # Tejgaon Hub (23.7644, 90.3928) to Gulshan 1 (23.7785, 90.4150)
        dist_m = FixFieldOrder._haversine_distance(23.7644, 90.3928, 23.7785, 90.4150)
        assert 2500 < dist_m < 3000, f"Expected approx 2.7km, got {dist_m}m"

    def test_geofence_arrival_circle_inside_and_outside(self):
        """Test circular geofence boundary detection."""
        mock_fence = MagicMock()
        mock_fence.geofence_type = "circle"
        mock_fence.geometry_json = json.dumps(
            {
                "lat": 23.7937,
                "lng": 90.4066,
                "radius_m": 500,
            }
        )

        mock_order = MagicMock(spec=FixFieldOrder)
        mock_order.geofence_id = mock_fence
        mock_order._haversine_distance = FixFieldOrder._haversine_distance

        # Point inside (approx 50m away)
        assert FixFieldOrder._check_geofence_arrival(mock_order, 23.7940, 90.4068) is True

        # Point outside (approx 2km away)
        assert FixFieldOrder._check_geofence_arrival(mock_order, 23.7800, 90.4000) is False

    def test_geofence_arrival_polygon_inside_and_outside(self):
        """Test polygon geofence ray-casting boundary detection."""
        mock_fence = MagicMock()
        mock_fence.geofence_type = "polygon"
        mock_fence.geometry_json = json.dumps(
            {
                "points": [
                    [23.7900, 90.4000],
                    [23.8000, 90.4000],
                    [23.8000, 90.4100],
                    [23.7900, 90.4100],
                ]
            }
        )

        mock_order = MagicMock(spec=FixFieldOrder)
        mock_order.geofence_id = mock_fence

        # Inside center
        assert FixFieldOrder._check_geofence_arrival(mock_order, 23.7950, 90.4050) is True

        # Outside
        assert FixFieldOrder._check_geofence_arrival(mock_order, 23.7850, 90.4050) is False

    def test_field_order_lifecycle_happy_path(self):
        """Test field order state progression from draft to completed."""
        mock_order = MagicMock(spec=FixFieldOrder)
        mock_order.state = "draft"
        mock_order.technician_id = MagicMock(id=101, name="Rahim Ahmed")
        mock_order.env = MagicMock()
        mock_order._emit_field_event = MagicMock()
        mock_order.__iter__.return_value = [mock_order]
        # transitions write through the guard (A02 audit M02-1); completion
        # evidence is checked by _fix_completion_evidence_missing (M02-2)
        mock_order._guarded = MagicMock()
        mock_order._guarded.return_value.write.side_effect = lambda vals: [
            setattr(mock_order, k, v) for k, v in vals.items()
        ]
        mock_order._fix_completion_evidence_missing.return_value = []

        # 1. Request dispatch
        FixFieldOrder.action_request_dispatch(mock_order)
        assert mock_order.state == "pending_dispatch"

        # 2. Dispatch
        FixFieldOrder.action_dispatch(mock_order)
        assert mock_order.state == "dispatched"
        mock_order._emit_field_event.assert_called_with(
            "field.order.dispatched", pytest.approx(mock_order._emit_field_event.call_args[0][1])
        )

        # 3. Accept
        FixFieldOrder.action_accept(mock_order)
        assert mock_order.state == "accepted"

        # 4. En route
        FixFieldOrder.action_start_travel(mock_order)
        assert mock_order.state == "en_route"

        # 5. Arrive
        mock_order.geofence_id = False
        FixFieldOrder.action_arrive(mock_order)
        assert mock_order.state == "arrived"

        # 6. Start work
        FixFieldOrder.action_start_work(mock_order)
        assert mock_order.state == "in_progress"

        # 7. Complete
        FixFieldOrder.action_complete(mock_order)
        assert mock_order.state == "completed"

    def test_field_order_decline_flow(self):
        """Test technician decline action records decline log and emits domain event."""
        mock_order = MagicMock(spec=FixFieldOrder)
        mock_order.id = 55
        mock_order.name = "FO/2026/00055"
        mock_order.state = "dispatched"
        prev_tech = MagicMock(id=202)
        mock_order.technician_id = prev_tech
        mock_order.company_id = MagicMock(id=1)
        mock_order.operating_unit_id = MagicMock(id=2)
        mock_order._emit_field_event = MagicMock()
        mock_order.__iter__.return_value = [mock_order]

        mock_decline_log = MagicMock()
        mock_order.env = {"fix.field.decline.log": mock_decline_log}
        mock_order._fields = {
            "decline_reason": SimpleNamespace(selection=[("distance", "D"), ("other", "O")])
        }
        mock_order._guarded = MagicMock()

        FixFieldOrder.action_decline(mock_order, reason="distance", notes="Out of coverage zone")
        mock_order._guarded.return_value.write.assert_called_once_with(
            {
                "state": "declined",
                "decline_reason": "distance",
                "decline_notes": "Out of coverage zone",
                "technician_id": False,
            }
        )
        mock_decline_log.sudo.return_value.create.assert_called_once()
        mock_order._emit_field_event.assert_called_once()
        event_args = mock_order._emit_field_event.call_args[0]
        assert event_args[0] == "field.order.declined"
        assert event_args[1]["reason"] == "distance"

    def test_field_order_invalid_transitions(self):
        """Verify illegal state transitions raise UserError."""
        mock_order = MagicMock(spec=FixFieldOrder)
        mock_order.__iter__.return_value = [mock_order]

        # Cannot accept if not dispatched
        mock_order.state = "draft"
        with pytest.raises(UserError):
            FixFieldOrder.action_accept(mock_order)

        # Cannot start work if not arrived
        mock_order.state = "en_route"
        with pytest.raises(UserError):
            FixFieldOrder.action_start_work(mock_order)

        # Cannot cancel completed order
        mock_order.state = "completed"
        with pytest.raises(UserError):
            FixFieldOrder.action_cancel(mock_order)

    def test_route_optimization_and_improvement_calculation(self):
        """Honest optimiser: computed over a real distance matrix, the recorded
        improvement is a consequence of the sequence, not a constant (R01 re-audit)."""
        # A crossing layout the 2-opt pass must untangle: depot -> NE -> SW -> SE -> NW
        coords = [(23.860, 90.400), (23.760, 90.390), (23.850, 90.380), (23.770, 90.395)]
        stops = [SimpleNamespace(latitude=la, longitude=lo) for la, lo in coords]
        written, posts = {}, []

        rec = SimpleNamespace(
            field_order_ids=stops,
            _guarded=lambda: SimpleNamespace(write=lambda vals: written.update(vals)),
            message_post=lambda body: posts.append(body),
        )

        FixFieldRoute.action_optimize_route([rec])
        assert written["route_state"] == "optimized"
        assert written["total_distance_km"] > 0
        assert written["baseline_duration_hours"] >= written["total_duration_hours"]
        assert any("engine:" in body for body in posts)

        # An order without coordinates must be refused, not distance-invented
        blind = SimpleNamespace(
            field_order_ids=[*stops[:2], SimpleNamespace(latitude=0.0, longitude=0.0)]
        )
        with pytest.raises(UserError, match="lack GPS coordinates"):
            FixFieldRoute.action_optimize_route([blind])

    def test_route_helpers_haversine_and_2opt(self):
        """Pure helpers: haversine sanity + 2-opt improves a crossing tour."""
        from addons.domain.a_service_delivery.cd_field_service.models.fix_field_route import (
            haversine_km,
            optimise_sequence,
            trip_km,
        )

        # Dhaka (Tejgaon) -> Gazipur is roughly 25-30 km great-circle
        d = haversine_km(23.7776, 90.3959, 23.9999, 90.4200)
        assert 24.0 < d < 32.0, f"unexpected Dhaka-Gazipur distance {d:.1f} km"

        pts = [(23.7776, 90.3959), (23.860, 90.400), (23.760, 90.390), (23.850, 90.380)]
        matrix = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                matrix[i][j] = haversine_km(*pts[i], *pts[j])
        base = trip_km(matrix, [0, 1, 2, 3])
        opt_seq = optimise_sequence(matrix)
        opt = trip_km(matrix, opt_seq)
        assert opt <= base + 1e-9
        assert opt_seq[0] == 0, "tour must start at the depot"

    def test_technician_location_distance_helper(self):
        """Test distance helper in FixTechnicianLocation."""
        d = FixTechnicianLocation._calc_distance(23.8103, 90.4125, 23.8103, 90.4135)
        assert 90.0 < d < 110.0, f"Expected approx 100m, got {d}m"

    def test_technician_location_record_ping_unthrottled(self):
        """Test initial location ping records cleanly and publishes outbox event."""

        mock_loc_model = MagicMock(spec=FixTechnicianLocation)
        mock_tech = MagicMock()
        mock_tech.exists.return_value = True
        mock_tech.company_id.id = 1
        mock_tech.operating_unit_id.id = 2

        mock_outbox = MagicMock()
        mock_loc_model.env = {
            "hr.employee": MagicMock(browse=MagicMock(return_value=mock_tech)),
            "fix.event.outbox": mock_outbox,
            "operating.unit": MagicMock(),
        }
        mock_loc_model.search.return_value = False  # No prior ping
        created_ping = MagicMock(id=999)
        mock_loc_model.create.return_value = created_ping

        res = FixTechnicianLocation.record_ping(
            mock_loc_model, technician_id=10, lat=23.75, lon=90.38
        )
        assert res == created_ping
        mock_loc_model.create.assert_called_once()
        create_args = mock_loc_model.create.call_args[0][0]
        assert create_args["is_throttled"] is False
        # FF-28: published through fix_events -> fix.event.outbox.emit(event_type, ...)
        mock_outbox.emit.assert_called_once()
        assert mock_outbox.emit.call_args[0][:3] == (
            "technician.location.ping",
            "fix.technician.location",
            999,
        )

    def test_technician_location_record_ping_throttled_nfr056(self):
        """Test ping within 30s and <100m is throttled per NFR-056 and suppresses event publication."""
        from datetime import datetime, timedelta

        mock_loc_model = MagicMock(spec=FixTechnicianLocation)
        mock_tech = MagicMock()
        mock_tech.exists.return_value = True
        mock_tech.company_id.id = 1
        mock_tech.operating_unit_id.id = 2

        # Prior ping 5 seconds ago at virtually identical spot
        prior_ping = MagicMock()
        prior_ping.timestamp = datetime.now() - timedelta(seconds=5)
        prior_ping.latitude = 23.75000
        prior_ping.longitude = 90.38000

        mock_outbox = MagicMock()
        mock_loc_model.env = {
            "hr.employee": MagicMock(browse=MagicMock(return_value=mock_tech)),
            "fix.event.outbox": mock_outbox,
            "operating.unit": MagicMock(),
        }
        mock_loc_model.search.return_value = prior_ping
        mock_loc_model._calc_distance = FixTechnicianLocation._calc_distance

        created_ping = MagicMock(id=1000)
        mock_loc_model.create.return_value = created_ping

        # Second ping: 5s later, moved ~10m (23.75005, 90.38005)
        FixTechnicianLocation.record_ping(
            mock_loc_model, technician_id=10, lat=23.75005, lon=90.38005
        )
        mock_loc_model.create.assert_called_once()
        create_args = mock_loc_model.create.call_args[0][0]
        assert create_args["is_throttled"] is True
        # Throttled ping does NOT emit to outbox
        mock_outbox.emit.assert_not_called()
