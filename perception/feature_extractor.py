from typing import List, Tuple
from .geometry import calculate_bbox

def determine_shape(pixels: List[Tuple[int, int]], bbox: Tuple[int, int, int, int]) -> str:
    """Determine a simple shape string from pixels and bbox."""
    if not pixels:
        return "empty"
        
    min_r, min_c, max_r, max_c = bbox
    height = max_r - min_r + 1
    width = max_c - min_c + 1
    area = len(pixels)
    bbox_area = width * height

    # Check line shapes first (before filled rectangle check)
    if height == 1 and width > 1:
        return "horizontal_line"
    if width == 1 and height > 1:
        return "vertical_line"
    
    if area == bbox_area:
        if width == height:
            if area == 1:
                return "pixel"
            return "square"
        return "rectangle"
    
    # L-shape heuristic: full area minus width*height should be width*height - width - height + 1
    # Very rudimentary, just returning 'irregular' for now if not full bounding box
    return "irregular"
