"""Kaggle runner generating official submission JSON payloads."""

import json
from pathlib import Path
from typing import Dict, Any, List
from submission.competition_agent import CompetitionCognitiveAgent
from environment.wrapper import ARCEnvironment
from benchmark.config import BASE_DIR, DEFAULT_MAX_STEPS


class KaggleSubmissionRunner:
    """Generates official Kaggle submission format payloads."""

    def __init__(self, output_dir: Path = BASE_DIR / "submission") -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.submission_json = self.output_dir / "submission.json"

    def generate_submission(self, game_ids: List[str], max_steps: int = DEFAULT_MAX_STEPS) -> Path:
        """Run CompetitionCognitiveAgent across game_ids and format Kaggle payload."""
        submission_data: Dict[str, Any] = {}

        for game_id in game_ids:
            env = ARCEnvironment(game_id=game_id)
            agent = CompetitionCognitiveAgent(name=f"CompAgent_{game_id}")

            obs = env.reset()
            agent.on_episode_start()
            game_actions = []

            for step in range(1, max_steps + 1):
                action = agent.act(obs)
                game_actions.append(action)
                next_obs, reward, done, info = env.step(action)
                obs = next_obs
                if done or info.get("status") in ["WIN", "GAME_OVER"]:
                    break

            agent.on_episode_end()
            submission_data[game_id] = {
                "actions": game_actions,
                "status": env.status,
                "total_steps": len(game_actions),
            }

        with open(self.submission_json, "w", encoding="utf-8") as f:
            json.dump(submission_data, f, indent=2)

        return self.submission_json
