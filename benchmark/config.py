"""Configuration defaults for ARC-AGI-3 Benchmarking Suite."""

from pathlib import Path
from typing import List

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results"
PLOTS_DIR = BASE_DIR / "plots"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_EPISODES = 5
DEFAULT_MAX_STEPS = 20
DEFAULT_HUMAN_BASELINE = 15

DEFAULT_GAMES: List[str] = [
    "sample_game",
    "public_game_01",
    "public_game_02",
]
