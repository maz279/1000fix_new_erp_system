"""HTTP contract tests for the dispatch-scoring FastAPI app (CD-M02-02, G2-03)."""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_service_root = Path(__file__).resolve().parents[1]
if str(_service_root) not in sys.path:
    sys.path.insert(0, str(_service_root))

from dispatch_scoring.main import app


@pytest.fixture
def client():
    return TestClient(app)


def _candidate(**overrides):
    base = {
        "id": 1,
        "name": "Rahim",
        "skills": ["laptop"],
        "certifications": ["COMPTIA-A+"],
        "van_stock_skus": ["MB-1"],
        "home_zone_code": "DHAKA-NORTH",
        "current_lat": 23.7930,
        "current_lon": 90.4060,
    }
    base.update(overrides)
    return base


def _job(candidates):
    return {
        "job_id": "FO-API-1",
        "service_order_ref": "SO-API-1",
        "required_skills": ["laptop"],
        "required_parts_skus": ["MB-1"],
        "zone_code": "DHAKA-NORTH",
        "customer_lat": 23.7937,
        "customer_lon": 90.4066,
        "candidates": candidates,
    }


def test_score_rejects_empty_candidate_list(client):
    resp = client.post("/score", json=_job([]))
    assert resp.status_code == 400
    assert resp.json()["detail"] == "At least one technician candidate must be provided."


def test_score_ranks_eligible_before_ineligible(client):
    candidates = [
        _candidate(id=7, name="Off duty", available=False),
        _candidate(id=8, name="On duty"),
    ]
    resp = client.post("/score", json=_job(candidates))
    assert resp.status_code == 200
    data = resp.json()
    assert data["job_id"] == "FO-API-1"
    assert data["total_candidates_evaluated"] == 2
    assert data["recommended_technician"]["technician_id"] == 8
    assert [c["technician_id"] for c in data["ranked_candidates"]] == [8, 7]
    assert data["ranked_candidates"][1]["eligible"] is False
    assert data["evaluated_at"]


def test_auto_dispatch_404_when_nobody_is_eligible(client):
    resp = client.post("/dispatch/auto", json=_job([_candidate(on_leave=True)]))
    assert resp.status_code == 404
    assert "No eligible technician" in resp.json()["detail"]


def test_route_optimize_requires_two_stops(client):
    payload = {
        "technician_id": 5,
        "date": "2026-10-22",
        "stops": [{"stop_id": "S1", "lat": 23.79, "lon": 90.40}],
    }
    resp = client.post("/route/optimize", json=payload)
    assert resp.status_code == 400
    assert "At least 2 customer stops" in resp.json()["detail"]


def test_route_optimize_builds_depot_and_default_stop_labels(client):
    payload = {
        "technician_id": 5,
        "date": "2026-10-22",
        "stops": [
            {"stop_id": "BANANI", "name": "Banani", "lat": 23.7937, "lon": 90.4066},
            {"lat": 23.7780, "lon": 90.3950},  # no id / name -> defaults
            {"stop_id": "GULSHAN", "lat": 23.7925, "lon": 90.4167},
        ],
    }
    resp = client.post("/route/optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["technician_id"] == 5
    assert data["depot_name"] == "Tejgaon Central Service Hub"
    assert data["baseline_stops_sequence"] == ["DEPOT-0", "BANANI", "STOP-2", "GULSHAN", "DEPOT-0"]
    seq = data["optimized_stops_sequence"]
    assert seq[0] == seq[-1] == "DEPOT-0"
    assert sorted(seq[1:-1]) == ["BANANI", "GULSHAN", "STOP-2"]
    assert data["optimized_distance_km"] <= data["baseline_distance_km"]


def test_route_optimize_honours_custom_depot(client):
    payload = {
        "technician_id": 9,
        "date": "2026-10-22",
        "depot_name": "Uttara Hub",
        "depot_lat": 23.8759,
        "depot_lon": 90.3795,
        "stops": [
            {"stop_id": "A", "lat": 23.8000, "lon": 90.4000},
            {"stop_id": "B", "lat": 23.7900, "lon": 90.4100},
        ],
    }
    data = client.post("/route/optimize", json=payload).json()
    assert data["depot_name"] == "Uttara Hub"
    assert data["baseline_stops_sequence"] == ["DEPOT-0", "A", "B", "DEPOT-0"]


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert resp.json() == {
        "service": "dispatch-scoring",
        "evaluations_total": 1,
        "g2_target_met": True,
        "active_stubs": 1,
    }
