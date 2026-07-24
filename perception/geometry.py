from typing import List, Tuple
import numpy as np

def calculate_bbox(pixels: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    """Calculate the bounding box of a set of pixels.
    Returns (min_r, min_c, max_r, max_c)
    """
    if not pixels:
        return (0, 0, 0, 0)
    min_r = min(p[0] for p in pixels)
    min_c = min(p[1] for p in pixels)
    max_r = max(p[0] for p in pixels)
    max_c = max(p[1] for p in pixels)
    return (min_r, min_c, max_r, max_c)

def calculate_centroid(pixels: List[Tuple[int, int]]) -> Tuple[float, float]:
    """Calculate the centroid of a set of pixels."""
    if not pixels:
        return (0.0, 0.0)
    r_sum = sum(p[0] for p in pixels)
    c_sum = sum(p[1] for p in pixels)
    return (r_sum / len(pixels), c_sum / len(pixels))

def calculate_perimeter(pixels: List[Tuple[int, int]]) -> int:
    """Calculate the perimeter of the component.
    A simple approach: count pixels that have at least one 4-way neighbor missing from the set.
    """
    pixel_set = set(pixels)
    perimeter = 0
    for r, c in pixels:
        neighbors = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        if not all(n in pixel_set for n in neighbors):
            perimeter += 1
    return perimeter
