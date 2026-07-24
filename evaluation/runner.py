"""Evaluation Runner for executing multi-episode benchmark evaluations on ARC-AGI-3."""

import time
from typing import Any, Dict, List, Optional
from agents.base import BaseAgent
from environment.wrapper import ARCEnvironment
from utils.logger import get_logger
from utils.replay import ReplayLogger
from analysis.action_statistics import ActionStatistics

logger = get_logger("evaluation")


class EvaluationRunner:
    """Runner that executes single and multi-episode benchmark evaluations."""

    def __init__(self, agent: BaseAgent, env: ARCEnvironment) -> None:
        self.agent = agent
        self.env = env

    def run_episode(
        self,
        max_steps: int = 20,
        replay_logger: Optional[ReplayLogger] = None,
        human_baseline_actions: int = 15,
    ) -> Dict[str, Any]:
        """Run a single episode for up to `max_steps`.

        Args:
            max_steps: Maximum step limit.
            replay_logger: Optional ReplayLogger instance to record trajectory.
            human_baseline_actions: Human test-tester baseline action count for scoring.

        Returns:
            Dictionary containing episode metrics.
        """
        self.agent.on_episode_start()
        obs = self.env.reset()

        total_reward = 0.0
        step_count = 0
        status = "NOT_FINISHED"

        for step in range(1, max_steps + 1):
            t0 = time.time()
            action = self.agent.act(obs)
            duration_ms = (time.time() - t0) * 1000.0

            next_obs, reward, done, info = self.env.step(action)
            status = info.get("status", "NOT_FINISHED")
            diff_cells = info.get("diff_cells", 0)
            frame = next_obs.get("frame", next_obs.get("grid", []))

            self.agent.record_step(
                observation=obs,
                action=action,
                reward=reward,
                status=status,
                diff_cells=diff_cells,
                frame=frame,
                duration_ms=duration_ms,
                info=info,
            )

            if replay_logger:
                replay_logger.log_step(
                    step=step,
                    frame=frame,
                    action=action,
                    reward=reward,
                    status=status,
                    diff_cells=diff_cells,
                    available_actions=obs.get("available_actions", []),
                    info=info,
                )

            total_reward += reward
            step_count = step

            obs = next_obs
            if done or status in ["WIN", "GAME_OVER"]:
                break

        self.agent.on_episode_end()
        summary = self.agent.history.get_summary()
        efficiency_score = (
            ActionStatistics.calculate_efficiency_score(step_count, human_baseline_actions)
            if status == "WIN"
            else 0.0
        )

        return {
            "agent_name": self.agent.name,
            "game_id": self.env.game_id,
            "total_steps": step_count,
            "cumulative_reward": total_reward,
            "status": status,
            "efficiency_score": efficiency_score,
            "history_summary": summary,
        }

    def run_benchmark(
        self, num_episodes: int = 5, max_steps: int = 20, human_baseline_actions: int = 15
    ) -> Dict[str, Any]:
        """Execute a multi-episode benchmark evaluation.

        Args:
            num_episodes: Total number of episodes to run.
            max_steps: Maximum step limit per episode.
            human_baseline_actions: Human action baseline count.

        Returns:
            Summary dictionary with aggregate metrics (win_rate, avg_steps, avg_efficiency).
        """
        logger.info(f"Starting Benchmark: {num_episodes} Episodes for Agent '{self.agent.name}'")

        episode_results: List[Dict[str, Any]] = []
        wins = 0
        total_steps_all = 0
        total_reward_all = 0.0
        total_efficiency = 0.0

        for ep in range(1, num_episodes + 1):
            result = self.run_episode(
                max_steps=max_steps, human_baseline_actions=human_baseline_actions
            )
            episode_results.append(result)

            if result["status"] == "WIN":
                wins += 1

            total_steps_all += result["total_steps"]
            total_reward_all += result["cumulative_reward"]
            total_efficiency += result["efficiency_score"]

            logger.info(
                f"Episode {ep}/{num_episodes} | Steps: {result['total_steps']} | Status: {result['status']} | Unique States: {result['history_summary']['state_coverage']['unique_states_visited']}"
            )

        win_rate = (wins / num_episodes) * 100.0 if num_episodes > 0 else 0.0
        avg_steps = total_steps_all / num_episodes if num_episodes > 0 else 0.0
        avg_reward = total_reward_all / num_episodes if num_episodes > 0 else 0.0
        avg_efficiency = total_efficiency / num_episodes if num_episodes > 0 else 0.0

        benchmark_summary = {
            "agent_name": self.agent.name,
            "game_id": self.env.game_id,
            "num_episodes": num_episodes,
            "win_rate_percent": round(win_rate, 2),
            "avg_steps_per_episode": round(avg_steps, 2),
            "avg_reward_per_episode": round(avg_reward, 2),
            "avg_efficiency_score": round(avg_efficiency, 4),
            "episodes": episode_results,
        }

        logger.info(
            f"Benchmark Complete! Win Rate: {win_rate:.1f}% | Avg Steps: {avg_steps:.2f} | Avg Efficiency: {avg_efficiency:.4f}"
        )
        return benchmark_summary
