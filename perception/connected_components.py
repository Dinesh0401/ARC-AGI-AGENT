import numpy as np
from typing import List, Tuple

def find_connected_components(grid: np.ndarray, bg_color: int = 0, connectivity: int = 8) -> List[List[Tuple[int, int]]]:
    """Find connected components in the grid.
    
    Args:
        grid: 2D numpy array.
        bg_color: Color to ignore (typically 0).
        connectivity: 4 for orthogonal only, 8 for orthogonal + diagonal.
        
    Returns:
        A list of components, where each component is a list of (row, col) coordinates.
    """
    rows, cols = grid.shape
    visited = np.zeros_like(grid, dtype=bool)
    components = []
    
    if connectivity == 4:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        
    for r in range(rows):
        for c in range(cols):
            if not visited[r, c] and grid[r, c] != bg_color:
                color = grid[r, c]
                component = []
                queue = [(r, c)]
                visited[r, c] = True
                
                while queue:
                    curr_r, curr_c = queue.pop(0)
                    component.append((curr_r, curr_c))
                    
                    for dr, dc in directions:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if not visited[nr, nc] and grid[nr, nc] == color:
                                visited[nr, nc] = True
                                queue.append((nr, nc))
                
                if component:
                    components.append(component)
                    
    return components
