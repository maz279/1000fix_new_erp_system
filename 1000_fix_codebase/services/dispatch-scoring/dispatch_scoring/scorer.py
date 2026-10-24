"""Dispatch scoring algorithm implementing the 6-dimensional candidate evaluation (CD-M02-02)."""

import math

from .models import (
    CandidateScoreBreakdown,
    DispatchScoreResponse,
    FieldJobRequest,
    TechnicianCandidate,
)


class DispatchScorer:
    """Calculates weighted multidimensional suitability scores for technician dispatch."""

    STUB_CERTIFICATION_ID = "STUB-M02-M22-001"

    @classmethod
    def evaluate_candidates(cls, request: FieldJobRequest) -> DispatchScoreResponse:
        ranked: list[CandidateScoreBreakdown] = []

        for tech in request.candidates:
            # 1. Eligibility guard: capacity, active availability, and M55 roster integration
            if not tech.available:
                breakdown = cls._create_ineligible_breakdown(
                    tech, "Technician currently marked unavailable / off-duty"
                )
                ranked.append(breakdown)
                continue

            if not tech.has_roster_slot:
                breakdown = cls._create_ineligible_breakdown(
                    tech, "Technician has no active roster slot for shift (M55 roster integration)"
                )
                ranked.append(breakdown)
                continue

            if tech.on_leave:
                breakdown = cls._create_ineligible_breakdown(
                    tech, "Technician is on approved leave (M55 roster integration)"
                )
                ranked.append(breakdown)
                continue

            if tech.current_workload_count >= tech.max_daily_capacity:
                breakdown = cls._create_ineligible_breakdown(
                    tech,
                    f"Max daily capacity exceeded ({tech.current_workload_count}/{tech.max_daily_capacity})",
                )
                ranked.append(breakdown)
                continue

            # FR-LMS-039 (STUB-M02-M22-001 CLOSED): verify required certifications
            if request.required_certifications:
                missing_certs = [
                    c for c in request.required_certifications if c not in tech.certifications
                ]
                if missing_certs:
                    breakdown = cls._create_ineligible_breakdown(
                        tech,
                        f"FR-LMS-039: Technician holds no ACTIVE certification for required scope ({', '.join(missing_certs)}) (M22 certification integration)",
                    )
                    ranked.append(breakdown)
                    continue

            # 2. Compute 6 dimensional scores (0.0 to 100.0)
            skill_score = cls._score_skills(request.required_skills, tech.skills)
            cert_score = cls._score_certification(tech, request.required_certifications)
            van_stock_score = cls._score_van_stock(request.required_parts_skus, tech.van_stock_skus)
            zone_score = cls._score_zone(request.zone_code, tech.home_zone_code)
            sla_risk_score = cls._score_sla_risk(request.sla_hours_remaining, request.priority)
            route_score, est_dist_km, est_time_min = cls._score_route_proximity(
                request.customer_lat, request.customer_lon, tech.current_lat, tech.current_lon
            )

            # 3. Weighted composite score
            w = request.weights
            total_weight = w.skill + w.certification + w.van_stock + w.zone + w.sla_risk + w.route
            if total_weight <= 0:
                total_weight = 1.0

            composite = (
                (w.skill * skill_score)
                + (w.certification * cert_score)
                + (w.van_stock * van_stock_score)
                + (w.zone * zone_score)
                + (w.sla_risk * sla_risk_score)
                + (w.route * route_score)
            ) / total_weight

            breakdown = CandidateScoreBreakdown(
                technician_id=tech.id,
                technician_name=tech.name,
                composite_score=round(composite, 2),
                skill_score=round(skill_score, 2),
                certification_score=round(cert_score, 2),
                van_stock_score=round(van_stock_score, 2),
                zone_score=round(zone_score, 2),
                sla_risk_score=round(sla_risk_score, 2),
                route_score=round(route_score, 2),
                estimated_travel_time_min=round(est_time_min, 1),
                estimated_distance_km=round(est_dist_km, 2),
                eligible=True,
                rejection_reason=None,
            )
            ranked.append(breakdown)

        # Sort: eligible first, then composite_score descending, then travel time ascending
        ranked.sort(
            key=lambda x: (x.eligible, x.composite_score, -x.estimated_travel_time_min),
            reverse=True,
        )

        recommended = next((c for c in ranked if c.eligible), None)

        return DispatchScoreResponse(
            job_id=request.job_id,
            total_candidates_evaluated=len(request.candidates),
            recommended_technician=recommended,
            ranked_candidates=ranked,
        )

    @classmethod
    def _create_ineligible_breakdown(
        cls, tech: TechnicianCandidate, reason: str
    ) -> CandidateScoreBreakdown:
        return CandidateScoreBreakdown(
            technician_id=tech.id,
            technician_name=tech.name,
            composite_score=0.0,
            skill_score=0.0,
            certification_score=0.0,
            van_stock_score=0.0,
            zone_score=0.0,
            sla_risk_score=0.0,
            route_score=0.0,
            estimated_travel_time_min=0.0,
            estimated_distance_km=0.0,
            eligible=False,
            rejection_reason=reason,
        )

    @staticmethod
    def _score_skills(required: list[str], technician_skills: list[str]) -> float:
        if not required:
            return 100.0
        req_set = {s.lower() for s in required}
        tech_set = {s.lower() for s in technician_skills}
        matched = len(req_set.intersection(tech_set))
        return (matched / len(req_set)) * 100.0

    @classmethod
    def _score_certification(
        cls, tech: TechnicianCandidate, required_certs: list[str] | None = None
    ) -> float:
        """Evaluates technician certifications honoring STUB-M02-M22-001 (CLOSED in R06-M04).
        Computes active certification matching per FR-LMS-039."""
        if not required_certs:
            return 100.0 if tech.certifications else 80.0
        req_set = {c.lower() for c in required_certs}
        tech_set = {c.lower() for c in tech.certifications}
        matched = len(req_set.intersection(tech_set))
        return (matched / len(req_set)) * 100.0

    @staticmethod
    def _score_van_stock(required_parts: list[str], van_parts: list[str]) -> float:
        if not required_parts:
            return 100.0
        req_set = {p.upper() for p in required_parts}
        van_set = {p.upper() for p in van_parts}
        matched = len(req_set.intersection(van_set))
        return (matched / len(req_set)) * 100.0

    @staticmethod
    def _score_zone(job_zone: str, tech_zone: str) -> float:
        if not job_zone or not tech_zone:
            return 50.0
        j_clean = job_zone.strip().upper()
        t_clean = tech_zone.strip().upper()
        if j_clean == t_clean:
            return 100.0
        # Adjacent zone check (e.g. DHAKA-NORTH vs DHAKA-CENTRAL)
        if ("DHAKA" in j_clean and "DHAKA" in t_clean) or ("CTG" in j_clean and "CTG" in t_clean):
            return 60.0
        return 15.0

    @staticmethod
    def _score_sla_risk(hours_remaining: float, priority: int) -> float:
        if hours_remaining <= 2.0:
            base = 100.0
        elif hours_remaining <= 4.0:
            base = 85.0
        elif hours_remaining <= 8.0:
            base = 70.0
        elif hours_remaining <= 24.0:
            base = 50.0
        else:
            base = 30.0
        # Priority boost
        boost = max(0, priority - 1) * 5.0
        return min(100.0, base + boost)

    @classmethod
    def _score_route_proximity(
        cls, cust_lat: float, cust_lon: float, tech_lat: float | None, tech_lon: float | None
    ) -> tuple[float, float, float]:
        """Calculates distance (km), estimated travel time (min), and route score."""
        if tech_lat is None or tech_lon is None:
            # Fallback when technician coordinates are unavailable
            return 50.0, 8.0, 30.0

        # Haversine distance
        dist_m = cls._haversine(cust_lat, cust_lon, tech_lat, tech_lon)
        dist_km = dist_m / 1000.0

        # Dhaka city transit speed: base 22 km/h + congestion multiplier 1.5x
        effective_speed_kmh = 16.0
        travel_time_min = (dist_km / effective_speed_kmh) * 60.0

        # Proximity score decay: 0 min = 100 score, 60 min = 40 score, 100+ min = 0 score
        score = max(0.0, 100.0 - (travel_time_min * 1.0))
        return score, dist_km, travel_time_min

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371000.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * (
            math.sin(dlam / 2.0) ** 2
        )
        return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
