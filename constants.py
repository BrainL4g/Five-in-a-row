from enum import IntEnum, auto

BOARD_SIZE = 15
CELL_SIZE = 36
GRID_OFFSET_X = 20
GRID_OFFSET_Y = 20
UI_PANEL_HEIGHT = 180
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + GRID_OFFSET_X * 2
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + GRID_OFFSET_Y + UI_PANEL_HEIGHT

EMPTY = 0
HUMAN = 1
AI_PLAYER = 2

FONT_SIZE_STATUS = 26
FONT_SIZE_BTN = 22
AI_THINKING_DELAY = 700


class Difficulty(IntEnum):
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()


class VisualStyle(IntEnum):
    CLASSIC = auto()
    MODERN = auto()


STYLES = {
    VisualStyle.CLASSIC: {
        "COLOR_BG": (220, 179, 92),
        "COLOR_GRID": (101, 67, 33),
        "COLOR_HUMAN": (200, 0, 0),
        "COLOR_AI": (20, 20, 20),
        "COLOR_HOVER": (255, 255, 255, 60),
        "COLOR_LAST_MOVE": (255, 255, 0, 180)
    },
    VisualStyle.MODERN: {
        "COLOR_BG": (18, 18, 24),
        "COLOR_GRID": (60, 68, 80),
        "COLOR_HUMAN": (97, 175, 239),
        "COLOR_AI": (235, 107, 111),
        "COLOR_HOVER": (255, 255, 255, 40),
        "COLOR_LAST_MOVE": (255, 193, 7, 180)
    }
}
