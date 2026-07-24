import numpy as np
import pytest
from perception import parse_grid_to_graph, Object, SceneGraph

def test_parse_simple_grid():
    # 0 is background, 1 is blue square, 2 is red line
    grid = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 0, 2, 2],
        [0, 0, 0, 0, 0],
    ])
    
    graph = parse_grid_to_graph(grid, bg_color=0)
    
    # Assert objects
    assert len(graph.objects) == 2
    
    obj1 = graph.get_object("Object_001")
    obj2 = graph.get_object("Object_002")
    
    # Validate object 1 (blue square)
    assert obj1.color == 1
    assert obj1.area == 4
    assert obj1.shape == "square"
    assert obj1.bbox == (1, 1, 2, 2)
    assert obj1.centroid == (1.5, 1.5)
    
    # Validate object 2 (red line)
    assert obj2.color == 2
    assert obj2.area == 2
    assert obj2.shape == "horizontal_line"
    assert obj2.bbox == (3, 3, 3, 4)
    assert obj2.centroid == (3.0, 3.5)
    
    # Assert relations
    rels1 = graph.get_relations("Object_001")
    # obj1 is Left Of and Above obj2
    rel_types = [r[0] for r in rels1]
    assert "Left Of" in rel_types
    assert "Above" in rel_types
    
    rels2 = graph.get_relations("Object_002")
    rel_types2 = [r[0] for r in rels2]
    assert "Right Of" in rel_types2
    assert "Below" in rel_types2

def test_adjacency_and_inside():
    # 3 is a hollow box (3x3), 4 is a pixel inside
    grid = np.array([
        [3, 3, 3, 0, 0],
        [3, 4, 3, 0, 0],
        [3, 3, 3, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ])
    
    graph = parse_grid_to_graph(grid)
    
    obj_box = None
    obj_inner = None
    for obj in graph.objects.values():
        if obj.color == 3:
            obj_box = obj
        elif obj.color == 4:
            obj_inner = obj
            
    assert obj_box is not None
    assert obj_inner is not None
    
    assert obj_inner.shape == "pixel"
    assert obj_box.area == 8
    
    # Check Inside
    rels_inner = graph.get_relations(obj_inner.id)
    assert any(r[0] == "Inside" and r[1] == obj_box.id for r in rels_inner)
    
    # Check Adjacent / Touches
    assert any(r[0] == "Touches" and r[1] == obj_box.id for r in rels_inner)
