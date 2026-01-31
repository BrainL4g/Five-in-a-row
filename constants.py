from enum import IntEnum, auto
from typing import Final

BOARD_SIZE: Final = 15
CELL_SIZE: Final = 40
WINDOW_WIDTH: Final = BOARD_SIZE * CELL_SIZE
WINDOW_HEIGHT: Final = BOARD_SIZE * CELL_SIZE + 120

EMPTY: Final = 0
HUMAN: Final = 1
AI_PLAYER: Final = 2

COLOR_BG = (240, 217, 181)
COLOR_GRID = (60, 40, 20)
COLOR_HUMAN = (20, 20, 20)
COLOR_AI = (245, 245, 245)
COLOR_HOVER = (80, 180, 255, 90)
COLOR_LAST_MOVE = (255, 80, 80, 160)

FONT_SIZE_STATUS = 32
FONT_SIZE_BTN = 28


class Difficulty(IntEnum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
