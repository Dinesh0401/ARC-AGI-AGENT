"""Benchmark runner coordinating single & multi-game evaluation runs."""

import time
from typing import Dict, Any, List, Optional
from agents.base import BaseAgent
from environment.wrapper import ARCEnvironment
from evaluation.runner import EvaluationRunner
from benchmark.metrics_collector import MetricsCollector
from benchmark.result_logger import ResultLogger
from benchmark.evaluation_metrics import EpisodeMetrics


class BenchmarkRunner:
    """Coordinates multi-episode benchmark runs for an agent."""

    def __init__(self, agent: BaseAgent, env: ARCEnvironment) -> None:
        self.agent = agent
        self.env = env
        self.collector = MetricsCollector()
        self.logger = ResultLogger()

    def run_benchmark(
        self, num_episodes: int = 5, max_steps: int = 20, human_baseline_actions: int = 15
    ) -> Dict[str, Any]:
        """Execute benchmark episodes and collect detailed metrics."""
        eval_runner = EvaluationRunner(agent=self.agent, env=self.env)
        episodes: List[EpisodeMetrics] = []

        for ep in range(1, num_episodes + 1):
            t0 = time.time()
            res = eval_runner.run_episode(
                max_steps=max_steps, human_baseline_actions=human_baseline_actions
            )
            duration = time.time() - t0

            ep_metric = self.collector.collect(
                agent=self.agent,
                game_id=self.env.game_id,
                episode_index=ep,
                result=res,
                duration_sec=duration,
                human_baseline_actions=human_baseline_actions,
            )
            episodes.append(ep_metric)

        return self.logger.log_episodes(self.agent.name, episodes)
