from __future__ import annotations
from abc import ABC, abstractmethod
import random
import time
from typing import Tuple, Optional, List
from constants import BOARD_SIZE, HUMAN, AI_PLAYER, EMPTY, Difficulty
from board import Board


class Player(ABC):
    @abstractmethod
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        pass


class HumanPlayer(Player):
    def get_move(self, board: Board) -> Optional[Tuple[int, int]]:
        return None


class AIPlayer(Player):
    def __init__(self, symbol: int, difficulty: Difficulty):
        self.symbol = symbol
        self
