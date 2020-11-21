import pygame


class Settings:

    def __init__(self):
        self.screen_width = int(pygame.display.Info().current_w * 1/3)
        self.screen_height = int(pygame.display.Info().current_h * 2/3)
        self.bg_color = (245, 245, 220)
        self.clock = pygame.time.Clock()
