"""Data models and schemas for dispatch scoring engine (CD-M02-02)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScoringWeights(BaseModel):
    """Configurable weights for the 6 scoring dimensions (must sum to 1.0)."""
    skill: float = Field(default=0.25, ge=0.0, le=1.0)
    certification: float = Field(default=0.10, ge=0.0, le=1.0)
    van_stock: float = Field(default=0.25, ge=0.0, le=1.0)
    zone: float = Field(default=0.15, ge=0.0, le=1.0)
    sla_risk: float = Field(default=0.10, ge=0.0, le=1.0)
    route: float = Field(default=0.15, ge=0.0, le=1.0)


class TechnicianCandidate(BaseModel):
    """Technician profile evaluated for dispatch eligibility and scoring."""
    id: int
    name: str
    skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    van_stock_skus: List[str] = Field(default_factory=list)
    home_zone_code: str
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None
    current_workload_count: int = 0
    max_daily_capacity: int = 6
    available: bool = True


class FieldJobRequest(BaseModel):
    """On-site field service order requesting automated dispatch scoring."""
    job_id: str
    service_order_ref: str
    required_skills: List[str] = Field(default_factory=list)
    required_parts_skus: List[str] = Field(default_factory=list)
    zone_code: str
    customer_lat: float
    customer_lon: float
    sla_hours_remaining: float = 24.0
    priority: int = 1
    candidates: List[TechnicianCandidate] = Field(default_factory=list)
    weights: ScoringWeights = Field(default_factory=ScoringWeights)


class CandidateScoreBreakdown(BaseModel):
    """Detailed dimensional score breakdown for a candidate."""
    technician_id: int
    technician_name: str
    composite_score: float
    skill_score: float
    certification_score: float
    van_stock_score: float
    zone_score: float
    sla_risk_score: float
    route_score: float
    estimated_travel_time_min: float
    estimated_distance_km: float
    eligible: bool
    rejection_reason: Optional[str] = None


class DispatchScoreResponse(BaseModel):
    """Response containing ranked candidates and recommended assignment."""
    job_id: str
    total_candidates_evaluated: int
    recommended_technician: Optional[CandidateScoreBreakdown] = None
    ranked_candidates: List[CandidateScoreBreakdown] = Field(default_factory=list)
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
