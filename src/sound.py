import os
import pygame

pygame.mixer.init()


class SoundManager:
    def __init__(self):
        self.sounds_enabled = True
        try:
            self.move_sound = pygame.mixer.Sound(os.path.join('data', 'move.wav'))
            self.win_sound = pygame.mixer.Sound(os.path.join('data', 'win.wav'))
            self.click_sound = pygame.mixer.Sound(os.path.join('data', 'click.wav'))
        except FileNotFoundError:
            self.move_sound = None
            self.win_sound = None
            self.click_sound = None

    def play_move(self):
        if self.sounds_enabled and self.move_sound:
            self.move_sound.play()

    def play_win(self):
        if self.sounds_enabled and self.win_sound:
            self.win_sound.play()

    def play_click(self):
        if self.sounds_enabled and self.click_sound:
            self.click_sound.play()

    def toggle(self):
        self.sounds_enabled = not self.sounds_enabled
