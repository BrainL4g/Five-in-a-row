from __future__ import annotations
import pygame
from typing import Dict, Any
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, Difficulty, VisualStyle


class Settings:
    def __init__(self, initial_difficulty: Difficulty, initial_style: VisualStyle):
        self.state = {
            "active": False,
            "difficulty": {
                "easy": {"text": "ЛЁГКИЙ", "pos": (WINDOW_WIDTH // 2 - 270, 150), "value": Difficulty.EASY},
                "medium": {"text": "СРЕДНИЙ", "pos": (WINDOW_WIDTH // 2 - 90, 150), "value": Difficulty.MEDIUM},
                "hard": {"text": "СЛОЖНЫЙ", "pos": (WINDOW_WIDTH // 2 + 90, 150), "value": Difficulty.HARD}
            },
            "visual": {
                "classic": {"text": "КЛАССИКА", "pos": (WINDOW_WIDTH // 2 - 190, 230), "value": VisualStyle.CLASSIC},
                "modern": {"text": "СОВРЕМЕННЫЙ", "pos": (WINDOW_WIDTH // 2 + 10, 230), "value": VisualStyle.MODERN}
            },
            "back_button": {"text": "НАЗАД", "pos": (WINDOW_WIDTH // 2 - 60, 320)}
        }
        self.selected_difficulty = initial_difficulty
        self.selected_style = initial_style
        self._update_active_buttons()

    def _update_active_buttons(self):
        for key, btn in self.state["difficulty"].items():
            btn["active"] = (btn["value"] == self.selected_difficulty)
        for key, btn in self.state["visual"].items():
            btn["active"] = (btn["value"] == self.selected_style)

    def handle_click(self, pos: tuple) -> tuple:
        for section in ["difficulty", "visual"]:
            for key, btn in self.state[section].items():
                rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 180, 42)
                if rect.collidepoint(pos):
                    if section == "difficulty":
                        self.selected_difficulty = btn["value"]
                    else:
                        self.selected_style = btn["value"]
                    self._update_active_buttons()
                    return ("setting_changed", None)
        back_rect = pygame.Rect(self.state["back_button"]["pos"][0], self.state["back_button"]["pos"][1], 120, 40)
        if back_rect.collidepoint(pos):
            return ("back", None)
        return ("", None)

    def update_hover(self, pos: tuple):
        for section in ["difficulty", "visual"]:
            for btn in self.state[section].values():
                rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 180, 42)
                btn["hover"] = rect.collidepoint(pos)
        back_btn = self.state["back_button"]
        back_rect = pygame.Rect(back_btn["pos"][0], back_btn["pos"][1], 120, 40)
        back_btn["hover"] = back_rect.collidepoint(pos)

    def show(self):
        self.state["active"] = True

    def hide(self):
        self.state["active"] = False

    def get_difficulty(self) -> Difficulty:
        return self.selected_difficulty

    def get_style(self) -> VisualStyle:
        return self.selected_style
