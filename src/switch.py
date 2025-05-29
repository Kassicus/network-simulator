"""
Module for the Switch game element.
Handles switch attributes, port management, and network connections.
"""

import pygame
import logging
from rack import RackMountable

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class Switch(RackMountable):
    display_name = "Network Switch"
    COLOR = (120, 255, 120)  # Light green
    PORT_COLOR = (0, 0, 0)   # Black
    PORT_SIZE = 16
    PORT_SPACING = 12
    HEIGHT = 1  # Rack units
    NUM_PORTS = 4

    def __init__(self, rack_x, rack_y, rack_width, unit_index, unit_height):
        super().__init__()
        self.rack_x = rack_x
        self.rack_y = rack_y
        self.rack_width = rack_width
        self.unit_index = unit_index
        self.unit_height = unit_height
        self.rect = pygame.Rect(
            rack_x,
            rack_y + unit_index * unit_height,
            rack_width,
            unit_height
        )
        self.ports = []  # List of port rects
        self.connections = [None for _ in range(self.NUM_PORTS)]  # (switch, port_index) or None
        self.selected_port = None  # (index) if this switch has a port selected
        self._update_ports()
        logging.info(f"Switch created at rack unit {unit_index+1}.")

    def _update_ports(self):
        # Evenly space ports horizontally
        total_width = self.NUM_PORTS * self.PORT_SIZE + (self.NUM_PORTS - 1) * self.PORT_SPACING
        start_x = self.rack_x + (self.rack_width - total_width) // 2
        y = self.rack_y + self.unit_index * self.unit_height + self.unit_height // 2 - self.PORT_SIZE // 2
        self.ports = []
        for i in range(self.NUM_PORTS):
            port_rect = pygame.Rect(
                start_x + i * (self.PORT_SIZE + self.PORT_SPACING),
                y,
                self.PORT_SIZE,
                self.PORT_SIZE
            )
            self.ports.append(port_rect)

    def draw(self, screen, highlight_port=None):
        # Draw switch body
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=6)
        # Draw ports
        for i, port_rect in enumerate(self.ports):
            color = self.PORT_COLOR
            if highlight_port == i or self.selected_port == i:
                pygame.draw.rect(screen, (255, 255, 0), port_rect, width=3)  # Highlight selected/hovered port
            pygame.draw.rect(screen, color, port_rect)

    def handle_mouse_click(self, pos):
        for i, port_rect in enumerate(self.ports):
            if port_rect.collidepoint(pos):
                logging.info(f"Clicked port {i+1} on switch at rack unit {self.unit_index+1}.")
                return i
        return None

    def get_port_center(self, port_index):
        port_rect = self.ports[port_index]
        return (port_rect.centerx, port_rect.centery)

    def set_connection(self, port_index, other_switch, other_port_index):
        self.connections[port_index] = (other_switch, other_port_index)
        logging.info(f"Port {port_index+1} on switch at rack unit {self.unit_index+1} connected to port {other_port_index+1} on another switch.")

    def clear_connection(self, port_index):
        self.connections[port_index] = None
        logging.info(f"Connection cleared on port {port_index+1} of switch at rack unit {self.unit_index+1}.")

    def get_connections(self):
        return self.connections

# Future: Define Switch class and related logic here. 