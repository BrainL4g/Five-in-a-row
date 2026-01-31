from __future__ import annotations

import numpy as np
from typing import Tuple, Optional, List

from constants import BOARD_SIZE, EMPTY


class Board:
    def __init__(self) -> None:
        self.grid: np.ndarray = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)
        self.last_move: Optional[Tuple[int, int, int]] = None

    def make_move(self, row: int, col: int, player: int) -> bool:
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return False
        if self.grid[row, col] != EMPTY:
            return False

        self.grid[row, col] = player
        self.last_move = (row, col, player)
        return True

    def undo_move(self, row: int, col: int) -> None:
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.grid[row, col] != EMPTY:
            self.grid[row, col] = EMPTY

    def is_full(self) -> bool:
        return np.all(self.grid != EMPTY)

    def check_win(self, player: int) -> bool:
        if self.last_move is None:
            return False
        r, c, last_player = self.last_move

        if last_player != player:
            return False

        directions: List[Tuple[int, int]] = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                nr, nc = r + dr * sign, c + dc * sign
                while (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and
                       self.grid[nr, nc] == player):
                    count += 1
                    nr += dr * sign
                    nc += dc * sign
            if count >= 5:
                return True
        return False

    def get_empty_cells(self) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.grid[r, c] == EMPTY
        ]