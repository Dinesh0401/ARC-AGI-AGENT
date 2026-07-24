"""Evaluation Runner for executing agents in ARC-AGI-3 environments."""

from typing import Any, Dict, List
from agents.base import BaseAgent
from environment.wrapper import ARCEnvironment
from utils.logger import get_logger

logger = get_logger("evaluation")


class EvaluationRunner:
    """Runner that handles agent-environment execution loops and metric collection."""

    def __init__(self, agent: BaseAgent, env: ARCEnvironment) -> None:
        self.agent = agent
        self.env = env

    def run_episode(self, max_steps: int = 20) -> Dict[str, Any]:
        """Run a single episode for up to `max_steps`.

        Args:
            max_steps: Maximum allowable environment steps.

        Returns:
            Dictionary containing metrics (total_steps, cumulative_reward, done, history).
        """
        logger.info(f"Starting episode with agent '{self.agent.name}' in env '{self.env.game_id}'")
        self.agent.reset()
        obs = self.env.reset()

        total_reward = 0.0
        step_count = 0
        done = False

        for step in range(1, max_steps + 1):
            action = self.agent.act(obs)
            next_obs, reward, done, info = self.env.step(action)
            self.agent.record_step(obs, action, reward, done)

            total_reward += reward
            step_count = step

            logger.info(f"Step {step}/{max_steps} | Action: {action} | Reward: {reward} | Done: {done}")

            obs = next_obs
            if done:
                logger.info(f"Episode completed at step {step}")
                break

        results = {
            "agent_name": self.agent.name,
            "game_id": self.env.game_id,
            "total_steps": step_count,
            "cumulative_reward": total_reward,
            "done": done,
            "action_history_length": len(self.agent.action_history),
        }
        logger.info(f"Episode Summary: {results}")
        return results
