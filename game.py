from __future__ import annotations

import pygame
from typing import Optional, Tuple

from constants import *
from board import Board
from players import HumanPlayer, AIPlayer
from renderer import Renderer


class Game:
    def __init__(self):
        self.board = Board()
        self.human = HumanPlayer()
        self.ai: AIPlayer = AIPlayer(AI_PLAYER, Difficulty.MEDIUM)
        self.renderer = Renderer()

        self.current_player: int = HUMAN
        self.game_over: bool = False
        self.winner: Optional[int] = None
        self.difficulty: Difficulty = Difficulty.MEDIUM
        self.last_hovered: Optional[Tuple[int, int]] = None

    def run(self) -> None:
        running = True

        while running:
            mouse_pos = pygame.mouse.get_pos()
            hovered = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEMOTION:
                    col = event.pos[0] // CELL_SIZE
                    row = event.pos[1] // CELL_SIZE
                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                        hovered = (row, col)
                    else:
                        hovered = None

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    col = event.pos[0] // CELL_SIZE
                    row = event.pos[1] // CELL_SIZE

                    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
                        if not self.game_over and self.current_player == HUMAN:
                            if self.board.make_move(row, col, HUMAN):
                                self._after_move(HUMAN)

                    elif self.renderer.btn_new_game["rect"].collidepoint(event.pos):
                        self.reset_game()

                    elif self.renderer.btn_easy["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.EASY)
                    elif self.renderer.btn_medium["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.MEDIUM)
                    elif self.renderer.btn_hard["rect"].collidepoint(event.pos):
                        self.set_difficulty(Difficulty.HARD)

            if not self.game_over and self.current_player == AI_PLAYER:
                move = self.ai.get_move(self.board)
                if move:
                    r, c = move
                    if self.board.make_move(r, c, AI_PLAYER):
                        self._after_move(AI_PLAYER)

            status = self._get_status_text()
            self.renderer.draw_board(self.board, hovered)
            self.renderer.draw_ui(status, self.difficulty, mouse_pos)
            self.renderer.update()

        self.renderer.close()

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
        if self.game_over:
            if self.winner == HUMAN:
                return "Вы победили!"
            if self.winner == AI_PLAYER:
                return "Победил компьютер"
            return "Ничья"
        return "Ваш ход" if self.current_player == HUMAN else "Думает…"

    def reset_game(self) -> None:
        self.board = Board()
        self.current_player = HUMAN
        self.game_over = False
        self.winner = None
        self.last_hovered = None

    def set_difficulty(self, diff: Difficulty) -> None:
        if self.game_over or self.current_player == AI_PLAYER:
            self.reset_game()
        self.difficulty = diff
        self.ai = AIPlayer(AI_PLAYER, diff)
