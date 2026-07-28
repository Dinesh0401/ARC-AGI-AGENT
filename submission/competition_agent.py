"""High-performance competition wrapper around CognitiveAgent."""

import time
import numpy as np
from typing import Dict, Any, Optional, List
from agents.cognitive_agent import CognitiveAgent
from optimization.competition_config import CompetitionConfig, ExecutionMode
from optimization.scene_hash import SceneHasher
from optimization.cache_manager import CacheManager
from optimization.memory_optimizer import MemoryOptimizer
from optimization.profiler import RuntimeProfiler
from perception.scene_graph import SceneGraph


class CompetitionCognitiveAgent(CognitiveAgent):
    """Kaggle competition wrapper integrating caching, profiling, and RAM optimization."""

    def __init__(self, name: str = "CompetitionCognitiveAgent", seed: int = 42) -> None:
        super().__init__(name=name, seed=seed)
        self.config = CompetitionConfig(mode=ExecutionMode.COMPETITION)
        self.hasher = SceneHasher()
        self.cache_manager = CacheManager(max_entries=self.config.cache_max_entries)
        self.memory_optimizer = MemoryOptimizer()
        self.profiler = RuntimeProfiler()

    def is_done(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> bool:
        return super().is_done(frames, latest_frame)

    def choose_action(self, frames: List[Dict[str, Any]], latest_frame: Dict[str, Any]) -> Any:
        """Optimized action loop with caching & latency profiling."""
        t0 = time.time()

        grid_data = latest_frame.get("frame", latest_frame.get("grid", []))
        grid = np.array(grid_data) if isinstance(grid_data, list) else grid_data
        grid_hash = self.hasher.hash_grid(grid)

        # 1. Perception with SceneGraph cache
        t_perc = time.time()
        cached_scene = self.cache_manager.get_scene(grid_hash)
        if cached_scene:
            current_scene = cached_scene
        else:
            objects = self.parser.parse_grid(grid)
            relations = self.relation_detector.detect_relations(objects)
            current_scene = SceneGraph(objects, relations)
            self.cache_manager.put_scene(grid_hash, current_scene)
        self.profiler.record_latency("perception", (time.time() - t_perc) * 1000.0)

        # 2. Memory optimization
        t_mem = time.time()
        self.memory_optimizer.prune_memory(self.memory)
        self.profiler.record_latency("memory", (time.time() - t_mem) * 1000.0)

        # 3. Superclass action execution
        action = super().choose_action(frames, latest_frame)

        total_ms = (time.time() - t0) * 1000.0
        self.profiler.record_latency("total_act", total_ms)
        return action
