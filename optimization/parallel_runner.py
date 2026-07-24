"""Multiprocessing parallel runner for concurrent game evaluation."""

from typing import List, Dict, Any, Callable
import concurrent.futures


class ParallelBenchmarkRunner:
    """Executes multi-game evaluation workloads across CPU cores."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers

    def run_parallel(self, eval_func: Callable[[str], Dict[str, Any]], game_ids: List[str]) -> List[Dict[str, Any]]:
        """Run eval_func concurrently for each game_id."""
        results: List[Dict[str, Any]] = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_game = {executor.submit(eval_func, gid): gid for gid in game_ids}
            for future in concurrent.futures.as_completed(future_to_game):
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    gid = future_to_game[future]
                    results.append({"game_id": gid, "error": str(exc), "status": "ERROR"})
        return results
