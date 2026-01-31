from __future__ import annotations

from abc import ABC, abstractmethod
import random
from typing import Tuple, Optional, List

from constants import HUMAN, AI_PLAYER, EMPTY, Difficulty
from board import Board


class Player(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        pass


class HumanPlayer(Player):
    def get_move(self, board: Board) -> None:
        return None


class AIPlayer(Player):
    def __init__(self, symbol: int, difficulty: Difficulty):
        self.symbol = symbol
        self.opponent = HUMAN if symbol == AI_PLAYER else AI_PLAYER
        self.difficulty = difficulty

    def get_move(self, board: Board) -> Tuple[int, int]:
        match self.difficulty:
            case Difficulty.EASY:
                return self._easy_move(board)
            case Difficulty.MEDIUM:
                return self._medium_move(board)
            case Difficulty.HARD:
                return self._hard_move(board)
            case _:
                return self._easy_move(board)

    def _easy_move(self, board: Board) -> Tuple[int, int]:
        empties = board.get_empty_cells()
        if not empties:
            return (0, 0)
        return random.choice(empties)

    def _medium_move(self, board: Board) -> Tuple[int, int]:
        if move := self._find_winning_move(board, self.symbol):
            return move
        if move := self._find_winning_move(board, self.opponent):
            return move
        return self._find_near_move(board)

    def _hard_move(self, board: Board) -> Tuple[int, int]:
        if move := self._find_winning_move(board, self.symbol):
            return move
        if move := self._find_winning_move(board, self.opponent):
            return move

        candidates = self._get_scoring_candidates(board)
        if candidates:
            return max(candidates, key=lambda x: x[1])[0]

        return self._find_near_move(board)

    def _find_winning_move(
        self, board: Board, player: int
    ) -> Optional[Tuple[int, int]]:
        for r, c in board.get_empty_cells():
            board.make_move(r, c, player)
            win = board.check_win(player)
            board.undo_move(r, c)
            if win:
                return (r, c)
        return None

    def _find_near_move(self, board: Board) -> Tuple[int, int]:
        candidates: set[Tuple[int, int]] = set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if (
                                0 <= nr < BOARD_SIZE
                                and 0 <= nc < BOARD_SIZE
                                and board.grid[nr, nc] == EMPTY
                            ):
                                candidates.add((nr, nc))

        if candidates:
            return random.choice(list(candidates))

        empties = board.get_empty_cells()
        return random.choice(empties) if empties else (0, 0)

    def _get_scoring_candidates(
        self, board: Board
    ) -> List[Tuple[Tuple[int, int], int]]:
        candidates: List[Tuple[Tuple[int, int], int]] = []
        seen = set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] != EMPTY:
                    for dr in (-2, -1, 0, 1, 2):
                        for dc in (-2, -1, 0, 1, 2):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                                if board.grid[nr, nc] == EMPTY and (nr, nc) not in seen:
                                    score = self._evaluate_position(board, nr, nc)
                                    candidates.append(((nr, nc), score))
                                    seen.add((nr, nc))

        return candidates

    def _evaluate_position(self, board: Board, r: int, c: int) -> int:
        score = 0
        board.make_move(r, c, self.symbol)

        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            open_ends = 0

            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                steps = 1
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board.grid[nr, nc] == self.symbol:
                        count += 1
                    elif board.grid[nr, nc] == EMPTY:
                        open_ends += 1
                        break
                    else:
                        break
                    nr += dr * sign
                    nc += dc * sign
                    steps += 1
                    if steps > 6:
                        break

            if count >= 4:
                score += 10000
            elif count == 3:
                score += 500 if open_ends >= 2 else 200
            elif count == 2:
                score += 50 if open_ends == 2 else 10

        board.undo_move(r, c)
        return score
