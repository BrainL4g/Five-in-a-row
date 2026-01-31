from __future__ import annotations

import pygame
from pygame import Surface, Rect
from typing import Optional, Tuple

from constants import *
from board import Board


class Renderer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Пять в ряд — 3 уровня сложности")
        self.font_status = pygame.font.SysFont("segoe ui", FONT_SIZE_STATUS, bold=True)
        self.font_btn = pygame.font.SysFont("segoe ui", FONT_SIZE_BTN, bold=True)
        self.clock = pygame.time.Clock()

        self.btn_new_game = self._make_button("НОВАЯ ИГРА", 180, 50)
        self.btn_easy = self._make_button("ЛЁГКИЙ", 110, 38)
        self.btn_medium = self._make_button("СРЕДНИЙ", 110, 38)
        self.btn_hard = self._make_button("СЛОЖНЫЙ", 110, 38)

    def _make_button(self, text: str, w: int, h: int) -> dict:
        return {
            "text": text,
            "rect": Rect(0, 0, w, h),
            "surface": self.font_btn.render(text, True, (255, 255, 255)),
            "bg": (70, 130, 180),
            "hover": (100, 180, 255),
            "border": (40, 80, 140)
        }

    def draw_board(self, board: Board, hovered: Optional[Tuple[int, int]]) -> None:
        self.screen.fill((245, 222, 179))

        for i in range(BOARD_SIZE + 1):
            thick = 3 if i in (0, BOARD_SIZE) else 1
            pygame.draw.line(self.screen, (139, 69, 19),
                             (i * CELL_SIZE, 0),
                             (i * CELL_SIZE, BOARD_SIZE * CELL_SIZE), thick)
            pygame.draw.line(self.screen, (139, 69, 19),
                             (0, i * CELL_SIZE),
                             (BOARD_SIZE * CELL_SIZE, i * CELL_SIZE), thick)

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = c * CELL_SIZE + CELL_SIZE // 2
                y = r * CELL_SIZE + CELL_SIZE // 2

                if board.grid[r, c] == HUMAN:
                    pygame.draw.circle(self.screen, (18, 18, 18), (x, y), CELL_SIZE // 2 - 6)
                    pygame.draw.circle(self.screen, (40, 40, 40), (x, y), CELL_SIZE // 2 - 9, 2)
                elif board.grid[r, c] == AI_PLAYER:
                    pygame.draw.circle(self.screen, (248, 248, 255), (x, y), CELL_SIZE // 2 - 6)
                    pygame.draw.circle(self.screen, (200, 200, 200), (x, y), CELL_SIZE // 2 - 9, 2)

                if board.last_move and board.last_move[:2] == (r, c):
                    pygame.draw.circle(self.screen, (220, 60, 60, 140), (x, y), CELL_SIZE // 2 - 4, 5)

        if hovered:
            hx, hy = hovered
            rect = pygame.Rect(hx * CELL_SIZE, hy * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            surf.fill((100, 180, 255, 70))
            pygame.draw.rect(surf, (60, 140, 255, 140), (0, 0, CELL_SIZE, CELL_SIZE), 3, border_radius=4)
            self.screen.blit(surf, rect.topleft)

    def draw_ui(self, status_text: str, difficulty: Difficulty, mouse_pos: Tuple[int, int]) -> None:
        y_base = BOARD_SIZE * CELL_SIZE + 12

        status_surf = self.font_status.render(status_text, True, (30, 30, 50))
        self.screen.blit(status_surf, (24, y_base + 4))

        diff_text = f"Сложность: {difficulty.name}"
        diff_surf = self.font_status.render(diff_text, True, (70, 70, 130))
        self.screen.blit(diff_surf, (WINDOW_WIDTH - diff_surf.get_width() - 24, y_base + 4))

        y_btn = y_base + 54
        self._render_button(self.btn_new_game, (WINDOW_WIDTH // 2 - 90, y_btn), mouse_pos)

        y_diff_btn = y_btn + 8
        self._render_button(self.btn_easy,   (WINDOW_WIDTH // 2 - 195, y_diff_btn), mouse_pos)
        self._render_button(self.btn_medium, (WINDOW_WIDTH // 2 -  65, y_diff_btn), mouse_pos)
        self._render_button(self.btn_hard,   (WINDOW_WIDTH // 2 +  65, y_diff_btn), mouse_pos)

    def _render_button(self, btn: dict, pos: Tuple[int, int], mouse: Tuple[int, int]) -> None:
        btn["rect"].topleft = pos
        is_hover = btn["rect"].collidepoint(mouse)

        color = btn["hover"] if is_hover else btn["bg"]
        pygame.draw.rect(self.screen, color, btn["rect"], border_radius=10)
        pygame.draw.rect(self.screen, btn["border"], btn["rect"], 2, border_radius=10)

        if is_hover:
            shadow = pygame.Surface((btn["rect"].width + 6, btn["rect"].height + 6), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 40), (3, 3, btn["rect"].width, btn["rect"].height), border_radius=10)
            self.screen.blit(shadow, (pos[0] - 3, pos[1] - 3))

        text_rect = btn["surface"].get_rect(center=btn["rect"].center)
        self.screen.blit(btn["surface"], text_rect)

    def update(self) -> None:
        pygame.display.flip()
        self.clock.tick(75)

    def close(self) -> None:
        pygame.quit()