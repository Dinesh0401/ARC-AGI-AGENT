"""CLI entry point for ARC-AGI-3 Agent."""

import argparse
from typing import List, Any
from agents.random_agent import RandomAgent
from agents.cognitive_agent import CognitiveAgent
from benchmark.config import DEFAULT_GAMES

try:
    import arc_agi
except ImportError:
    arc_agi = None

def run_agent_on_game(agent, arc, game_id: str, render_mode: str = None):
    """Run a specific agent on a specific game using the official toolkit."""
    env = arc.make(game_id, render_mode=render_mode)
    obs = env.reset()
    
    # Run the game loop
    
    def _to_dict(o: Any) -> dict:
        if isinstance(o, dict): return o
        d = {"frame": getattr(o, "frame", []), "available_actions": getattr(o, "available_actions", [])}
        if hasattr(o, "state"):
            state_val = getattr(o, "state")
            d["status"] = getattr(state_val, "value", str(state_val))
        if hasattr(o, "game_id"): d["game_id"] = getattr(o, "game_id")
        return d

    # Official toolkit states: obs has 'frame'/'grid' and 'available_actions'
    obs_dict = _to_dict(obs)
    frames = [obs_dict]
    
    # Reset agent internal memory
    agent.reset()
    
    steps = 0
    from arcengine import GameAction
    while steps < 100:  # arbitrary safety limit if env doesn't terminate
        action = agent.choose_action(frames, obs_dict)
        
        # Parse action from string/tuple to GameAction
        if isinstance(action, tuple) and len(action) == 3:
            action_name, x, y = action
            game_action = getattr(GameAction, action_name, GameAction.ACTION1)
            data = {"x": x, "y": y}
        else:
            action_name = str(action)
            game_action = getattr(GameAction, action_name, GameAction.ACTION1)
            data = None
            
        # Step the environment
        obs = env.step(game_action, data=data)
        if obs is None:
            break
            
        obs_dict = _to_dict(obs)
        frames.append(obs_dict)
        
        # Check termination
        status = obs_dict.get("status")
        if status in ["WIN", "GAME_OVER"]:
            break
        
        # Or if the agent thinks it's done:
        if agent.is_done(frames, obs_dict):
            break
            
        steps += 1
        
    print(f"Finished {game_id} in {steps} steps. Final Status: {obs_dict.get('status')}")
    
    # Print Cognitive Metrics
    print("\n================ Cognitive Metrics ================")
    if hasattr(agent, 'memory') and hasattr(agent.memory, 'episodic'):
        print(f"Unique States Visited: {len(agent.memory.episodic.visit_counts)}")
    if hasattr(agent, 'hypothesis_engine'):
        print(f"Hypotheses Generated: {len(agent.hypothesis_engine.hypotheses)}")
        print(f"Verified: {len(agent.hypothesis_engine.get_verified_hypotheses())}")
        rejected_count = sum(1 for h in agent.hypothesis_engine.hypotheses.values() if h.status.name == 'REJECTED')
        print(f"Rejected: {rejected_count}")
        print(f"Still Active: {len(agent.hypothesis_engine.get_active_hypotheses())}")
    if hasattr(agent, 'prediction_engine'):
        total = getattr(agent.prediction_engine, 'total_predictions', 0)
        correct = getattr(agent.prediction_engine, 'correct_predictions', 0)
        acc = (correct / total * 100) if total > 0 else 0
        print(f"Prediction Accuracy: {acc:.1f}% ({correct}/{total})")
    if hasattr(agent, 'repeated_loop_count'):
        print(f"Repeated Loop Count: {agent.repeated_loop_count}")
    if hasattr(agent, 'object_interactions'):
        print(f"Object Interactions: {agent.object_interactions}")
    if hasattr(agent, 'planner_invocations'):
        print(f"Planner Invocations: {agent.planner_invocations}")
        successes = getattr(agent, 'planner_successes', 0)
        fallbacks = getattr(agent, 'planner_fallbacks', 0)
        print(f"Planner Success: {successes}")
        print(f"Planner Fallback: {fallbacks}")
        
        if agent.planner_invocations > 0:
            avg_conf = getattr(agent, 'total_planner_confidence', 0.0) / agent.planner_invocations
            avg_score = getattr(agent, 'total_beam_score', 0.0) / agent.planner_invocations
            print(f"Average Confidence: {avg_conf:.2f}")
            print(f"Average Beam Score: {avg_score:.2f}")
            if successes > 0:
                print(f"Average Planning Depth: {agent.total_planning_depth / successes:.1f}")
            else:
                print("Average Planning Depth: 0.0")
                
        print(f"Rollouts Expanded: {getattr(agent, 'total_rollouts_expanded', 0)}")
        print("Unique Predicted States:")
        for d, count in getattr(agent, 'unique_predicted_states_by_depth', {}).items():
            print(f"  Depth {d}: {count}")
    print("===================================================\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ARC-AGI-3 Agent Runner"
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="cognitive",
        choices=["cognitive", "random"],
        help="Agent architecture type to evaluate (cognitive or random)",
    )
    parser.add_argument(
        "--game",
        type=str,
        default="ls20",
        help="Environment / Game ID to evaluate on (e.g. ls20, ft09)",
    )
    parser.add_argument(
        "--competition",
        action="store_true",
        help="Run competition mode against multiple games and print official scorecard",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Disable terminal rendering for faster execution",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    args = parser.parse_args()

    if arc_agi is None:
        print("ERROR: Official 'arc-agi' toolkit is not installed. Please run 'pip install arc-agi'")
        return

    arc = arc_agi.Arcade()

    if args.agent == "random":
        agent = RandomAgent(name="RandomAgent", seed=args.seed)
    else:
        agent = CognitiveAgent(name="CognitiveAgent", seed=args.seed)

    render_mode = None if args.fast else "terminal"

    if args.competition:
        print("Running in Competition Mode...")
        # Run on a predefined set of games or all public games if available
        games_to_run = ["ls20", "ft09", "ar25", "bp35", "cd82"]  # Just a sample, would ideally list all 25
        for g_id in games_to_run:
            print(f"\n--- Running Game: {g_id} ---")
            try:
                run_agent_on_game(agent, arc, g_id, render_mode=render_mode)
            except Exception as e:
                print(f"Error running game {g_id}: {e}")
        
        # Official Scorecard
        print("\n================ OFFICIAL SCORECARD ================")
        print(arc.get_scorecard())
        print("====================================================")
    else:
        # Run single game
        print(f"Running single game: {args.game}")
        run_agent_on_game(agent, arc, args.game, render_mode=render_mode)
        
        print("\n================ OFFICIAL SCORECARD ================")
        print(arc.get_scorecard())
        print("====================================================")


if __name__ == "__main__":
    main()
