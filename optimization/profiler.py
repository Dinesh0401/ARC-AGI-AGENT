"""Runtime Profiler tracking sub-module latencies during agent execution."""

import time
from typing import Dict, List
from pathlib import Path
from benchmark.config import RESULTS_DIR


class RuntimeProfiler:
    """Profiles latency across perception, memory, reasoning, planning, world model, and learning."""

    def __init__(self) -> None:
        self.module_times: Dict[str, List[float]] = {
            "perception": [],
            "memory": [],
            "reasoning": [],
            "planning": [],
            "world_model": [],
            "learning": [],
        }

    def record_latency(self, module_name: str, duration_ms: float) -> None:
        if module_name in self.module_times:
            self.module_times[module_name].append(duration_ms)

    def get_summary(self) -> Dict[str, Dict[str, float]]:
        summary: Dict[str, Dict[str, float]] = {}
        for mod, times in self.module_times.items():
            if times:
                avg_t = sum(times) / len(times)
                max_t = max(times)
                summary[mod] = {"avg_ms": round(avg_t, 3), "max_ms": round(max_t, 3), "calls": len(times)}
            else:
                summary[mod] = {"avg_ms": 0.0, "max_ms": 0.0, "calls": 0}
        return summary

    def save_report(self, output_file: Path = RESULTS_DIR / "runtime_profile.csv") -> None:
        summary = self.get_summary()
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("module,avg_ms,max_ms,calls\n")
            for mod, data in summary.items():
                f.write(f"{mod},{data['avg_ms']},{data['max_ms']},{data['calls']}\n")
