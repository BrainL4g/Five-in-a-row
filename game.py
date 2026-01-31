from __future__ import annotations
import pygame
import time
from typing import Optional, Tuple, Dict
from constants import *
from board import Board
from players import HumanPlayer, AIPlayer
from renderer import Renderer


class Game:
    def __init__(self):
        self.board = Board()
        self.human = HumanPlayer()
        self.ai = AIPlayer(AI_PLAYER, Difficulty.MEDIUM)
        self.renderer = Renderer()
        self.current_player = HUMAN
        self.game_over = False
        self.winner = None
        self.difficulty = Difficulty.MEDIUM
        self.scale_factors = {}
        self.animation_timer = 0
        self.ai_thinking = False
        self.ai_move_time = 0

    def run(self):
        running = True
        hovered = None
        last_move_time = 0

        while running:
            current_time = pygame.time.get_ticks()
            mouse_pos = pygame.mouse.get_pos()
            self.animation_timer += 1
            self._update_animations()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    if 100 <= mx < 100 + BOARD_SIZE * CELL_SIZE and 100 <= my < 100 + BOARD_SIZE * CELL_SIZE:
                        col = (mx - 100) // CELL_SIZE
                        row = (my - 100) // CELL_SIZE
                        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                            hovered = (row, col)
                        else:
                            hovered = None
                    else:
                        hovered = None
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.game_over and self.current_player == HUMAN:
                        mx, my = event.pos
                        if 100 <= mx < 100 + BOARD_SIZE * CELL_SIZE and 100 <= my < 100 + BOARD_SIZE * CELL_SIZE:
                            col = (mx - 100) // CELL_SIZE
                            row = (my - 100) // CELL_SIZE
                            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                                if self.board.make_move(row, col, HUMAN):
                                    self.scale_factors[(row, col)] = 0.1
                                    last_move_time = current_time
                                    self._after_move(HUMAN)
                    if self.renderer.btn_new_game["rect"].collidepoint(event.pos):
                        self.reset_game()
                    if self.renderer.btn_easy["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.EASY)
                    if self.renderer.btn_medium["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.MEDIUM)
                    if self.renderer.btn_hard["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.HARD)

            if not self.game_over and self.current_player == AI_PLAYER and not self.ai_thinking:
                if current_time - last_move_time > AI_THINKING_DELAY:
                    self.ai_thinking = True
                    self.ai_move_time = current_time

            if self.ai_thinking and current_time - self.ai_move_time > 500:
                move = self.ai.get_move(self.board)
                if move:
                    r, c = move
                    if self.board.make_move(r, c, AI_PLAYER):
                        self.scale_factors[(r, c)] = 0.1
                        last_move_time = current_time
                        self._after_move(AI_PLAYER)
                self.ai_thinking = False

            status = self._get_status_text()
            self.renderer.draw_board(self.board, hovered, self.scale_factors)
            self.renderer.draw_ui(status, self.difficulty, mouse_pos, self.game_over)
            self.renderer.update()
            pygame.time.delay(10)

        self.renderer.close()

    def _update_animations(self):
        keys_to_remove = []
        for pos, scale in self.scale_factors.items():
            if scale < 1.0:
                self.scale_factors[pos] = min(1.0, scale + 0.08)
            elif scale > 1.0:
                self.scale_factors[pos] = max(1.0, scale - 0.08)
            else:
                keys_to_remove.append(pos)
        for key in keys_to_remove:
            del self.scale_factors[key]

    def _after_move(self, player):
        if self.board.check_win(player):
            self.game_over = True
            self.winner = player
            self.board.game_over = True
            self.renderer.win_animation_timer = 0
        elif self.board.is_full():
            self.game_over = True
            self.winner = None
            self.board.game_over = True
        else:
            self.current_player = AI_PLAYER if player == HUMAN else HUMAN
            self.board.current_player = self.current_player

    def _get_status_text(self):
        if self.ai_thinking:
            return "Компьютер думает..."
        if self.game_over:
            if self.winner == HUMAN:
                return "🎉 Вы победили! 🎉"
            if self.winner == AI_PLAYER:
                return "💻 Победил компьютер"
            return "🤝 Ничья!"
        return "Ваш ход" if self.current_player == HUMAN else "Ход компьютера..."

    def reset_game(self):
        self.board = Board()
        self.current_player = HUMAN
        self.game_over = False
        self.winner = None
        self.scale_factors.clear()
        self.ai_thinking = False
        self.renderer.win_animation_timer = 0

    def set_difficulty(self, diff):
        if self.game_over or self.current_player == AI_PLAYER:
            self.reset_game()
        self.difficulty = diff
        self.ai = AIPlayer(AI_PLAYER, diff)
