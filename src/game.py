from __future__ import annotations
import pygame
import time
from typing import Optional, Tuple, Dict
from src.constants import *
from src.board import Board
from src.players import HumanPlayer, AIPlayer
from src.renderer import Renderer
from src.menu import Menu
from src.settings import Settings


class Game:
    def __init__(self):
        self.board = Board()
        self.renderer = Renderer()
        self.menu = Menu()
        self.settings = Settings(Difficulty.MEDIUM, VisualStyle.CLASSIC)
        self.renderer.set_style(self.settings.get_style())
        self.human = HumanPlayer()
        self.ai = AIPlayer(AI_PLAYER, self.settings.get_difficulty())
        self.current_player = HUMAN
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
        self.ai_move_time = 0

    def run(self) -> None:
        running = True
        hovered = None
        last_move_time = 0
        while running:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    hovered = self._get_hovered_cell(mouse_pos)
                    if self.menu.state["active"]:
                        self.menu.update_hover(mouse_pos)
                    elif self.settings.state["active"]:
                        self.settings.update_hover(mouse_pos)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.menu.state["active"]:
                        action = self.menu.handle_click(mouse_pos)
                        if action == "new_game":
                            self.reset_game()
                            self.menu.hide()
                        elif action == "settings":
                            self.menu.hide()
                            self.settings.show()
                        elif action == "exit":
                            running = False
                    elif self.settings.state["active"]:
                        action, _ = self.settings.handle_click(mouse_pos)
                        if action == "back":
                            self.settings.hide()
                            self.menu.show()
                        elif action == "setting_changed":
                            self.renderer.set_style(self.settings.get_style())
                            self.ai = AIPlayer(AI_PLAYER, self.settings.get_difficulty())
                    else:
                        hovered = self._get_hovered_cell(mouse_pos)
                        if hovered:
                            if not self.game_over and self.current_player == HUMAN:
                                if self.board.make_move(hovered[0], hovered[1], HUMAN):
                                    self._after_move(HUMAN)
                        ui_btn_rect = pygame.Rect(WINDOW_WIDTH // 2 - 70,
                                                  GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE + 50,
                                                  140, 40)
                        if ui_btn_rect.collidepoint(mouse_pos):
                            self.menu.show()
            if not self.game_over and self.current_player == AI_PLAYER and not self.ai_thinking:
                if current_time - last_move_time > AI_THINKING_DELAY:
                    self.ai_thinking = True
                    self.ai_move_time = current_time
            if self.ai_thinking and current_time - self.ai_move_time > 500:
                move = self.ai.get_move(self.board)
                if move:
                    r, c = move
                    if self.board.make_move(r, c, AI_PLAYER):
                        last_move_time = current_time
                        self._after_move(AI_PLAYER)
                self.ai_thinking = False
            self.renderer.draw_board(self.board, hovered)
            if self.menu.state["active"]:
                self.renderer.draw_menu(self.menu.state)
            elif self.settings.state["active"]:
                self.renderer.draw_settings(self.settings.state)
            else:
                status = self._get_status_text()
                self.renderer.draw_ui(status, self.settings.get_difficulty(), mouse_pos, self.game_over)
            self.renderer.update()
        self.renderer.close()

    def _get_hovered_cell(self, mouse_pos) -> Optional[Tuple[int, int]]:
        mx, my = mouse_pos
        if (GRID_OFFSET_X <= mx < GRID_OFFSET_X + BOARD_SIZE * CELL_SIZE and
                GRID_OFFSET_Y <= my < GRID_OFFSET_Y + BOARD_SIZE * CELL_SIZE):
            col = (mx - GRID_OFFSET_X) // CELL_SIZE
            row = (my - GRID_OFFSET_Y) // CELL_SIZE
            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                return (row, col)
        return None

    def _after_move(self, player: int) -> None:
        if self.board.check_win(player):
            self.game_over = True
            self.winner = player
        elif self.board.is_full():
            self.game_over = True
            self.winner = None
        else:
            self.current_player = AI_PLAYER if player == HUMAN else HUMAN

    def _get_status_text(self) -> str:
        if self.ai_thinking:
            return "Компьютер думает..."
        if self.game_over:
            if self.winner == HUMAN:
                return "Вы победили!"
            if self.winner == AI_PLAYER:
                return "Победил компьютер"
            return "Ничья!"
        return "Ваш ход" if self.current_player == HUMAN else "Ход компьютера..."

    def reset_game(self):
        self.board = Board()
        self.current_player = HUMAN
        self.game_over = False
        self.winner = None
        self.ai_thinking = False
