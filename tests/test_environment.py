"""Unit tests for ARCEnvironment wrapper."""

import pytest
from environment.wrapper import ARCEnvironment


def test_environment_reset() -> None:
    env = ARCEnvironment(game_id="test_game", grid_size=(5, 5))
    obs = env.reset()

    assert obs["game_id"] == "test_game"
    assert obs["step"] == 0
    assert obs["grid_shape"] == [5, 5]
    assert len(obs["available_actions"]) > 0
    assert not obs["done"]


def test_environment_step() -> None:
    env = ARCEnvironment(game_id="test_game", grid_size=(5, 5))
    env.reset()
    obs, reward, done, info = env.step(action=0)

    assert obs["step"] == 1
    assert isinstance(reward, float)
    assert isinstance(done, bool)
    assert info["game_id"] == "test_game"
