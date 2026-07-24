"""Unit tests for visualizer and replay utilities."""

from pathlib import Path
import tempfile
import pytest
from utils.visualizer import ARCColorPalette, render_ansi_grid, save_frame_image
from utils.replay import ReplayLogger, ReplayViewer


def test_color_palette_lengths_16() -> None:
    assert len(ARCColorPalette.RGB_NORM) == 16
    assert len(ARCColorPalette.HEX) == 16
    assert len(ARCColorPalette.ANSI_BG) == 16


def test_render_ansi_grid_16_colors() -> None:
    grid = [[0, 5, 10, 15], [1, 6, 11, 14]]
    ansi_str = render_ansi_grid(grid)
    assert isinstance(ansi_str, str)
    assert "┌" in ansi_str
    assert "└" in ansi_str


def test_save_frame_image_16_colors() -> None:
    grid = [[0, 1, 10], [12, 14, 15]]
    with tempfile.TemporaryDirectory() as tmpdir:
        img_path = Path(tmpdir) / "frame.png"
        save_frame_image(grid, str(img_path))
        assert img_path.exists()
        assert img_path.stat().st_size > 0


def test_enriched_replay_logger_and_viewer() -> None:
    logger = ReplayLogger(game_id="test_game")
    grid = [[0, 1], [15, 0]]
    logger.log_step(
        step=1,
        frame=grid,
        action="ACTION1",
        reward=0.0,
        status="NOT_FINISHED",
        diff_cells=2,
        available_actions=["ACTION1", "ACTION2"],
    )
    logger.log_step(
        step=2,
        frame=grid,
        action="ACTION2",
        reward=1.0,
        status="WIN",
        diff_cells=0,
        available_actions=["ACTION1", "ACTION2"],
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        replay_path = Path(tmpdir) / "replay.json"
        logger.save(replay_path)
        assert replay_path.exists()

        viewer = ReplayViewer(replay_path)
        assert viewer.game_id == "test_game"
        assert len(viewer.trajectory) == 2
        assert viewer.data["final_status"] == "WIN"
