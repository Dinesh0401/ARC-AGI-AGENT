from dataclasses import dataclass, field
from typing import List, Tuple, Optional

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
