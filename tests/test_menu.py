"""Тесты для меню"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
from src.menu import Menu


class TestMenu:
    """Тесты меню"""

    def test_menu_initialization(self):
        """Тест инициализации меню"""
        menu = Menu()
        assert menu.state["active"] is True
        assert len(menu.state["buttons"]) == 3
        assert "new_game" in menu.state["buttons"]
        assert "settings" in menu.state["buttons"]
        assert "exit" in menu.state["buttons"]

    def test_handle_click(self):
        """Тест обработки клика"""
        menu = Menu()

        pos = menu.state["buttons"]["new_game"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 220, 50)
        click_pos = (rect.centerx, rect.centery)

        result = menu.handle_click(click_pos)
        assert result == "new_game"

    def test_handle_click_invalid(self):
        """Тест клика вне кнопок"""
        menu = Menu()
        result = menu.handle_click((0, 0))
        assert result == ""

    def test_update_hover(self):
        """Тест обновления наведения"""
        menu = Menu()
        pos = menu.state["buttons"]["new_game"]["pos"]
        rect = pygame.Rect(pos[0], pos[1], 220, 50)
        hover_pos = (rect.centerx, rect.centery)

        menu.update_hover(hover_pos)
        assert menu.state["buttons"]["new_game"]["hover"] is True

    def test_show_hide(self):
        """Тест показа/скрытия меню"""
        menu = Menu()
        menu.hide()
        assert menu.state["active"] is False

        menu.show()
        assert menu.state["active"] is True