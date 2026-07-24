import pytest
import numpy as np
from pathlib import Path
from optimization import (
    CompetitionConfig,
    ExecutionMode,
    SceneHasher,
    CacheManager,
    MemoryOptimizer,
    RuntimeProfiler,
)
from submission import CompetitionCognitiveAgent, KaggleSubmissionRunner
from memory import CognitiveMemory


def test_scene_hasher():
    arr1 = np.zeros((10, 10), dtype=int)
    arr2 = np.zeros((10, 10), dtype=int)
    arr3 = np.ones((10, 10), dtype=int)

    h1 = SceneHasher.hash_grid(arr1)
    h2 = SceneHasher.hash_grid(arr2)
    h3 = SceneHasher.hash_grid(arr3)

    assert h1 == h2
    assert h1 != h3


def test_cache_manager():
    cache = CacheManager(max_entries=2)
    cache.put_scene("h1", "scene1")
    cache.put_scene("h2", "scene2")

    assert cache.get_scene("h1") == "scene1"
    assert cache.get_scene("h2") == "scene2"

    cache.put_scene("h3", "scene3")
    # h1 was accessed recently, h2 should be evicted or LRU managed
    assert len(cache.scene_cache) == 2


def test_memory_optimizer():
    opt = MemoryOptimizer()
    mem = CognitiveMemory()

    # Add high & low confidence beliefs
    b1 = mem.belief_memory.add_belief("high conf", confidence=0.8)
    b2 = mem.belief_memory.add_belief("low conf", confidence=0.05)

    opt.prune_memory(mem)

    assert mem.belief_memory.get_belief(b1) is not None
    assert mem.belief_memory.get_belief(b2) is None


def test_competition_agent_and_kaggle_runner(tmp_path):
    runner = KaggleSubmissionRunner(output_dir=tmp_path)
    json_path = runner.generate_submission(game_ids=["sample_game"], max_steps=2)

    assert json_path.exists()
    assert (tmp_path / "submission.json").exists()
