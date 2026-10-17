import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure src can be imported directly
_service_root = Path(__file__).resolve().parents[1]
if str(_service_root) not in sys.path:
    sys.path.insert(0, str(_service_root))

from dispatch_scoring.main import app
from dispatch_scoring.models import (
    FieldJobRequest,
    TechnicianCandidate,
    ScoringWeights,
)
from dispatch_scoring.scorer import DispatchScorer
from dispatch_scoring.route_optimizer import RouteOptimizer, RouteStop
from dispatch_scoring.geospatial_client import GeospatialClient


@pytest.fixture
def client():
    return TestClient(app)


class TestDispatchScoringService:
    """Test suite for dispatch scoring FastAPI endpoints and pure algorithm."""

    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "dispatch-scoring"
        assert any("STUB-M02-M22-001" in s for s in data["stubs_active"])

    def test_scoring_algorithm_multi_dimension(self):
        """Verify 6-dimensional scoring ranks candidates correctly."""
        cand_perfect = TechnicianCandidate(
            id=1,
            name="Rahim - Perfect Match",
            skills=["laptop", "motherboard", "soldering"],
            certifications=["CompTIA_A+"],
            van_stock_skus=["MB-DELL-5520", "RAM-DDR4-8GB"],
            home_zone_code="DHAKA-NORTH",
            current_lat=23.7930,
            current_lon=90.4060,  # ~100m from customer
            current_workload_count=2,
            max_daily_capacity=6,
            available=True,
        )

        cand_distant = TechnicianCandidate(
            id=2,
            name="Karim - Distant No Stock",
            skills=["laptop"],
            certifications=[],
            van_stock_skus=[],
            home_zone_code="DHAKA-SOUTH",
            current_lat=23.7200,
            current_lon=90.4100,  # ~8km from customer
            current_workload_count=1,
            max_daily_capacity=6,
            available=True,
        )

        job_req = FieldJobRequest(
            job_id="FO-2026-001",
            service_order_ref="SO-001",
            required_skills=["laptop", "motherboard"],
            required_parts_skus=["MB-DELL-5520"],
            zone_code="DHAKA-NORTH",
            customer_lat=23.7937,
            customer_lon=90.4066,
            sla_hours_remaining=3.5,
            priority=2,
            candidates=[cand_perfect, cand_distant],
        )

        result = DispatchScorer.evaluate_candidates(job_req)
        assert result.total_candidates_evaluated == 2
        assert result.recommended_technician is not None
        assert result.recommended_technician.technician_id == 1
        assert result.recommended_technician.composite_score > 85.0
        assert result.ranked_candidates[0].composite_score > result.ranked_candidates[1].composite_score

    def test_ineligible_candidate_over_capacity(self):
        """Technician exceeding max daily capacity must be flagged ineligible."""
        cand_busy = TechnicianCandidate(
            id=3,
            name="Busy Tech",
            skills=["laptop"],
            home_zone_code="DHAKA-NORTH",
            current_workload_count=6,
            max_daily_capacity=6,
            available=True,
        )
        job_req = FieldJobRequest(
            job_id="FO-2026-002",
            service_order_ref="SO-002",
            zone_code="DHAKA-NORTH",
            customer_lat=23.7937,
            customer_lon=90.4066,
            candidates=[cand_busy],
        )
        result = DispatchScorer.evaluate_candidates(job_req)
        assert len(result.ranked_candidates) == 1
        c = result.ranked_candidates[0]
        assert c.eligible is False
        assert "capacity" in c.rejection_reason.lower()
        assert result.recommended_technician is None

    def test_api_auto_dispatch_endpoint(self, client):
        cand = {
            "id": 10,
            "name": "Tanvir Hasan",
            "skills": ["ac_repair"],
            "certifications": [],
            "van_stock_skus": ["COMP-1.5T"],
            "home_zone_code": "DHAKA-NORTH",
            "current_lat": 23.7900,
            "current_lon": 90.4100,
            "current_workload_count": 1,
            "max_daily_capacity": 5,
            "available": True,
        }
        payload = {
            "job_id": "FO-2026-099",
            "service_order_ref": "SO-099",
            "required_skills": ["ac_repair"],
            "required_parts_skus": ["COMP-1.5T"],
            "zone_code": "DHAKA-NORTH",
            "customer_lat": 23.7925,
            "customer_lon": 90.4167,
            "sla_hours_remaining": 5.0,
            "priority": 1,
            "candidates": [cand],
        }
        resp = client.post("/dispatch/auto", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["technician_id"] == 10
        assert data["eligible"] is True
        assert data["composite_score"] > 70.0


class TestRouteOptimizationAndG203:
    """Tests asserting Gate G2-03 compliance: >= 15% travel time reduction."""

    def test_vroom_route_optimization_achieves_g2_target(self):
        """Simulate real 5-stop Dhaka field service route and verify >= 15% savings."""
        depot = RouteStop(stop_id="DEPOT", name="Tejgaon Central Hub", lat=23.7644, lon=90.3928)
        # 5 customer stops scattered across Banani, Gulshan, Baridhara, Mohakhali
        stops = [
            RouteStop(stop_id="STOP-1", name="Banani Block C", lat=23.7937, lon=90.4066),
            RouteStop(stop_id="STOP-2", name="Mohakhali DOHS", lat=23.7780, lon=90.3950),
            RouteStop(stop_id="STOP-3", name="Baridhara Diplomatic", lat=23.8010, lon=90.4210),
            RouteStop(stop_id="STOP-4", name="Gulshan 2 Circle", lat=23.7925, lon=90.4167),
            RouteStop(stop_id="STOP-5", name="Tejgaon Link Road", lat=23.7690, lon=90.4020),
        ]

        result = RouteOptimizer.optimize_itinerary(
            technician_id=501,
            date="2026-10-17",
            depot=depot,
            stops=stops,
        )

        assert result.achieves_g2_target is True
        assert result.travel_time_savings_pct >= 15.0, (
            f"Gate G2-03 requires >= 15% reduction, got {result.travel_time_savings_pct}%"
        )
        assert result.optimized_travel_time_min < result.baseline_travel_time_min
        assert len(result.optimized_stops_sequence) == len(stops) + 2  # Includes start and end depot


class TestGeospatialFallbacks:
    """Test suite validating INT-019 to INT-023 fallback mechanisms."""

    def test_int019_geocoding_centroid_fallback(self):
        client = GeospatialClient()
        # Known centroid query
        res = client.geocode("House 12, Road 4, Banani, Dhaka")
        assert res.source == "fallback"
        assert abs(res.latitude - 23.7937) < 0.001
        assert abs(res.longitude - 90.4066) < 0.001

        # Unknown address queries fall back to central Dhaka
        res_unknown = client.geocode("Random remote village without GPS")
        assert res_unknown.source == "fallback"
        assert abs(res_unknown.latitude - 23.7644) < 0.001

    def test_int020_routing_haversine_fallback(self):
        client = GeospatialClient(osrm_url="http://127.0.0.1:9999")  # Unreachable port to force fallback
        res = client.route_eta(23.7644, 90.3928, 23.7937, 90.4066)
        assert res.source == "haversine_fallback"
        assert 3.0 < res.distance_km < 5.0
        assert res.duration_min > 10.0

    def test_int022_traffic_congestion_model(self):
        client = GeospatialClient()
        # Morning peak (09:00)
        res_peak = client.get_traffic_multiplier("DHAKA-NORTH", hour=9)
        assert res_peak.congestion_multiplier >= 1.9

        # Midnight (02:00)
        res_night = client.get_traffic_multiplier("DHAKA-NORTH", hour=2)
        assert res_night.congestion_multiplier < 1.1
