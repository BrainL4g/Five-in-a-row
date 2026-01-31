from __future__ import annotations
import pygame
from pygame import Surface, Rect
from typing import Optional, Tuple
from constants import *
from board import Board


class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Пять в ряд")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.font_status = pygame.font.SysFont("Arial", FONT_SIZE_STATUS)
        self.font_btn = pygame.font.SysFont("Arial", FONT_SIZE_BTN)
        self.clock = pygame.time.Clock()
        self.current_style = STYLES[VisualStyle.CLASSIC]

    def set_style(self, style: VisualStyle):
        self.current_style = STYLES[style]

    def draw_board(self, board: Board, hovered: Optional[Tuple[int, int]]) -> None:
        self.screen.fill(self.current_style["COLOR_BG"])
        for i in range(BOARD_SIZE + 1):
            pygame.draw.line(self.screen, self.current_style["COLOR_GRID"],
                             (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y),
                             (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE), 2)
            pygame.draw.line(self.screen, self.current_style["COLOR_GRID"],
                             (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE),
                             (GRID_OFFSET_X + BOARD_SIZE * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE), 2)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                y = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                if board.grid[r, c] == HUMAN:
                    pygame.draw.circle(self.screen, self.current_style["COLOR_HUMAN"], (x, y), CELL_SIZE // 2 - 4)
                elif board.grid[r, c] == AI_PLAYER:
                    pygame.draw.circle(self.screen, self.current_style["COLOR_AI"], (x, y), CELL_SIZE // 2 - 4)
        if board.last_move:
            lr, lc, _ = board.last_move
            lx = GRID_OFFSET_X + lc * CELL_SIZE + CELL_SIZE // 2
            ly = GRID_OFFSET_Y + lr * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(self.screen, self.current_style["COLOR_LAST_MOVE"], (lx, ly), CELL_SIZE // 2 - 2, 3)
        if board.win_line:
            for r, c in board.win_line:
                x = GRID_OFFSET_X + c * CELL_SIZE + CELL_SIZE // 2
                y = GRID_OFFSET_Y + r * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, (255, 255, 0), (x, y), CELL_SIZE // 2 - 1, 3)
        if hovered and board.grid[hovered[0], hovered[1]] == EMPTY:
            hr, hc = hovered
            hx = GRID_OFFSET_X + hc * CELL_SIZE
            hy = GRID_OFFSET_Y + hr * CELL_SIZE
            hover_surf = Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            hover_surf.fill(self.current_style["COLOR_HOVER"])
            self.screen.blit(hover_surf, (hx, hy))

    def draw_menu(self, menu_state):
        overlay = Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        title = self.font_status.render("ПЯТЬ В РЯД", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 80))
        buttons = menu_state["buttons"]
        for btn in buttons.values():
            rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 220, 50)
            color = (100, 100, 200) if btn.get("hover", False) else (70, 70, 160)
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=8)
            text = self.font_btn.render(btn["text"], True, (255, 255, 255))
            self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

    def draw_settings(self, settings_state):
        overlay = Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        title = self.font_status.render("НАСТРОЙКИ", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 60))
        for section in ["difficulty", "visual"]:
            for key, btn in settings_state[section].items():
                rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 180, 42)
                is_active = btn.get("active", False)
                color = (90, 180, 90) if is_active else (80, 80, 150)
                if btn.get("hover", False):
                    color = tuple(min(c + 30, 255) for c in color)
                pygame.draw.rect(self.screen, color, rect, border_radius=6)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=6)
                text = self.font_btn.render(btn["text"], True, (255, 255, 255))
                self.screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))
        back_btn = settings_state["back_button"]
        back_rect = pygame.Rect(back_btn["pos"][0], back_btn["pos"][1], 120, 40)
        back_color = (180, 80, 80) if back_btn.get("hover", False) else (150, 60, 60)
        pygame.draw.rect(self.screen, back_color, back_rect, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255), back_rect, 2, border_radius=6)
        text = self.font_btn.render(back_btn["text"], True, (255, 255, 255))
        self.screen.blit(text, (back_rect.centerx - text.get_width() // 2, back_rect.centery - text.get_height() // 2))

    def draw_ui(self, status_text: str, difficulty: Difficulty, mouse_pos: Tuple[int, int], game_over: bool) -> None:
        y_base = GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE + 20
        status_surf = self.font_status.render(status_text, True, (30, 30, 30))
        self.screen.blit(status_surf, (GRID_OFFSET_X, y_base))
        diff_text = f"Сложность: {difficulty.name}"
        diff_surf = self.font_status.render(diff_text, True, (50, 50, 100))
        self.screen.blit(diff_surf, (WINDOW_WIDTH - diff_surf.get_width() - GRID_OFFSET_X, y_base))
        btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 70, y_base + 50, 140, 40)
        pygame.draw.rect(self.screen, (80, 120, 200), btn_rect, border_radius=6)
        pygame.draw.rect(self.screen, (255, 255, 255), btn_rect, 2, border_radius=6)
        btn_text = self.font_btn.render("МЕНЮ", True, (255, 255, 255))
        self.screen.blit(btn_text,
                         (btn_rect.centerx - btn_text.get_width() // 2, btn_rect.centery - btn_text.get_height() // 2))
        if btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(self.screen, (255, 255, 255, 80), btn_rect, 3, border_radius=6)

    def update(self):
        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        pygame.quit()
