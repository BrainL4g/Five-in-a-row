"""Тесты для настроек"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
from src.settings import Settings
from src.constants import Difficulty, VisualStyle


class TestSettings:
    """Тесты настроек"""

    def test_settings_initialization(self):
        """Тест инициализации настроек"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)
        assert settings.selected_difficulty == Difficulty.MEDIUM
        assert settings.selected_style == VisualStyle.CLASSIC
        assert settings.state["active"] is False

        assert settings.state["difficulty"]["medium"]["active"] is True
        assert settings.state["visual"]["classic"]["active"] is True

    def test_handle_click_difficulty(self):
        """Тест клика по сложности"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)

        pos = settings.state["difficulty"]["easy"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 180, 42)
        click_pos = (rect.centerx, rect.centery)

        result, _ = settings.handle_click(click_pos)
        assert result == "setting_changed"
        assert settings.selected_difficulty == Difficulty.EASY

    def test_handle_click_visual(self):
        """Тест клика по стилю"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)

        pos = settings.state["visual"]["modern"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 180, 42)
        click_pos = (rect.centerx, rect.centery)

        result, _ = settings.handle_click(click_pos)
        assert result == "setting_changed"
        assert settings.selected_style == VisualStyle.MODERN

    def test_handle_click_back(self):
        """Тест клика по кнопке назад"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)

        pos = settings.state["back_button"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 120, 40)
        click_pos = (rect.centerx, rect.centery)

        result, _ = settings.handle_click(click_pos)
        assert result == "back"

    def test_update_hover(self):
        """Тест обновления наведения"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)

        pos = settings.state["difficulty"]["easy"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 180, 42)
        hover_pos = (rect.centerx, rect.centery)

        settings.update_hover(hover_pos)
        assert settings.state["difficulty"]["easy"]["hover"] is True

    def test_show_hide(self):
        """Тест показа/скрытия настроек"""
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)

        settings.show()
        assert settings.state["active"] is True

        settings.hide()
        settings.hide()
        assert settings.state["active"] is False

    def test_get_difficulty_style(self):
        """Тест получения сложности и стиля"""
        settings = Settings(Difficulty.HARD, VisualStyle.MODERN)

        assert settings.get_difficulty() == Difficulty.HARD
        assert settings.get_style() == VisualStyle.MODERN