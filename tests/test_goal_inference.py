import pytest

from perception.scene_graph import SceneGraph
from perception.object_parser import Object
from memory.working import WorkingMemory
from memory.belief_memory import BeliefMemory
from reasoning.goal_generator import GoalGenerator

def create_dummy_scene() -> SceneGraph:
    obj1 = Object(
        id="Object_001", color=1, pixels=[(0, 0)],
        centroid=(0.0, 0.0), bbox=(0, 0, 1, 1),
        area=1, perimeter=4, shape="square"
    )
    obj2 = Object(
        id="Object_002", color=2, pixels=[(1, 1)],
        centroid=(1.0, 1.0), bbox=(1, 1, 2, 2),
        area=1, perimeter=4, shape="square"
    )
    obj2.visited = True # Mark obj2 as already thoroughly explored
    return SceneGraph([obj1, obj2], [])

def test_goal_generator_intrinsic_motivation():
    working = WorkingMemory()
    belief = BeliefMemory()
    generator = GoalGenerator(working, belief)
    
    scene = create_dummy_scene()
    goals = generator.generate_goals(scene)
    
    # It should generate Interact and StateChange goals for Object_001 (not visited)
    # but NOT for Object_002 (visited).
    assert any(g.target_conditions.get("target_obj") == "Object_001" for g in goals)
    assert not any(g.target_conditions.get("target_obj") == "Object_002" for g in goals)
    assert len(goals) == 2 # Interact and StateChange for obj1
