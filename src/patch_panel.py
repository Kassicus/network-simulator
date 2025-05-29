"""
Module for the Patch Panel game element.
Handles patch panel attributes and cable connections.
"""

from rack import RackMountable
import pygame
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class PatchPanel8(RackMountable):
    display_name = "8-Port Patch Panel"
    COLOR = (80, 180, 255)  # Blue
    PORT_COLOR = (0, 0, 0)  # Black
    PORT_SIZE = 16
    PORT_SPACING = 12
    HEIGHT = 1
    NUM_PORTS = 8

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
        self.ports = []
        self.connections = [None for _ in range(self.NUM_PORTS)]
        self.selected_port = None
        self._update_ports()
        logging.info(f"PatchPanel8 created at rack unit {unit_index+1}.")

    def _update_ports(self):
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
        self.rect.width = self.rack_width
        self._update_ports()
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=6)
        for i, port_rect in enumerate(self.ports):
            color = self.PORT_COLOR
            if highlight_port == i or self.selected_port == i:
                pygame.draw.rect(screen, (255, 255, 0), port_rect, width=3)
            pygame.draw.rect(screen, color, port_rect)

    def handle_mouse_click(self, pos):
        for i, port_rect in enumerate(self.ports):
            if port_rect.collidepoint(pos):
                logging.info(f"Clicked port {i+1} on patch panel at rack unit {self.unit_index+1}.")
                return i
        return None

    def get_port_center(self, port_index):
        port_rect = self.ports[port_index]
        return (port_rect.centerx, port_rect.centery)

    def set_connection(self, port_index, other_device, other_port_index):
        self.connections[port_index] = (other_device, other_port_index)
        logging.info(f"Port {port_index+1} on patch panel at rack unit {self.unit_index+1} connected to port {other_port_index+1} on another device.")

    def clear_connection(self, port_index):
        self.connections[port_index] = None
        logging.info(f"Connection cleared on port {port_index+1} of patch panel at rack unit {self.unit_index+1}.")

    def get_connections(self):
        return self.connections

class PatchPanel16(RackMountable):
    display_name = "16-Port Patch Panel"
    COLOR = (80, 180, 255)  # Blue
    PORT_COLOR = (0, 0, 0)  # Black
    PORT_SIZE = 16
    PORT_SPACING = 12
    HEIGHT = 2
    NUM_PORTS = 16

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
            unit_height * self.HEIGHT
        )
        self.ports = []
        self.connections = [None for _ in range(self.NUM_PORTS)]
        self.selected_port = None
        self._update_ports()
        logging.info(f"PatchPanel16 created at rack unit {unit_index+1}.")

    def _update_ports(self):
        ports_per_row = 8
        total_width = ports_per_row * self.PORT_SIZE + (ports_per_row - 1) * self.PORT_SPACING
        start_x = self.rack_x + (self.rack_width - total_width) // 2
        y1 = self.rack_y + self.unit_index * self.unit_height + self.unit_height // 2 - self.PORT_SIZE // 2
        y2 = y1 + self.unit_height
        self.ports = []
        for i in range(ports_per_row):
            port_rect = pygame.Rect(
                start_x + i * (self.PORT_SIZE + self.PORT_SPACING),
                y1,
                self.PORT_SIZE,
                self.PORT_SIZE
            )
            self.ports.append(port_rect)
        for i in range(ports_per_row):
            port_rect = pygame.Rect(
                start_x + i * (self.PORT_SIZE + self.PORT_SPACING),
                y2,
                self.PORT_SIZE,
                self.PORT_SIZE
            )
            self.ports.append(port_rect)

    def draw(self, screen, highlight_port=None):
        self.rect.width = self.rack_width
        self._update_ports()
        pygame.draw.rect(screen, self.COLOR, self.rect, border_radius=6)
        for i, port_rect in enumerate(self.ports):
            color = self.PORT_COLOR
            if highlight_port == i or self.selected_port == i:
                pygame.draw.rect(screen, (255, 255, 0), port_rect, width=3)
            pygame.draw.rect(screen, color, port_rect)

    def handle_mouse_click(self, pos):
        for i, port_rect in enumerate(self.ports):
            if port_rect.collidepoint(pos):
                logging.info(f"Clicked port {i+1} on patch panel at rack unit {self.unit_index+1}.")
                return i
        return None

    def get_port_center(self, port_index):
        port_rect = self.ports[port_index]
        return (port_rect.centerx, port_rect.centery)

    def set_connection(self, port_index, other_device, other_port_index):
        self.connections[port_index] = (other_device, other_port_index)
        logging.info(f"Port {port_index+1} on patch panel at rack unit {self.unit_index+1} connected to port {other_port_index+1} on another device.")

    def clear_connection(self, port_index):
        self.connections[port_index] = None
        logging.info(f"Connection cleared on port {port_index+1} of patch panel at rack unit {self.unit_index+1}.")

    def get_connections(self):
        return self.connections 