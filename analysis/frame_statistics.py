"""Frame-level trajectory statistics and cell color distribution metrics."""

from typing import Any, Dict, List
import numpy as np


class FrameStatistics:
    """Computes color distributions, frame difference statistics, and grid dimensions."""

    @staticmethod
    def get_color_histogram(frame: List[List[int]]) -> Dict[int, int]:
        """Compute pixel count histogram across 16 color values (0-15)."""
        frame_np = np.array(frame, dtype=int)
        counts: Dict[int, int] = {}
        for c in range(16):
            cnt = int(np.sum(frame_np == c))
            if cnt > 0:
                counts[c] = cnt
        return counts

    @staticmethod
    def analyze_trajectory_frames(trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a full step trajectory of frame objects.

        Args:
            trajectory: List of step frame payloads.

        Returns:
            Dictionary containing frame statistics summary.
        """
        diff_counts = [step.get("diff_cells", 0) for step in trajectory]
        avg_diff = float(np.mean(diff_counts)) if diff_counts else 0.0
        max_diff = int(np.max(diff_counts)) if diff_counts else 0

        # Accumulate total color histogram
        total_histogram: Dict[int, int] = {}
        for step in trajectory:
            grid = step.get("frame", step.get("grid", []))
            if grid:
                hist = FrameStatistics.get_color_histogram(grid)
                for color, cnt in hist.items():
                    total_histogram[color] = total_histogram.get(color, 0) + cnt

        return {
            "total_frames_analyzed": len(trajectory),
            "avg_frame_diff_cells": round(avg_diff, 2),
            "max_frame_diff_cells": max_diff,
            "overall_color_distribution": total_histogram,
        }
