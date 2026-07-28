import pytest
import numpy as np

from perception.scene_graph import SceneGraph
from perception.object_parser import Object
from memory.episodic import EpisodicMemory
from world_model import PredictionEngine
from learning.exploration import CuriosityExplorer

def create_dummy_scene(color: int = 1) -> SceneGraph:
    obj = Object(
        id="test_obj",
        color=color,
        pixels=[(0, 0)],
        centroid=(0.0, 0.0),
        bbox=(0, 0, 1, 1),
        area=1,
        perimeter=4,
        shape="square"
    )
    return SceneGraph([obj], [])

def test_exploration_ucb_favor_unvisited():
    memory = EpisodicMemory()
    engine = PredictionEngine()
    explorer = CuriosityExplorer(memory, engine)
    
    state = create_dummy_scene()
    # Mocking prediction engine so actions don't change state initially
    # If state doesn't change, we stay in unvisited state? No, action changes state conceptually.
    
    # Let's say action "ACTION1" leads to a state we've visited 10 times, 
    # and "ACTION2" leads to a state visited 0 times.
    state1 = create_dummy_scene(1)
    state2 = create_dummy_scene(2)
    
    for _ in range(10):
        memory.add_experience(create_dummy_scene(0), "ACTION1", 0, state1)
        
    class MockEngine:
        def evaluate_action(self, s, a):
            class MockPred:
                predicted_state = state1 if a == "ACTION1" else state2
            return MockPred()
            
    explorer.prediction_engine = MockEngine()
    
    valid_actions = ["ACTION1", "ACTION2"]
    
    # ACTION2 leads to state2 (0 visits), ACTION1 leads to state1 (10 visits)
    # ACTION2 should be chosen due to infinite UCB score
    chosen = explorer.choose_action(state, valid_actions, last_action=None)
    assert chosen == "ACTION2"

def test_exploration_loop_penalty():
    memory = EpisodicMemory()
    explorer = CuriosityExplorer(memory, PredictionEngine())
    
    state = create_dummy_scene()
    valid_actions = ["ACTION1", "ACTION2"]
    
    # If last action was ACTION1, ACTION2 (opposite) should be penalized heavily
    chosen = explorer.choose_action(state, valid_actions, last_action="ACTION1")
    assert chosen == "ACTION1" # ACTION1 gets higher score because ACTION2 is penalized
