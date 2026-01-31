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
        if move := self._find_winning_move(board, symbol):
            return move
        if move := self._find_winning_move(board, opponent):
            return move
        candidates = self._get_scoring_candidates(board, symbol)
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]
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

    def _get_scoring_candidates(self, board: Board, symbol: int) -> List[Tuple[Tuple[int, int], int]]:
        candidates = []
        seen = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in (-2, -1, 0, 1, 2):
                        for dc in (-2, -1, 0, 1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                                    board.grid[nr, nc] == EMPTY and (nr, nc) not in seen):
                                score = self._evaluate_position(board, nr, nc, symbol)
                                candidates.append(((nr, nc), score))
                                seen.add((nr, nc))
        return candidates

    def _evaluate_position(self, board: Board, r: int, c: int, symbol: int) -> int:
        if not board.make_move(r, c, symbol):
            return -999999

        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            line_cells = [(r, c)]
            stones = 1
            open_ends = 0

            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                consecutive = 0
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board.grid[nr, nc] == symbol:
                        consecutive += 1
                        line_cells.append((nr, nc))
                    elif board.grid[nr, nc] == EMPTY:
                        open_ends += 1
                        break
                    else:
                        break
                    nr += dr * sign
                    nc += dc * sign

                stones += consecutive

            if stones >= 5:
                score += 1_000_000
            elif stones == 4:
                score += 50_000 if open_ends >= 2 else 8_000
            elif stones == 3:
                score += 2_500 if open_ends >= 2 else 400
            elif stones == 2:
                score += 180 if open_ends == 2 else 30
            elif stones == 1:
                score += 10 if open_ends == 2 else 2

            if open_ends == 0 and stones >= 3:
                score -= 3000

        board.undo_move(r, c)
        return score


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
        time.sleep(0.3)
        return self.strategy.find_move(board, self.symbol, self.opponent)
