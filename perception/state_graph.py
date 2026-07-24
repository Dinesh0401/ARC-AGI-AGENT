import numpy as np
from typing import List, Dict, Tuple, Any

from .object_parser import Object
from .connected_components import find_connected_components
from .geometry import calculate_bbox, calculate_centroid, calculate_perimeter
from .feature_extractor import determine_shape
from .relation_detector import detect_relations

class StateGraph:
    """Graph representation of the grid state."""
    
    def __init__(self, objects: List[Object], relations: List[Tuple[int, str, Any]]):
        self.objects = {obj.id: obj for obj in objects}
        
        # adjacency list format: { obj_id: [(relation_type, target), ...] }
        self.edges: Dict[int, List[Tuple[str, Any]]] = {obj.id: [] for obj in objects}
        
        for source_id, rel_type, target in relations:
            self.edges[source_id].append((rel_type, target))
            
    def get_object(self, obj_id: int) -> Object:
        return self.objects[obj_id]
        
    def get_relations(self, obj_id: int) -> List[Tuple[str, Any]]:
        return self.edges[obj_id]

def parse_grid_to_graph(grid: np.ndarray, bg_color: int = 0) -> StateGraph:
    """Parse a grid into a StateGraph."""
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
            id=i + 1,
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
    return StateGraph(objects, relations)
