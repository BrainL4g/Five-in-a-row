from __future__ import annotations

import pygame
from pygame import Surface, Rect
from typing import Optional, Tuple

from constants import *
from board import Board


class Renderer:
    def __init__(self):
        pygame.init()
        self.screen: Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Пять в ряд · 3 уровня сложности")
        self.font_status = pygame.font.SysFont("segoe ui", FONT_SIZE_STATUS)
        self.font_btn = pygame.font.SysFont("segoe ui", FONT_SIZE_BTN, bold=True)
        self.clock = pygame.time.Clock()

        self.btn_new_game = self._create_button("НОВАЯ ИГРА", 180, 50)
        self.btn_easy = self._create_button("ЛЁГКИЙ", 120, 40)
        self.btn_medium = self._create_button("СРЕДНИЙ", 120, 40)
        self.btn_hard = self._create_button("СЛОЖНЫЙ", 120, 40)

    def _create_button(self, text: str, w: int, h: int) -> dict:
        return {
            "text": text,
            "rect": Rect(0, 0, w, h),
            "surface": self.font_btn.render(text, True, (255, 255, 255)),
            "bg": (60, 120, 220),
            "hover": (90, 150, 255),
        }

    def draw_board(self, board: Board, hovered: Optional[Tuple[int, int]]) -> None:
        self.screen.fill(COLOR_BG)

        for i in range(BOARD_SIZE + 1):
            thick = 3 if i in (0, BOARD_SIZE) else 1
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (i * CELL_SIZE, 0),
                (i * CELL_SIZE, BOARD_SIZE * CELL_SIZE),
                thick,
            )
            pygame.draw.line(
                self.screen,
                COLOR_GRID,
                (0, i * CELL_SIZE),
                (BOARD_SIZE * CELL_SIZE, i * CELL_SIZE),
                thick,
            )

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2
                color = (
                    COLOR_HUMAN
                    if board.grid[r, c] == HUMAN
                    else COLOR_AI if board.grid[r, c] == AI_PLAYER else None
                )
                if color:
                    pygame.draw.circle(self.screen, color, (x, y), CELL_SIZE // 2 - 5)
                    if board.last_move and board.last_move[:2] == (r, c):
                        pygame.draw.circle(
                            self.screen, COLOR_LAST_MOVE, (x, y), CELL_SIZE // 2 - 3, 4
                        )

        if hovered:
            hx, hy = hovered
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill(COLOR_HOVER)
            self.screen.blit(surf, (hx * CELL_SIZE, hy * CELL_SIZE))

    def draw_ui(
        self, status_text: str, difficulty: Difficulty, mouse_pos: Tuple[int, int]
    ) -> None:
        y_base = BOARD_SIZE * CELL_SIZE + 15

        status = self.font_status.render(status_text, True, (30, 30, 30))
        self.screen.blit(status, (20, y_base))

        diff_text = f"Сложность: {difficulty.name}"
        diff_surf = self.font_status.render(diff_text, True, (80, 80, 140))
        self.screen.blit(diff_surf, (WINDOW_WIDTH - diff_surf.get_width() - 20, y_base))

        self._draw_button(
            self.btn_new_game, (WINDOW_WIDTH // 2 - 90, y_base + 45), mouse_pos
        )

        y_diff = y_base + 50
        self._draw_button(self.btn_easy, (WINDOW_WIDTH // 2 - 200, y_diff), mouse_pos)
        self._draw_button(self.btn_medium, (WINDOW_WIDTH // 2 - 60, y_diff), mouse_pos)
        self._draw_button(self.btn_hard, (WINDOW_WIDTH // 2 + 80, y_diff), mouse_pos)

    def _draw_button(
        self, btn: dict, pos: Tuple[int, int], mouse_pos: Tuple[int, int]
    ) -> None:
        btn["rect"].topleft = pos
        color = btn["hover"] if btn["rect"].collidepoint(mouse_pos) else btn["bg"]
        pygame.draw.rect(self.screen, color, btn["rect"], border_radius=8)
        pygame.draw.rect(self.screen, (30, 30, 30), btn["rect"], 2, border_radius=8)
        text_rect = btn["surface"].get_rect(center=btn["rect"].center)
        self.screen.blit(btn["surface"], text_rect)

    def update(self) -> None:
        pygame.display.flip()
        self.clock.tick(60)

    def close(self) -> None:
        pygame.quit()
