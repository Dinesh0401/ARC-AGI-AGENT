"""Replay logger and trajectory viewer utility for ARC-AGI-3 (Enriched Format)."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from utils.logger import get_logger
from utils.visualizer import render_ansi_grid

logger = get_logger("replay")


class ReplayLogger:
    """Logs rich episode trajectories (frames, actions, rewards, statuses, diffs) to JSON files."""

    def __init__(self, game_id: str) -> None:
        self.game_id = game_id
        self.frames: List[Dict[str, Any]] = []

    def log_step(
        self,
        step: int,
        frame: List[List[int]],
        action: Any,
        reward: float,
        status: str,
        diff_cells: int,
        available_actions: List[Any],
        info: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append step data to trajectory log buffer in standard ARC research schema."""
        step_payload = {
            "step": step,
            "timestamp": time.time(),
            "frame": frame,
            "action": action,
            "reward": reward,
            "status": status,
            "diff_cells": diff_cells,
            "available_actions": available_actions,
            "info": info or {},
        }
        self.frames.append(step_payload)

    def save(self, filepath: Path) -> None:
        """Save trajectory buffer to a JSON replay file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        replay_data = {
            "game_id": self.game_id,
            "total_steps": len(self.frames),
            "final_status": self.frames[-1]["status"] if self.frames else "UNKNOWN",
            "trajectory": self.frames,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(replay_data, f, indent=2)
        logger.info(f"Saved replay trajectory with {len(self.frames)} steps to '{filepath}'")


class ReplayViewer:
    """Loads and renders saved JSON replay trajectories."""

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        with open(filepath, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.game_id = self.data.get("game_id", "unknown")
        self.trajectory = self.data.get("trajectory", [])

    def display_terminal_replay(self, max_frames: Optional[int] = None) -> None:
        """Print step-by-step ANSI terminal animation of the loaded trajectory."""
        print(f"\n================ REPLAY VIEWER: {self.game_id} ================")
        print(f"Total Trajectory Steps: {len(self.trajectory)} | Final Status: {self.data.get('final_status')}\n")

        frames_to_show = self.trajectory[:max_frames] if max_frames else self.trajectory
        for frame_item in frames_to_show:
            step = frame_item["step"]
            action = frame_item["action"]
            reward = frame_item["reward"]
            status = frame_item.get("status", "NOT_FINISHED")
            diff_cells = frame_item.get("diff_cells", 0)
            frame_grid = frame_item.get("frame", frame_item.get("grid", []))

            print(
                f"--- STEP {step} | Action: {action} | Diff: {diff_cells} cells | Status: {status} | Reward: {reward} ---"
            )
            print(render_ansi_grid(frame_grid))
            print()
