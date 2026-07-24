"""Competition Configuration Manager controlling runtime modes and resource limits."""

from enum import Enum, auto
from dataclasses import dataclass


class ExecutionMode(Enum):
    DEV = auto()
    BENCHMARK = auto()
    COMPETITION = auto()


@dataclass
class CompetitionConfig:
    mode: ExecutionMode = ExecutionMode.COMPETITION
    max_planning_time_sec: float = 2.0
    memory_limit_mb: float = 4096.0
    cache_max_entries: int = 1000
    enable_parallel_eval: bool = True
    verbose_logging: bool = False
