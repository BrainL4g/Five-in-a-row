from __future__ import annotations
import pygame
from typing import Dict, Any
from constants import WINDOW_WIDTH, WINDOW_HEIGHT, Difficulty, VisualStyle


class Menu:
    def __init__(self):
        self.state = {
            "active": True,
            "buttons": {
                "new_game": {"text": "НОВАЯ ИГРА", "pos": (WINDOW_WIDTH // 2 - 110, 180)},
                "settings": {"text": "НАСТРОЙКИ", "pos": (WINDOW_WIDTH // 2 - 110, 250)},
                "exit": {"text": "ВЫХОД", "pos": (WINDOW_WIDTH // 2 - 110, 320)}
            }
        }

    def handle_click(self, pos: tuple) -> str:
        for btn_key, btn in self.state["buttons"].items():
            rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 220, 50)
            if rect.collidepoint(pos):
                return btn_key
        return ""

    def update_hover(self, pos: tuple):
        for btn in self.state["buttons"].values():
            rect = pygame.Rect(btn["pos"][0], btn["pos"][1], 220, 50)
            btn["hover"] = rect.collidepoint(pos)

    def show(self):
        self.state["active"] = True

    def hide(self):
        self.state["active"] = False
