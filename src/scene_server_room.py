"""
Module for the Server Room scene.
Handles UI and logic for managing cables, switches, and patch panels.
"""

import pygame
import logging
from rack import Rack

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class ServerRoomScene:
    def __init__(self, screen, scene_manager=None):
        self.screen = screen
        self.scene_manager = scene_manager  # For scene switching
        self.bg_color = (30, 32, 38)
        self.title_color = (220, 220, 220)
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        width, height = self.screen.get_size()
        # Place two racks side by side
        rack_width = 120
        rack_height = 400
        spacing = 80
        x1 = width // 2 - rack_width - spacing // 2
        x2 = width // 2 + spacing // 2
        y = height // 2 - rack_height // 2
        self.racks = [
            Rack(x1, y, rack_width, rack_height),
            Rack(x2, y, rack_width, rack_height)
        ]
        self.title = 'Server Room'
        logging.info("ServerRoomScene initialized with 2 racks.")

    def draw(self):
        self.screen.fill(self.bg_color)
        # Draw title
        title_surf = self.title_font.render(self.title, True, self.title_color)
        self.screen.blit(title_surf, (24, 16))
        # Draw racks
        for rack in self.racks:
            rack.draw(self.screen)
        pygame.display.flip()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                if self.scene_manager:
                    logging.info("Switching to desk scene.")
                    self.scene_manager.set_scene('desk')
            elif event.key == pygame.K_s:
                # Already in server room, do nothing
                pass
        elif event.type == pygame.MOUSEMOTION:
            for rack in self.racks:
                rack.handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rack in self.racks:
                rack.handle_mouse_click(event.pos)
        return None

    def update(self, dt):
        pass  # For future use 