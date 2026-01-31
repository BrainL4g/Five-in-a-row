from __future__ import annotations
import pygame
from pygame import Surface, Rect
from typing import Optional, Tuple
from constants import *
from board import Board


class Renderer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Пять в ряд • Улучшенная графика")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
        self.font_status = pygame.font.SysFont("Arial", FONT_SIZE_STATUS, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", FONT_SIZE_BTN, bold=True)
        self.clock = pygame.time.Clock()
        self.animations = {}
        self.win_animation_timer = 0
        self.win_animation_phase = 0
        self.btn_new_game = self._make_button("НОВАЯ ИГРА", 200, 50, COLOR_BTN_NEW_GAME)
        self.btn_easy = self._make_button("ЛЁГКИЙ", 120, 42, COLOR_BTN_EASY)
        self.btn_medium = self._make_button("СРЕДНИЙ", 120, 42, COLOR_BTN_MEDIUM)
        self.btn_hard = self._make_button("СЛОЖНЫЙ", 120, 42, COLOR_BTN_HARD)
        self.btn_gradient = self._create_gradient((200, 50), (30, 30, 40), (50, 50, 70))

    def _make_button(self, text: str, w: int, h: int, color):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=12)
        pygame.draw.rect(surf, (255, 255, 255, 60), (0, 0, w, h), 3, border_radius=12)
        text_surf = self.font_btn.render(text, True, (255, 255, 255))
        return {
            "text": text,
            "rect": Rect(0, 0, w, h),
            "surface": surf,
            "text_surface": text_surf,
            "bg": color,
            "hover": tuple(min(c + 30, 255) for c in color),
            "border": (255, 255, 255, 60)
        }

    def _create_gradient(self, size, color1, color2):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        for y in range(size[1]):
            ratio = y / size[1]
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (size[0], y))
        return surf

    def draw_board(self, board, hovered, scale_factors):
        self.screen.fill(COLOR_BG)
        board_rect = pygame.Rect(100, 100, BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE)
        pygame.draw.rect(self.screen, (25, 28, 36), board_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_GRID_LINE, board_rect, 3, border_radius=10)
        for i in range(BOARD_SIZE + 1):
            x = 100 + i * CELL_SIZE
            y = 100 + i * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, 100), (x, 100 + BOARD_SIZE * CELL_SIZE),
                             2 if i in (0, BOARD_SIZE) else 1)
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (100, y), (100 + BOARD_SIZE * CELL_SIZE, y),
                             2 if i in (0, BOARD_SIZE) else 1)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = 100 + c * CELL_SIZE + CELL_SIZE // 2
                y = 100 + r * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, COLOR_GRID_LINE, (x, y), 1)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x = 100 + c * CELL_SIZE + CELL_SIZE // 2
                y = 100 + r * CELL_SIZE + CELL_SIZE // 2
                if board.grid[r, c] == HUMAN:
                    scale = scale_factors.get((r, c), 1.0)
                    radius = int((CELL_SIZE // 2 - 8) * scale)
                    for i in range(3):
                        pygame.draw.circle(self.screen,
                                           (min(97 + i * 10, 255), min(175 + i * 5, 255), min(239 - i * 5, 255)),
                                           (x, y), radius - i * 2)
                    pygame.draw.circle(self.screen, (70, 130, 200), (x, y), radius - 6)
                    for i in range(3):
                        pygame.draw.circle(self.screen, (97, 175, 239, 30 - i * 10), (x, y), radius + 5 + i * 2)
                elif board.grid[r, c] == AI_PLAYER:
                    scale = scale_factors.get((r, c), 1.0)
                    radius = int((CELL_SIZE // 2 - 8) * scale)
                    for i in range(3):
                        pygame.draw.circle(self.screen,
                                           (min(235 + i * 5, 255), min(107 + i * 10, 255), min(111 + i * 5, 255)),
                                           (x, y), radius - i * 2)
                    pygame.draw.circle(self.screen, (200, 80, 90), (x, y), radius - 6)
                    for i in range(3):
                        pygame.draw.circle(self.screen, (235, 107, 111, 30 - i * 10), (x, y), radius + 5 + i * 2)
        if board.last_move:
            lr, lc, _ = board.last_move
            lx = 100 + lc * CELL_SIZE + CELL_SIZE // 2
            ly = 100 + lr * CELL_SIZE + CELL_SIZE // 2
            pulse = (pygame.time.get_ticks() // 20) % 20
            ring_radius = CELL_SIZE // 2 - 4 + pulse // 2
            for i in range(3):
                pygame.draw.circle(self.screen, (255, 193, 7, 100 - i * 30), (lx, ly), ring_radius - i * 3, 2)
        if board.win_line and hasattr(board, 'game_over') and board.game_over:
            self.win_animation_timer = (self.win_animation_timer + 1) % 60
            self.win_animation_phase = self.win_animation_timer // 15
            alpha = 120 + 100 * (self.win_animation_timer % 30) / 30
            for r, c in board.win_line:
                x = 100 + c * CELL_SIZE + CELL_SIZE // 2
                y = 100 + r * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, (255, 221, 87, int(alpha)), (x, y), CELL_SIZE // 2 - 3)
                pygame.draw.circle(self.screen, (255, 255, 255, int(alpha * 0.7)), (x, y), CELL_SIZE // 2 - 3, 2)
        if hovered and board.grid[hovered[0], hovered[1]] == EMPTY:
            hr, hc = hovered
            hx = 100 + hc * CELL_SIZE
            hy = 100 + hr * CELL_SIZE
            bounce = abs((pygame.time.get_ticks() // 5) % 40 - 20) / 20
            offset_y = int(-5 * bounce)
            hover_rect = pygame.Rect(hx, hy + offset_y, CELL_SIZE, CELL_SIZE)
            hover_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            hover_surf.fill((255, 255, 255, 30))
            pygame.draw.rect(hover_surf, (255, 255, 255, 100), (0, 0, CELL_SIZE, CELL_SIZE), 2, border_radius=4)
            self.screen.blit(hover_surf, hover_rect.topleft)
            preview_color = COLOR_HUMAN if hasattr(board,
                                                   'current_player') and board.current_player == HUMAN else COLOR_AI
            preview_alpha = 80 + 40 * bounce
            preview_x = hx + CELL_SIZE // 2
            preview_y = hy + CELL_SIZE // 2 + offset_y
            pygame.draw.circle(self.screen, (*preview_color[:3], int(preview_alpha)), (preview_x, preview_y),
                               CELL_SIZE // 2 - 10)

    def draw_ui(self, status_text, difficulty, mouse_pos, game_over):
        y_base = 100 + BOARD_SIZE * CELL_SIZE + 30
        status_bg = pygame.Rect(100, y_base - 10, BOARD_SIZE * CELL_SIZE, 50)
        pygame.draw.rect(self.screen, (30, 33, 42), status_bg, border_radius=8)
        pygame.draw.rect(self.screen, (60, 68, 80), status_bg, 2, border_radius=8)
        status_surf = self.font_status.render(status_text, True, COLOR_STATUS)
        status_x = 100 + (BOARD_SIZE * CELL_SIZE - status_surf.get_width()) // 2
        self.screen.blit(status_surf, (status_x, y_base))
        diff_text = f"Сложность: {difficulty.name}"
        diff_surf = self.font_status.render(diff_text, True, COLOR_DIFFICULTY)
        self.screen.blit(diff_surf, (WINDOW_WIDTH - diff_surf.get_width() - 120, y_base))
        y_btn = y_base + 70
        self._render_button(self.btn_new_game, (WINDOW_WIDTH // 2 - self.btn_new_game["rect"].width // 2, y_btn),
                            mouse_pos)
        y_diff_btn = y_btn + 60
        btn_spacing = 140
        start_x = WINDOW_WIDTH // 2 - (btn_spacing * 1.5)
        self._render_button(self.btn_easy, (start_x, y_diff_btn), mouse_pos)
        self._render_button(self.btn_medium, (start_x + btn_spacing, y_diff_btn), mouse_pos)
        self._render_button(self.btn_hard, (start_x + btn_spacing * 2, y_diff_btn), mouse_pos)
        diff_indicators = {
            Difficulty.EASY: (start_x, y_diff_btn),
            Difficulty.MEDIUM: (start_x + btn_spacing, y_diff_btn),
            Difficulty.HARD: (start_x + btn_spacing * 2, y_diff_btn)
        }
        if game_over:
            ind_x, ind_y = diff_indicators[difficulty]
            pygame.draw.rect(self.screen, (255, 255, 255, 150), (
            ind_x - 5, ind_y - 5, self.btn_easy["rect"].width + 10, self.btn_easy["rect"].height + 10), 3,
                             border_radius=14)

    def _render_button(self, btn, pos, mouse):
        btn["rect"].topleft = pos
        is_hover = btn["rect"].collidepoint(mouse)
        if is_hover:
            shadow = pygame.Surface((btn["rect"].width + 8, btn["rect"].height + 8), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 80), (4, 4, btn["rect"].width, btn["rect"].height), border_radius=14)
            self.screen.blit(shadow, (pos[0] - 4, pos[1] - 4))
            scale_surf = pygame.transform.scale(btn["surface"],
                                                (int(btn["rect"].width * 1.05), int(btn["rect"].height * 1.05)))
            scaled_rect = scale_surf.get_rect(center=btn["rect"].center)
            self.screen.blit(scale_surf, scaled_rect)
        else:
            self.screen.blit(btn["surface"], pos)
        text_rect = btn["text_surface"].get_rect(center=btn["rect"].center)
        self.screen.blit(btn["text_surface"], text_rect)
        if is_hover:
            glow = pygame.Surface((btn["rect"].width + 20, btn["rect"].height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow, (*btn["bg"][:3], 30), (10, 10, btn["rect"].width, btn["rect"].height),
                             border_radius=16)
            self.screen.blit(glow, (pos[0] - 10, pos[1] - 10))

    def update(self):
        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        pygame.quit()
