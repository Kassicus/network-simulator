"""
Module for the Network Rack game element.
Handles rack attributes and operations.
"""

import pygame
import logging
from datetime import datetime

# --- RackMountable base class and registry ---
class RackMountable:
    registry = []
    display_name = "Rack Device"
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls not in RackMountable.registry:
            RackMountable.registry.append(cls)
    @classmethod
    def get_display_name(cls):
        return getattr(cls, 'display_name', cls.__name__)

from switch import Switch

# Configure logging for rack operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Rack:
    def __init__(self, x, y, width=240, height=480, units=12):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.units = units
        self.unit_height = self.height // self.units
        self.slots = [None for _ in range(self.units)]  # None means empty
        self.highlighted_unit = None
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        # Auto-populate first slot with a Switch (1U)
        if self.slots[0] is None:
            self.add_device(Switch, 0)
        logging.info(f"Rack initialized at ({self.x}, {self.y}) with {self.units}U.")

    def can_place_device(self, device_cls, start_unit):
        height = getattr(device_cls, 'HEIGHT', 1)
        if start_unit + height > self.units:
            return False
        for i in range(start_unit, start_unit + height):
            if self.slots[i] is not None:
                return False
        return True

    def add_device(self, device_cls, start_unit):
        height = getattr(device_cls, 'HEIGHT', 1)
        if not self.can_place_device(device_cls, start_unit):
            logging.warning(f"Cannot place {device_cls.get_display_name()} at {start_unit+1}U: not enough space or overlap.")
            return False
        device = device_cls(self.x, self.y, self.width, start_unit, self.unit_height)
        for i in range(start_unit, start_unit + height):
            self.slots[i] = device if i == start_unit else 'OCCUPIED'  # Mark only the first slot with the device, others as occupied
        logging.info(f"Added {device_cls.get_display_name()} to rack at unit {start_unit+1}U, height {height}U.")
        return True

    def draw(self, screen):
        # Draw rack outline
        pygame.draw.rect(screen, (60, 60, 70), self.rect, border_radius=8, width=4)
        # Draw units
        i = 0
        while i < self.units:
            unit_rect = pygame.Rect(
                self.x,
                self.y + i * self.unit_height,
                self.width,
                self.unit_height
            )
            slot = self.slots[i]
            # Draw device if present (only in its starting slot)
            if slot and slot != 'OCCUPIED':
                slot.rack_width = self.width
                slot.rect.width = self.width
                slot.draw(screen)
                height = getattr(slot, 'HEIGHT', 1)
                i += height
                continue
            else:
                color = (80, 80, 90)
                pygame.draw.rect(screen, color, unit_rect)
            # Highlight empty slot on hover
            if self.highlighted_unit == i and self.slots[i] is None:
                pygame.draw.rect(screen, (120, 180, 255), unit_rect, width=4)
            i += 1

    def handle_mouse_motion(self, pos):
        # Highlight the unit under the mouse if empty and enough space for the menu device
        if self.rect.collidepoint(pos):
            rel_y = pos[1] - self.y
            unit = rel_y // self.unit_height
            if 0 <= unit < self.units:
                if self.slots[unit] is None:
                    self.highlighted_unit = unit
                    logging.info(f"Mouse over empty slot {unit+1}U.")
                else:
                    self.highlighted_unit = None
                # Pass to device if present
                if self.slots[unit] and self.slots[unit] != 'OCCUPIED':
                    if hasattr(self.slots[unit], 'handle_mouse_motion'):
                        self.slots[unit].handle_mouse_motion(pos)
            else:
                self.highlighted_unit = None
        else:
            self.highlighted_unit = None

    def handle_mouse_click(self, pos):
        # Pass click to device if present
        if self.rect.collidepoint(pos):
            rel_y = pos[1] - self.y
            unit = rel_y // self.unit_height
            if 0 <= unit < self.units:
                logging.info(f"Clicked on slot {unit+1}U.")
                if self.slots[unit] and self.slots[unit] != 'OCCUPIED':
                    if hasattr(self.slots[unit], 'handle_mouse_click'):
                        return self.slots[unit].handle_mouse_click(pos)
                # Future: add/remove device logic here

    def get_state(self):
        return {
            'slots': self.slots,
            'highlighted_unit': self.highlighted_unit
        }

# Future: Define NetworkRack class and related logic here. 