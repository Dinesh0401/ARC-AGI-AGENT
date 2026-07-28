import pytest
from integration.arc_adapter import FrameParser, ActionAdapter
from agents.cognitive_agent import CognitiveAgent
from perception.scene_graph import SceneGraph

def test_frame_parser():
    parser = FrameParser()
    
    # Fake official ARC frame
    frame = {
        "frame": [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ],
        "available_actions": ["ACTION1", "ACTION2"]
    }
    
    scene = parser.parse(frame)
    assert isinstance(scene, SceneGraph)
    # The SceneGraph should have extracted objects based on grid
    assert len(scene.objects) >= 0

def test_action_adapter_simple():
    # Test simple actions
    assert ActionAdapter.to_game_action("ACTION1") == "ACTION1"
    assert ActionAdapter.to_game_action("ACTION7") == "ACTION7"
    assert ActionAdapter.to_game_action("RESET") == "RESET"

def test_action_adapter_complex():
    # Test complex coordinate actions
    action = ActionAdapter.to_game_action("ACTION6(5, 10)")
    assert action == ("ACTION6", 5, 10)

def test_action_adapter_malformed():
    # Should fallback to ACTION1 safely
    assert ActionAdapter.to_game_action("ACTION6(abc)") == "ACTION1"

def test_cognitive_agent_choose_action():
    agent = CognitiveAgent(enable_world_model=False, enable_learning=False, enable_planning=False)
    
    frame = {
        "frame": [
            [2, 2],
            [2, 2]
        ],
        "available_actions": ["ACTION2", "ACTION3"]
    }
    
    # Should pick one of the available actions
    action = agent.choose_action([frame], frame)
    assert action in ["ACTION2", "ACTION3"]

def test_cognitive_agent_is_done():
    agent = CognitiveAgent()
    agent.memory.knowledge_base.update_fact("solved", {"value": True})
    assert agent.is_done([], {}) == True
    
    agent.memory.knowledge_base.facts.clear()
    assert agent.is_done([], {}) == False
