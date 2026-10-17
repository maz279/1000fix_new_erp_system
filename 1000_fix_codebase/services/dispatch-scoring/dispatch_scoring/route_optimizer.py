"""Route optimization engine implementing TSP/VRP with baseline travel-time comparison (G2-03)."""
import math
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any


@dataclass
class RouteStop:
    stop_id: str
    name: str
    lat: float
    lon: float
    time_window_start: str = "09:00"
    time_window_end: str = "18:00"
    service_duration_min: float = 30.0


@dataclass
class RouteOptimizationResult:
    technician_id: int
    date: str
    depot_name: str
    baseline_stops_sequence: List[str]
    optimized_stops_sequence: List[str]
    baseline_distance_km: float
    optimized_distance_km: float
    baseline_travel_time_min: float
    optimized_travel_time_min: float
    travel_time_savings_pct: float
    achieves_g2_target: bool  # >= 15.0% travel-time reduction


class RouteOptimizer:
    """Solves TSP / VRP over geographic distance matrix and compares with baseline unoptimized sequence."""

    DHAKA_CONGESTION_FACTOR = 1.65  # Dhaka urban transit multiplier
    AVERAGE_SPEED_KMH = 20.0

    @classmethod
    def optimize_itinerary(
        cls,
        technician_id: int,
        date: str,
        depot: RouteStop,
        stops: List[RouteStop],
    ) -> RouteOptimizationResult:
        if len(stops) < 2:
            raise ValueError("At least 2 customer stops are required for route optimization.")

        all_points = [depot] + stops
        n = len(all_points)

        # 1. Compute distance matrix (km)
        dist_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_matrix[i][j] = cls._haversine_km(
                        all_points[i].lat, all_points[i].lon,
                        all_points[j].lat, all_points[j].lon,
                    )

        # 2. Baseline naive trip: sequential FIFO booking order (0 -> 1 -> 2 -> ... -> N -> 0)
        baseline_order = list(range(n)) + [0]
        baseline_dist = sum(dist_matrix[baseline_order[k]][baseline_order[k + 1]] for k in range(len(baseline_order) - 1))
        baseline_time_min = (baseline_dist / cls.AVERAGE_SPEED_KMH) * 60.0 * cls.DHAKA_CONGESTION_FACTOR

        # 3. Optimized route via Nearest Neighbor heuristic + 2-opt refinement (VROOM simulation)
        optimized_indices = cls._solve_tsp_2opt(dist_matrix)
        optimized_order = [0] + optimized_indices + [0]
        optimized_dist = sum(dist_matrix[optimized_order[k]][optimized_order[k + 1]] for k in range(len(optimized_order) - 1))
        optimized_time_min = (optimized_dist / cls.AVERAGE_SPEED_KMH) * 60.0 * cls.DHAKA_CONGESTION_FACTOR

        # 4. Travel-time savings calculation
        if baseline_time_min > 0:
            savings_pct = round(((baseline_time_min - optimized_time_min) / baseline_time_min) * 100.0, 2)
        else:
            savings_pct = 0.0

        return RouteOptimizationResult(
            technician_id=technician_id,
            date=date,
            depot_name=depot.name,
            baseline_stops_sequence=[all_points[idx].stop_id for idx in baseline_order],
            optimized_stops_sequence=[all_points[idx].stop_id for idx in optimized_order],
            baseline_distance_km=round(baseline_dist, 2),
            optimized_distance_km=round(optimized_dist, 2),
            baseline_travel_time_min=round(baseline_time_min, 1),
            optimized_travel_time_min=round(optimized_time_min, 1),
            travel_time_savings_pct=savings_pct,
            achieves_g2_target=(savings_pct >= 15.0),
        )

    @classmethod
    def _solve_tsp_2opt(cls, matrix: List[List[float]]) -> List[int]:
        """Nearest Neighbor initial tour followed by 2-opt edge swapping."""
        n = len(matrix)
        unvisited = set(range(1, n))
        current = 0
        tour = []

        while unvisited:
            next_node = min(unvisited, key=lambda node: matrix[current][node])
            unvisited.remove(next_node)
            tour.append(next_node)
            current = next_node

        # 2-opt refinement
        improved = True
        while improved:
            improved = False
            for i in range(len(tour) - 1):
                for j in range(i + 1, len(tour)):
                    prev_cost = (
                        matrix[0 if i == 0 else tour[i - 1]][tour[i]]
                        + matrix[tour[j]][0 if j == len(tour) - 1 else tour[j + 1]]
                    )
                    new_cost = (
                        matrix[0 if i == 0 else tour[i - 1]][tour[j]]
                        + matrix[tour[i]][0 if j == len(tour) - 1 else tour[j + 1]]
                    )
                    if new_cost < prev_cost - 1e-4:
                        tour[i : j + 1] = reversed(tour[i : j + 1])
                        improved = True
                        break
                if improved:
                    break

        return tour

    @staticmethod
    def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2.0) ** 2
            + math.cos(p1) * math.cos(p2) * (math.sin(dl / 2.0) ** 2)
        )
        return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
