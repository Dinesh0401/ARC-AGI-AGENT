"""Visualization module rendering research charts for agent comparison."""

from pathlib import Path
from typing import Dict, Any, List
from benchmark.config import PLOTS_DIR

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class BenchmarkVisualizer:
    """Renders charts comparing Win Rate, Avg Steps, Efficiency, and Prediction Error."""

    def __init__(self, output_dir: Path = PLOTS_DIR) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_plots(self, comparison_data: Dict[str, Dict[str, Any]]) -> List[Path]:
        """Generate benchmark charts for agents in comparison data."""
        generated_files: List[Path] = []

        if not HAS_MATPLOTLIB or not comparison_data:
            # Create text fallbacks if matplotlib unavailable
            fallback_file = self.output_dir / "benchmark_summary.txt"
            with open(fallback_file, "w", encoding="utf-8") as f:
                f.write("BENCHMARK COMPARISON SUMMARY\n")
                f.write("============================\n")
                for agent_name, metrics in comparison_data.items():
                    f.write(
                        f"{agent_name}: Win Rate={metrics.get('win_rate_percent')}%, Avg Steps={metrics.get('avg_steps')}\n"
                    )
            return [fallback_file]

        agents = list(comparison_data.keys())
        win_rates = [comparison_data[a].get("win_rate_percent", 0.0) for a in agents]
        avg_steps = [comparison_data[a].get("avg_steps", 0.0) for a in agents]
        efficiencies = [comparison_data[a].get("avg_efficiency", 0.0) for a in agents]

        # 1. Win Rate Chart
        plt.figure(figsize=(6, 4))
        plt.bar(agents, win_rates, color=["#4C72B0", "#55A868"])
        plt.title("Benchmark Win Rate (%)")
        plt.ylabel("Win Rate (%)")
        plt.ylim(0, 100)
        p1 = self.output_dir / "win_rate.png"
        plt.savefig(p1, bbox_inches="tight")
        plt.close()
        generated_files.append(p1)

        # 2. Avg Steps Chart
        plt.figure(figsize=(6, 4))
        plt.bar(agents, avg_steps, color=["#C44E52", "#8172B0"])
        plt.title("Average Steps per Episode")
        plt.ylabel("Steps")
        p2 = self.output_dir / "steps.png"
        plt.savefig(p2, bbox_inches="tight")
        plt.close()
        generated_files.append(p2)

        # 3. Efficiency Chart
        plt.figure(figsize=(6, 4))
        plt.bar(agents, efficiencies, color=["#CCB974", "#64B5CD"])
        plt.title("Human Baseline Efficiency Score")
        plt.ylabel("Efficiency Score (0.0 - 1.0)")
        plt.ylim(0, 1.0)
        p3 = self.output_dir / "efficiency.png"
        plt.savefig(p3, bbox_inches="tight")
        plt.close()
        generated_files.append(p3)

        return generated_files
