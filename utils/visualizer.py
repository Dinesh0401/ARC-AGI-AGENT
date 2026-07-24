"""ARC-AGI-3 Grid Visualizer and Color Palette utility for 16 grid values (0-15)."""

from typing import List, Optional, Tuple
import numpy as np


class ARCColorPalette:
    """Standard 16-color ARC-AGI-3 palette definitions."""

    # RGB tuples normalized (0.0 to 1.0) for Matplotlib / PIL
    RGB_NORM = [
        (0.0, 0.0, 0.0),        # 0: Black
        (0.0, 0.455, 0.851),    # 1: Blue
        (1.0, 0.255, 0.212),    # 2: Red
        (0.18, 0.8, 0.25),      # 3: Green
        (1.0, 0.863, 0.0),      # 4: Yellow
        (0.667, 0.667, 0.667),  # 5: Gray
        (0.941, 0.071, 0.745),  # 6: Magenta
        (1.0, 0.522, 0.106),    # 7: Orange
        (0.498, 0.859, 1.0),    # 8: Teal
        (0.529, 0.055, 0.145),  # 9: Maroon
        (0.694, 0.051, 0.788),  # 10: Lavender
        (0.004, 1.0, 0.439),    # 11: Lime
        (0.0, 0.122, 0.247),    # 12: Navy
        (0.239, 0.6, 0.439),    # 13: Olive
        (1.0, 0.498, 0.314),    # 14: Coral
        (0.855, 0.647, 0.125),  # 15: Gold
    ]

    # Hex strings
    HEX = [
        "#000000", "#0074D9", "#FF4136", "#2ECC40", "#FFDC00",
        "#AAAAAA", "#F012BE", "#FF851B", "#7FDBFF", "#870E25",
        "#B10DC9", "#01FF70", "#001F3F", "#3D9970", "#FF7F50", "#DAA520"
    ]

    # ANSI background color codes for terminal rendering
    ANSI_BG = [
        "\033[48;5;0m  \033[0m",   # 0: Black
        "\033[48;5;21m  \033[0m",  # 1: Blue
        "\033[48;5;196m  \033[0m", # 2: Red
        "\033[48;5;46m  \033[0m",  # 3: Green
        "\033[48;5;226m  \033[0m", # 4: Yellow
        "\033[48;5;244m  \033[0m", # 5: Gray
        "\033[48;5;201m  \033[0m", # 6: Magenta
        "\033[48;5;208m  \033[0m", # 7: Orange
        "\033[48;5;51m  \033[0m",  # 8: Teal
        "\033[48;5;88m  \033[0m",  # 9: Maroon
        "\033[48;5;129m  \033[0m", # 10: Lavender
        "\033[48;5;118m  \033[0m", # 11: Lime
        "\033[48;5;17m  \033[0m",  # 12: Navy
        "\033[48;5;65m  \033[0m",  # 13: Olive
        "\033[48;5;209m  \033[0m", # 14: Coral
        "\033[48;5;178m  \033[0m", # 15: Gold
    ]


def render_ansi_grid(grid: List[List[int]]) -> str:
    """Render a 2D integer grid as a colorized ANSI terminal block string.

    Args:
        grid: 2D array of color integers (0-15).

    Returns:
        Formatted multi-line ANSI color string.
    """
    lines = []
    lines.append("┌" + "──" * len(grid[0]) + "┐")
    for row in grid:
        line_str = "│"
        for val in row:
            color_idx = val if 0 <= val <= 15 else 0
            line_str += ARCColorPalette.ANSI_BG[color_idx]
        line_str += "│"
        lines.append(line_str)
    lines.append("└" + "──" * len(grid[0]) + "┘")
    return "\n".join(lines)


def render_matplotlib_frame(
    grid: List[List[int]],
    title: str = "",
    figsize: Tuple[int, int] = (6, 6),
    show_grid_lines: bool = True,
):
    """Render 2D grid using Matplotlib.

    Args:
        grid: 2D array of color integers (0-15).
        title: Plot title string.
        figsize: Figure dimensions tuple.
        show_grid_lines: Whether to overlay cell border lines.

    Returns:
        Matplotlib figure and axes tuple (fig, ax).
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, BoundaryNorm

    grid_np = np.array(grid, dtype=int)
    cmap = ListedColormap(ARCColorPalette.RGB_NORM)
    norm = BoundaryNorm(range(17), cmap.N)

    fig, ax = plt.subplots(figsize=figsize)
    ax.imshow(grid_np, cmap=cmap, norm=norm)

    if show_grid_lines:
        h, w = grid_np.shape
        ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=1.5)
        ax.tick_params(which="minor", size=0)

    ax.set_xticks([])
    ax.set_yticks([])
    if title:
        ax.set_title(title, fontsize=12, fontweight="bold")
    plt.tight_layout()
    return fig, ax


def save_frame_image(grid: List[List[int]], output_path: str, scale: int = 20) -> None:
    """Export 2D grid directly as a PNG image using PIL.

    Args:
        grid: 2D array of color integers (0-15).
        output_path: Target PNG filepath.
        scale: Pixel magnification scaling factor per grid cell.
    """
    from PIL import Image

    grid_np = np.array(grid, dtype=int)
    h, w = grid_np.shape
    img_data = np.zeros((h, w, 3), dtype=np.uint8)

    for i in range(h):
        for j in range(w):
            color_idx = grid_np[i, j] if 0 <= grid_np[i, j] <= 15 else 0
            rgb_float = ARCColorPalette.RGB_NORM[color_idx]
            img_data[i, j] = [int(c * 255) for c in rgb_float]

    img = Image.fromarray(img_data, mode="RGB")
    if scale > 1:
        img = img.resize((w * scale, h * scale), resample=Image.NEAREST)
    img.save(output_path)
