import pytest
from memory import CognitiveMemory
from perception.scene_graph import SceneGraph
from perception.object_parser import Object

def test_working_memory():
    mem = CognitiveMemory()
    mem.working.add_thought("Need key")
    mem.working.add_thought("Door is locked")
    
    thoughts = mem.working.get_thoughts()
    assert len(thoughts) == 2
    thought_texts = [t.text for t in thoughts]
    assert "Need key" in thought_texts
    
    # Test capacity eviction with explicit priorities
    for i in range(15):
        mem.working.add_thought(f"Thought {i}", priority=i)
        
    thoughts = mem.working.get_thoughts()
    assert len(thoughts) == 10
    thought_texts = [t.text for t in thoughts]
    # Highest priority thoughts (priorities 5-14) should survive
    assert "Thought 14" in thought_texts
    # Lowest priority thoughts (priorities 0-4) should be evicted
    assert "Need key" not in thought_texts

def test_semantic_memory():
    mem = CognitiveMemory()
    mem.semantic.add_concept("Door", {"requires": "Key"})
    mem.semantic.add_concept("Key", {"opens": "Door"})
    
    door_concept = mem.semantic.get_concept("Door")
    assert door_concept["requires"] == "Key"
    
def test_procedural_memory():
    mem = CognitiveMemory()
    mem.procedural.add_strategy(
        situation={"has_key": True},
        strategy=["ACTION1", "ACTION2"],
        outcome="Success"
    )
    mem.procedural.add_strategy(
        situation={"has_key": False},
        strategy=["ACTION3"],
        outcome="Failed"
    )
    
    successful = mem.procedural.get_successful_strategies()
    assert len(successful) == 1
    assert successful[0].strategy == ["ACTION1", "ACTION2"]
    
    failed = mem.procedural.get_failed_strategies()
    assert len(failed) == 1
    assert failed[0].strategy == ["ACTION3"]

def test_knowledge_base():
    mem = CognitiveMemory()
    
    # Create mock SceneGraph
    obj1 = Object(id="Object_001", color=1, pixels=[], centroid=(0,0), bbox=(0,0,1,1), area=4, perimeter=4, shape="square")
    obj2 = Object(id="Object_002", color=2, pixels=[], centroid=(2,2), bbox=(2,2,3,3), area=4, perimeter=4, shape="square")
    sg = SceneGraph([obj1, obj2], [("Object_001", "Left Of", "Object_002")])
    
    mem.knowledge_base.update_from_scene_graph(sg)
    
    facts1 = mem.knowledge_base.get_object_facts("Object_001")
    assert facts1["color"] == 1
    assert "Object_002" in facts1["Left Of"]
    
    # Test Query
    blue_objects = mem.knowledge_base.query("color", 1)
    assert "Object_001" in blue_objects
