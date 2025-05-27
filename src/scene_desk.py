"""
Module for the Player Desk scene.
Handles UI and logic for the player's main computer and remote access.
"""

import pygame

class PlayerDeskScene:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_size()
        self.bg_color = (24, 26, 32)
        self.title_color = (220, 220, 220)
        self.monitor_color = (40, 44, 52)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.title = 'Desk'
        # Monitor rectangle (centered)
        self.monitor_rect = pygame.Rect(
            self.WIDTH//2 - 200, self.HEIGHT//2 - 120, 400, 240
        )

    def draw(self):
        self.screen.fill(self.bg_color)
        # Draw title in upper left
        title_surf = self.title_font.render(self.title, True, self.title_color)
        self.screen.blit(title_surf, (24, 16))
        # Draw monitor rectangle
        pygame.draw.rect(self.screen, self.monitor_color, self.monitor_rect, border_radius=16)
        pygame.display.flip()

    def handle_event(self, event):
        pass  # No interaction yet 