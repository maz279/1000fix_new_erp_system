"""Dimension-level tests for DispatchScorer and RouteOptimizer edge cases (CD-M02-02)."""

import sys
from pathlib import Path

import pytest

_service_root = Path(__file__).resolve().parents[1]
if str(_service_root) not in sys.path:
    sys.path.insert(0, str(_service_root))

from dispatch_scoring.models import FieldJobRequest, ScoringWeights, TechnicianCandidate
from dispatch_scoring.route_optimizer import RouteOptimizer, RouteStop
from dispatch_scoring.scorer import DispatchScorer


def _tech(**overrides):
    base = {"id": 1, "name": "Tech", "home_zone_code": "DHAKA-NORTH"}
    base.update(overrides)
    return TechnicianCandidate(**base)


def _job(candidates, **overrides):
    base = {
        "job_id": "J-1",
        "service_order_ref": "SO-1",
        "zone_code": "DHAKA-NORTH",
        "customer_lat": 23.7937,
        "customer_lon": 90.4066,
        "candidates": candidates,
    }
    base.update(overrides)
    return FieldJobRequest(**base)


class TestEligibilityAndComposite:
    def test_unavailable_technician_is_rejected(self):
        resp = DispatchScorer.evaluate_candidates(_job([_tech(available=False)]))
        only = resp.ranked_candidates[0]
        assert only.eligible is False
        assert "unavailable" in only.rejection_reason
        assert only.composite_score == 0.0
        assert resp.recommended_technician is None

    def test_zero_weights_do_not_divide_by_zero(self):
        weights = ScoringWeights(
            skill=0.0, certification=0.0, van_stock=0.0, zone=0.0, sla_risk=0.0, route=0.0
        )
        resp = DispatchScorer.evaluate_candidates(_job([_tech()], weights=weights))
        rec = resp.recommended_technician
        assert rec is not None
        assert rec.eligible is True
        assert rec.composite_score == 0.0
        # the dimensions are still computed and reported
        assert rec.skill_score == 100.0
        assert rec.zone_score == 100.0

    def test_missing_coordinates_use_route_fallback(self):
        resp = DispatchScorer.evaluate_candidates(_job([_tech()]))
        rec = resp.recommended_technician
        assert rec.route_score == 50.0
        assert rec.estimated_distance_km == 8.0
        assert rec.estimated_travel_time_min == 30.0

    def test_tie_break_prefers_shorter_travel_time(self):
        near = _tech(id=1, current_lat=23.7937, current_lon=90.4066)
        # same composite (route weight 0) but a longer trip
        far = _tech(id=2, current_lat=23.9000, current_lon=90.4066)
        weights = ScoringWeights(
            skill=1.0, certification=0.0, van_stock=0.0, zone=0.0, sla_risk=0.0, route=0.0
        )
        resp = DispatchScorer.evaluate_candidates(_job([far, near], weights=weights))
        assert [c.technician_id for c in resp.ranked_candidates] == [1, 2]


class TestDimensionScores:
    def test_skills_without_requirement_is_full_score(self):
        assert DispatchScorer._score_skills([], ["anything"]) == 100.0

    def test_skills_partial_match_is_case_insensitive(self):
        assert DispatchScorer._score_skills(["Laptop", "AC"], ["laptop"]) == 50.0

    def test_certification_without_requirement(self):
        assert DispatchScorer._score_certification(_tech(certifications=["X"])) == 100.0
        assert DispatchScorer._score_certification(_tech(certifications=[])) == 80.0

    def test_certification_match_ratio(self):
        tech = _tech(certifications=["dell-l2"])
        assert DispatchScorer._score_certification(tech, ["DELL-L2", "HP-L1"]) == 50.0

    def test_van_stock(self):
        assert DispatchScorer._score_van_stock([], []) == 100.0
        assert DispatchScorer._score_van_stock(["mb-1", "RAM-1"], ["MB-1"]) == 50.0

    @pytest.mark.parametrize(
        ("job_zone", "tech_zone", "expected"),
        [
            ("", "DHAKA-NORTH", 50.0),
            ("DHAKA-NORTH", "", 50.0),
            (" dhaka-north ", "DHAKA-NORTH", 100.0),
            ("DHAKA-NORTH", "DHAKA-SOUTH", 60.0),
            ("CTG-PORT", "CTG-CITY", 60.0),
            ("DHAKA-NORTH", "KHULNA", 15.0),
        ],
    )
    def test_zone(self, job_zone, tech_zone, expected):
        assert DispatchScorer._score_zone(job_zone, tech_zone) == expected

    @pytest.mark.parametrize(
        ("hours", "priority", "expected"),
        [
            (1.0, 1, 100.0),
            (2.0, 3, 100.0),  # boost capped at 100
            (3.0, 1, 85.0),
            (6.0, 1, 70.0),
            (12.0, 1, 50.0),
            (48.0, 1, 30.0),
            (48.0, 3, 40.0),  # +5 per priority level above 1
            (48.0, 0, 30.0),  # never a negative boost
        ],
    )
    def test_sla_risk(self, hours, priority, expected):
        assert DispatchScorer._score_sla_risk(hours, priority) == expected

    def test_route_proximity_decays_to_zero(self):
        # Dhaka -> Chattogram (~200 km) is far beyond the 100-minute horizon
        score, dist_km, minutes = DispatchScorer._score_route_proximity(
            23.7644, 90.3928, 22.3569, 91.7832
        )
        assert score == 0.0
        assert dist_km > 150.0
        assert minutes > 100.0

    def test_route_proximity_same_point(self):
        score, dist_km, minutes = DispatchScorer._score_route_proximity(
            23.7644, 90.3928, 23.7644, 90.3928
        )
        assert (score, dist_km, minutes) == (100.0, 0.0, 0.0)


class TestRouteOptimizerEdges:
    def test_fewer_than_two_stops_rejected(self):
        depot = RouteStop("D", "Depot", 23.76, 90.39)
        with pytest.raises(ValueError, match="At least 2 customer stops"):
            RouteOptimizer.optimize_itinerary(1, "2026-10-22", depot, [RouteStop("A", "A", 1, 1)])

    def test_zero_distance_itinerary_reports_no_savings(self):
        depot = RouteStop("D", "Depot", 23.76, 90.39)
        stops = [RouteStop("A", "A", 23.76, 90.39), RouteStop("B", "B", 23.76, 90.39)]
        result = RouteOptimizer.optimize_itinerary(1, "2026-10-22", depot, stops)
        assert result.baseline_distance_km == 0.0
        assert result.travel_time_savings_pct == 0.0
        assert result.achieves_g2_target is False
        assert result.optimized_stops_sequence[0] == result.optimized_stops_sequence[-1] == "D"
