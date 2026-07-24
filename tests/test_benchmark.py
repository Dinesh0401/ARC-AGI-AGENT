import pytest
from pathlib import Path
from benchmark import (
    MetricsCollector,
    ResultLogger,
    ReportGenerator,
    BenchmarkVisualizer,
    compare_agents,
)
from agents.cognitive_agent import CognitiveAgent
from environment.wrapper import ARCEnvironment


def test_metrics_collector():
    collector = MetricsCollector()
    agent = CognitiveAgent(name="TestCognitive")
    env = ARCEnvironment(game_id="sample_game")
    obs = env.reset()

    # Step once
    action = agent.act(obs)
    next_obs, reward, done, info = env.step(action)
    agent.record_step(obs, action, reward, info.get("status", "NOT_FINISHED"), info=info)

    result = {
        "status": "NOT_FINISHED",
        "total_steps": 1,
        "cumulative_reward": reward,
    }

    metrics = collector.collect(
        agent=agent,
        game_id="sample_game",
        episode_index=1,
        result=result,
        duration_sec=0.1,
    )

    assert metrics.agent_name == "TestCognitive"
    assert metrics.game_id == "sample_game"
    assert metrics.total_steps == 1
    assert metrics.mem_metrics is not None
    assert metrics.mem_metrics.working_thoughts_count > 0


def test_compare_agents_execution(tmp_path):
    output_dir = tmp_path / "results"
    logger = ResultLogger(output_dir=output_dir)

    comparison = compare_agents(num_episodes=2, max_steps=5, game_id="sample_game")

    assert "RandomAgent-Baseline" in comparison
    assert "CognitiveAgent-FullPipeline" in comparison
    assert (output_dir / "results.json").exists() or (Path("results") / "results.json").exists()
