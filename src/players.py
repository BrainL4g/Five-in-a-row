from __future__ import annotations
from abc import ABC, abstractmethod
import random
import time
from typing import Tuple, Optional, List
from src.constants import BOARD_SIZE, HUMAN, AI_PLAYER, EMPTY, Difficulty
from src.board import Board


class Player(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        pass


class HumanPlayer(Player):
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        return None


class AIStrategy(ABC):
    @abstractmethod
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        pass


class EasyStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (7, 7)


class MediumStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        return self._find_near_move(board)

    def _find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_empty_cells():
            if board.make_move(r, c, player):
                win = board.check_win(player)
                board.undo_move(r, c)
                if win:
                    return (r, c)
        return None

    def _find_near_move(self, board: Board) -> Tuple[int, int]:
        candidates = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                                    board.grid[nr, nc] == EMPTY):
                                candidates.add((nr, nc))
        if candidates:
            return random.choice(list(candidates))
        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (7, 7)


class HardStrategy(AIStrategy):
    def find_move(self, board: Board, symbol: int, opponent: int) -> Tuple[int, int]:
        best_move = None
        best_value = -float('inf')
        depth = 5

        candidates = self._get_ordered_candidates(board, symbol, opponent)

        for r, c in candidates:
            if board.make_move(r, c, symbol):
                value = -self._minimax(board, depth - 1, False, -float('inf'), float('inf'), opponent, symbol)
                board.undo_move(r, c)
                if value > best_value:
                    best_value = value
                    best_move = (r, c)
        return best_move if best_move else self._find_near_move(board)

    def _minimax(self, board: Board, depth: int, maximizing: bool, alpha: float, beta: float, player: int,
                 opponent: int) -> float:
        if board.check_win(player if not maximizing else opponent):
            return 1000000 if maximizing else -1000000
        if board.is_full() or depth == 0:
            return self._evaluate(board, player, opponent)

        if maximizing:
            max_eval = -float('inf')
            for r, c in self._get_ordered_candidates(board, player, opponent):
                if board.make_move(r, c, player):
                    eval = self._minimax(board, depth - 1, False, alpha, beta, player, opponent)
                    board.undo_move(r, c)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for r, c in self._get_ordered_candidates(board, opponent, player):
                if board.make_move(r, c, opponent):
                    eval = self._minimax(board, depth - 1, True, alpha, beta, player, opponent)
                    board.undo_move(r, c)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def _evaluate(self, board: Board, symbol: int, opponent: int) -> int:
        score = self._evaluate_player(board, symbol) - self._evaluate_player(board, opponent) * 1.1
        return score

    def _evaluate_player(self, board: Board, player: int) -> int:
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in directions:
                        count, open_ends = self._count_consecutive(board, r, c, dr, dc, player)
                        if count >= 5:
                            score += 1000000
                        elif count == 4:
                            score += 80000 if open_ends >= 2 else 12000
                        elif count == 3:
                            score += 4000 if open_ends >= 2 else 600
                        elif count == 2:
                            score += 200 if open_ends == 2 else 40
        return score

    def _count_consecutive(self, board: Board, r: int, c: int, dr: int, dc: int, player: int) -> Tuple[int, int]:
        count = 1
        open_ends = 0
        for sign in (1, -1):
            nr, nc = r + dr * sign, c + dc * sign
            while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if board.grid[nr, nc] == player:
                    count += 1
                elif board.grid[nr, nc] == EMPTY:
                    open_ends += 1
                    break
                else:
                    break
                nr += dr * sign
                nc += dc * sign
        return count, open_ends

    def _get_ordered_candidates(self, board: Board, symbol: int, opponent: int) -> List[Tuple[int, int]]:
        threats = []
        for r, c in board.get_empty_cells():
            board.make_move(r, c, opponent)
            if board.check_win(opponent):
                board.undo_move(r, c)
                return [(r, c)]
            board.undo_move(r, c)

        candidates = []
        seen = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board.grid[nr, nc] == EMPTY and (
                            nr, nc) not in seen:
                                seen.add((nr, nc))
                                board.make_move(nr, nc, symbol)
                                score = self._evaluate_player(board, symbol)
                                board.undo_move(nr, nc)
                                candidates.append(((nr, nc), score))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, _ in candidates[:30]] or board.get_empty_cells()

    def _find_near_move(self, board: Board) -> Tuple[int, int]:
        candidates = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board.grid[nr, nc] == EMPTY:
                                candidates.add((nr, nc))
        if candidates:
            return random.choice(list(candidates))
        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (7, 7)


class AIPlayer(Player):
    def __init__(self, symbol: int, difficulty: Difficulty):
        self.symbol = symbol
        self.opponent = HUMAN if symbol == AI_PLAYER else AI_PLAYER
        self.strategy = self._get_strategy(difficulty)

    def _get_strategy(self, difficulty: Difficulty) -> AIStrategy:
        match difficulty:
            case Difficulty.EASY:
                return EasyStrategy()
            case Difficulty.MEDIUM:
                return MediumStrategy()
            case Difficulty.HARD:
                return HardStrategy()
            case _:
                return EasyStrategy()

    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        empties = board.get_empty_cells()
        if not empties:
            return None
        time.sleep(0.4)
        return self.strategy.find_move(board, self.symbol, self.opponent)
