"""Statistical analysis utilities for compute confidence intervals, std dev, mean, and median."""

import math
from typing import Dict, List, Any


class StatisticalAnalyzer:
    """Computes rigorous statistical metrics for benchmark data."""

    @staticmethod
    def calculate_stats(values: List[float]) -> Dict[str, float]:
        """Compute mean, median, std dev, and 95% confidence interval half-width."""
        if not values:
            return {"mean": 0.0, "median": 0.0, "std_dev": 0.0, "ci_95": 0.0}

        n = len(values)
        mean = sum(values) / n

        sorted_vals = sorted(values)
        if n % 2 == 1:
            median = sorted_vals[n // 2]
        else:
            median = (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0

        variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0.0
        std_dev = math.sqrt(variance)

        # 95% Confidence Interval half-width using Z=1.96 (for sample > 1)
        stderr = std_dev / math.sqrt(n) if n > 0 else 0.0
        ci_95 = 1.96 * stderr

        return {
            "mean": round(mean, 4),
            "median": round(median, 4),
            "std_dev": round(std_dev, 4),
            "ci_95": round(ci_95, 4),
        }
