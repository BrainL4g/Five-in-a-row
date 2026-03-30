"""Тесты для класса Board"""
import pytest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.board import Board
from src.constants import BOARD_SIZE, EMPTY, HUMAN, AI_PLAYER


class TestBoard:
    """Тесты для доски"""

    def test_initial_board(self):
        """Тест создания пустой доски"""
        board = Board()
        assert board.grid.shape == (BOARD_SIZE, BOARD_SIZE)
        assert np.all(board.grid == EMPTY)
        assert board.last_move is None
        assert board.win_line is None
        assert board.move_history == []

    def test_make_move_valid(self):
        """Тест корректного хода"""
        board = Board()
        result = board.make_move(7, 7, HUMAN)
        assert result is True
        assert board.grid[7, 7] == HUMAN
        assert board.last_move == (7, 7, HUMAN)
        assert len(board.move_history) == 1

    def test_make_move_invalid_out_of_bounds(self):
        """Тест хода за пределы доски"""
        board = Board()
        result = board.make_move(-1, 0, HUMAN)
        assert result is False
        result = board.make_move(BOARD_SIZE, 0, HUMAN)
        assert result is False

    def test_make_move_on_occupied_cell(self):
        """Тест хода на занятую клетку"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        result = board.make_move(7, 7, AI_PLAYER)
        assert result is False
        assert board.grid[7, 7] == HUMAN

    def test_undo_last_move(self):
        """Тест отмены последнего хода"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        board.make_move(7, 8, AI_PLAYER)

        undone = board.undo_last_move()
        assert undone == (7, 8)
        assert board.grid[7, 8] == EMPTY
        assert board.last_move == (7, 7, HUMAN)
        assert len(board.move_history) == 1

    def test_undo_moves(self):
        """Тест отмены нескольких ходов"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        board.make_move(7, 8, AI_PLAYER)
        board.make_move(8, 8, HUMAN)

        undone = board.undo_moves(2)
        assert len(undone) == 2
        assert board.grid[7, 8] == EMPTY
        assert board.grid[8, 8] == EMPTY
        assert board.grid[7, 7] == HUMAN
        assert len(board.move_history) == 1

    def test_is_full(self):
        """Тест проверки заполненности доски"""
        board = Board()
        assert board.is_full() == False

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                board.make_move(i, j, HUMAN)
        assert board.is_full() == True

    def test_get_empty_cells(self):
        """Тест получения пустых клеток"""
        board = Board()
        empty_cells = board.get_empty_cells()
        assert len(empty_cells) == BOARD_SIZE * BOARD_SIZE

        board.make_move(0, 0, HUMAN)
        empty_cells = board.get_empty_cells()
        assert len(empty_cells) == BOARD_SIZE * BOARD_SIZE - 1
        assert (0, 0) not in empty_cells

    def test_get_near_empty_cells(self):
        """Тест получения клеток рядом с занятыми"""
        board = Board()
        board.make_move(7, 7, HUMAN)

        near_cells = board.get_near_empty_cells()
        expected_count = 0
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                if dr == 0 and dc == 0:
                    continue
                r, c = 7 + dr, 7 + dc
                if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                    expected_count += 1

        assert len(near_cells) == expected_count

    def test_get_hash(self):
        """Тест получения хэша доски"""
        board1 = Board()
        board2 = Board()

        assert board1.get_hash() == board2.get_hash()

        board1.make_move(7, 7, HUMAN)
        assert board1.get_hash() != board2.get_hash()

    def test_win_horizontal(self):
        """Тест победы по горизонтали"""
        board = Board()
        for col in range(7, 12):
            board.make_move(7, col, HUMAN)

        assert board.check_win(HUMAN) is True
        assert board.win_line is not None

    def test_win_vertical(self):
        """Тест победы по вертикали"""
        board = Board()
        for row in range(7, 12):
            board.make_move(row, 7, HUMAN)

        assert board.check_win(HUMAN) is True

    def test_win_diagonal(self):
        """Тест победы по диагонали"""
        board = Board()
        for i in range(5):
            board.make_move(7 + i, 7 + i, HUMAN)

        assert board.check_win(HUMAN) is True

    def test_no_win(self):
        """Тест отсутствия победы"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        board.make_move(7, 8, HUMAN)
        board.make_move(7, 9, HUMAN)
        board.make_move(7, 10, HUMAN)

        assert board.check_win(HUMAN) is False

    def test_undo_specific_move(self):
        """Тест отмены конкретного хода"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        board.make_move(7, 8, AI_PLAYER)
        board.make_move(8, 8, HUMAN)

        board.undo_move(7, 8)
        assert board.grid[7, 8] == EMPTY
        assert len(board.move_history) == 2

    def test_cache_clearing(self):
        """Тест очистки кэша"""
        board = Board()
        board.make_move(7, 7, HUMAN)
        near_cells1 = board.get_near_empty_cells()

        board.make_move(7, 8, HUMAN)
        near_cells2 = board.get_near_empty_cells()

        assert near_cells1 != near_cells2