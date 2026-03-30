"""Тесты для рендерера"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
from src.renderer import Renderer
from src.constants import VisualStyle, Difficulty, HUMAN, AI_PLAYER


class TestRenderer:
    """Тесты рендерера"""

    def test_renderer_initialization(self):
        """Тест инициализации рендерера"""
        pygame.init()
        renderer = Renderer()
        assert renderer.screen is not None
        assert renderer.font_status is not None
        assert renderer.font_btn is not None
        renderer.close()

    def test_set_style(self):
        """Тест смены стиля"""
        pygame.init()
        renderer = Renderer()
        initial_style = renderer.current_style

        renderer.set_style(VisualStyle.MODERN)
        assert renderer.current_style != initial_style
        renderer.close()

    def test_update(self):
        """Тест обновления экрана"""
        pygame.init()
        renderer = Renderer()
        renderer.update()
        renderer.close()

    def test_close(self):
        """Тест закрытия"""
        pygame.init()
        renderer = Renderer()
        renderer.close()
        assert pygame.get_init() is False

    def test_draw_board_empty(self):
        """Тест отрисовки пустой доски"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        renderer.draw_board(board, None)
        renderer.update()
        renderer.close()

    def test_draw_board_with_pieces(self):
        """Тест отрисовки доски с фигурами"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        board.make_move(7, 7, HUMAN)
        board.make_move(7, 8, AI_PLAYER)
        renderer.draw_board(board, None)
        renderer.update()
        renderer.close()

    def test_draw_board_with_last_move(self):
        """Тест отрисовки доски с последним ходом"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        board.make_move(5, 5, HUMAN)
        renderer.draw_board(board, None)
        assert board.last_move is not None
        renderer.update()
        renderer.close()

    def test_draw_board_with_win_line(self):
        """Тест отрисовки доски с выигрышной линией"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        for c in range(5):
            board.make_move(0, c, HUMAN)
        board.check_win(HUMAN)
        assert board.win_line is not None
        renderer.draw_board(board, None)
        renderer.update()
        renderer.close()

    def test_draw_board_with_hover(self):
        """Тест отрисовки доски с наведением курсора"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        renderer.draw_board(board, (5, 5))
        renderer.update()
        renderer.close()

    def test_draw_board_hover_on_occupied(self):
        """Тест отрисовки наведения на занятую клетку"""
        pygame.init()
        renderer = Renderer()
        from src.board import Board
        board = Board()
        board.make_move(3, 3, HUMAN)
        renderer.draw_board(board, (3, 3))
        renderer.update()
        renderer.close()

    def test_draw_menu(self):
        """Тест отрисовки меню"""
        pygame.init()
        renderer = Renderer()
        from src.menu import Menu
        menu = Menu()
        menu.show()
        renderer.draw_menu(menu.state)
        renderer.update()
        renderer.close()

    def test_draw_settings(self):
        """Тест отрисовки настроек"""
        pygame.init()
        renderer = Renderer()
        from src.settings import Settings
        settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)
        settings.show()
        renderer.draw_settings(settings.state)
        renderer.update()
        renderer.close()

    def test_draw_ui(self):
        """Тест отрисовки UI"""
        pygame.init()
        renderer = Renderer()
        renderer.draw_ui("Тест статус", Difficulty.MEDIUM, (0, 0), False)
        renderer.update()
        renderer.close()

    def test_draw_ui_game_over(self):
        """Тест отрисовки UI в состоянии игра завершена"""
        pygame.init()
        renderer = Renderer()
        renderer.draw_ui("Вы победили!", Difficulty.MEDIUM, (0, 0), True)
        renderer.update()
        renderer.close()