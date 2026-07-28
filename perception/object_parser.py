from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import numpy as np
from .connected_components import find_connected_components
from .geometry import calculate_bbox, calculate_centroid, calculate_perimeter
from .feature_extractor import determine_shape

@dataclass
class Object:
    """Represents a symbolic object extracted from the ARC grid."""
    id: str  # e.g., "Object_001"
    color: int
    pixels: List[Tuple[int, int]]  # List of (row, col) coordinates
    centroid: Tuple[float, float]
    bbox: Tuple[int, int, int, int]  # (min_r, min_c, max_r, max_c)
    area: int
    perimeter: int
    shape: str
    
    # Advanced features
    holes: int = 0
    orientation: float = 0.0
    symmetry: float = 0.0
    convexity: float = 0.0
    movable: Optional[bool] = None
    visited: bool = False
    
    features: dict = field(default_factory=dict)

class ObjectParser:
    """Parses a 2D grid into a list of Object representations."""
    
    def parse_grid(self, grid: np.ndarray, bg_color: int = 0) -> List[Object]:
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
            
        return objects
