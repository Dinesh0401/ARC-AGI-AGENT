"""CLI entry point for ARC-AGI-3 research agent baseline, visualizer, benchmarking, and analysis."""

import argparse
import json
from pathlib import Path
from agents.random_agent import RandomAgent
from agents.cognitive_agent import CognitiveAgent
from environment.wrapper import ARCEnvironment
from evaluation.runner import EvaluationRunner
from benchmark.benchmark_runner import BenchmarkRunner
from benchmark.report_generator import ReportGenerator
from benchmark.visualization import BenchmarkVisualizer
from utils.logger import setup_logger
from utils.visualizer import render_ansi_grid
from utils.replay import ReplayLogger, ReplayViewer
from analysis.frame_statistics import FrameStatistics
from analysis.action_statistics import ActionStatistics


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ARC-AGI-3 Research Agent Baseline, Visualizer, Benchmark & Trajectory Analysis"
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="cognitive",
        choices=["cognitive", "random"],
        help="Agent architecture type to evaluate (cognitive or random)",
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
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run multi-episode benchmark evaluation",
    )
    parser.add_argument(
        "--num-episodes",
        type=int,
        default=5,
        help="Number of episodes to execute during benchmarking",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Render live ANSI color grid in terminal after each step",
    )
    parser.add_argument(
        "--save-replay",
        type=str,
        default=None,
        help="Optional path to save JSON trajectory replay",
    )
    parser.add_argument(
        "--view-replay",
        type=str,
        default=None,
        help="Path to saved JSON replay file to play back in terminal",
    )
    parser.add_argument(
        "--analyze",
        type=str,
        default=None,
        help="Path to saved JSON replay file to perform trajectory statistical analysis",
    )

    args = parser.parse_args()
    logger = setup_logger("main")

    # Analyze trajectory replay mode
    if args.analyze:
        replay_path = Path(args.analyze)
        if not replay_path.exists():
            logger.error(f"Replay file '{replay_path}' does not exist.")
            return
        with open(replay_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        trajectory = data.get("trajectory", [])

        frame_stats = FrameStatistics.analyze_trajectory_frames(trajectory)
        action_stats = ActionStatistics.analyze_action_trajectory(trajectory)

        print(f"\n================ TRAJECTORY ANALYSIS: {data.get('game_id')} ================")
        print(f"Total Steps: {action_stats['total_actions']}")
        print(f"Final Status: {data.get('final_status')}")
        print(f"Action Counts: {action_stats['action_counts']}")
        print(f"Complex Actions (ACTION6): {action_stats['complex_action_count']}")
        print(f"Avg Modified Cells/Step: {frame_stats['avg_frame_diff_cells']}")
        print(f"Max Modified Cells/Step: {frame_stats['max_frame_diff_cells']}")
        print(f"Color Histogram (0-15): {frame_stats['overall_color_distribution']}")
        print("========================================================================\n")
        return

    # View trajectory replay mode
    if args.view_replay:
        replay_path = Path(args.view_replay)
        if not replay_path.exists():
            logger.error(f"Replay file '{replay_path}' does not exist.")
            return
        viewer = ReplayViewer(replay_path)
        viewer.display_terminal_replay()
        return

    env = ARCEnvironment(game_id=args.env)

    if args.agent == "random":
        agent = RandomAgent(name="RandomAgent-Baseline", seed=args.seed)
    else:
        agent = CognitiveAgent(name="CognitiveAgent-FullPipeline", seed=args.seed)

    # Multi-episode Benchmark mode
    if args.benchmark:
        benchmark_runner = BenchmarkRunner(agent=agent, env=env)
        metrics = benchmark_runner.run_benchmark(
            num_episodes=args.num_episodes, max_steps=args.max_steps
        )

        # Generate report and charts
        report_gen = ReportGenerator()
        report_gen.generate_report({agent.name: metrics})
        visualizer = BenchmarkVisualizer()
        visualizer.generate_plots({agent.name: metrics})

        print("\n================ BENCHMARK SUMMARY ================")
        print(f"Agent: {metrics['agent_name']}")
        print(f"Total Episodes: {metrics['total_episodes']}")
        print(f"Win Rate: {metrics['win_rate_percent']}%")
        print(f"Avg Steps/Episode: {metrics['avg_steps']}")
        print(f"Avg Efficiency Score: {metrics['avg_efficiency']}")
        print("Results saved to results/results.csv and results/results.json")
        print("===================================================\n")
        return

    # Single episode execution loop with optional visualizer & replay logging
    logger.info(f"Initializing single episode evaluation for agent '{agent.name}'...")
    runner = EvaluationRunner(agent=agent, env=env)
    replay_logger = ReplayLogger(game_id=args.env) if args.save_replay else None

    result = runner.run_episode(
        max_steps=args.max_steps, replay_logger=replay_logger
    )

    if args.visualize:
        print("\n--- SINGLE EPISODE STEP TRAJECTORY ---")
        for rec in agent.history.records:
            print(
                f"Step {rec.step} | Action: {rec.action} | Status: {rec.status} | Diff: {rec.diff_cells} cells"
            )
        print()

    if replay_logger and args.save_replay:
        replay_logger.save(Path(args.save_replay))

    summary = agent.history.get_summary()
    logger.info(f"Episode Completed! Final Status: {result['status']} | Summary: {summary}")


if __name__ == "__main__":
    main()
