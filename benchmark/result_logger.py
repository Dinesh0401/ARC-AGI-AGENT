"""Result logger exporting metrics to CSV and JSON formats."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List
from benchmark.evaluation_metrics import EpisodeMetrics
from benchmark.config import RESULTS_DIR


class ResultLogger:
    """Exports benchmark telemetry to CSV and JSON files."""

    def __init__(self, output_dir: Path = RESULTS_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.csv_path = self.output_dir / "results.csv"
        self.json_path = self.output_dir / "results.json"

    def log_episodes(
        self, agent_name: str, episodes: List[EpisodeMetrics]
    ) -> Dict[str, Any]:
        """Save episode results to CSV and JSON."""
        # 1. Export JSON
        dict_episodes = [ep.to_dict() for ep in episodes]
        wins = sum(1 for ep in episodes if ep.win)
        num_eps = len(episodes)
        win_rate = (wins / num_eps * 100.0) if num_eps > 0 else 0.0
        avg_steps = sum(ep.total_steps for ep in episodes) / num_eps if num_eps > 0 else 0.0
        avg_eff = (
            sum(ep.human_efficiency_score for ep in episodes) / num_eps if num_eps > 0 else 0.0
        )

        summary = {
            "agent_name": agent_name,
            "total_episodes": num_eps,
            "win_rate_percent": round(win_rate, 2),
            "avg_steps": round(avg_steps, 2),
            "avg_efficiency": round(avg_eff, 4),
            "episodes": dict_episodes,
        }

        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # 2. Export CSV
        if dict_episodes:
            headers = list(dict_episodes[0].keys())
            file_exists = self.csv_path.exists()
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                for row in dict_episodes:
                    writer.writerow(row)

        return summary
