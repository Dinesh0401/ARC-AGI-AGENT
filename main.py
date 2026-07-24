"""CLI entry point to execute ARC-AGI-3 research agent experiments."""

import argparse
import sys
from agents.random_agent import RandomAgent
from environment.wrapper import ARCEnvironment
from evaluation.runner import EvaluationRunner
from utils.logger import setup_logger


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ARC-AGI-3 Research Agent Baseline Runner"
    )
    parser.add_argument(
        "--env",
        type=str,
        default="sample_game",
        help="Environment / Game ID to evaluate on",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum steps allowed per episode",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for agent reproducibility",
    )

    args = parser.parse_args()

    logger = setup_logger("main")
    logger.info("Initializing ARC-AGI-3 Research Agent framework...")

    # Initialize environment and baseline agent
    env = ARCEnvironment(game_id=args.env)
    agent = RandomAgent(name="RandomAgent-Baseline", seed=args.seed)

    runner = EvaluationRunner(agent=agent, env=env)
    metrics = runner.run_episode(max_steps=args.max_steps)

    logger.info("Phase 0 Baseline Execution Successful!")
    logger.info(f"Final Metrics: {metrics}")


if __name__ == "__main__":
    main()
