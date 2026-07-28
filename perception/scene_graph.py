import numpy as np
from typing import List, Dict, Tuple, Any

from .object_parser import Object
from .connected_components import find_connected_components
from .geometry import calculate_bbox, calculate_centroid, calculate_perimeter
from .feature_extractor import determine_shape
from .relation_detector import detect_relations

class SceneGraph:
    """Scene Graph representation of the grid environment."""
    
    def __init__(self, objects: List[Object], relations: List[Tuple[str, str, Any]]):
        self.objects = {obj.id: obj for obj in objects}
        
        # adjacency list format: { obj_id: [(relation_type, target), ...] }
        self.edges: Dict[str, List[Tuple[str, Any]]] = {obj.id: [] for obj in objects}
        
        for source_id, rel_type, target in relations:
            self.edges[source_id].append((rel_type, target))
            
    def get_object(self, obj_id: str) -> Object:
        return self.objects[obj_id]
        
    def get_relations(self, obj_id: str) -> List[Tuple[str, Any]]:
        return self.edges[obj_id]

    @property
    def relations(self) -> List[Tuple[str, str, Any]]:
        """Return all relations as a flat list of (source_id, relation_type, target) tuples."""
        all_rels = []
        for obj_id, rels in self.edges.items():
            for rel_type, target in rels:
                all_rels.append((obj_id, rel_type, target))
        return all_rels

def parse_grid_to_graph(grid: np.ndarray, bg_color: int = 0) -> SceneGraph:
    """Parse a grid into a SceneGraph."""
    components = find_connected_components(grid, bg_color=bg_color, connectivity=8)
    
    objects = []
    for i, comp_pixels in enumerate(components):
        if not comp_pixels:
            continue
            
        color = int(grid[comp_pixels[0][0], comp_pixels[0][1]])
        bbox = calculate_bbox(comp_pixels)
        centroid = calculate_centroid(comp_pixels)
        area = len(comp_pixels)
        perimeter = calculate_perimeter(comp_pixels)
        shape = determine_shape(comp_pixels, bbox)
        
        obj = Object(
            id=f"Object_{i+1:03d}",
            color=color,
            pixels=comp_pixels,
            centroid=centroid,
            bbox=bbox,
            area=area,
            perimeter=perimeter,
            shape=shape
        )
        objects.append(obj)
        
    relations = detect_relations(objects)
    return SceneGraph(objects, relations)
