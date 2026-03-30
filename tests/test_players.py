"""Тесты для игроков и стратегий"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.board import Board
from src.players import (
    HumanPlayer, AIPlayer, EasyStrategy,
    MediumStrategy, HardStrategy
)
from src.constants import Difficulty, HUMAN, AI_PLAYER, BOARD_SIZE


class TestPlayers:
    """Тесты для игроков"""

    def test_human_player(self):
        """Тест игрока-человека"""
        player = HumanPlayer()
        board = Board()
        assert player.get_move(board) is None

    def test_ai_player_creation(self):
        """Тест создания AI игрока"""
        ai = AIPlayer(AI_PLAYER, Difficulty.EASY)
        assert ai.symbol == AI_PLAYER
        assert ai.opponent == HUMAN
        assert isinstance(ai.strategy, EasyStrategy)

        ai = AIPlayer(AI_PLAYER, Difficulty.MEDIUM)
        assert isinstance(ai.strategy, MediumStrategy)

        ai = AIPlayer(AI_PLAYER, Difficulty.HARD)
        assert isinstance(ai.strategy, HardStrategy)


class TestEasyStrategy:
    """Тесты легкой стратегии"""

    def test_find_move(self):
        """Тест выбора хода"""
        strategy = EasyStrategy()
        board = Board()

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        assert isinstance(move, tuple)
        assert len(move) == 2
        assert 0 <= move[0] < BOARD_SIZE
        assert 0 <= move[1] < BOARD_SIZE

    def test_find_move_on_full_board(self):
        """Тест выбора хода на заполненной доске"""
        strategy = EasyStrategy()
        board = Board()

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                board.make_move(i, j, HUMAN)

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        assert move == (BOARD_SIZE // 2, BOARD_SIZE // 2)


class TestMediumStrategy:
    """Тесты средней стратегии"""

    def test_find_winning_move(self):
        """Тест поиска выигрышного хода"""
        strategy = MediumStrategy()
        board = Board()

        for col in range(7, 11):
            board.make_move(7, col, AI_PLAYER)

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        assert move == (7, 11) or move == (7, 6)

    def test_block_opponent_win(self):
        """Тест блокировки выигрыша противника"""
        strategy = MediumStrategy()
        board = Board()

        for col in range(7, 11):
            board.make_move(7, col, HUMAN)

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        assert move == (7, 11) or move == (7, 6)


class TestHardStrategy:
    """Тесты сложной стратегии"""

    def test_find_move(self):
        """Тест выбора хода"""
        strategy = HardStrategy()
        board = Board()

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        assert isinstance(move, tuple)
        assert len(move) == 2

    def test_opening_move(self):
        """Тест начального хода"""
        strategy = HardStrategy()
        board = Board()

        move = strategy.find_move(board, AI_PLAYER, HUMAN)
        center = BOARD_SIZE // 2
        assert abs(move[0] - center) <= 5
        assert abs(move[1] - center) <= 5

    def test_evaluate_position(self):
        """Тест оценки позиции"""
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)

        score = strategy._evaluate_position(board, 7, 8, AI_PLAYER, HUMAN)
        assert isinstance(score, int)

    def test_count_in_direction(self):
        """Тест подсчета в направлении"""
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)
        board.make_move(7, 8, AI_PLAYER)

        count, ends = strategy._count_in_direction(board, 7, 7, 0, 1, AI_PLAYER)
        assert count == 2

    def test_count_line_length(self):
        """Тест подсчета длины линии"""
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)
        board.make_move(7, 8, AI_PLAYER)
        board.make_move(7, 9, AI_PLAYER)

        length = strategy._count_line_length(board, 7, 7, 0, 1, AI_PLAYER)
        assert length == 3

    def test_score_line(self):
        """Тест оценки линии"""
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)
        board.make_move(7, 8, AI_PLAYER)
        board.make_move(7, 9, AI_PLAYER)
        board.make_move(7, 10, AI_PLAYER)

        score = strategy._score_line(board, 7, 7, AI_PLAYER, AI_PLAYER)
        assert score > 0

    def test_find_critical_threat(self):
        """Тест поиска критической угрозы"""
        strategy = HardStrategy()
        board = Board()
        for c in range(4):
            board.make_move(7, c, HUMAN)
        board.make_move(8, 0, AI_PLAYER)

        threat = strategy._find_critical_threat(board, HUMAN, 3, 1)
        assert isinstance(threat, tuple) or threat is None

    def test_find_near_move(self):
        """Тест поиска хода рядом с фигурами"""
        from src.players import AIStrategy
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)

        move = strategy._find_near_move(board)
        assert isinstance(move, tuple)
        assert 0 <= move[0] < BOARD_SIZE
        assert 0 <= move[1] < BOARD_SIZE

    def test_select_best_moves(self):
        """Тест выбора лучших ходов"""
        strategy = HardStrategy()
        board = Board()
        board.make_move(7, 7, AI_PLAYER)

        candidates = [(7, 8), (8, 7), (6, 7), (8, 8)]
        best = strategy._select_best_moves(candidates, board, AI_PLAYER, HUMAN)
        assert isinstance(best, list)
        assert len(best) > 0

    def test_get_opening_move(self):
        """Тест начального хода"""
        strategy = HardStrategy()
        board = Board()

        move = strategy._get_opening_move(board)
        assert isinstance(move, tuple)
        center = BOARD_SIZE // 2
        assert abs(move[0] - center) <= 5
        assert abs(move[1] - center) <= 5