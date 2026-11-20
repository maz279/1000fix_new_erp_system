"""M43 planning engine — the deterministic maths behind the capture models.

Pure Python (no Odoo import) so every rule is unit-testable against known
values (T-04: the local method is deterministic and tested). The Odoo models
in this package call these functions; none of them writes anything, which is
what lets the what-if simulation reuse them without side effects (T-09,
BRU-DPL-15).

Spec: 1000fix_ERP_Module/03_Modules/E_Supply_Chain_and_Inventory/
M43_Demand_Planning_and_Replenishment.md §5, §8, §9.
"""
from __future__ import annotations

import math
from statistics import NormalDist, mean, pstdev

# Syntetos–Boylan–Croston cut-offs for demand-pattern classification
# (FR-DPL-008): average inter-demand interval and squared coefficient of
# variation of non-zero demand sizes.
ADI_CUTOFF = 1.32
CV2_CUTOFF = 0.49

# Readiness gate minimums (FR-DPL-005, BRU-DPL-01).
MIN_HISTORY_MONTHS = 12
MIN_DEMAND_DENSITY = 0.20
MIN_COMPLETENESS = 0.90


class PlanningError(ValueError):
    """A planning input that the spec forbids (raised, never silently fixed)."""


def classify_intermittency(adi: float, cv2: float) -> str:
    """FR-DPL-008: smooth / erratic / intermittent / lumpy."""
    if adi is None or cv2 is None or adi <= 0 or cv2 < 0:
        raise PlanningError("ADI must be > 0 and CV² must be ≥ 0")
    if adi < ADI_CUTOFF:
        return "smooth" if cv2 < CV2_CUTOFF else "erratic"
    return "intermittent" if cv2 < CV2_CUTOFF else "lumpy"


def method_for(intermittency: str, critical: bool = False) -> str:
    """FR-DPL-011 / BRU-DPL-04: the forecasting method follows the demand
    pattern. Single exponential smoothing is never used for intermittent or
    lumpy demand; critical intermittent parts get bootstrapped lead-time
    demand."""
    if intermittency in ("intermittent", "lumpy"):
        return "bootstrap" if critical else "croston_sba"
    if intermittency in ("smooth", "erratic"):
        return "ets"
    raise PlanningError(f"unknown intermittency class {intermittency!r}")


def nine_box(abc_class: str, xyz_class: str) -> str:
    """FR-DPL-006: the ABC × XYZ cell, e.g. 'AX'."""
    if abc_class not in ("a", "b", "c") or xyz_class not in ("x", "y", "z"):
        raise PlanningError("ABC must be a/b/c and XYZ must be x/y/z")
    return (abc_class + xyz_class).upper()


def default_policy(abc_class: str, xyz_class: str, criticality: str) -> str:
    """BRU-DPL-17: a CZ part defaults to order-on-demand unless it is
    job-stopping critical; everything else starts on a continuous ROP."""
    if abc_class == "c" and xyz_class == "z" and criticality != "job_stopping":
        return "order_on_demand"
    return "continuous_rop"


def readiness_verdict(months: float, density: float, completeness: float,
                      contaminated: bool) -> str:
    """FR-DPL-005 / BRU-DPL-01: 'ready' or 'provisional'. A provisional
    part-location never gets a published statistical forecast."""
    if contaminated:
        return "provisional"
    if (months or 0) < MIN_HISTORY_MONTHS:
        return "provisional"
    if (density or 0) < MIN_DEMAND_DENSITY or (completeness or 0) < MIN_COMPLETENESS:
        return "provisional"
    return "ready"


def z_for_service_level(service_level_pct: float) -> float:
    """Cycle-service z-score for a target in percent (e.g. 98 → 2.054)."""
    if service_level_pct is None or not 50.0 <= service_level_pct < 100.0:
        raise PlanningError("service level must be in [50, 100) percent")
    return NormalDist().inv_cdf(service_level_pct / 100.0)


def safety_stock(service_level_pct: float, mean_daily_demand: float,
                 std_daily_demand: float, mean_lead_days: float,
                 std_lead_days: float) -> float:
    """FR-DPL-020 / BRU-DPL-07: safety stock from demand AND lead-time
    variability against a service target — never a flat multiplier.

        SS = z · sqrt(L · σd² + d² · σL²)
    """
    for v in (mean_daily_demand, std_daily_demand, mean_lead_days, std_lead_days):
        if v is None or v < 0:
            raise PlanningError("demand and lead-time inputs must be ≥ 0")
    z = z_for_service_level(service_level_pct)
    variance = (mean_lead_days * std_daily_demand ** 2
                + mean_daily_demand ** 2 * std_lead_days ** 2)
    return round(z * math.sqrt(variance), 2)


def reorder_point(mean_daily_demand: float, mean_lead_days: float,
                  safety: float) -> float:
    """FR-DPL-021: ROP = lead-time demand + safety stock."""
    return round(mean_daily_demand * mean_lead_days + safety, 2)


def economic_order_quantity(annual_demand: float, order_cost: float,
                            unit_holding_cost: float) -> float:
    """FR-DPL-021: Wilson EOQ = sqrt(2·D·S / H). Zero when not computable."""
    if not annual_demand or not order_cost or not unit_holding_cost:
        return 0.0
    if annual_demand < 0 or order_cost < 0 or unit_holding_cost < 0:
        raise PlanningError("EOQ inputs must be ≥ 0")
    return round(math.sqrt(2.0 * annual_demand * order_cost / unit_holding_cost), 2)


def apply_order_constraints(quantity: float, moq: float = 0.0,
                            pack_size: float = 0.0) -> tuple[float, list[str]]:
    """BRU-DPL-10: respect supplier MOQ and pack size; every adjustment is
    returned so the caller records it."""
    notes: list[str] = []
    qty = max(quantity or 0.0, 0.0)
    if moq and qty < moq:
        notes.append(f"raised {qty:g} to supplier MOQ {moq:g}")
        qty = moq
    if pack_size and pack_size > 0:
        packs = math.ceil(qty / pack_size - 1e-9)
        rounded = packs * pack_size
        if rounded != qty:
            notes.append(f"rounded {qty:g} up to {packs} pack(s) of {pack_size:g}")
            qty = rounded
    return round(qty, 2), notes


def requires_planner_review(abc_class: str, criticality: str,
                            old_value: float, new_value: float,
                            max_change_pct: float = 25.0) -> bool:
    """BRU-DPL-08 / T-13: A-class and job-stopping parts always need a
    planner; B and C apply automatically only inside the guard rail."""
    if abc_class == "a" or criticality == "job_stopping":
        return True
    if not old_value:
        return False  # first parameter set for a B/C part — nothing to breach
    change = abs((new_value or 0.0) - old_value) / abs(old_value) * 100.0
    return change > max_change_pct


def rebalance_net_benefit(benefit_value: float, transfer_cost: float) -> float:
    """BRU-DPL-13: a transfer is proposed only where this is positive."""
    return round((benefit_value or 0.0) - (transfer_cost or 0.0), 2)


def lead_time_statistics(samples: list[float]) -> dict:
    """FR-DPL-019 / BRU-DPL-09: mean, population σ and nearest-rank P95 of
    ACTUAL receipt lead times (never the supplier's quoted figure)."""
    clean = sorted(float(s) for s in samples if s is not None and s >= 0)
    if not clean:
        return {"sample_count": 0, "mean_days": 0.0, "std_dev_days": 0.0, "p95_days": 0.0}
    rank = max(1, math.ceil(0.95 * len(clean)))
    return {
        "sample_count": len(clean),
        "mean_days": round(mean(clean), 2),
        "std_dev_days": round(pstdev(clean), 2) if len(clean) > 1 else 0.0,
        "p95_days": clean[rank - 1],
    }


def mape(pairs: list[tuple[float, float]]) -> float:
    """FR-DPL-016: mean absolute percentage error over (forecast, actual)
    pairs, in percent; periods with zero actual are skipped (undefined)."""
    errs = [abs(f - a) / abs(a) for f, a in pairs if a]
    return round(100.0 * sum(errs) / len(errs), 2) if errs else 0.0


def bias(pairs: list[tuple[float, float]]) -> float:
    """FR-DPL-016: signed bias (Σ(forecast − actual) / Σ actual), percent.
    Positive = over-forecasting."""
    total_actual = sum(a for _, a in pairs)
    if not total_actual:
        return 0.0
    return round(100.0 * sum(f - a for f, a in pairs) / total_actual, 2)


def simulate_tradeoff(base_service_level: float, new_service_level: float,
                      base_safety_value: float, base_cycle_value: float,
                      demand_change_pct: float = 0.0,
                      lead_time_change_pct: float = 0.0) -> dict:
    """FR-DPL-024: the investment / service trade-off for a changed target.

    Safety stock scales with z, with sqrt of lead time and linearly with
    demand; cycle stock scales with demand. Pure — returns numbers only, so
    a simulation can never write parameters (BRU-DPL-15)."""
    z0 = z_for_service_level(base_service_level)
    z1 = z_for_service_level(new_service_level)
    demand_factor = 1.0 + (demand_change_pct or 0.0) / 100.0
    lt_factor = 1.0 + (lead_time_change_pct or 0.0) / 100.0
    if demand_factor < 0 or lt_factor <= 0:
        raise PlanningError("demand change must be ≥ −100% and lead-time change > −100%")
    safety = (base_safety_value or 0.0) * (z1 / z0 if z0 else 0.0) * demand_factor * math.sqrt(lt_factor)
    cycle = (base_cycle_value or 0.0) * demand_factor
    return {
        "resulting_investment": round(safety + cycle, 2),
        "resulting_service_level": round(new_service_level, 2),
        "resulting_stockout_risk": round(100.0 - new_service_level, 2),
    }
