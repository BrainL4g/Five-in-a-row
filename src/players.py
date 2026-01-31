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
        if move := self._find_double_open_four_threat(board, opponent):
            return move
        if move := self._find_double_or_critical_three_threat(board, opponent):
            return move

        empty_count = len(board.get_empty_cells())
        total_moves_made = BOARD_SIZE ** 2 - empty_count

        if total_moves_made < 6:
            cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2
            candidates = []
            for dr in range(-5, 6):
                for dc in range(-5, 6):
                    r, c = cy + dr, cx + dc
                    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board.grid[r, c] == EMPTY:
                        candidates.append((r, c))
            if candidates:
                return random.choice(candidates)

        candidates = self._get_scoring_candidates(board, symbol)
        if candidates:
            top_score = candidates[0][1]
            good_moves = [pos for pos, sc in candidates[:8] if sc >= top_score - 2000]
            return random.choice(good_moves)

        return self._find_near_move(board)

    def _find_winning_move(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for r, c in board.get_empty_cells():
            if board.make_move(r, c, player):
                win = board.check_win(player)
                board.undo_move(r, c)
                if win:
                    return (r, c)
        return None

    def _find_double_open_four_threat(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        threats = []
        for r, c in board.get_empty_cells():
            if board.make_move(r, c, player):
                count = self._count_open_fours(board, player)
                board.undo_move(r, c)
                if count >= 2:
                    threats.append((r, c))
        if threats:
            return random.choice(threats)
        return None

    def _find_double_or_critical_three_threat(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        threats = []
        for r, c in board.get_empty_cells():
            if board.make_move(r, c, player):
                open_threes = self._count_open_threes(board, player)
                board.undo_move(r, c)
                if open_threes >= 2:
                    threats.append((r, c))
                elif open_threes >= 1:
                    threats.append((r, c))
        if threats:
            return random.choice(threats)
        return None

    def _count_open_fours(self, board: Board, player: int) -> int:
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in directions:
                        stones, open_ends = self._count_in_direction(board, r, c, dr, dc, player)
                        if stones == 4 and open_ends >= 2:
                            count += 1
        return count

    def _count_open_threes(self, board: Board, player: int) -> int:
        count = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board.grid[r, c] == player:
                    for dr, dc in directions:
                        stones, open_ends = self._count_in_direction(board, r, c, dr, dc, player)
                        if stones == 3 and open_ends >= 2:
                            count += 1
        return count

    def _count_in_direction(self, board: Board, r: int, c: int, dr: int, dc: int, player: int) -> Tuple[int, int]:
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
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                                    board.grid[nr, nc] == EMPTY and (nr, nc) not in seen):
                                score = self._evaluate_position(board, nr, nc, symbol)
                                candidates.append(((nr, nc), score))
                                seen.add((nr, nc))
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:12]

    def _evaluate_position(self, board: Board, r: int, c: int, symbol: int) -> int:
        if not board.make_move(r, c, symbol):
            return -999999
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            stones = 1
            open_ends = 0
            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                while 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                    if board.grid[nr, nc] == symbol:
                        stones += 1
                    elif board.grid[nr, nc] == EMPTY:
                        open_ends += 1
                        break
                    else:
                        break
                    nr += dr * sign
                    nc += dc * sign
            if stones >= 5:
                score += 1000000
            elif stones == 4:
                score += 50000 if open_ends >= 2 else 8000
            elif stones == 3:
                score += 2500 if open_ends >= 2 else 400
            elif stones == 2:
                score += 180 if open_ends == 2 else 30
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
