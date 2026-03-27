from __future__ import annotations
import numpy as np
from typing import Tuple, Optional, List
from src.constants import BOARD_SIZE, EMPTY
import json
import hashlib


class Board:
    def __init__(self) -> None:
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        self.last_move: Optional[Tuple[int, int, int]] = None
        self.win_line: Optional[List[Tuple[int, int]]] = None
        self._near_cache: List[Tuple[int, int]] = []
        self.move_history: List[Tuple[int, int, int]] = []

    def make_move(self, row: int, col: int, player: int) -> bool:
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        if self.grid[row, col] != EMPTY:
            return False
        self.grid[row, col] = player
        self.last_move = (row, col, player)
        self.move_history.append((row, col, player))
        self._near_cache = []
        return True

    def undo_last_move(self) -> Optional[Tuple[int, int]]:
        if not self.move_history:
            return None
        row, col, _ = self.move_history.pop()
        if self.grid[row, col] != EMPTY:
            self.grid[row, col] = EMPTY
        self.win_line = None
        self._near_cache = []
        self.last_move = self.move_history[-1] if self.move_history else None
        return (row, col)

    def undo_moves(self, count: int) -> List[Tuple[int, int]]:
        undone = []
        for _ in range(count):
            move = self.undo_last_move()
            if move:
                undone.append(move)
            else:
                break
        return undone

    def is_full(self) -> bool:
        return np.all(self.grid != EMPTY)

    def check_win(self, player: int) -> bool:
        if self.last_move is None:
            return False
        r, c, last_player = self.last_move
        if last_player != player:
            return False
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        self.win_line = [(r, c)]
        for dr, dc in directions:
            count = 1
            line = [(r, c)]
            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                while (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                       self.grid[nr, nc] == player):
                    count += 1
                    line.append((nr, nc))
                    nr += dr * sign
                    nc += dc * sign
            if count >= 5:
                self.win_line = line
                return True
        self.win_line = None
        return False

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        return [(r, c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if self.grid[r, c] == EMPTY]

    def get_near_empty_cells(self) -> List[Tuple[int, int]]:
        if self._near_cache:
            return self._near_cache

        seen = set()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.grid[r, c] != EMPTY:
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            if dr == 0 and dc == 0:
                                continue
                            nr = r + dr
                            nc = c + dc
                            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and self.grid[nr, nc] == EMPTY:
                                seen.add((nr, nc))

        self._near_cache = list(seen)
        return self._near_cache if self._near_cache else self.get_empty_cells()

    def get_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.grid.tolist()).encode()).hexdigest()
