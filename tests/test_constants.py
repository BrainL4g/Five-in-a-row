"""Тесты для констант"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.constants import (
    BOARD_SIZE, CELL_SIZE, GRID_OFFSET_X, GRID_OFFSET_Y,
    UI_PANEL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    EMPTY, HUMAN, AI_PLAYER, FONT_SIZE_STATUS, FONT_SIZE_BTN,
    AI_THINKING_DELAY, Difficulty, VisualStyle, STYLES
)


class TestConstants:
    """Тесты констант"""

    def test_board_dimensions(self):
        """Тест размеров доски"""
        assert BOARD_SIZE == 15
        assert CELL_SIZE == 36
        assert GRID_OFFSET_X == 20
        assert GRID_OFFSET_Y == 20

    def test_window_dimensions(self):
        """Тест размеров окна"""
        expected_width = BOARD_SIZE * CELL_SIZE + GRID_OFFSET_X * 2
        expected_height = BOARD_SIZE * CELL_SIZE + GRID_OFFSET_Y + UI_PANEL_HEIGHT

        assert WINDOW_WIDTH == expected_width
        assert WINDOW_HEIGHT == expected_height

    def test_players(self):
        """Тест идентификаторов игроков"""
        assert EMPTY == 0
        assert HUMAN == 1
        assert AI_PLAYER == 2

    def test_difficulty_enum(self):
        """Тест перечисления сложности"""
        assert Difficulty.EASY == 1
        assert Difficulty.MEDIUM == 2
        assert Difficulty.HARD == 3

    def test_visual_style_enum(self):
        """Тест перечисления стилей"""
        assert VisualStyle.CLASSIC == 1
        assert VisualStyle.MODERN == 2

    def test_styles_dict(self):
        """Тест словаря стилей"""
        assert VisualStyle.CLASSIC in STYLES
        assert VisualStyle.MODERN in STYLES

        classic_style = STYLES[VisualStyle.CLASSIC]
        assert "COLOR_BG" in classic_style
        assert "COLOR_GRID" in classic_style
        assert "COLOR_HUMAN" in classic_style
        assert "COLOR_AI" in classic_style