"""
Module for the Network Rack game element.
Handles rack attributes and operations.
"""

import pygame
import logging
from datetime import datetime

# Configure logging for rack operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Rack:
    def __init__(self, x, y, width=120, height=400, units=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.units = units
        self.unit_height = self.height // self.units
        self.slots = [None for _ in range(self.units)]  # None means empty
        self.highlighted_unit = None
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        logging.info(f"Rack initialized at ({self.x}, {self.y}) with {self.units}U.")

    def draw(self, screen):
        # Draw rack outline
        pygame.draw.rect(screen, (60, 60, 70), self.rect, border_radius=8, width=4)
        # Draw units
        for i in range(self.units):
            unit_rect = pygame.Rect(
                self.x,
                self.y + i * self.unit_height,
                self.width,
                self.unit_height
            )
            color = (40, 44, 52) if self.slots[i] else (80, 80, 90)
            pygame.draw.rect(screen, color, unit_rect)
            # Highlight empty slot on hover
            if self.highlighted_unit == i and self.slots[i] is None:
                pygame.draw.rect(screen, (120, 180, 255), unit_rect, width=4)
            # Draw unit number
            font = pygame.font.SysFont('Consolas', 18)
            label = font.render(f"{i+1}U", True, (180, 180, 200))
            screen.blit(label, (self.x + 8, self.y + i * self.unit_height + 4))

    def handle_mouse_motion(self, pos):
        # Highlight the unit under the mouse if empty
        if self.rect.collidepoint(pos):
            rel_y = pos[1] - self.y
            unit = rel_y // self.unit_height
            if 0 <= unit < self.units:
                if self.slots[unit] is None:
                    self.highlighted_unit = unit
                    logging.info(f"Mouse over empty slot {unit+1}U.")
                else:
                    self.highlighted_unit = None
            else:
                self.highlighted_unit = None
        else:
            self.highlighted_unit = None

    def handle_mouse_click(self, pos):
        # Placeholder for future: add/remove device
        if self.rect.collidepoint(pos):
            rel_y = pos[1] - self.y
            unit = rel_y // self.unit_height
            if 0 <= unit < self.units:
                logging.info(f"Clicked on slot {unit+1}U.")
                # Future: add/remove device logic here

    def get_state(self):
        return {
            'slots': self.slots,
            'highlighted_unit': self.highlighted_unit
        }

# Future: Define NetworkRack class and related logic here. 