"""Head-to-head comparative evaluation runner for RandomAgent vs CognitiveAgent."""

import argparse
from typing import Dict, Any
from agents.random_agent import RandomAgent
from agents.cognitive_agent import CognitiveAgent
from environment.wrapper import ARCEnvironment
from benchmark.benchmark_runner import BenchmarkRunner
from benchmark.report_generator import ReportGenerator
from benchmark.visualization import BenchmarkVisualizer
from benchmark.config import DEFAULT_EPISODES, DEFAULT_MAX_STEPS


def compare_agents(
    num_episodes: int = DEFAULT_EPISODES,
    max_steps: int = DEFAULT_MAX_STEPS,
    game_id: str = "sample_game",
    seed: int = 42,
) -> Dict[str, Dict[str, Any]]:
    """Run head-to-head comparison between RandomAgent and CognitiveAgent."""
    env = ARCEnvironment(game_id=game_id)

    # 1. Evaluate RandomAgent
    random_agent = RandomAgent(name="RandomAgent-Baseline", seed=seed)
    runner_random = BenchmarkRunner(agent=random_agent, env=env)
    res_random = runner_random.run_benchmark(num_episodes=num_episodes, max_steps=max_steps)

    # 2. Evaluate CognitiveAgent
    cognitive_agent = CognitiveAgent(name="CognitiveAgent-FullPipeline", seed=seed)
    runner_cog = BenchmarkRunner(agent=cognitive_agent, env=env)
    res_cog = runner_cog.run_benchmark(num_episodes=num_episodes, max_steps=max_steps)

    comparison = {
        random_agent.name: res_random,
        cognitive_agent.name: res_cog,
    }

    # 3. Generate Report & Plots
    report_gen = ReportGenerator()
    report_text = report_gen.generate_report(comparison)

    visualizer = BenchmarkVisualizer()
    visualizer.generate_plots(comparison)

    print("\n" + "=" * 60)
    print(report_text)
    print("=" * 60 + "\n")

    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run head-to-head benchmark comparing RandomAgent vs CognitiveAgent"
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=DEFAULT_EPISODES,
        help="Number of episodes per agent",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=DEFAULT_MAX_STEPS,
        help="Maximum steps allowed per episode",
    )
    parser.add_argument(
        "--game",
        type=str,
        default="sample_game",
        help="Environment Game ID",
    )

    args = parser.parse_args()
    compare_agents(
        num_episodes=args.episodes,
        max_steps=args.max_steps,
        game_id=args.game,
    )


if __name__ == "__main__":
    main()
