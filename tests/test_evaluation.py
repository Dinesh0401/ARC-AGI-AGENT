"""Unit tests for EvaluationRunner multi-episode benchmark."""

import pytest
from agents.random_agent import RandomAgent
from environment.wrapper import ARCEnvironment
from evaluation.runner import EvaluationRunner


def test_single_episode_run() -> None:
    env = ARCEnvironment(game_id="test_env")
    agent = RandomAgent(name="TestAgent", seed=42)
    runner = EvaluationRunner(agent=agent, env=env)

    result = runner.run_episode(max_steps=5)
    assert result["agent_name"] == "TestAgent"
    assert result["game_id"] == "test_env"
    assert result["total_steps"] <= 5
    assert "history_summary" in result


def test_multi_episode_benchmark_run() -> None:
    env = ARCEnvironment(game_id="test_env")
    agent = RandomAgent(name="TestAgent", seed=42)
    runner = EvaluationRunner(agent=agent, env=env)

    summary = runner.run_benchmark(num_episodes=3, max_steps=5)
    assert summary["agent_name"] == "TestAgent"
    assert summary["num_episodes"] == 3
    assert len(summary["episodes"]) == 3
    assert "win_rate_percent" in summary
    assert "avg_steps_per_episode" in summary
